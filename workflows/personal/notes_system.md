# Sistema de notas — WhatsApp → RAG → Notion → propuestas

## Objetivo
Que las notas que me mando en los 3 chats (Psi / Ide / Vida) se ordenen solas, se puedan buscar desde
Claude, se sincronicen con Notion sin duplicar y el sistema me proponga qué hacer.

## Cómo fluye
```
WhatsApp ──(bridge, solo lectura)──┐
Exports .zip (~/Downloads/whatsapp)┴─► notes_rag.py ─► .tmp/notes_rag/notes.db (SQLite + búsqueda)
                                                   ├─► enrich_links.py  (títulos + temas de los links)
                                                   ├─► notion_sync.py   (↔ base "Pendientes")
                                                   ├─► notes_mcp.py     (Claude Code lo consulta: MCP "notas")
                                                   └─► weekly_review.py (propuestas + notificación)
```

## Herramientas
| Herramienta | Qué hace |
|---|---|
| `tools/whatsapp_digest.py` | Parser y clasificador (tags, tareas, duplicados, fuera de lugar). Lo usan todas. |
| `tools/notes_rag.py` | `ingest`, `search`, `pending`, `propose [--llm]`, `watch`. |
| `tools/notes_mcp.py` | Servidor MCP de solo lectura: `buscar_notas`, `pendientes`, `propuestas`, `notas_recientes`. Registrado en `.mcp.json`. |
| `tools/notion_sync.py` | Baja los "Hecho" de Notion y sube tareas nuevas (Clave = no duplica). Nunca edita ni borra filas. |
| `tools/enrich_links.py` | Título de cada link (oEmbed de YouTube / X / TikTok, og:title en el resto) → `links.md` por tema. |
| `tools/weekly_review.py` | Todo junto → `.tmp/notes_rag/review-FECHA.md`. |
| `tools/whatsapp_bridge.sh` | Instala el bridge de WhatsApp en la Mac, en modo solo lectura. |
| `tools/notes_schedule.sh` | launchd: revisión los domingos 10:00, sync con Notion cada hora. |
| `/whatsapp` | Comando de Claude Code: corre la revisión y me da 3 cosas para hoy. |

## Puesta en marcha (Mac)
1. `.env` (no va a git):
   ```
   NOTION_TOKEN=secret_...           # notion.so/profile/integrations → nueva integración interna
   NOTION_PENDIENTES_DB=0987fdfa4c0c47e9ad1517b5dd945528
   WHATSAPP_EXPORTS_DIR=~/Downloads/whatsapp   # opcional
   ```
   En Notion: base **Pendientes** → ⋯ → Conexiones → agregar la integración.
2. Elegir la fuente:
   - **Exports** (sin riesgo): exportar los 3 chats a `~/Downloads/whatsapp/`.
   - **Bridge** (automático): `bash tools/whatsapp_bridge.sh install && bash tools/whatsapp_bridge.sh link && bash tools/whatsapp_bridge.sh start`.
3. `bash tools/notes_schedule.sh install`.
4. Abrir Claude Code en el repo y aprobar el MCP "notas" la primera vez.

## Puesta en marcha (Windows, PowerShell en la carpeta del repo)
```powershell
python -m pip install -r requirements.txt
python tools\windows_setup.py check           # qué falta
python tools\windows_setup.py env             # pide el token de Notion (oculto) y escribe .env sin BOM
python tools\notion_sync.py --dry-run         # prueba: ~60 filas, 0 creadas
python tools\windows_setup.py schedule        # Programador de tareas: domingo 10:00 + sync cada hora
# Opcional, bridge de WhatsApp (necesita Git, Go y gcc de MSYS2; el script dice qué instalar con winget):
python tools\windows_setup.py bridge-install
python tools\windows_setup.py bridge-link     # QR
python tools\windows_setup.py bridge-start    # oculto, y arranca en cada inicio de sesión
```
- Las tareas programadas usan `pythonw.exe` (sin ventana) + `tools/run_logged.py`: la salida y los errores
  quedan en `.tmp/notes_rag/logs/<script>.log`.
- La notificación de Windows es un globo en la bandeja del sistema.
- `.mcp.json` usa `python` (en Windows `python3` suele ser el acceso directo a la Microsoft Store).
- `tools/devex_setup.sh` es bash: en Windows se corre desde Git Bash.

## Reglas
- `--llm` hace una llamada paga a Claude: solo cuando lo pido.
- Solo se crean en Notion tareas anotadas desde el 28/9/2026: lo anterior se cargó a mano.
- El bridge guarda **todos** los chats en `~/whatsapp-mcp/whatsapp-bridge/store/messages.db`; el RAG lee solo
  mis mensajes de los 3 chats.

## Aprendizajes
- El bridge de lharries/whatsapp-mcp levanta un servidor REST en `:8080` (todas las interfaces, sin auth) con
  `/api/send`. `whatsapp_bridge.sh` lo desactiva antes de compilar y está fijado al commit `7d6a06d`, que fue
  el que se revisó. Para actualizarlo: revisar el diff nuevo, cambiar `COMMIT` y verificar que el parche siga aplicando.
- go-sqlite3 guarda los timestamps como `2026-09-27 15:04:05-03:00`. Se usa la hora local tal cual.
- Instagram suele bloquear las lecturas anónimas: esos links quedan "sin título" y se reintentan a los 7 días.
- La búsqueda usa FTS5 con `remove_diacritics`, así que "panaderia" encuentra "panadería".
- Tests: `python3 -m unittest discover tests` (36 tests, con datos inventados: nada personal en el repo).
- Windows: `/TR` de schtasks admite hasta 261 caracteres; por eso `run_logged.py` arma la ruta del log solo.
  Un `.env` escrito con `Out-File` sin `-Encoding ascii` lleva BOM y rompe la primera clave:
  `windows_setup.py env` lo escribe sin BOM.
- En Windows el bridge necesita CGO (`CGO_ENABLED=1`) y el gcc de MSYS2 (`C:\msys64\ucrt64\bin`) para go-sqlite3.
