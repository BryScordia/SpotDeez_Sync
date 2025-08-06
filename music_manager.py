import os
import sys
import csv
import yaml
import requests
import subprocess
import re
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
os.makedirs(MP3_DIR, exist_ok=True)

# ——— Gestión de registros ———
def load_downloaded():
    if not os.path.exists(DOWNLOAD_CSV):
        return set()
    with open(DOWNLOAD_CSV, newline='', encoding='utf-8') as f:
        return set(line.strip() for line in f if line.strip())

downloaded = load_downloaded()

def log_success(link):
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
    write_header = not os.path.exists(ERROR_CSV)
    with open(ERROR_CSV, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(['type','link','error'])
        writer.writerow([item_type, link, message])

# ——— Inicialización de Spotify ———
def init_spotify():
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
    return url.rstrip("/\r\n").split("/")[-1].split("?")[0]

def safe(name):
    if not isinstance(name, str) or not name:
        return ""
    return re.sub(r'[<>:\"/\\|?*]', '', name).strip()

def map_isrc_to_deezer_track(isrc, link_context=None):
    r = requests.get(f"https://api.deezer.com/track/isrc:{isrc}", timeout=10)
    if r.status_code == 200 and (j := r.json()).get("id"):
        return j["id"]
    log_error('isrc_map_failure', link_context or isrc, f"No Deezer track for ISRC {isrc}")
    return None

# ——— Descarga Deezer con fallback ———
def download_deezer_link(link, fmt, subfolder=None):
    """Descarga un link de Deezer, organizando álbumes en carpeta de artista y subcarpeta de álbum sin prefijo."""
    if link in downloaded:
        print(f"Ya descargado: {link}")
        return
    base = MP3_DIR if fmt == 'mp3' else FLAC_DIR
    # obtener artista y título de álbum si aplica
    artist = None
    album_title = None
    if '/album/' in link:
        dzid = parse_spotify_id(link)
        try:
            data = requests.get(f"https://api.deezer.com/album/{dzid}", timeout=10).json()
            artist = data.get('artist', {}).get('name')
            album_title = data.get('title')
        except Exception as e:
            log_error('metadata_failure', link, str(e))
    # definir carpeta de artista o subfolder
    if artist:
        parent_dest = os.path.join(base, safe(artist))
    elif subfolder:
        parent_dest = os.path.join(base, safe(subfolder))
    else:
        parent_dest = base
    os.makedirs(parent_dest, exist_ok=True)
    # función interna para invocar deemix
    def try_download(rfmt):
        bitrate = 'FLAC' if rfmt == 'flac' else '320'
        cmd = [sys.executable, '-m', 'deemix', '--bitrate', bitrate, '--path', parent_dest, link]
        subprocess.run(cmd, check=True)
    # descarga con fallback
    try:
        try_download(fmt)
        # renombrar carpeta "Artista - Álbum" a solo "Álbum"
        if album_title and artist:
            orig_folder = os.path.join(parent_dest, safe(f"{artist} - {album_title}"))
            new_folder = os.path.join(parent_dest, safe(album_title))
            try:
                if os.path.isdir(orig_folder) and not os.path.exists(new_folder):
                    os.rename(orig_folder, new_folder)
            except Exception as e:
                log_error('rename_failure', orig_folder, str(e))
        log_success(link)
    except subprocess.CalledProcessError as e:
        err = str(e)
        # fallback a MP3 si pide FLAC y no existe
        if fmt == 'flac' and 'wrongBitrate' in err:
            print(f"No hay FLAC de {link}, reintentando MP3...")
            try:
                try_download('mp3')
                log_success(link)
            except subprocess.CalledProcessError as e2:
                log_error('download_failure', link, str(e2))
        else:
            log_error('download_failure', link, err)

# ——— Funciones Spotify ———
def spotify_download_link(sp, link, fmt, subfolder=None):
    sid = parse_spotify_id(link)
    # pista
    if '/track/' in link:
        info = sp.track(sid)
        isrc = info.get('external_ids', {}).get('isrc','')
        dzid = map_isrc_to_deezer_track(isrc, link)
        if dzid:
            dl = f"https://www.deezer.com/track/{dzid}"
            download_deezer_link(dl, fmt, subfolder)
        else:
            log_error('track_not_found', link, 'No Deezer mapping')
    # álbum
    elif '/album/' in link:
        tracks = sp.album_tracks(sid, limit=1)['items']
        isrc = sp.track(tracks[0]['id']).get('external_ids', {}).get('isrc','')
        dzid = map_isrc_to_deezer_track(isrc, link)
        if dzid:
            # descargar álbum
            r = requests.get(f"https://api.deezer.com/track/{dzid}", timeout=10)
            album_id = r.json().get('album', {}).get('id')
            if album_id:
                download_deezer_link(f"https://www.deezer.com/album/{album_id}", fmt, subfolder)
            else:
                log_error('album_not_found', link, 'Album ID missing')
        else:
            log_error('album_not_found', link, 'ISRC mapping failed')
    # playlist
    else:
        pinfo = sp.playlist(sid)
        name = pinfo.get('name','playlist')
        offset = 0
        while True:
            res = sp.playlist_items(sid, offset=offset, limit=100)
            items = res.get('items', [])
            if not items: break
            for itm in items:
                tid = itm.get('track', {}).get('id')
                if tid:
                    spotify_download_link(sp, f"https://open.spotify.com/track/{tid}", fmt, name)
            offset += len(items)

# ——— Importar cuenta ———
def spotify_import_account(sp, fmt):
    print("\n--- Importar en mi cuenta ---")
    print("1) Biblioteca (canciones)")
    print("2) Álbumes guardados")
    print("3) Playlists")
    choice = input("Opción [1-3]: ").strip()
    # biblioteca
    if choice=='1':
        all_tracks=[]
        off=0
        while True:
            resp = sp.current_user_saved_tracks(limit=50, offset=off)
            items = resp.get('items',[])
            if not items: break
            for itm in items:
                tid = itm['track']['id']
                all_tracks.append(f"https://open.spotify.com/track/{tid}")
            off += len(items)
        for link in all_tracks:
            spotify_download_link(sp, link, fmt)
    # álbumes
    elif choice=='2':
        albums = []
        off = 0
        while True:
            resp = sp.current_user_saved_albums(limit=50, offset=off)
            items = resp.get('items',[])
            if not items: break
            for itm in items:
                aid = itm['album']['id']
                albums.append(f"https://open.spotify.com/album/{aid}")
            off += len(items)
        for link in albums:
            spotify_download_link(sp, link, fmt)
    # playlists
    elif choice=='3':
        pls=[]
        off=0
        while True:
            resp = sp.current_user_playlists(limit=50, offset=off)
            items=resp.get('items',[])
            if not items: break
            pls.extend(items)
            off+=len(items)
        for i,pl in enumerate(pls,1): print(f"{i}) {pl['name']}")
        sel=int(input("Elige playlist: ").strip())-1
        pid=pls[sel]['id']
        spotify_download_link(sp, f"https://open.spotify.com/playlist/{pid}", fmt)
    else:
        print("Opción inválida.")

# ——— Menús ———
def menu_spotify(sp):
    print("\n--- Importar desde Spotify ---")
    print("1) Link de canción")
    print("2) Link de álbum")
    print("3) Link de playlist")
    print("4) Importar en mi cuenta")
    opt = input("Opción [1-4]: ").strip()
    fmt = 'flac' if input("Formato (1=FLAC, 2=MP3): ").strip()=='1' else 'mp3'
    if opt in ['1','2','3']:
        link = input("Pega el link: ").strip()
        spotify_download_link(sp, link, fmt)
    elif opt=='4':
        spotify_import_account(sp, fmt)
    else:
        print("Opción inválida.")


def menu_deezer():
    print("\n--- Descargar desde Deezer ---")
    print("1) Canción")
    print("2) Álbum")
    print("3) Playlist")
    typ = input("Opción [1-3]: ").strip()
    fmt = 'flac' if input("Formato (1=FLAC, 2=MP3): ").strip()=='1' else 'mp3'
    link = input("Pega el link: ").strip()
    sub=None
    if typ=='3':
        pid = parse_spotify_id(link)
        sub=requests.get(f"https://api.deezer.com/playlist/{pid}", timeout=10).json().get('title','Playlist')
    download_deezer_link(link, fmt, sub)


def main():
    sp = init_spotify()
    while True:
        print("\n=== Music Manager ===")
        print("1) Importar desde Spotify")
        print("2) Descargar desde Deezer")
        print("3) Salir")
        cmd = input("Opción [1-3]: ").strip()
        if cmd=='1':
            menu_spotify(sp)
        elif cmd=='2':
            menu_deezer()
        elif cmd=='3':
            break
        else:
            print("Opción inválida.")

if __name__=='__main__':
    main()
