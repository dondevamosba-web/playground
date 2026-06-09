#!/usr/bin/env python3
"""
Scrape upcoming electronic events in Argentina from Resident Advisor via their GraphQL API.
Uses direct API access (no geo-redirect issues from Firecrawl's US servers).

Usage:
  python3 tools/scrape_ra_events.py
  python3 tools/scrape_ra_events.py --city cordoba        # search area by name
  python3 tools/scrape_ra_events.py --area-id 395         # Buenos Aires (default)
  python3 tools/scrape_ra_events.py --days 60 --limit 40
  python3 tools/scrape_ra_events.py --output .tmp/my_events.json
"""

import argparse
import json
import os
import sys
from datetime import date, timedelta
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).parent.parent
load_dotenv(ROOT / ".env")

RA_GRAPHQL = "https://ra.co/graphql"
HEADERS = {
    "Content-Type": "application/json",
    "Referer": "https://ra.co/events/ar/buenos-aires",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Origin": "https://ra.co",
}

EVENTS_QUERY = """
query GET_RA_EVENTS($filters: FilterInputDtoInput, $pageSize: Int, $page: Int) {
  eventListings(filters: $filters, pageSize: $pageSize, page: $page, sort: {attending: {order: DESCENDING}}) {
    totalResults
    data {
      event {
        id
        title
        date
        startTime
        contentUrl
        images { filename type }
        venue { id name address }
        artists { id name }
      }
    }
  }
}
"""

AREA_QUERY = """
query { areas(searchTerm: $term, limit: 5) { id name country { name } } }
"""


def find_area_id(city_name: str) -> str | None:
    resp = requests.post(
        RA_GRAPHQL,
        headers=HEADERS,
        json={"query": "query($term: String) { areas(searchTerm: $term, limit: 5) { id name country { name } } }",
              "variables": {"term": city_name}},
        timeout=20,
    )
    areas = resp.json().get("data", {}).get("areas", [])
    arg_areas = [a for a in areas if a.get("country", {}).get("name") == "Argentina"]
    if arg_areas:
        print(f"Found area: {arg_areas[0]['name']} (ID {arg_areas[0]['id']})")
        return arg_areas[0]["id"]
    if areas:
        print(f"Found area: {areas[0]['name']} (ID {areas[0]['id']})")
        return areas[0]["id"]
    return None


def scrape_events(area_id: str = "395", days: int = 45, limit: int = 30) -> list[dict]:
    today = date.today().isoformat()
    until = (date.today() + timedelta(days=days)).isoformat()

    resp = requests.post(
        RA_GRAPHQL,
        headers=HEADERS,
        json={
            "query": EVENTS_QUERY,
            "variables": {
                "filters": {
                    "areas": {"eq": int(area_id)},
                    "listingDate": {"gte": today, "lte": until},
                },
                "pageSize": limit,
                "page": 1,
            },
        },
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()

    if "errors" in data:
        print(f"GraphQL error: {data['errors'][0]['message']}")
        return []

    root = data["data"]["eventListings"]
    total = root["totalResults"]
    print(f"Found {total} events in area {area_id} (next {days} days)")

    events = []
    for listing in root["data"]:
        ev = listing.get("event")
        if not ev:
            continue

        imgs = ev.get("images", [])
        img_url = next(
            (i["filename"] for i in imgs if "landscape" in str(i.get("type", ""))),
            imgs[0]["filename"] if imgs else "",
        )
        if img_url and not img_url.startswith("http"):
            img_url = "https://images.ra.co/" + img_url

        events.append({
            "name": ev["title"],
            "date": ev.get("date", "")[:10],
            "time": ev.get("startTime", ""),
            "venue": ev.get("venue", {}).get("name", ""),
            "city": "Buenos Aires",
            "artists": [a["name"] for a in ev.get("artists", [])],
            "image_url": img_url,
            "event_url": "https://ra.co" + ev.get("contentUrl", ""),
        })

    return events


def main():
    parser = argparse.ArgumentParser(description="Scrape RA Argentina events via GraphQL")
    parser.add_argument("--area-id", default="395", help="RA area ID (395 = Buenos Aires)")
    parser.add_argument("--city", default=None, help="Search area by name e.g. 'Cordoba'")
    parser.add_argument("--days", type=int, default=45, help="Days ahead to look")
    parser.add_argument("--limit", type=int, default=30, help="Max events")
    parser.add_argument("--output", default=".tmp/ra_events.json")
    args = parser.parse_args()

    os.makedirs(".tmp", exist_ok=True)

    area_id = args.area_id
    if args.city:
        found = find_area_id(args.city)
        if not found:
            print(f"Area '{args.city}' not found on RA. Using Buenos Aires (395).")
        else:
            area_id = found

    events = scrape_events(area_id=area_id, days=args.days, limit=args.limit)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(events, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(events)} events → {args.output}")
    for e in events:
        artists = ", ".join(e["artists"][:2]) or "TBC"
        print(f"  {e['date']} — {e['name']} @ {e['venue']} [{artists}]")


if __name__ == "__main__":
    main()
