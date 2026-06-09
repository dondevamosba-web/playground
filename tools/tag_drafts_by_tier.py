#!/usr/bin/env python3
"""
Apply tier-based priority labels to existing Gmail drafts.

Reads lead JSONs, builds an email→tier lookup, then scans all drafts and
applies the matching priority label based on the lead's tier:
  Tier A → 🟢 Priority — Send Now    (Label_3)
  Tier B → 🟡 Good Lead — Send Soon  (Label_4)
  Tier C → 🔴 Long Shot              (Label_5)

Usage:
  python3 tools/tag_drafts_by_tier.py           # dry run — just prints
  python3 tools/tag_drafts_by_tier.py --apply   # actually applies labels
"""

import json
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
from gmail_draft import _get_service

ROOT = Path(__file__).parent.parent

LEAD_FILES = {
    "plumbing": ROOT / ".tmp" / "plumbing_leads.json",
    "hvac":     ROOT / ".tmp" / "hvac_leads.json",
    "roofing":  ROOT / ".tmp" / "roofing_leads.json",
    "windows":  ROOT / ".tmp" / "windows_leads.json",
}

TIER_LABEL = {
    "A": "Label_3",  # 🟢 Priority — Send Now
    "B": "Label_4",  # 🟡 Good Lead — Send Soon
    "C": "Label_5",  # 🔴 Long Shot — Generic Email
}


def build_email_tier_map() -> dict[str, tuple[str, str]]:
    """Returns {email: (tier, niche)} for all scored leads."""
    result = {}
    for niche, path in LEAD_FILES.items():
        if not path.exists():
            continue
        leads = json.loads(path.read_text())
        for lead in leads:
            email = (lead.get("email") or "").strip().lower()
            tier = lead.get("tier")
            if email and tier:
                result[email] = (tier, niche)
    return result


def run(apply: bool = False):
    email_tier = build_email_tier_map()
    print(f"Loaded {len(email_tier)} leads with email + tier")

    service = _get_service()
    page_token = None
    total = tagged = skipped = 0

    while True:
        kwargs = {"userId": "me", "maxResults": 500}
        if page_token:
            kwargs["pageToken"] = page_token

        resp = service.users().drafts().list(**kwargs).execute()
        drafts = resp.get("drafts", [])

        for d in drafts:
            total += 1
            try:
                detail = service.users().drafts().get(
                    userId="me", id=d["id"], format="metadata"
                ).execute()
            except Exception:
                continue

            headers = detail.get("message", {}).get("payload", {}).get("headers", [])
            to = next((h["value"] for h in headers if h["name"].lower() == "to"), "").strip().lower()
            msg_id = detail["message"]["id"]
            existing_labels = detail["message"].get("labelIds", [])

            match = email_tier.get(to)
            if not match:
                skipped += 1
                continue

            tier, niche = match
            label_id = TIER_LABEL.get(tier)
            if not label_id:
                skipped += 1
                continue

            if label_id in existing_labels:
                skipped += 1
                continue

            subject = next((h["value"] for h in headers if h["name"].lower() == "subject"), "")
            print(f"  [{tier}] {niche:10s}  {to:<40}  {subject[:45]}")

            if apply:
                service.users().messages().modify(
                    userId="me",
                    id=msg_id,
                    body={"addLabelIds": [label_id]}
                ).execute()
                tagged += 1

        page_token = resp.get("nextPageToken")
        if not page_token:
            break

    if apply:
        print(f"\nDone. {tagged} drafts labeled | {skipped} skipped (no match or already labeled) | {total} total scanned")
    else:
        print(f"\nDry run — {total} drafts scanned, {total - skipped} would be labeled. Run with --apply to apply.")


if __name__ == "__main__":
    apply = "--apply" in sys.argv
    if not apply:
        print("DRY RUN — pass --apply to write labels\n")
    run(apply=apply)
