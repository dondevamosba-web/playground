#!/usr/bin/env python3
"""
Fetch engagement metrics for published Fiestas posts.

Reads media IDs from the sheet (column M), pulls likes/comments/shares from Graph API,
ranks by engagement, shows which events resonated.

Output: HTML dashboard + JSON log

Usage:
  python3 tools/metrics_fiestas.py                    # Fetch & render
  python3 tools/metrics_fiestas.py --csv metrics.csv  # Export to CSV
"""
import argparse
import json
import os
import sys
import csv
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

import requests
from tools.sheets_client import get_services

GRAPH = "https://graph.facebook.com/v19.0"
AR_TZ = timezone(timedelta(hours=-3))
LOG = ROOT / ".tmp" / "metrics_fiestas.json"


def fetch_metrics(media_id, token):
    """Get likes, comments, shares for a media item."""
    try:
        res = requests.get(
            f"{GRAPH}/{media_id}",
            params={"fields": "like_count,comments_count,media_product_type",
                    "access_token": token},
            timeout=30).json()
        if "error" in res:
            return None
        return {
            "likes": res.get("like_count", 0),
            "comments": res.get("comments_count", 0),
            "engagement": res.get("like_count", 0) + res.get("comments_count", 0),
        }
    except Exception as e:
        print(f"  Error fetching {media_id}: {e}")
        return None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--csv", help="Export to CSV file")
    args = p.parse_args()

    sheets, _ = get_services()
    sid = os.environ["FIESTAS_APPROVAL_SHEET_ID"]
    token = os.environ["INSTAGRAM_ACCESS_TOKEN"]

    rows = sheets.spreadsheets().values().get(
        spreadsheetId=sid, range="Queue!A2:N600").execute().get("values", [])

    metrics = []
    for i, r in enumerate(rows, 2):
        if len(r) < 13 or not r[12]:  # No media_id
            continue

        media_id = r[12].strip()
        name = (r[2] or "").strip()
        event_date = (r[3] or "").strip()
        caption = (r[7] or "").strip()[:80]

        data = fetch_metrics(media_id, token)
        if not data:
            continue

        metrics.append({
            "row": i,
            "name": name,
            "date": event_date,
            "caption": caption,
            "media_id": media_id,
            "likes": data["likes"],
            "comments": data["comments"],
            "engagement": data["engagement"],
            "fetched_at": datetime.now(tz=AR_TZ).isoformat(),
        })
        print(f"  {name:30} {data['engagement']:>3} eng (♥ {data['likes']}, 💬 {data['comments']})")

    if not metrics:
        print("Sin posts publicados con media_id")
        return 0

    # Sort by engagement
    metrics.sort(key=lambda m: m["engagement"], reverse=True)

    # Save to JSON
    LOG.parent.mkdir(parents=True, exist_ok=True)
    LOG.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n→ {LOG}")

    # Export to CSV if requested
    if args.csv:
        with open(args.csv, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["name", "date", "likes", "comments", "engagement"])
            w.writeheader()
            for m in metrics:
                w.writerow({k: m[k] for k in w.fieldnames})
        print(f"→ {args.csv}")

    # Simple HTML
    html = f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<title>Fiestas — Métricas</title><style>
 body {{ font-family: sans-serif; padding: 20px; background: #f5f5f5; }}
 table {{ width: 100%; border-collapse: collapse; background: white; }}
 th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
 th {{ background: #333; color: white; }}
 tr:hover {{ background: #f9f9f9; }}
 .eng {{ font-weight: bold; color: #d6003c; }}
</style></head><body><h1>Fiestas — Engagement</h1>
<p>Actualizado: {datetime.now(tz=AR_TZ).strftime('%Y-%m-%d %H:%M')}</p>
<table><tr><th>Evento</th><th>Fecha</th><th>❤️ Likes</th><th>💬 Comentarios</th><th class="eng">Engagement</th></tr>"""

    for m in metrics:
        html += f"""<tr>
 <td><strong>{m['name']}</strong><br><small>{m['caption']}</small></td>
 <td>{m['date']}</td>
 <td>{m['likes']}</td>
 <td>{m['comments']}</td>
 <td class="eng">{m['engagement']}</td>
</tr>"""

    html += """</table></body></html>"""
    out = ROOT / ".tmp" / "metrics_fiestas.html"
    out.write_text(html, encoding="utf-8")
    print(f"→ {out}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
