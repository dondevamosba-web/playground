#!/usr/bin/env python3
"""
Publish approved rows from the Fiestas Queue sheet directly.
Reads Queue tab, posts all rows with Status='approved', marks them 'posted'.

Usage:
  python3 tools/publish_fiestas_queue.py --dry-run
  python3 tools/publish_fiestas_queue.py
"""
import argparse, os, sys, time, requests
from pathlib import Path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
from dotenv import load_dotenv; load_dotenv(ROOT / ".env")
from tools.sheets_client import get_services

SHEET_ID = os.environ["FIESTAS_APPROVAL_SHEET_ID"]
IG_ID    = os.environ["FIESTAS_INSTAGRAM_BUSINESS_ACCOUNT_ID"]
TOKEN    = os.environ["INSTAGRAM_ACCESS_TOKEN"]
GRAPH    = "https://graph.facebook.com/v19.0"

# Queue tab columns (0-based)
COL_EVENT_NAME  = 2
COL_EVENT_DATE  = 3
COL_FEED_CAP    = 7
COL_IMAGE_URL   = 9
COL_STATUS      = 11
COL_POST_ID     = 12


def publish_image(image_url, caption):
    r = requests.post(f"{GRAPH}/{IG_ID}/media", data={
        "image_url": image_url,
        "caption": caption,
        "access_token": TOKEN,
    })
    res = r.json()
    if "id" not in res:
        print(f"    ERROR container: {res}")
        return None
    time.sleep(2)
    r2 = requests.post(f"{GRAPH}/{IG_ID}/media_publish", data={
        "creation_id": res["id"],
        "access_token": TOKEN,
    })
    res2 = r2.json()
    if "id" not in res2:
        print(f"    ERROR publish: {res2}")
        return None
    return res2["id"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--min-date", default=None, help="Only publish events on or after this date (YYYY-MM-DD)")
    args = parser.parse_args()

    sheets, _ = get_services()
    result = sheets.spreadsheets().values().get(
        spreadsheetId=SHEET_ID, range="Queue!A2:M500"
    ).execute()
    rows = result.get("values", [])

    def date_ok(r):
        if not args.min_date:
            return True
        event_date = r[COL_EVENT_DATE].strip() if len(r) > COL_EVENT_DATE else ""
        return event_date >= args.min_date

    to_post = [
        (i + 2, r) for i, r in enumerate(rows)
        if len(r) > COL_STATUS
        and r[COL_STATUS].strip() == "approved"
        and (len(r) <= COL_POST_ID or not r[COL_POST_ID].strip())
        and date_ok(r)
    ]

    if not to_post:
        print("Nada para publicar.")
        return

    print(f"{len(to_post)} post(s) aprobados:\n")
    posted = 0
    for sheet_row, r in to_post:
        name      = r[COL_EVENT_NAME] if len(r) > COL_EVENT_NAME else ""
        date      = r[COL_EVENT_DATE] if len(r) > COL_EVENT_DATE else ""
        caption   = r[COL_FEED_CAP]  if len(r) > COL_FEED_CAP   else ""
        image_url = r[COL_IMAGE_URL] if len(r) > COL_IMAGE_URL  else ""

        print(f"  [{date}] {name[:55]}")
        print(f"  Img: {image_url[:70]}")

        if not image_url:
            print("  SKIP — sin imagen\n")
            continue

        if args.dry_run:
            print("  [dry-run] OK\n")
            continue

        media_id = publish_image(image_url, caption)
        if media_id:
            sheets.spreadsheets().values().batchUpdate(
                spreadsheetId=SHEET_ID,
                body={"valueInputOption": "RAW", "data": [
                    {"range": f"Queue!L{sheet_row}", "values": [["posted"]]},
                    {"range": f"Queue!M{sheet_row}", "values": [[media_id]]},
                ]}
            ).execute()
            print(f"  ✓ Posted — {media_id}\n")
            posted += 1
            time.sleep(3)
        else:
            print("  ✗ Error\n")

    print(f"Done. {posted}/{len(to_post)} publicados.")


if __name__ == "__main__":
    main()
