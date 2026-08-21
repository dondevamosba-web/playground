#!/usr/bin/env python3
"""
Assign varied image URLs to PlayStation rows in the Techno sheet.
Rotates through a pool per product type so no two consecutive posts look the same.
"""
import os, sys
from pathlib import Path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
from dotenv import load_dotenv; load_dotenv(ROOT / ".env")
from tools.sheets_client import get_services

SHEET_ENV_KEY = "TECHNO_CONTENT_CALENDAR_SHEET_ID"

# Image pools per product — will cycle through them
POOLS = {
    "ps5_slim": [
        "https://gmedia.playstation.com/is/image/SIEPDC/ps5-slim-product-thumbnail-01-en-10aug23",
        "https://gmedia.playstation.com/is/image/SIEPDC/ps5-slim-product-thumbnail-02-en-10aug23",
        "https://gmedia.playstation.com/is/image/SIEPDC/ps5-slim-product-thumbnail-03-en-10aug23",
        "https://m.media-amazon.com/images/I/51fM0CKG+HL.jpg",
        "https://m.media-amazon.com/images/I/81yWGJFpI6L.jpg",
        "https://gmedia.playstation.com/is/image/SIEPDC/ps5-product-thumbnail-01-en-14sep21",
        "https://pisces.bbystatic.com/image2/BestBuy_US/images/products/6566/6566039_sd.jpg",
    ],
    "ps5_bundle": [
        "https://pisces.bbystatic.com/image2/BestBuy_US/images/products/6571/6571608_sd.jpg",
        "https://m.media-amazon.com/images/I/51fM0CKG+HL.jpg",
        "https://gmedia.playstation.com/is/image/SIEPDC/ps5-slim-product-thumbnail-02-en-10aug23",
        "https://pisces.bbystatic.com/image2/BestBuy_US/images/products/6571/6571623_sd.jpg",
        "https://m.media-amazon.com/images/I/81yWGJFpI6L.jpg",
        "https://gmedia.playstation.com/is/image/SIEPDC/ps5-slim-product-thumbnail-03-en-10aug23",
    ],
    "ps5_gow": [
        "https://i5.walmartimages.com/seo/2023-New-PlayStation-5-Slim-Digital-Edition-God-of-War-Ragnarok-Bundle_47aea2c0-4d6c-4b3d-b4f5-7af6fdddf18e.3f6caa97c8df0f0a94bcaeab3d25d1bf.jpeg",
        "https://pisces.bbystatic.com/image2/BestBuy_US/images/products/6571/6571625_sd.jpg",
        "https://gmedia.playstation.com/is/image/SIEPDC/ps5-slim-product-thumbnail-01-en-10aug23",
        "https://m.media-amazon.com/images/I/81GOoI9DKZL.jpg",
        "https://pisces.bbystatic.com/image2/BestBuy_US/images/products/6566/6566041_sd.jpg",
    ],
    "dualsense_edge": [
        "https://gmedia.playstation.com/is/image/SIEPDC/dualsense-edge-product-thumbnail-01-en-13jan23",
        "https://gmedia.playstation.com/is/image/SIEPDC/dualsense-edge-product-thumbnail-02-en-13jan23",
        "https://m.media-amazon.com/images/I/61pCjLiENYL.jpg",
        "https://pisces.bbystatic.com/image2/BestBuy_US/images/products/6499/6499102_sd.jpg",
        "https://gmedia.playstation.com/is/image/SIEPDC/dualsense-edge-product-thumbnail-01-en-13jan23",
        "https://m.media-amazon.com/images/I/61SdSOGJVzL.jpg",
    ],
}

def classify(product: str) -> str:
    p = product.lower()
    if "dualsense edge" in p:
        return "dualsense_edge"
    if "god of war" in p:
        return "ps5_gow"
    if "2 dualsense" in p or "+ 2" in p:
        return "ps5_bundle"
    if "ps5" in p:
        return "ps5_slim"
    return ""

def main():
    sheets, _ = get_services()
    sid = os.getenv(SHEET_ENV_KEY)
    result = sheets.spreadsheets().values().get(spreadsheetId=sid, range="A2:K300").execute()
    rows = result.get("values", [])

    counters = {k: 0 for k in POOLS}
    updates = []

    for i, row in enumerate(rows):
        sheet_row = i + 2
        prod = row[3].strip() if len(row) > 3 else ""
        status = row[9].strip() if len(row) > 9 else ""
        if status == "posted":
            continue
        cat = classify(prod)
        if not cat:
            continue
        pool = POOLS[cat]
        url = pool[counters[cat] % len(pool)]
        counters[cat] += 1
        print(f"  row {sheet_row:3d} [{cat:15}] {prod[:35]:35} → {url[:55]}")
        updates.append({"range": f"I{sheet_row}", "values": [[url]]})

    print(f"\n{len(updates)} rows to update.")
    if not updates:
        return
    sheets.spreadsheets().values().batchUpdate(
        spreadsheetId=sid,
        body={"valueInputOption": "RAW", "data": updates},
    ).execute()
    print("Done.")

if __name__ == "__main__":
    main()
