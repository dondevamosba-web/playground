#!/usr/bin/env python3
"""
Local calendar server — serves interactive content calendars for all 4 IG projects.
Run:  python3 tools/calendar_server.py
Open: http://localhost:5055
"""

import json
import subprocess
import sys
from pathlib import Path

import sys as _sys
_sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask, Response, jsonify, request, send_from_directory
from tools.sync_to_sheet import sync_post

ROOT = Path(__file__).parent.parent
TMP = ROOT / ".tmp"

app = Flask(__name__)

SOURCE_MAP = {
    "fiestas": TMP / "ra_events_captioned.json",
    "storm":   TMP / "storm_schedule.json",
    "techno":  TMP / "tech_posts.json",
    "ola":     TMP / "ola_schedule.json",
}

# fiestas posts use event name as id — patch the approve endpoint to match
FIESTAS_ID_FIELD = "name"


# ── static files ────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8"/>
<title>IG Calendars</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@700;800&family=Inter:wght@400;500;600&display=swap"/>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Inter', sans-serif; background: #050A14; color: #fff;
       min-height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 24px; }
h1 { font-family: 'Plus Jakarta Sans', sans-serif; font-size: 28px; font-weight: 800; color: #E2E8F0; margin-bottom: 8px; }
p { color: #64748B; font-size: 14px; margin-bottom: 32px; }
.grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; width: 100%; max-width: 600px; }
a.card {
  display: flex; flex-direction: column; gap: 6px;
  background: #111827; border: 1px solid #1E293B; border-radius: 16px;
  padding: 24px; text-decoration: none; color: white;
  transition: border-color .15s, background .15s;
}
a.card:hover { border-color: #6366F1; background: #131F35; }
a.card .name { font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 700; font-size: 16px; }
a.card .handle { font-size: 12px; color: #64748B; }
a.card .dot { width: 10px; height: 10px; border-radius: 50%; margin-bottom: 8px; }
</style>
</head>
<body>
<div>
  <h1>IG Content Calendars</h1>
  <p>Select a project to view and manage its content calendar.</p>
  <div class="grid">
    <a class="card" href="/calendar/ola">
      <div class="dot" style="background:#0EA5E9"></div>
      <div class="name">Ola Digital</div>
      <div class="handle">@oladigital</div>
    </a>
    <a class="card" href="/calendar/fiestas">
      <div class="dot" style="background:#C084FC"></div>
      <div class="name">Fiestas Electrónicas</div>
      <div class="handle">@fiestaselectronicasbuenosaires</div>
    </a>
    <a class="card" href="/calendar/storm">
      <div class="dot" style="background:#A3E635"></div>
      <div class="name">Storm Digital</div>
      <div class="handle">@storm.digital</div>
    </a>
    <a class="card" href="/calendar/techno">
      <div class="dot" style="background:#E5E7EB"></div>
      <div class="name">Techno Apple</div>
      <div class="handle">@techno.apple.ok</div>
    </a>
  </div>
</div>
</body>
</html>"""


@app.route("/calendar/<project>")
def serve_calendar(project):
    cal_map = {
        "ola":     TMP / "ola_calendar.html",
        "fiestas": TMP / "fiestas_calendar.html",
        "storm":   TMP / "storm_calendar.html",
        "techno":  TMP / "techno_calendar.html",
    }
    if project not in cal_map:
        return "Not found", 404
    path = cal_map[project]
    if not path.exists():
        return f"Calendar not generated yet. Run: python3 tools/generate_calendars.py", 404

    html = path.read_text()
    # Inject interactive approve widget before </body>
    html = html.replace("</body>", APPROVE_WIDGET + f"\n<script>const PROJECT='{project}';</script>\n</body>")
    return Response(html, mimetype="text/html")


@app.route("/tmp/<path:filename>")
def serve_tmp(filename):
    return send_from_directory(TMP, filename)


@app.route("/img-proxy")
def img_proxy():
    """Proxy Drive thumbnail/download URLs through the server so browser auth isn't needed."""
    import urllib.request, urllib.error
    url = request.args.get("url", "")
    if not url or "drive.google.com" not in url:
        return "", 400
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = resp.read()
            content_type = resp.headers.get("Content-Type", "image/jpeg")
        return Response(data, mimetype=content_type.split(";")[0])
    except Exception as e:
        return "", 404


# ── API ──────────────────────────────────────────────────────────────────────

@app.route("/api/approve", methods=["POST"])
def approve():
    """Approve a post and set its date/time. Regenerates calendar HTML."""
    data = request.json
    project = data.get("project")
    post_id = data.get("id")
    date_val = data.get("date")
    time_val = data.get("time", "")
    unapprove = data.get("unapprove", False)

    if project not in SOURCE_MAP:
        return jsonify(error="Unknown project"), 400

    src = SOURCE_MAP[project]
    posts = json.loads(src.read_text())

    updated = False
    for p in posts:
        match = (str(p.get("id")) == str(post_id)) or (p.get("name") == post_id) or (str(p.get("id","")) == str(post_id))
        if match:
            if unapprove:
                p["approved"] = None
                p.pop("date", None)
                p.pop("schedule_date", None)
                p.pop("time", None)
                if project == "ola":
                    p["status"] = "pending"
            else:
                p["approved"] = True
                p["time"] = time_val or ""
                if project == "techno":
                    p["schedule_date"] = date_val
                else:
                    p["date"] = date_val
                if project == "ola":
                    p["status"] = "approved"
            updated = True
            break

    if not updated:
        return jsonify(error="Post not found"), 404

    src.write_text(json.dumps(posts, indent=2, ensure_ascii=False))

    # Sync to Google Sheet
    updated_post = next((p for p in posts if str(p.get("id")) == str(post_id) or p.get("name") == post_id), None)
    if updated_post:
        try:
            sync_post(project, updated_post, unapprove)
        except Exception as e:
            print(f"[sheet sync warning] {e}")

    result = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "generate_calendars.py")],
        capture_output=True, text=True, cwd=ROOT
    )
    if result.returncode != 0:
        return jsonify(error=result.stderr), 500

    # Fire autopost immediately so scheduled-for-now posts go out
    if not unapprove:
        AUTOPOST_MAP = {
            "ola":    ROOT / "tools" / "auto_post_from_calendar.py",
            "storm":  ROOT / "tools" / "auto_post_storm.py",
            "techno": ROOT / "tools" / "auto_post_techno.py",
        }
        script = AUTOPOST_MAP.get(project)
        if script and script.exists():
            subprocess.Popen([sys.executable, str(script)], cwd=ROOT)

    return jsonify(ok=True)


# ── Approve widget (injected into each calendar) ─────────────────────────────

APPROVE_WIDGET = """
<!-- Bottom panel -->
<div id="approve-panel" style="display:none;position:fixed;bottom:0;left:0;right:0;
  background:#111827;border-top:1px solid #1E293B;padding:16px 48px;
  align-items:center;gap:12px;z-index:200;flex-wrap:wrap;">
  <div style="flex:1;min-width:180px">
    <div id="ap-title" style="font-family:'Plus Jakarta Sans',sans-serif;font-weight:700;font-size:15px;margin-bottom:2px"></div>
    <div id="ap-subtitle" style="font-size:11px;color:#64748B"></div>
  </div>
  <input type="date" id="ap-date" min="2026-06-01" max="2026-12-31"
    style="background:#1E293B;border:1px solid #334155;color:white;padding:8px 12px;border-radius:8px;font-size:14px;outline:none"/>
  <input type="time" id="ap-time" value="10:00"
    style="background:#1E293B;border:1px solid #334155;color:white;padding:8px 12px;border-radius:8px;font-size:14px;outline:none;width:120px"/>
  <button id="ap-approve-btn" onclick="doQuickApprove()"
    style="background:#22C55E;border:none;color:white;padding:10px 24px;border-radius:8px;font-weight:700;font-size:14px;cursor:pointer">
    ✓ Aprobar
  </button>
  <button onclick="doApprove()"
    style="background:#6366F1;border:none;color:white;padding:10px 20px;border-radius:8px;font-weight:600;font-size:14px;cursor:pointer">
    Guardar fecha/hora
  </button>
  <button onclick="doUnapprove()" id="ap-unapprove" style="display:none;
    background:#1E293B;border:1px solid #334155;color:#94A3B8;padding:10px 16px;border-radius:8px;font-size:13px;cursor:pointer">
    Quitar aprobación
  </button>
  <button onclick="closePanel()"
    style="background:transparent;border:none;color:#64748B;font-size:20px;cursor:pointer;padding:4px 8px">✕</button>
</div>

<!-- Time picker popup (shown after drag-drop) -->
<div id="time-popup" style="display:none;position:fixed;background:#1E293B;border:1px solid #334155;
  border-radius:16px;padding:20px 24px;z-index:9999;box-shadow:0 24px 48px rgba(0,0,0,.6);min-width:260px">
  <div id="tp-title" style="font-family:'Plus Jakarta Sans',sans-serif;font-weight:700;font-size:14px;margin-bottom:4px"></div>
  <div id="tp-date" style="font-size:12px;color:#6366F1;margin-bottom:16px"></div>
  <label style="font-size:11px;color:#94A3B8;display:block;margin-bottom:6px;text-transform:uppercase;letter-spacing:.8px">Hora de publicación</label>
  <input type="time" id="tp-time" value="10:00"
    style="width:100%;background:#111827;border:1px solid #334155;color:white;padding:10px 14px;border-radius:8px;font-size:18px;outline:none;margin-bottom:16px"/>
  <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:16px">
    <button onclick="setTime('08:00')" class="tp-preset">08:00</button>
    <button onclick="setTime('10:00')" class="tp-preset">10:00</button>
    <button onclick="setTime('12:00')" class="tp-preset">12:00</button>
    <button onclick="setTime('18:00')" class="tp-preset">18:00</button>
    <button onclick="setTime('20:00')" class="tp-preset">20:00</button>
  </div>
  <div style="display:flex;gap:8px">
    <button onclick="confirmDrop()"
      style="flex:1;background:#6366F1;border:none;color:white;padding:10px;border-radius:8px;font-weight:600;font-size:14px;cursor:pointer">
      Confirmar
    </button>
    <button onclick="cancelDrop()"
      style="background:#111827;border:1px solid #334155;color:#94A3B8;padding:10px 16px;border-radius:8px;font-size:13px;cursor:pointer">
      Cancelar
    </button>
  </div>
</div>

<!-- Drag ghost label -->
<div id="drop-ghost" style="display:none;position:fixed;top:0;left:0;pointer-events:none;
  background:#6366F1;color:white;padding:5px 12px;border-radius:8px;font-size:12px;font-weight:600;z-index:9999">
</div>

<style>
.queue-card, .post-card { cursor: grab !important; }
.queue-card:active, .post-card:active { cursor: grabbing !important; }
.queue-card.dragging, .post-card.dragging { opacity: .35; transform: scale(.97); }
.day-cell.drop-target { background: #1E2D4A !important; outline: 2px dashed #6366F1; outline-offset: -3px; }
.tp-preset {
  background: #111827; border: 1px solid #334155; color: #94A3B8;
  padding: 4px 10px; border-radius: 6px; font-size: 12px; cursor: pointer;
  transition: background .1s, color .1s;
}
.tp-preset:hover { background: #6366F1; color: white; border-color: #6366F1; }
</style>

<script>
let _activePost = null;
let _dragPost = null;
let _pendingDrop = null; // { post, date }

// ── Modal + panel ─────────────────────────────────────────────────────────────
const _origOpen = window.openModal;
window.openModal = function(p) {
  _origOpen(p);
  _activePost = p;
  const isApproved = p.approved || p.status === 'approved' || p.status === 'posted';
  const dateStr = p.date || p.schedule_date || '';
  const timeStr = p.time || '';
  document.getElementById('ap-title').textContent = p.name || p.product || p.label || p.content_type || '';
  document.getElementById('ap-subtitle').textContent = isApproved
    ? ('✓ Aprobado · ' + dateStr + (timeStr ? ' · ' + timeStr : ''))
    : (dateStr ? dateStr + (timeStr ? ' · ' + timeStr : '') + ' — pendiente aprobación' : 'Sin fecha asignada');
  document.getElementById('ap-date').value = dateStr;
  document.getElementById('ap-time').value = timeStr || '10:00';
  document.getElementById('ap-unapprove').style.display = isApproved ? 'inline-block' : 'none';
  document.getElementById('ap-approve-btn').style.display = isApproved ? 'none' : 'inline-block';
  document.getElementById('approve-panel').style.display = 'flex';
};

function closePanel() {
  document.getElementById('approve-panel').style.display = 'none';
}

async function doQuickApprove() {
  const p = _activePost;
  const date = p.date || p.schedule_date || document.getElementById('ap-date').value;
  const time = p.time || document.getElementById('ap-time').value || '10:00';
  if (!date) { alert('Este post no tiene fecha. Asigná una fecha primero.'); return; }
  const id = p.id !== undefined ? p.id : (p.name || '');
  const btn = document.getElementById('ap-approve-btn');
  btn.textContent = 'Guardando…'; btn.disabled = true;
  const data = await callApprove(id, date, time, false);
  if (data.ok) {
    document.getElementById('modal').classList.remove('open');
    closePanel();
    location.reload();
  } else {
    alert('Error: ' + (data.error || 'unknown'));
    btn.textContent = '✓ Aprobar'; btn.disabled = false;
  }
}

async function callApprove(id, date, time, unapprove) {
  const res = await fetch('/api/approve', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({ project: PROJECT, id: String(id), date, time: time || '', unapprove: !!unapprove })
  });
  return res.json();
}

async function doApprove() {
  const date = document.getElementById('ap-date').value;
  const time = document.getElementById('ap-time').value;
  if (!date) { alert('Elegí una fecha primero'); return; }
  const p = _activePost;
  const id = p.id !== undefined ? p.id : (p.name || '');
  const btn = event.target;
  btn.textContent = 'Guardando…'; btn.disabled = true;
  const data = await callApprove(id, date, time, false);
  if (data.ok) {
    document.getElementById('modal').classList.remove('open');
    closePanel();
    location.reload();
  } else {
    alert('Error: ' + (data.error || 'unknown'));
    btn.textContent = 'Guardar'; btn.disabled = false;
  }
}

async function doUnapprove() {
  const p = _activePost;
  if (!confirm('Quitar del calendario?')) return;
  const id = p.id !== undefined ? p.id : (p.name || '');
  const data = await callApprove(id, null, null, true);
  if (data.ok) { location.reload(); }
}

// ── Time picker popup ─────────────────────────────────────────────────────────
function setTime(t) { document.getElementById('tp-time').value = t; }

function showTimePopup(post, date, x, y) {
  _pendingDrop = { post, date };
  const popup = document.getElementById('time-popup');
  document.getElementById('tp-title').textContent = post.name || post.product || post.label || '';
  document.getElementById('tp-date').textContent = date;
  document.getElementById('tp-time').value = post.time || '10:00';
  // Position near drop point, keep on screen
  const pw = 260, ph = 240;
  const left = Math.min(x, window.innerWidth - pw - 16);
  const top = Math.min(y, window.innerHeight - ph - 16);
  popup.style.left = Math.max(8, left) + 'px';
  popup.style.top = Math.max(8, top) + 'px';
  popup.style.display = 'block';
}

async function confirmDrop() {
  if (!_pendingDrop) return;
  const { post, date } = _pendingDrop;
  const time = document.getElementById('tp-time').value;
  const id = post.id !== undefined ? post.id : (post.name || '');
  const btn = document.querySelector('#time-popup button');
  btn.textContent = 'Guardando…'; btn.disabled = true;
  const data = await callApprove(id, date, time, false);
  if (data.ok) {
    document.getElementById('time-popup').style.display = 'none';
    _pendingDrop = null;
    location.reload();
  } else {
    alert('Error: ' + (data.error || 'unknown'));
    btn.textContent = 'Confirmar'; btn.disabled = false;
  }
}

function cancelDrop() {
  document.getElementById('time-popup').style.display = 'none';
  _pendingDrop = null;
}

// ── Drag and drop ─────────────────────────────────────────────────────────────
document.addEventListener('dragstart', e => {
  const card = e.target.closest('[data-post]');
  if (!card) return;
  try { _dragPost = JSON.parse(card.dataset.post); } catch { return; }
  card.classList.add('dragging');
  e.dataTransfer.effectAllowed = 'move';
  e.dataTransfer.setData('text/plain', card.dataset.post);
});

document.addEventListener('dragend', () => {
  document.querySelectorAll('.dragging').forEach(el => el.classList.remove('dragging'));
  document.querySelectorAll('.drop-target').forEach(el => el.classList.remove('drop-target'));
  document.getElementById('drop-ghost').style.display = 'none';
});

document.addEventListener('dragover', e => {
  const cell = e.target.closest('.day-cell:not(.empty)');
  if (!cell || !_dragPost) return;
  e.preventDefault();
  e.dataTransfer.dropEffect = 'move';
  document.querySelectorAll('.drop-target').forEach(el => el.classList.remove('drop-target'));
  cell.classList.add('drop-target');
  const ghost = document.getElementById('drop-ghost');
  ghost.style.display = 'block';
  ghost.style.left = (e.clientX + 14) + 'px';
  ghost.style.top = (e.clientY - 32) + 'px';
  ghost.textContent = cell.dataset.date || '';
});

document.addEventListener('dragleave', e => {
  if (!e.target.closest('.drop-target')) {
    document.querySelectorAll('.drop-target').forEach(el => el.classList.remove('drop-target'));
  }
});

document.addEventListener('drop', e => {
  const cell = e.target.closest('.day-cell:not(.empty)');
  if (!cell || !_dragPost) return;
  e.preventDefault();
  const targetDate = cell.dataset.date;
  if (!targetDate) return;
  // Show time picker near drop point
  showTimePopup(_dragPost, targetDate, e.clientX, e.clientY - 260);
});
</script>
"""


if __name__ == "__main__":
    print("IG Calendar Server running at http://localhost:5055")
    print("Press Ctrl+C to stop.\n")
    app.run(port=5055, debug=False)
