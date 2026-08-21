#!/usr/bin/env python3
"""
Show the next N pending Techno posts as a tight image grid HTML.
Usage:
  python3 tools/techno_preview_next.py          # next 20
  python3 tools/techno_preview_next.py --n 40
"""
import argparse, os, sys
from datetime import date
from pathlib import Path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
from dotenv import load_dotenv; load_dotenv(ROOT / ".env")
from tools.sheets_client import get_services

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=20)
    args = parser.parse_args()

    sheets, _ = get_services()
    sid = os.getenv("TECHNO_CONTENT_CALENDAR_SHEET_ID")
    result = sheets.spreadsheets().values().get(spreadsheetId=sid, range="A2:K400").execute()
    rows = result.get("values", [])

    today = date.today().isoformat()
    posts = []
    for row in rows:
        d = row[0].strip() if row else ""
        t = row[1].strip() if len(row)>1 else ""
        prod = row[3].strip() if len(row)>3 else ""
        media = row[8].strip() if len(row)>8 else ""
        status = row[9].strip() if len(row)>9 else ""
        if status == "posted" or not d or d < today:
            continue
        posts.append({"date": d, "time": t, "product": prod, "image": media, "status": status})

    posts.sort(key=lambda p: p["date"] + p["time"])
    posts = posts[:args.n]

    cards = ""
    for p in posts:
        img = p["image"]
        label = p["product"] or "—"
        dt = f"{p['date'][5:]} {p['time']}"
        if img:
            thumb = f'<img src="{img}" onerror="this.style.display=\'none\';this.nextSibling.style.display=\'flex\'" /><div class="ph">Sin imagen</div>'
        else:
            thumb = '<div class="ph" style="display:flex">Sin imagen</div>'
        cards += f"""<div class="card">
  <div class="img-wrap">{thumb}</div>
  <div class="meta"><div class="prod">{label}</div><div class="dt">{dt}</div></div>
</div>"""

    html = f"""<!DOCTYPE html><html><head><meta charset="UTF-8">
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ background: #060606; font-family: -apple-system, sans-serif; padding: 16px; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 8px; }}
.card {{ background: #111; border-radius: 10px; overflow: hidden; }}
.img-wrap {{ position: relative; aspect-ratio: 1; overflow: hidden; background: #1a1a1a; }}
.img-wrap img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
.ph {{ width: 100%; height: 100%; display: none; align-items: center; justify-content: center;
  font-size: 9px; color: #333; background: #111; }}
.meta {{ padding: 6px 8px; }}
.prod {{ font-size: 10px; color: #ccc; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
.dt {{ font-size: 9px; color: #555; margin-top: 2px; }}
</style></head><body>
<div class="grid">{cards}</div>
</body></html>"""

    out = ROOT / ".tmp" / "techno_next_preview.html"
    out.write_text(html)
    print(f"✓ {out}")
    import subprocess; subprocess.run(["open", str(out)])

if __name__ == "__main__":
    main()
