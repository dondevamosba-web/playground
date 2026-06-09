#!/usr/bin/env python3
"""
Flight price checker using Serpapi Google Flights.
Searches multiple departure dates and returns the cheapest options.

Usage:
    python tools/check_flights.py --origin EZE --destination CUN --weeks 18 --results 5
    python tools/check_flights.py --no-email

Requires:
    SERPAPI_KEY in .env
"""

import argparse
import os
import sys
from datetime import datetime, timedelta

import requests
from dotenv import load_dotenv

load_dotenv()

SERPAPI_KEY = os.getenv("SERPAPI_KEY")
RECIPIENT_EMAIL = os.getenv("GMAIL_RECIPIENT_EMAIL", "carminattiguido@gmail.com")
SERPAPI_URL = "https://serpapi.com/search"


def search_week(origin: str, destination: str, dep_date: str, return_date: str) -> list:
    params = {
        "engine": "google_flights",
        "departure_id": origin,
        "arrival_id": destination,
        "outbound_date": dep_date,
        "return_date": return_date,
        "currency": "USD",
        "hl": "en",
        "type": "1",
        "api_key": SERPAPI_KEY,
    }
    resp = requests.get(SERPAPI_URL, params=params, timeout=20)
    if resp.status_code != 200:
        return []
    data = resp.json()
    flights = data.get("best_flights", []) + data.get("other_flights", [])
    results = []
    for f in flights:
        legs = f.get("flights", [])
        if not legs:
            continue
        results.append({
            "dep_date": dep_date,
            "return_date": return_date,
            "price": f.get("price", 9999),
            "airline": legs[0].get("airline", "?"),
            "duration": f.get("total_duration", 0),
            "stops": len(legs) - 1,
        })
    return results


def search_flexible(origin: str, destination: str, weeks: int, stay_days: int, step: int = 1) -> list:
    all_results = []
    today = datetime.now()
    days_until_friday = (4 - today.weekday()) % 7 or 7
    first_friday = today + timedelta(days=days_until_friday + 7)

    for i in range(0, weeks, step):
        dep = first_friday + timedelta(weeks=i)
        ret = dep + timedelta(days=stay_days)
        dep_str = dep.strftime("%Y-%m-%d")
        ret_str = ret.strftime("%Y-%m-%d")
        print(f"  Checking {dep_str} → {ret_str}...", flush=True)
        all_results.extend(search_week(origin, destination, dep_str, ret_str))

    all_results.sort(key=lambda x: x["price"])
    return all_results


def format_results(origin: str, destination: str, results: list, top_n: int) -> tuple:
    subject = f"✈️  {origin} → {destination} cheapest flights — {datetime.now().strftime('%b %d')}"
    if not results:
        return subject, f"No flights found for {origin} → {destination}."
    lines = [f"Cheapest {origin} → {destination} round trips:\n"]
    for i, r in enumerate(results[:top_n], 1):
        stops = "direct" if r["stops"] == 0 else f"{r['stops']} stop{'s' if r['stops'] > 1 else ''}"
        h, m = divmod(r["duration"], 60)
        lines.append(
            f"#{i}  ${r['price']} USD  |  Depart {r['dep_date']}  |  Return {r['return_date']}  "
            f"|  {r['airline']}  |  {stops}  |  {h}h{m:02d}m"
        )
    lines.append(f"\nAll prices USD, round trip. Searched {datetime.now().strftime('%Y-%m-%d %H:%M')}.")
    return subject, "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--origin", default="EZE")
    parser.add_argument("--destination", default="GIG")
    parser.add_argument("--weeks", type=int, default=8)
    parser.add_argument("--stay", type=int, default=7)
    parser.add_argument("--step", type=int, default=1)
    parser.add_argument("--results", type=int, default=5)
    parser.add_argument("--max-price", type=int, default=None)
    parser.add_argument("--no-email", action="store_true")
    args = parser.parse_args()

    if not SERPAPI_KEY:
        print("ERROR: SERPAPI_KEY not set in .env")
        sys.exit(1)

    print(f"Searching {args.origin} → {args.destination}, {args.weeks} weeks...")
    results = search_flexible(args.origin, args.destination, args.weeks, args.stay, args.step)
    if args.max_price:
        results = [r for r in results if r["price"] < args.max_price]
    print(f"Done. {len(results)} options found.")

    subject, body = format_results(args.origin, args.destination, results, args.results)

    if args.no_email:
        print(f"\n{subject}\n\n{body}")
    else:
        print("\n--- EMAIL DRAFT ---")
        print(f"TO: {RECIPIENT_EMAIL}")
        print(f"SUBJECT: {subject}")
        print(f"BODY:\n{body}")
        print("--- END DRAFT ---")


if __name__ == "__main__":
    main()
