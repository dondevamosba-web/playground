#!/usr/bin/env python3
"""
Create Gmail reply-template drafts for inbound leads (Tier A and B by default).

Reads .tmp/inbound_leads.json, skips already-drafted leads (tracked in
.tmp/inbound_drafted_ids.json), and creates one draft per new lead.

Usage:
    python3 tools/draft_inbound_leads.py
    python3 tools/draft_inbound_leads.py --tier A
    python3 tools/draft_inbound_leads.py --dry-run
"""

import argparse
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT         = Path(__file__).parent.parent
LEADS_FILE   = ROOT / ".tmp" / "inbound_leads.json"
DRAFTED_IDS  = ROOT / ".tmp" / "inbound_drafted_ids.json"

load_dotenv(ROOT / ".env")

DRAFT_TO     = "dondevamosba@gmail.com"
BOOKING_LINK = "https://cal.com/guido-carminatti-wvudqi/15min"

sys.path.insert(0, str(ROOT / "tools"))
from gmail_draft import create_draft, build_html_body

NICHE_LABELS = {
    "roofing":  "roofing",
    "hvac":     "HVAC",
    "plumbing": "plumbing",
    "windows":  "window replacement",
    "siding":   "siding",
    "unknown":  "home services",
}


def load_json(path, default):
    p = Path(path)
    return json.loads(p.read_text()) if p.exists() else default


def save_json(path, data):
    Path(path).parent.mkdir(exist_ok=True)
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False))


def build_reply_body(lead: dict) -> str:
    name         = lead.get("name") or "there"
    first_name   = name.split()[0] if name and name != "there" else name
    niche_label  = NICHE_LABELS.get(lead.get("niche", "unknown"), "home services")
    city         = lead.get("city") or ""
    city_line    = f" in {city}" if city else ""

    body = (
        f"Hey {first_name},\n\n"
        f"Thanks for reaching out — really appreciate you taking the time.\n\n"
        f"I saw your inquiry about our {niche_label} lead generation service{city_line}. "
        f"I'd love to connect and learn more about your business so I can show you exactly "
        f"how we'd approach your market.\n\n"
        f"The fastest way to move forward is a quick 15-minute call — no pitch, just a "
        f"conversation to see if there's a fit:\n\n"
        f"{BOOKING_LINK}\n\n"
        f"If that link doesn't work for your schedule, just reply with a few times that do "
        f"and I'll make it happen.\n\n"
        f"Talk soon,"
    )
    return body


def subject_for(lead: dict) -> str:
    niche_label = NICHE_LABELS.get(lead.get("niche", "unknown"), "home services")
    name = lead.get("name") or ""
    first_name = name.split()[0] if name else ""
    if first_name:
        return f"Re: your {niche_label} inquiry, {first_name}"
    return f"Re: your {niche_label} inquiry"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tier", default="A,B", help="Comma-separated tiers to draft (default: A,B)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    tiers = {t.strip().upper() for t in args.tier.split(",")}

    if not LEADS_FILE.exists():
        print(f"No leads file at {LEADS_FILE}. Run import_netlify_leads.py first.")
        sys.exit(1)

    leads        = load_json(LEADS_FILE, [])
    drafted_ids  = set(load_json(DRAFTED_IDS, []))

    candidates = [
        l for l in leads
        if l.get("tier") in tiers and l.get("id") not in drafted_ids
    ]

    print(f"Leads loaded: {len(leads)} total, {len(candidates)} new candidate(s) for tiers {tiers}")

    if not candidates:
        print("Nothing to draft.")
        return

    drafted_count = 0

    for lead in candidates:
        lead_id  = lead.get("id") or lead.get("email") or str(leads.index(lead))
        subject  = subject_for(lead)
        plain    = build_reply_body(lead)
        html     = build_html_body(plain)

        print(f"  Draft: [{lead.get('tier')}] {lead.get('name') or '(no name)'} | {lead.get('email') or '(no email)'}")
        print(f"    Subject: {subject}")

        if args.dry_run:
            print("    [dry-run] Skipped.")
            continue

        try:
            result = create_draft(to=DRAFT_TO, subject=subject, body=html, html=True)
            drafted_ids.add(lead_id)
            drafted_count += 1
            print(f"    Draft created: {result['draft_id']}")
        except Exception as e:
            print(f"    ERROR creating draft: {e}")

    if args.dry_run:
        print(f"\n[dry-run] Would have created {len(candidates)} draft(s). No files written.")
        return

    save_json(DRAFTED_IDS, sorted(drafted_ids))
    print(f"\nCreated {drafted_count} draft(s) → check dondevamosba@gmail.com")


if __name__ == "__main__":
    main()
