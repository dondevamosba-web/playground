#!/usr/bin/env python3
"""
Scrape upcoming electronic/dance music events in Argentina via the Ticketmaster Discovery API v2.

No ticketmaster.com.ar exists — this uses the official global Discovery API with countryCode=AR.
Get a free API key (5000 req/day) at: https://developer.ticketmaster.com/

Setup:
  Add to .env:  TM_API_KEY=your_key_here

Usage:
  python3 tools/scrape_ticketmaster_ar.py
  python3 tools/scrape_ticketmaster_ar.py --days 60 --limit 50
  python3 tools/scrape_ticketmaster_ar.py --output .tmp/tm_events.json
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

TM_API_KEY = os.getenv("TM_API_KEY", "").strip()
TM_BASE = "https://app.ticketmaster.com/discovery/v2/events.json"

# Ticketmaster genre/subgenre IDs for electronic music in AR
# classificationName filters work too, but IDs are more precise.
# We search multiple terms to maximise coverage.
SEARCH_TERMS = ["electronic", "dance", "techno", "EDM", "electronica"]


def scrape_events(days: int = 45, limit: int = 50) -> list[dict]:
    if not TM_API_KEY:
        print("ERROR: TM_API_KEY not set in .env — get a free key at developer.ticketmaster.com")
        return []

    today = date.today()
    start_dt = today.strftime("%Y-%m-%dT00:00:00Z")
    end_dt = (today + timedelta(days=days)).strftime("%Y-%m-%dT23:59:59Z")

    seen_ids = set()
    events = []

    for term in SEARCH_TERMS:
        params = {
            "apikey": TM_API_KEY,
            "countryCode": "AR",
            "classificationName": term,
            "startDateTime": start_dt,
            "endDateTime": end_dt,
            "size": limit,
            "sort": "date,asc",
        }

        try:
            resp = requests.get(TM_BASE, params=params, timeout=20)
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"  WARN: Ticketmaster API error for '{term}': {e}")
            continue

        data = resp.json()
        embedded = data.get("_embedded", {})
        raw_events = embedded.get("events", [])
        print(f"  '{term}': {len(raw_events)} results")

        for ev in raw_events:
            ev_id = ev.get("id", "")
            if ev_id in seen_ids:
                continue
            seen_ids.add(ev_id)

            # Date
            dates = ev.get("dates", {})
            ev_date = dates.get("start", {}).get("localDate", "")

            # Venue + city
            venues = ev.get("_embedded", {}).get("venues", [{}])
            venue = venues[0].get("name", "") if venues else ""
            city = venues[0].get("city", {}).get("name", "") if venues else ""
            if not city:
                city = "Argentina"

            # Artists (attractions)
            attractions = ev.get("_embedded", {}).get("attractions", [])
            artists = [a["name"] for a in attractions if a.get("name")]

            # Image — prefer 16:9 ratio image
            images = ev.get("images", [])
            img_url = ""
            for img in images:
                if img.get("ratio") == "16_9" and img.get("width", 0) >= 640:
                    img_url = img.get("url", "")
                    break
            if not img_url and images:
                img_url = images[0].get("url", "")

            # Ticket URL
            ticket_url = ev.get("url", "")

            events.append({
                "name": ev.get("name", ""),
                "date": ev_date,
                "time": dates.get("start", {}).get("localTime", ""),
                "venue": venue,
                "city": city,
                "artists": artists,
                "image_url": img_url,
                "event_url": ticket_url,
            })

        if len(events) >= limit:
            break

    return events


def main():
    parser = argparse.ArgumentParser(description="Scrape Ticketmaster AR electronic events via Discovery API")
    parser.add_argument("--days", type=int, default=45, help="Days ahead to look")
    parser.add_argument("--limit", type=int, default=50, help="Max events total")
    parser.add_argument("--output", default=".tmp/tm_ar_events.json")
    args = parser.parse_args()

    os.makedirs(".tmp", exist_ok=True)

    print("Scraping Ticketmaster Discovery API (Argentina, electronic)...")
    events = scrape_events(days=args.days, limit=args.limit)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(events, f, indent=2, ensure_ascii=False)

    print(f"\nSaved {len(events)} events → {args.output}")
    for e in events:
        artists = ", ".join(e["artists"][:2]) or "TBC"
        print(f"  {e['date']} — {e['name']} @ {e['venue']}, {e['city']} [{artists}]")


if __name__ == "__main__":
    main()
