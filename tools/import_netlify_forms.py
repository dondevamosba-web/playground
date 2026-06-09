#!/usr/bin/env python3
"""
Pull expense entries from the Google Sheets log → write to .tmp/new_expenses.json.
Run before build_gastos_final.py to incorporate web-logged entries into the Excel.

Usage:
    python3 tools/import_netlify_forms.py [--dry-run]
"""

import json
import sys
import argparse
import warnings
warnings.filterwarnings("ignore")

from pathlib import Path
from dotenv import load_dotenv
import os

ROOT         = Path(__file__).parent.parent
NEW_EXPENSES = ROOT / ".tmp" / "new_expenses.json"
IMPORTED_IDS = ROOT / ".tmp" / "imported_submission_ids.json"

load_dotenv(ROOT / ".env")
sys.path.insert(0, str(ROOT / "tools"))
from sheets_client import get_services


def load_json(path, default):
    p = Path(path)
    return json.loads(p.read_text()) if p.exists() else default


def save_json(path, data):
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False))


def fnum(v):
    try:
        return float(v) if v else None
    except (ValueError, TypeError):
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    sheet_id = os.getenv("EXPENSE_SHEET_ID")
    if not sheet_id:
        print("ERROR: EXPENSE_SHEET_ID not found in .env")
        sys.exit(1)

    print("Fetching entries from Google Sheets log...")
    sheets, _ = get_services()
    result = sheets.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range="Log!A:J"
    ).execute()

    rows = result.get("values", [])
    if len(rows) <= 1:
        print("No entries yet.")
        return

    header = rows[0]
    data_rows = rows[1:]
    print(f"  Found {len(data_rows)} total entries")

    already_imported = set(load_json(IMPORTED_IDS, []))
    new_rows = [(i, r) for i, r in enumerate(data_rows) if r[0] not in already_imported]
    print(f"  {len(new_rows)} new (unimported)")

    if not new_rows:
        print("Nothing new to import.")
        return

    def col(row, idx, default=""):
        return row[idx].strip() if idx < len(row) else default

    existing = load_json(NEW_EXPENSES, {})
    imported_count = 0

    for _, row in new_rows:
        timestamp  = col(row, 0)
        month      = col(row, 1)
        entry_type = col(row, 2) or "daily"
        day        = col(row, 3)
        desc       = col(row, 4)
        ars        = fnum(col(row, 5))
        usd        = fnum(col(row, 6))
        category   = col(row, 7)
        payment    = col(row, 8)
        status     = col(row, 9)

        # Normalize month capitalisation (e.g. "may 2026" → "May 2026")
        if month:
            month = month.title()

        if not month or not desc:
            already_imported.add(timestamp)
            continue

        if month not in existing:
            existing[month] = {"income": [], "fixed": [], "daily": []}

        if entry_type == "daily":
            e = {"day": day, "desc": desc, "ars": ars, "usd": usd}
            if category: e["category"] = category
            if payment:  e["payment"]  = payment
        elif entry_type == "fixed":
            e = {"desc": desc, "ars": ars, "usd": usd}
            if status:   e["status"] = status
        elif entry_type == "income":
            e = {"desc": desc, "ars": ars, "usd": usd}
        else:
            already_imported.add(timestamp)
            continue

        existing[month][entry_type].append(e)
        already_imported.add(timestamp)
        imported_count += 1
        print(f"  + [{entry_type.upper()}] {month} — {desc}  ARS={ars} USD={usd}")

    if args.dry_run:
        print("\n[dry-run] No files written.")
        return

    NEW_EXPENSES.parent.mkdir(exist_ok=True)
    save_json(NEW_EXPENSES, existing)
    save_json(IMPORTED_IDS, sorted(already_imported))

    print(f"\n✅ Imported {imported_count} entries → {NEW_EXPENSES}")
    print("Next step: python3 tools/build_gastos_final.py")


if __name__ == "__main__":
    main()
