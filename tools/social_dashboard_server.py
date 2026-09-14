#!/usr/bin/env python3
"""
Local social dashboard — one page, 4 accounts (Ola Digital, Storm, Fiestas,
Techno): followers, day/week/month growth, what's been posted, and a
"Mejoras" button that asks Claude for concrete next actions per account.

Run:  python3 tools/social_dashboard_server.py
Open: http://localhost:5056

Requires the same .env keys as tools/post_instagram.py (INSTAGRAM_ACCESS_TOKEN
+ per-account business account IDs) plus ANTHROPIC_API_KEY for the Mejoras
button. An account missing its ID in .env still renders, marked as "no
configurada" instead of crashing the whole page.

WhatsApp: web.whatsapp.com blocks being embedded in an iframe (Meta sets
X-Frame-Options), so the WhatsApp card is a launch button to a new tab, not
an inline chat view. Fully inline WhatsApp would need an unofficial
automation library (e.g. whatsapp-web.js) — a separate, heavier piece of
work, left out of this MVP.

Growth needs at least two days of snapshots to show a delta. The page
auto-snapshots today's followers/media count on every load, so just using
the dashboard daily is enough to build history — a cron running
tools/snapshot_social_stats.py is optional, only useful for days nobody
opens the page.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from flask import Flask, jsonify, request, Response

from tools.claude_call import call_claude
from tools.post_instagram import ACCOUNT_CONFIG
from tools.social_stats import (
    DISPLAY_NAMES,
    account_history,
    compute_growth,
    fetch_account_stats,
    fetch_recent_media,
    record_snapshot,
)

app = Flask(__name__)

ACCENT = {
    "ola": "#0EA5E9",
    "fiestas": "#C084FC",
    "storm": "#A3E635",
    "techno": "#E5E7EB",
    "empleo": "#F97316",
    "talento": "#F43F5E",
}

IMPROVE_SCHEMA = {
    "type": "object",
    "properties": {
        "suggestions": {"type": "array", "items": {"type": "string"}, "minItems": 4, "maxItems": 6},
    },
    "required": ["suggestions"],
}

IMPROVE_SYSTEM_PROMPT = (
    "Sos un consultor de growth para cuentas de Instagram de vida nocturna, "
    "eventos y marketing digital en Argentina. Te paso las estadísticas y los "
    "últimos posteos de una cuenta. Devolvé entre 4 y 6 sugerencias concretas "
    "y accionables para esta semana — nada genérico tipo 'postea más seguido'. "
    "Basate en lo que ves en los datos: horarios, tipo de contenido que "
    "funciona, engagement por post, ritmo de crecimiento. Español, tono directo."
)


def _sparkline(history: list[dict]) -> str:
    points = [h["followers_count"] for h in history[-14:]]
    if len(points) < 2:
        return ""
    lo, hi = min(points), max(points)
    span = (hi - lo) or 1
    w, h, pad = 160, 36, 4
    step = (w - 2 * pad) / (len(points) - 1)
    coords = [
        f"{pad + i * step:.1f},{pad + (h - 2 * pad) * (1 - (v - lo) / span):.1f}"
        for i, v in enumerate(points)
    ]
    return (
        f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
        f'<polyline fill="none" stroke="currentColor" stroke-width="2" '
        f'points="{" ".join(coords)}"/></svg>'
    )


def _account_payload(account: str) -> dict:
    try:
        stats = fetch_account_stats(account)
    except Exception as e:
        return {"account": account, "name": DISPLAY_NAMES[account], "error": str(e)}

    if not stats:
        return {
            "account": account, "name": DISPLAY_NAMES[account], "configured": False,
            "missing_key": ACCOUNT_CONFIG[account]["ig_id_key"],
        }

    record_snapshot(stats)
    try:
        posts = fetch_recent_media(account, limit=4)
    except Exception:
        posts = []

    return {
        "account": account,
        "name": DISPLAY_NAMES[account],
        "configured": True,
        "username": stats["username"],
        "followers_count": stats["followers_count"],
        "media_count": stats["media_count"],
        "growth": compute_growth(account),
        "sparkline": _sparkline(account_history(account)),
        "posts": [
            {
                "caption": (p.get("caption") or "").strip()[:90],
                "permalink": p.get("permalink"),
                "media_type": p.get("media_type"),
                "thumbnail": p.get("thumbnail_url") or p.get("media_url"),
                "like_count": p.get("like_count", 0),
                "comments_count": p.get("comments_count", 0),
                "timestamp": (p.get("timestamp") or "")[:10],
            }
            for p in posts
        ],
    }


@app.route("/")
def index():
    return Response(PAGE_HTML, mimetype="text/html")


@app.route("/api/accounts")
def api_accounts():
    return jsonify([_account_payload(a) for a in ACCOUNT_CONFIG])


@app.route("/api/improve/<account>", methods=["POST"])
def api_improve(account):
    if account not in ACCOUNT_CONFIG:
        return jsonify({"error": "cuenta desconocida"}), 404

    data = _account_payload(account)
    if not data.get("configured"):
        return jsonify({"error": f"{DISPLAY_NAMES[account]} no está configurada en .env"}), 400

    posts_summary = "\n".join(
        f"- \"{p['caption']}\" ({p['media_type']}, {p['like_count']} likes, "
        f"{p['comments_count']} comentarios, {p['timestamp']})"
        for p in data["posts"]
    ) or "(sin posts recientes)"

    prompt = (
        f"Cuenta: {data['name']} (@{data['username']})\n"
        f"Seguidores: {data['followers_count']} "
        f"(1d: {data['growth']['1d']}, 7d: {data['growth']['7d']}, 30d: {data['growth']['30d']})\n"
        f"Total de posts: {data['media_count']}\n\n"
        f"Últimos posteos:\n{posts_summary}"
    )

    try:
        result = call_claude(prompt, system_prompt=IMPROVE_SYSTEM_PROMPT, model="sonnet",
                              as_json=True, schema=IMPROVE_SCHEMA)
        import json
        parsed = json.loads(result) if isinstance(result, str) else result
        return jsonify(parsed)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


PAGE_HTML = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Panel Social</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@700;800&family=Inter:wght@400;500;600&display=swap"/>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Inter', sans-serif; background: #050A14; color: #E2E8F0; min-height: 100vh; padding: 32px 20px 80px; }
h1 { font-family: 'Plus Jakarta Sans', sans-serif; font-size: 26px; font-weight: 800; margin-bottom: 4px; }
.sub { color: #64748B; font-size: 13px; margin-bottom: 28px; }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 16px; max-width: 1200px; margin: 0 auto; }
.card { background: #111827; border: 1px solid #1E293B; border-radius: 16px; padding: 20px; display: flex; flex-direction: column; gap: 12px; }
.card.disabled { opacity: .55; }
.card-head { display: flex; align-items: center; gap: 10px; }
.dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
.card-head .name { font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 800; font-size: 15px; }
.card-head .handle { color: #64748B; font-size: 12px; }
.followers { font-family: 'Plus Jakarta Sans', sans-serif; font-size: 34px; font-weight: 800; }
.growth-row { display: flex; gap: 8px; flex-wrap: wrap; }
.badge { font-size: 11px; padding: 3px 8px; border-radius: 999px; background: #1E293B; color: #94A3B8; }
.badge.up { color: #4ADE80; background: rgba(74,222,128,.12); }
.badge.down { color: #F87171; background: rgba(248,113,113,.12); }
.spark { color: #6366F1; }
.posts { display: flex; flex-direction: column; gap: 8px; }
.post { display: flex; gap: 10px; align-items: center; text-decoration: none; color: inherit; }
.post img { width: 40px; height: 40px; object-fit: cover; border-radius: 8px; background: #1E293B; flex-shrink: 0; }
.post .cap { font-size: 12px; color: #CBD5E1; line-height: 1.3; }
.post .meta { font-size: 11px; color: #64748B; }
.missing { font-size: 12px; color: #94A3B8; }
.missing code { color: #C4B5FD; }
button.improve { margin-top: 4px; background: #1E293B; color: #E2E8F0; border: 1px solid #334155; border-radius: 10px; padding: 10px 14px; font-size: 13px; font-weight: 600; cursor: pointer; }
button.improve:hover { border-color: #6366F1; }
button.improve:disabled { opacity: .5; cursor: default; }
.suggestions { font-size: 13px; color: #CBD5E1; display: flex; flex-direction: column; gap: 6px; padding-top: 4px; border-top: 1px dashed #1E293B; }
.suggestions li { margin-left: 16px; }
.wa-card { max-width: 1200px; margin: 20px auto 0; background: #111827; border: 1px solid #1E293B; border-radius: 16px; padding: 20px; display: flex; justify-content: space-between; align-items: center; gap: 16px; flex-wrap: wrap; }
.wa-card .name { font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 800; }
.wa-card .note { color: #64748B; font-size: 12px; max-width: 480px; }
a.wa-btn { background: #25D366; color: #05210F; font-weight: 700; text-decoration: none; padding: 10px 16px; border-radius: 10px; font-size: 13px; white-space: nowrap; }
</style>
</head>
<body>
<h1>Panel Social</h1>
<div class="sub">Crecimiento y actividad de las 6 cuentas — actualiza cada vez que abrís la página.</div>
<div id="grid" class="grid"><div class="sub">Cargando...</div></div>

<div class="wa-card">
  <div>
    <div class="name">💬 WhatsApp de la empresa</div>
    <div class="note">No se puede embeber acá adentro (WhatsApp Web bloquea que lo metan en un iframe). Este botón te lo abre en una pestaña nueva.</div>
  </div>
  <a class="wa-btn" href="https://web.whatsapp.com/" target="_blank" rel="noopener">Abrir WhatsApp Web ↗</a>
</div>

<script>
const ACCENT = {ola:'#0EA5E9', fiestas:'#C084FC', storm:'#A3E635', techno:'#E5E7EB', empleo:'#F97316', talento:'#F43F5E'};

function growthBadge(label, val) {
  if (val === null || val === undefined) return `<span class="badge">${label}: —</span>`;
  const cls = val > 0 ? 'up' : val < 0 ? 'down' : '';
  const sign = val > 0 ? '+' : '';
  return `<span class="badge ${cls}">${label}: ${sign}${val}</span>`;
}

function renderCard(a) {
  const accent = ACCENT[a.account] || '#6366F1';
  if (a.error) {
    return `<div class="card disabled">
      <div class="card-head"><span class="dot" style="background:${accent}"></span><span class="name">${a.name}</span></div>
      <div class="missing">Error consultando la API: ${a.error}</div>
    </div>`;
  }
  if (!a.configured) {
    return `<div class="card disabled">
      <div class="card-head"><span class="dot" style="background:${accent}"></span><span class="name">${a.name}</span></div>
      <div class="missing">No configurada. Falta <code>${a.missing_key}</code> en .env</div>
    </div>`;
  }
  const posts = a.posts.map(p => `
    <a class="post" href="${p.permalink || '#'}" target="_blank" rel="noopener">
      ${p.thumbnail ? `<img src="${p.thumbnail}"/>` : '<div class="post" style="width:40px;height:40px"></div>'}
      <div>
        <div class="cap">${p.caption || '(sin texto)'}</div>
        <div class="meta">${p.timestamp} · ❤ ${p.like_count} · 💬 ${p.comments_count}</div>
      </div>
    </a>`).join('') || '<div class="missing">Sin posts recientes.</div>';

  return `<div class="card" id="card-${a.account}">
    <div class="card-head"><span class="dot" style="background:${accent}"></span>
      <div><div class="name">${a.name}</div><div class="handle">@${a.username}</div></div>
    </div>
    <div class="followers">${a.followers_count.toLocaleString('es-AR')}</div>
    <div class="growth-row">
      ${growthBadge('1d', a.growth['1d'])}
      ${growthBadge('7d', a.growth['7d'])}
      ${growthBadge('30d', a.growth['30d'])}
    </div>
    <div class="spark" style="color:${accent}">${a.sparkline || ''}</div>
    <div class="posts">${posts}</div>
    <button class="improve" onclick="improve('${a.account}', this)">✨ Mejoras</button>
    <div class="suggestions" id="sug-${a.account}" style="display:none"></div>
  </div>`;
}

async function loadAccounts() {
  const res = await fetch('/api/accounts');
  const accounts = await res.json();
  document.getElementById('grid').innerHTML = accounts.map(renderCard).join('');
}

async function improve(account, btn) {
  btn.disabled = true;
  btn.textContent = 'Pensando...';
  const box = document.getElementById('sug-' + account);
  try {
    const res = await fetch('/api/improve/' + account, { method: 'POST' });
    const data = await res.json();
    if (data.error) {
      box.innerHTML = `<div class="missing">${data.error}</div>`;
    } else {
      box.innerHTML = '<ul>' + data.suggestions.map(s => `<li>${s}</li>`).join('') + '</ul>';
    }
    box.style.display = 'block';
  } catch (e) {
    box.innerHTML = `<div class="missing">Error: ${e}</div>`;
    box.style.display = 'block';
  } finally {
    btn.disabled = false;
    btn.textContent = '✨ Mejoras';
  }
}

loadAccounts();
</script>
</body>
</html>"""


if __name__ == "__main__":
    app.run(port=5056, debug=True)
