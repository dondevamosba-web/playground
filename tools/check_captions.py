#!/usr/bin/env python3
"""
Validate Fiestas pending posts against caption standards.

Stop hook: exit code 0 = all pass, exit code 2 = blocker found.

Standards:
  ✓ No "Vía @handle" attribution lines
  ✓ No opening ¿ (closing ? only)
  ✓ Has hashtags
  ✓ Has image URL (or VIDEO: note)

Usage:
  python3 tools/check_captions.py              # Exit 0/2
  python3 tools/check_captions.py --verbose    # Print findings
"""
import argparse
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from tools.sheets_client import get_services


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--verbose", action="store_true")
    args = p.parse_args()

    sheets, _ = get_services()
    sid = os.environ["FIESTAS_APPROVAL_SHEET_ID"]
    rows = sheets.spreadsheets().values().get(
        spreadsheetId=sid, range="Queue!A2:N600").execute().get("values", [])

    errors = []
    for i, r in enumerate(rows, 2):
        if len(r) < 12 or r[11].strip() != "pending":
            continue

        caption = (r[7] or "").strip()
        image = (r[9] or "").strip()
        notes = (r[13] or "").strip() if len(r) > 13 else ""
        source = (r[1] or "").strip()

        # Blocker: "Vía @"
        if re.search(r"\bVía\s*@|vía\s*@", caption):
            errors.append(f"Fila {i}: tiene 'Vía @' (prohibido)")

        # Blocker: opening ¿
        if re.search(r"¿", caption):
            errors.append(f"Fila {i}: tiene opening ¿ (solo closing ? en Argentina)")

        # Blocker: no hashtags
        if "#" not in caption:
            errors.append(f"Fila {i}: sin hashtags")

        # Blocker: no image, no video
        if not image and not notes.startswith("VIDEO:"):
            errors.append(f"Fila {i}: sin imagen y sin VIDEO: en notes")

        # Warning: venue flyer but no "(flyer)" in source
        if "(flyer)" not in source:
            pass  # Not a blocker, just info

    if errors:
        if args.verbose:
            print("\n❌ Caption blockers found:\n")
            for e in errors:
                print(f"  {e}")
        return 2

    if args.verbose:
        print(f"\n✓ All {len([r for r in rows if len(r) > 11 and r[11].strip() == 'pending'])} pending posts pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
