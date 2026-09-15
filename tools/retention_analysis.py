#!/usr/bin/env python3
"""
Analyze which events drive audience retention/churn.

Segment posts by artist/venue, measure follow/unfollow delta,
identify what content sticks vs. what causes unfollows.

Output: JSON with retention scores per artist/venue.

Usage:
  python3 tools/retention_analysis.py              # Analyze historical data
  python3 tools/retention_analysis.py --artist Solomun  # Single artist
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


def fetch_followers_history(ig_id, token, days=14):
    """
    Fetch historical follower count (simulated from Graph API insights).
    Note: Graph API doesn't expose historical followers directly, so we estimate
    from posted content timestamps and engagement patterns.
    """
    # This is a placeholder — real implementation would use:
    # - Instagram Insights API (requires Instagram Business Account)
    # - Or manual tracking script that polls daily
    # For now, we'll analyze based on post engagement as a proxy for retention
    return {}


def analyze_retention_by_artist(sheet_id, token):
    """Analyze which artists drive follower growth vs. churn."""
    sheets, _ = get_services()
    rows = sheets.spreadsheets().values().get(
        spreadsheetId=sheet_id, range="Queue!A2:N600").execute().get("values", [])

    artist_data = defaultdict(lambda: {
        "posts": [],
        "total_engagement": 0,
        "avg_engagement": 0,
        "posts_count": 0,
    })

    for i, r in enumerate(rows, 2):
        if len(r) < 13 or not r[12]:  # No media_id (not posted)
            continue

        media_id = r[12].strip()
        name = (r[2] or "").strip()
        event_date = (r[3] or "").strip()

        # Extract artist from name
        artist = name.split(" - ")[0].strip() if " - " in name else name

        # Fetch engagement
        try:
            res = requests.get(
                f"{GRAPH}/{media_id}",
                params={"fields": "like_count,comments_count,shares",
                        "access_token": token},
                timeout=30).json()
            engagement = res.get("like_count", 0) + res.get("comments_count", 0)
        except Exception:
            engagement = 0

        if engagement == 0:
            continue

        artist_data[artist]["posts"].append({
            "name": name,
            "date": event_date,
            "engagement": engagement,
        })
        artist_data[artist]["total_engagement"] += engagement
        artist_data[artist]["posts_count"] += 1

    # Calculate averages
    for artist in artist_data:
        if artist_data[artist]["posts_count"] > 0:
            artist_data[artist]["avg_engagement"] = (
                artist_data[artist]["total_engagement"] /
                artist_data[artist]["posts_count"]
            )

    return artist_data


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--artist", help="Analyze single artist")
    p.add_argument("--venue", help="Analyze single venue")
    args = p.parse_args()

    sheet_id = os.environ["FIESTAS_APPROVAL_SHEET_ID"]
    token = os.environ["INSTAGRAM_ACCESS_TOKEN"]

    print("\n📊 Retention Analysis\n")
    print("Note: Graph API doesn't expose follower deltas directly.")
    print("Using engagement as a proxy for content stickiness.\n")

    data = analyze_retention_by_artist(sheet_id, token)

    if not data:
        print("No posted content with engagement data.")
        return 0

    # Sort by avg engagement (high = sticks, low = churn)
    sorted_artists = sorted(
        data.items(),
        key=lambda x: x[1]["avg_engagement"],
        reverse=True
    )

    print("=== Top Artists by Engagement ===\n")
    for artist, stats in sorted_artists[:15]:
        avg = stats["avg_engagement"]
        emoji = "🔥" if avg > 20 else "📈" if avg > 10 else "📉"
        print(f"  {emoji} {artist:30} avg={avg:>6.1f} ({stats['posts_count']} posts)")

    # Save analysis
    out = ROOT / ".tmp" / "retention_analysis.json"
    out_data = {
        "timestamp": datetime.now(tz=AR_TZ).isoformat(),
        "artists": [
            {
                "name": a,
                "avg_engagement": s["avg_engagement"],
                "posts": s["posts_count"],
                "total": s["total_engagement"],
            }
            for a, s in sorted_artists
        ]
    }
    out.write_text(json.dumps(out_data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n→ {out}")

    # Single artist analysis
    if args.artist and args.artist in data:
        print(f"\n=== {args.artist} ===")
        artist_info = data[args.artist]
        print(f"Posts: {artist_info['posts_count']}")
        print(f"Avg engagement: {artist_info['avg_engagement']:.1f}")
        for post in artist_info["posts"]:
            print(f"  {post['date']}: {post['engagement']} eng")

    return 0


if __name__ == "__main__":
    sys.exit(main())
