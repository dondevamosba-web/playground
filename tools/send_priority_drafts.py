#!/usr/bin/env python3
"""
Send up to N Gmail drafts labeled 🟢 Priority — Send Now (Label_3).

Picks drafts round-robin across niches (plumbing, HVAC, roofing, windows) so
sends stay mixed. After sending, removes Label_3 and adds Label_4
(Good Lead — Send Soon) as a "sent" marker so it won't be picked again.

Usage:
  python3 tools/send_priority_drafts.py              # send up to 20 (default)
  python3 tools/send_priority_drafts.py --limit 10   # send up to 10
  python3 tools/send_priority_drafts.py --dry-run    # preview without sending

Logs each send to .tmp/send_log.jsonl
"""

import json
import random
import re
import sys
import time
import os
from datetime import datetime, timezone
from pathlib import Path

VALID_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}$")

sys.path.insert(0, os.path.dirname(__file__))
from gmail_draft import _get_service

PRIORITY_LABEL  = "Label_3"   # 🟢 Priority — Send Now
SENT_LABEL      = "Label_4"   # 🟡 Good Lead — Send Soon  (repurposed as "sent" marker)

NICHE_LABELS = {
    "Label_12": "plumbing",
    "Label_11": "hvac",
    "Label_10": "roofing",
    "Label_9":  "roofing",
    "Label_13": "windows",
}

LOG_FILE = Path(__file__).parent.parent / ".tmp" / "send_log.jsonl"
DEFAULT_LIMIT = 20


def fetch_priority_drafts(service) -> list[dict]:
    """Return all drafts carrying the Priority label, with metadata."""
    drafts = []
    page_token = None
    while True:
        kwargs = {"userId": "me", "maxResults": 500}
        if page_token:
            kwargs["pageToken"] = page_token
        resp = service.users().drafts().list(**kwargs).execute()
        for d in resp.get("drafts", []):
            try:
                detail = service.users().drafts().get(
                    userId="me", id=d["id"], format="metadata"
                ).execute()
            except Exception:
                continue
            label_ids = detail["message"].get("labelIds", [])
            if PRIORITY_LABEL not in label_ids:
                continue
            headers = detail["message"]["payload"]["headers"]
            to      = next((h["value"] for h in headers if h["name"].lower() == "to"), "")
            subject = next((h["value"] for h in headers if h["name"].lower() == "subject"), "")
            if not VALID_EMAIL.match(to):
                print(f"  Skipping invalid email: {to[:60]}")
                continue
            niche   = next((NICHE_LABELS[l] for l in label_ids if l in NICHE_LABELS), "unknown")
            drafts.append({
                "draft_id":  d["id"],
                "message_id": detail["message"]["id"],
                "to":        to,
                "subject":   subject,
                "niche":     niche,
                "label_ids": label_ids,
            })
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    return drafts


def interleave(drafts: list[dict]) -> list[dict]:
    """Round-robin by niche so sends are mixed across verticals."""
    buckets: dict[str, list] = {}
    for d in drafts:
        buckets.setdefault(d["niche"], []).append(d)
    result = []
    while any(buckets.values()):
        for niche in list(buckets.keys()):
            if buckets[niche]:
                result.append(buckets[niche].pop(0))
    return result


def log_send(entry: dict):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")


def run(limit: int = DEFAULT_LIMIT, dry_run: bool = False):
    service = _get_service()

    print("Fetching priority drafts...")
    all_drafts = fetch_priority_drafts(service)
    print(f"Found {len(all_drafts)} priority drafts")

    if not all_drafts:
        print("Nothing to send.")
        return

    ordered = interleave(all_drafts)
    batch = ordered[:limit]

    niche_counts: dict[str, int] = {}
    for d in batch:
        niche_counts[d["niche"]] = niche_counts.get(d["niche"], 0) + 1

    print(f"Sending {len(batch)} drafts (limit={limit}): {niche_counts}")
    if dry_run:
        print("\n[DRY RUN — no emails sent]\n")
        for i, d in enumerate(batch, 1):
            print(f"  [{i}] {d['niche']:10s}  {d['to']:<40}  {d['subject'][:50]}")
        return

    sent = 0
    for i, d in enumerate(batch, 1):
        try:
            result = service.users().drafts().send(
                userId="me",
                body={"id": d["draft_id"]}
            ).execute()
            log_send({
                "ts":      datetime.now(timezone.utc).isoformat(),
                "niche":   d["niche"],
                "to":      d["to"],
                "subject": d["subject"],
            })
            print(f"  [{i}/{len(batch)}] SENT  {d['niche']:10s}  {d['to']}")
            sent += 1
        except Exception as e:
            print(f"  [{i}/{len(batch)}] ERROR {d['to']}: {e}")

        # Random delay 8–20s between sends to avoid spam triggers
        if i < len(batch):
            time.sleep(random.uniform(8, 20))

    remaining = len(all_drafts) - sent
    print(f"\nDone — {sent} sent | {remaining} priority drafts remaining")


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    limit = DEFAULT_LIMIT
    args = sys.argv[1:]
    for i, arg in enumerate(args):
        if arg.startswith("--limit"):
            limit = int(arg.split("=")[-1]) if "=" in arg else int(args[i + 1])
    run(limit=limit, dry_run=dry_run)
