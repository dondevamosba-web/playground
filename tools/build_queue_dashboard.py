#!/usr/bin/env python3
"""
Build a single HTML page showing what is about to post on each of the six accounts.

Reads every account calendar, keeps the rows that have not gone out yet, and
writes a self-contained file — no server, no external assets, safe to open from
disk or send to someone.

Usage:
  python3 tools/build_queue_dashboard.py
  python3 tools/build_queue_dashboard.py --out C:/tmp/queue.html --limit 40
"""
import argparse
import html
import os
import re
import sys
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from tools.sheets_client import get_services

# Five calendars share a layout; Techno carries two extra columns before Caption,
# and Fiestas uses the approval Queue shape. Indices are 0-based into the row.
CALENDAR = {"date": 0, "time": 1, "kind": 4, "caption": 5, "tags": 6,
            "media": 7, "status": 8, "post_id": 9}
TECHNO   = {"date": 0, "time": 1, "kind": 5, "caption": 6, "tags": 7,
            "media": 8, "status": 9, "post_id": 10}
FIESTAS  = {"date": 3, "time": None, "kind": 1, "caption": 7, "tags": None,
            "media": 9, "status": 11, "post_id": 12}

ACCOUNTS = [
    ("Fiestas",     "@fiestaselectronicasbuenosaires", "FIESTAS_APPROVAL_SHEET_ID",   "Queue",  FIESTAS),
    ("Techno",      "@techno.apple.ok",                "TECHNO_CONTENT_CALENDAR_SHEET_ID", None, TECHNO),
    ("Ola Digital", "@oladigitalok",                   "CONTENT_CALENDAR_SHEET_ID",   None,     CALENDAR),
    ("Ola Empleo",  "@olavarria.empleo",               "OLA_EMPLEO_CALENDAR_SHEET_ID", None,    CALENDAR),
    ("Talento USA", "@talento.remoto.usa",             "TALENTO_USA_CALENDAR_SHEET_ID", None,   CALENDAR),
    ("Storm",       "@storm.mkt.agency",               "STORM_CONTENT_CALENDAR_SHEET_ID", None, CALENDAR),
]

DRIVE_ID = re.compile(r"[?&]id=([A-Za-z0-9_-]+)|/d/([A-Za-z0-9_-]+)")


def cell(row, idx):
    if idx is None or idx >= len(row):
        return ""
    return (row[idx] or "").strip()


def thumb(url: str) -> str:
    """Drive download links do not render in an img tag; the thumbnail host does."""
    if not url:
        return ""
    if url.startswith("VIDEO:"):
        url = url[6:].strip()
    m = DRIVE_ID.search(url) if "drive.google.com" in url else None
    if m:
        return f"https://drive.google.com/thumbnail?id={m.group(1) or m.group(2)}&sz=w400"
    return url


def read_account(sheets, name, handle, env, tab, cols, limit):
    sid = os.environ.get(env)
    if not sid:
        return {"name": name, "handle": handle, "error": f"falta {env} en .env", "rows": []}
    try:
        if tab is None:
            meta = sheets.spreadsheets().get(spreadsheetId=sid).execute()
            tab = meta["sheets"][0]["properties"]["title"]
        values = sheets.spreadsheets().values().get(
            spreadsheetId=sid, range=f"{tab}!A2:N1000").execute().get("values", [])
    except Exception as e:
        return {"name": name, "handle": handle, "error": str(e)[:160], "rows": []}

    today = date.today().isoformat()
    pending, posted = [], 0
    for r in values:
        status = cell(r, cols["status"]).lower()
        if cell(r, cols["post_id"]) or status == "posted":
            posted += 1
            continue
        caption = cell(r, cols["caption"])
        if not caption:
            continue
        when = cell(r, cols["date"])
        pending.append({
            "date":    when,
            "time":    cell(r, cols["time"]),
            "kind":    cell(r, cols["kind"]),
            "caption": caption,
            "tags":    cell(r, cols["tags"]),
            "thumb":   thumb(cell(r, cols["media"])),
            "status":  status or "—",
            "past":    bool(when) and when < today,
        })

    pending.sort(key=lambda p: (p["date"] or "9999", p["time"] or ""))
    return {"name": name, "handle": handle, "error": None,
            "posted": posted, "total": len(pending), "rows": pending[:limit]}


def render(accounts, limit) -> str:
    gen = datetime.now().strftime("%d/%m/%Y %H:%M")
    total = sum(a.get("total", 0) for a in accounts)
    out = [f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cola de publicación — 6 cuentas</title>
<style>
  :root {{
    --bg:#f6f6f7; --card:#fff; --ink:#16161a; --muted:#6b6b76;
    --line:#e3e3e8; --accent:#d6003c; --warn:#b26a00; --ok:#1a7f4b;
  }}
  @media (prefers-color-scheme: dark) {{
    :root {{ --bg:#0e0e11; --card:#18181d; --ink:#f0f0f4; --muted:#9a9aa6;
             --line:#2a2a33; --accent:#ff3d6e; --warn:#e2a13c; --ok:#4ade80; }}
  }}
  * {{ box-sizing:border-box }}
  body {{ margin:0; padding:28px 20px 60px; background:var(--bg); color:var(--ink);
    font:15px/1.5 -apple-system,Segoe UI,Roboto,sans-serif; }}
  header {{ max-width:1100px; margin:0 auto 28px }}
  h1 {{ font-size:26px; margin:0 0 6px; letter-spacing:-.02em }}
  .sub {{ color:var(--muted); font-size:13px }}
  main {{ max-width:1100px; margin:0 auto; display:flex; flex-direction:column; gap:22px }}
  section {{ background:var(--card); border:1px solid var(--line); border-radius:12px; overflow:hidden }}
  .head {{ display:flex; align-items:baseline; gap:10px; flex-wrap:wrap;
    padding:14px 18px; border-bottom:1px solid var(--line) }}
  .head h2 {{ font-size:17px; margin:0 }}
  .handle {{ color:var(--muted); font-size:13px }}
  .count {{ margin-left:auto; font-size:13px; color:var(--muted) }}
  .count b {{ color:var(--accent); font-size:15px }}
  .empty {{ padding:18px; color:var(--muted); font-size:14px }}
  .err {{ padding:18px; color:var(--warn); font-size:14px }}
  .wrap {{ overflow-x:auto }}
  table {{ width:100%; border-collapse:collapse; min-width:640px }}
  td {{ padding:11px 14px; border-top:1px solid var(--line); vertical-align:top }}
  tr:first-child td {{ border-top:none }}
  .th {{ width:78px }}
  .th img {{ width:64px; height:64px; object-fit:cover; border-radius:7px;
    background:var(--line); display:block }}
  .noimg {{ width:64px; height:64px; border-radius:7px; background:var(--line);
    display:grid; place-items:center; color:var(--muted); font-size:11px }}
  .when {{ width:112px; white-space:nowrap; font-variant-numeric:tabular-nums; font-size:13px }}
  .when small {{ display:block; color:var(--muted) }}
  .cap {{ font-size:14px; white-space:pre-wrap }}
  .tags {{ color:var(--muted); font-size:12px; margin-top:5px }}
  .kind {{ color:var(--muted); font-size:12px; margin-bottom:3px }}
  .st {{ width:96px; text-align:right }}
  .pill {{ display:inline-block; padding:2px 9px; border-radius:99px;
    font-size:11px; border:1px solid var(--line); color:var(--muted); white-space:nowrap }}
  .pill.pending {{ color:var(--warn); border-color:currentColor }}
  .pill.approved {{ color:var(--ok); border-color:currentColor }}
  .late {{ color:var(--accent); font-weight:600 }}
  footer {{ max-width:1100px; margin:26px auto 0; color:var(--muted); font-size:12px }}
</style></head><body>
<header>
  <h1>Cola de publicación</h1>
  <div class="sub">{total} posts sin publicar en 6 cuentas · generado {gen}
    · mostrando hasta {limit} por cuenta</div>
</header><main>"""]

    for a in accounts:
        out.append('<section><div class="head">'
                   f'<h2>{html.escape(a["name"])}</h2>'
                   f'<span class="handle">{html.escape(a["handle"])}</span>')
        if a["error"]:
            out.append('</div><div class="err">⚠ ' + html.escape(a["error"]) + "</div></section>")
            continue
        out.append(f'<span class="count"><b>{a["total"]}</b> en cola · '
                   f'{a["posted"]} publicados</span></div>')
        if not a["rows"]:
            out.append('<div class="empty">Nada pendiente.</div></section>')
            continue

        out.append('<div class="wrap"><table>')
        for r in a["rows"]:
            img = (f'<img src="{html.escape(r["thumb"])}" alt="" loading="lazy">'
                   if r["thumb"] else '<div class="noimg">sin<br>img</div>')
            when = html.escape(r["date"] or "sin fecha")
            if r["past"]:
                when = f'<span class="late">{when}</span>'
            time_s = f'<small>{html.escape(r["time"])}</small>' if r["time"] else ""
            kind = f'<div class="kind">{html.escape(r["kind"])}</div>' if r["kind"] else ""
            tags = f'<div class="tags">{html.escape(r["tags"])}</div>' if r["tags"] else ""
            cap = html.escape(r["caption"][:300]) + ("…" if len(r["caption"]) > 300 else "")
            cls = r["status"] if r["status"] in ("pending", "approved") else ""
            out.append(
                f'<tr><td class="th">{img}</td>'
                f'<td class="when">{when}{time_s}</td>'
                f'<td>{kind}<div class="cap">{cap}</div>{tags}</td>'
                f'<td class="st"><span class="pill {cls}">{html.escape(r["status"])}</span></td></tr>')
        out.append("</table></div></section>")

    out.append('</main><footer>Las fechas en rojo ya pasaron. '
               '"pending" espera aprobación; "approved" sale en la próxima corrida '
               'de publish_one_each (11:00, 15:00 y 18:00 AR).</footer></body></html>')
    return "\n".join(out)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", default=str(ROOT / ".tmp" / "queue_dashboard.html"))
    p.add_argument("--limit", type=int, default=25, help="Filas por cuenta")
    args = p.parse_args()

    sheets, _ = get_services()
    accounts = []
    for name, handle, env, tab, cols in ACCOUNTS:
        a = read_account(sheets, name, handle, env, tab, cols, args.limit)
        accounts.append(a)
        if a["error"]:
            print(f"  {name}: ERROR {a['error']}")
        else:
            print(f"  {name}: {a['total']} en cola, {a['posted']} publicados")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(accounts, args.limit), encoding="utf-8")
    print(f"\n-> {out}")


if __name__ == "__main__":
    main()
