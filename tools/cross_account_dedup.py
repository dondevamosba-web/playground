#!/usr/bin/env python3
"""
Check if an event is already queued/posted before publishing.
Returns 0 if OK, 1 if duplicate found. Window default ±7 days.

CAMBIO: el matching ya no es substring exacto sobre el nombre crudo.
Ahora usa tools.event_normalize.is_same_event(), que compara por
venue+fecha normalizados (con fallback a similitud de nombre por tokens).
Esto es lo que dejó pasar "Agents Of Time, Yotto, Jast en Mandarine Tent"
como si no fuera duplicado de "Agents Of Time & MORE ARTISTS [TIME MACHINE]".

Para usar el matching también hay que pasar --venue (opcional pero
recomendado: sin venue, cae a comparación solo por nombre con threshold
más exigente).
"""
import argparse, os, sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
from dotenv import load_dotenv
load_dotenv(ROOT / ".env")
from tools.sheets_client import get_services
from tools.event_normalize import is_same_event


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--event", required=True)
    p.add_argument("--date", required=True)
    p.add_argument("--venue", default="", help="Recomendado: mejora mucho el matching")
    p.add_argument("--account", required=True)
    p.add_argument("--window", type=int, default=7)
    args = p.parse_args()

    d = [int(x) for x in args.date.split("-")]
    center = date(d[0], d[1], d[2])
    start = (center - timedelta(days=args.window)).isoformat()
    end = (center + timedelta(days=args.window)).isoformat()

    sheets, _ = get_services()
    sid = os.environ["FIESTAS_APPROVAL_SHEET_ID"]
    rows = sheets.spreadsheets().values().get(
        spreadsheetId=sid, range="Queue!A2:N600").execute().get("values", [])

    duplicates = []
    for i, r in enumerate(rows, 2):
        if len(r) < 12:
            continue
        post_date = (r[3] or "").strip()
        post_name = (r[2] or "").strip()
        post_venue = (r[4] or "").strip() if len(r) > 4 else ""
        status = (r[11] or "").strip().lower()
        if status != "posted":
            continue
        if post_date and not (start <= post_date <= end):
            continue
        if is_same_event(args.event, args.venue, args.date,
                          post_name, post_venue, post_date):
            duplicates.append({"name": post_name, "date": post_date, "row": i})
            print(f"⚠️  DUPLICATE: row {i} already posted: {post_name} ({post_date})")

    if duplicates:
        print(f"\nFOUND {len(duplicates)} duplicate(s).")
        return 1
    print(f"✓ No duplicates found for '{args.event}' ({args.date})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
