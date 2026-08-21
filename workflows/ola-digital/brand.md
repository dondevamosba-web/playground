# Ola Digital — brand

## Language
`es` (español rioplatense, sin anglicismos innecesarios — "publicidad en redes" antes que "social ads")

## What this is
Agencia de marketing digital en Olavarría, Buenos Aires. Vende Meta Ads + funnels de WhatsApp + gestión de redes a pymes locales (gastronomía, comercios, clínicas, servicios profesionales). Cero presencia SEO — Instagram es el canal de ventas.

## Audience
Dueños de pyme en Olavarría (110k habitantes) que hoy usan Instagram como catálogo de fotos, no como herramienta de captación. No saben qué es CPL o ROAS, pero sienten que "no les está funcionando" la publicidad. Ningún competidor local (Studio Concept, 3D Gráfica) les habla de resultados — les hablan de diseño.

## Voice
Directo, orientado a resultados, sin jerga de agencia, con un toque de confrontación local ("le hablo a vos, dueño de la pizzería de la esquina"). Cinco adjetivos: directo, local, provocador, concreto, sin vueltas.

- Publicaría: "Tu negocio no tiene señal." / "3 cambios. Y leads en 30 días."
- Nunca publicaría: "Potenciamos tu marca a través de soluciones 360° de comunicación integral."
- Preguntas en español: solo el `?` de cierre, nunca el `¿` de apertura.
- Nunca usar el patrón "No es X, es Y" ni "No solo X, sino Y" — afirmar Y directo.

## Colours — CONFIRMADOS, fuente real de verdad
Tomados directo de `ola-digital-posts.html` (raíz de `playground`), el archivo que efectivamente generó las imágenes que ya se están posteando (ver `tools/screenshot_ola_digital_v2.py` → `.tmp/ola_digital_posts_v2/*.png`, subidas por `auto_post_from_calendar.py` con Post ID real en el Content Calendar). No son una interpretación — son los tokens reales.

| Role | Hex | Use |
|---|---|---|
| Base | `#0F172A` | Fondo principal, `html`/`body` |
| Base alt | `#0B1220` | Variante más oscura (paneles) |
| Panel | `#172033` | Paneles secundarios (ej. cards before/after) |
| Blue | `#0EA5E9` | Acento primario |
| Blue dim | `#0284C7` | Blue en hover/estado apagado |
| Orange | `#F97316` | Acento secundario — se alterna con blue **por poster completo**, nunca mezclados en el mismo poster |
| White | `#FFFFFF` | Headline |
| Muted | `rgba(255,255,255,.62)` | Body/eyebrow secundario |
| Muted 2 | `rgba(255,255,255,.42)` | Texto terciario |
| Line | `rgba(255,255,255,.10)` | Separadores (ej. entre ítems de lista) |

**Descartado — no reintroducir:** el "rediseño señal" naranja-sobre-negro-puro (`#0B0E13`/`#FF5A1F`/Bahnschrift) de una sesión anterior, y la variante "cream"/"ocean #1E3A5F" de `ola-digital-posts-colors.html`. Ninguno de los dos es lo que se posteó nunca — ver `workflows/ola-digital/posts-señal/` (v1, con esa paleta vieja) vs. `workflows/ola-digital/posts-señal-v2/` (correcta, usar esta).

## Type
- **Fuente única:** `Inter`, variable font, todos los pesos vía `font-variation-settings`/CSS `font-weight` (100–900)
- **No está instalada localmente** — vendorizada en `workflows/ola-digital/posts-señal-v2/fonts/Inter-Variable.woff2`, referenciada con path relativo (`url('fonts/Inter-Variable.woff2')`, `format('woff2-variations')`). No linkear Google Fonts CDN.
- Escala (de `ola-digital-posts.html`): eyebrow 18px/700/uppercase/.22em · h1 84–120px/900/-.035em · h2 64px/800 · h3 44px/800 · lede 30px/500 muted · body 26px/500 muted · stat gigante 360px/900 (460px en variante "scream")

## Layout (estructura real, no improvisar otra)
Board fijo 1080×1080 o 1080×1350. Tres bloques verticales:
1. **Head** — wordmark "● OLA DIGITAL" (dot blue + texto blanco, 800/22px/.16em) a la izquierda; tag de categoría (muted, 15px, uppercase, .18em) a la derecha. Padding ~90-100px arriba.
2. **Body** — centrado verticalmente. Eyebrow + headline (o stat gigante, o lista numerada `.od-list`). Padding lateral 140-180px.
3. **Foot** — texto muted a la izquierda (`oladigital.com.ar` por defecto, o fuente del dato, o "Cliente real · Olavarría"), CTA/arrow en el color de acento a la derecha (`Escribinos →`).

## Handle & CTA
`@oladigitalok` (confirmado en el perfil real de Instagram). Sitio: `oladigital.com.ar`. CTA siempre a WhatsApp (nunca DM de Instagram ni formulario) — "Escribinos", "Diagnóstico gratis", "Hablemos".

## Formats in use
Square 1080×1080 es lo que se viene usando. El Content Calendar (Google Sheet, ID en `.env` como `CONTENT_CALENDAR_SHEET_ID`) programa 5 posts/semana (Lun 8:00, Mar 12:00, Mié 19:00, Jue 12:00, Vie 19:00) — ver `content_calendar_autopost.md`. Todo sale como `post_type=single` aunque la columna Content Type diga "reel" o "carrusel" (no hay pipeline de video todavía).

## Do not
- No prometer "10K seguidores en 30 días" ni cualquier atajo de crecimiento
- No usar jerga tipo "solución 360°", "potenciar tu marca", "sinergia"
- No mostrar datos reales de clientes sin anonimizar
- No hashtags genéricos tipo #marketing en el set de hashtags (sí se puede usar `#marketing` como gancho/ejemplo dentro del headline, como en Señal 05)
- No repetir el dato "87-89% de búsquedas locales" — ya se usó muchísimas veces en el calendar (ver comentario en `tools/fill_content_calendar.py`)
- No poner Status en "approved" al cargar contenido nuevo al Sheet — siempre "pending". Guido revisa y aprueba a mano (una vez se subieron 14 posts sin revisar y 11 no se pudieron borrar por API)

## Reference posts
- `ola-digital-posts.html` (raíz de playground) — la fuente de verdad real, ya generó 59+ posts publicados. Copiar su sistema de tokens/layout siempre, no reinventar.
- `workflows/ola-digital/posts-señal-v2/señal-01.html` a `señal-06.html` — implementación de la serie "Señal" (un error concreto de Instagram por post) sobre ese sistema real. Cargados al Content Calendar como filas `pending` para 2026-08-26 → 2026-09-02.
- `.tmp/ola_digital_posts_v2/*.png` — pool histórico de 16 posts (stat/hook/list/manifesto/versus/beforeafter) que el calendar viene reciclando desde mayo. Ya completó un ciclo completo (146 filas) — la serie Señal es contenido nuevo para no seguir repitiendo estas 16 imágenes.
