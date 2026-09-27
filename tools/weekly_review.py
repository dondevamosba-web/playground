#!/usr/bin/env python3
"""
Notes review — the one command that keeps everything up to date and proposes what to do.

  1. Update the notes RAG: WhatsApp bridge (if running) + any exports in WHATSAPP_EXPORTS_DIR
  2. Enrich new links (titles + topics)
  3. Sync with Notion (if NOTION_TOKEN is set): pull "Hecho", push new tasks
  4. Proposals → .tmp/notes_rag/review-YYYY-MM-DD.md (+ macOS notification)

Scheduled by tools/notes_schedule.sh (Mac) or tools/windows_setup.py schedule (Windows), Sunday 10:00. Also run by the /whatsapp command.

Usage:
  python3 tools/weekly_review.py            # free: rule-based proposals only
  python3 tools/weekly_review.py --llm      # + Claude proposals (paid API call)
  python3 tools/weekly_review.py --days 7 --no-links --no-notion
"""
import argparse
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from tools import enrich_links
from tools import notes_rag as rag

EXPORTS_DIR = Path(os.environ.get("WHATSAPP_EXPORTS_DIR", "~/Downloads/whatsapp")).expanduser()


def notify(title, text):
    if shutil.which("osascript"):
        subprocess.run(["osascript", "-e", f'display notification "{text}" with title "{title}"'], check=False)
    elif os.name == "nt":
        ps = ("Add-Type -AssemblyName System.Windows.Forms; $n = New-Object System.Windows.Forms.NotifyIcon; "
              "$n.Icon = [System.Drawing.SystemIcons]::Information; $n.Visible = $true; "
              f"$n.ShowBalloonTip(10000, '{title}', '{text}', 'Info'); Start-Sleep 11; $n.Dispose()")
        subprocess.Popen(["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", ps],
                         creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))


def main():
    rag.wd.utf8_io()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--llm", action="store_true", help="add Claude proposals (paid API call)")
    ap.add_argument("--no-links", action="store_true")
    ap.add_argument("--no-notion", action="store_true")
    args = ap.parse_args()

    rag.wd.load_config()
    db = rag.connect()
    log = []

    # 1. Sources
    if rag.bridge_path().exists():
        new = rag.ingest_bridge(db, rag.bridge_path())
        log.append(f"Bridge: {new} mensajes nuevos")
    exports = sorted(EXPORTS_DIR.glob("*.zip")) if EXPORTS_DIR.exists() else []
    if exports:
        new = rag.ingest_exports(db, [str(p) for p in exports])
        log.append(f"Exports ({EXPORTS_DIR}): {new} mensajes nuevos")
    items = rag.rebuild(db)
    if not log:
        log.append(f"⚠ Sin fuentes nuevas: ni bridge ({rag.bridge_path()}) ni exports en {EXPORTS_DIR}")

    # 2. Links
    if not args.no_links:
        try:
            n = enrich_links.enrich(db, limit=100)
            enrich_links.report(db)
            log.append(f"Links: {n} consultados → {enrich_links.OUT.name}")
        except Exception as e:
            log.append(f"⚠ Links: {e}")

    # 3. Notion
    if not args.no_notion and os.environ.get("NOTION_TOKEN") and os.environ.get("NOTION_PENDIENTES_DB"):
        import requests
        from tools import notion_sync
        try:
            res = notion_sync.sync(db, requests.Session(), os.environ["NOTION_TOKEN"], os.environ["NOTION_PENDIENTES_DB"])
            log.append(f"Notion: {res['created']} tareas nuevas, {res['done']} hechas")
        except Exception as e:
            log.append(f"⚠ Notion: {e}")
    elif not args.no_notion:
        log.append("Notion: sin NOTION_TOKEN en .env, salteado")

    # 4. Proposals
    props = rag.propose(db, args.days)
    lines = [f"# Revisión de notas — {datetime.now():%Y-%m-%d}", "", "## Propuestas", ""]
    lines += [f"- {p}" for p in props]
    if args.llm:
        try:
            lines += ["", "## 🤖 Claude propone", "", rag.propose_llm(db, args.days)]
        except Exception as e:
            lines += ["", f"⚠ Claude: {e}"]
    pend = rag.pending(db)
    lines += ["", f"## Pendientes ({len(pend)})", ""]
    lines += [f"- [ ] {p['title']}  _({p['tag'] or 'sin tag'}, {p['date'][:10]})_" for p in pend]
    lines += ["", "## Corrida", ""] + [f"- {l}" for l in log] + [f"- {len(items)} notas en total"]

    out = rag.DATA / f"review-{datetime.now():%Y-%m-%d}.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:4 + len(props)]))
    print(f"\n  → {out}")
    notify("Revisión de notas", f"{len(props)} propuestas, {len(pend)} pendientes")


if __name__ == "__main__":
    main()
