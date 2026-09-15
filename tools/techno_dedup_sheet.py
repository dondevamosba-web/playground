#!/usr/bin/env python3
"""
Remove duplicate date+time slots from the Techno content calendar.
For each (date, time) slot:
  - Always keep rows with status=posted
  - Among pending rows, keep only the one with the highest row number (newest)
  - Delete the rest

Usage:
  python3 tools/techno_dedup_sheet.py --dry-run
  python3 tools/techno_dedup_sheet.py
"""

import argparse
import os
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from tools.sheets_client import get_services

SHEET_ENV_KEY = "TECHNO_CONTENT_CALENDAR_SHEET_ID"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    sheets, _ = get_services()
    sheet_id = os.getenv(SHEET_ENV_KEY)

    result = sheets.spreadsheets().values().get(
        spreadsheetId=sheet_id, range="A2:K500"
    ).execute()
    rows = result.get("values", [])

    def col(row, i):
        return row[i].strip() if i < len(row) else ""

    # Group by (date, time): list of (sheet_row_number, status, product)
    slots = defaultdict(list)
    for i, row in enumerate(rows):
        sheet_row = i + 2
        date = col(row, 0)
        time = col(row, 1)
        product = col(row, 3)
        status = col(row, 9)
        if not date or not time:
            continue
        slots[(date, time)].append((sheet_row, status, product))

    rows_to_delete = []
    for (date, time), entries in sorted(slots.items()):
        if len(entries) <= 1:
            continue

        posted = [(r, s, p) for r, s, p in entries if s == "posted"]
        pending = [(r, s, p) for r, s, p in entries if s != "posted"]

        # Sort pending by row number, keep the last (newest)
        pending.sort(key=lambda x: x[0])
        to_keep_pending = pending[-1:] if pending else []
        to_delete_pending = pending[:-1]

        # If there are posted rows AND pending rows for same slot, delete the pending ones too
        # (slot already published)
        if posted and pending:
            to_delete_pending = pending  # delete all pending if already posted
            to_keep_pending = []

        deleting = to_delete_pending
        for r, s, p in deleting:
            print(f"  DELETE row {r:3d}: {date} {time} | {p[:35]:35} [{s}]")
            rows_to_delete.append(r)

        if posted or to_keep_pending:
            kept = (posted + to_keep_pending)[-1]
            print(f"  KEEP   row {kept[0]:3d}: {date} {time} | {kept[2][:35]:35} [{kept[1]}]")

    print(f"\n{len(rows_to_delete)} rows to delete.")
    if args.dry_run or not rows_to_delete:
        return

    # Delete rows from bottom to top so indices don't shift
    meta = sheets.spreadsheets().get(spreadsheetId=sheet_id).execute()
    sheet_id_int = meta["sheets"][0]["properties"]["sheetId"]

    requests = []
    for r in sorted(rows_to_delete, reverse=True):
        requests.append({
            "deleteDimension": {
                "range": {
                    "sheetId": sheet_id_int,
                    "dimension": "ROWS",
                    "startIndex": r - 1,
                    "endIndex": r,
                }
            }
        })

    sheets.spreadsheets().batchUpdate(
        spreadsheetId=sheet_id,
        body={"requests": requests},
    ).execute()
    print("Done — duplicates removed.")


if __name__ == "__main__":
    main()
