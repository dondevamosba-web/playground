#!/usr/bin/env python3
"""
Mark posts with past event dates as 'vencida' (expired).

Scans all 6 account sheets, finds rows where event_date < today,
marks them as 'vencida' in the Status column so they never publish.

Usage:
  python3 tools/cleanup_vencidas.py              # Count & show
  python3 tools/cleanup_vencidas.py --apply      # Actually mark them
"""
import argparse
import os
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from tools.sheets_client import get_services

ACCOUNTS = {
    "Fiestas": "Queue",
    "Techno": "Hoja 1",
    "Storm": "Hoja 1",
    "Ola Digital": "Hoja 1",
    "Ola Empleo": "Hoja 1",
    "Talento USA": "Hoja 1",
}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--apply", action="store_true", help="Actually update the sheets")
    args = p.parse_args()

    sheets, _ = get_services()
    sid = os.environ["FIESTAS_APPROVAL_SHEET_ID"]
    today = date.today().isoformat()

    total_vencidas = 0

    for acct, tab in ACCOUNTS.items():
        print(f"\n📋 {acct} ({tab}):")
        rows = sheets.spreadsheets().values().get(
            spreadsheetId=sid, range=f"{tab}!A2:N600").execute().get("values", [])

        vencidas = []
        for i, r in enumerate(rows, 2):
            if len(r) < 12 or not r[3]:  # No event date
                continue
            event_date = r[3].strip()
            status = (r[11].strip() if len(r) > 11 else "").lower()

            # Skip already posted or already marked vencida
            if status == "posted" or status == "vencida" or r[12] if len(r) > 12 else "":
                continue

            if event_date < today:
                vencidas.append(i)
                name = (r[2] or "").strip()
                print(f"  ⏰ Fila {i}: {name} ({event_date})")

        if vencidas:
            print(f"  → {len(vencidas)} vencidas")
            total_vencidas += len(vencidas)

            if args.apply:
                updates = []
                for row_num in vencidas:
                    updates.append({
                        "range": f"{tab}!L{row_num}",
                        "values": [["vencida"]]
                    })
                sheets.spreadsheets().values().batchUpdate(
                    spreadsheetId=sid,
                    body={"valueInputOption": "RAW", "data": updates}).execute()
                print(f"  ✅ Marcadas como vencida")

    print(f"\n=== Total: {total_vencidas} posts vencidos ===")
    if not args.apply:
        print("Usa --apply para marcarlos")
    return 0


if __name__ == "__main__":
    sys.exit(main())
