#!/usr/bin/env python3
"""
Morning briefing: today's scheduled posts, approval-queue status, DM follow-ups
due, and new IG comments. Prints to stdout and (with --email) drops a Gmail
draft to yourself. Designed for a weekday-morning cron.

Usage:
  python3 tools/morning_briefing.py
  python3 tools/morning_briefing.py --email
"""
import argparse
import os
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from sheets_client import get_services

UNIFIED = os.environ["UNIFIED_APPROVAL_SHEET_ID"]
ACCOUNTS = ["Ola Digital", "Storm", "Fiestas", "Techno"]


def section_queue(sheets):
    lines, today = [], str(date.today())
    for acct in ACCOUNTS:
        res = sheets.spreadsheets().values().get(
            spreadsheetId=UNIFIED, range=f"'{acct}'!A2:G").execute()
        rows = [r + [""] * (7 - len(r)) for r in res.get("values", [])]
        drafts = sum(1 for r in rows if r[4] == "draft")
        approved = sum(1 for r in rows if r[4] == "approved")
        hoy = [r for r in rows if r[3][:10] == today and r[4] not in ("posted", "rejected")]
        flag = f" · HOY: {len(hoy)} post(s)" if hoy else ""
        lines.append(f"- {acct}: {drafts} en draft, {approved} aprobados sin publicar{flag}")
    return lines


def section_ayer():
    """Yesterday's publish results from the launchd logs + today's due slots."""
    import re
    from datetime import datetime, timedelta
    ayer = (date.today() - timedelta(days=1)).isoformat()
    ok, err = 0, []
    for logname in ("cron_publish.log", "cron_publish_approved.log"):
        log = ROOT / ".tmp" / logname
        if not log.exists():
            continue
        block_day = ""
        for ln in log.read_text(errors="ignore").splitlines()[-600:]:
            m = re.search(r"\[launchd\] \S+ exit=(\d+) (\d{4}-\d{2}-\d{2})", ln)
            if m:
                block_day = m.group(2)
            if f"] {ayer}" in ln or block_day == ayer or ayer in ln:
                if "Posted — Media ID" in ln or "✓ Posted" in ln or "Sheet updated → posted" in ln:
                    ok += 1
                if "ERROR" in ln:
                    err.append(ln.strip()[:100])
    lines = [f"- Ayer: {ok} post(s) publicados" + (f", {len(err)} errores" if err else ", sin errores")]
    lines += [f"  - ⚠️ {e}" for e in err[:5]]
    return lines


def section_dm_followups():
    import subprocess
    r = subprocess.run([sys.executable, str(ROOT / "tools" / "storm_dm_leads.py"), "due"],
                       capture_output=True, text=True)
    out = r.stdout.strip()
    return out.splitlines() if out and "Nada vencido" not in out else ["- Nada vencido"]


def section_comments():
    import subprocess
    r = subprocess.run([sys.executable, str(ROOT / "tools" / "comment_drafter.py"), "--no-claude"],
                       capture_output=True, text=True)
    return [f"- {r.stdout.strip() or r.stderr.strip()[:100]}"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--email", action="store_true")
    a = ap.parse_args()

    sheets, _ = get_services()
    parts = [f"BRIEFING — {date.today():%A %d/%m/%Y}", "", "## Publicaciones"]
    parts += section_ayer()
    parts += ["", "## Cola de contenido"]
    parts += section_queue(sheets)
    parts += ["", "## Follow-ups DM (Storm)"]
    parts += section_dm_followups()
    parts += ["", "## Comentarios IG"]
    parts += section_comments()
    body = "\n".join(parts)
    print(body)

    if a.email:
        from gmail_draft import create_draft
        create_draft(to="carminattiguido@gmail.com",
                     subject=f"Briefing {date.today():%d/%m}", body=body)
        print("\n(Draft creado en Gmail)")


if __name__ == "__main__":
    main()
