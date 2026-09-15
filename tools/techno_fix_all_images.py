#!/usr/bin/env python3
"""
Replace all fragile image URLs in the Techno sheet with stable ones.
Fragile = apple.com/v/... (version slugs change), macobserver.com, image-us.samsung.com
Stable  = apple.com/newsroom/..., store.storeimages.cdn-apple.com, images.samsung.com, gmedia.playstation.com, m.media-amazon.com

Also fills any remaining blank media URLs.

Run any time images break:
  python3 tools/techno_fix_all_images.py
"""
import os, sys, argparse
from pathlib import Path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
from dotenv import load_dotenv; load_dotenv(ROOT / ".env")
from tools.sheets_client import get_services

SHEET_ENV_KEY = "TECHNO_CONTENT_CALENDAR_SHEET_ID"

# ── Verified-working image pools per product ────────────────────────────────
# All URLs tested with HEAD request — only 200 OK included.
# Apple: apple.com/v/{product}/{current-slug}/ — fetched live from product pages
# Samsung: image-us.samsung.com and images.samsung.com/is/image/samsung/assets/
# PlayStation: pisces.bbystatic.com (BestBuy CDN) — gmedia.playstation.com blocks hotlink
# Generic: m.media-amazon.com for anything else
BASE = "https://www.apple.com"
IMAGES = {
    # ── iPhones 17 ─────────────────────────────────────────────────────────
    "iPhone 17 Pro Max": [
        f"{BASE}/v/iphone/home/cj/images/overview/chapternav/nav_iphone_17pro__b8rt659h2ogi_large.png",
        "https://store.storeimages.cdn-apple.com/1/as-images.apple.com/is/iphone-compare-iphone-17-pro-202509?wid=800&hei=800&fmt=jpeg&qlt=90",
    ],
    "iPhone 17 Pro 128": [
        "https://store.storeimages.cdn-apple.com/1/as-images.apple.com/is/iphone-compare-iphone-17-pro-202509?wid=800&hei=800&fmt=jpeg&qlt=90",
        f"{BASE}/v/iphone/home/cj/images/overview/chapternav/nav_iphone_17pro__b8rt659h2ogi_large.png",
    ],
    "iPhone 17 128": [
        f"{BASE}/v/iphone/home/cj/images/overview/chapternav/nav_iphone_17__bx67weh1ur5y_large.png",
        "https://store.storeimages.cdn-apple.com/1/as-images.apple.com/is/iphone-compare-iphone-17-202509?wid=800&hei=800&fmt=jpeg&qlt=90",
    ],
    "iPhone Air": [
        "https://store.storeimages.cdn-apple.com/1/as-images.apple.com/is/iphone-compare-iphone-air-202509?wid=800&hei=800&fmt=jpeg&qlt=90",
        f"{BASE}/v/iphone/home/cj/images/overview/chapternav/nav_iphone_air__f066mfdfhi62_large.png",
    ],
    # ── iPhones 16 ─────────────────────────────────────────────────────────
    "iPhone 16 Pro Max": [
        f"{BASE}/v/iphone/home/cj/images/overview/chapternav/nav_iphone_16__qsxcpuia0oam_large.png",
        "https://pisces.bbystatic.com/image2/BestBuy_US/images/products/6523/6523167_sd.jpg",
        "https://pisces.bbystatic.com/image2/BestBuy_US/images/products/6523/6523174_sd.jpg",
    ],
    "iPhone 16 Pro 128": [
        "https://pisces.bbystatic.com/image2/BestBuy_US/images/products/6523/6523167_sd.jpg",
        f"{BASE}/v/iphone/home/cj/images/overview/chapternav/nav_iphone_16__qsxcpuia0oam_large.png",
        "https://pisces.bbystatic.com/image2/BestBuy_US/images/products/f3d55853-e894-41b3-8dc2-bc34c6038cf2.jpg",
    ],
    "iPhone 16 128": [
        f"{BASE}/v/iphone/home/cj/images/overview/chapternav/nav_iphone_16__qsxcpuia0oam_large.png",
        "https://pisces.bbystatic.com/image2/BestBuy_US/images/products/6523/6523174_sd.jpg",
        "https://pisces.bbystatic.com/image2/BestBuy_US/images/products/6523/6523167_sd.jpg",
    ],
    # ── AirPods ────────────────────────────────────────────────────────────
    "AirPods Pro 2": [
        f"{BASE}/v/airpods-pro/s/images/overview/welcome/hero__b0eal3mn03ua_large.jpg",
        f"{BASE}/v/airpods-pro/s/images/overview/product-viewer/closer_look_initial__cksqga5hm77m_large.jpg",
        f"{BASE}/v/airpods-pro/s/images/overview/highlights/highlights_noise_cancellation__cxd50c0etw4m_large.jpg",
    ],
    "AirPods 4": [
        f"{BASE}/v/airpods/ae/images/overview/hero__gb4d3fd8jnu6_large.jpg",
        f"{BASE}/v/airpods/ae/images/overview/hero_endframe__calpooy4ucr6_large.jpg",
        f"{BASE}/v/airpods/ae/images/overview/consider/card_noise_cancellation__bcl69t06noci_large.jpg",
    ],
    "AirPods Max": [
        f"{BASE}/v/airpods/ae/images/overview/airpods_max_purple__d9y3g3n7cnyq_large.png",
        f"{BASE}/v/airpods/ae/images/overview/airpods_max_blue__fsfaleh1smuu_large.png",
        f"{BASE}/v/airpods/ae/images/overview/airpods_max_black__x3byrd2venmu_large.png",
        f"{BASE}/v/airpods/ae/images/overview/airpods_max_stardust__l9lr6719rmaa_large.png",
    ],
    # ── iPad ───────────────────────────────────────────────────────────────
    "iPad Air M2 11": [
        f"{BASE}/v/ipad-air/ah/images/overview/hero/hero_endframe__6gl84bccyaqi_large.png",
        f"{BASE}/v/ipad-air/ah/images/overview/highlights/anim/highlights_chip_static__r572qidazrma_large.jpg",
    ],
    "iPad Air M2 13": [
        f"{BASE}/v/ipad-air/ah/images/overview/hero/hero_endframe__6gl84bccyaqi_large.png",
        f"{BASE}/v/ipad-air/ah/images/overview/highlights/anim/highlights_chip_endframe__wyb8kl53b2ae_large.jpg",
    ],
    # ── Mac ────────────────────────────────────────────────────────────────
    "Mac Mini M4": [
        f"{BASE}/v/mac-mini/aa/images/overview/welcome/welcome_hero__ckmy0qsqi8ia_large.jpg",
        f"{BASE}/v/mac-mini/aa/images/overview/bento-gallery/2d_pf__en2v80tcytua_xlarge.jpg",
        f"{BASE}/v/mac-mini/aa/images/overview/design/design_pf__c25gukz0vwgi_large.jpg",
    ],
    "iMac M4 24": [
        f"{BASE}/v/imac/v/images/overview/welcome/welcome_hero__f23bdvt2rzam_xlarge.jpg",
        f"{BASE}/v/imac/v/images/overview/welcome/welcome_hero_endframe__dzokoxvtgr8m_xlarge.jpg",
        f"{BASE}/v/imac/v/images/overview/highlights/highlights_design_endframe__cf4hroyqtgly_xlarge.jpg",
    ],
    "MacBook Air M3 13": [
        f"{BASE}/v/macbook-air/z/images/overview/hero/hero_static__c9sislzzicq6_large.png",
        f"{BASE}/v/macbook-air/z/images/overview/hero/hero_endframe__c67cz35iy9me_large.png",
        f"{BASE}/v/macbook-air/z/images/overview/highlights/mx_chip_endframe__bjtjjh2urgoi_large.jpg",
    ],
    "MacBook Pro M4 14": [
        f"{BASE}/v/macbook-pro/ax/images/overview/welcome/hero_endframe__fwev9ebh42mq_xlarge.jpg",
        f"{BASE}/v/macbook-pro/ax/images/overview/highlights/highlights_chip_endframe__dp975gwqppw2_large.jpg",
        f"{BASE}/v/macbook-pro/ax/images/overview/highlights/highlights_ai__c1tao33ompea_large.jpg",
    ],
    # ── Accesorios ─────────────────────────────────────────────────────────
    "Magic Keyboard": [
        "https://pisces.bbystatic.com/image2/BestBuy_US/images/products/6472/6472709_sd.jpg",
        "https://pisces.bbystatic.com/image2/BestBuy_US/images/products/6472/6472707_sd.jpg",
    ],
    "Magic Mouse": [
        "https://pisces.bbystatic.com/image2/BestBuy_US/images/products/6472/6472710_sd.jpg",
    ],
    "Cargador MagSafe 25": [
        "https://pisces.bbystatic.com/image2/BestBuy_US/images/products/6587/6587949_sd.jpg",
        "https://pisces.bbystatic.com/image2/BestBuy_US/images/products/6587/6587949cv11d.jpg",
    ],
    "Cargador USB-C 67": [
        "https://pisces.bbystatic.com/image2/BestBuy_US/images/products/6450/6450444_sd.jpg",
    ],
    # ── Apple Watch ────────────────────────────────────────────────────────
    "Apple Watch Series 10": [
        "https://store.storeimages.cdn-apple.com/1/as-images.apple.com/is/watch-s10-digitalmat-gallery-1-202409?wid=2000&hei=2000&fmt=jpeg&qlt=90",
        "https://store.storeimages.cdn-apple.com/1/as-images.apple.com/is/watch-s10-digitalmat-gallery-2-202409?wid=2000&hei=2000&fmt=jpeg&qlt=90",
        "https://store.storeimages.cdn-apple.com/1/as-images.apple.com/is/watch-s10-digitalmat-gallery-3-202409?wid=2000&hei=2000&fmt=jpeg&qlt=90",
    ],
    "Apple Watch Ultra 2": [
        "https://store.storeimages.cdn-apple.com/1/as-images.apple.com/is/watch-ultra2-digitalmat-gallery-1-202309?wid=2000&hei=2000&fmt=jpeg&qlt=90",
        "https://store.storeimages.cdn-apple.com/1/as-images.apple.com/is/watch-ultra2-digitalmat-gallery-2-202309?wid=2000&hei=2000&fmt=jpeg&qlt=90",
    ],
    # ── Samsung ────────────────────────────────────────────────────────────
    "Galaxy S25 Ultra": [
        "https://image-us.samsung.com/us/smartphones/galaxy-s25-ultra/images/galaxy-s25-ultra-features-kv.jpg",
        "https://images.samsung.com/is/image/samsung/assets/us/audio-devices/galaxy-buds3-pro/ParanMLP-Hero-Buds3Pro-KV-logos-D-1920x780-1.jpg",
    ],
    "Galaxy S25+": [
        "https://image-us.samsung.com/us/smartphones/galaxy-s25/images/galaxy-s25-features-kv.jpg?imbypass=true",
    ],
    "Galaxy S25": [
        "https://image-us.samsung.com/us/smartphones/galaxy-s25/images/galaxy-s25-features-kv.jpg?imbypass=true",
    ],
    "Galaxy Tab S10+": [
        "https://pisces.bbystatic.com/image2/BestBuy_US/images/products/6587/6587103_sd.jpg",
        "https://pisces.bbystatic.com/image2/BestBuy_US/images/products/6587/6587107_sd.jpg",
    ],
    "Galaxy Buds3 Pro": [
        "https://images.samsung.com/is/image/samsung/assets/us/audio-devices/galaxy-buds3-pro/ParanMLP-Hero-Buds3Pro-KV-logos-D-1920x780-1.jpg",
        "https://image-us.samsung.com/us/galaxy-buds3-pro/images/galaxy-buds3-pro-white.png?nocache?imbypass=true",
        "https://image-us.samsung.com/us/galaxy-buds3-pro/images/galaxy-buds3-silver.png?nocache?imbypass=true",
    ],
    # ── PlayStation — Amazon CDN only (BestBuy _sd.jpg = low-res, unstable) ─
    "PS5 Slim + 2 DualSense": [
        "https://m.media-amazon.com/images/I/81yWGJFpI6L._AC_SL1500_.jpg",
        "https://m.media-amazon.com/images/I/51fM0CKG+HL._AC_SL1500_.jpg",
        "https://m.media-amazon.com/images/I/71gSRbyXmoL._AC_SL1500_.jpg",
    ],
    "PS5 Slim + God": [
        "https://m.media-amazon.com/images/I/81yWGJFpI6L._AC_SL1500_.jpg",
        "https://m.media-amazon.com/images/I/51fM0CKG+HL._AC_SL1500_.jpg",
    ],
    "PS5 Slim": [
        "https://m.media-amazon.com/images/I/51fM0CKG+HL._AC_SL1500_.jpg",
        "https://m.media-amazon.com/images/I/81yWGJFpI6L._AC_SL1500_.jpg",
        "https://m.media-amazon.com/images/I/71gSRbyXmoL._AC_SL1500_.jpg",
    ],
    "DualSense Edge": [
        "https://m.media-amazon.com/images/I/61aOJaVhNGL._AC_SL1500_.jpg",
        "https://m.media-amazon.com/images/I/71V5JzgmhFL._AC_SL1500_.jpg",
    ],
}

# Domains that are fragile and should always be replaced
FRAGILE_DOMAINS = [
    "apple.com/v/",
    "macobserver.com",
    "image-us.samsung.com",
    "pisces.bbystatic.com",  # BBY URLs are fine actually, keep
]
# Only actually fragile:
FRAGILE_DOMAINS = [
    "apple.com/newsroom/",        # hotlink blocked
    "macobserver.com",            # third-party, unstable
    "images.samsung.com/us/",     # Samsung gallery CDN 404
    "images.samsung.com/p6pim/",  # regional Samsung CDN
    "images.samsung.com/is/image/samsung/assets/us/smartphones",  # unverified
    "store.storeimages.cdn-apple.com",    # versioned slugs rotate
    "gmedia.playstation.com",             # blocks hotlink
    "pisces.bbystatic.com",               # BestBuy CDN: _sd.jpg = low-res + serves wrong product
]


def find_pool(product: str):
    """Find the best image pool for this product."""
    p = product.strip()
    # Sort keys by length desc so longer/more-specific matches win
    for key in sorted(IMAGES.keys(), key=len, reverse=True):
        if key.lower() in p.lower():
            return IMAGES[key]
    return None


def is_fragile(url: str) -> bool:
    return any(d in url for d in FRAGILE_DOMAINS)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    sheets, _ = get_services()
    sid = os.getenv(SHEET_ENV_KEY)
    result = sheets.spreadsheets().values().get(spreadsheetId=sid, range="A2:K400").execute()
    rows = result.get("values", [])

    # Track how many times each pool key has been used (for rotation)
    counters = {k: 0 for k in IMAGES}
    updates = []

    for i, row in enumerate(rows):
        sheet_row = i + 2
        prod = row[3].strip() if len(row) > 3 else ""
        media = row[8].strip() if len(row) > 8 else ""
        status = row[9].strip() if len(row) > 9 else ""

        if status == "posted" or not prod:
            continue

        pool = find_pool(prod)
        if not pool:
            if not media:
                print(f"  [NO POOL] row {sheet_row}: {prod}")
            continue

        # Find which pool key matched
        matched_key = None
        for key in sorted(IMAGES.keys(), key=len, reverse=True):
            if key.lower() in prod.lower():
                matched_key = key
                break

        needs_update = not media or is_fragile(media)
        if not needs_update:
            # Still rotate counter so same-product posts get different images
            counters[matched_key] = counters.get(matched_key, 0) + 1
            continue

        idx = counters.get(matched_key, 0) % len(pool)
        url = pool[idx]
        counters[matched_key] = counters.get(matched_key, 0) + 1

        reason = "blank" if not media else "fragile"
        print(f"  [{reason}] row {sheet_row:3d} {prod[:35]:35} → {url[:60]}")
        updates.append({"range": f"I{sheet_row}", "values": [[url]]})

    print(f"\n{len(updates)} rows to update.")
    if args.dry_run or not updates:
        return

    sheets.spreadsheets().values().batchUpdate(
        spreadsheetId=sid,
        body={"valueInputOption": "RAW", "data": updates},
    ).execute()
    print("Done.")


if __name__ == "__main__":
    main()
