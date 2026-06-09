"""
Generates personalized cold-outreach Gmail drafts for HVAC leads.

Reads from .tmp/hvac_leads.json, picks leads with email addresses,
and creates HTML drafts in Gmail.

Usage:
  python3 tools/generate_hvac_drafts.py              # create drafts for leads without one
  python3 tools/generate_hvac_drafts.py --rebuild    # delete existing drafts and recreate all
  python3 tools/generate_hvac_drafts.py --limit 5   # process first 5 only
  python3 tools/generate_hvac_drafts.py --min-tier A  # only Tier A leads (default: B)
"""

import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
from gmail_draft import create_draft, build_html_body, _get_service

TMP_DIR = os.path.join(os.path.dirname(__file__), "..", ".tmp")
LEADS_JSON = os.path.join(TMP_DIR, "hvac_leads.json")

TEMPLATES = {
    "none": (
        "Quick question about your HVAC leads in {city}",
        "Hey {name},\n\n"
        "Found your HVAC company in {city} and noticed you don't have any ads running — "
        "most of your competitors are already using Meta and Google to lock up local AC and heating calls.\n\n"
        "We run paid ads exclusively for HVAC contractors. Last month we helped a company "
        "in a nearby market go from 4 service calls/week to 22 — all exclusive leads, no Angi, no lead-sharing.\n\n"
        "Would it make sense to hop on a 15-min call this week to see if there's a fit? "
        "No pitch, just want to understand what your slow season looks like.\n\n"
        "— Guido"
    ),
    "inactive": (
        "You ran Facebook ads before — here's what went wrong",
        "Hey {name},\n\n"
        "Saw you ran some Facebook ads a while back but stopped. That's the most common "
        "story I hear from HVAC owners: ran ads, got garbage leads, or the agency disappeared after month 2.\n\n"
        "We only work with HVAC companies (no roofers, plumbers, etc.) and we guarantee "
        "exclusive leads — the same job doesn't go to 5 other contractors in your area.\n\n"
        "If you're open to it, I'd love to show you what we did differently for a company in {state} "
        "that had the same experience. 15 minutes, no commitment.\n\n"
        "— Guido"
    ),
    "active": (
        "Are your HVAC leads exclusive or shared?",
        "Hey {name},\n\n"
        "Noticed you're running some ads — good move. Most HVAC companies in your market aren't.\n\n"
        "Quick question: are your leads exclusive, or are they going to 3–5 other contractors at the same time?\n\n"
        "We run campaigns where every lead comes only to you. Higher close rate, less time chasing "
        "people who already booked someone else.\n\n"
        "Happy to do a free audit of what you're running now and show you exactly where leads are "
        "leaking. No strings attached.\n\n"
        "— Guido"
    ),
}

# fb_ads_status values from check_fb_ads.py → map to template keys
STATUS_TO_TEMPLATE = {
    "none": "none",
    "fb_only": "none",      # no Google Ads — pitch Google
    "google_only": "none",  # no Meta — pitch Meta
    "both": "active",       # running both — improvement pitch
    "unknown": "none",
    "no_website": "none",
}
DEFAULT_TEMPLATE = "none"


def state_from_city(city: str) -> str:
    parts = city.rsplit(" ", 1)
    return parts[-1] if len(parts) > 1 else city


def delete_drafts_for_leads(lead_emails: set):
    """Delete all drafts whose recipient is in lead_emails."""
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
            try:
                detail = service.users().drafts().get(userId="me", id=d["id"], format="metadata").execute()
            except Exception:
                continue
            headers = detail.get("message", {}).get("payload", {}).get("headers", [])
            to = next((h["value"] for h in headers if h["name"].lower() == "to"), "")
            if any(email in to for email in lead_emails):
                try:
                    service.users().drafts().delete(userId="me", id=d["id"]).execute()
                    print(f"  Deleted draft → {to}")
                    deleted += 1
                except Exception:
                    pass

        page_token = resp.get("nextPageToken")
        if not page_token:
            break

    print(f"Deleted {deleted} drafts.\n")


TIER_ORDER = {"A": 0, "B": 1, "C": 2}


def run(limit: int = None, rebuild: bool = False, min_tier: str = "B"):
    with open(LEADS_JSON) as f:
        leads = json.load(f)

    with_email = [l for l in leads if l.get("email")]
    print(f"Total leads: {len(leads)} | With email: {len(with_email)}")

    # Tier filtering
    unscored = [l for l in with_email if not l.get("tier")]
    if unscored:
        print(f"  Warning: {len(unscored)} lead(s) have no tier field — run score_leads.py first. Processing them anyway.")

    min_order = TIER_ORDER[min_tier]
    skipped_by_tier = {t: 0 for t in ("A", "B", "C")}
    filtered = []
    for l in with_email:
        tier = l.get("tier")
        if tier is None:
            filtered.append(l)  # no tier → include (with warning above)
        elif TIER_ORDER.get(tier, 99) <= min_order:
            filtered.append(l)
        else:
            skipped_by_tier[tier] = skipped_by_tier.get(tier, 0) + 1

    print(f"After tier filter (min {min_tier}): {len(filtered)} leads | Skipped: {sum(skipped_by_tier.values())}")

    if limit:
        filtered = filtered[:limit]

    if rebuild:
        print("Deleting existing drafts for these leads...")
        delete_drafts_for_leads({l["email"] for l in filtered})

    created = 0
    tier_counts = {"A": 0, "B": 0, "C": 0, None: 0}
    for i, lead in enumerate(filtered, 1):
        name = lead.get("name", "there")
        city = lead.get("city", "your city")
        state = state_from_city(city)
        status = lead.get("fb_ads_status") or "none"

        template_key = STATUS_TO_TEMPLATE.get(status, DEFAULT_TEMPLATE)
        subject_tpl, body_tpl = TEMPLATES[template_key]

        subject = subject_tpl.format(name=name, city=city, state=state)
        plain_body = body_tpl.format(name=name, city=city, state=state)
        html_body = build_html_body(plain_body, include_pricing=True)

        tier_label = lead.get("tier", "?")
        print(f"  [{i}/{len(filtered)}] {name} ({city}) [Tier {tier_label}] — {lead['email']}")
        try:
            result = create_draft(
                to=lead["email"],
                subject=subject,
                body=html_body,
                html=True,
                label_ids=["Label_11"],  # HVAC - Lead Flow Angle
            )
            print(f"    Draft ID: {result['draft_id']}")
            created += 1
            tier_counts[lead.get("tier")] = tier_counts.get(lead.get("tier"), 0) + 1
        except Exception as e:
            print(f"    Error: {e}")

        time.sleep(0.3)

    skipped_c = skipped_by_tier.get("C", 0)
    skipped_b = skipped_by_tier.get("B", 0) if min_tier == "A" else 0
    summary_parts = [f"{tier_counts.get('A', 0)} Tier A", f"{tier_counts.get('B', 0)} Tier B"]
    print(f"\nDone — {created} drafts created ({', '.join(summary_parts)} | skipped {skipped_c} Tier C{f', {skipped_b} Tier B' if skipped_b else ''})")


if __name__ == "__main__":
    limit = None
    rebuild = "--rebuild" in sys.argv
    min_tier = "B"
    args = sys.argv[1:]
    for i, arg in enumerate(args):
        if arg.startswith("--limit"):
            limit = int(arg.split("=")[-1]) if "=" in arg else int(args[i + 1])
        elif arg.startswith("--min-tier"):
            val = arg.split("=")[-1] if "=" in arg else args[i + 1]
            if val not in TIER_ORDER:
                print(f"Error: --min-tier must be A, B, or C (got '{val}')")
                sys.exit(1)
            min_tier = val
    run(limit=limit, rebuild=rebuild, min_tier=min_tier)
