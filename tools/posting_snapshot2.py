#!/usr/bin/env python3
"""
Snapshot of the 6 IG accounts: last posted + next 3 queued, per account.
Same data sources as preview_next_posts.py (which only shows "next N").

Usage:
  python3 tools/posting_snapshot2.py
Output: .tmp/posting_snapshot2.html
"""
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
from tools.preview_next_posts import CALENDARS, FIESTAS, col, resolve_media

AR_TZ = timezone(timedelta(hours=-3))


def fetch(sheets, account, env_key, rng, cols, want_status, limit, today=None):
    sheet_id = os.getenv(env_key, "")
    if not sheet_id:
        return [], f"{env_key} no está en .env"
    try:
        rows = sheets.spreadsheets().values().get(
            spreadsheetId=sheet_id, range=rng).execute().get("values", [])
    except Exception as e:
        return [], str(e)[:120]
    out = []
    for rownum, r in enumerate(rows, start=2):
        status = col(r, cols["status"]).lower()
        post_id = col(r, cols["post_id"])
        date = col(r, cols.get("date"))
        if want_status == "posted":
            if status != "posted" and not post_id:
                continue
        else:
            if status not in ("approved", "pending") or post_id:
                continue
            if account == "Fiestas" and today and date and date < today:
                continue
        out.append({
            "row": rownum, "date": date, "time": col(r, cols.get("time")),
            "content": col(r, cols.get("content")), "type": col(r, cols.get("type")),
            "caption": col(r, cols["caption"]), "media": col(r, cols["media"]),
            "status": status or "posted",
        })
    if want_status == "posted":
        out = out[-limit:][::-1]  # most recent last-in-sheet first
    else:
        out = out[:limit]
    return out, None


def card(account, color, p, tag_label, tag_color):
    cap = html.escape(p["caption"][:200]) + ("…" if len(p["caption"]) > 200 else "")
    title = html.escape(p["content"] or p["type"] or "(sin título)")
    when = " ".join(x for x in (p["date"], p["time"]) if x) or "sin fecha"
    src = p.get("src", "")
    media = p["media"]
    is_video = any(e in media.lower() for e in (".mp4", ".mov", "video"))
    if is_video and media:
        media_tag = f'<div class="nomedia">🎬 video: {title}</div>'
    elif src:
        media_tag = f'<img src="{html.escape(src)}" loading="lazy" onerror="this.outerHTML=\'<div class=nomedia>⚠️ imagen no accesible</div>\'">'
    elif media:
        media_tag = '<div class="nomedia">⚠️ imagen no accesible</div>'
    else:
        media_tag = '<div class="nomedia">sin media</div>'
    return f"""
    <div class="card">
      <div class="head" style="background:{tag_color}"><span>{tag_label}</span><span>fila {p['row']}</span></div>
      {media_tag}
      <div class="body">
        <div class="title">{title}</div>
        <div class="when">📅 {when}</div>
        <div class="cap">{cap}</div>
      </div>
    </div>"""


def main():
    sheets, drive = get_services()
    today = datetime.now(tz=AR_TZ).strftime("%Y-%m-%d")
    sections = []
    issues = []

    for account, (env_key, rng, cols, color) in {**CALENDARS, "Fiestas": FIESTAS}.items():
        last, err1 = fetch(sheets, account, env_key, rng, cols, "posted", 1)
        nxt, err2 = fetch(sheets, account, env_key, rng, cols, "pending", 3, today)
        err = err1 or err2
        if err:
            sections.append(f'<div class="err">⚠️ {account}: {html.escape(err)}</div>')
            issues.append(f"{account}: {err}")
            continue

        cards = []
        if last:
            p = last[0]
            p["src"] = resolve_media(p["media"], drive)
            if not p["src"] and p["media"] and "video" not in p["media"].lower() and not p["media"].lower().endswith((".mp4", ".mov")):
                issues.append(f"{account} · último posteado (fila {p['row']}): imagen no carga")
            cards.append(card(account, color, p, "⏪ ÚLTIMO POSTEADO", "#334155"))
        else:
            cards.append('<div class="nomedia" style="border-radius:12px">sin historial de posteados</div>')
            issues.append(f"{account}: sin historial de posteados")

        if not nxt:
            issues.append(f"{account}: cola de próximos vacía")
        for i, p in enumerate(nxt, start=1):
            p["src"] = resolve_media(p["media"], drive)
            if not p["src"] and p["media"] and "video" not in p["media"].lower() and not p["media"].lower().endswith((".mp4", ".mov")):
                issues.append(f"{account} · próximo #{i} (fila {p['row']}): imagen no carga")
            cards.append(card(account, color, p, f"⏩ PRÓXIMO #{i}", color))

        sections.append(f'<h2 style="border-left:6px solid {color};padding-left:10px">{account}</h2><div class="grid">{"".join(cards)}</div>')

    now = datetime.now(tz=AR_TZ).strftime("%Y-%m-%d %H:%M")
    issues_html = ""
    if issues:
        issues_html = '<div class="issues"><b>⚠️ Revisar:</b><ul>' + "".join(f"<li>{html.escape(i)}</li>" for i in issues) + "</ul></div>"
    else:
        issues_html = '<div class="ok-banner">✅ Todo OK — último posteado + próximos 3 cargan bien en las 6 cuentas.</div>'

    doc = f"""<!DOCTYPE html><html lang="es"><head><meta charset="utf-8">
<title>Snapshot — último + próximos 3, 6 cuentas</title>
<style>
  body{{font-family:-apple-system,sans-serif;background:#0f172a;color:#e2e8f0;margin:24px}}
  h1{{font-size:22px}} h2{{margin-top:32px}}
  .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:16px}}
  .card{{background:#1e293b;border-radius:12px;overflow:hidden;display:flex;flex-direction:column}}
  .head{{display:flex;justify-content:space-between;padding:6px 12px;font-size:11px;font-weight:700;color:#fff}}
  .card img{{width:100%;aspect-ratio:1;object-fit:cover;background:#334155}}
  .nomedia{{width:100%;aspect-ratio:1;display:flex;align-items:center;justify-content:center;background:#334155;color:#94a3b8;text-align:center;padding:12px}}
  .body{{padding:12px}} .title{{font-weight:700;margin-bottom:4px;font-size:14px}}
  .when{{font-size:11px;color:#94a3b8;margin-bottom:8px}}
  .cap{{font-size:12px;white-space:pre-wrap;color:#cbd5e1}}
  .err{{background:#7f1d1d;padding:10px 14px;border-radius:8px;margin-top:24px}}
  .issues{{background:#7c2d12;padding:14px 18px;border-radius:8px;margin-top:16px}}
  .ok-banner{{background:#14532d;padding:14px 18px;border-radius:8px;margin-top:16px;font-weight:700}}
</style></head><body>
<h1>Snapshot — último posteado + próximos 3 · generado {now} AR</h1>
{issues_html}
{"".join(sections)}
</body></html>"""
    out = ROOT / ".tmp" / "posting_snapshot2.html"
    out.write_text(doc)
    print(f"→ {out}")
    if issues:
        print(f"\n{len(issues)} problema(s) encontrados:")
        for i in issues:
            print(f"  - {i}")
    else:
        print("Todo OK.")


if __name__ == "__main__":
    main()
