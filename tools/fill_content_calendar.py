#!/usr/bin/env python3
"""
Create or update the Ola Digital content calendar in Google Sheets.
Generates posts for the next N weeks with Claude-written captions.

Usage:
  python3 tools/fill_content_calendar.py                  # 4 weeks from today
  python3 tools/fill_content_calendar.py --weeks 8
  python3 tools/fill_content_calendar.py --dry-run        # print without writing
  python3 tools/fill_content_calendar.py --sheet-id XXXX  # append to existing sheet
"""

import argparse
import os
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from tools.sheets_client import get_services
from tools.claude_call import call_claude

SHEET_TITLE   = "Ola Digital — Content Calendar"
SHEET_ENV_KEY = "CONTENT_CALENDAR_SHEET_ID"

# (weekday 0=Mon, time_str AR UTC-3, post_type, content_type)
WEEKLY_SLOTS = [
    (0, "08:00", "reel",     "Reel educativo: tip o cómo hacer algo"),
    (1, "12:00", "reel",     "Reel de entretenimiento o dato sorprendente"),
    (2, "19:00", "carousel", "Carrusel guardable: lista o proceso paso a paso"),
    (3, "12:00", "reel",     "Reel de prueba social o resultado de cliente"),
    (4, "19:00", "carousel", "Carrusel o post con llamado a la acción"),
]

# Real designed posts exported from ola-digital-posts.html via
# screenshot_ola_digital_v2.py (the old pool here was bare number/title
# placeholder cards, not actual designed content — fixed 2026-07-17).
# Expanded 2026-07-21 from 13 to all 16 real singles (was missing 07/08/12,
# and single_count resets to 0 each script run, so index 0 — 01_stat_seo_local
# — kept landing on the first single-post slot of every run, producing
# visible duplicates like row 73 vs row 105).
TRIAD_CYCLE = [
    ".tmp/ola_digital_posts_v2/01_stat_seo_local.png",
    ".tmp/ola_digital_posts_v2/02_hook_sabías_que.png",
    ".tmp/ola_digital_posts_v2/03_bold_manifesto.png",
    ".tmp/ola_digital_posts_v2/04_list_errores.png",
    ".tmp/ola_digital_posts_v2/05_stat_email_marketing.png",
    ".tmp/ola_digital_posts_v2/06_versus_competencia.png",
    ".tmp/ola_digital_posts_v2/07_hook_sabías_que.png",
    ".tmp/ola_digital_posts_v2/08_bold_manifesto.png",
    ".tmp/ola_digital_posts_v2/09_list_checklist.png",
    ".tmp/ola_digital_posts_v2/10_stat_google_ads.png",
    ".tmp/ola_digital_posts_v2/11_bold_verdad_incómoda.png",
    ".tmp/ola_digital_posts_v2/12_hook_errores.png",
    ".tmp/ola_digital_posts_v2/13_versus_mentalidad.png",
    ".tmp/ola_digital_posts_v2/14_list_sitio_web.png",
    ".tmp/ola_digital_posts_v2/15_beforeafter_caso_real.png",
    ".tmp/ola_digital_posts_v2/16_stat_sitio_web.png",
]

HASHTAGS = (
    "#OlaDigital #OlaDigitalOlavarría #Olavarría #OlavarríaBsAs "
    "#PymesOlavarría #NegociosOlavarría #MarketingDigital #MarketingArgentina "
    "#AgenciaDigital #RedesSociales #SEOLocal #GoogleAds #Emprendedores #PymeArgentina"
)

BRAND_CONTEXT = """
Ola Digital es una agencia de marketing digital en Olavarría, Buenos Aires, Argentina.
Audiencia: dueños de pymes locales (gastronomía, comercios, clínicas, servicios profesionales).
Tono: profesional pero cercano, en español rioplatense (vos, ustedes).
Meta: generar leads y establecer autoridad en marketing digital local.
"""


# Haiku defaults to the same "87-89% de búsquedas locales" stat almost every
# time a stat/hook prompt is generated with no other anchor — found 2026-07-22
# after it had already posted live 4 times plus 3 more queued. Rotate through
# a fixed list of distinct angles so captions actually vary.
STAT_ANGLES = [
    "tiempo de respuesta a mensajes de Instagram/WhatsApp",
    "costo de no tener reseñas recientes en Google",
    "abandono de sitios web lentos en mobile",
    "diferencia de conversión entre negocios con y sin video en redes",
    "cuánto tarda un cliente en decidir entre dos negocios similares",
    "impacto de fotos profesionales vs. fotos de celular en redes",
    "frecuencia de posteo mínima para no perder alcance orgánico",
    "por qué un negocio con web pero sin mantenimiento pierde clientes",
]


def generate_caption(content_type: str, post_number: int) -> str:
    angle = STAT_ANGLES[(post_number - 1) % len(STAT_ANGLES)]
    prompt = f"""Escribí un caption para Instagram de Ola Digital.

{BRAND_CONTEXT}

Tipo de post: {content_type}
Número en secuencia: {post_number}
Si el post es de tipo stat/dato/hook, basalo en este ángulo específico (no inventes
otro, y sobre todo no uses el dato de "87-89% de búsquedas locales" — ya se usó
muchas veces): {angle}

Reglas:
- Máximo 120 palabras
- Primera línea: gancho fuerte (sin emojis)
- 2-3 líneas de valor concreto
- CTA al final (DM, comentario o link en bio)
- Sin hashtags (se agregan aparte)
- Tono directo, sin jerga vacía
- No empieces con pregunta (no arrancás con ¿ ni con ?)
- Arrancá con una afirmación, dato, o hecho concreto

Devolvé solo el texto del caption, sin comillas ni explicaciones."""

    return call_claude(prompt, model="haiku")


def build_rows(start: date, weeks: int, dry_run: bool, single_count: int = 0) -> list[list]:
    rows = []
    for week in range(weeks):
        for weekday, time_str, post_type, content_type in WEEKLY_SLOTS:
            days_offset = (week * 7) + (weekday - start.weekday()) % 7
            post_date = start + timedelta(days=days_offset)
            post_number = week * len(WEEKLY_SLOTS) + WEEKLY_SLOTS.index(
                (weekday, time_str, post_type, content_type)
            ) + 1

            if dry_run:
                caption = f"[Caption para: {content_type}]"
            else:
                print(f"  [{post_date} {time_str}] {content_type}...")
                caption = generate_caption(content_type, post_number)

            # No video pipeline exists yet, so every slot posts as a single
            # image (triad cycle) regardless of the reel/carousel label —
            # that label still shapes the caption via content_type above.
            media_url = TRIAD_CYCLE[single_count % len(TRIAD_CYCLE)]
            single_count += 1
            effective_post_type = "single"

            rows.append([
                post_date.isoformat(),
                time_str,
                post_date.strftime("%A"),
                content_type,
                effective_post_type,
                caption,
                HASHTAGS,
                media_url,
                "pending",
                "",          # Post ID — auto_post fills this
            ])

    rows.sort(key=lambda r: r[0] + r[1])
    return rows


def create_sheet(drive, title: str) -> str:
    f = drive.files().create(
        body={"name": title, "mimeType": "application/vnd.google-apps.spreadsheet"},
        fields="id",
    ).execute()
    return f["id"]


def write_to_sheet(sheets, sheet_id: str, rows: list[list]):
    header = [
        "Date", "Time (AR)", "Day", "Content Type", "Post Type",
        "Caption", "Hashtags", "Media URL", "Status", "Post ID",
    ]
    existing = sheets.spreadsheets().values().get(
        spreadsheetId=sheet_id, range="A1:J1"
    ).execute().get("values", [])

    if not existing:
        sheets.spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range="A1",
            valueInputOption="RAW",
            body={"values": [header]},
        ).execute()

    sheets.spreadsheets().values().append(
        spreadsheetId=sheet_id,
        range="A1",
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body={"values": rows},
    ).execute()


def save_sheet_id(sheet_id: str):
    env_path = ROOT / ".env"
    content = env_path.read_text()
    if SHEET_ENV_KEY + "=" in content:
        lines = [
            f"{SHEET_ENV_KEY}={sheet_id}" if l.startswith(SHEET_ENV_KEY + "=") else l
            for l in content.splitlines()
        ]
        env_path.write_text("\n".join(lines) + "\n")
    else:
        with open(env_path, "a") as f:
            f.write(f"\n{SHEET_ENV_KEY}={sheet_id}\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--weeks",    type=int, default=4)
    parser.add_argument("--sheet-id", help="Existing sheet ID (overrides .env)")
    parser.add_argument("--dry-run",  action="store_true")
    args = parser.parse_args()

    start = date.today() + timedelta(days=1)
    total = args.weeks * len(WEEKLY_SLOTS)

    # Continue the image cycle from where the sheet already left off instead
    # of always restarting at index 0 — otherwise every top-up run reclusters
    # repeats within days of each other instead of spacing them ~3+ weeks
    # apart (found 2026-07-22: the "89% stat" investigation surfaced this).
    single_count = 0
    sheet_id = args.sheet_id or os.getenv(SHEET_ENV_KEY)
    if sheet_id and not args.dry_run:
        sheets_probe, _ = get_services()
        existing = sheets_probe.spreadsheets().values().get(
            spreadsheetId=sheet_id, range="H2:H10000"
        ).execute().get("values", [])
        single_count = sum(1 for r in existing if r and r[0].strip())

    print(f"Generating {total} posts across {args.weeks} weeks (from {start})...")
    rows = build_rows(start, args.weeks, args.dry_run, single_count)

    if args.dry_run:
        print("\n── Preview ─────────────────────────────────────────────")
        for r in rows:
            print(f"  {r[0]} {r[1]}  [{r[4]}] {r[3]}")
            print(f"    {r[5][:80]}...")
        print(f"\n  Total: {len(rows)} posts")
        return

    sheets, drive = get_services()

    if not sheet_id:
        print(f"Creating Google Sheet: '{SHEET_TITLE}'...")
        sheet_id = create_sheet(drive, SHEET_TITLE)
        save_sheet_id(sheet_id)
        print(f"  Sheet ID saved to .env as {SHEET_ENV_KEY}")

    print(f"Writing {len(rows)} rows...")
    write_to_sheet(sheets, sheet_id, rows)
    print(f"\nDone! https://docs.google.com/spreadsheets/d/{sheet_id}")
    print("\nNext step: add Media URLs to each row, then run:")
    print("  python3 tools/auto_post_from_calendar.py")


if __name__ == "__main__":
    main()
