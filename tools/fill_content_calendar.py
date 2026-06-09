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


def generate_caption(content_type: str, post_number: int) -> str:
    prompt = f"""Escribí un caption para Instagram de Ola Digital.

{BRAND_CONTEXT}

Tipo de post: {content_type}
Número en secuencia: {post_number}

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


def build_rows(start: date, weeks: int, dry_run: bool) -> list[list]:
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

            rows.append([
                post_date.isoformat(),
                time_str,
                post_date.strftime("%A"),
                content_type,
                post_type,
                caption,
                HASHTAGS,
                "",          # Media URL — user fills this
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

    print(f"Generating {total} posts across {args.weeks} weeks (from {start})...")
    rows = build_rows(start, args.weeks, args.dry_run)

    if args.dry_run:
        print("\n── Preview ─────────────────────────────────────────────")
        for r in rows:
            print(f"  {r[0]} {r[1]}  [{r[4]}] {r[3]}")
            print(f"    {r[5][:80]}...")
        print(f"\n  Total: {len(rows)} posts")
        return

    sheets, drive = get_services()
    sheet_id = args.sheet_id or os.getenv(SHEET_ENV_KEY)

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
