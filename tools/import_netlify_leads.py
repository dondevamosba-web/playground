#!/usr/bin/env python3
"""
Fetch inbound lead form submissions from Netlify Forms API.

Detects niche from form name, maps fields to a standard lead dict,
deduplicates against .tmp/imported_netlify_lead_ids.json, and writes
new leads to .tmp/inbound_leads.json.

Usage:
    python3 tools/import_netlify_leads.py
    python3 tools/import_netlify_leads.py --form-id <form_id>
    python3 tools/import_netlify_leads.py --dry-run
"""

import argparse
import json
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT        = Path(__file__).parent.parent
LEADS_FILE  = ROOT / ".tmp" / "inbound_leads.json"
SEEN_IDS    = ROOT / ".tmp" / "imported_netlify_lead_ids.json"

load_dotenv(ROOT / ".env")

NETLIFY_API = "https://api.netlify.com/api/v1"

# Map form name fragments → niche label
NICHE_MAP = {
    "roofing":  "roofing",
    "hvac":     "hvac",
    "plumbing": "plumbing",
    "windows":  "windows",
    "siding":   "siding",
}


def load_json(path, default):
    p = Path(path)
    return json.loads(p.read_text()) if p.exists() else default


def save_json(path, data):
    Path(path).parent.mkdir(exist_ok=True)
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False))


def detect_niche(form_name: str) -> str:
    name_lower = form_name.lower()
    for keyword, niche in NICHE_MAP.items():
        if keyword in name_lower:
            return niche
    return "unknown"


def get_forms(token: str, site_id: str) -> list:
    url = f"{NETLIFY_API}/sites/{site_id}/forms"
    resp = requests.get(url, headers={"Authorization": f"Bearer {token}"})
    resp.raise_for_status()
    return resp.json()


def get_submissions(token: str, form_id: str) -> list:
    url = f"{NETLIFY_API}/forms/{form_id}/submissions"
    resp = requests.get(url, headers={"Authorization": f"Bearer {token}"})
    resp.raise_for_status()
    return resp.json()


def map_submission(sub: dict, niche: str) -> dict:
    data = sub.get("data", {})
    return {
        "id":      sub.get("id"),
        "name":    data.get("name") or data.get("full_name") or "",
        "company": data.get("company") or data.get("business") or "",
        "city":    data.get("city") or data.get("location") or "",
        "phone":   data.get("phone") or data.get("telephone") or "",
        "email":   data.get("email") or "",
        "website": data.get("website") or data.get("url") or "",
        "message": data.get("message") or data.get("notes") or "",
        "niche":   niche,
        "source":  "netlify_form",
        "submitted_at": sub.get("created_at", ""),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--form-id", help="Target a specific Netlify form ID")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    token = os.getenv("NETLIFY_TOKEN")
    site_id = os.getenv("NETLIFY_SITE_ID")

    if not token:
        print("ERROR: NETLIFY_TOKEN not found in .env")
        sys.exit(1)
    if not site_id and not args.form_id:
        print("ERROR: NETLIFY_SITE_ID not found in .env (required unless --form-id is given)")
        sys.exit(1)

    seen_ids = set(load_json(SEEN_IDS, []))
    existing_leads = load_json(LEADS_FILE, [])

    # Determine which forms to pull
    if args.form_id:
        forms = [{"id": args.form_id, "name": args.form_id}]
    else:
        print(f"Fetching forms for site {site_id}...")
        forms = get_forms(token, site_id)
        print(f"  Found {len(forms)} form(s)")

    new_leads = []

    for form in forms:
        form_id   = form["id"]
        form_name = form.get("name", form_id)
        niche     = detect_niche(form_name)
        subs      = get_submissions(token, form_id)
        new_subs  = [s for s in subs if s["id"] not in seen_ids]

        print(f"  Form '{form_name}' (niche={niche}): {len(subs)} total, {len(new_subs)} new")

        for sub in new_subs:
            lead = map_submission(sub, niche)
            new_leads.append(lead)
            seen_ids.add(sub["id"])
            print(f"    + {lead['name'] or '(no name)'} | {lead['email'] or '(no email)'} | {niche}")

    if not new_leads:
        print("No new leads found.")
        return

    if args.dry_run:
        print(f"\n[dry-run] Would add {len(new_leads)} lead(s). No files written.")
        return

    updated = existing_leads + new_leads
    save_json(LEADS_FILE, updated)
    save_json(SEEN_IDS, sorted(seen_ids))

    print(f"\nImported {len(new_leads)} new lead(s) → {LEADS_FILE}")
    print("Next step: python3 tools/score_inbound_leads.py")


if __name__ == "__main__":
    main()
