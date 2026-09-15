#!/usr/bin/env python3
"""
Preview the next N unposted posts per account across all 6 Instagram queues
(Ola Digital, Storm, Techno, Fiestas, Empleo, Talento USA) as one HTML grid.

Reads the same calendar sheets the auto_post_* publishers use; shows rows with
status approved/pending and no post ID yet, in schedule order.

Usage:
  python3 tools/preview_next_posts.py               # 5 per account (30 total)
  python3 tools/preview_next_posts.py --per-account 8
Output: .tmp/preview_next_posts.html
"""
import argparse
import html
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from tools.sheets_client import get_services

AR_TZ = timezone(timedelta(hours=-3))

# account: (env key for sheet ID, range, column indexes {field: idx}, accent color)
SERVER_KEYS = {"Ola Digital": "ola", "Storm": "storm", "Techno": "techno",
               "Empleo": "empleo", "Talento USA": "talento", "Fiestas": "fiestas-queue"}

CALENDARS = {
    "Ola Digital": ("CONTENT_CALENDAR_SHEET_ID", "A2:J1000",
                    dict(date=0, time=1, content=3, type=4, caption=5, media=7, status=8, post_id=9), "#0ea5e9"),
    "Storm":       ("STORM_CONTENT_CALENDAR_SHEET_ID", "A2:J1000",
                    dict(date=0, time=1, content=3, type=4, caption=5, media=7, status=8, post_id=9), "#8b5cf6"),
    "Techno":      ("TECHNO_CONTENT_CALENDAR_SHEET_ID", "A2:L1000",
                    dict(date=0, time=1, content=3, type=5, caption=6, media=8, status=9, post_id=10, cand=11), "#22c55e"),
    "Empleo":      ("OLA_EMPLEO_CALENDAR_SHEET_ID", "A2:J1000",
                    dict(date=0, time=1, content=3, type=4, caption=5, media=7, status=8, post_id=9), "#f59e0b"),
    "Talento USA": ("TALENTO_USA_CALENDAR_SHEET_ID", "A2:J1000",
                    dict(date=0, time=1, content=3, type=4, caption=5, media=7, status=8, post_id=9), "#ef4444"),
}
# Fiestas uses its own Queue tab layout (see publish_one_each.run_fiestas)
FIESTAS = ("FIESTAS_APPROVAL_SHEET_ID", "Queue!A2:M500",
           dict(date=3, content=2, caption=7, media=9, status=11, post_id=12), "#ec4899")


def col(row, i):
    return row[i].strip() if i is not None and len(row) > i and row[i] else ""


def fetch_queue(sheets, account, env_key, rng, cols, limit):
    sheet_id = os.getenv(env_key, "")
    if not sheet_id:
        return [], f"{env_key} no está en .env"
    try:
        rows = sheets.spreadsheets().values().get(
            spreadsheetId=sheet_id, range=rng).execute().get("values", [])
    except Exception as e:
        return [], str(e)[:120]
    today = datetime.now(tz=AR_TZ).strftime("%Y-%m-%d")
    out = []
    for rownum, r in enumerate(rows, start=2):
        if col(r, cols["status"]).lower() not in ("approved", "pending"):
            continue
        if col(r, cols["post_id"]):
            continue
        date = col(r, cols.get("date"))
        if account == "Fiestas" and date and date < today:
            continue  # skip past events
        out.append({
            "row": rownum,
            "date": date, "time": col(r, cols.get("time")),
            "content": col(r, cols.get("content")),
            "type": col(r, cols.get("type")),
            "caption": col(r, cols["caption"]),
            "media": col(r, cols["media"]),
            "cand": col(r, cols.get("cand")),
            "status": col(r, cols["status"]).lower(),
        })
        # Scan further than `limit` so we can prioritize rows that already
        # have a real-photo candidate (see sort below) instead of just
        # taking the chronologically-first N, which were mostly the ones
        # missing a candidate.
        if len(out) >= limit * 20:
            break

    # Rows with a candidate image go first (stable sort keeps date order
    # within each group), then truncate to the requested limit.
    out.sort(key=lambda p: 0 if p.get("cand") else 1)
    out = out[:limit]
    return out, None


def resolve_media(media, drive):
    """Return the image as a base64 data URI (thumbnail), so the preview
    never depends on Drive auth, hotlink protection, or local paths."""
    import base64
    import io
    import re

    import requests
    from PIL import Image

    if not media:
        return ""
    raw = None
    m = re.search(r"drive\.google\.com/(?:uc\?[^\"]*id=|file/d/)([A-Za-z0-9_-]{10,})", media)
    try:
        if m:
            raw = drive.files().get_media(fileId=m.group(1)).execute()
        elif media.startswith(("http://", "https://")):
            r = requests.get(media, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            r.raise_for_status()
            raw = r.content
        else:
            p = ROOT / media
            if p.exists():
                raw = p.read_bytes()
    except Exception as e:
        print(f"  media fail ({media[:60]}…): {str(e)[:60]}")
        return ""
    if not raw:
        return ""
    try:
        img = Image.open(io.BytesIO(raw)).convert("RGB")
        img.thumbnail((800, 800), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=82)
        return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
    except Exception as e:
        print(f"  media decode fail ({media[:60]}…): {str(e)[:60]}")
        return ""


def card(account, color, p, n):
    cap = html.escape(p["caption"][:220]) + ("…" if len(p["caption"]) > 220 else "")
    title = html.escape(p["content"] or p["type"] or "(sin título)")
    when = " ".join(x for x in (p["date"], p["time"]) if x) or "sin fecha"
    media = p["media"]
    src = p.get("src", "")
    is_video = any(e in media.lower() for e in (".mp4", ".mov", "video"))
    if is_video and media:
        media_tag = f'<div class="nomedia">🎬 acá va el video viral de: {title}</div>'
    elif p.get("cand_src"):
        # Real product photo found — show it over the old generic template
        # image, since that's the whole point of sourcing it.
        media_tag = (f'<div class="candwrap"><img src="{html.escape(p["cand_src"])}" loading="lazy">'
                     f'<div class="candtag">FOTO REAL — confirmar</div></div>')
    elif src:
        media_tag = f'<img src="{html.escape(src)}" loading="lazy" onerror="this.outerHTML=\'<div class=nomedia>imagen no accesible</div>\'">'
    elif media:
        media_tag = '<div class="nomedia">imagen no accesible</div>'
    else:
        media_tag = '<div class="nomedia">sin media</div>'
    badge = "✅ approved" if p["status"] == "approved" else "⏳ pending"
    key = SERVER_KEYS.get(account, "")
    row = p.get("row", "")
    btns = ""
    if key and row and p["status"] == "pending":
        use = (f'<button class="ok" onclick="act(this,\'use-image\',\'{key}\',{row})">🖼 Usar esta imagen</button>'
               if p.get("cand_src") else "")
        btns = (f'<div class="btns">{use}'
                f'<button class="ok" onclick="act(this,\'approve\',\'{key}\',{row})">✓ Aprobar</button>'
                f'<button class="no" onclick="act(this,\'skip\',\'{key}\',{row})">✕ Saltear</button></div>')
    return f"""
    <div class="card">
      <div class="head" style="background:{color}"><span>{account} · #{n} · fila {row}</span><span>{badge}</span></div>
      {media_tag}
      <div class="body">
        <div class="title">{title}</div>
        <div class="when">📅 {when}</div>
        <div class="cap">{cap}</div>
        {btns}
      </div>
    </div>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-account", type=int, default=5)
    a = ap.parse_args()

    sheets, drive = get_services()
    sections, total = [], 0
    for account, (env_key, rng, cols, color) in {**CALENDARS, "Fiestas": FIESTAS}.items():
        posts, err = fetch_queue(sheets, account, env_key, rng, cols, a.per_account)
        if err:
            sections.append(f'<div class="err">⚠️ {account}: {html.escape(err)}</div>')
            continue
        if not posts:
            sections.append(f'<div class="err">⚠️ {account}: cola vacía — nada programado</div>')
            continue
        total += len(posts)
        for p in posts:
            p["src"] = resolve_media(p["media"], drive)
            if p.get("cand"):
                for cand_url in p["cand"].split(","):
                    cand_url = cand_url.strip()
                    if not cand_url:
                        continue
                    p["cand_src"] = resolve_media(cand_url, drive)
                    if p["cand_src"]:
                        break
        cards = "".join(card(account, color, p, i + 1) for i, p in enumerate(posts))
        sections.append(f'<h2 style="border-left:6px solid {color};padding-left:10px">{account} ({len(posts)})</h2><div class="grid">{cards}</div>')

    now = datetime.now(tz=AR_TZ).strftime("%Y-%m-%d %H:%M")
    doc = f"""<!DOCTYPE html><html lang="es"><head><meta charset="utf-8">
<title>Próximos posts — 6 cuentas</title>
<style>
  body{{font-family:-apple-system,sans-serif;background:#0f172a;color:#e2e8f0;margin:24px}}
  h1{{font-size:22px}} h2{{margin-top:32px}}
  .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:16px}}
  .card{{background:#1e293b;border-radius:12px;overflow:hidden;display:flex;flex-direction:column}}
  .head{{display:flex;justify-content:space-between;padding:6px 12px;font-size:12px;font-weight:700;color:#fff}}
  .card img{{width:100%;aspect-ratio:1;object-fit:cover;background:#334155}}
  .nomedia{{width:100%;aspect-ratio:1;display:flex;align-items:center;justify-content:center;background:#334155;color:#94a3b8}}
  .body{{padding:12px}} .title{{font-weight:700;margin-bottom:4px}}
  .when{{font-size:12px;color:#94a3b8;margin-bottom:8px}}
  .cap{{font-size:13px;white-space:pre-wrap;color:#cbd5e1}}
  .err{{background:#7f1d1d;padding:10px 14px;border-radius:8px;margin-top:24px}}
  .btns{{display:flex;gap:8px;margin-top:10px}}
  .btns button{{flex:1;padding:8px;border:none;border-radius:8px;font-weight:700;cursor:pointer}}
  .ok{{background:#16a34a;color:#fff}} .no{{background:#475569;color:#fff}}
  .done{{opacity:.45}}
  .candwrap{{position:relative}}
  .candtag{{position:absolute;bottom:0;left:0;right:0;background:#b45309;color:#fff;font-size:12px;font-weight:700;text-align:center;padding:4px}}
</style>
<script>
async function act(btn, ep, sheet, row) {{
  btn.disabled = true;
  try {{
    const r = await fetch(`http://127.0.0.1:8765/${{ep}}?sheet=${{sheet}}&row=${{row}}`);
    const j = await r.json();
    const card = btn.closest('.card');
    if (j.ok) {{
      card.querySelector('.head span:last-child').textContent = ep === 'approve' ? '✅ aprobado' : '⛔ salteado';
      card.classList.add('done');
      card.querySelector('.btns').remove();
    }} else {{
      alert('Error: ' + j.msg); btn.disabled = false;
    }}
  }} catch (e) {{
    alert('¿Servidor de aprobación apagado? ' + e); btn.disabled = false;
  }}
}}
</script></head><body>
<h1>Próximos posts — {total} en cola · generado {now} AR</h1>
{"".join(sections)}
</body></html>"""
    out = ROOT / ".tmp" / "preview_next_posts.html"
    out.write_text(doc)
    print(f"{total} posts → {out}")


if __name__ == "__main__":
    main()
