"""
Scrapes casas en venta from mipropiedad.ar/propiedades?ciudad=Olavarría
using Playwright to bypass Vercel bot protection.

For each listing, visits the detail page to extract exact GPS coordinates
from the JSON-LD structured data. Saves results to .tmp/listings.json

Usage:
  python3 tools/scrape_mipropiedad.py              # scrape all
  python3 tools/scrape_mipropiedad.py --limit 120  # stop after 120 detail pages
"""

import json
import os
import random
import re
import sys
import time

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from bs4 import BeautifulSoup

CITY = "Olavarría"
CITY_URL = f"https://mipropiedad.ar/propiedades?tipo-operacion=1&ciudad={CITY}"
BASE = "https://mipropiedad.ar"
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", ".tmp", "listings.json")
URLS_CHECKPOINT = os.path.join(os.path.dirname(__file__), "..", ".tmp", "urls_checkpoint.json")


def extract_cards(page):
    try:
        page.wait_for_selector("div[class*='grid'] a[class*='block']", timeout=10000)
    except PlaywrightTimeout:
        pass

    soup = BeautifulSoup(page.content(), "html.parser")
    cards = soup.select("div[class*='grid'] a[class*='block']")
    results = []

    for card in cards:
        price_el = card.select_one("div[class*='font-semibold'][class*='text-[#0A215B]']")
        if not price_el:
            continue
        price_text = price_el.get_text(strip=True)
        if not price_text or "consultar" in price_text.lower():
            continue

        title_el = card.select_one("h3")
        title = title_el.get_text(strip=True) if title_el else ""

        href = card.get("href", "")
        if href and not href.startswith("http"):
            href = BASE + href

        results.append({"title": title, "price": price_text, "url": href})

    return results, soup


def get_last_page(soup):
    nums = []
    for a in soup.select("a[href*='page=']"):
        m = re.search(r"page=(\d+)", a.get("href", ""))
        if m:
            nums.append(int(m.group(1)))
    return max(nums) if nums else 1


def extract_detail(page, url):
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        time.sleep(random.uniform(1.5, 2.5))
    except PlaywrightTimeout:
        return None

    soup = BeautifulSoup(page.content(), "html.parser")

    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string)
            graph = data.get("@graph", [data])
            for node in graph:
                types = node.get("@type", [])
                if isinstance(types, str):
                    types = [types]
                if "RealEstateListing" in types:
                    geo = node.get("geo", {})
                    addr = node.get("address", {})
                    return {
                        "lat": geo.get("latitude"),
                        "lng": geo.get("longitude"),
                        "street": addr.get("streetAddress", ""),
                    }
        except (json.JSONDecodeError, AttributeError):
            continue

    return None


def collect_urls(list_page):
    """Scrape all listing pages and return URL/title/price list. Uses checkpoint if available."""
    if os.path.exists(URLS_CHECKPOINT):
        print(f"  Loading URL checkpoint ({URLS_CHECKPOINT})")
        with open(URLS_CHECKPOINT, encoding="utf-8") as f:
            return json.load(f)

    all_listings = []
    print(f"Collecting listings from {CITY_URL} ...")
    list_page.goto(CITY_URL, wait_until="domcontentloaded", timeout=30000)
    time.sleep(random.uniform(2, 3))

    cards, soup = extract_cards(list_page)
    total_pages = get_last_page(soup)
    print(f"  Page 1/{total_pages}: {len(cards)} listings")
    all_listings.extend(cards)

    for page_num in range(2, total_pages + 1):
        url = f"{CITY_URL}&page={page_num}"
        list_page.goto(url, wait_until="domcontentloaded", timeout=30000)
        time.sleep(random.uniform(2, 4))
        cards, _ = extract_cards(list_page)
        print(f"  Page {page_num}/{total_pages}: {len(cards)} listings")
        if not cards:
            break
        all_listings.extend(cards)

    with open(URLS_CHECKPOINT, "w", encoding="utf-8") as f:
        json.dump(all_listings, f, ensure_ascii=False, indent=2)
    print(f"  Saved URL checkpoint ({len(all_listings)} listings)")
    return all_listings


def run(limit=None):
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    # Load any previously saved results to resume from
    existing = {}
    if os.path.exists(OUTPUT_PATH):
        with open(OUTPUT_PATH, encoding="utf-8") as f:
            try:
                for item in json.load(f):
                    existing[item["url"]] = item
            except (json.JSONDecodeError, KeyError):
                pass

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            locale="es-AR",
            viewport={"width": 1280, "height": 800},
        )
        list_page = context.new_page()
        detail_page = context.new_page()

        all_listings = collect_urls(list_page)
        print(f"\nTotal listings: {len(all_listings)}")

        enriched = list(existing.values())
        visited = 0

        for i, listing in enumerate(all_listings):
            if listing["url"] in existing:
                continue  # already have GPS for this one

            if limit and visited >= limit:
                print(f"  Reached limit of {limit} detail pages.")
                break

            print(f"  Detail [{i+1}/{len(all_listings)}] {listing['title'][:50]}...", end=" ")
            detail = extract_detail(detail_page, listing["url"])
            visited += 1

            if detail and detail.get("lat") and detail.get("lng"):
                listing.update(detail)
                enriched.append(listing)
                print(f"✓ {detail['street'][:40]}")
            else:
                print("✗ no coords")

            # Save incrementally
            with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
                json.dump(enriched, f, ensure_ascii=False, indent=2)

            time.sleep(random.uniform(1, 2))

        browser.close()

    print(f"\nSaved {len(enriched)} listings with GPS → {OUTPUT_PATH}")
    return enriched


if __name__ == "__main__":
    limit = None
    if "--limit" in sys.argv:
        idx = sys.argv.index("--limit")
        limit = int(sys.argv[idx + 1])
    run(limit=limit)
