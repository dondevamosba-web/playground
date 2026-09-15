# Handoff — 2026-07-21

Estado del pipeline de Instagram al momento del traspaso.

---

## ✅ Hecho en esta sesión

| Tarea | Estado |
|-------|--------|
| Fiestas — 2 entradas rotas (video thumbnails) marcadas como `skip` | ✅ |
| Ola Digital — calendario rellenado 5 semanas en el sheet | ✅ |
| Ola Empleo — 105 posts generados en el sheet | ✅ |
| Fiestas — 14 posts publicados (11 borrar a mano en la app) | ⚠️ VER NOTA |
| `generate_techno_cards.py` — fix para usar image cache en vez de text cards | ✅ (en disco) |

**NOTA FIESTAS:** Se publicaron 14 posts scrapeados sin revisión. Solo 3 se pudieron borrar por API. Los otros 11 hay que borrarlos manualmente en la app de @fiestaselectronicasbuenosaires.

---

## ❌ Pendiente en la otra PC

### 1. Techno — regenerar cards con imágenes reales

197 filas pendientes tienen paths de `_text.png` en col I. Hay que limpiarlos para que `generate_techno_cards.py` los regenere usando el cache de imágenes (`/.tmp/techno_image_cache.json`).

```bash
cd ~/Downloads/playground

# Limpiar paths de text cards del sheet (dejar col I vacía en filas no posted)
python3 -c "
import sys, os
sys.path.insert(0, 'tools')
from dotenv import load_dotenv
load_dotenv('.env')
from tools.sheets_client import get_services
sheets, _ = get_services()
sid = os.getenv('TECHNO_CONTENT_CALENDAR_SHEET_ID')
result = sheets.spreadsheets().values().get(spreadsheetId=sid, range='A2:K400').execute()
rows = result.get('values', [])
clears = []
for i, row in enumerate(rows):
    status = row[9].strip() if len(row)>9 else ''
    media  = row[8].strip() if len(row)>8 else ''
    if status != 'posted' and media.endswith('_text.png'):
        clears.append({'range': f'I{i+2}', 'values': [['']]})
sheets.spreadsheets().values().batchUpdate(
    spreadsheetId=sid,
    body={'valueInputOption': 'RAW', 'data': clears}
).execute()
print(f'{len(clears)} paths limpiados')
"

# Regenerar cards (ahora usa cache de imágenes, no text fallback)
python3 tools/generate_techno_cards.py
```

### 2. Talento USA — fill de calendario falló

El script `fill_content_talento_usa.py` crasheó por error de auth en Claude CLI. Posiblemente falta `ANTHROPIC_API_KEY` en `.env` o el CLI no está autenticado.

```bash
# Verificar API key
grep ANTHROPIC .env

# Si no está, agregar:
echo 'ANTHROPIC_API_KEY=sk-...' >> .env

# Correr de nuevo
python3 tools/fill_content_talento_usa.py --weeks 5
```

### 3. Ola Digital — agregar Media URLs al calendario

El fill escribió 25 filas con slots de contenido pero sin imágenes. Hay que agregarles la URL del archivo de imagen correspondiente de `.tmp/ola_digital_posts_v2/` y después correr:

```bash
python3 tools/auto_post_from_calendar.py
```

---

## Estado de cada cuenta

| Cuenta | ¿Posteando? | Notas |
|--------|------------|-------|
| **Storm** | ✅ Sí | Funciona, postea 1x día |
| **Techno** | ⚠️ Sí pero con text cards | Fix listo, falta correr regeneración |
| **Ola Digital** | ⚠️ Calendario rellenado, falta media | Correr auto_post_from_calendar.py |
| **Ola Empleo** | ✅ Calendar lleno | Debería arrancar solo con el cron |
| **Talento USA** | ❌ Calendar vacío | fill_content falló, ver punto 2 |
| **Fiestas** | ✅ Parcial | Funciona, pero borrar 11 posts a mano |

---

## Cómo funciona el pipeline

```
launchd (com.playground.publish-one-each)
  → corre a las 11:00, 15:00, 18:00 AR
  → tools/publish_one_each.py
      → lee cada sheet de cada cuenta
      → publica 1 post por cuenta si hay algo "due"
      → sube imagen a Drive → postea a IG via Graph API
```

Sheets de cada cuenta:
- Ola Digital: `CONTENT_CALENDAR_SHEET_ID`
- Storm: `STORM_CONTENT_CALENDAR_SHEET_ID`
- Techno: `TECHNO_CONTENT_CALENDAR_SHEET_ID`
- Ola Empleo: `OLA_EMPLEO_CALENDAR_SHEET_ID`
- Talento USA: `TALENTO_USA_CALENDAR_SHEET_ID`
- Fiestas: `FIESTAS_APPROVAL_SHEET_ID` (tab Queue)

---

## Cuentas de Instagram

| Cuenta | Handle |
|--------|--------|
| Ola Digital | @oladigitalok |
| Ola Empleo | @olavarria.empleo |
| Talento USA | @talento.remoto.usa |
| Storm | @storm.mkt.agency |
| Techno | @techno.apple.ok |
| Fiestas | @fiestaselectronicasbuenosaires |

---

## Bugs conocidos pendientes

- **Ola Digital barras blancas**: el screenshot de `screenshot_ola_digital_v2.py` captura cards con dimensiones incorrectas → IG agrega letterbox. Investigar dimensiones de `.dc-card` en `ola-digital-posts.html`.
- **Techno text cards ya publicadas**: los posts con texto en vez de imagen que están live en @techno.apple.ok no se pueden deshacer. Los próximos deberían salir con imagen una vez corrida la regeneración.
