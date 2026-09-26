#!/usr/bin/env python3
"""
Mark old, never-published rows of a content calendar as "skip" so they stop
showing up as pending/stuck (e.g. offers with outdated prices).

Touches rows whose Status is approved / pending / empty and whose
Date is more than --older-than days ago. Posted, skipped or rejected rows are
never touched. Always run with --dry-run first.

  python3 tools/skip_stale_posts.py --account Techno --dry-run
  python3 tools/skip_stale_posts.py --account Techno
"""

import argparse
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from tools.sheets_client import get_services
from tools.posting_sources import CALENDARS, col_letter

STALE = {"", "pending", "approved"}  # preview_sent is left alone: someone may still be reviewing it


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--account", required=True, choices=list(CALENDARS))
    parser.add_argument("--older-than", type=int, default=3, help="days (default 3)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    c = CALENDARS[args.account]
    cutoff = (date.today() - timedelta(days=args.older_than)).isoformat()
    sheets, _ = get_services()
    rows = sheets.spreadsheets().values().get(
        spreadsheetId=c["sheet_id"], range="A1:Z2000").execute().get("values", [])

    updates = []
    for i, row in enumerate(rows[1:], start=2):
        row = row + [""] * (26 - len(row))
        status = row[c["status"]].strip().lower()
        if status in STALE and row[c["date"]][:4].isdigit() and row[c["date"]] < cutoff:
            updates.append({"range": f"{col_letter(c['status'])}{i}", "values": [["skip"]]})
            print(f"fila {i}: {row[c['date']]} {status:>12} -> skip  {row[3][:40]}")

    if updates and not args.dry_run:
        sheets.spreadsheets().values().batchUpdate(
            spreadsheetId=c["sheet_id"], body={"valueInputOption": "RAW", "data": updates}
        ).execute()
    print(f"\n{len(updates)} fila(s) {'a pasar a skip (dry-run)' if args.dry_run else 'pasadas a skip'} en {args.account} (fecha anterior a {cutoff}).")


if __name__ == "__main__":
    main()
