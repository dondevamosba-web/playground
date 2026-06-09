#!/usr/bin/env python3
"""
Fetch the next 3 posts (not already in the sheet) for Ola Digital, Storm, and Techno
and append them as draft rows to the unified approval sheet.
"""

import os
import sys
import requests
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from tools.sheets_client import get_services

SHEET_ID = os.environ.get("UNIFIED_APPROVAL_SHEET_ID", "1I0N4kYz-Hpzns8Qmk8e-fDKH8Cdn5ws7kFpjah5yY-A")
ACCESS_TOKEN = os.environ["INSTAGRAM_ACCESS_TOKEN"]
GRAPH = "https://graph.facebook.com/v19.0"
AR_TZ = timezone(timedelta(hours=-3))

ACCOUNTS = {
    "Ola Digital": os.environ["INSTAGRAM_BUSINESS_ACCOUNT_ID"],
    "Storm":       os.environ["STORM_INSTAGRAM_BUSINESS_ACCOUNT_ID"],
    "Techno":      os.environ["TECHNO_INSTAGRAM_BUSINESS_ACCOUNT_ID"],
}


def get_existing_post_ids(sheets, tab_name):
    result = sheets.spreadsheets().values().get(
        spreadsheetId=SHEET_ID,
        range=f"'{tab_name}'!G2:G100"
    ).execute()
    rows = result.get("values", [])
    return {r[0] for r in rows if r}


def fetch_posts(account_id, limit=20):
    url = f"{GRAPH}/{account_id}/media"
    params = {
        "fields": "id,caption,media_url,thumbnail_url,timestamp,media_type",
        "limit": limit,
        "access_token": ACCESS_TOKEN,
    }
    r = requests.get(url, params=params)
    r.raise_for_status()
    return r.json().get("data", [])


def main():
    sheets, _ = get_services()

    for tab_name, account_id in ACCOUNTS.items():
        print(f"\n{tab_name} ({account_id})")
        existing_ids = get_existing_post_ids(sheets, tab_name)
        print(f"  Already in sheet: {len(existing_ids)} posts")

        try:
            posts = fetch_posts(account_id)
        except Exception as e:
            print(f"  ERROR fetching: {e}")
            continue

        new_rows = []
        for p in posts:
            if p["id"] in existing_ids:
                continue
            ts = datetime.fromisoformat(p["timestamp"].replace("Z", "+00:00"))
            ts_ar = ts.astimezone(AR_TZ).strftime("%Y-%m-%d %H:%M")
            caption = (p.get("caption") or "").replace("\n", " ").strip()
            image_url = p.get("media_url") or p.get("thumbnail_url") or ""
            new_rows.append([ts_ar, caption, image_url, "", "draft", "", p["id"]])
            if len(new_rows) == 3:
                break

        if not new_rows:
            print("  No new posts found.")
            continue

        sheets.spreadsheets().values().append(
            spreadsheetId=SHEET_ID,
            range=f"'{tab_name}'!A2",
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body={"values": new_rows}
        ).execute()
        print(f"  Added {len(new_rows)} new rows.")

    print("\nDone.")


if __name__ == "__main__":
    main()
