#!/usr/bin/env python3
"""Scan IG business profiles: follower count and top reels, ranked by engagement.

Reads through tools/ig_fetch.py (Graph API business_discovery) because the old
web_profile_info endpoint returns 429 for every handle since July 2026. Two
things that endpoint gave and the Graph API does not: video view counts and
related-profile suggestions. Videos are ranked by likes instead, and "related"
always comes back empty.

Usage: ig_viral_scout.py handle1 handle2 ...
Prints JSON to stdout: {handle: {followers, related: [], videos: [{shortcode, likes, comments, caption}]}}
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from tools import ig_fetch


def fetch(handle):
    return ig_fetch.fetch_account(handle)


def main():
    out = {}
    for h in sys.argv[1:]:
        try:
            acc = fetch(h)
        except ig_fetch.IGFetchError as e:
            out[h] = {"error": str(e)}
            continue
        videos = [{
            "shortcode": p["shortcode"],
            "likes":     p["likes"],
            "comments":  p["comments"],
            "caption":   p["caption"][:80].replace("\n", " "),
        } for p in acc["posts"] if p["is_video"]]
        videos.sort(key=lambda v: v["likes"] + 3 * v["comments"], reverse=True)
        out[h] = {
            "followers": acc["followers"],
            "related": [],  # not exposed by business_discovery
            "videos": videos,
        }
        time.sleep(1)
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
