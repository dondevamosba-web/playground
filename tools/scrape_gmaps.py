"""
Generic Google Maps scraper for any local service vertical.

Extracts: name, address, phone, website, rating, review count.
"Small" = fewer than 100 reviews (proxy for size).

Usage:
  python3 tools/scrape_gmaps.py --vertical landscaping
  python3 tools/scrape_gmaps.py --vertical plumbing --cities "Austin TX,Denver CO"
  python3 tools/scrape_gmaps.py --vertical dental --limit 30

Supported verticals: landscaping, plumbing, dental, solar, chiropractic,
                     roofing, hvac, pest_control, electrician, painting
"""

import argparse
import json
import os
import random
import time

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

TMP_DIR = os.path.join(os.path.dirname(__file__), "..", ".tmp")

DEFAULT_CITIES = [
    "Austin TX", "San Antonio TX", "Jacksonville FL", "Columbus OH",
    "Charlotte NC", "Indianapolis IN", "Fort Worth TX", "Memphis TN",
    "Louisville KY", "Baltimore MD", "Milwaukee WI", "Albuquerque NM",
    "Tucson AZ", "Fresno CA", "Sacramento CA", "Mesa AZ",
    "Kansas City MO", "Omaha NE", "Raleigh NC", "Virginia Beach VA",
]

VERTICAL_QUERIES = {
    "landscaping":    "landscaping company",
    "plumbing":       "plumber",
    "dental":         "dentist",
    "solar":          "solar panel installation",
    "chiropractic":   "chiropractor",
    "roofing":        "roofing contractor",
    "hvac":           "HVAC contractor",
    "pest_control":   "pest control company",
    "electrician":    "electrician",
    "painting":       "painting contractor",
}

SMALL_THRESHOLD = 100


def scrape_city(page, city: str, query: str, limit: int) -> list[dict]:
    url = f"https://www.google.com/maps/search/{(query + ' ' + city).replace(' ', '+')}"
    print(f"  → {city}")

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

    while len(results) < limit and scroll_attempts < 15:
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

        if page.query_selector("span.HlvSq"):
            break

    for i in range(min(len(results), limit)):
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--vertical", required=True, choices=list(VERTICAL_QUERIES.keys()),
                        help="Service vertical to scrape")
    parser.add_argument("--cities", default=None, help="Comma-separated 'City ST' list")
    parser.add_argument("--limit", type=int, default=20, help="Max results per city")
    args = parser.parse_args()

    query = VERTICAL_QUERIES[args.vertical]
    output_path = os.path.join(TMP_DIR, f"{args.vertical}_leads.json")
    cities = [c.strip() for c in args.cities.split(",")] if args.cities else DEFAULT_CITIES

    existing = []
    if os.path.exists(output_path):
        with open(output_path) as f:
            existing = json.load(f)
    existing_keys = {(r["name"], r["city"]) for r in existing}
    all_leads = list(existing)

    print(f"Vertical: {args.vertical} | Query: '{query}'\n"
          f"Cities: {len(cities)} | Limit: {args.limit}/city\n")

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
                city_leads = scrape_city(page, city, query, args.limit)
                new = [r for r in city_leads if (r["name"], r["city"]) not in existing_keys]
                all_leads.extend(new)
                for r in new:
                    existing_keys.add((r["name"], r["city"]))
                print(f"    {len(new)} new leads from {city} (total: {len(all_leads)})")
                os.makedirs(TMP_DIR, exist_ok=True)
                with open(output_path, "w") as f:
                    json.dump(all_leads, f, indent=2, ensure_ascii=False)
                time.sleep(random.uniform(3.0, 6.0))
            except Exception as e:
                print(f"    error on {city}: {e}")
                continue

        browser.close()

    print(f"\nDone. {len(all_leads)} total leads → {output_path}")


if __name__ == "__main__":
    main()
