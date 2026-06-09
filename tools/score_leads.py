#!/usr/bin/env python3
"""
Scores and ranks scraped leads by outreach value.

Adds `score` (0–100) and `tier` (A/B/C) to each lead, then sorts by score descending.
Writes back to the same JSON file so downstream draft tools pick up the ranked order.

Scoring signals (max 100 pts):
  Rating        — 20 pts   (higher is better, null gets a neutral 5)
  Review count  — 15 pts   (sweet spot 20–80, shows established but not giant)
  Has email     — 25 pts   (required for outreach, highest weight)
  Has phone     — 10 pts   (reachability)
  Has website   — 10 pts   (digital-savvy = easier to sell paid ads)
  FB Ads status — 20 pts   (none=20, google_only=16, fb_only=12, both=5)

Tiers:
  A  ≥ 65   top priority
  B  40–64  good prospect
  C  < 40   lower priority

Usage:
  python3 tools/score_leads.py --niche roofing      # default
  python3 tools/score_leads.py --niche hvac
  python3 tools/score_leads.py --niche roofing --top 20   # print top N only
  python3 tools/score_leads.py --niche roofing --tier A   # filter by tier
"""
import argparse
import json
import os
from pathlib import Path

ROOT = Path(__file__).parent.parent
LEAD_FILES = {
    "roofing":  ROOT / ".tmp" / "roofing_leads.json",
    "hvac":     ROOT / ".tmp" / "hvac_leads.json",
    "plumbing": ROOT / ".tmp" / "plumbing_leads.json",
    "windows":  ROOT / ".tmp" / "windows_leads.json",
}

FB_ADS_SCORE = {
    "none":        20,  # no ads running → biggest opportunity
    "google_only": 16,  # digital budget but no Meta yet
    "fb_only":     12,  # running Meta, could pitch Google
    "both":         5,  # already covered, harder sell
    "unknown":      8,  # couldn't determine, neutral
    "no_website":   0,  # no web presence, very hard sell
}


def score_rating(rating) -> int:
    if rating is None:
        return 5  # unknown, not a disqualifier
    if rating >= 5.0:
        return 20
    if rating >= 4.7:
        return 17
    if rating >= 4.5:
        return 14
    if rating >= 4.0:
        return 8
    return 0


def score_review_count(count) -> int:
    if count is None:
        return 0
    if 20 <= count <= 80:
        return 15   # sweet spot: established but not a big franchise
    if 10 <= count < 20:
        return 12
    if 80 < count <= 100:
        return 8    # bigger, less urgent need for help
    if 1 <= count < 10:
        return 5
    return 0


def score_lead(lead: dict) -> int:
    pts = 0
    pts += score_rating(lead.get("rating"))
    pts += score_review_count(lead.get("review_count"))
    pts += 25 if lead.get("email") else 0
    pts += 10 if lead.get("phone") else 0
    pts += 10 if lead.get("website") else 0
    pts += FB_ADS_SCORE.get(lead.get("fb_ads_status") or "", 0)
    return pts


def tier(score: int) -> str:
    if score >= 65:
        return "A"
    if score >= 40:
        return "B"
    return "C"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--niche", choices=["roofing", "hvac", "plumbing", "windows"], default="roofing")
    parser.add_argument("--top", type=int, default=None, help="Print top N leads")
    parser.add_argument("--tier", choices=["A", "B", "C"], default=None, help="Filter by tier")
    args = parser.parse_args()

    path = LEAD_FILES[args.niche]
    if not path.exists():
        print(f"No leads file at {path}. Run scrape_{args.niche}_gmaps.py first.")
        return

    leads = json.loads(path.read_text())

    for lead in leads:
        s = score_lead(lead)
        lead["score"] = s
        lead["tier"] = tier(s)

    leads.sort(key=lambda l: l["score"], reverse=True)
    path.write_text(json.dumps(leads, indent=2, ensure_ascii=False))

    # Summary
    tier_counts = {"A": 0, "B": 0, "C": 0}
    for lead in leads:
        tier_counts[lead["tier"]] += 1

    print(f"Scored {len(leads)} {args.niche} leads")
    print(f"  Tier A (≥65): {tier_counts['A']}  |  Tier B (40-64): {tier_counts['B']}  |  Tier C (<40): {tier_counts['C']}")
    print()

    # Print ranked list
    filtered = leads
    if args.tier:
        filtered = [l for l in leads if l["tier"] == args.tier]
    if args.top:
        filtered = filtered[:args.top]

    label = f"Top {len(filtered)}" if args.top else f"All {len(filtered)}"
    tier_label = f" (Tier {args.tier})" if args.tier else ""
    print(f"{label}{tier_label} — ranked by score")
    print(f"{'Score':>5}  {'Tier':>4}  {'Company':<35}  {'City':<18}  {'Email':<32}  FB Ads")
    print("-" * 110)
    for lead in filtered:
        print(
            f"{lead['score']:>5}  {lead['tier']:>4}  "
            f"{(lead.get('name') or ''):<35}  "
            f"{(lead.get('city') or ''):<18}  "
            f"{(lead.get('email') or ''):<32}  "
            f"{lead.get('fb_ads_status') or ''}"
        )

    print(f"\nFile updated: {path}")


if __name__ == "__main__":
    main()
