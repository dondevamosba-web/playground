#!/usr/bin/env python3
"""
Weekly competitor digest: pulls each watched account's last 12 posts (Graph API
business_discovery, via tools/ig_fetch.py), ranks by engagement, writes a digest.

Only reaches business and creator accounts. A personal account in the watchlist
shows up as an ERROR line in the digest instead of silently vanishing.

Watchlists per niche live in tools/competitor_watchlist.json — edit freely.

Usage:
  python3 tools/competitor_watcher.py                  # all niches
  python3 tools/competitor_watcher.py --niche fiestas
Output: .tmp/competitor_digest_<date>.md
"""
import argparse
import json
import sys
import time
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
WATCHLIST = ROOT / "tools" / "competitor_watchlist.json"
HDRS = {
    "x-ig-app-id": "936619743392459",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125 Safari/537.36",
}


def fetch(handle):
    # web_profile_info returns 429 for every handle since July 2026; ig_fetch
    # serves the same shape from the Graph API. See tools/ig_fetch.py.
    from tools import ig_fetch
    return ig_fetch.fetch_user(handle)


def post_row(node):
    cap = node["edge_media_to_caption"]["edges"]
    return {
        "likes": node["edge_liked_by"]["count"],
        "comments": node["edge_media_to_comment"]["count"],
        "caption": (cap[0]["node"]["text"].replace("\n", " ")[:80] if cap else ""),
        "url": f"https://www.instagram.com/p/{node['shortcode']}/",
        "date": datetime.fromtimestamp(node["taken_at_timestamp"]).date().isoformat(),
        "video": node.get("is_video", False),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--niche")
    a = ap.parse_args()
    watch = json.loads(WATCHLIST.read_text())
    niches = {a.niche: watch[a.niche]} if a.niche else watch

    lines = [f"# Competitor digest — {date.today()}\n"]
    for niche, handles in niches.items():
        lines.append(f"\n## {niche}\n")
        for h in handles:
            try:
                u = fetch(h)
            except Exception as e:
                lines.append(f"### @{h} — ERROR: {e}\n")
                continue
            followers = u["edge_followed_by"]["count"]
            posts = [post_row(p["node"]) for p in u["edge_owner_to_timeline_media"]["edges"]]
            posts.sort(key=lambda p: p["likes"] + 3 * p["comments"], reverse=True)
            lines.append(f"### @{h} — {followers:,} followers, {len(posts)} posts recientes\n")
            for p in posts[:3]:
                kind = "🎬" if p["video"] else "🖼"
                lines.append(f"- {kind} {p['date']} · {p['likes']:,} likes / {p['comments']} com — {p['caption']} ({p['url']})")
            lines.append("")
            time.sleep(2)

    out = ROOT / ".tmp" / f"competitor_digest_{date.today():%Y%m%d}.md"
    out.write_text("\n".join(lines))
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
