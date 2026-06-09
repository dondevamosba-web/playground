"""
Generates personalized cold-outreach Gmail drafts for any local service vertical.

Reads from .tmp/{vertical}_leads.json, picks leads with email addresses,
and creates HTML drafts in Gmail.

Usage:
  python3 tools/generate_outreach_drafts.py --vertical landscaping
  python3 tools/generate_outreach_drafts.py --vertical dental --limit 10
  python3 tools/generate_outreach_drafts.py --vertical plumbing --rebuild
"""

import json
import os
import sys
import time
import argparse

sys.path.insert(0, os.path.dirname(__file__))
from gmail_draft import create_draft, build_html_body, _get_service

TMP_DIR = os.path.join(os.path.dirname(__file__), "..", ".tmp")

CAL_LINK = "https://cal.com/guido-carminatti-wvudqi/15min"

# Per-vertical templates keyed by fb_ads_status: never | inactive | active
VERTICAL_TEMPLATES = {
    "landscaping": {
        "service": "landscaping",
        "never": (
            "Quick question about your landscaping leads in {city}",
            "Hey {name},\n\n"
            "Found {company} on Google — noticed you don't have any ads running. "
            "Most landscaping companies in {city} are picking up residential jobs through Meta right now "
            "while competitors stay stuck on yard signs and referrals.\n\n"
            "We run paid ads exclusively for local service businesses. We recently helped a landscaper "
            "in a nearby market go from 4 jobs/week to 17 — all recurring customers, no Thumbtack.\n\n"
            "Would it make sense to hop on a 15-min call this week? "
            "No pitch — just want to understand your busy season."
        ),
        "inactive": (
            "You ran Facebook ads before — here's what went wrong",
            "Hey {name},\n\n"
            "Noticed {company} ran some Facebook ads a while back but stopped. "
            "That's the most common story I hear from landscapers: ran ads, got garbage leads, "
            "or the agency disappeared after month 2.\n\n"
            "We guarantee exclusive leads — the same job doesn't go to 5 other landscapers in your area.\n\n"
            "Happy to show you what we did differently for a company in {state} with the same experience. "
            "15 minutes, no commitment."
        ),
        "active": (
            "Are your landscaping leads exclusive or shared?",
            "Hey {name},\n\n"
            "Noticed {company} is running some ads — smart move. Most in {city} aren't.\n\n"
            "Quick question: are those leads exclusive, or shared with 3–5 other landscapers at the same time?\n\n"
            "We run campaigns where every lead comes only to you. Happy to do a free audit of what "
            "you're running now. No strings."
        ),
    },
    "plumbing": {
        "service": "plumbing",
        "never": (
            "Quick question about your plumbing leads in {city}",
            "Hey {name},\n\n"
            "Found {company} on Google — you don't have any ads running, which is surprising "
            "because emergency plumbing is one of the highest-intent searches on Google and Meta.\n\n"
            "We run paid ads exclusively for plumbers. A client in a similar market went from "
            "word-of-mouth only to 25 booked jobs/month in 60 days.\n\n"
            "Worth a 15-min call to see if we can do the same for {city}?"
        ),
        "inactive": (
            "You ran ads before — why plumbers usually stop (and how to fix it)",
            "Hey {name},\n\n"
            "Saw {company} ran some ads but stopped. Most plumbers quit because the leads were "
            "shared with 4 other plumbers, or the agency didn't understand emergency vs. scheduled work.\n\n"
            "We only work with local service businesses and send every lead exclusively to one company.\n\n"
            "15 minutes to show you what a different approach looks like?"
        ),
        "active": (
            "Are your plumbing leads exclusive or shared?",
            "Hey {name},\n\n"
            "Noticed {company} is running ads — nice. Most plumbers in {city} rely entirely on "
            "Google Maps and hope for the best.\n\n"
            "Are those leads exclusive or going to multiple contractors simultaneously? "
            "Happy to audit what you're running and show you where leads are leaking."
        ),
    },
    "dental": {
        "service": "dental",
        "never": (
            "Quick question about new patient flow at {company}",
            "Hey {name},\n\n"
            "Found {company} on Google — noticed you're not running any paid ads for new patients. "
            "Most dental offices in {city} competing for high-value patients (implants, Invisalign, "
            "cosmetic) are already on Meta and Google.\n\n"
            "We run patient acquisition campaigns exclusively for dental offices. "
            "A practice in a similar market added 40 new patients/month at $85 CPL.\n\n"
            "Would a 15-min call make sense to see what's realistic for {city}?"
        ),
        "inactive": (
            "Dental ads didn't work before — here's why and what's different now",
            "Hey {name},\n\n"
            "Saw {company} ran some ads but stopped. Dental ads fail for a few common reasons: "
            "wrong patient targeting, or the agency treated you like any other service business.\n\n"
            "We only work with dental offices and we focus on high-value case types — "
            "not just cleanings that don't move the revenue needle.\n\n"
            "15 minutes to walk through what a different strategy would look like?"
        ),
        "active": (
            "Are you tracking patient acquisition cost at {company}?",
            "Hey {name},\n\n"
            "Noticed {company} is running some ads — great sign. "
            "Quick question: do you know your cost per new patient by procedure type?\n\n"
            "Most dental practices running ads don't break it down that way, "
            "which means they're overpaying for low-value cases.\n\n"
            "Happy to do a free audit and show you where the budget is leaking."
        ),
    },
    "solar": {
        "service": "solar",
        "never": (
            "Quick question about your solar leads in {city}",
            "Hey {name},\n\n"
            "Found {company} on Google — you're not running any ads, which is a big opportunity. "
            "Homeowner intent for solar in {city} is at a multi-year high right now "
            "and most installers are still buying expensive shared leads from lead gen platforms.\n\n"
            "We run exclusive homeowner lead campaigns for local solar installers. "
            "No Energysage. No shared leads. Every inquiry comes only to you.\n\n"
            "Worth a quick 15-min call to see what the numbers would look like?"
        ),
        "inactive": (
            "Solar ads didn't convert — here's the most common reason why",
            "Hey {name},\n\n"
            "Noticed {company} ran some ads but stopped. The most common failure point for solar "
            "ads is targeting homeowners who rent or have shaded roofs — audiences that look great "
            "on paper but never convert.\n\n"
            "We use roof-ownership and utility-bill targeting to cut out that waste from day one.\n\n"
            "15 minutes to show you what that looks like for {state}?"
        ),
        "active": (
            "What's your cost per solar appointment in {city}?",
            "Hey {name},\n\n"
            "Noticed {company} is running ads — solid move. "
            "Quick question: what are you paying per qualified appointment right now?\n\n"
            "We run solar campaigns where leads are exclusive and pre-qualified "
            "(homeowner, own roof, avg utility bill above threshold). "
            "Happy to compare benchmarks with what you're seeing."
        ),
    },
    "chiropractic": {
        "service": "chiropractic",
        "never": (
            "Quick question about new patient flow at {company}",
            "Hey {name},\n\n"
            "Found {company} on Google — noticed you're not running any ads for new patients. "
            "Most chiropractors in {city} rely on referrals and Google Maps, "
            "which caps how fast they can grow.\n\n"
            "We run paid ads exclusively for chiropractic offices. "
            "A clinic in a similar market added 35 new patients/month at under $50 CPL.\n\n"
            "15-min call to see if that's realistic for {city}?"
        ),
        "inactive": (
            "Chiropractic ads didn't work before — here's what most agencies miss",
            "Hey {name},\n\n"
            "Saw {company} ran some ads but stopped. Most agencies run generic pain-point ads "
            "that attract tire-kickers. We target people actively searching for a chiropractor "
            "within a specific radius who haven't booked yet.\n\n"
            "15 minutes to walk through what a focused approach looks like?"
        ),
        "active": (
            "Are your chiropractic leads booking or just inquiring?",
            "Hey {name},\n\n"
            "Noticed {company} is running ads — nice. "
            "Quick question: what's your show rate from ad leads?\n\n"
            "Most chiro ad campaigns have a show-rate problem, not a lead volume problem. "
            "Happy to do a free audit and show you where the drop-off is happening."
        ),
    },
}

# Fallback for verticals not in VERTICAL_TEMPLATES
GENERIC_TEMPLATES = {
    "never": (
        "Quick question about your {service} leads in {city}",
        "Hey {name},\n\n"
        "Found {company} on Google — noticed you don't have any ads running. "
        "Most {service} businesses in {city} are already using Meta and Google to lock up local jobs.\n\n"
        "We run paid ads exclusively for local service businesses. "
        "Would it make sense to hop on a 15-min call this week to see if there's a fit?"
    ),
    "inactive": (
        "You ran Facebook ads before — here's what went wrong",
        "Hey {name},\n\n"
        "Noticed {company} ran some Facebook ads but stopped. "
        "We guarantee exclusive leads — they don't go to multiple {service} businesses simultaneously.\n\n"
        "15 minutes to show you what a different approach looks like?"
    ),
    "active": (
        "Are your {service} leads exclusive or shared?",
        "Hey {name},\n\n"
        "Noticed {company} is running some ads — smart move.\n\n"
        "Are those leads exclusive or going to multiple competitors? "
        "Happy to audit what you're running. No strings."
    ),
}


def get_templates(vertical: str) -> dict:
    return VERTICAL_TEMPLATES.get(vertical, GENERIC_TEMPLATES)


def state_from_city(city: str) -> str:
    parts = city.rsplit(" ", 1)
    return parts[-1] if len(parts) > 1 else city


def delete_drafts_for_leads(lead_emails: set):
    service = _get_service()
    deleted = 0
    page_token = None
    while True:
        kwargs = {"userId": "me", "maxResults": 500}
        if page_token:
            kwargs["pageToken"] = page_token
        resp = service.users().drafts().list(**kwargs).execute()
        drafts = resp.get("drafts", [])
        for d in drafts:
            detail = service.users().drafts().get(userId="me", id=d["id"], format="metadata").execute()
            headers = detail.get("message", {}).get("payload", {}).get("headers", [])
            to = next((h["value"] for h in headers if h["name"].lower() == "to"), "")
            if any(email in to for email in lead_emails):
                service.users().drafts().delete(userId="me", id=d["id"]).execute()
                print(f"  Deleted draft → {to}")
                deleted += 1
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    print(f"Deleted {deleted} drafts.\n")


def run(vertical: str, limit: int = None, rebuild: bool = False):
    leads_path = os.path.join(TMP_DIR, f"{vertical}_leads.json")
    if not os.path.exists(leads_path):
        print(f"No leads file at {leads_path}. Run scrape_gmaps.py --vertical {vertical} first.")
        sys.exit(1)

    with open(leads_path) as f:
        leads = json.load(f)

    with_email = [l for l in leads if l.get("email")]
    print(f"Vertical: {vertical} | Total leads: {len(leads)} | With email: {len(with_email)}")

    if limit:
        with_email = with_email[:limit]

    if rebuild:
        print("Deleting existing drafts for these leads...")
        delete_drafts_for_leads({l["email"] for l in with_email})

    templates = get_templates(vertical)
    service_label = VERTICAL_TEMPLATES.get(vertical, {}).get("service", vertical)
    created = 0

    for i, lead in enumerate(with_email, 1):
        name = lead.get("name", "there")
        company = lead.get("name", "your company")
        city = lead.get("city", "your city")
        state = state_from_city(city)
        status = lead.get("fb_ads_status") or "never"
        template_key = status if status in templates else "never"
        subject_tpl, body_tpl = templates[template_key] if isinstance(templates[template_key], tuple) else (
            templates[template_key][0], templates[template_key][1]
        )

        fmt = dict(name=name, company=company, city=city, state=state, service=service_label)
        subject = subject_tpl.format(**fmt)
        plain_body = body_tpl.format(**fmt)

        # Append CTA and booking link
        plain_body += f"\n\n→ Book a 15-min call: {CAL_LINK}"

        html_body = build_html_body(plain_body, include_pricing=True)

        print(f"  [{i}/{len(with_email)}] {name} ({city}) — {lead['email']}")
        try:
            result = create_draft(
                to=lead["email"],
                subject=subject,
                body=html_body,
                html=True,
            )
            print(f"    Draft ID: {result['draft_id']}")
            created += 1
        except Exception as e:
            print(f"    Error: {e}")

        time.sleep(0.3)

    print(f"\nDone — {created} drafts created.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--vertical", required=True, choices=list(VERTICAL_TEMPLATES.keys()) + ["roofing", "hvac"],
                        help="Which vertical to generate drafts for")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--rebuild", action="store_true")
    args = parser.parse_args()
    run(args.vertical, limit=args.limit, rebuild=args.rebuild)
