#!/usr/bin/env python3
"""
Fetch last 3 posts from each of the 4 IG accounts and write them to the unified approval sheet.
Each row: Queued At | Caption | Image URL | Schedule Date | Status | Comments | Post ID
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

ACCOUNTS = {
    "Ola Digital": os.environ["INSTAGRAM_BUSINESS_ACCOUNT_ID"],
    "Storm":       os.environ["STORM_INSTAGRAM_BUSINESS_ACCOUNT_ID"],
    "Fiestas":     os.environ["FIESTAS_INSTAGRAM_BUSINESS_ACCOUNT_ID"],
    "Techno":      os.environ["TECHNO_INSTAGRAM_BUSINESS_ACCOUNT_ID"],
}

AR_TZ = timezone(timedelta(hours=-3))


def fetch_recent_posts(account_id, limit=3):
    url = f"{GRAPH}/{account_id}/media"
    params = {
        "fields": "id,caption,media_url,thumbnail_url,timestamp,permalink,media_type",
        "limit": limit,
        "access_token": ACCESS_TOKEN,
    }
    r = requests.get(url, params=params)
    r.raise_for_status()
    return r.json().get("data", [])


def main():
    sheets, _ = get_services()

    for tab_name, account_id in ACCOUNTS.items():
        print(f"Fetching {tab_name} ({account_id})...")
        try:
            posts = fetch_recent_posts(account_id)
        except Exception as e:
            print(f"  ERROR: {e}")
            continue

        rows = []
        for p in posts:
            ts = datetime.fromisoformat(p["timestamp"].replace("Z", "+00:00"))
            ts_ar = ts.astimezone(AR_TZ).strftime("%Y-%m-%d %H:%M")
            caption = (p.get("caption") or "").replace("\n", " ").strip()
            image_url = p.get("media_url") or p.get("thumbnail_url") or ""
            post_id = p.get("id", "")
            rows.append([ts_ar, caption, image_url, "", "draft", "", post_id])

        if not rows:
            print(f"  No posts found.")
            continue

        sheets.spreadsheets().values().append(
            spreadsheetId=SHEET_ID,
            range=f"'{tab_name}'!A2",
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body={"values": rows}
        ).execute()

        print(f"  Added {len(rows)} rows.")

    print("\nDone.")


if __name__ == "__main__":
    main()
