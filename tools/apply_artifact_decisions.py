#!/usr/bin/env python3
"""
Apply approve/reject decisions exported from the "Mesa de Posteos" artifact
to the unified Instagram approval sheet.

The artifact saves decisions in its own store and exports them as a JSON file
("Exportar decisiones"). This script writes Status (col E) and Comments (col F)
for each matching row. A row matches on Queued At (col A) + the first 60 chars
of the caption (col B), so rows moving around in the sheet don't matter.
Rows that are no longer pending (already approved/rejected/posted) are skipped.

Usage:
  python3 tools/apply_artifact_decisions.py decisiones-posteos.json
  python3 tools/apply_artifact_decisions.py decisiones-posteos.json --dry-run
"""

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from tools.sheets_client import get_services

SHEET_ID = os.environ.get("UNIFIED_APPROVAL_SHEET_ID", "1I0N4kYz-Hpzns8Qmk8e-fDKH8Cdn5ws7kFpjah5yY-A")
PENDING = {"", "pending", "draft"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="JSON exported from the artifact")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    decisions = json.loads(Path(args.file).read_text())
    sheets, _ = get_services()

    updates, skipped = [], []
    for tab in sorted({d["tab"] for d in decisions}):
        rows = sheets.spreadsheets().values().get(
            spreadsheetId=SHEET_ID, range=f"'{tab}'!A1:F1000"
        ).execute().get("values", [])
        index = {}
        for i, row in enumerate(rows[1:], start=2):
            row = row + [""] * (6 - len(row))
            index[(row[0], row[1][:60])] = (i, row[4].strip().lower())

        for d in (d for d in decisions if d["tab"] == tab):
            hit = index.get((d["queuedAt"], d["captionStart"]))
            if not hit:
                skipped.append(f"{tab}: no encontrada — {d['captionStart'][:40]}")
                continue
            row_num, current = hit
            if current not in PENDING:
                skipped.append(f"{tab} fila {row_num}: ya estaba '{current}'")
                continue
            updates.append({"range": f"'{tab}'!E{row_num}:F{row_num}",
                            "values": [[d["status"], d.get("comment", "")]]})
            print(f"{tab} fila {row_num}: {d['status']}  {d['captionStart'][:40]}")

    for s in skipped:
        print(f"SKIP {s}")

    if updates and not args.dry_run:
        sheets.spreadsheets().values().batchUpdate(
            spreadsheetId=SHEET_ID,
            body={"valueInputOption": "RAW", "data": updates},
        ).execute()
    print(f"\n{len(updates)} fila(s) {'a actualizar (dry-run)' if args.dry_run else 'actualizadas'}, {len(skipped)} salteada(s).")


if __name__ == "__main__":
    main()
