#!/usr/bin/env python3
"""
Shared helpers for organic Instagram/Facebook stats (followers, recent posts)
and day-by-day growth history across the 4 business accounts (ola, storm,
fiestas, techno — same accounts as tools/post_instagram.py ACCOUNT_CONFIG).

Not a CLI on its own — used by tools/snapshot_social_stats.py and
tools/social_dashboard_server.py.

Requires in .env:
  INSTAGRAM_ACCESS_TOKEN
  INSTAGRAM_BUSINESS_ACCOUNT_ID / STORM_INSTAGRAM_BUSINESS_ACCOUNT_ID /
  FIESTAS_INSTAGRAM_BUSINESS_ACCOUNT_ID / TECHNO_INSTAGRAM_BUSINESS_ACCOUNT_ID
"""

import json
import os
import sys
from datetime import date, timedelta
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")

from tools.post_instagram import ACCOUNT_CONFIG

ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
GRAPH = "https://graph.facebook.com/v21.0"
HISTORY_FILE = ROOT / ".tmp" / "social_stats_history.jsonl"

DISPLAY_NAMES = {
    "ola": "Ola Digital",
    "storm": "Storm",
    "fiestas": "Fiestas",
    "techno": "Techno",
    "empleo": "Ola Empleo",
    "talento": "Talento USA",
}


def graph_get(path: str, params: dict) -> dict:
    params = {**params, "access_token": ACCESS_TOKEN}
    r = requests.get(f"{GRAPH}{path}", params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def fetch_account_stats(account: str) -> dict | None:
    """Live followers/media count for one account. None if not configured."""
    ig_id = os.getenv(ACCOUNT_CONFIG[account]["ig_id_key"])
    if not ig_id or not ACCESS_TOKEN:
        return None
    data = graph_get(f"/{ig_id}", {"fields": "username,followers_count,media_count,profile_picture_url"})
    return {
        "account": account,
        "ig_id": ig_id,
        "username": data.get("username"),
        "followers_count": data.get("followers_count"),
        "media_count": data.get("media_count"),
        "profile_picture_url": data.get("profile_picture_url"),
    }


def fetch_recent_media(account: str, limit: int = 6) -> list[dict]:
    ig_id = os.getenv(ACCOUNT_CONFIG[account]["ig_id_key"])
    if not ig_id or not ACCESS_TOKEN:
        return []
    data = graph_get(f"/{ig_id}/media", {
        "fields": "caption,media_type,media_url,thumbnail_url,permalink,timestamp,like_count,comments_count",
        "limit": limit,
    })
    return data.get("data", [])


def load_history() -> list[dict]:
    if not HISTORY_FILE.exists():
        return []
    lines = HISTORY_FILE.read_text(encoding="utf-8").splitlines()
    return [json.loads(l) for l in lines if l.strip()]


def record_snapshot(stats: dict) -> None:
    """Upsert today's followers/media snapshot for one account."""
    if not stats or stats.get("followers_count") is None:
        return
    today = date.today().isoformat()
    history = [
        h for h in load_history()
        if not (h["date"] == today and h["account"] == stats["account"])
    ]
    history.append({
        "date": today,
        "account": stats["account"],
        "followers_count": stats["followers_count"],
        "media_count": stats["media_count"],
    })
    HISTORY_FILE.parent.mkdir(exist_ok=True)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        for h in sorted(history, key=lambda h: (h["account"], h["date"])):
            f.write(json.dumps(h) + "\n")


def account_history(account: str) -> list[dict]:
    return sorted(
        (h for h in load_history() if h["account"] == account),
        key=lambda h: h["date"],
    )


def compute_growth(account: str) -> dict:
    """Follower deltas vs the closest snapshot at/before N days ago."""
    history = account_history(account)
    if not history:
        return {"1d": None, "7d": None, "30d": None}
    latest = history[-1]
    today = date.fromisoformat(latest["date"])
    result = {}
    for label, days in (("1d", 1), ("7d", 7), ("30d", 30)):
        target = today - timedelta(days=days)
        candidates = [h for h in history if date.fromisoformat(h["date"]) <= target]
        result[label] = (latest["followers_count"] - candidates[-1]["followers_count"]) if candidates else None
    return result
