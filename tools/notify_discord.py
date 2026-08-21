#!/usr/bin/env python3
"""
Send a Discord notification when an IG post publishes (or would, in --dry-run).
Reads DISCORD_WEBHOOK_URL from .env. Never raises — a notification failure
must never break a real publish run.

Usage (CLI):
  python3 tools/notify_discord.py --account techno --caption "..." --image-url "..." \
      --hashtags "#foo #bar" --status posted --post-id 123456

Usage (import):
  from tools.notify_discord import notify
  notify(account="techno", caption=caption, image_url=media_url,
         hashtags=hashtags, status="posted", post_id=post_id)
"""

import argparse
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")

STATUS_COLOR = {
    "posted": 0x3FB950,     # green
    "dry-run": 0x667EEA,    # blue/purple
    "error": 0xE24B4A,      # red
}
STATUS_LABEL = {
    "posted": "✅ Published",
    "dry-run": "🧪 Dry-run (not actually posted)",
    "error": "❌ Failed to publish",
}


def notify(
    account: str,
    caption: str,
    image_url: str = "",
    hashtags: str = "",
    status: str = "posted",
    post_id: str = None,
) -> bool:
    """
    Send a Discord embed for a publish event. Returns True/False, never raises.
    Silently no-ops if DISCORD_WEBHOOK_URL isn't configured.
    """
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        return False

    # Discord rejects embeds whose image.url isn't an absolute http(s) URL —
    # local file paths (unresolved media) would otherwise 400 the whole request.
    if image_url and not image_url.startswith(("http://", "https://")):
        image_url = ""

    try:
        fields = [
            {"name": "Status", "value": STATUS_LABEL.get(status, status), "inline": True},
        ]
        if post_id:
            fields.append({"name": "Post ID", "value": f"`{post_id}`", "inline": True})
        if hashtags:
            fields.append({"name": "Hashtags", "value": hashtags[:1024], "inline": False})

        payload = {
            "embeds": [{
                "title": f"📸 {account}",
                "description": caption[:2000] if caption else "(no caption)",
                "color": STATUS_COLOR.get(status, 0x8B949E),
                "image": {"url": image_url} if image_url else None,
                "fields": fields,
            }]
        }

        response = requests.post(webhook_url, json=payload, timeout=5)
        if response.status_code not in (200, 204):
            print(f"    (notify_discord: Discord rejected it — {response.status_code} {response.text[:200]})", file=sys.stderr)
            return False
        return True

    except Exception as e:
        print(f"    (notify_discord: failed — {e})", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--account", required=True)
    parser.add_argument("--caption", required=True)
    parser.add_argument("--image-url", default="")
    parser.add_argument("--hashtags", default="")
    parser.add_argument("--status", default="posted", choices=["posted", "dry-run", "error"])
    parser.add_argument("--post-id", default=None)
    args = parser.parse_args()

    ok = notify(
        account=args.account,
        caption=args.caption,
        image_url=args.image_url,
        hashtags=args.hashtags,
        status=args.status,
        post_id=args.post_id,
    )
    print("Sent" if ok else "Not sent (check DISCORD_WEBHOOK_URL in .env)")


if __name__ == "__main__":
    main()
