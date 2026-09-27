#!/usr/bin/env python3
"""
Notes RAG — a local, always-updated index of the 3 note-to-self chats (Psi / Ide / Vida)
that can be searched and that proposes what to do next.

Sources (either or both):
  - WhatsApp exports (.zip / chat.txt / folder)          → manual, any time
  - WhatsApp bridge DB (whatsapp-bridge/store/messages.db) → automatic, see tools/whatsapp_bridge.sh

Storage: .tmp/notes_rag/notes.db (SQLite + FTS5). Raw messages are the source of truth;
tags, flags and duplicates are recomputed on every ingest with tools/whatsapp_digest.py.

Usage:
  python3 tools/notes_rag.py ingest Psi.zip Ide.zip Vida.zip   # from exports
  python3 tools/notes_rag.py ingest --bridge                    # from the bridge DB
  python3 tools/notes_rag.py watch --every 600                  # re-ingest from the bridge forever
  python3 tools/notes_rag.py search "cocina gas"
  python3 tools/notes_rag.py pending
  python3 tools/notes_rag.py propose [--days 7] [--llm]         # --llm calls Claude (paid API)
"""
import argparse
import hashlib
import json
import os
import re
import sqlite3
import sys
import time
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")   # WHATSAPP_BRIDGE_DB etc. — also for the MCP server, which imports this module

from tools import whatsapp_digest as wd

DATA = ROOT / ".tmp" / "notes_rag"
DB_PATH = DATA / "notes.db"
NOTION_STATE = DATA / "notion_state.json"   # written by tools/notion_sync.py
DEFAULT_BRIDGE = Path.home() / "whatsapp-mcp" / "whatsapp-bridge" / "store" / "messages.db"

STALE_DAYS = 14


# ── Storage ────────────────────────────────────────────────────────────────────

def connect(path=None):
    path = Path(path or DB_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    db.executescript("""
        CREATE TABLE IF NOT EXISTS raw   (id TEXT PRIMARY KEY, chat_key TEXT, ts TEXT, text TEXT, source TEXT);
        CREATE TABLE IF NOT EXISTS notes (id TEXT PRIMARY KEY, chat TEXT, date TEXT, note TEXT, tags TEXT,
                                          kind TEXT, flags TEXT, urls TEXT);
        CREATE TABLE IF NOT EXISTS links (url TEXT PRIMARY KEY, title TEXT, topic TEXT, fetched TEXT);
        CREATE TABLE IF NOT EXISTS meta  (k TEXT PRIMARY KEY, v TEXT);
        CREATE VIRTUAL TABLE IF NOT EXISTS notes_fts USING fts5(id UNINDEXED, body, tokenize='unicode61 remove_diacritics 2');
    """)
    return db


def _raw_id(chat_key, ts, text):
    return hashlib.sha1(f"{chat_key}|{ts:%Y-%m-%d %H:%M}|{text.strip()}".encode()).hexdigest()[:16]


def add_raw(db, chat_key, msgs, source):
    """Insert parsed messages ({ts, text}); returns how many were new."""
    before = db.total_changes
    db.executemany("INSERT OR IGNORE INTO raw VALUES (?,?,?,?,?)",
                   [(_raw_id(chat_key, m["ts"], m["text"]), chat_key, m["ts"].isoformat(), m["text"], source)
                    for m in msgs])
    return db.total_changes - before


def rebuild(db):
    """Recompute tags/flags/duplicates over every stored message and refresh the search index."""
    rows = db.execute("SELECT id, chat_key, ts, text FROM raw").fetchall()
    items = []
    for r in rows:
        if r["chat_key"] not in wd.CHATS:
            continue
        it = wd.classify({"ts": datetime.fromisoformat(r["ts"]), "text": r["text"]}, r["chat_key"])
        it["id"] = r["id"]
        items.append(it)
    items.sort(key=lambda x: x["date"])
    wd.mark_duplicates(items)
    titles = {r["url"]: r["title"] or "" for r in db.execute("SELECT url, title FROM links")}
    db.execute("DELETE FROM notes")
    db.execute("DELETE FROM notes_fts")
    for it in items:
        db.execute("INSERT INTO notes VALUES (?,?,?,?,?,?,?,?)",
                   (it["id"], it["chat"], it["date"], it["note"], json.dumps(it["tags"]), it["kind"],
                    json.dumps(it["flags"]), json.dumps(it["urls"])))
        body = " ".join([it["note"], " ".join(it["tags"])] + [titles.get(u, "") for u in it["urls"]])
        db.execute("INSERT INTO notes_fts VALUES (?,?)", (it["id"], body))
    db.execute("INSERT OR REPLACE INTO meta VALUES ('last_ingest', ?)", (datetime.now().isoformat(),))
    db.commit()
    return items


def load_items(db):
    return [{"id": r["id"], "chat": r["chat"], "date": r["date"], "note": r["note"], "tags": json.loads(r["tags"]),
             "kind": r["kind"], "flags": json.loads(r["flags"]), "urls": json.loads(r["urls"])}
            for r in db.execute("SELECT * FROM notes ORDER BY date")]


# ── Sources ────────────────────────────────────────────────────────────────────

def ingest_exports(db, paths):
    new = 0
    for title, text in wd._load_sources(paths):
        key = wd._chat_key(title)
        if not key:
            print(f"  ⚠ '{title}': no empieza con Psi / Ide / Vida, salteado")
            continue
        msgs = wd.parse_chat(text)
        if not msgs and text.strip():
            print(f"  ⚠ '{title}': 0 mensajes leídos — ¿cambió el formato del export?")
        n = add_raw(db, key, msgs, "export")
        new += n
        print(f"  ✓ {title}: {len(msgs)} mensajes, {n} nuevos")
    return new


def _bridge_ts(value):
    # go-sqlite3 stores time.Time as "2026-09-27 15:04:05.123-03:00" (or with a T); keep the local wall time.
    m = re.match(r"(\d{4}-\d{2}-\d{2})[ T](\d{2}:\d{2}:\d{2})", str(value))
    return datetime.fromisoformat(f"{m.group(1)} {m.group(2)}") if m else None


def ingest_bridge(db, bridge_path):
    """Read only MY messages from the 3 note chats in the bridge DB (read-only connection)."""
    src = sqlite3.connect(f"file:{bridge_path}?mode=ro", uri=True)
    rows = src.execute("""SELECT c.name, m.timestamp, m.content FROM messages m
                          JOIN chats c ON c.jid = m.chat_jid
                          WHERE m.is_from_me = 1 AND m.content IS NOT NULL AND m.content != ''""").fetchall()
    src.close()
    by_chat = {}
    for name, ts, content in rows:
        key = wd._chat_key(name or "")
        ts = _bridge_ts(ts)
        if key and ts:
            by_chat.setdefault(key, []).append({"ts": ts, "text": content})
    new = sum(add_raw(db, k, msgs, "bridge") for k, msgs in by_chat.items())
    return new


def bridge_path():
    return Path(os.environ.get("WHATSAPP_BRIDGE_DB", DEFAULT_BRIDGE)).expanduser()


def refresh_from_bridge(db):
    """Re-ingest only if the bridge DB changed since the last ingest. Cheap enough to call on every query."""
    p = bridge_path()
    if not p.exists():
        return False
    last = db.execute("SELECT v FROM meta WHERE k='bridge_mtime'").fetchone()
    mtime = str(p.stat().st_mtime)
    if last and last["v"] == mtime:
        return False
    ingest_bridge(db, p)
    db.execute("INSERT OR REPLACE INTO meta VALUES ('bridge_mtime', ?)", (mtime,))
    rebuild(db)
    return True


# ── Queries ────────────────────────────────────────────────────────────────────

def search(db, query, limit=10):
    terms = [t for t in re.findall(r"\w+", query.lower()) if len(t) > 1]
    if not terms:
        return []
    fts_q = " OR ".join(f'"{t}"*' for t in terms)
    rows = db.execute("""SELECT n.* FROM notes_fts f JOIN notes n ON n.id = f.id
                         WHERE notes_fts MATCH ? ORDER BY bm25(notes_fts) LIMIT ?""", (fts_q, limit)).fetchall()
    return [dict(r) for r in rows]


def notion_done():
    """Task keys / titles already marked done in Notion (via tools/notion_sync.py)."""
    if not NOTION_STATE.exists():
        return set()
    state = json.loads(NOTION_STATE.read_text(encoding="utf-8"))
    return {k for k, v in state.get("tasks", {}).items() if v.get("done")}


def pending(db):
    done = notion_done()
    return [p for p in wd.pending_items(load_items(db)) if p["key"] not in done]


def propose(db, days=7, today=None):
    """Rule-based proposals. Deterministic and free; --llm adds Claude on top."""
    today = today or datetime.now()
    since = (today - timedelta(days=days)).strftime("%Y-%m-%d")
    items = load_items(db)
    recent = [i for i in items if i["date"] >= since]
    pend = pending(db)
    out = []
    span = "esta semana" if days == 7 else f"en los últimos {days} días"

    stale = [p for p in pend if p["date"] < (today - timedelta(days=STALE_DAYS)).strftime("%Y-%m-%d")]
    if stale:
        top = ", ".join(p["title"][:40] for p in stale[:5])
        out.append(f"🕰️ {len(stale)} tareas con más de {STALE_DAYS} días abiertas. Hacelas o borralas: {top}")

    counts = Counter(wd.task_key(i["note"].splitlines()[0][:120]) for i in items if i["kind"] == "task")
    repeated = [p for p in pend if counts[p["key"]] >= 2]
    for p in repeated[:3]:
        out.append(f"🔁 «{p['title'][:60]}» lo anotaste {counts[p['key']]} veces: pasalo a 🔴 Ahora o soltalo.")

    misplaced = [i for i in recent if "fuera_de_lugar" in i["flags"]]
    if misplaced:
        out.append(f"📦 {len(misplaced)} notas {span} están en el chat equivocado "
                   f"(ej: «{misplaced[0]['note'].splitlines()[0][:50]}» en {misplaced[0]['chat']}).")

    bare = [i for i in recent if "link_sin_nota" in i["flags"]]
    if bare:
        doms = Counter(re.sub(r"^https?://(www\.)?([^/]+).*", r"\2", i["urls"][0]) for i in bare)
        out.append(f"🔗 {len(bare)} links sin nota {span} ({', '.join(f'{d} {n}' for d, n in doms.most_common(3))}). "
                   "Mirá .tmp/notes_rag/links.md (agrupados por tema) y decidí cuáles quedan.")

    late = [i for i in recent if "madrugada" in i["flags"]]
    late_psi = [i for i in late if i["chat"].startswith("Psi")]
    if len(late) >= 3:
        msg = f"🌙 {len(late)} notas entre las 0 y las 6 AM {span}"
        if len(late_psi) >= 2:
            msg += f", {len(late_psi)} en Psi: vale llevarlo a terapia (rumia nocturna)"
        out.append(msg + ".")

    tags = Counter(t for i in recent for t in i["tags"])
    if tags:
        out.append(f"📊 {span.capitalize()} anotaste sobre todo: " + ", ".join(f"{t} {n}" for t, n in tags.most_common(3)) + ".")

    if not recent:
        out.append(f"🤷 No hay notas en los últimos {days} días. ¿Está corriendo el bridge o falta exportar?")
    return out


def propose_llm(db, days=7):
    """Ask Claude for 5 concrete next actions (paid API call — only with --llm)."""
    from tools.claude_call import call_claude
    since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    recent = [i for i in load_items(db) if i["date"] >= since and i["note"]]
    ctx = "\n".join(f"[{i['chat']} {i['date']}] {i['note'][:200]}" for i in recent[-80:])
    tasks = "\n".join(f"- {p['title']} ({p['tag']}, {p['date'][:10]})" for p in pending(db)[:60])
    prompt = ("Sos mi asistente personal. Estas son mis notas de la última semana y mis pendientes.\n"
              "Proponé 5 acciones concretas para esta semana, en español rioplatense, una línea cada una, "
              "priorizando lo que se repite o lleva más tiempo abierto. Sin relleno.\n\n"
              f"NOTAS:\n{ctx}\n\nPENDIENTES:\n{tasks}")
    return call_claude(prompt, model="sonnet")


# ── CLI ────────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("ingest"); p.add_argument("inputs", nargs="*"); p.add_argument("--bridge", action="store_true")
    p = sub.add_parser("watch"); p.add_argument("--every", type=int, default=600)
    p = sub.add_parser("search"); p.add_argument("query"); p.add_argument("-n", type=int, default=10)
    sub.add_parser("pending")
    p = sub.add_parser("propose"); p.add_argument("--days", type=int, default=7); p.add_argument("--llm", action="store_true")
    args = ap.parse_args()

    wd.load_config()
    db = connect()

    if args.cmd == "ingest":
        new = ingest_exports(db, args.inputs) if args.inputs else 0
        if args.bridge:
            if not bridge_path().exists():
                sys.exit(f"No encuentro el bridge en {bridge_path()} (ver tools/whatsapp_bridge.sh)")
            new += ingest_bridge(db, bridge_path())
        items = rebuild(db)
        print(f"  → {new} mensajes nuevos · {len(items)} en total · {DB_PATH}")
    elif args.cmd == "watch":
        print(f"  Mirando {bridge_path()} cada {args.every}s (Ctrl+C para cortar)")
        while True:
            if refresh_from_bridge(db):
                print(f"  {datetime.now():%H:%M} actualizado")
            time.sleep(args.every)
    elif args.cmd == "search":
        refresh_from_bridge(db)
        for r in search(db, args.query, args.n):
            print(f"- [{r['chat']} {r['date']}] {' / '.join(r['note'].split(chr(10)))[:160] or r['urls']}")
    elif args.cmd == "pending":
        refresh_from_bridge(db)
        for p in pending(db):
            print(f"- [ ] {p['title']}  ({p['tag'] or 'sin tag'}, {p['chat']}, {p['date'][:10]})")
    elif args.cmd == "propose":
        refresh_from_bridge(db)
        for line in propose(db, args.days):
            print(line)
        if args.llm:
            print("\n🤖 Claude propone:\n" + propose_llm(db, args.days))


if __name__ == "__main__":
    main()
