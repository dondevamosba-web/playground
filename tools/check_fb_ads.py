"""
Checks each roofing lead's website for Facebook Pixel and Google Ads tags.
This is more reliable than the Ad Library — a pixel means they've set up tracking,
which strongly correlates with running paid ads.

Classifies as:
  - "none"      : no FB pixel, no Google Ads tag → hottest lead (Variant A DM)
  - "fb_only"   : FB pixel only → pitch Google Ads
  - "google_only": Google Ads tag only → pitch Facebook Ads
  - "both"      : both present → pitch better results / lower CPL
  - "no_website": no website to check → skip or manual outreach
  - "unknown"   : website unreachable

Updates .tmp/roofing_leads.json in-place with fb_ads_status field.

Usage:
  python3 tools/check_fb_ads.py
  python3 tools/check_fb_ads.py --limit 30
"""

import argparse
import json
import os
import random
import time
import urllib.request
import urllib.error
import ssl

DEFAULT_LEADS_PATH = os.path.join(os.path.dirname(__file__), "..", ".tmp", "roofing_leads.json")

FB_PIXEL_SIGNALS = [
    "fbq(", "facebook.com/tr?", "connect.facebook.net",
    "facebook-jssdk", "_fbp", "fbevents.js",
]

GOOGLE_ADS_SIGNALS = [
    "gtag(", "google_conversion", "googleadservices.com",
    "googletag.cmd", "AW-",  # Google Ads conversion ID prefix
]


def check_website(url: str) -> str:
    if not url:
        return "no_website"

    # Normalize URL
    if not url.startswith("http"):
        url = "https://" + url

    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; bot/1.0)"},
        )
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            # Read first 150KB — pixels are always in the <head>
            html = resp.read(150_000).decode("utf-8", errors="ignore")
    except Exception:
        return "unknown"

    has_fb = any(sig in html for sig in FB_PIXEL_SIGNALS)
    has_google = any(sig in html for sig in GOOGLE_ADS_SIGNALS)

    if has_fb and has_google:
        return "both"
    if has_fb:
        return "fb_only"
    if has_google:
        return "google_only"
    return "none"


def load_leads(path: str) -> list[dict]:
    if not os.path.exists(path):
        print(f"No leads file found at {path}")
        return []
    with open(path) as f:
        return json.load(f)


def save_leads(leads: list[dict], path: str):
    with open(path, "w") as f:
        json.dump(leads, f, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--input", default=None, help="Path to leads JSON (default: roofing_leads.json)")
    args = parser.parse_args()

    leads_path = args.input if args.input else DEFAULT_LEADS_PATH
    leads = load_leads(leads_path)
    if not leads:
        return

    unprocessed = [l for l in leads if l.get("fb_ads_status") is None]
    if args.limit:
        unprocessed = unprocessed[: args.limit]

    print(f"Checking {len(unprocessed)} leads for ad pixels...")
    stats: dict[str, int] = {}

    for i, lead in enumerate(unprocessed):
        status = check_website(lead.get("website"))
        lead["fb_ads_status"] = status
        stats[status] = stats.get(status, 0) + 1
        print(f"  [{i+1}/{len(unprocessed)}] {lead['name'][:40]:<40} → {status}")

        if (i + 1) % 10 == 0:
            save_leads(leads, leads_path)

        time.sleep(random.uniform(0.5, 1.5))

    save_leads(leads, leads_path)

    print(f"\nResults:")
    for k, v in sorted(stats.items(), key=lambda x: -x[1]):
        print(f"  {k:<15}: {v}")

    hot = sum(1 for l in leads if l.get("fb_ads_status") == "none" and l.get("phone"))
    print(f"\nHot leads (no pixels, has phone): {hot}")
    print(f"Saved to {leads_path}")


if __name__ == "__main__":
    main()
