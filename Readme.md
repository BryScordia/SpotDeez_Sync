# Music Manager

**Music Manager** es una herramienta de línea de comandos que te permite sincronizar tu biblioteca de Spotify con descargas de alta calidad desde Deezer. Importa pistas, álbumes o playlists desde: 

- Enlaces directos de Spotify.  
- Tu cuenta de Spotify (canciones, álbumes o playlists guardadas).  

Luego mapea las pistas por ISRC y descarga en **FLAC** o **MP3 320 kbps** en carpetas organizadas.

---
## 🔧 Dependencias

Este proyecto requiere:

- **Python 3.10+**  
- **spotipy**: API de Spotify.  
- **requests**: solicitudes HTTP.  
- **PyYAML**: carga de configuración YAML.  
- **deemix**: CLI para descargar desde Deezer.  
- **python-dotenv** (opcional): variables de entorno en `.env`.

```bash
pip install -r requirements.txt
```

>**requirements.txt** debería incluir:
>```text
>spotipy
>requests
>PyYAML
>deemix
>python-dotenv
>```

---
## ⚙️ Configuración

1. **Clona el repo**:
   ```bash
   git clone https://github.com/BryScordia/music-manager.git
   cd music-manager
   ```
2. **Crea el archivo de configuración**:
   ```bash
   cp example_config.yml config.yml
   ```
3. **Edita `config.yml`** con tus credenciales y rutas:
   ```yaml
   spotify:
     client_id:     "TU_CLIENT_ID"
     client_secret: "TU_CLIENT_SECRET"
     redirect_uri:  "TU_REDIRECT_URI"

   paths:
     deezer_flac: "/ruta/a/tu/deezer_flac"
     deezer_mp3:  "/ruta/a/tu/deezer_mp3"
     error_log:   "errors.csv"
   ```
4. (Opcional) Si prefieres variables de entorno, renombra `config.yml` a `.env` y define:
   ```dotenv
   SPOTIFY_ID=...
   SPOTIFY_SECRET=...
   SPOTIFY_REDIR=...
   DEEZER_FLAC=/ruta/a/deezer_flac
   DEEZER_MP3=/ruta/a/deezer_mp3
   ERROR_LOG=errors.csv
   ```

---
## 🚀 Uso

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

**Ejemplo de importación desde cuenta**:
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
## ⚠️ Registro de errores

Si alguna pista o álbum no se encuentra en Deezer, queda registrado en `errors.csv` con columnas:

```
type,link,error
isrc_map_failure,<context>,No Deezer track found for ISRC...
download_failure,<url>,CalledProcessError...
```

---
## 💡 Buenas prácticas

- Mantén **`config.yml`** en tu `.gitignore`.  
- Para colaborar, usa **`example_config.yml`** como plantilla.  
- Revisa y limpia **`errors.csv`** tras cada ejecución masiva.

---

## ⚖️ Términos y responsabilidad

Este software es de **uso personal** y se proporciona "tal cual". El autor no asume responsabilidad alguna por:

- El uso que se haga de los contenidos descargados.
- El cumplimiento de los **Términos de Servicio** de Spotify y Deezer.

Asegúrate de utilizar esta herramienta conforme a la legislación vigente y las políticas de ambas plataformas.

---

## 🤖 Generado con ChatGPT

Parte del código y la documentación de este proyecto fueron generados con ayuda de ChatGPT de OpenAI.

---
## 📄 Licencia

Licenciado bajo **MIT**. Consulta [LICENSE](LICENSE) para detalles.

---
## 👤 Autor

**Bryan Olmos** — [GitHub](https://github.com/BryScordia)
