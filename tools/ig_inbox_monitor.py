#!/usr/bin/env python3
"""
Monitor Instagram comments and DMs across all 4 accounts.
Sends an email draft (via Gmail MCP) with anything that needs attention:
- Comments with questions (?, preguntas, precio, cómo, cuándo, dónde, info)
- Negative/spam comments
- New DM threads updated in the last 24h

Usage:
  python3 tools/ig_inbox_monitor.py            # check last 24h, email if anything found
  python3 tools/ig_inbox_monitor.py --dry-run  # print findings without emailing
  python3 tools/ig_inbox_monitor.py --hours 48 # check last 48h
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from tools.sheets_client import get_services

GRAPH    = "https://graph.facebook.com/v19.0"
TOKEN    = os.environ["INSTAGRAM_ACCESS_TOKEN"]
AR_TZ    = timezone(timedelta(hours=-3))
OWNER    = os.environ.get("OWNER_EMAIL", "carminattiguido@gmail.com")

ACCOUNTS = {
    "Fiestas":    (os.environ["FIESTAS_INSTAGRAM_BUSINESS_ACCOUNT_ID"],    "282931238497562"),
    "Ola Digital":(os.environ["INSTAGRAM_BUSINESS_ACCOUNT_ID"],             "210769605619003"),
    "Storm":      (os.environ["STORM_INSTAGRAM_BUSINESS_ACCOUNT_ID"],       "1571830086362037"),
    "Techno":     (os.environ["TECHNO_INSTAGRAM_BUSINESS_ACCOUNT_ID"],      "101629826062220"),
}

# Keywords that signal the comment needs attention
ATTENTION_RE = [
    r"\?",                          # question mark
    r"\b(precio|precios|cuánto|cuanto|costo)\b",
    r"\b(cómo|como|dónde|donde|cuándo|cuando|info|información|informacion)\b",
    r"\b(link|ticket|tickets|entrada|entradas|comprar)\b",
    r"\b(malo|pésimo|basura|estafa|reportar|spam)\b",
]

import re
_attention_pattern = re.compile("|".join(ATTENTION_RE), re.IGNORECASE)


def page_token(page_id: str) -> str:
    r = requests.get(f"{GRAPH}/me/accounts",
                     params={"access_token": TOKEN, "fields": "id,access_token"})
    for p in r.json().get("data", []):
        if p["id"] == page_id:
            return p["access_token"]
    return TOKEN


def check_comments(ig_id: str, pt: str, since_dt: datetime) -> list[dict]:
    """Return comments newer than since_dt that need attention."""
    flagged = []
    posts = requests.get(f"{GRAPH}/{ig_id}/media", params={
        "fields": "id,timestamp,permalink,comments_count",
        "limit": 20,
        "access_token": pt,
    }).json().get("data", [])

    for post in posts:
        if post.get("comments_count", 0) == 0:
            continue
        post_ts = datetime.fromisoformat(post["timestamp"].replace("Z", "+00:00"))
        # Only check posts from last 30 days
        if (datetime.now(timezone.utc) - post_ts).days > 30:
            continue

        comments = requests.get(f"{GRAPH}/{post['id']}/comments", params={
            "access_token": pt,
            "fields": "id,text,timestamp,username",
            "limit": 50,
        }).json().get("data", [])

        for c in comments:
            c_ts = datetime.fromisoformat(c["timestamp"].replace("Z", "+00:00"))
            if c_ts < since_dt:
                continue
            if _attention_pattern.search(c.get("text", "")):
                flagged.append({
                    "type":     "comment",
                    "post_url": post.get("permalink", ""),
                    "username": c.get("username", "?"),
                    "text":     c.get("text", ""),
                    "ts":       c_ts.astimezone(AR_TZ).strftime("%d/%m %H:%M"),
                })
    return flagged


def check_dms(page_id: str, pt: str, since_dt: datetime) -> list[dict]:
    """Return DM threads updated since since_dt."""
    flagged = []
    convs = requests.get(f"{GRAPH}/{page_id}/conversations", params={
        "access_token": pt,
        "fields": "id,updated_time",
        "limit": 25,
    }).json().get("data", [])

    for conv in convs:
        upd = datetime.fromisoformat(conv["updated_time"].replace("Z", "+00:00"))
        if upd < since_dt:
            continue
        # Get latest message
        msgs = requests.get(f"{GRAPH}/{conv['id']}/messages", params={
            "access_token": pt,
            "fields": "message,from,created_time",
            "limit": 1,
        }).json().get("data", [])
        for m in msgs:
            sender = m.get("from", {}).get("name", "?")
            text   = m.get("message", "")
            m_ts   = datetime.fromisoformat(m["created_time"].replace("Z", "+00:00"))
            if m_ts < since_dt:
                continue
            flagged.append({
                "type":   "dm",
                "from":   sender,
                "text":   text[:200],
                "ts":     m_ts.astimezone(AR_TZ).strftime("%d/%m %H:%M"),
            })
    return flagged


def build_email(findings: dict[str, list]) -> str:
    lines = ["Resumen de inbox — " + datetime.now(AR_TZ).strftime("%d/%m/%Y %H:%M") + " AR\n"]
    total = sum(len(v) for v in findings.values())
    lines.append(f"Total: {total} interacciones que necesitan atención\n")
    lines.append("=" * 60)

    for account, items in findings.items():
        if not items:
            continue
        lines.append(f"\n── {account} ──")
        for it in items:
            if it["type"] == "comment":
                lines.append(f"  COMMENT [{it['ts']}] @{it['username']}: {it['text'][:120]}")
                lines.append(f"    → {it['post_url']}")
            elif it["type"] == "dm":
                lines.append(f"  DM [{it['ts']}] {it['from']}: {it['text'][:120]}")

    lines.append("\n" + "=" * 60)
    lines.append("Respondé desde el Business Suite o la app.")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--hours",   type=int, default=24)
    args = parser.parse_args()

    since = datetime.now(timezone.utc) - timedelta(hours=args.hours)
    findings: dict[str, list] = {}

    for account, (ig_id, page_id) in ACCOUNTS.items():
        pt = page_token(page_id)
        items  = check_comments(ig_id, pt, since)
        items += check_dms(page_id, pt, since)
        findings[account] = items
        print(f"{account}: {len(items)} items")

    total = sum(len(v) for v in findings.values())

    if total == 0:
        print("Inbox limpio — nada que requiera atención.")
        return

    body = build_email(findings)
    print("\n" + body)

    if not args.dry_run:
        # Save to .tmp for reference
        out = ROOT / ".tmp" / "inbox_report.txt"
        out.write_text(body)
        print(f"\nReport saved: {out}")
        # Send email draft via Gmail (requires gmail_draft.py)
        import subprocess
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "gmail_draft.py"),
             "--to", OWNER,
             "--subject", f"[Inbox] {total} interacciones — {datetime.now(AR_TZ).strftime('%d/%m')}",
             "--body", body],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print("Email draft creado.")
        else:
            print("Email draft falló:", result.stderr[:200])


if __name__ == "__main__":
    main()
