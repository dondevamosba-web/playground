#!/usr/bin/env python3
"""
Tiny localhost server so the preview HTML can approve/skip posts with a click.

Endpoints (GET, localhost only):
  /approve?sheet=KEY&row=N        → status col = approved
  /skip?sheet=KEY&row=N           → status col = skipped
  /use-image?sheet=techno&row=N   → copy candidate image (col L) to media (col I)
  /health                         → ok

Sheet keys map to the calendars below. Runs permanently via launchd KeepAlive
on port 8765. Never exposed beyond 127.0.0.1.
"""
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from tools.sheets_client import get_services

PORT = 8765

# key: (env var, range prefix, status col letter, media col letter or None)
SHEETS = {
    "fiestas-queue":   ("FIESTAS_APPROVAL_SHEET_ID", "Queue!", "L", None),
    "unified-fiestas": ("UNIFIED_APPROVAL_SHEET_ID", "'Fiestas'!", "E", None),
    "ola":             ("CONTENT_CALENDAR_SHEET_ID", "", "I", "H"),
    "storm":           ("STORM_CONTENT_CALENDAR_SHEET_ID", "", "I", "H"),
    "techno":          ("TECHNO_CONTENT_CALENDAR_SHEET_ID", "", "J", "I"),
    "empleo":          ("OLA_EMPLEO_CALENDAR_SHEET_ID", "", "I", "H"),
    "talento":         ("TALENTO_USA_CALENDAR_SHEET_ID", "", "I", "H"),
}

_services = {}


def sheets_svc():
    if "s" not in _services:
        _services["s"], _ = get_services()
    return _services["s"]


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(f"{self.address_string()} {fmt % args}")

    def reply(self, code, msg):
        body = json.dumps({"ok": code == 200, "msg": msg}).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")  # file:// previews
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        u = urlparse(self.path)
        q = {k: v[0] for k, v in parse_qs(u.query).items()}
        try:
            if u.path == "/health":
                return self.reply(200, "ok")
            key, row = q.get("sheet", ""), q.get("row", "")
            if key not in SHEETS or not row.isdigit():
                return self.reply(400, "sheet o row inválidos")
            env, prefix, st_col, media_col = SHEETS[key]
            sid = os.environ[env]
            svc = sheets_svc()
            if u.path in ("/approve", "/skip"):
                val = "approved" if u.path == "/approve" else "skipped"
                svc.spreadsheets().values().update(
                    spreadsheetId=sid, range=f"{prefix}{st_col}{row}",
                    valueInputOption="RAW", body={"values": [[val]]}).execute()
                return self.reply(200, f"fila {row} → {val}")
            if u.path == "/use-image":
                if not media_col:
                    return self.reply(400, "sheet sin columna de media")
                cand = svc.spreadsheets().values().get(
                    spreadsheetId=sid, range=f"{prefix}L{row}").execute().get("values", [[""]])[0][0]
                if not cand.strip():
                    return self.reply(400, "sin candidata en col L")
                svc.spreadsheets().values().update(
                    spreadsheetId=sid, range=f"{prefix}{media_col}{row}",
                    valueInputOption="RAW", body={"values": [[cand]]}).execute()
                return self.reply(200, f"fila {row}: imagen candidata aplicada")
            return self.reply(404, "endpoint desconocido")
        except Exception as e:
            return self.reply(500, str(e)[:200])


def main():
    srv = HTTPServer(("127.0.0.1", PORT), Handler)
    print(f"approval server en http://127.0.0.1:{PORT}")
    srv.serve_forever()


if __name__ == "__main__":
    main()
