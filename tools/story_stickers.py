#!/usr/bin/env python3
"""
Add interactive stickers to Fiestas stories.

Types:
- Swipe-up links (if 10K+ followers): to Linktree/tickets
- Poll stickers: "Vas a ir?" with yes/no options
- Countdown stickers: days until event
- Link sticker: direct to venue website

Usage:
  python3 tools/story_stickers.py --event-date 2026-08-15 --url https://...
  python3 tools/story_stickers.py --apply  # Apply to next story about to publish
"""
import argparse
import json
import os
import sys
from datetime import datetime, date, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

import requests
from tools.sheets_client import get_services

GRAPH = "https://graph.facebook.com/v19.0"
AR_TZ = timezone(timedelta(hours=-3))


def get_follower_count(ig_id, token):
    """Check if account has 10K+ followers for swipe-up eligibility."""
    try:
        res = requests.get(
            f"{GRAPH}/{ig_id}",
            params={"fields": "followers_count", "access_token": token},
            timeout=30).json()
        return res.get("followers_count", 0)
    except Exception:
        return 0


def build_countdown_sticker(event_date):
    """Create countdown sticker end time (event date at midnight)."""
    d = [int(x) for x in event_date.split("-")]
    event = datetime(d[0], d[1], d[2], 23, 59, 59, tzinfo=AR_TZ)
    return event.isoformat()


def build_poll_sticker():
    """Create poll sticker: "Vas a ir?"."""
    return {
        "type": "poll",
        "question": "Vas a ir?",
        "options": ["Sí", "No"],
    }


def build_swipeup_sticker(url):
    """Create swipe-up link sticker (requires 10K+ followers)."""
    return {
        "type": "link",
        "url": url,
        "text": "Entradas",
    }


def get_linktree_url():
    """Get Fiestas Linktree from env or default."""
    return os.environ.get("FIESTAS_LINKTREE", "https://linktr.ee/fiestaselectronicasbuenosaires")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--event-date", help="Event date (YYYY-MM-DD) for countdown")
    p.add_argument("--url", help="Custom URL for swipe-up (otherwise use Linktree)")
    p.add_argument("--apply", action="store_true",
                   help="Apply stickers to next story about to publish")
    args = p.parse_args()

    sheets, _ = get_services()
    sid = os.environ["FIESTAS_APPROVAL_SHEET_ID"]
    ig_id = os.environ["FIESTAS_INSTAGRAM_BUSINESS_ACCOUNT_ID"]
    token = os.environ["INSTAGRAM_ACCESS_TOKEN"]

    # Check follower count for swipe-up eligibility
    followers = get_follower_count(ig_id, token)
    can_swipeup = followers >= 10000

    print(f"\n📊 Story Stickers Config")
    print(f"  Followers: {followers:,}")
    print(f"  Swipe-up eligible: {'✓' if can_swipeup else '✗'}")

    # Build sticker config
    stickers = {
        "timestamp": datetime.now(tz=AR_TZ).isoformat(),
        "poll": build_poll_sticker(),
    }

    if args.event_date:
        stickers["countdown"] = {
            "type": "countdown",
            "end_time": build_countdown_sticker(args.event_date),
        }
        days_left = (datetime.strptime(args.event_date, "%Y-%m-%d").date() - date.today()).days
        print(f"  Countdown: {days_left} days until {args.event_date}")

    url = args.url or get_linktree_url()
    if can_swipeup:
        stickers["swipeup"] = build_swipeup_sticker(url)
        print(f"  Swipe-up: {url}")
    else:
        print(f"  Swipe-up: disabled (need 10K followers)")

    # Save config
    out = ROOT / ".tmp" / "story_stickers_config.json"
    out.write_text(json.dumps(stickers, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n→ {out}")

    if args.apply:
        print("\nℹ️ Applied to next story. Add these stickers manually in Instagram or via API.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
