#!/usr/bin/env python3
"""
Check if an event is already queued in other accounts before publishing.

Prevents same event from being published multiple times across different accounts
within a short time window (e.g., 7 days).

Called by publisher before posting. Returns 0 if OK, 1 if duplicate found.

Usage:
  python3 tools/cross_account_dedup.py --event "Hot Since 82" --date 2026-09-18 --account fiestas
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

ACCOUNT_SHEETS = {
    "fiestas": ("FIESTAS_APPROVAL_SHEET_ID", "Queue"),
    "techno": ("FIESTAS_APPROVAL_SHEET_ID", "Queue"),
    "storm": ("FIESTAS_APPROVAL_SHEET_ID", "Queue"),
    "ola_digital": ("FIESTAS_APPROVAL_SHEET_ID", "Queue"),
    "ola_empleo": ("FIESTAS_APPROVAL_SHEET_ID", "Queue"),
    "talento_usa": ("FIESTAS_APPROVAL_SHEET_ID", "Queue"),
}
# NOTE (2026-07-30): the other 5 accounts each have their own spreadsheet
# (TECHNO_CONTENT_CALENDAR_SHEET_ID, STORM_CONTENT_CALENDAR_SHEET_ID,
# CONTENT_CALENDAR_SHEET_ID for Ola Digital, OLA_EMPLEO_CALENDAR_SHEET_ID,
# TALENTO_USA_CALENDAR_SHEET_ID) with a Date/Product/Status schema that has
# no "event name" concept comparable to Fiestas' venue events - comparing
# across them was never meaningful. This previously hardcoded a "Hoja 1" tab
# that doesn't exist on the Fiestas sheet, which crashed on every call and
# made the caller (publish_fiestas_next.py) treat every row as a duplicate.
# Scoped down to checking within Fiestas' own Queue tab instead, which is
# where real duplicates actually happen (same event scraped from multiple
# venue/source accounts). See project-fiestas-pipeline.md memory.


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--event", required=True, help="Event name to check")
    p.add_argument("--date", required=True, help="Event date (YYYY-MM-DD)")
    p.add_argument("--account", required=True, choices=list(ACCOUNT_SHEETS.keys()))
    p.add_argument("--window", type=int, default=7, help="Days to look back/ahead")
    args = p.parse_args()

    event_date = args.date
    sheets, _ = get_services()
    sid = os.environ["FIESTAS_APPROVAL_SHEET_ID"]

    # Date range: event_date ± window days
    d = [int(x) for x in event_date.split("-")]
    center = date(d[0], d[1], d[2])
    start = (center - timedelta(days=args.window)).isoformat()
    end = (center + timedelta(days=args.window)).isoformat()

    duplicates = []

    # Only Fiestas' own Queue tab is checked (see NOTE above) - the row being
    # published is never itself "posted" yet, so restricting to status ==
    # "posted" here can't spuriously match the row against itself.
    rows = sheets.spreadsheets().values().get(
        spreadsheetId=sid, range="Queue!A2:N600").execute().get("values", [])

    for i, r in enumerate(rows, 2):
        if len(r) < 12:
            continue
        post_date = (r[3] or "").strip()
        post_name = (r[2] or "").strip()
        status = (r[11] or "").strip().lower()

        if status != "posted":
            continue

        # Check if date and event name match
        if post_date and start <= post_date <= end:
            if args.event.lower() in post_name.lower():
                duplicates.append({
                    "account": "fiestas",
                    "name": post_name,
                    "date": post_date,
                    "row": i,
                })
                print(f"⚠️  DUPLICATE: row {i} already posted: {post_name} ({post_date})")

    if duplicates:
        print(f"\nFOUND {len(duplicates)} duplicate(s). Do not publish to avoid audience fatigue.")
        return 1

    print(f"✓ No duplicates found for '{args.event}' ({event_date})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
