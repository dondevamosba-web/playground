#!/usr/bin/env python3
"""
Generate a branded Storm Digital proposal PDF for a prospect.

Usage:
  python3 tools/storm_proposal.py --client "ABC Roofing" --vertical roofing \
      --budget 3000 --cpl 45 [--city "Austin TX"] [--out .tmp/proposal.pdf]

Pricing model: no retainer — 15% of ad spend, performance-based (per CLAUDE brand kit).
"""
import argparse
from datetime import date
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).parent.parent
CAL_LINK = "https://cal.com/guido-carminatti-wvudqi/15min"

TPL = """<!DOCTYPE html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Rubik:wght@400;500;700&family=Space+Grotesk:wght@500;700&family=Space+Mono&display=swap" rel="stylesheet">
<style>
@page {{ size: A4; margin: 0 }}
* {{ margin:0; box-sizing:border-box }}
body {{ font-family:'Rubik',sans-serif; color:#150f23 }}
.page {{ width:210mm; height:296mm; padding:22mm; position:relative; page-break-after:always }}
.dark {{ background:#150f23; color:#fff }}
.eyebrow {{ font-family:'Space Mono',monospace; text-transform:uppercase; letter-spacing:.18em; font-size:11px; color:#fa7faa }}
h1 {{ font-family:'Space Grotesk',sans-serif; font-size:44px; line-height:1.05; margin:14px 0 }}
h2 {{ font-family:'Space Grotesk',sans-serif; font-size:26px; margin:10px 0 18px }}
.hl {{ background:#c2ef4e; color:#150f23; padding:0 8px; border-radius:4px }}
.muted {{ color:rgba(255,255,255,.72) }} .mutedl {{ color:#5a5470 }}
.wordmark {{ font-family:'Space Grotesk',sans-serif; font-size:16px; margin-bottom:60px }}
.cards {{ display:grid; grid-template-columns:1fr 1fr; gap:14px; margin-top:18px }}
.card {{ border:1px solid #e2ddf0; border-radius:14px; padding:20px }}
.card .big {{ font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:34px; color:#422082 }}
.card .lbl {{ font-size:13px; color:#5a5470; margin-top:6px }}
table {{ width:100%; border-collapse:collapse; margin-top:14px; font-size:14px }}
td,th {{ padding:10px 12px; border-bottom:1px solid #e2ddf0; text-align:left }}
th {{ font-family:'Space Mono',monospace; font-size:11px; text-transform:uppercase; letter-spacing:.1em; color:#5a5470 }}
.foot {{ position:absolute; bottom:14mm; left:22mm; right:22mm; display:flex; justify-content:space-between;
  font-family:'Space Mono',monospace; font-size:10px; color:#9890b0 }}
ol {{ padding-left:20px; line-height:2 }}
.lime {{ color:#c2ef4e }}
</style></head><body>

<div class="page dark">
  <div class="wordmark">⚡ <b>Storm</b> <span class="muted">Digital</span></div>
  <div class="eyebrow">Proposal · {today}</div>
  <h1>Lead generation for<br><span class="hl">{client}</span></h1>
  <p class="muted" style="font-size:17px; max-width:130mm; margin-top:10px">
    Meta + Google Ads built for {vertical} contractors{city_phrase}.
    Performance-based — we earn when your phone rings, not before.</p>
  <div class="foot"><span>storm.mkt.agency</span><span>prepared for {client}</span></div>
</div>

<div class="page">
  <div class="eyebrow">The plan</div>
  <h2>What we'll run, and what it costs</h2>
  <div class="cards">
    <div class="card"><div class="big">${budget:,}</div><div class="lbl">Recommended monthly ad spend (paid to Google/Meta directly — your money, your accounts)</div></div>
    <div class="card"><div class="big">${cpl}</div><div class="lbl">Target cost per lead by day 90 (we report against this weekly)</div></div>
    <div class="card"><div class="big">{leads}</div><div class="lbl">Estimated qualified leads per month at target CPL</div></div>
    <div class="card"><div class="big">15%</div><div class="lbl">Our fee, as % of ad spend. No retainer, no setup fee, cancel monthly</div></div>
  </div>
  <h2 style="margin-top:28px">First 90 days</h2>
  <table>
    <tr><th>When</th><th>What happens</th></tr>
    <tr><td>Week 1</td><td>Tracking install (calls + forms), landing page fixes, campaign build. Live within 48h of access.</td></tr>
    <tr><td>Weeks 2–4</td><td>Learning phase: tight geo targeting, negative keywords, first creative tests.</td></tr>
    <tr><td>Months 2–3</td><td>Weekly bid/budget/creative iteration toward the ${cpl} CPL target.</td></tr>
    <tr><td>Day 90</td><td>Scale review: if CPL is at target, we scale spend 20% at a time.</td></tr>
  </table>
  <div class="foot"><span>storm.mkt.agency</span><span>2 / 3</span></div>
</div>

<div class="page">
  <div class="eyebrow">Next steps</div>
  <h2>Three things and we're live</h2>
  <ol style="font-size:16px">
    <li>Reply to this proposal or book a 15-min call: <b>{cal}</b></li>
    <li>Grant ad account + analytics access (we'll send a 5-min checklist).</li>
    <li>We launch within 48 hours. First report lands 7 days later.</li>
  </ol>
  <p class="mutedl" style="margin-top:24px; font-size:14px">Every number we see, you see — live dashboard, call recordings,
  weekly summary in plain English. If we don't perform, firing us takes one email.</p>
  <div class="foot"><span>storm.mkt.agency</span><span>3 / 3</span></div>
</div>
</body></html>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--client", required=True)
    ap.add_argument("--vertical", default="home-service")
    ap.add_argument("--city", default="")
    ap.add_argument("--budget", type=int, default=3000)
    ap.add_argument("--cpl", type=int, default=45)
    ap.add_argument("--out")
    a = ap.parse_args()

    html = TPL.format(
        client=a.client, vertical=a.vertical,
        city_phrase=f" in {a.city}" if a.city else "",
        budget=a.budget, cpl=a.cpl, leads=a.budget // a.cpl,
        today=f"{date.today():%B %Y}", cal=CAL_LINK)

    out = Path(a.out) if a.out else ROOT / ".tmp" / f"proposal_{a.client.lower().replace(' ', '_')}.pdf"
    out.parent.mkdir(exist_ok=True)
    tmp_html = out.with_suffix(".html")
    tmp_html.write_text(html)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        pg.goto(tmp_html.resolve().as_uri())
        pg.wait_for_timeout(700)
        pg.pdf(path=str(out), format="A4", print_background=True)
        b.close()
    tmp_html.unlink()
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
