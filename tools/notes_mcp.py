#!/usr/bin/env python3
"""
Read-only MCP server over the notes RAG (tools/notes_rag.py), so Claude Code can search and
reason over the Psi / Ide / Vida chats. Stdlib only (JSON-RPC 2.0 over stdio).

It can NOT send WhatsApp messages or change anything: every tool only reads.
Before each call it re-ingests from the WhatsApp bridge if the bridge DB changed.

Registered for this repo in .mcp.json. Manual test:
  printf '%s\n' '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | python3 tools/notes_mcp.py
"""
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from tools import notes_rag as rag

PROTOCOL = "2025-06-18"

TOOLS = [
    {"name": "buscar_notas",
     "description": "Busca en mis notas de WhatsApp (chats Psi, Ide, Vida) por palabras. Ignora acentos.",
     "inputSchema": {"type": "object", "properties": {
         "consulta": {"type": "string"}, "limite": {"type": "integer", "default": 10}}, "required": ["consulta"]}},
    {"name": "pendientes",
     "description": "Tareas abiertas (checklists + tareas sueltas), sin duplicados y sin las marcadas Hecho en Notion.",
     "inputSchema": {"type": "object", "properties": {"tag": {"type": "string", "description": "ej. #casa"}}}},
    {"name": "propuestas",
     "description": "Qué conviene hacer ahora: tareas viejas, repetidas, notas fuera de lugar, links sin nota, sueño.",
     "inputSchema": {"type": "object", "properties": {"dias": {"type": "integer", "default": 7}}}},
    {"name": "notas_recientes",
     "description": "Notas de los últimos N días, opcionalmente de un solo chat (Psi, Ide o Vida).",
     "inputSchema": {"type": "object", "properties": {
         "dias": {"type": "integer", "default": 7}, "chat": {"type": "string"}}}},
]


def _fmt(note):
    text = " / ".join(note["note"].splitlines())[:300] or " ".join(json.loads(note["urls"]) if isinstance(note["urls"], str) else note["urls"])
    return f"[{note['chat']} {note['date']}] {text}"


def call_tool(db, name, args):
    rag.refresh_from_bridge(db)
    if name == "buscar_notas":
        hits = rag.search(db, args["consulta"], int(args.get("limite", 10)))
        return "\n".join(_fmt(h) for h in hits) or "Sin resultados."
    if name == "pendientes":
        tag = args.get("tag")
        rows = [p for p in rag.pending(db) if not tag or p["tag"] == tag]
        return "\n".join(f"- {p['title']} ({p['tag'] or 'sin tag'}, {p['chat']}, {p['date'][:10]})" for p in rows) or "Nada pendiente."
    if name == "propuestas":
        return "\n".join(rag.propose(db, int(args.get("dias", 7))))
    if name == "notas_recientes":
        since = (datetime.now() - timedelta(days=int(args.get("dias", 7)))).strftime("%Y-%m-%d")
        chat = (args.get("chat") or "").lower()
        rows = [n for n in rag.load_items(db) if n["date"] >= since and n["chat"].lower().startswith(chat)]
        return "\n".join(_fmt(n) for n in rows) or "Sin notas en ese período."
    raise ValueError(f"Herramienta desconocida: {name}")


def handle(db, req):
    method, rid = req.get("method"), req.get("id")
    if method == "initialize":
        result = {"protocolVersion": req.get("params", {}).get("protocolVersion", PROTOCOL),
                  "capabilities": {"tools": {}}, "serverInfo": {"name": "notas", "version": "1.0"}}
    elif method == "tools/list":
        result = {"tools": TOOLS}
    elif method == "tools/call":
        p = req.get("params", {})
        try:
            text, err = call_tool(db, p.get("name"), p.get("arguments") or {}), False
        except Exception as e:  # report to the model instead of crashing the server
            text, err = f"Error: {e}", True
        result = {"content": [{"type": "text", "text": text}], "isError": err}
    elif method == "ping":
        result = {}
    elif rid is None:          # notifications (e.g. notifications/initialized) get no response
        return None
    else:
        return {"jsonrpc": "2.0", "id": rid, "error": {"code": -32601, "message": f"Method not found: {method}"}}
    return {"jsonrpc": "2.0", "id": rid, "result": result}


def main():
    rag.wd.load_config()
    db = rag.connect()
    for line in sys.stdin:
        if not line.strip():
            continue
        resp = handle(db, json.loads(line))
        if resp is not None:
            sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
