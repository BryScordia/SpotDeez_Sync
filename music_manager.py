import os
import sys
import csv
import yaml
import requests
import subprocess
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# ——— Configuración ———
cfg = yaml.safe_load(open("config.yml", encoding="utf-8"))
SPOTIFY_ID     = cfg["spotify"]["client_id"]
SPOTIFY_SECRET = cfg["spotify"]["client_secret"]
SPOTIFY_REDIR  = cfg["spotify"]["redirect_uri"]

FLAC_DIR     = cfg["paths"]["deezer_flac"]
MP3_DIR      = cfg["paths"]["deezer_mp3"]
ERROR_CSV    = cfg.get("paths", {}).get("error_log", "errors.csv")
DOWNLOAD_CSV = cfg.get("paths", {}).get("download_log", "downloaded.csv")

# Asegura carpetas base
os.makedirs(FLAC_DIR, exist_ok=True)
os.makedirs(MP3_DIR,  exist_ok=True)

# ——— Gestión de registros ———
def load_downloaded():
    """Carga links ya descargados desde DOWNLOAD_CSV."""
    if not os.path.exists(DOWNLOAD_CSV):
        return set()
    with open(DOWNLOAD_CSV, newline='', encoding='utf-8') as f:
        return set(line.strip() for line in f if line.strip())

downloaded = load_downloaded()

def log_success(link):
    """Registra un link descargado exitosamente."""
    if link in downloaded:
        return
    write_header = not os.path.exists(DOWNLOAD_CSV)
    with open(DOWNLOAD_CSV, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(['link'])
        writer.writerow([link])
    downloaded.add(link)

def log_error(item_type, link, message):
    """Registra errores en ERROR_CSV."""
    write_header = not os.path.exists(ERROR_CSV)
    with open(ERROR_CSV, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(['type','link','error'])
        writer.writerow([item_type, link, message])

# ——— Inicialización de Spotify ———
def init_spotify():
    """Inicializa el cliente Spotipy con refresco automático de token."""
    auth_manager = SpotifyOAuth(
        client_id=SPOTIFY_ID,
        client_secret=SPOTIFY_SECRET,
        redirect_uri=SPOTIFY_REDIR,
        scope="user-library-read playlist-read-private",
        cache_path=".spotify-token-cache"
    )
    return spotipy.Spotify(auth_manager=auth_manager)

# ——— Helpers ———
def parse_spotify_id(url):
    return url.rstrip("/").split("/")[-1].split("?")[0]

def map_isrc_to_deezer_track(isrc, link_context=None):
    r = requests.get(f"https://api.deezer.com/track/isrc:{isrc}")
    if r.status_code == 200 and (j := r.json()).get("id"):
        return j["id"]
    context = link_context or isrc
    log_error('isrc_map_failure', context, f"No Deezer track for ISRC {isrc}")
    return None

# ——— Descarga Deezer ———
def download_deezer_link(link, fmt, subfolder=None):
    # Omite si ya descargado
    if link in downloaded:
        print(f"Ya descargado: {link}, se omite.")
        return

    # Carpeta de destino
    base = MP3_DIR if fmt == "mp3" else FLAC_DIR
    dest = os.path.join(base, subfolder) if subfolder else base
    os.makedirs(dest, exist_ok=True)

    # Comando Deemix: bitrate y path
    bitrate = "FLAC" if fmt == "flac" else "320"
    cmd = [sys.executable, "-m", "deemix", "--bitrate", bitrate, "--path", dest, link]

    try:
        subprocess.run(cmd, check=True)
        log_success(link)
    except subprocess.CalledProcessError as e:
        log_error('download_failure', link, str(e))

# ——— Funciones principales ———
def spotify_download_link(sp, link, fmt):
    sid = parse_spotify_id(link)
    if "/track/" in link:
        info = sp.track(sid)
        isrc = info.get("external_ids", {}).get("isrc", "")
        dzid = map_isrc_to_deezer_track(isrc, link)
        if dzid:
            dl = f"https://www.deezer.com/track/{dzid}"
            download_deezer_link(dl, fmt)
        else:
            log_error('track_not_found', link, 'No Deezer mapping')

    elif "/album/" in link:
        tracks = sp.album_tracks(sid, limit=1)["items"]
        isrc = sp.track(tracks[0]["id"]).get("external_ids", {}).get("isrc", "")
        dzid = map_isrc_to_deezer_track(isrc, link)
        if dzid:
            r = requests.get(f"https://api.deezer.com/track/{dzid}")
            album_id = r.json().get("album", {}).get("id")
            if album_id:
                dl = f"https://www.deezer.com/album/{album_id}"
                download_deezer_link(dl, fmt)
            else:
                log_error('album_not_found', link, 'Album ID missing')
        else:
            log_error('album_not_found', link, 'ISRC mapping failed')

    else:
        name = sp.playlist(sid).get("name", "playlist")
        offset = 0; tracks = []
        while True:
            res = sp.playlist_items(sid, offset=offset, limit=100)
            items = res.get("items", [])
            if not items: break
            tracks.extend(items)
            if not res.get("next"): break
            offset += len(items)
        for item in tracks:
            t = item.get("track", {})
            isrc = t.get("external_ids", {}).get("isrc", "")
            dzid = map_isrc_to_deezer_track(isrc, link)
            if dzid:
                dl = f"https://www.deezer.com/track/{dzid}"
                download_deezer_link(dl, fmt, subfolder=name)
            else:
                log_error('playlist_track_not_found', name, f"ISRC mapping failed for {t.get('id')}")

# ——— Pre-carga de álbumes guardados ———
def get_all_saved_album_links(sp):
    """Devuelve una lista con los links de todos los álbumes guardados."""
    albums = []
    offset = 0
    while True:
        resp = sp.current_user_saved_albums(limit=50, offset=offset)
        items = resp.get("items", [])
        if not items:
            break
        for item in items:
            album_id = item["album"]["id"]
            albums.append(f"https://open.spotify.com/album/{album_id}")
        offset += len(items)
    return albums

# ——— Importar cuenta Spotify ———
def spotify_import_account(sp, fmt):
    print("\n--- Importar en mi cuenta ---")
    print("1) Biblioteca (canciones guardadas)")
    print("2) Álbumes guardados")
    print("3) Playlists")
    choice = input("Opción [1-3]: ").strip()

    if choice == "1":
        off=0; ids=[]
        while True:
            resp = sp.current_user_saved_tracks(limit=50, offset=off)
            if not resp.get("items"): break
            ids.extend([itm["track"]["id"] for itm in resp["items"]])
            off += len(resp["items"])
        for tid in ids:
            spotify_download_link(sp, f"https://open.spotify.com/track/{tid}", fmt)

    elif choice == "2":
        print("Obteniendo todos los álbumes guardados...")
        links = get_all_saved_album_links(sp)
        print(f"Se encontraron {len(links)} álbumes. Comenzando descargas...\n")
        for link in links:
            spotify_download_link(sp, link, fmt)

    elif choice == "3":
        off=0; pls=[]
        while True:
            r = sp.current_user_playlists(limit=50, offset=off)
            if not r.get("items"): break
            pls.extend(r["items"])
            off += len(r["items"])
        for idx, pl in enumerate(pls,1): print(f"{idx}) {pl['name']}")
        sel=int(input("Elige playlist: ").strip())-1
        link=pls[sel]["external_urls"]["spotify"]
        spotify_download_link(sp, link, fmt)
    else:
        print("Opción inválida.")

# ——— Menús ———
def menu_spotify(sp):
    print("\n--- Importar desde Spotify ---")
    print("1) Link de canción")
    print("2) Link de álbum")
    print("3) Link de playlist")
    print("4) Importar en mi cuenta")
    opt=input("Opción [1-4]: ").strip()
    fmt="flac" if input("Formato (1=FLAC, 2=MP3): ").strip()=="1" else "mp3"
    if opt in ("1","2","3"):
        link=input("Pega el link de Spotify: ").strip()
        spotify_download_link(sp, link, fmt)
    elif opt=="4": spotify_import_account(sp, fmt)
    else: print("Opción inválida.")

def menu_deezer():
    print("\n--- Descargar desde Deezer ---")
    print("1) Canción")
    print("2) Álbum")
    print("3) Playlist")
    typ=input("Opción [1-3]: ").strip()
    fmt="flac" if input("Formato (1=FLAC, 2=MP3): ").strip()=="1" else "mp3"
    link=input("Pega el link de Deezer: ").strip()
    sub=None
    if typ=="3":
        pid=link.rstrip("/").split("/")[-1]
        sub=requests.get(f"https://api.deezer.com/playlist/{pid}").json().get("title","Playlist")
    download_deezer_link(link, fmt, subfolder=sub)


def main():
    sp = init_spotify()
    while True:
        print("\n=== Music Manager ===")
        print("1) Importar desde Spotify")
        print("2) Descargar desde Deezer")
        print("3) Salir")
        cmd=input("Opción [1-3]: ").strip()
        if cmd=="1": menu_spotify(sp)
        elif cmd=="2": menu_deezer()
        elif cmd=="3": break
        else: print("Opción inválida.")

if __name__=="__main__": main()
