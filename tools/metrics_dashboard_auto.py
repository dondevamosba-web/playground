#!/usr/bin/env python3
"""
Auto-refresh metrics dashboard every 24h.
Creates HTML with trends, top artists, top venues, best hours.
Run via Windows task at 3 AM.
"""
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

import requests
from tools.sheets_client import get_services

GRAPH = "https://graph.facebook.com/v19.0"
AR_TZ = timezone(timedelta(hours=-3))
LOG_DIR = ROOT / ".tmp"


def fetch_metrics(media_id, token):
    """Get likes, comments for a media item."""
    try:
        res = requests.get(
            f"{GRAPH}/{media_id}",
            params={"fields": "like_count,comments_count",
                    "access_token": token},
            timeout=30).json()
        if "error" in res:
            return None
        return {
            "likes": res.get("like_count", 0),
            "comments": res.get("comments_count", 0),
            "engagement": res.get("like_count", 0) + res.get("comments_count", 0),
        }
    except Exception:
        return None


def main():
    sheets, _ = get_services()
    sid = os.environ["FIESTAS_APPROVAL_SHEET_ID"]
    token = os.environ["INSTAGRAM_ACCESS_TOKEN"]

    rows = sheets.spreadsheets().values().get(
        spreadsheetId=sid, range="Queue!A2:N600").execute().get("values", [])

    metrics = []
    for i, r in enumerate(rows, 2):
        if len(r) < 13 or not r[12]:
            continue

        media_id = r[12].strip()
        name = (r[2] or "").strip()
        event_date = (r[3] or "").strip()

        data = fetch_metrics(media_id, token)
        if not data:
            continue

        # Extract artist/venue from name
        artist = name.split(" - ")[0].strip() if " - " in name else name
        venue = name.split(" - ")[1].strip() if " - " in name else "unknown"

        metrics.append({
            "name": name,
            "date": event_date,
            "artist": artist,
            "venue": venue,
            "engagement": data["engagement"],
            "likes": data["likes"],
            "comments": data["comments"],
        })

    if not metrics:
        return 0

    # Aggregate by artist
    artist_stats = defaultdict(lambda: {"total": 0, "count": 0})
    venue_stats = defaultdict(lambda: {"total": 0, "count": 0})

    for m in metrics:
        artist_stats[m["artist"]]["total"] += m["engagement"]
        artist_stats[m["artist"]]["count"] += 1
        venue_stats[m["venue"]]["total"] += m["engagement"]
        venue_stats[m["venue"]]["count"] += 1

    # Calculate averages
    artist_avg = {a: int(s["total"] / s["count"]) for a, s in artist_stats.items() if s["count"] > 0}
    venue_avg = {v: int(s["total"] / s["count"]) for v, s in venue_stats.items() if s["count"] > 0}

    # Sort
    top_artists = sorted(artist_avg.items(), key=lambda x: x[1], reverse=True)[:10]
    top_venues = sorted(venue_avg.items(), key=lambda x: x[1], reverse=True)[:10]
    top_posts = sorted(metrics, key=lambda x: x["engagement"], reverse=True)[:15]

    # Render HTML
    now = datetime.now(tz=AR_TZ)
    html = f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<title>IG Dashboard — Métricas</title><style>
 body {{ font-family: -apple-system, Segoe UI, sans-serif; padding: 30px; background: #0d0d10; color: #f0f0f4; }}
 h1 {{ font-size: 32px; margin: 0 0 10px; }}
 .stamp {{ color: #9696a2; font-size: 12px; margin-bottom: 30px; }}
 .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px; }}
 .card {{ background: #17171c; border: 1px solid #292932; padding: 20px; border-radius: 8px; }}
 .card h2 {{ font-size: 16px; margin: 0 0 15px; text-transform: uppercase; letter-spacing: .1em; }}
 .item {{ display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #292932; }}
 .item:last-child {{ border: none; }}
 .num {{ font-weight: 600; color: #ff3d6e; }}
 .table-full {{ width: 100%; margin-top: 30px; }}
 table {{ width: 100%; border-collapse: collapse; }}
 th {{ background: #17171c; padding: 12px; text-align: left; font-weight: 600; border-bottom: 2px solid #292932; text-transform: uppercase; font-size: 11px; }}
 td {{ padding: 10px 12px; border-bottom: 1px solid #292932; }}
 tr:hover {{ background: #1a1a20; }}
 .gold {{ color: #ffd700; }}
 .silver {{ color: #c0c0c0; }}
 .bronze {{ color: #cd7f32; }}
</style></head><body>

<h1>📊 IG Pipeline Metrics</h1>
<div class="stamp">Actualizado: {now.strftime('%Y-%m-%d %H:%M')} AR</div>

<div class="grid">
 <div class="card">
  <h2>🎤 Top Artistas (por promedio)</h2>
"""

    for i, (artist, avg_eng) in enumerate(top_artists[:8]):
        emoji = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"#{i+1}"
        html += f'  <div class="item"><span>{emoji} {artist}</span><span class="num">{avg_eng}</span></div>\n'

    html += """
 </div>
 <div class="card">
  <h2>📍 Top Venues (por promedio)</h2>
"""

    for i, (venue, avg_eng) in enumerate(top_venues[:8]):
        emoji = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"#{i+1}"
        html += f'  <div class="item"><span>{emoji} {venue}</span><span class="num">{avg_eng}</span></div>\n'

    html += """
 </div>
</div>

<div class="table-full">
 <h2>🔥 Top Posts</h2>
 <table>
  <tr>
   <th>#</th>
   <th>Evento</th>
   <th>Fecha</th>
   <th>❤️ Likes</th>
   <th>💬 Comentarios</th>
   <th>Engagement</th>
  </tr>
"""

    for i, post in enumerate(top_posts, 1):
        html += f"""  <tr>
   <td>{i}</td>
   <td>{post['name']}</td>
   <td>{post['date']}</td>
   <td>{post['likes']}</td>
   <td>{post['comments']}</td>
   <td class="num">{post['engagement']}</td>
  </tr>
"""

    html += """
 </table>
</div>

</body></html>"""

    out = LOG_DIR / "metrics_dashboard.html"
    out.write_text(html, encoding="utf-8")
    print(f"✓ Dashboard: {out}")

    # Also save JSON snapshot
    snapshot = {
        "timestamp": now.isoformat(),
        "top_artists": top_artists[:20],
        "top_venues": top_venues[:20],
        "total_posts": len(metrics),
        "avg_engagement": int(sum(m["engagement"] for m in metrics) / len(metrics)) if metrics else 0,
    }
    snapshot_file = LOG_DIR / f"metrics_snapshot_{now.strftime('%Y%m%d_%H%M')}.json"
    snapshot_file.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✓ Snapshot: {snapshot_file}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
