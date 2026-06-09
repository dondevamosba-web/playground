"""
Prospect research and scoring tool.

For each lead, collects signals and produces a priority_score (0–100)
to rank who to contact first.

Signals checked:
  - fb_ads_status (pixel presence on website)
  - website quality (exists, HTTPS, loads fast)
  - review score and count (high rating + low count = quality small biz)
  - social presence (Facebook/Instagram links on site)
  - contact info completeness (email + phone)

Score breakdown:
  - No pixels at all (none): +30
  - Has website: +15
  - Website loads (not broken): +10
  - Rating 4.0–4.9: +15 | 5.0 or <4.0: +5
  - Review count 10–50 (sweet spot): +10 | 51–100: +5
  - Has email: +10
  - Has phone: +5
  - No social links on site (not already doing social marketing): +5

Usage:
  python3 tools/research_leads.py --input .tmp/landscaping_leads.json
  python3 tools/research_leads.py --input .tmp/roofing_leads.json --limit 50
  python3 tools/research_leads.py --input .tmp/dental_leads.json --top 20
"""

import argparse
import json
import os
import random
import re
import ssl
import time
import urllib.request
import urllib.error

SOCIAL_SIGNALS = ["facebook.com/", "instagram.com/", "twitter.com/", "linkedin.com/"]


def fetch_html(url: str, timeout: int = 10) -> str | None:
    if not url:
        return None
    if not url.startswith("http"):
        url = "https://" + url
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; research-bot/1.0)"},
        )
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            return resp.read(100_000).decode("utf-8", errors="ignore")
    except Exception:
        return None


def score_lead(lead: dict, html: str | None) -> tuple[int, dict]:
    breakdown = {}
    score = 0

    # Ad pixel status
    status = lead.get("fb_ads_status")
    if status == "none":
        score += 30
        breakdown["no_pixels"] = 30
    elif status in ("fb_only", "google_only"):
        score += 10
        breakdown["partial_pixels"] = 10
    elif status == "both":
        score += 0
        breakdown["full_pixels"] = 0
    elif status is None:
        score += 15
        breakdown["status_unknown"] = 15

    # Website exists
    if lead.get("website"):
        score += 15
        breakdown["has_website"] = 15
    else:
        return score, breakdown  # can't check further without website

    # Website loads
    if html is not None:
        score += 10
        breakdown["website_loads"] = 10
    else:
        return score, breakdown

    # Social links on site
    has_social = any(sig in html for sig in SOCIAL_SIGNALS)
    if not has_social:
        score += 5
        breakdown["no_social_marketing"] = 5

    # Review rating
    rating = lead.get("rating")
    if rating:
        if 4.0 <= rating < 5.0:
            score += 15
            breakdown["good_rating"] = 15
        elif rating == 5.0:
            score += 8
            breakdown["perfect_rating"] = 8
        else:
            score += 5
            breakdown["low_rating"] = 5

    # Review count (sweet spot: established but small)
    count = lead.get("review_count")
    if count:
        if 10 <= count <= 50:
            score += 10
            breakdown["sweet_spot_reviews"] = 10
        elif 51 <= count <= 100:
            score += 5
            breakdown["moderate_reviews"] = 5

    # Contact info
    if lead.get("email"):
        score += 10
        breakdown["has_email"] = 10
    if lead.get("phone"):
        score += 5
        breakdown["has_phone"] = 5

    return score, breakdown


def classify_priority(score: int) -> str:
    if score >= 70:
        return "HOT"
    if score >= 45:
        return "WARM"
    return "COLD"


def research_lead(lead: dict) -> dict:
    html = fetch_html(lead.get("website"))
    score, breakdown = score_lead(lead, html)
    lead["priority_score"] = score
    lead["priority"] = classify_priority(score)
    lead["score_breakdown"] = breakdown
    return lead


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to leads JSON")
    parser.add_argument("--limit", type=int, default=None, help="Max leads to research")
    parser.add_argument("--top", type=int, default=None, help="Print top N leads after scoring")
    parser.add_argument("--force", action="store_true", help="Re-research already-scored leads")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"File not found: {args.input}")
        return

    with open(args.input) as f:
        leads = json.load(f)

    to_process = leads if args.force else [l for l in leads if l.get("priority_score") is None]
    if args.limit:
        to_process = to_process[: args.limit]

    print(f"Researching {len(to_process)} leads from {args.input}...")

    for i, lead in enumerate(to_process):
        score, _ = 0, {}
        lead = research_lead(lead)
        # Update in original list
        for j, orig in enumerate(leads):
            if orig.get("name") == lead.get("name") and orig.get("city") == lead.get("city"):
                leads[j] = lead
                break
        print(f"  [{i+1}/{len(to_process)}] {lead['name'][:40]:<40} "
              f"score={lead['priority_score']:>3}  {lead['priority']}")
        time.sleep(random.uniform(0.5, 1.2))

    with open(args.input, "w") as f:
        json.dump(leads, f, indent=2, ensure_ascii=False)

    print(f"\nSaved → {args.input}")

    # Summary
    hot = [l for l in leads if l.get("priority") == "HOT"]
    warm = [l for l in leads if l.get("priority") == "WARM"]
    cold = [l for l in leads if l.get("priority") == "COLD"]
    print(f"\nPriority breakdown:")
    print(f"  HOT  🔥 : {len(hot)}")
    print(f"  WARM    : {len(warm)}")
    print(f"  COLD    : {len(cold)}")

    if args.top:
        ranked = sorted([l for l in leads if l.get("priority_score") is not None],
                        key=lambda x: x["priority_score"], reverse=True)
        print(f"\nTop {args.top} leads:")
        for l in ranked[: args.top]:
            print(f"  {l['priority_score']:>3}  {l['priority']:<4}  {l['name'][:35]:<35}  {l.get('city','')}")


if __name__ == "__main__":
    main()
