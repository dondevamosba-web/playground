#!/usr/bin/env python3
"""
Meta Ad Library competitor spy.

Pulls active ads for one or more competitor brands/keywords from the Meta Ad Library,
then uses Claude to summarize creative patterns: hooks, offers, tone, CTAs, formats.
Output is printed and optionally saved as a brief to .tmp/ad_spy_{slug}.md.

Requires in .env:
  META_ACCESS_TOKEN — user token with ads_read (or basic user token for Ad Library)

Usage:
  python3 tools/competitor_ad_spy.py --brand "HomeAdvisor"
  python3 tools/competitor_ad_spy.py --brand "roofing leads agency" --country US --limit 50
  python3 tools/competitor_ad_spy.py --brand "Angi,Thumbtack,HomeAdvisor"  # multiple brands
  python3 tools/competitor_ad_spy.py --brand "HVAC contractor ads" --save   # save brief to .tmp/
  python3 tools/competitor_ad_spy.py --dry-run   # print raw ads only, no Claude summary
"""
import argparse
import os
import re
import sys
from datetime import date
from pathlib import Path

import requests

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from tools.claude_call import call_claude

GRAPH_URL = "https://graph.facebook.com/v19.0"
AD_FIELDS = ",".join([
    "page_name",
    "ad_creative_bodies",
    "ad_creative_link_titles",
    "ad_creative_link_captions",
    "ad_creative_link_descriptions",
    "ad_delivery_start_time",
    "publisher_platforms",
    "impressions",
])


# ── API ───────────────────────────────────────────────────────────────────────

def fetch_ads(search_term: str, token: str, country: str, limit: int) -> list:
    params = {
        "search_terms": search_term,
        "ad_reached_countries": f'["{country}"]',
        "ad_type": "ALL",
        "fields": AD_FIELDS,
        "limit": min(limit, 200),
        "access_token": token,
    }
    ads = []
    url = f"{GRAPH_URL}/ads_archive"
    while url and len(ads) < limit:
        resp = requests.get(url, params=params, timeout=30)
        if resp.status_code != 200:
            err = resp.json().get("error", {})
            print(f"  Ad Library API error: {err.get('message', resp.text)}")
            break
        data = resp.json()
        ads.extend(data.get("data", []))
        url = data.get("paging", {}).get("next")
        params = {}
    return ads[:limit]


# ── Extraction ────────────────────────────────────────────────────────────────

def extract_text(ad: dict) -> dict:
    bodies = ad.get("ad_creative_bodies") or []
    titles = ad.get("ad_creative_link_titles") or []
    captions = ad.get("ad_creative_link_captions") or []
    descriptions = ad.get("ad_creative_link_descriptions") or []
    platforms = ad.get("publisher_platforms") or []
    impressions = ad.get("impressions") or {}

    return {
        "page": ad.get("page_name", ""),
        "body": " | ".join(bodies) if bodies else "",
        "headline": " | ".join(titles) if titles else "",
        "description": " | ".join(descriptions) if descriptions else "",
        "caption": " | ".join(captions) if captions else "",
        "platforms": ", ".join(platforms),
        "started": ad.get("ad_delivery_start_time", "")[:10],
        "impressions_lower": impressions.get("lower_bound", ""),
        "impressions_upper": impressions.get("upper_bound", ""),
    }


def format_for_claude(ads_by_brand: dict) -> str:
    lines = []
    for brand, ads in ads_by_brand.items():
        lines.append(f"\n## {brand} ({len(ads)} ads)\n")
        for i, ad in enumerate(ads[:30], 1):  # cap at 30 ads per brand for context
            body = ad["body"][:300] if ad["body"] else "(no body)"
            headline = ad["headline"][:120] if ad["headline"] else ""
            lines.append(f"{i}. [{ad['started']}] {ad['page']}")
            if headline:
                lines.append(f"   Headline: {headline}")
            lines.append(f"   Copy: {body}")
            if ad["platforms"]:
                lines.append(f"   Platforms: {ad['platforms']}")
            lines.append("")
    return "\n".join(lines)


# ── Analysis ──────────────────────────────────────────────────────────────────

def analyze(search_term: str, ads_by_brand: dict) -> str:
    total = sum(len(v) for v in ads_by_brand.values())
    ad_text = format_for_claude(ads_by_brand)

    prompt = f"""You are a senior performance marketing strategist analyzing competitor ads for the search term "{search_term}".

Here are {total} active Meta ads from competitors:
{ad_text}

Write a creative intelligence brief with these exact sections:

**1. Top Hooks (3–5 examples)**
The most common opening lines or attention-grabbing patterns. Quote specific examples.

**2. Offer Patterns**
What offers, guarantees, or value props appear most (e.g. free quotes, % off, money-back guarantee, exclusivity, urgency).

**3. Tone & Messaging**
Dominant tone (fear/urgency, social proof, educational, aspirational). What emotional levers are used.

**4. CTA Patterns**
Most common calls to action. What action they push and how.

**5. Format & Platform Mix**
Which platforms appear. Any signals about video vs image vs carousel preference.

**6. Gaps & Opportunities**
What angles are missing or underused that could differentiate a new entrant.

Keep each section to 3–5 bullet points. Be specific and actionable."""

    return call_claude(prompt, model="haiku")


# ── Main ──────────────────────────────────────────────────────────────────────

def slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--brand", required=True,
                        help="Brand name(s) or keyword to search (comma-separated for multiple)")
    parser.add_argument("--country", default="US", help="Country code (default: US)")
    parser.add_argument("--limit", type=int, default=50, help="Max ads per search term (default: 50)")
    parser.add_argument("--save", action="store_true", help="Save brief to .tmp/ad_spy_<slug>.md")
    parser.add_argument("--dry-run", action="store_true", help="Print raw ads only, skip Claude analysis")
    args = parser.parse_args()

    token = os.getenv("META_ACCESS_TOKEN")
    if not token:
        print("Missing META_ACCESS_TOKEN in .env")
        print("Get one at: https://developers.facebook.com/tools/explorer")
        sys.exit(1)

    brands = [b.strip() for b in args.brand.split(",") if b.strip()]
    ads_by_brand: dict[str, list] = {}

    for brand in brands:
        print(f"Fetching ads for: {brand}")
        raw_ads = fetch_ads(brand, token, args.country, args.limit)
        extracted = [extract_text(a) for a in raw_ads]
        ads_by_brand[brand] = extracted
        print(f"  → {len(extracted)} ads found")

    total = sum(len(v) for v in ads_by_brand.values())
    if total == 0:
        print("No ads found. Try a different search term or check your token.")
        return

    if args.dry_run:
        for brand, ads in ads_by_brand.items():
            print(f"\n{'='*60}\n{brand}\n{'='*60}")
            for ad in ads:
                print(f"\n[{ad['started']}] {ad['page']}")
                if ad["headline"]:
                    print(f"  Headline: {ad['headline'][:100]}")
                print(f"  Copy: {ad['body'][:200]}")
        return

    print(f"\nAnalyzing {total} ads with Claude...")
    brief = analyze(args.brand, ads_by_brand)
    print(f"\n{'='*60}")
    print(f"CREATIVE BRIEF — {args.brand.upper()}")
    print(f"Generated: {date.today().isoformat()}  |  Ads analyzed: {total}")
    print(f"{'='*60}\n")
    print(brief)

    if args.save:
        slug = slugify(args.brand)
        out_path = ROOT / ".tmp" / f"ad_spy_{slug}.md"
        out_path.parent.mkdir(exist_ok=True)
        content = (
            f"# Ad Spy Brief — {args.brand}\n"
            f"Generated: {date.today().isoformat()}  |  Ads analyzed: {total}  |  Country: {args.country}\n\n"
            f"{brief}\n"
        )
        out_path.write_text(content)
        print(f"\nBrief saved to: {out_path}")


if __name__ == "__main__":
    main()
