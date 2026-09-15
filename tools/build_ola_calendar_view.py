#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build a visual HTML calendar of everything pending/approved in the Ola Digital
Content Calendar (Google Sheet), with an embedded thumbnail per post so you can
see what's about to go out, not just read captions.

Usage:
  python3 tools/build_ola_calendar_view.py

Writes workflows/ola-digital/calendar_view.html. Open it locally, or hand it to
Claude Code to republish as an Artifact.

Flags duplicate image usage, broken/placeholder captions (from failed Haiku
calls), and overdue rows (date already passed) so review is fast.
"""
import base64
import html
import io
import json
import os
import sys
from collections import defaultdict, Counter
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from PIL import Image
from tools.sheets_client import get_services

SHEET_ID = os.getenv("CONTENT_CALENDAR_SHEET_ID")
FONT_PATH = ROOT / "workflows/ola-digital/posts-señal-v2/fonts/Inter-Variable.woff2"
THUMB_CACHE = ROOT / "workflows/ola-digital/.thumb_cache.json"
OUT_PATH = ROOT / "workflows/ola-digital/calendar_view.html"

BROKEN_MARKERS = ["Necesito ", "Me falta ", "¿Cuál es", "no puedo escribir", "para escribir un caption"]

DOW_ES = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
MONTH_ES = ["", "enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
            "septiembre", "octubre", "noviembre", "diciembre"]


def esc(s):
    return html.escape(s, quote=True)


def parse_date(s):
    y, m, d = map(int, s.split("-"))
    return date(y, m, d)


def week_start(d):
    return d - timedelta(days=d.weekday())


def fmt_date_short(d):
    return f"{d.day:02d} {MONTH_ES[d.month][:3]}"


def source_label(media_url):
    if "posts-señal-v2" in media_url:
        return "Señal"
    if ".tmp/ola_digital_posts_v2" in media_url:
        return "Pool 16"
    return "Otro"


def status_pill(r):
    if r["is_broken"]:
        return '<span class="pill pill-broken">caption roto</span>'
    if r["status"] == "approved":
        return '<span class="pill pill-approved">aprobado</span>'
    return '<span class="pill pill-pending">pendiente</span>'


def load_rows():
    sheets, _ = get_services()
    raw = sheets.spreadsheets().values().get(
        spreadsheetId=SHEET_ID, range="A2:J2000"
    ).execute().get("values", [])
    today = date.today()
    rows = []
    for r in raw:
        r = r + [""] * (10 - len(r))
        status = r[8]
        if status not in ("pending", "approved"):
            continue
        d = parse_date(r[0])
        rows.append({
            "date": r[0], "time": r[1], "day": r[2], "content_type": r[3],
            "post_type": r[4], "caption": r[5], "hashtags": r[6],
            "media_url": r[7], "status": status, "post_id": r[9],
            "is_past": d < today,
            "is_broken": any(m in r[5] for m in BROKEN_MARKERS),
        })
    rows.sort(key=lambda o: (o["date"], o["time"]))
    return rows, today


def load_thumbs(media_urls):
    cache = {}
    if THUMB_CACHE.exists():
        cache = json.loads(THUMB_CACHE.read_text(encoding="utf-8"))
    changed = False
    for u in media_urls:
        if u in cache:
            continue
        p = ROOT / u
        if not p.exists():
            continue
        im = Image.open(p).convert("RGB")
        im.thumbnail((480, 480), Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, format="JPEG", quality=78)
        cache[u] = base64.b64encode(buf.getvalue()).decode("ascii")
        changed = True
    if changed:
        THUMB_CACHE.write_text(json.dumps(cache), encoding="utf-8")
    return cache


def main():
    rows, today = load_rows()
    uniq_media = sorted(set(r["media_url"] for r in rows))
    thumbs = load_thumbs(uniq_media)

    def thumb_src(media_url):
        b64 = thumbs.get(media_url)
        return f"data:image/jpeg;base64,{b64}" if b64 else ""

    inter_b64 = base64.b64encode(FONT_PATH.read_bytes()).decode("ascii") if FONT_PATH.exists() else ""

    weeks = defaultdict(list)
    for r in rows:
        weeks[week_start(parse_date(r["date"]))].append(r)
    sorted_weeks = sorted(weeks.keys())

    total = len(rows)
    overdue = [r for r in rows if r["is_past"]]
    broken = [r for r in rows if r["is_broken"]]
    approved = [r for r in rows if r["status"] == "approved"]
    pending = [r for r in rows if r["status"] == "pending"]
    senal = [r for r in rows if "posts-señal-v2" in r["media_url"]]

    dup_counts = Counter(r["media_url"] for r in rows)
    dup_images = sum(1 for u, n in dup_counts.items() if n > 1 and ".tmp/ola_digital_posts_v2" in u)

    week_html_parts = []
    for wk in sorted_weeks:
        wk_end = wk + timedelta(days=6)
        wk_rows = weeks[wk]
        wk_overdue = sum(1 for r in wk_rows if r["is_past"])
        label = f"Semana del {fmt_date_short(wk)} al {fmt_date_short(wk_end)}"
        if wk_end < today:
            badge = '<span class="week-badge week-badge-past">ya pasó — sin postear</span>'
        elif wk <= today <= wk_end:
            badge = '<span class="week-badge week-badge-now">esta semana</span>'
        else:
            badge = ""

        day_cards = []
        for r in wk_rows:
            d = parse_date(r["date"])
            dow = DOW_ES[d.weekday()]
            past_cls = " card-past" if r["is_past"] else ""
            broken_cls = " card-broken" if r["is_broken"] else ""
            caption_full = r["caption"]
            media_name = r["media_url"].rsplit("/", 1)[-1]
            thumb = thumb_src(r["media_url"])
            thumb_img = f'<img class="thumb" src="{thumb}" alt="" loading="lazy">' if thumb else '<div class="thumb thumb-missing"></div>'
            day_cards.append(f"""
        <details class="card{past_cls}{broken_cls}">
          <summary>
            {thumb_img}
            <div class="card-info">
              <div class="card-toprow">
                {status_pill(r)}
                <span class="pill pill-source">{esc(source_label(r['media_url']))}</span>
              </div>
              <div class="card-when-line">
                <span class="card-dow">{esc(dow)} {fmt_date_short(d)}</span>
                <span class="card-time">{esc(r['time'])}</span>
              </div>
              <div class="card-content-type">{esc(r['content_type'])}</div>
            </div>
          </summary>
          <div class="card-body">
            <div class="card-caption">{esc(caption_full)}</div>
            <div class="card-meta">
              <span>{esc(media_name)}</span>
              <span>·</span>
              <span>{esc(r['post_type'])}</span>
            </div>
          </div>
        </details>""")

        week_html_parts.append(f"""
    <section class="week">
      <div class="week-head">
        <h2>{esc(label)}</h2>
        {badge}
        <span class="week-count">{len(wk_rows)} post{'s' if len(wk_rows) != 1 else ''}{f' · {wk_overdue} atrasado{"s" if wk_overdue != 1 else ""}' if wk_overdue else ''}</span>
      </div>
      <div class="cards">
        {''.join(day_cards)}
      </div>
    </section>""")

    weeks_html = "\n".join(week_html_parts)
    today_str = today.strftime("%d/%m")

    HTML = f"""<title>Ola Digital — calendario de posteo</title>
<style>
@font-face {{
  font-family: 'Inter';
  src: url(data:font/woff2;base64,{inter_b64}) format('woff2-variations'),
       url(data:font/woff2;base64,{inter_b64}) format('woff2');
  font-weight: 100 900;
}}

:root {{
  --bg: #f4f6fa; --panel: #ffffff; --panel-2: #eef1f7; --ink: #0f172a;
  --muted: #5b6478; --muted-2: #8992a5; --line: rgba(15,23,42,0.10);
  --blue: #0EA5E9; --blue-ink: #0369a1; --orange: #F97316;
  --ok-bg: #dcf7e3; --ok-ink: #16803c;
  --pending-bg: #fef3d6; --pending-ink: #92620a;
  --broken-bg: #fde0e0; --broken-ink: #b91c1c;
  --source-bg: #e6effc; --source-ink: #1d4ed8;
  --past-tint: rgba(244,63,94,0.06);
}}

@media (prefers-color-scheme: dark) {{
  :root {{
    --bg: #0b1220; --panel: #121a2b; --panel-2: #172033; --ink: #eef2f8;
    --muted: #9aa4b8; --muted-2: #6b7690; --line: rgba(255,255,255,0.10);
    --blue: #38bdf8; --blue-ink: #7dd3fc; --orange: #fb923c;
    --ok-bg: rgba(34,197,94,0.16); --ok-ink: #4ade80;
    --pending-bg: rgba(245,158,11,0.16); --pending-ink: #fbbf24;
    --broken-bg: rgba(244,63,94,0.18); --broken-ink: #fb7185;
    --source-bg: rgba(14,165,233,0.14); --source-ink: #67c9f5;
    --past-tint: rgba(244,63,94,0.08);
  }}
}}
:root[data-theme="light"] {{
  --bg: #f4f6fa; --panel: #ffffff; --panel-2: #eef1f7; --ink: #0f172a;
  --muted: #5b6478; --muted-2: #8992a5; --line: rgba(15,23,42,0.10);
  --blue: #0EA5E9; --blue-ink: #0369a1; --orange: #F97316;
  --ok-bg: #dcf7e3; --ok-ink: #16803c; --pending-bg: #fef3d6; --pending-ink: #92620a;
  --broken-bg: #fde0e0; --broken-ink: #b91c1c; --source-bg: #e6effc; --source-ink: #1d4ed8;
  --past-tint: rgba(244,63,94,0.06);
}}

* {{ box-sizing: border-box; }}
body {{
  margin: 0; background: var(--bg); color: var(--ink);
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  font-feature-settings: 'ss01','cv11';
  -webkit-font-smoothing: antialiased;
}}

.wrap {{ max-width: 880px; margin: 0 auto; padding: 40px 24px 100px; }}

.header {{ display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; flex-wrap: wrap; gap: 12px; }}
.wordmark {{ display: flex; align-items: center; gap: 10px; font-weight: 800; font-size: 15px; letter-spacing: 0.14em; text-transform: uppercase; color: var(--muted); }}
.wordmark .dot {{ width: 9px; height: 9px; border-radius: 50%; background: var(--blue); box-shadow: 0 0 0 3px rgba(14,165,233,0.18); }}
h1 {{ font-size: 34px; font-weight: 900; letter-spacing: -0.02em; margin: 4px 0 22px; text-wrap: balance; }}

.stats {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; margin-bottom: 32px; }}
@media (max-width: 700px) {{ .stats {{ grid-template-columns: repeat(2, 1fr); }} }}
.stat {{ background: var(--panel); border: 1px solid var(--line); border-radius: 14px; padding: 16px; }}
.stat .num {{ font-size: 28px; font-weight: 900; letter-spacing: -0.02em; font-variant-numeric: tabular-nums; }}
.stat .lbl {{ font-size: 12.5px; color: var(--muted); font-weight: 600; margin-top: 2px; }}
.stat.warn .num {{ color: var(--broken-ink); }}
.stat.pastwarn .num {{ color: var(--pending-ink); }}

.alert {{ background: var(--broken-bg); border: 1px solid rgba(244,63,94,0.3); color: var(--broken-ink);
  border-radius: 14px; padding: 16px 18px; margin-bottom: 14px; font-size: 14.5px; line-height: 1.5; }}
.alert strong {{ font-weight: 800; }}
.alert-ok {{ background: var(--ok-bg); border-color: rgba(34,197,94,0.3); color: var(--ok-ink); }}
.alert:last-of-type {{ margin-bottom: 32px; }}

.week {{ margin-bottom: 36px; }}
.week-head {{ display: flex; align-items: baseline; gap: 10px; flex-wrap: wrap; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid var(--line); }}
.week-head h2 {{ font-size: 16px; font-weight: 800; margin: 0; letter-spacing: -0.01em; }}
.week-count {{ font-size: 12.5px; color: var(--muted-2); margin-left: auto; font-weight: 600; }}
.week-badge {{ font-size: 11px; font-weight: 700; letter-spacing: 0.04em; text-transform: uppercase; padding: 3px 9px; border-radius: 999px; }}
.week-badge-past {{ background: var(--broken-bg); color: var(--broken-ink); }}
.week-badge-now {{ background: var(--source-bg); color: var(--source-ink); }}

.cards {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(190px, 1fr)); gap: 16px; }}
.card {{ background: var(--panel); border: 1px solid var(--line); border-radius: 14px; overflow: hidden; }}
.card[open] {{ box-shadow: 0 4px 16px rgba(15,23,42,0.10); grid-column: span 1; }}
.card.card-past {{ box-shadow: inset 0 0 0 2px var(--pending-ink); }}
.card.card-broken {{ box-shadow: inset 0 0 0 2px var(--broken-ink); }}

.card summary {{ cursor: pointer; list-style: none; display: block; }}
.card summary::-webkit-details-marker {{ display: none; }}

.thumb {{ width: 100%; aspect-ratio: 1 / 1; object-fit: cover; display: block; background: var(--panel-2); }}
.thumb-missing {{ background: var(--panel-2); }}

.card-info {{ padding: 10px 12px 12px; }}
.card-toprow {{ display: flex; gap: 5px; margin-bottom: 7px; flex-wrap: wrap; }}
.pill {{ font-size: 10.5px; font-weight: 700; padding: 3px 8px; border-radius: 999px; letter-spacing: 0.02em; }}
.pill-approved {{ background: var(--ok-bg); color: var(--ok-ink); }}
.pill-pending {{ background: var(--pending-bg); color: var(--pending-ink); }}
.pill-broken {{ background: var(--broken-bg); color: var(--broken-ink); }}
.pill-source {{ background: var(--source-bg); color: var(--source-ink); }}

.card-when-line {{ display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 3px; }}
.card-dow {{ font-size: 12.5px; font-weight: 800; font-variant-numeric: tabular-nums; }}
.card-time {{ font-size: 12px; color: var(--muted); font-variant-numeric: tabular-nums; }}

.card-content-type {{ font-size: 12px; color: var(--muted); line-height: 1.35; }}

.card-body {{ padding: 0 12px 14px; }}
.card-caption {{ white-space: pre-line; font-size: 13.5px; line-height: 1.5; color: var(--ink); background: var(--panel-2); border-radius: 10px; padding: 12px 14px; margin-bottom: 8px; }}
.card-meta {{ font-size: 11.5px; color: var(--muted-2); display: flex; gap: 8px; font-variant-numeric: tabular-nums; }}

@media (max-width: 480px) {{
  .cards {{ grid-template-columns: repeat(2, 1fr); }}
}}

footer {{ margin-top: 40px; font-size: 12.5px; color: var(--muted-2); text-align: center; }}
</style>

<div class="wrap">
  <div class="header"><div class="wordmark"><span class="dot"></span>OLA DIGITAL</div></div>
  <h1>Lo que se viene para postear</h1>

  <div class="stats">
    <div class="stat"><div class="num">{total}</div><div class="lbl">posts en cola</div></div>
    <div class="stat"><div class="num">{len(approved)}</div><div class="lbl">aprobados</div></div>
    <div class="stat"><div class="num">{len(pending)}</div><div class="lbl">pendientes</div></div>
    <div class="stat pastwarn"><div class="num">{len(overdue)}</div><div class="lbl">atrasados (fecha ya pasó)</div></div>
    <div class="stat warn"><div class="num">{len(broken)}</div><div class="lbl">con caption roto</div></div>
  </div>

  {"<div class='alert'><strong>Ojo:</strong> " + str(len(overdue)) + " posts tienen fecha anterior a hoy (" + today_str + "). Con todo aprobado y el cron diario corriendo, el auto-poster los va a ir publicando de a uno por día empezando por el más viejo hasta ponerse al día. Y " + str(len(broken)) + " tienen el caption roto (Claude Haiku pidió más contexto en vez de escribir texto) — están en rojo, no los apruebes así.</div>" if (overdue or broken) else ""}
  {"<div class='alert alert-ok'><strong>Repetidos:</strong> quedan " + str(dup_images) + " imágenes del pool viejo usadas más de una vez en la cola. Reemplazalas de a tandas con posters nuevos antes de aprobar esas filas.</div>" if dup_images else ""}
  {"<div class='alert alert-ok'><strong>Sin repetidos, sin captions rotos, todo aprobado.</strong> El cron <code>ola-digital-daily-post</code> corre todos los días a las 10:08 AM y publica el post más antiguo pendiente, así que el atraso se va a ir poniendo al día de a 1 por día.</div>" if not (overdue or broken or dup_images) else ""}

  {weeks_html}

  <footer>{total} filas · {len(senal)} de la serie Señal · generado desde el Content Calendar (Google Sheets)</footer>
</div>
"""

    OUT_PATH.write_text(HTML, encoding="utf-8")
    print(f"wrote {OUT_PATH} ({len(HTML)} chars, {total} rows, {len(uniq_media)} unique images)")


if __name__ == "__main__":
    main()
