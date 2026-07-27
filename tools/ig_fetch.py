#!/usr/bin/env python3
"""
Read other accounts' Instagram posts through the Graph API.

Instagram's unofficial `web_profile_info` endpoint started returning 429 for every
handle in July 2026. Everything that used to read it goes through here instead,
using Graph API `business_discovery`, which is authenticated and not rate-limited
the same way.

Two entry points:

  fetch_account(handle)  → clean dict, use this in new code
  fetch_user(handle)     → same data reshaped to look like the old web_profile_info
                           payload, so existing callers need a one-line change

Limits worth knowing:
  - business_discovery only reaches **business and creator** accounts. A personal
    account raises IGFetchError instead of returning posts.
  - Video view counts and related-profile suggestions are not exposed. Rank by
    likes and comments instead.
"""
import os
import sys
from datetime import datetime
from pathlib import Path

import requests

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

GRAPH = "https://graph.facebook.com/v21.0"

MEDIA_FIELDS = ("media_type,media_product_type,caption,permalink,timestamp,"
                "like_count,comments_count,media_url,thumbnail_url,"
                "children{media_url,media_type}")


class IGFetchError(RuntimeError):
    """business_discovery refused the handle — usually a personal account."""


def _credentials() -> tuple[str, str]:
    try:
        return (os.environ["INSTAGRAM_ACCESS_TOKEN"],
                os.environ["FIESTAS_INSTAGRAM_BUSINESS_ACCOUNT_ID"])
    except KeyError as e:
        raise IGFetchError(f"falta {e.args[0]} en .env") from e


def _best_image(m: dict) -> str:
    """First real still: opening image of a carousel, else media or thumbnail."""
    if m.get("media_type") == "CAROUSEL_ALBUM":
        for kid in m.get("children", {}).get("data", []):
            if kid.get("media_type") == "IMAGE" and kid.get("media_url"):
                return kid["media_url"]
    if m.get("media_type") == "VIDEO":
        return m.get("thumbnail_url", "")
    return m.get("media_url") or m.get("thumbnail_url") or ""


def fetch_account(handle: str, limit: int = 25) -> dict:
    """Return {handle, followers, media_count, posts:[...]} for a business account."""
    token, ig_id = _credentials()
    handle = handle.lstrip("@")
    fields = (f"business_discovery.username({handle})"
              f"{{followers_count,media_count,media.limit({limit}){{{MEDIA_FIELDS}}}}}")
    try:
        r = requests.get(f"{GRAPH}/{ig_id}", params={"fields": fields,
                                                    "access_token": token},
                         timeout=30).json()
    except requests.RequestException as e:
        raise IGFetchError(f"@{handle}: {e}") from e

    if "error" in r:
        raise IGFetchError(f"@{handle}: {r['error'].get('message', '')[:160]}")

    bd = r.get("business_discovery", {})
    posts = []
    for m in bd.get("media", {}).get("data", []):
        is_video = m.get("media_type") == "VIDEO"
        posts.append({
            "shortcode":  m["permalink"].rstrip("/").split("/")[-1],
            "permalink":  m["permalink"],
            "caption":    m.get("caption") or "",
            "timestamp":  m["timestamp"],
            "date":       m["timestamp"][:10],
            "media_type": m.get("media_type", ""),
            "is_video":   is_video,
            "is_reel":    m.get("media_product_type") == "REELS",
            "likes":      m.get("like_count", 0),
            "comments":   m.get("comments_count", 0),
            "image_url":  _best_image(m),
        })
    return {
        "handle":      handle,
        "followers":   bd.get("followers_count", 0),
        "media_count": bd.get("media_count", 0),
        "posts":       posts,
    }


def fetch_user(handle: str, limit: int = 25) -> dict:
    """Legacy shim: `fetch_account` reshaped like the old web_profile_info user dict.

    Only the keys the existing callers actually read are populated. Anything the
    Graph API does not expose — video_view_count, edge_related_profiles — comes
    back as zero or empty rather than missing, so callers keep working.
    """
    acc = fetch_account(handle, limit)
    edges = []
    for p in acc["posts"]:
        ts = int(datetime.fromisoformat(p["timestamp"].replace("+0000", "+00:00")).timestamp())
        edges.append({"node": {
            "shortcode":               p["shortcode"],
            "display_url":             p["image_url"],
            "thumbnail_resources":     [],
            "is_video":                p["is_video"],
            "video_view_count":        0,
            "taken_at_timestamp":      ts,
            "edge_liked_by":           {"count": p["likes"]},
            "edge_media_to_comment":   {"count": p["comments"]},
            "edge_media_to_caption":   {"edges": ([{"node": {"text": p["caption"]}}]
                                                  if p["caption"] else [])},
        }})
    return {
        "username":                    acc["handle"],
        "edge_followed_by":            {"count": acc["followers"]},
        "edge_owner_to_timeline_media": {"edges": edges},
        "edge_related_profiles":       {"edges": []},
    }


if __name__ == "__main__":
    for h in sys.argv[1:] or ["crobarclub"]:
        try:
            a = fetch_account(h)
        except IGFetchError as e:
            print(f"ERROR {e}")
            continue
        print(f"@{a['handle']} — {a['followers']:,} seguidores — {len(a['posts'])} posts")
        for p in a["posts"][:5]:
            kind = "reel" if p["is_reel"] else p["media_type"].lower()
            print(f"  [{p['date']}] {kind:14} {p['likes']:>6} likes  "
                  f"{p['caption'].splitlines()[0][:60] if p['caption'] else ''}")
