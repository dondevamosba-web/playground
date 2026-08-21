#!/usr/bin/env python3
"""Show next 30 posts to publish (approved + pending)."""
import os, sys
from pathlib import Path
from datetime import date

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from tools.sheets_client import get_services

sheets, _ = get_services()
sid = os.environ["FIESTAS_APPROVAL_SHEET_ID"]
rows = sheets.spreadsheets().values().get(
    spreadsheetId=sid, range="Queue!A2:N600").execute().get("values", [])

posts = []
for i, r in enumerate(rows, 2):
    if len(r) < 12:
        continue
    status = (r[11] or "").strip() if len(r) > 11 else ""
    posted = (r[12] or "").strip() if len(r) > 12 else ""

    if posted:
        continue
    if status not in ("approved", "pending"):
        continue

    date_str = (r[3] or "").strip()
    name = (r[2] or "").strip()
    cap = (r[7] or "").strip()[:150]
    source = (r[1] or "").strip()

    posts.append({
        "row": i,
        "date": date_str,
        "name": name,
        "cap": cap,
        "source": source,
        "status": status,
    })

posts.sort(key=lambda x: x["date"])
today = date.today().isoformat()

# Build HTML
html = """<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Fiestas — Queue</title><style>
 :root { --bg:#0d0d10; --card:#17171c; --ink:#f0f0f4; --muted:#9696a2;
   --line:#292932; --ok:#4ade80; --wait:#e2a13c; }
 * { box-sizing: border-box; }
 body { margin: 0; padding: 30px 20px 70px; background: var(--bg);
   color: var(--ink); font: 14px/1.6 -apple-system,Segoe UI,sans-serif; }
 header { max-width: 1200px; margin: 0 auto 30px; }
 h1 { margin: 0 0 8px; font-size: 28px; letter-spacing: -.02em; }
 .sub { color: var(--muted); font-size: 13px; }
 .grid { max-width: 1200px; margin: 0 auto; display: grid;
   grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 16px; }
 .post { background: var(--card); border: 1px solid var(--line);
   border-radius: 8px; padding: 16px; display: flex; flex-direction: column; }
 .status { display: inline-block; padding: 2px 8px; border-radius: 12px;
   font-size: 11px; font-weight: 600; text-transform: uppercase;
   width: fit-content; margin-bottom: 8px; }
 .approved { background: rgba(74,222,128,.2); color: var(--ok); }
 .pending { background: rgba(226,161,60,.2); color: var(--wait); }
 .past { color: #888; }
 .name { font-weight: 600; font-size: 15px; margin: 8px 0 4px; }
 .date { color: var(--muted); font-size: 12px; }
 .source { color: var(--muted); font-size: 11px; margin-top: 8px;
   padding-top: 8px; border-top: 1px solid var(--line); }
</style></head><body>

<header>
 <h1>Fiestas Queue — Next 30</h1>
 <div class="sub">
"""

approved_count = len([p for p in posts[:30] if p["status"] == "approved"])
pending_count = len([p for p in posts[:30] if p["status"] == "pending"])

html += f"{approved_count} approved (ready) · {pending_count} pending (need your OK)"
html += """</div>
</header>

<div class="grid">
"""

for i, post in enumerate(posts[:30], 1):
    is_past = post["date"] < today
    status_class = "approved" if post["status"] == "approved" else "pending"
    date_class = "past" if is_past else ""

    html += f"""<div class="post">
 <div class="status {status_class}">{post['status']}</div>
 <div class="name">{post['name'][:50]}</div>
 <div class="date {date_class}">{post['date']}</div>
 <div class="source">{post['source']}</div>
</div>
"""

html += """</div>
</body></html>"""

out = ROOT / ".tmp" / "fiestas_next_30.html"
out.write_text(html, encoding="utf-8")
print(f"✓ {out}")

# Also text
print(f"\n📋 PRÓXIMOS 30 ({approved_count} approved, {pending_count} pending)\n")
for i, post in enumerate(posts[:30], 1):
    status_emoji = "✅" if post["status"] == "approved" else "⏳"
    past = " (VENCIDA)" if post["date"] < today else ""
    print(f"{i:2}. {status_emoji} [{post['date']}]{past} {post['name'][:40]}")
