# Techno (@techno.apple.ok) — context handoff

Paste this at the start of a new session to restore context on the `@techno.apple.ok` IG pipeline.

**Last Updated**: 2026-07-31

---

## Ubicación y acceso

- Proyecto: `C:\Users\Guido\Dropbox\playground` (NO OneDrive). Mac project corriendo en Windows:
  usar `.venv-win\Scripts\python.exe`, y siempre `PYTHONIOENCODING=utf-8` antes de correr
  cualquier script (consola es cp1252, se cuelga con ✓/— en un print).
- Sheet: env var `TECHNO_CONTENT_CALENDAR_SHEET_ID` en `.env` = 
  `1QTJ81L7WVFjOglHeUbOLAjKYrqoYxwym-mx8RzFKvEI`
  Columnas: A=Date B=Time C=Day D=Product E=Brand F=Post Type G=Caption
  H=Hashtags I=Media URL J=Status K=Post ID
- Cards generadas en `.tmp\techno_cards\tNNN_*.png` (NNN = fila del sheet) por
  `tools/generate_techno_cards.py`, función `make_photo_card(product, caption, photo, sheet_row)`
  — sobreescribe el PNG si se le pasa el mismo row.
- Publica automático `tools/auto_post_techno.py` vía Windows Task Scheduler (`IG_publish_techno`),
  trata "pending" y "approved" igual para publicar — aprobar en el sheet solo documenta que Guido
  ya revisó, no controla si se publica. **Las 7 tareas programadas de las 6 cuentas estaban
  pausadas a propósito desde el 29/07** (limpieza de performance de PC) — chequear
  `schtasks /query /tn "IG_publish_techno"` antes de asumir que está publicando sola.

## Bug de sourcing de imágenes (encontrado 29/07/2026)

El generador cachea UNA sola foto por familia de producto en `.tmp/techno_image_cache.json`
(fuzzy match por nombre) → productos distintos de la misma familia terminaban con la foto
idéntica, y peor: mezclas de producto (iPhone 16 Plus mostrando una caja de PS5, cargador
MagSafe mostrando un teclado mecánico con anime, MacBook Pro M4 mostrando chips M5).

**Causa raíz**: las URLs de bbystatic (BestBuy) reciclan IDs de producto con el tiempo, y el
microsite "vivo" de `apple.com/v/<producto>/.../highlights/` cambia de contenido bajo el mismo
link cuando Apple lanza una generación nueva — no son URLs estables.

**Fuente segura**: `apple.com/newsroom/<año>/<mes>/<slug>/article/...` (press release fechado,
no cambia). Usar siempre esto, no bbystatic ni el microsite vivo, para cualquier imagen de
producto Apple que se vaya a reusar o cachear.

**Importante**: el chequeo de duplicados por hash NO detecta este bug (dos fotos con hash
distinto, ambas equivocadas, pasan el check igual) — hay que mirar la card renderizada a ojo,
no solo comparar hashes, cuando haya productos de la misma familia en el lote.

## Estado a la fecha 29/07/2026

- 30 posts pendientes (28/jul–06/ago) aprobados, 9 imágenes reemplazadas por newsroom.apple.com,
  0 duplicados por hash, 0 productos equivocados a ojo tras revisión.
- Pendiente sin resolver: cargador MagSafe (filas 369 y 394) con la MISMA foto en ambas — no se
  encontró segunda foto confiable de cargador a tiempo.
- Historial ya publicado (últimos 15 posts) no se tocó — ahí quedan duplicados conocidos ya
  marcados a mano como "dup-manual (already live 3x)": iPhone 16 Pro Max 256GB posteado 6 veces,
  iPhone 16 Pro 128GB 2 veces.
- 15 filas "pending" sin producto ni imagen cargada (datos vacíos), quedaron afuera de la revisión.
- Ledger real (`TECHNO_LEDGER_ID`) tiene solo 2 filas cargadas (una es venta de prueba con
  comprador "test") — no sirve todavía como fuente de stock en vivo para nada.

## Sitio web (creado 30/07/2026)

GitHub Pages: https://dondevamosba-web.github.io/techno-site/ (repo `dondevamosba-web/techno-site`,
público). Como el ledger está casi vacío, el catálogo del sitio se armó con los ~56 productos
distintos que aparecen en el calendario de contenido (iPhone, Mac, iPad, Watch, AirPods, Samsung,
PlayStation), agrupados por categoría, con CTA a WhatsApp (`wa.me/5491162310105`) para consultar
stock/precio real — igual que ya hacen en sus propias captions. Si el ledger se puebla de verdad,
regenerar el catálogo desde ahí en vez del calendario.

## Dashboard visual de la revisión del 29/07

https://claude.ai/code/artifact/5e5b5402-d446-4c26-9a5e-e2355301c56e
