#!/usr/bin/env python3
"""
Score inbound leads from .tmp/inbound_leads.json.

Inbound-specific scoring (max 100 pts):
  has_email        — 30 pts  (required to reply)
  has_phone        — 20 pts  (faster follow-up)
  has_website      — 15 pts  (digital-savvy prospect)
  message_length   — 10 pts  (>50 chars = thoughtful inquiry)
  niche_match      — 25 pts  (roofing or hvac = core service niches)

Tiers:
  A  >= 65   top priority (reply same day)
  B  40–64   good prospect
  C  < 40    lower priority

Usage:
    python3 tools/score_inbound_leads.py
    python3 tools/score_inbound_leads.py --tier A
    python3 tools/score_inbound_leads.py --top 10
"""

import argparse
import json
from pathlib import Path

ROOT        = Path(__file__).parent.parent
LEADS_FILE  = ROOT / ".tmp" / "inbound_leads.json"

PRIORITY_NICHES = {"roofing", "hvac"}


def score_lead(lead: dict) -> int:
    pts = 0
    pts += 30 if lead.get("email") else 0
    pts += 20 if lead.get("phone") else 0
    pts += 15 if lead.get("website") else 0
    pts += 10 if len(lead.get("message") or "") > 50 else 0
    pts += 25 if lead.get("niche") in PRIORITY_NICHES else 0
    return min(pts, 100)


def tier(score: int) -> str:
    if score >= 65:
        return "A"
    if score >= 40:
        return "B"
    return "C"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tier", choices=["A", "B", "C"], default=None, help="Filter output by tier")
    parser.add_argument("--top", type=int, default=None, help="Print top N leads")
    args = parser.parse_args()

    if not LEADS_FILE.exists():
        print(f"No leads file at {LEADS_FILE}. Run import_netlify_leads.py first.")
        return

    leads = json.loads(LEADS_FILE.read_text())

    for lead in leads:
        s = score_lead(lead)
        lead["score"] = s
        lead["tier"]  = tier(s)

    leads.sort(key=lambda l: l["score"], reverse=True)
    LEADS_FILE.write_text(json.dumps(leads, indent=2, ensure_ascii=False))

    tier_counts = {"A": 0, "B": 0, "C": 0}
    for lead in leads:
        tier_counts[lead["tier"]] += 1

    print(f"Scored {len(leads)} inbound lead(s)")
    print(f"  Tier A (>=65): {tier_counts['A']}  |  Tier B (40-64): {tier_counts['B']}  |  Tier C (<40): {tier_counts['C']}")
    print()

    filtered = leads
    if args.tier:
        filtered = [l for l in leads if l["tier"] == args.tier]
    if args.top:
        filtered = filtered[:args.top]

    label = f"Top {len(filtered)}" if args.top else f"All {len(filtered)}"
    tier_label = f" (Tier {args.tier})" if args.tier else ""
    print(f"{label}{tier_label} — ranked by score")
    print(f"{'Score':>5}  {'Tier':>4}  {'Name':<28}  {'Niche':<10}  {'Email':<30}  {'Phone'}")
    print("-" * 100)
    for lead in filtered:
        print(
            f"{lead['score']:>5}  {lead['tier']:>4}  "
            f"{(lead.get('name') or ''):<28}  "
            f"{(lead.get('niche') or ''):<10}  "
            f"{(lead.get('email') or ''):<30}  "
            f"{lead.get('phone') or ''}"
        )

    print(f"\nFile updated: {LEADS_FILE}")
    print("Next step: python3 tools/draft_inbound_leads.py")


if __name__ == "__main__":
    main()
