#!/usr/bin/env python3
"""
Two-way sync between the notes RAG and the Notion "Pendientes" database.

  Notion → local: reads every row; tasks checked "Hecho" stop showing up in pending/proposals.
  local → Notion: creates rows for new pending tasks (never duplicates: matched by "Clave"
                  or by the normalized title). It never edits or deletes existing rows.

Only tasks noted on/after BASELINE are created: everything before was loaded by hand on 27/9/2026.

Needs in .env:
  NOTION_TOKEN=secret_...                  (Notion → Settings → Connections → Develop integrations;
                                           then share the Pendientes database with the integration)
  NOTION_PENDIENTES_DB=<database id>

Usage:
  python3 tools/notion_sync.py --dry-run
  python3 tools/notion_sync.py
"""
import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import requests

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from tools import notes_rag as rag

API = "https://api.notion.com/v1"
VERSION = "2022-06-28"
BASELINE = "2026-09-28"
DEFAULT_PRIORITY = "🟠 Después"


def _headers(token):
    return {"Authorization": f"Bearer {token}", "Notion-Version": VERSION, "Content-Type": "application/json"}


def _text(prop):
    items = (prop or {}).get("title") or (prop or {}).get("rich_text") or []
    return "".join(t.get("plain_text", "") for t in items)


def fetch_rows(session, token, db_id):
    rows, cursor = [], None
    while True:
        body = {"page_size": 100, **({"start_cursor": cursor} if cursor else {})}
        r = session.post(f"{API}/databases/{db_id}/query", headers=_headers(token), json=body, timeout=30)
        r.raise_for_status()
        data = r.json()
        for page in data["results"]:
            p = page["properties"]
            rows.append({"id": page["id"], "title": _text(p.get("Tarea")), "clave": _text(p.get("Clave")),
                         "done": bool((p.get("Hecho") or {}).get("checkbox"))})
        if not data.get("has_more"):
            return rows
        cursor = data["next_cursor"]


def build_state(rows):
    """Index Notion rows by Clave and by normalized title (rows loaded by hand have no Clave)."""
    tasks = {}
    for row in rows:
        for key in {row["clave"], rag.wd.task_key(row["title"])} - {""}:
            tasks[key] = {"done": row["done"], "page_id": row["id"], "title": row["title"]}
    return {"synced_at": datetime.now().isoformat(), "tasks": tasks}


def page_body(db_id, p):
    props = {
        "Tarea": {"title": [{"text": {"content": p["title"][:200]}}]},
        "Clave": {"rich_text": [{"text": {"content": p["key"]}}]},
        "Origen": {"select": {"name": "auto"}},
        "Prioridad": {"select": {"name": DEFAULT_PRIORITY}},
        "Anotado": {"date": {"start": p["date"][:10]}},
        "Hecho": {"checkbox": False},
    }
    if p["tag"]:
        props["Tag"] = {"select": {"name": p["tag"]}}
    if p["chat"]:
        props["Chat"] = {"select": {"name": p["chat"]}}
    return {"parent": {"database_id": db_id}, "properties": props}


def sync(db, session, token, db_id, dry_run=False):
    state = build_state(fetch_rows(session, token, db_id))
    rag.NOTION_STATE.parent.mkdir(parents=True, exist_ok=True)
    rag.NOTION_STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    done = len({t["page_id"] for t in state["tasks"].values() if t["done"]})

    new = [p for p in rag.pending(db) if p["date"][:10] >= BASELINE and p["key"] not in state["tasks"]]
    for p in new:
        if dry_run:
            print(f"  + (dry-run) {p['title']}  [{p['tag']}, {p['chat']}]")
            continue
        r = session.post(f"{API}/pages", headers=_headers(token), json=page_body(db_id, p), timeout=30)
        r.raise_for_status()
        print(f"  + {p['title']}")
    return {"notion_rows": len({t['page_id'] for t in state['tasks'].values()}), "done": done, "created": len(new)}


def explain_error(e):
    """Turn network / API failures into one actionable line."""
    status = getattr(getattr(e, "response", None), "status_code", None)
    if status == 401:
        return "✗ Notion rechazó el token (401): revisá NOTION_TOKEN en .env o regeneralo."
    if status == 404:
        return ("✗ Notion no encuentra la base (404): compartila con la integración "
                "(página → ⋯ → Conexiones) y revisá NOTION_PENDIENTES_DB.")
    if isinstance(e, (requests.exceptions.ProxyError, requests.exceptions.ConnectionError)):
        return f"✗ Sin conexión a api.notion.com (red o proxy bloqueado): {type(e).__name__}"
    return f"✗ Error de Notion: {e}"


def main():
    rag.wd.utf8_io()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
    token, db_id = os.environ.get("NOTION_TOKEN"), os.environ.get("NOTION_PENDIENTES_DB")
    if not token or not db_id:
        sys.exit("Faltan NOTION_TOKEN y/o NOTION_PENDIENTES_DB en .env (ver el docstring de este archivo).")

    rag.wd.load_config()
    db = rag.connect()
    rag.refresh_from_bridge(db)
    try:
        res = sync(db, requests.Session(), token, db_id, args.dry_run)
    except requests.RequestException as e:
        sys.exit(explain_error(e))
    print(f"  Notion: {res['notion_rows']} filas, {res['done']} hechas · creadas ahora: {res['created']}"
          + (" (dry-run)" if args.dry_run else ""))


if __name__ == "__main__":
    main()
