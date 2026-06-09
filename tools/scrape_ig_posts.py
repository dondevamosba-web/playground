#!/usr/bin/env python3
"""
Scrape recent posts from public Instagram accounts using instaloader.
Filters for event-related posts and outputs structured JSON.

Accounts to monitor are set in .env as FIESTAS_IG_SOURCE_ACCOUNTS (comma-separated)
or passed directly as arguments.

Usage:
  python3 tools/scrape_ig_posts.py                              # uses .env list
  python3 tools/scrape_ig_posts.py musicaelectronica.club baires.electronica
  python3 tools/scrape_ig_posts.py musicaelectronica.club --limit 6
  python3 tools/scrape_ig_posts.py --shortcodes DZNZgKlEee6 DY7bIOIDrZs   # specific posts
  python3 tools/scrape_ig_posts.py --output .tmp/ig_posts.json
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

import instaloader
from dotenv import load_dotenv

ROOT = Path(__file__).parent.parent
load_dotenv(ROOT / ".env")

SOURCE_ACCOUNTS_ENV = os.getenv("FIESTAS_IG_SOURCE_ACCOUNTS", "")

EVENT_KEYWORDS = [
    "fiesta", "party", "evento", "event", "dj", "techno", "house", "electróni",
    "electroni", "ticket", "entrada", "venue", "club", "boliche", "after",
    "lineup", "presenta", "pres.", "pres ", "open to close", "live set",
    "arena", "festival", "rave", "baile", "pista", "soundsystem",
]


def looks_like_event(caption: str) -> bool:
    if not caption:
        return False
    low = caption.lower()
    return any(kw in low for kw in EVENT_KEYWORDS)


def scrape_shortcodes(shortcodes: list[str], L: instaloader.Instaloader) -> list[dict]:
    posts = []
    for sc in shortcodes:
        try:
            post = instaloader.Post.from_shortcode(L.context, sc)
            posts.append({
                "shortcode": sc,
                "post_url": f"https://www.instagram.com/p/{sc}/",
                "source_account": post.owner_username,
                "caption": post.caption or "",
                "date": str(post.date.date()),
                "image_url": post.url,
                "is_video": post.is_video,
                "is_event": looks_like_event(post.caption or ""),
            })
            print(f"  OK @{post.owner_username}: {(post.caption or '')[:70]}")
            time.sleep(1)
        except Exception as e:
            print(f"  FAIL {sc}: {e}")
    return posts


def scrape_profile(handle: str, limit: int, L: instaloader.Instaloader) -> list[dict]:
    handle = handle.lstrip("@")
    try:
        profile = instaloader.Profile.from_username(L.context, handle)
        print(f"  @{handle}: {profile.followers} followers")
    except Exception as e:
        print(f"  FAIL @{handle}: {e}")
        return []

    posts = []
    try:
        for i, post in enumerate(profile.get_posts()):
            if i >= limit:
                break
            posts.append({
                "shortcode": post.shortcode,
                "post_url": f"https://www.instagram.com/p/{post.shortcode}/",
                "source_account": handle,
                "caption": post.caption or "",
                "date": str(post.date.date()),
                "image_url": post.url,
                "is_video": post.is_video,
                "is_event": looks_like_event(post.caption or ""),
            })
            time.sleep(1.5)  # be polite to IG rate limits
    except Exception as e:
        print(f"  Error reading posts for @{handle}: {e}")

    event_count = sum(1 for p in posts if p["is_event"])
    print(f"  {len(posts)} posts, {event_count} flagged as events")
    return posts


def main():
    parser = argparse.ArgumentParser(description="Scrape IG accounts for event posts")
    parser.add_argument("handles", nargs="*", help="IG handles (without @)")
    parser.add_argument("--shortcodes", nargs="+", help="Specific post shortcodes to fetch")
    parser.add_argument("--limit", type=int, default=12, help="Posts per account")
    parser.add_argument("--output", default=".tmp/ig_posts.json")
    args = parser.parse_args()

    L = instaloader.Instaloader(
        quiet=True,
        download_pictures=False,
        download_videos=False,
        download_video_thumbnails=False,
        save_metadata=False,
    )

    ig_user = os.getenv("IG_SCRAPER_USERNAME", "")
    ig_pass = os.getenv("IG_SCRAPER_PASSWORD", "")
    if ig_user and ig_pass:
        try:
            L.login(ig_user, ig_pass)
            print(f"Logged in as @{ig_user}")
        except Exception as e:
            print(f"Login failed: {e} — Instagram will likely block unauthenticated scraping")
    else:
        print("No IG_SCRAPER_USERNAME/PASSWORD in .env — Instagram may return 403")

    os.makedirs(".tmp", exist_ok=True)
    all_posts = []

    # Specific shortcodes
    if args.shortcodes:
        print(f"Fetching {len(args.shortcodes)} specific posts...")
        all_posts.extend(scrape_shortcodes(args.shortcodes, L))

    # Profile accounts
    handles = args.handles
    if not handles and not args.shortcodes:
        handles = [h.strip().lstrip("@") for h in SOURCE_ACCOUNTS_ENV.split(",") if h.strip()]

    if not handles and not args.shortcodes:
        print("No accounts or shortcodes specified.")
        print("Pass handles as args or set FIESTAS_IG_SOURCE_ACCOUNTS in .env")
        sys.exit(1)

    for handle in handles:
        print(f"Scraping @{handle}...")
        posts = scrape_profile(handle, limit=args.limit, L=L)
        all_posts.extend(posts)
        if len(handles) > 1:
            time.sleep(3)

    # Deduplicate by shortcode
    seen = set()
    unique = []
    for p in all_posts:
        if p["shortcode"] not in seen:
            seen.add(p["shortcode"])
            unique.append(p)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(unique, f, indent=2, ensure_ascii=False)

    event_total = sum(1 for p in unique if p.get("is_event"))
    print(f"\nTotal: {len(unique)} posts ({event_total} event posts) → {args.output}")


if __name__ == "__main__":
    main()
