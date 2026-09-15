#!/usr/bin/env python3
"""
Predict trending artistas and venues.

Analyzes historical engagement data to identify high-performing artists.
Pre-queues their upcoming events 2-3 weeks before venues post them.

Output: JSON with artist/venue scores + recommendations for pre-queueing.

Usage:
  python3 tools/predict_trending.py                    # Analyze + recommend
  python3 tools/predict_trending.py --venue VENUE_NAME # Single venue analysis
"""
import argparse
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

import requests
from tools.sheets_client import get_services

GRAPH = "https://graph.facebook.com/v19.0"
AR_TZ = timezone(timedelta(hours=-3))


def fetch_metrics(media_id, token):
    """Get engagement for a media item."""
    try:
        res = requests.get(
            f"{GRAPH}/{media_id}",
            params={"fields": "like_count,comments_count,media_product_type",
                    "access_token": token},
            timeout=30).json()
        if "error" in res:
            return None
        return res.get("like_count", 0) + res.get("comments_count", 0)
    except Exception:
        return None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--venue", help="Analyze single venue")
    args = p.parse_args()

    sheets, _ = get_services()
    sid = os.environ["FIESTAS_APPROVAL_SHEET_ID"]
    token = os.environ["INSTAGRAM_ACCESS_TOKEN"]

    rows = sheets.spreadsheets().values().get(
        spreadsheetId=sid, range="Queue!A2:N600").execute().get("values", [])

    # Collect engagement per artist/venue
    artist_data = defaultdict(lambda: {"total": 0, "count": 0, "posts": []})
    venue_data = defaultdict(lambda: {"total": 0, "count": 0, "posts": []})

    for i, r in enumerate(rows, 2):
        if len(r) < 13 or not r[12]:
            continue

        media_id = r[12].strip()
        name = (r[2] or "").strip()
        event_date = (r[3] or "").strip()

        engagement = fetch_metrics(media_id, token)
        if engagement is None or engagement == 0:
            continue

        # Parse artist and venue from name
        # Format usually: "Artist Name - Venue Name" or "Artist (LIVE) - Venue"
        parts = name.split(" - ")
        artist = parts[0].strip() if parts else name
        venue = parts[1].strip() if len(parts) > 1 else "unknown"

        # Clean up artist name (remove venue markers)
        artist = artist.replace(" (LIVE)", "").replace(" (OPEN TO CLOSE)", "").strip()

        artist_data[artist]["total"] += engagement
        artist_data[artist]["count"] += 1
        artist_data[artist]["posts"].append({"name": name, "date": event_date, "eng": engagement})

        venue_data[venue]["total"] += engagement
        venue_data[venue]["count"] += 1
        venue_data[venue]["posts"].append({"name": name, "date": event_date, "eng": engagement})

    # Calculate averages and trends
    artist_scores = {}
    for artist, data in artist_data.items():
        if data["count"] >= 2:  # Only if 2+ posts
            avg = data["total"] / data["count"]
            # Trending: if last post had higher engagement than average
            trend = "📈" if data["posts"][-1]["eng"] > avg else "📉"
            artist_scores[artist] = {
                "avg_engagement": round(avg, 1),
                "posts": data["count"],
                "total": data["total"],
                "trend": trend,
                "last_post": data["posts"][-1],
            }

    venue_scores = {}
    for venue, data in venue_data.items():
        if data["count"] >= 2:
            avg = data["total"] / data["count"]
            trend = "📈" if data["posts"][-1]["eng"] > avg else "📉"
            venue_scores[venue] = {
                "avg_engagement": round(avg, 1),
                "posts": data["count"],
                "total": data["total"],
                "trend": trend,
            }

    # Sort by engagement
    top_artists = sorted(artist_scores.items(), key=lambda x: x[1]["avg_engagement"], reverse=True)
    top_venues = sorted(venue_scores.items(), key=lambda x: x[1]["avg_engagement"], reverse=True)

    # Output
    print("\n=== TOP ARTISTAS (por engagement promedio) ===\n")
    for artist, score in top_artists[:15]:
        trend = score["trend"]
        avg = score["avg_engagement"]
        print(f"  {trend} {artist:30} avg={avg:>5.1f} ({score['posts']} posts)")

    print("\n=== TOP VENUES ===\n")
    for venue, score in top_venues[:10]:
        trend = score["trend"]
        avg = score["avg_engagement"]
        print(f"  {trend} {venue:30} avg={avg:>5.1f} ({score['posts']} posts)")

    # Save prediction data
    prediction = {
        "timestamp": datetime.now(tz=AR_TZ).isoformat(),
        "top_artists": top_artists[:30],
        "top_venues": top_venues[:15],
        "recommendations": {
            "high_roi": [a for a, _ in top_artists[:5]],
            "trending": [a for a, s in top_artists if s["trend"] == "📈"][:5],
            "declining": [a for a, s in top_artists if s["trend"] == "📉"][:5],
        }
    }

    out = ROOT / ".tmp" / "prediction_trending.json"
    out.write_text(json.dumps(prediction, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n→ {out}")

    # Single venue analysis
    if args.venue and args.venue in venue_scores:
        print(f"\n=== Análisis: {args.venue} ===")
        score = venue_scores[args.venue]
        print(f"Promedio: {score['avg_engagement']}")
        print(f"Posts: {score['posts']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
