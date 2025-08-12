# Music Manager

> Bilingual README (Español / English). Jump to: [🇪🇸 Español](#-español) • [🇬🇧 English](#-english)

---

## 🇪🇸 Español

### 🎧 ¿Qué es *Music Manager*?
**Music Manager** es una herramienta de línea de comandos para sincronizar tu biblioteca de Spotify con descargas de alta calidad desde Deezer. Puedes importar pistas, álbumes o playlists desde:

- Enlaces directos de **Spotify**.
- Tu **cuenta de Spotify** (canciones, álbumes o playlists guardadas).
- Enlaces directos de **Deezer** (canción, álbum o playlist).

Las pistas se resuelven por **ISRC** y se descargan en **FLAC** o **MP3 320 kbps** dentro de carpetas organizadas. Incluye registros de aciertos/errores para auditoría.

---

### ✨ Características
- Importación desde enlaces o tu cuenta de Spotify.
- Emparejamiento por **ISRC** para mayor precisión.
- Descargas en **FLAC** o **MP3 320 kbps** usando la CLI de *deemix*.
- Estructura de carpetas organizada y **logs** (`downloaded.csv`, `errors.csv`).
- Configuración flexible vía `config.yml` o variables de entorno.

---

### 🔧 Requisitos
- **Python 3.10+**
- **spotipy** – Cliente de la API de Spotify
- **requests** – Solicitudes HTTP
- **PyYAML** – Carga de configuración YAML
- **deemix** – CLI para descargas desde Deezer
- **python-dotenv** *(opcional)* – Variables en `.env`

Instala dependencias:
```bash
pip install -r requirements.txt
```

> `requirements.txt` debería incluir:
> ```text
> spotipy
> requests
> PyYAML
> deemix
> python-dotenv
> ```

> 💡 **Sugerencia:** usa un entorno virtual.
> ```bash
> python -m venv .venv
> # Linux/macOS
> source .venv/bin/activate
> # Windows (PowerShell)
> .venv\Scripts\Activate.ps1
> ```

---

### ⚙️ Instalación y Configuración
1) **Clona el repositorio**
```bash
git clone https://github.com/BryScordia/music-manager.git
cd music-manager
```

2) **Crea tu archivo de configuración**
```bash
cp example_config.yml config.yml
```

3) **Edita `config.yml`** con tus credenciales y rutas
```yaml
spotify:
  client_id:     "TU_CLIENT_ID"
  client_secret: "TU_CLIENT_SECRET"
  redirect_uri:  "http://localhost:8888/callback"  # Debe coincidir con tu App de Spotify

paths:
  deezer_flac: "/ruta/a/tu/deezer_flac"
  deezer_mp3:  "/ruta/a/tu/deezer_mp3"
  error_log:   "errors.csv"
  download_log: "downloaded.csv"
```

4) **Configura tu App de Spotify**
- Crea una aplicación en el *Dashboard* de Spotify.
- Copia **Client ID** y **Client Secret** a `config.yml`.
- En *Edit Settings → Redirect URIs*, añade `http://localhost:8888/callback`.

5) **Inicializa la CLI de Deemix (Deezer)**
```bash
python -m deemix
```
Sigue el *prompt* para proporcionar la **cookie** de tu cuenta de Deezer (desde las herramientas de desarrollador del navegador).

6) *(Opcional)* **Usar `.env` en lugar de `config.yml`**
```bash
mv config.yml .env
```
Define las variables:
```dotenv
SPOTIFY_ID=...
SPOTIFY_SECRET=...
SPOTIFY_REDIR=http://localhost:8888/callback
DEEZER_FLAC=/ruta/a/deezer_flac
DEEZER_MP3=/ruta/a/deezer_mp3
ERROR_LOG=errors.csv
DOWNLOAD_LOG=downloaded.csv
```

---

### 🚀 Uso
Ejecuta el script principal:
```bash
python music_manager.py
```

Sigue el menú interactivo:
1. **Importar desde Spotify**  
   - Link de canción / álbum / playlist  
   - Importar toda tu cuenta (biblioteca, álbumes o playlists)
2. **Descargar desde Deezer**  
   - Link de canción / álbum / playlist
3. **Salir**

**Ejemplo**
```text
=== Music Manager ===
1) Importar desde Spotify
2) Descargar desde Deezer
3) Salir
Opción [1-3]: 1
Formato (1=FLAC, 2=MP3): 1
--- Importar en mi cuenta ---
1) Biblioteca (canciones guardadas)
2) Álbumes guardados
3) Playlists
Opción [1-3]: 2
...descargando álbumes guardados en FLAC...
```

---

### 🧾 Registros (logs)
Si alguna pista/álbum no se encuentra en Deezer, se registra en `errors.csv`:

```csv
type,link,error
isrc_map_failure,<context>,No Deezer track found for ISRC...
download_failure,<url>,CalledProcessError...
```

Adicionalmente, `downloaded.csv` guarda los aciertos.

---

### 💡 Buenas prácticas
- Mantén tu **`config.yml`** fuera del control de versiones (añádelo a `.gitignore`).
- Usa **`example_config.yml`** como plantilla para colaboradores.
- Revisa/limpia `errors.csv` y `downloaded.csv` tras cada ejecución masiva.

---

### ⚖️ Términos y responsabilidad
Este software es de **uso personal** y se proporciona *"tal cual"*. El autor no asume responsabilidad por:
- El uso de los contenidos descargados.
- El cumplimiento de los **Términos de Servicio** de Spotify y Deezer.

Usa esta herramienta conforme a la legislación vigente y las políticas de cada plataforma.

---

### 📄 Licencia
Licenciado bajo **MIT**. Consulta `LICENSE` para más detalles.

---

### 👤 Autor
**Bryan Olmos** — [GitHub](https://github.com/BryScordia)

---

## 🇬🇧 English

### 🎧 What is *Music Manager*?
**Music Manager** is a command‑line tool that lets you sync your Spotify library with high‑quality downloads from Deezer. You can import tracks, albums, or playlists from:

- **Spotify** direct links.
- Your **Spotify account** (saved tracks, albums, or playlists).
- **Deezer** direct links (track, album, or playlist).

Tracks are matched by **ISRC**, then downloaded as **FLAC** or **MP3 320 kbps** into organized folders. Success/error logs are included for auditing.

---

### ✨ Features
- Import from links or your Spotify account.
- **ISRC**‑based matching for accuracy.
- **FLAC** or **MP3 320 kbps** downloads via *deemix* CLI.
- Organized folder structure and **logs** (`downloaded.csv`, `errors.csv`).
- Flexible configuration via `config.yml` or environment variables.

---

### 🔧 Requirements
- **Python 3.10+**
- **spotipy** – Spotify Web API client
- **requests** – HTTP requests
- **PyYAML** – YAML configuration loader
- **deemix** – Deezer download CLI
- **python-dotenv** *(optional)* – `.env` support

Install dependencies:
```bash
pip install -r requirements.txt
```

> `requirements.txt` should include:
> ```text
> spotipy
> requests
> PyYAML
> deemix
> python-dotenv
> ```

> 💡 **Tip:** use a virtual environment.
> ```bash
> python -m venv .venv
> # Linux/macOS
> source .venv/bin/activate
> # Windows (PowerShell)
> .venv\Scripts\Activate.ps1
> ```

---

### ⚙️ Setup
1) **Clone the repository**
```bash
git clone https://github.com/BryScordia/music-manager.git
cd music-manager
```

2) **Create your config file**
```bash
cp example_config.yml config.yml
```

3) **Edit `config.yml`** with your credentials and paths
```yaml
spotify:
  client_id:     "YOUR_CLIENT_ID"
  client_secret: "YOUR_CLIENT_SECRET"
  redirect_uri:  "http://localhost:8888/callback"  # Must match your Spotify App

paths:
  deezer_flac: "/path/to/deezer_flac"
  deezer_mp3:  "/path/to/deezer_mp3"
  error_log:   "errors.csv"
  download_log: "downloaded.csv"
```

4) **Configure your Spotify Developer App**
- Create an app in the Spotify Dashboard.
- Copy **Client ID** and **Client Secret** into `config.yml`.
- In *Edit Settings → Redirect URIs*, add `http://localhost:8888/callback`.

5) **Initialize Deemix CLI (Deezer)**
```bash
python -m deemix
```
Follow the prompt to provide your Deezer account **cookie** (from your browser’s developer tools).

6) *(Optional)* **Use `.env` instead of `config.yml`**
```bash
mv config.yml .env
```
Define variables:
```dotenv
SPOTIFY_ID=...
SPOTIFY_SECRET=...
SPOTIFY_REDIR=http://localhost:8888/callback
DEEZER_FLAC=/path/to/deezer_flac
DEEZER_MP3=/path/to/deezer_mp3
ERROR_LOG=errors.csv
DOWNLOAD_LOG=downloaded.csv
```

---

### 🚀 Usage
Run the main script:
```bash
python music_manager.py
```

Use the interactive menu:
1. **Import from Spotify**  
   - Track / album / playlist link  
   - Import your whole account (library, albums, or playlists)
2. **Download from Deezer**  
   - Track / album / playlist link
3. **Exit**

**Example**
```text
=== Music Manager ===
1) Importar desde Spotify
2) Descargar desde Deezer
3) Salir
Option [1-3]: 1
Format (1=FLAC, 2=MP3): 1
--- Import from my account ---
1) Library (saved tracks)
2) Saved albums
3) Playlists
Option [1-3]: 2
...downloading saved albums in FLAC...
```

---

### 🧾 Logs
When a track/album cannot be found on Deezer, it’s recorded in `errors.csv`:

```csv
type,link,error
isrc_map_failure,<context>,No Deezer track found for ISRC...
download_failure,<url>,CalledProcessError...
```

Additionally, `downloaded.csv` stores successful downloads.

---

### ⚖️ Terms & Responsibility
This software is for **personal use** and is provided *“as is”*. The author assumes no responsibility for:
- How downloaded content is used.
- Compliance with **Spotify** and **Deezer** Terms of Service.

Use this tool in accordance with applicable laws and each platform’s policies.

---

### 📄 License
Licensed under **MIT**. See `LICENSE` for details.

---

### 👤 Author
**Bryan Olmos** — [GitHub](https://github.com/BryScordia)
