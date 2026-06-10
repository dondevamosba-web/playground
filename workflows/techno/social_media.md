# Workflow: @techno.apple.ok — Social Media Posts

## Objetivo
Generar, previsualizar y publicar posts de productos Apple en Instagram y Facebook. Mercado objetivo: compradores en Olavarría que buscan productos Apple importados directamente desde USA a mejores precios que el retail local.

**Margen:** precio de venta = costo proveedor + 70 USD. Nunca publicar precios del proveedor.
**WhatsApp de contacto:** +5491162310105

## Cuenta
- Instagram: `@techno.apple.ok`
- Facebook: página vinculada a la cuenta de Business
- Account key en scripts: `--account techno`

## Tipos de contenido

| Tipo | Cuándo usarlo | Frecuencia sugerida |
|------|---------------|---------------------|
| `offer` | Producto con precio, CTA directo al WhatsApp | 3–4x por semana |
| `feature` | Destacar specs o ventajas sin enfocarse en precio | 1–2x por semana |
| `launch` | Llegada de nuevo modelo o edición | Según lanzamientos |
| `meme` | Humor de la marca para viralizar y ganar alcance | 1x por semana |

## Flujo completo

### Paso 1 — Generar posts

```bash
# Un solo post de oferta
python tools/generate_tech_posts.py \
  --brand apple \
  --product "iPhone 16 Pro Max 256GB" \
  --price "1.500.000" \
  --type offer

# Tres variaciones de feature para Samsung
python tools/generate_tech_posts.py \
  --brand samsung \
  --product "Galaxy S25 Ultra" \
  --price "1.200.000" \
  --type feature \
  --count 3

# Agregar posts sin borrar los anteriores
python tools/generate_tech_posts.py \
  --brand playstation \
  --product "PS5 Slim + 2 Joysticks" \
  --price "850.000" \
  --type launch \
  --append
```

Output: `.tmp/tech_posts.json`

### Paso 2 — Previsualizar

```bash
python tools/preview_tech_posts.py
```

Se abre `.tmp/tech_posts_preview.html` en el browser. Ahí:
1. Chequeás los posts que querés publicar
2. Hacés clic en **Generar comandos**
3. Copiás los comandos generados o me los pasás a mí para ejecutarlos

### Paso 3 — Agregar imagen (opcional pero recomendado)

Los posts necesitan una imagen pública accesible por URL para el Graph API.

Opciones:
- Diseñá en Canva → exportá → subí a Google Drive público o Cloudinary
- Usa la URL pública de la imagen

Editá `.tmp/tech_posts.json` y completá el campo `image_url` del post correspondiente antes de publicar.

### Paso 4 — Publicar

```bash
python tools/post_instagram.py \
  --account techno \
  --type single \
  --image-url "https://..." \
  --caption "Caption del post"
```

El script publica simultáneamente en Instagram y Facebook.

Para programar:
```bash
python tools/post_instagram.py \
  --account techno \
  --type single \
  --image-url "https://..." \
  --caption "..." \
  --schedule "2026-06-07T18:00:00-03:00"
```

## Calendario de contenido + auto-publicación

Alternativa al flujo manual de arriba: mantener un Google Sheet con posts programados y publicarlos automáticamente cuando llega su horario.

### Paso 1 — Crear/llenar el calendario

```bash
python3 tools/fill_content_techno.py             # genera el sheet + captions con Claude
python3 tools/fill_content_techno.py --dry-run   # preview sin escribir
```

Crea el sheet "Techno — Content Calendar" y guarda el ID en `.env` como `TECHNO_CONTENT_CALENDAR_SHEET_ID`. Misma estructura de columnas que el calendario de Ola Digital: vos completás **Media URL** y dejás Status en `pending`.

### Paso 2 — Auto-publicar

```bash
python3 tools/auto_post_techno.py            # publica lo que está vencido
python3 tools/auto_post_techno.py --dry-run  # preview
```

Ya corre automáticamente por cron a las 9:30 y 18:30 (hora AR); log en `.tmp/cron_autopost.log`. Para saltear un post, poné Status = `skip` en el sheet.

## Setup inicial (una sola vez)

Completar en `.env`:

```
TECHNO_INSTAGRAM_BUSINESS_ACCOUNT_ID=   # ID numérico del IG Business Account
TECHNO_FACEBOOK_PAGE_ID=                # ID numérico de la FB Page
TECHNO_WHATSAPP=                        # Número con código de país, ej: +5491112345678
```

El `INSTAGRAM_ACCESS_TOKEN` ya existente se reutiliza si el token del system user cubre esta cuenta.
Si no, generar uno nuevo en Meta Business Suite → System Users.

Verificar que la cuenta de IG esté en modo Business o Creator y vinculada a una FB Page.

## Hashtags por defecto

Se agregan automáticamente a lo que genera Claude:

| Marca | Hashtags |
|-------|----------|
| Apple | #apple #macbook #iphone #ios #applefan #manzanita #appleargentina |
| Local | #Olavarría #OlavarríaTech #TecnologíaOlavarría #CompraEnOlavarría |
| General | #tecnologia #tech #argentina #importadoUSA #directordeUSA #gadgets |

## Notas operativas

- Los posts generados quedan en `.tmp/tech_posts.json` hasta que se reemplaza o se usa `--append`
- El campo `approved` en el JSON es solo referencial; la aprobación real es elegir qué comandos ejecutar
- Para memes: no hace falta `--price`, solo `--brand` y `--type meme`
- Si el token vence, renovar en Meta Business Suite → System Users → Generate Token
