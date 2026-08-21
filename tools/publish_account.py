#!/usr/bin/env python3
"""
Publish one approved post from ANY account (Techno, Storm, Ola Digital, etc).

Generic version of publish_fiestas_next.py. Specify --account to choose which.

Usage:
  python3 tools/publish_account.py --account techno --dry-run
  python3 tools/publish_account.py --account storm
  python3 tools/publish_account.py --account ola_digital
"""
import argparse
import os
import re
import subprocess
import sys
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

import requests
from tools.sheets_client import get_services

GRAPH = "https://graph.facebook.com/v19.0"
AR_TZ = timezone(timedelta(hours=-3))

# Mapping: account name → (sheet_id, ig_id, ig_token, tab_name)
ACCOUNTS = {
    "techno": (
        os.environ.get("TECHNO_SHEET_ID"),
        os.environ.get("TECHNO_INSTAGRAM_BUSINESS_ACCOUNT_ID"),
        os.environ.get("INSTAGRAM_ACCESS_TOKEN"),
        "Hoja 1"
    ),
    "storm": (
        os.environ.get("STORM_SHEET_ID"),
        os.environ.get("STORM_INSTAGRAM_BUSINESS_ACCOUNT_ID"),
        os.environ.get("INSTAGRAM_ACCESS_TOKEN"),
        "Hoja 1"
    ),
    "ola_digital": (
        os.environ.get("OLA_DIGITAL_SHEET_ID"),
        os.environ.get("OLA_DIGITAL_INSTAGRAM_BUSINESS_ACCOUNT_ID"),
        os.environ.get("INSTAGRAM_ACCESS_TOKEN"),
        "Hoja 1"
    ),
    "ola_empleo": (
        os.environ.get("OLA_EMPLEO_SHEET_ID"),
        os.environ.get("OLA_EMPLEO_INSTAGRAM_BUSINESS_ACCOUNT_ID"),
        os.environ.get("INSTAGRAM_ACCESS_TOKEN"),
        "Hoja 1"
    ),
    "talento_usa": (
        os.environ.get("TALENTO_USA_SHEET_ID"),
        os.environ.get("TALENTO_USA_INSTAGRAM_BUSINESS_ACCOUNT_ID"),
        os.environ.get("INSTAGRAM_ACCESS_TOKEN"),
        "Hoja 1"
    ),
}

COL_SOURCE, COL_NAME, COL_DATE, COL_CAPTION = 1, 2, 3, 7
COL_IMAGE, COL_STATUS, COL_POST_ID = 9, 11, 12


def cell(row, idx):
    return (row[idx] or "").strip() if idx < len(row) else ""


def check_dedup(event_name, event_date, account):
    """Check if event already queued in other accounts."""
    try:
        result = subprocess.run(
            [sys.executable, "tools/cross_account_dedup.py",
             "--event", event_name, "--date", event_date, "--account", account],
            capture_output=True, timeout=30, cwd=ROOT)
        return result.returncode == 0  # 0 = OK, 1 = duplicate
    except Exception as e:
        print(f"  Dedup check error: {e}")
        return True  # Assume OK on error


def add_ticket_links(caption):
    """Extract and add ticket links to caption if missing."""
    if not caption or "Entradas:" in caption or "entradas:" in caption:
        return caption

    patterns = [
        r"https?://[a-z0-9.-]*ticketmaster[a-z0-9.-]*/[^\s]+",
        r"https?://[a-z0-9.-]*eventbrite[a-z0-9.-]*/[^\s]+",
        r"https?://bit\.ly/[a-zA-Z0-9]+",
    ]

    for pattern in patterns:
        match = re.search(pattern, caption, re.IGNORECASE)
        if match:
            url = match.group(0)
            caption = f"{caption}\n\nEntradas: {url}"
            print(f"  ✓ Added ticket link")
            break
    return caption


def publish(ig_id, token, caption, image_url):
    """Publish image to feed."""
    payload = {"image_url": image_url, "caption": caption, "access_token": token}
    res = requests.post(f"{GRAPH}/{ig_id}/media", data=payload, timeout=60).json()
    if "id" not in res:
        print(f"  ERROR container: {res}")
        return None
    time.sleep(2)
    res2 = requests.post(f"{GRAPH}/{ig_id}/media_publish",
                         data={"creation_id": res["id"], "access_token": token},
                         timeout=60).json()
    if "id" not in res2:
        print(f"  ERROR publish: {res2}")
        return None
    return res2["id"]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--account", required=True, choices=list(ACCOUNTS.keys()))
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    sid, ig_id, token, tab = ACCOUNTS[args.account]
    if not all([sid, ig_id, token]):
        print(f"ERROR: Missing credentials for {args.account}")
        return 1

    sheets, _ = get_services()
    rows = sheets.spreadsheets().values().get(
        spreadsheetId=sid, range=f"{tab}!A2:N600").execute().get("values", [])

    today = date.today().isoformat()
    stamp = datetime.now(tz=AR_TZ).strftime("%Y-%m-%d %H:%M")

    candidates = []
    for i, r in enumerate(rows):
        if cell(r, COL_STATUS) != "approved" or cell(r, COL_POST_ID):
            continue
        when = cell(r, COL_DATE)
        if when and when < today:
            continue
        if not cell(r, COL_CAPTION) or not cell(r, COL_IMAGE):
            continue
        candidates.append((when or "9999-12-31", i + 2, r))

    if not candidates:
        print(f"[{stamp}] @{args.account}: nada aprobado.")
        return 0

    candidates.sort(key=lambda c: (c[0], c[1]))
    when, sheet_row, r = candidates[0]
    name = cell(r, COL_NAME)
    print(f"[{stamp}] @{args.account}: {len(candidates)} en cola. Publicando fila {sheet_row}: {name} ({when})")

    # Check for duplicates in other accounts
    if not check_dedup(name, when, args.account):
        print(f"  ⚠️  DUPLICATE found in other account. Skipping.")
        return 1

    if args.dry_run:
        print("  [dry-run] no se publicó nada")
        return 0

    # Add ticket links if available
    caption = cell(r, COL_CAPTION)
    caption = add_ticket_links(caption)

    media_id = publish(ig_id, token, caption, cell(r, COL_IMAGE))
    if not media_id:
        return 1

    sheets.spreadsheets().values().batchUpdate(
        spreadsheetId=sid,
        body={"valueInputOption": "RAW", "data": [
            {"range": f"{tab}!L{sheet_row}", "values": [["posted"]]},
            {"range": f"{tab}!M{sheet_row}", "values": [[media_id]]},
        ]}).execute()
    print(f"  OK {media_id} — quedan {len(candidates) - 1}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
