#!/usr/bin/env python3
"""
Scrape recent posts from competitor fiestas electronicas IG accounts.
Returns posts sorted by engagement (likes + comments), flagging reels vs images.

Usage:
  python3 tools/scrape_competitor_kpis.py
  python3 tools/scrape_competitor_kpis.py --limit 8 --top 10
  python3 tools/scrape_competitor_kpis.py --output .tmp/competitor_kpis.json
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

ACCOUNTS = os.getenv("FIESTAS_IG_SOURCE_ACCOUNTS", "").split(",")


def scrape_account(handle, limit, L):
    handle = handle.strip().lstrip("@")
    if not handle:
        return []
    try:
        profile = instaloader.Profile.from_username(L.context, handle)
    except Exception as e:
        print(f"  SKIP @{handle}: {e}")
        return []

    posts = []
    try:
        for i, post in enumerate(profile.get_posts()):
            if i >= limit:
                break
            media_type = "reel" if post.is_video else "image"
            posts.append({
                "account": handle,
                "shortcode": post.shortcode,
                "url": f"https://www.instagram.com/p/{post.shortcode}/",
                "date": str(post.date.date()),
                "type": media_type,
                "likes": post.likes,
                "comments": post.comments,
                "engagement": post.likes + post.comments * 3,
                "caption": (post.caption or "")[:200],
                "image_url": post.url,
                "video_url": post.video_url if post.is_video else None,
            })
            time.sleep(1.2)
    except Exception as e:
        print(f"  Error @{handle}: {e}")

    print(f"  @{handle}: {len(posts)} posts, top engagement {max((p['engagement'] for p in posts), default=0)}")
    return posts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=6, help="Posts per account to fetch")
    parser.add_argument("--top", type=int, default=15, help="Top N results to return")
    parser.add_argument("--output", default=".tmp/competitor_kpis.json")
    args = parser.parse_args()

    L = instaloader.Instaloader(
        quiet=True,
        download_pictures=False,
        download_videos=False,
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=False,
    )

    ig_user = os.getenv("INSTALOADER_USER") or os.getenv("IG_USERNAME")
    ig_pass = os.getenv("INSTALOADER_PASS") or os.getenv("IG_PASSWORD")
    if ig_user and ig_pass:
        try:
            L.login(ig_user, ig_pass)
            print(f"Logged in as @{ig_user}")
        except Exception as e:
            print(f"Login failed ({e}), continuing anonymously")

    all_posts = []
    for handle in ACCOUNTS:
        print(f"Scraping @{handle}...")
        all_posts.extend(scrape_account(handle, args.limit, L))

    all_posts.sort(key=lambda p: p["engagement"], reverse=True)
    top = all_posts[:args.top]

    out = Path(args.output)
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(top, indent=2, ensure_ascii=False))

    print(f"\nTop {len(top)} posts saved → {out}")
    print(f"\n{'#':<3} {'Type':<6} {'Likes':>6} {'Cmts':>5} {'Account':<28} {'Date':<12} URL")
    print("-" * 100)
    for i, p in enumerate(top, 1):
        print(f"{i:<3} {p['type']:<6} {p['likes']:>6} {p['comments']:>5}  @{p['account']:<26} {p['date']:<12} {p['url']}")


if __name__ == "__main__":
    main()
