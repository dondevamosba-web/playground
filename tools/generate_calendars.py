#!/usr/bin/env python3
"""
Generate HTML content calendars for Fiestas, Storm, and Techno Apple.
Run after approving / dating posts in the source JSON files.

Sources:
  .tmp/ra_events_captioned.json  → .tmp/fiestas_calendar.html
  .tmp/storm_schedule.json       → .tmp/storm_calendar.html
  .tmp/tech_posts.json           → .tmp/techno_calendar.html
"""

import json
import os
import urllib.parse
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).parent.parent
TMP = ROOT / ".tmp"


# ── helpers ────────────────────────────────────────────────────────────────

def month_grid(year: int, month: int):
    """Return list of weeks; each week is 7 day-numbers (0 = empty)."""
    from calendar import monthcalendar
    return monthcalendar(year, month)


def escape(s: str) -> str:
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def resolve_img(path: str) -> str:
    """Convert paths/URLs to previewable URLs, routing Drive files through the local proxy."""
    if not path:
        return ""
    if path.startswith(".tmp/"):
        return "/tmp/" + path[5:]
    # Drive download URL → proxy via server
    if "drive.google.com/uc" in path and "id=" in path:
        file_id = path.split("id=")[-1].split("&")[0]
        thumb = f"https://drive.google.com/thumbnail?id={file_id}&sz=w400"
        return f"/img-proxy?url={urllib.parse.quote(thumb, safe='')}"
    if "drive.google.com/thumbnail" in path and "id=" in path:
        return f"/img-proxy?url={urllib.parse.quote(path, safe='')}"
    if "drive.google.com/file/d/" in path:
        file_id = path.split("/d/")[1].split("/")[0]
        thumb = f"https://drive.google.com/thumbnail?id={file_id}&sz=w400"
        return f"/img-proxy?url={urllib.parse.quote(thumb, safe='')}"
    return path


MONTH_NAMES = {
    5: "Mayo 2026", 6: "Junio 2026", 7: "Julio 2026",
    8: "Agosto 2026", 9: "Septiembre 2026", 10: "Octubre 2026",
}

WEEK_DAYS = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
TODAY = date.today().isoformat()


def build_html(title: str, subtitle: str, accent: str, accent2: str,
               bg: str, header_grad: str, logo_text: str, logo_color: str,
               posts_by_date: dict, queue: list, legend_items: list,
               months: list, project: str = "") -> str:
    """Render the full HTML string."""

    # ── styles ────────────────────────────────────────────────────────────
    css = f"""
:root {{
  --accent: {accent};
  --accent2: {accent2};
  --bg: {bg};
  --surface: #111827;
  --border: #1E293B;
  --grey: #94A3B8;
  --white: #FFFFFF;
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: 'Inter', sans-serif; background: var(--bg); color: var(--white); min-height: 100vh; }}

header {{
  background: {header_grad};
  padding: 40px 48px 32px;
  display: flex; align-items: center; gap: 20px;
}}
.logo-mark {{
  width: 48px; height: 48px; background: white; border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 800;
  color: {logo_color}; font-size: 14px; letter-spacing: -1px; text-align: center; line-height: 1.1;
}}
header h1 {{ font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 800; font-size: 24px; }}
header p {{ font-size: 14px; color: rgba(255,255,255,.65); margin-top: 2px; }}

.legend {{
  display: flex; gap: 16px; padding: 16px 48px;
  background: #111827; border-bottom: 1px solid var(--border); flex-wrap: wrap; align-items: center;
}}
.pill {{
  display: inline-flex; align-items: center;
  padding: 2px 10px; border-radius: 99px;
  font-size: 11px; font-weight: 600; letter-spacing: .3px;
}}
.stat-row {{ display: flex; gap: 32px; padding: 20px 48px; background: #0D1321; border-bottom: 1px solid var(--border); }}
.stat {{ text-align: center; }}
.stat .n {{ font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 800; font-size: 28px; color: var(--accent); }}
.stat .l {{ font-size: 11px; color: var(--grey); text-transform: uppercase; letter-spacing: 1px; margin-top: 2px; }}

.months {{ padding: 32px 48px 48px; display: flex; flex-direction: column; gap: 48px; }}
.month-block h2 {{
  font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 700;
  font-size: 20px; color: var(--grey); text-transform: uppercase;
  letter-spacing: 2px; margin-bottom: 16px;
}}
.cal-grid {{
  display: grid; grid-template-columns: repeat(7, 1fr);
  gap: 2px; border-radius: 16px; overflow: hidden; border: 1px solid var(--border);
}}
.day-header {{
  background: #111827; padding: 10px 0;
  text-align: center; font-size: 11px; font-weight: 600;
  color: var(--grey); letter-spacing: 1px; text-transform: uppercase;
}}
.day-cell {{
  background: #111827; min-height: 110px; padding: 8px;
  position: relative; border: 1px solid var(--border); transition: background .15s;
}}
.day-cell.empty {{ background: #0D1321; }}
.day-cell.today {{ background: #0F1E2E; }}
.day-cell.has-post {{ background: #0F1A2E; cursor: pointer; }}
.day-cell.has-post:hover {{ background: #132240; }}
.day-num {{ font-size: 12px; font-weight: 600; color: var(--grey); margin-bottom: 6px; }}
.day-cell.today .day-num {{ color: var(--accent); }}
.post-card {{ border-radius: 8px; overflow: hidden; border: 1px solid var(--border); }}
.post-thumb {{ width: 100%; aspect-ratio: 1/1; object-fit: cover; display: block; background: #1E293B; }}
.post-meta {{ padding: 5px 6px; background: #1E293B; }}
.post-title {{ font-size: 9px; color: var(--grey); line-height: 1.3;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }}
.post-status {{
  font-size: 9px; font-weight: 700; letter-spacing: .3px; margin-top: 3px;
}}
.status-approved {{ color: #4ADE80; }}
.status-pending {{ color: #FBBF24; }}
.img-placeholder {{
  width: 100%; height: 52px; display: none;
  background: linear-gradient(135deg, #1E293B, #0F172A);
  align-items: center; justify-content: center;
  font-size: 9px; color: #334155; text-align: center;
}}

/* Queue */
.queue-section {{ padding: 0 48px 48px; }}
.queue-section h2 {{
  font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 700;
  font-size: 18px; color: var(--grey); margin-bottom: 16px;
  display: flex; align-items: center; gap: 10px;
}}
.queue-badge {{
  background: #FBBF24; color: #0F172A; border-radius: 99px;
  font-size: 11px; font-weight: 700; padding: 2px 8px;
}}
.queue-grid {{
  display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 12px;
}}
.queue-card {{
  background: #111827; border: 1px solid var(--border); border-radius: 12px;
  overflow: hidden; cursor: pointer; transition: border-color .15s;
}}
.queue-card:hover {{ border-color: var(--accent); }}
.queue-thumb {{ width: 100%; aspect-ratio: 1/1; object-fit: cover; background: #1E293B; }}
.queue-meta {{ padding: 8px; }}
.queue-label {{ font-size: 11px; font-weight: 600; color: var(--white); margin-bottom: 4px; }}
.queue-caption {{ font-size: 10px; color: var(--grey); line-height: 1.4;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }}

/* Modal */
.modal-bg {{
  display: none; position: fixed; inset: 0;
  background: rgba(0,0,0,.85); z-index: 100;
  align-items: center; justify-content: center; backdrop-filter: blur(4px);
}}
.modal-bg.open {{ display: flex; }}
.modal {{
  background: #111827; border-radius: 20px; border: 1px solid var(--border);
  max-width: 520px; width: 90%; max-height: 90vh; overflow-y: auto;
}}
.modal-img {{ width: 100%; border-radius: 16px 16px 0 0; display: block; object-fit: cover; max-height: 320px; }}
.modal-body {{ padding: 24px; }}
.modal-body h3 {{ font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 700; font-size: 18px; margin-bottom: 12px; }}
.modal-caption {{ font-size: 14px; color: #CBD5E1; line-height: 1.6; white-space: pre-wrap; }}
.modal-meta {{ display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 16px; }}
.modal-close {{
  position: sticky; top: 0; float: right;
  background: #1E293B; border: none; color: white;
  border-radius: 99px; width: 32px; height: 32px;
  cursor: pointer; font-size: 16px; margin: 12px 12px 0 0;
}}
"""

    # ── legend pills ───────────────────────────────────────────────────────
    legend_html = ""
    for text, color, bg_c in legend_items:
        legend_html += f'<span class="pill" style="background:{bg_c};color:{color}">{escape(text)}</span> '

    # ── stats ──────────────────────────────────────────────────────────────
    total = sum(len(v) for v in posts_by_date.values()) + len(queue)
    scheduled = sum(len(v) for v in posts_by_date.values())
    approved_count = sum(
        1 for posts in posts_by_date.values()
        for p in posts if p.get("approved")
    )
    stats_html = f"""
<div class="stat-row">
  <div class="stat"><div class="n">{total}</div><div class="l">Total posts</div></div>
  <div class="stat"><div class="n">{scheduled}</div><div class="l">Scheduled</div></div>
  <div class="stat"><div class="n">{len(queue)}</div><div class="l">In queue</div></div>
  <div class="stat"><div class="n">{approved_count}</div><div class="l">Approved</div></div>
</div>"""

    # ── months ─────────────────────────────────────────────────────────────
    months_html = ""
    for year, month in months:
        weeks = month_grid(year, month)
        grid_html = ""
        for day in WEEK_DAYS:
            grid_html += f'<div class="day-header">{day}</div>'
        for week in weeks:
            for day_num in week:
                if day_num == 0:
                    grid_html += '<div class="day-cell empty"></div>'
                    continue
                d_str = f"{year}-{month:02d}-{day_num:02d}"
                day_posts = posts_by_date.get(d_str, [])
                extra = "today" if d_str == TODAY else ""
                if day_posts:
                    extra += " has-post"
                cells = f'<div class="day-num">{day_num}</div>'
                for p in day_posts[:1]:
                    p = {**p, "image_url": resolve_img(p.get("image_url") or p.get("file") or "")}
                    img = escape(p["image_url"])
                    status_cls = "status-approved" if p.get("approved") else "status-pending"
                    status_txt = "Aprobado" if p.get("approved") else "Pendiente"
                    title_txt = escape(p.get("name") or p.get("product") or p.get("label") or "")
                    p_json = json.dumps(p, ensure_ascii=False).replace('</','<\\/')
                    p_json_attr = escape(json.dumps(p, ensure_ascii=False))
                    time_txt = escape(p.get("time") or "")
                    time_html = f'<div style="font-size:9px;color:#6366F1;margin-top:2px">⏰ {time_txt}</div>' if time_txt else ''
                    placeholder_hidden = '<div class="img-placeholder">Sin imagen</div>'
                    placeholder_visible = '<div class="img-placeholder" style="display:flex">Sin imagen</div>'
                    if img:
                        thumb_html = f'<div style="position:relative"><img class="post-thumb" src="{img}" loading="lazy" onerror="this.style.display=\'none\';this.nextElementSibling.style.display=\'flex\'" />{placeholder_hidden}</div>'
                    else:
                        thumb_html = f'<div style="position:relative">{placeholder_visible}</div>'
                    cells += f"""
<div class="post-card" draggable="true" data-post="{p_json_attr}" data-date="{d_str}" onclick="openModal(JSON.parse(this.dataset.post))">
  {thumb_html}
  <div class="post-meta">
    <div class="post-title">{title_txt}</div>
    <div class="post-status {status_cls}">{status_txt}</div>
    {time_html}
  </div>
</div>"""
                grid_html += f'<div class="day-cell {extra.strip()}" data-date="{d_str}">{cells}</div>'

        months_html += f"""
<div class="month-block">
  <h2>{MONTH_NAMES.get(month, f'{month}/{year}')}</h2>
  <div class="cal-grid">{grid_html}</div>
</div>"""

    # ── queue ──────────────────────────────────────────────────────────────
    queue_cards = ""
    for p in queue:
        p = {**p, "image_url": resolve_img(p.get("image_url") or p.get("file") or "")}
        img = escape(p["image_url"])
        label = escape(p.get("name") or p.get("product") or p.get("label") or "")
        caption_snip = escape((p.get("feed_caption") or p.get("caption") or "")[:80])
        p_json = json.dumps(p, ensure_ascii=False).replace('</','<\\/')
        p_json_attr = escape(json.dumps(p, ensure_ascii=False))
        q_ph_hidden  = '<div class="img-placeholder" style="height:80px">Sin imagen</div>'
        q_ph_visible = '<div class="img-placeholder" style="height:80px;display:flex">Sin imagen</div>'
        if img:
            q_thumb = f'<div style="position:relative"><img class="queue-thumb" src="{img}" loading="lazy" onerror="this.style.display=\'none\';this.nextElementSibling.style.display=\'flex\'" />{q_ph_hidden}</div>'
        else:
            q_thumb = f'<div style="position:relative">{q_ph_visible}</div>'
        queue_cards += f"""
<div class="queue-card" draggable="true" data-post="{p_json_attr}" onclick="openModal(JSON.parse(this.dataset.post))">
  {q_thumb}
  <div class="queue-meta">
    <div class="queue-label">{label}</div>
    <div class="queue-caption">{caption_snip}</div>
  </div>
</div>"""

    queue_section = ""
    if queue:
        queue_section = f"""
<div class="queue-section">
  <h2>Cola — sin fecha asignada <span class="queue-badge">{len(queue)}</span></h2>
  <div class="queue-grid">{queue_cards}</div>
</div>"""

    # ── JS modal ───────────────────────────────────────────────────────────
    js = """
function openModal(p) {
  const img = p.image_url || p.file || '';
  const title = p.name || p.product || p.label || '';
  const caption = p.feed_caption || p.caption || p.story_caption || '';
  const date = p.date || p.schedule_date || '';
  const status = p.approved ? '✓ Aprobado' : '⏳ Pendiente';
  document.getElementById('m-img').src = img;
  document.getElementById('m-img').onerror = function(){ this.style.display='none'; };
  document.getElementById('m-title').textContent = title;
  document.getElementById('m-caption').textContent = caption;
  document.getElementById('m-meta').innerHTML =
    (date ? `<span style="background:#1E293B;padding:3px 10px;border-radius:6px;font-size:12px;color:#CBD5E1">${date}</span>` : '') +
    `<span style="background:#1E293B;padding:3px 10px;border-radius:6px;font-size:12px;color:#CBD5E1">${status}</span>`;
  // Inject approve / unapprove button inside modal
  const actions = document.getElementById('m-actions');
  const id = p.id !== undefined ? p.id : (p.name || '');
  if (!p.approved) {
    actions.innerHTML = `<button onclick="modalApprove('${id}','${date||''}',false)" style="background:#22C55E;border:none;color:white;padding:10px 24px;border-radius:8px;font-weight:700;font-size:14px;cursor:pointer">✓ Aprobar</button>`;
  } else {
    actions.innerHTML = `<button onclick="modalApprove('${id}','${date||''}',true)" style="background:#64748B;border:none;color:white;padding:10px 24px;border-radius:8px;font-weight:700;font-size:14px;cursor:pointer">✗ Desaprobar</button>`;
  }
  document.getElementById('modal').classList.add('open');
}
async function modalApprove(id, date, unapprove) {
  const time = '10:00';
  const btn = event.target;
  btn.textContent = 'Guardando…'; btn.disabled = true;
  try {
    const resp = await fetch('/api/approve', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({project:PROJECT,id,date,time,unapprove})});
    const data = await resp.json();
    if (data.ok) { location.reload(); }
    else { btn.textContent = 'Error'; btn.disabled = false; }
  } catch(e) { btn.textContent = 'Error'; btn.disabled = false; }
}
function closeModal(e) {
  if (e.target === document.getElementById('modal')) {
    document.getElementById('modal').classList.remove('open');
  }
}
"""

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8" />
<title>{escape(title)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700;800&family=Inter:wght@400;500;600&display=swap" />
<style>{css}</style>
</head>
<body>

<header>
  <div class="logo-mark">{escape(logo_text)}</div>
  <div>
    <h1>{escape(title)}</h1>
    <p>{escape(subtitle)}</p>
  </div>
</header>

<div class="legend">{legend_html}</div>
{stats_html}
<div class="months" id="calendar">{months_html}</div>
{queue_section}

<div class="modal-bg" id="modal" onclick="closeModal(event)">
  <div class="modal">
    <button class="modal-close" onclick="document.getElementById('modal').classList.remove('open')">✕</button>
    <img class="modal-img" id="m-img" src="" alt="" />
    <div class="modal-body">
      <div class="modal-meta" id="m-meta"></div>
      <h3 id="m-title"></h3>
      <div class="modal-caption" id="m-caption"></div>
      <div id="m-actions" style="margin-top:20px;display:flex;gap:10px;flex-wrap:wrap"></div>
    </div>
  </div>
</div>

<script>const PROJECT = '{project}';\n{js}</script>
</body>
</html>"""


# ── Fiestas ────────────────────────────────────────────────────────────────

def fetch_fiestas_sheet_statuses() -> dict:
    """Return {event_name: status} from the Fiestas approval sheet."""
    try:
        import sys
        sys.path.insert(0, str(ROOT))
        from dotenv import load_dotenv
        load_dotenv(ROOT / ".env")
        from tools.sheets_client import get_services
        import os
        sheets, _ = get_services()
        sheet_id = os.getenv("FIESTAS_APPROVAL_SHEET_ID")
        resp = sheets.spreadsheets().values().get(
            spreadsheetId=sheet_id, range="Queue!A:N"
        ).execute()
        rows = resp.get("values", [])
        return {r[2]: r[11] for r in rows[1:] if len(r) > 11}
    except Exception as e:
        print(f"[fiestas sheet] could not fetch statuses: {e}")
        return {}


def build_fiestas():
    with open(TMP / "ra_events_captioned.json") as f:
        events = json.load(f)

    sheet_statuses = fetch_fiestas_sheet_statuses()
    for e in events:
        sheet_status = sheet_statuses.get(e.get("name", ""))
        if sheet_status:
            e["approved"] = (sheet_status == "approved")
            e["sheet_status"] = sheet_status

    posts_by_date = {}
    for e in events:
        d = e.get("date", "")[:10]
        if d:
            posts_by_date.setdefault(d, []).append(e)

    queue = [e for e in events if not e.get("date")]

    html = build_html(
        title="Fiestas Electrónicas BA — Content Calendar",
        subtitle="Eventos próximos · @fiestaselectronicasbuenosaires",
        accent="#C084FC",
        accent2="#7C3AED",
        bg="#0A0210",
        header_grad="linear-gradient(135deg, #1A0533, #4C1D95, #7C3AED)",
        logo_text="FIES\nTAS",
        logo_color="#7C3AED",
        posts_by_date=posts_by_date,
        queue=queue,
        legend_items=[
            ("Evento publicable", "#C084FC", "#2D1B4E"),
            ("Pendiente", "#FBBF24", "#2D1E05"),
        ],
        months=[(2026, 6), (2026, 7)],
        project="fiestas",
    )

    out = TMP / "fiestas_calendar.html"
    out.write_text(html)
    print(f"✓ {out}")


# ── Storm ──────────────────────────────────────────────────────────────────

def build_storm():
    with open(TMP / "storm_schedule.json") as f:
        posts = json.load(f)

    posts_by_date = {}
    queue = []
    for p in posts:
        d = p.get("date")
        if d and p.get("approved"):
            posts_by_date.setdefault(d, []).append(p)
        else:
            queue.append(p)

    html = build_html(
        title="Storm Digital — Content Calendar",
        subtitle="Batch de posts · @storm.digital",
        accent="#A3E635",
        accent2="#65A30D",
        bg="#05080F",
        header_grad="linear-gradient(135deg, #0A0F1E, #1A2744, #2D1B69)",
        logo_text="STM",
        logo_color="#2D1B69",
        posts_by_date=posts_by_date,
        queue=queue,
        legend_items=[
            ("Aprobado", "#A3E635", "#1A2E05"),
            ("Sin fecha", "#FBBF24", "#2D1E05"),
        ],
        months=[(2026, 6), (2026, 7)],
        project="storm",
    )

    out = TMP / "storm_calendar.html"
    out.write_text(html)
    print(f"✓ {out}")


# ── Techno Apple ───────────────────────────────────────────────────────────

def build_techno():
    with open(TMP / "tech_posts.json") as f:
        posts = json.load(f)

    posts_by_date = {}
    queue = []
    for p in posts:
        d = p.get("schedule_date") or p.get("date")
        if d:  # show all dated posts on calendar regardless of approval
            posts_by_date.setdefault(d, []).append(p)
        else:
            queue.append(p)

    html = build_html(
        title="Techno Apple — Content Calendar",
        subtitle="Productos Apple · @techno.apple.ok",
        accent="#E5E7EB",
        accent2="#9CA3AF",
        bg="#050505",
        header_grad="linear-gradient(135deg, #111111, #1C1C1E, #2C2C2E)",
        logo_text="APL",
        logo_color="#1C1C1E",
        posts_by_date=posts_by_date,
        queue=queue,
        legend_items=[
            ("Aprobado", "#E5E7EB", "#1C1C1E"),
            ("Pendiente aprobación", "#FBBF24", "#2D1E05"),
        ],
        months=[(2026, 6), (2026, 7), (2026, 8)],
        project="techno",
    )

    out = TMP / "techno_calendar.html"
    out.write_text(html)
    print(f"✓ {out}")


# ── Ola Digital ────────────────────────────────────────────────────────────────

def build_ola():
    with open(TMP / "ola_schedule.json") as f:
        posts = json.load(f)

    posts_by_date = {}
    queue = []
    for p in posts:
        status = p.get("status", "pending")
        d = p.get("date", "")
        img = p.get("image_url", "")
        # Convert Drive file IDs to thumbnail URLs
        if img and "drive.google.com" not in img and len(img) > 20 and "/" not in img:
            img = f"https://drive.google.com/thumbnail?id={img}&sz=w400"
            p["image_url"] = img
        if d and status in ("pending", "approved"):
            p["approved"] = (status == "approved")
            posts_by_date.setdefault(d, []).append(p)
        elif status == "posted":
            p["approved"] = True
            posts_by_date.setdefault(d, []).append(p)
        else:
            queue.append(p)

    html = build_html(
        title="Ola Digital — Content Calendar",
        subtitle="Lun / Mié / Vie · 10:00 AM (ART) · @oladigitalok",
        accent="#0EA5E9",
        accent2="#0369A1",
        bg="#0A0F1E",
        header_grad="linear-gradient(135deg, #0C4A6E, #0369A1, #0EA5E9)",
        logo_text="OLA",
        logo_color="#0369A1",
        posts_by_date=posts_by_date,
        queue=queue,
        legend_items=[
            ("Publicado", "#4ADE80", "#1A2E1A"),
            ("Pendiente", "#FBBF24", "#2D1E05"),
        ],
        months=[(2026, 6), (2026, 7)],
        project="ola",
    )

    out = TMP / "ola_calendar.html"
    out.write_text(html)
    print(f"✓ {out}")


if __name__ == "__main__":
    build_fiestas()
    build_storm()
    build_techno()
    build_ola()
    print("\nDone. Open the HTML files in .tmp/ to preview.")
