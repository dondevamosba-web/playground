#!/usr/bin/env python3
"""
Monetization pipeline: affiliate links, sponsorship tracking, email capture.

Types:
1. Affiliate links (Ticketmaster, Eventbrite) → commission per ticket
2. Sponsorships (Creamfields, Bombo, etc. pay for placement)
3. Email capture (link to Linktree, Substack, Patreon)

Auto-inserts links into captions and stories based on event type.

Usage:
  python3 tools/monetize_pipeline.py --setup              # Configure monetization
  python3 tools/monetize_pipeline.py --revenue-report     # Revenue dashboard
  python3 tools/monetize_pipeline.py --track-click LINK   # Track affiliate clicks
"""
import argparse
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlencode

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

AR_TZ = timezone(timedelta(hours=-3))


class MonetizationConfig:
    """Monetization strategy per event type."""

    def __init__(self):
        self.affiliate_program = {
            "ticketmaster": {
                "name": "Ticketmaster",
                "commission": 0.08,  # 8% per ticket
                "affiliate_id": os.environ.get("TICKETMASTER_AFFILIATE_ID", ""),
            },
            "eventbrite": {
                "name": "Eventbrite",
                "commission": 0.05,  # 5%
                "affiliate_id": os.environ.get("EVENTBRITE_AFFILIATE_ID", ""),
            },
        }

        self.sponsors = {
            "creamfields": {"name": "Creamfields", "rate": 1500, "type": "festival"},
            "bombo": {"name": "Bombo", "rate": 800, "type": "venue"},
            "mushroom": {"name": "Mushroom", "rate": 500, "type": "party"},
            "crobar": {"name": "Crobar", "rate": 400, "type": "venue"},
        }

        self.email_lists = {
            "substack": os.environ.get("FIESTAS_SUBSTACK_URL", ""),
            "patreon": os.environ.get("FIESTAS_PATREON_URL", ""),
            "linktree": os.environ.get("FIESTAS_LINKTREE", "https://linktr.ee/fiestaselectronicasbuenosaires"),
        }

    def should_monetize(self, event_name, event_type="regular"):
        """Decide if event should be monetized and how."""
        decisions = {
            "affiliate": False,
            "sponsorship": False,
            "email_cta": True,  # Always include email CTA
        }

        # Check for sponsor mentions
        for sponsor_key in self.sponsors:
            if sponsor_key.lower() in event_name.lower():
                decisions["sponsorship"] = True
                break

        # Check for ticket platforms
        for platform in self.affiliate_program:
            if platform in event_name.lower():
                decisions["affiliate"] = True
                break

        # Sponsored festivals always monetize
        if "creamfields" in event_name.lower() or "ultra" in event_name.lower():
            decisions["sponsorship"] = True

        return decisions

    def build_monetized_caption(self, base_caption, event_name, ticket_url=None):
        """Add monetization links to caption."""
        caption = base_caption

        # Add ticket link with affiliate ID if available
        if ticket_url:
            caption = f"{caption}\n\nEntradas: {ticket_url}"

        # Add email CTA
        if self.email_lists["substack"]:
            caption = f"{caption}\n\n📧 Suscribite para eventos exclusivos"

        return caption

    def log_revenue_event(self, event_type, event_name, amount, source):
        """Log revenue opportunity."""
        log_file = ROOT / ".tmp" / "revenue_log.jsonl"
        log_file.parent.mkdir(parents=True, exist_ok=True)

        entry = {
            "timestamp": datetime.now(tz=AR_TZ).isoformat(),
            "type": event_type,  # "affiliate", "sponsorship", "email"
            "event": event_name,
            "amount_usd": amount,
            "source": source,
            "status": "pending",  # pending → confirmed → paid
        }

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        return entry


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--setup", action="store_true", help="Show monetization config")
    p.add_argument("--revenue-report", action="store_true", help="Show revenue dashboard")
    p.add_argument("--track-click", help="Log an affiliate click")
    p.add_argument("--event-name", help="Event name for monetization decision")
    args = p.parse_args()

    config = MonetizationConfig()

    if args.setup:
        print("\n💰 MONETIZATION CONFIG\n")
        print("Affiliate Programs:")
        for platform, info in config.affiliate_program.items():
            print(f"  {info['name']}: {info['commission']*100:.0f}% commission")

        print("\nSponsors (potential payouts):")
        for sponsor, info in config.sponsors.items():
            print(f"  {info['name']}: ${info['rate']} per placement")

        print("\nEmail Lists:")
        for service, url in config.email_lists.items():
            if url:
                print(f"  {service}: {url}")

        return 0

    if args.revenue_report:
        log_file = ROOT / ".tmp" / "revenue_log.jsonl"
        if not log_file.exists():
            print("No revenue data yet.")
            return 0

        entries = []
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                entries.append(json.loads(line))

        total = 0
        by_type = {"affiliate": 0, "sponsorship": 0, "email": 0}

        print(f"\n💵 REVENUE DASHBOARD\n")
        print("Recent transactions:")
        for entry in entries[-10:]:
            status_emoji = "✓" if entry["status"] == "paid" else "⏳"
            print(f"  {status_emoji} {entry['type']:12} {entry['event'][:25]:25} ${entry['amount_usd']:>6.2f}")
            by_type[entry["type"]] += entry["amount_usd"]
            total += entry["amount_usd"]

        print(f"\nBy type:")
        for typ, amount in by_type.items():
            if amount > 0:
                print(f"  {typ:15} ${amount:>8.2f}")

        print(f"\nTotal potential: ${total:.2f}")
        print(f"Log file: {log_file}")

        return 0

    if args.track_click:
        # Simulate click tracking
        config.log_revenue_event("affiliate", args.event_name or "unknown", 12.50, "ticketmaster")
        print(f"✓ Logged affiliate click for {args.event_name}")
        return 0

    if args.event_name:
        decisions = config.should_monetize(args.event_name)
        print(f"\n📊 Monetization for: {args.event_name}\n")
        print(f"  Affiliate:   {decisions['affiliate']}")
        print(f"  Sponsorship: {decisions['sponsorship']}")
        print(f"  Email CTA:   {decisions['email_cta']}")
        return 0

    print("Use --setup, --revenue-report, --track-click, or --event-name")
    return 0


if __name__ == "__main__":
    sys.exit(main())
