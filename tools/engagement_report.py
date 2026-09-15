#!/usr/bin/env python3
"""
Weekly engagement report across the 6 Instagram accounts.

Pulls the last 30 posts per account from the Graph API and computes:
  - average likes/comments per account (7d vs 30d trend)
  - top 3 and flop 3 posts per account
  - best posting hours (median engagement by hour bucket)

Output: .tmp/engagement_report.html (+ Gmail draft summary with --email).
Scheduled Mondays via launchd. Uses claude nothing — pure data.

Usage:
  python3 tools/engagement_report.py [--email]
"""
import argparse
import html
import os
import statistics
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

AR = timezone(timedelta(hours=-3))
GRAPH = "https://graph.facebook.com/v19.0"
TOKEN = os.environ["INSTAGRAM_ACCESS_TOKEN"]

ACCOUNTS = {
    "Ola Digital": "INSTAGRAM_BUSINESS_ACCOUNT_ID",
    "Storm": "STORM_INSTAGRAM_BUSINESS_ACCOUNT_ID",
    "Fiestas": "FIESTAS_INSTAGRAM_BUSINESS_ACCOUNT_ID",
    "Techno": "TECHNO_INSTAGRAM_BUSINESS_ACCOUNT_ID",
    "Empleo": "OLA_EMPLEO_INSTAGRAM_BUSINESS_ACCOUNT_ID",
    "Talento USA": "TALENTO_USA_INSTAGRAM_BUSINESS_ACCOUNT_ID",
}


def fetch(ig_id):
    r = requests.get(f"{GRAPH}/{ig_id}/media", params={
        "fields": "caption,like_count,comments_count,timestamp,media_type,permalink",
        "limit": 30, "access_token": TOKEN}, timeout=20)
    posts = r.json().get("data", [])
    for p in posts:
        p["eng"] = p.get("like_count", 0) + 3 * p.get("comments_count", 0)
        p["dt"] = datetime.fromisoformat(p["timestamp"].replace("+0000", "+00:00")).astimezone(AR)
    return posts


def account_stats(posts):
    now = datetime.now(AR)
    last7 = [p for p in posts if now - p["dt"] <= timedelta(days=7)]
    ranked = sorted(posts, key=lambda p: p["eng"], reverse=True)
    by_hour = {}
    for p in posts:
        by_hour.setdefault(p["dt"].hour // 3 * 3, []).append(p["eng"])
    best_hours = sorted(by_hour.items(), key=lambda kv: -statistics.median(kv[1]))[:2]
    return {
        "n": len(posts), "n7": len(last7),
        "avg30": statistics.mean([p["eng"] for p in posts]) if posts else 0,
        "avg7": statistics.mean([p["eng"] for p in last7]) if last7 else 0,
        "top": ranked[:3], "flop": ranked[-3:] if len(ranked) > 5 else [],
        "best_hours": [f"{h:02d}-{h+3:02d}h (mediana {statistics.median(v):.0f})" for h, v in best_hours],
    }


def post_line(p):
    cap = html.escape((p.get("caption") or "(sin caption)")[:70])
    return (f'<li>❤️ {p.get("like_count",0)} · 💬 {p.get("comments_count",0)} · '
            f'{p["dt"]:%d/%m %H:%M} · <a href="{p.get("permalink","")}">{cap}</a></li>')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--email", action="store_true")
    a = ap.parse_args()

    sections, summary = [], []
    for name, env in ACCOUNTS.items():
        ig_id = os.environ.get(env, "")
        if not ig_id:
            continue
        try:
            posts = fetch(ig_id)
        except Exception as e:
            summary.append(f"- {name}: ERROR {str(e)[:60]}")
            continue
        if not posts:
            continue
        s = account_stats(posts)
        trend = "↑" if s["avg7"] > s["avg30"] * 1.1 else ("↓" if s["avg7"] < s["avg30"] * 0.9 else "→")
        summary.append(f"- {name}: {s['n7']} posts esta semana · engagement prom 7d {s['avg7']:.0f} vs 30d {s['avg30']:.0f} {trend} · mejores horas: {', '.join(s['best_hours'])}")
        sections.append(
            f"<h2>{name}</h2><p>{html.escape(summary[-1][2:])}</p>"
            f"<h4>Top 3</h4><ul>{''.join(post_line(p) for p in s['top'])}</ul>"
            + (f"<h4>Flop 3</h4><ul>{''.join(post_line(p) for p in s['flop'])}</ul>" if s["flop"] else ""))

    now = datetime.now(AR)
    doc = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>Engagement</title><style>
    body{{font-family:-apple-system,sans-serif;background:#0f172a;color:#e2e8f0;margin:24px;max-width:820px}}
    a{{color:#60a5fa;text-decoration:none}} h2{{border-bottom:2px solid #334155;padding-bottom:4px}}
    li{{margin:4px 0;font-size:14px}} h4{{margin:10px 0 4px;color:#94a3b8}}</style></head><body>
    <h1>Engagement semanal — {now:%d/%m/%Y}</h1>
    <p>engagement = likes + 3×comentarios · últimos 30 posts por cuenta</p>
    {''.join(sections)}</body></html>"""
    out = ROOT / ".tmp" / "engagement_report.html"
    out.write_text(doc)
    body = "\n".join(summary)
    print(body)
    print(f"\n→ {out}")

    if a.email:
        from gmail_draft import create_draft
        create_draft(to="carminattiguido@gmail.com",
                     subject=f"Engagement semanal {now:%d/%m}",
                     body=body + f"\n\nDetalle: abrir {out}")
        print("(Draft creado en Gmail)")


if __name__ == "__main__":
    main()
