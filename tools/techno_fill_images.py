#!/usr/bin/env python3
"""
Fill missing Media URLs in the Techno content calendar Google Sheet.
Only updates rows where Media URL (col I) is blank and status is pending.

Usage:
  python3 tools/techno_fill_images.py --dry-run
  python3 tools/techno_fill_images.py
"""

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from tools.sheets_client import get_services

SHEET_ENV_KEY = "TECHNO_CONTENT_CALENDAR_SHEET_ID"

# Import the stable pool from the canonical source
from tools.techno_fix_all_images import IMAGES as IMAGE_POOL

_counters: dict = {}

def find_image(product_name: str) -> str:
    """Find best image URL for a product, rotating through the pool."""
    for key in sorted(IMAGE_POOL.keys(), key=len, reverse=True):
        if key.lower() in product_name.lower():
            idx = _counters.get(key, 0)
            _counters[key] = idx + 1
            return IMAGE_POOL[key][idx % len(IMAGE_POOL[key])]
    return ""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    sheets, _ = get_services()
    sheet_id = os.getenv(SHEET_ENV_KEY)

    result = sheets.spreadsheets().values().get(
        spreadsheetId=sheet_id, range="A2:K200"
    ).execute()
    rows = result.get("values", [])

    updates = []
    for i, row in enumerate(rows):
        sheet_row = i + 2  # 1-indexed, skipping header
        status = row[9].strip() if len(row) > 9 else ""
        media = row[8].strip() if len(row) > 8 else ""
        product = row[3].strip() if len(row) > 3 else ""

        if status != "pending" or media or not product:
            continue

        url = find_image(product)
        if not url:
            print(f"  [row {sheet_row}] NO MATCH — {product}")
            continue

        print(f"  [row {sheet_row}] {product[:40]:40} → {url[:60]}")
        updates.append({
            "range": f"I{sheet_row}",
            "values": [[url]],
        })

    print(f"\n{len(updates)} URLs to fill.")

    if args.dry_run or not updates:
        return

    sheets.spreadsheets().values().batchUpdate(
        spreadsheetId=sheet_id,
        body={
            "valueInputOption": "RAW",
            "data": updates,
        },
    ).execute()
    print("Done — sheet updated.")


if __name__ == "__main__":
    main()
