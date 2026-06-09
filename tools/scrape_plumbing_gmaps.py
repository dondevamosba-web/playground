"""
Scrapes Google Maps for small plumbing contractors in US cities.
Extracts: name, address, phone, website, rating, review count.

"Small" = fewer than 100 reviews (proxy for size).

Usage:
  python3 tools/scrape_plumbing_gmaps.py                     # default cities
  python3 tools/scrape_plumbing_gmaps.py --cities "Austin TX,Denver CO"
  python3 tools/scrape_plumbing_gmaps.py --limit 50          # max results per city
"""

import argparse
import json
import os
import random
import time

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", ".tmp", "plumbing_leads.json")

DEFAULT_CITIES = [
    "Austin TX", "San Antonio TX", "Jacksonville FL", "Columbus OH",
    "Charlotte NC", "Indianapolis IN", "Fort Worth TX", "Memphis TN",
    "Louisville KY", "Baltimore MD", "Milwaukee WI", "Albuquerque NM",
    "Tucson AZ", "Fresno CA", "Sacramento CA", "Mesa AZ",
    "Kansas City MO", "Omaha NE", "Raleigh NC", "Virginia Beach VA",
    "Denver CO", "Nashville TN", "Oklahoma City OK", "El Paso TX",
]

SMALL_THRESHOLD = 100

SEARCH_QUERIES = [
    "plumber",
    "plumbing company",
    "plumbing contractor",
    "plumbing repair service",
]


def scrape_city(page, city: str, limit: int) -> list:
    query = f"{random.choice(SEARCH_QUERIES)} {city}"
    url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}"
    print(f"  → {city}  [{query.split(city)[0].strip()}]")

    try:
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        time.sleep(random.uniform(2.5, 4.0))
    except PlaywrightTimeout:
        print(f"    timeout loading {city}, skipping")
        return []

    for selector in ['button[aria-label*="Accept"]', 'button[aria-label*="Agree"]']:
        try:
            btn = page.query_selector(selector)
            if btn:
                btn.click()
                time.sleep(1)
        except Exception:
            pass

    results = []
    seen_names = set()
    scroll_attempts = 0
    max_scrolls = 15

    while len(results) < limit and scroll_attempts < max_scrolls:
        cards = page.query_selector_all('div[role="feed"] > div')
        for card in cards:
            if len(results) >= limit:
                break
            try:
                name_el = card.query_selector('div.fontHeadlineSmall, span.fontHeadlineSmall, h3')
                if not name_el:
                    continue
                name = name_el.inner_text().strip()
                if not name or name in seen_names:
                    continue

                rating = None
                review_count = None
                rating_el = card.query_selector('span.MW4etd')
                reviews_el = card.query_selector('span.UY7F9')
                if rating_el:
                    try:
                        rating = float(rating_el.inner_text().strip())
                    except ValueError:
                        pass
                if reviews_el:
                    raw = reviews_el.inner_text().strip().replace("(", "").replace(")", "").replace(",", "")
                    try:
                        review_count = int(raw)
                    except ValueError:
                        pass

                if review_count and review_count > SMALL_THRESHOLD:
                    continue

                address = None
                addr_els = card.query_selector_all('div.W4Etjb, div[jsan*="address"]')
                if addr_els:
                    address = addr_els[0].inner_text().strip()

                seen_names.add(name)
                results.append({
                    "name": name,
                    "city": city,
                    "address": address,
                    "rating": rating,
                    "review_count": review_count,
                    "phone": None,
                    "website": None,
                    "email": None,
                    "fb_ads_status": None,
                })
            except Exception:
                continue

        feed = page.query_selector('div[role="feed"]')
        if feed:
            feed.evaluate("el => el.scrollTop += 1200")
        else:
            page.keyboard.press("PageDown")
        time.sleep(random.uniform(1.5, 2.5))
        scroll_attempts += 1

        end_el = page.query_selector("span.HlvSq")
        if end_el:
            break

    enrich_count = min(len(results), limit)
    for i in range(enrich_count):
        results[i] = enrich_detail(page, results[i], city)
        time.sleep(random.uniform(1.8, 3.2))

    return results


def enrich_detail(page, lead: dict, city: str) -> dict:
    query = f"{lead['name']} {city}"
    url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}"
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=20000)
        time.sleep(random.uniform(2.0, 3.0))

        first = page.query_selector('div[role="feed"] > div:first-child')
        if first:
            first.click()
            time.sleep(random.uniform(1.5, 2.5))

        phone_el = page.query_selector('button[data-item-id*="phone"] div.fontBodyMedium')
        if phone_el:
            lead["phone"] = phone_el.inner_text().strip()

        website_el = page.query_selector('a[data-item-id*="authority"]')
        if website_el:
            href = website_el.get_attribute("href")
            if href:
                lead["website"] = href

    except Exception:
        pass
    return lead


def load_existing() -> list:
    if os.path.exists(OUTPUT_PATH):
        with open(OUTPUT_PATH) as f:
            return json.load(f)
    return []


def save(leads: list):
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(leads, f, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cities", default=None, help="Comma-separated list of 'City ST'")
    parser.add_argument("--limit", type=int, default=20, help="Max results per city")
    args = parser.parse_args()

    cities = [c.strip() for c in args.cities.split(",")] if args.cities else DEFAULT_CITIES

    existing = load_existing()
    existing_keys = {(r["name"], r["city"]) for r in existing}
    all_leads = list(existing)

    print(f"Scraping {len(cities)} cities, up to {args.limit} small plumbing companies each...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 900},
        )
        page = ctx.new_page()

        for city in cities:
            try:
                city_leads = scrape_city(page, city, args.limit)
                new = [r for r in city_leads if (r["name"], r["city"]) not in existing_keys]
                all_leads.extend(new)
                for r in new:
                    existing_keys.add((r["name"], r["city"]))
                print(f"    {len(new)} new leads from {city} (total: {len(all_leads)})")
                save(all_leads)
                time.sleep(random.uniform(3.0, 6.0))
            except Exception as e:
                print(f"    error on {city}: {e}")
                continue

        browser.close()

    print(f"\nDone. {len(all_leads)} total leads saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
