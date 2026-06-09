#!/usr/bin/env python3
"""
Weekly performance report generator.

Pulls the last 7 days of Meta Ads data (campaign level), computes key metrics,
writes an executive summary via Claude, generates a PDF, uploads to Google Drive,
and creates a Gmail draft with the Drive link + inline summary.

Requires in .env:
  META_ACCESS_TOKEN   — token with ads_read permission
  META_AD_ACCOUNT_ID  — comma-separated (e.g. act_123,act_456)

Usage:
  python3 tools/weekly_report.py                      # last 7 days
  python3 tools/weekly_report.py --days 14            # last 14 days
  python3 tools/weekly_report.py --dry-run            # PDF only, skip Drive + draft
  python3 tools/weekly_report.py --client "Acme Co"   # label the report for a specific client
"""
import argparse
import os
import sys
import tempfile
from datetime import date, timedelta
from pathlib import Path

import requests
from fpdf import FPDF

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from tools.claude_call import call_claude
from tools.gmail_draft import create_draft, build_html_body
from tools.sheets_client import get_services

GRAPH_URL = "https://graph.facebook.com/v19.0"

# ── Colour palette ─────────────────────────────────────────────────────────────
DARK   = (15,  23,  42)
MID    = (51,  65,  85)
LIGHT  = (100, 116, 136)
ACCENT = (99,  102, 241)
WHITE  = (255, 255, 255)
BG     = (248, 250, 252)
BORDER = (226, 232, 240)
GREEN  = (34,  197,  94)
RED    = (239,  68,  68)

FONTS = {
    "regular": "/System/Library/Fonts/Supplemental/Arial.ttf",
    "bold":    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "italic":  "/System/Library/Fonts/Supplemental/Arial Italic.ttf",
}


# ── Meta API ──────────────────────────────────────────────────────────────────

def fetch_insights(account_id: str, token: str, date_start: str, date_end: str) -> list:
    fields = "campaign_name,spend,impressions,clicks,actions,action_values,cpc,ctr"
    params = {
        "level": "campaign",
        "fields": fields,
        "time_range": f'{{"since":"{date_start}","until":"{date_end}"}}',
        "limit": 200,
        "access_token": token,
    }
    rows, url = [], f"{GRAPH_URL}/{account_id}/insights"
    while url:
        resp = requests.get(url, params=params, timeout=30)
        if resp.status_code != 200:
            err = resp.json().get("error", {})
            print(f"  API error: {err.get('message', resp.text)}")
            break
        data = resp.json()
        rows.extend(data.get("data", []))
        url = data.get("paging", {}).get("next")
        params = {}
    return rows


CONVERSION_ACTIONS = [
    "purchase", "offsite_conversion.fb_pixel_purchase",
    "lead",     "offsite_conversion.fb_pixel_lead",
]


def _val(row, key):
    items = {a["action_type"]: float(a["value"]) for a in (row.get(key) or [])}
    for k in CONVERSION_ACTIONS:
        if k in items:
            return items[k]
    return 0.0


def aggregate_campaigns(rows: list) -> list:
    camps = {}
    for row in rows:
        name = row.get("campaign_name", "Unknown")
        if name not in camps:
            camps[name] = {"spend": 0, "impressions": 0, "clicks": 0, "conv": 0, "rev": 0}
        camps[name]["spend"]       += float(row.get("spend", 0))
        camps[name]["impressions"] += int(row.get("impressions", 0))
        camps[name]["clicks"]      += int(row.get("clicks", 0))
        camps[name]["conv"]        += _val(row, "actions")
        camps[name]["rev"]         += _val(row, "action_values")

    results = []
    for name, m in camps.items():
        spend = m["spend"]
        conv  = m["conv"]
        rev   = m["rev"]
        clicks = m["clicks"]
        imps   = m["impressions"]
        results.append({
            "campaign":    name,
            "spend":       spend,
            "impressions": imps,
            "clicks":      clicks,
            "ctr":         clicks / imps * 100 if imps else 0,
            "cpa":         spend / conv if conv else None,
            "roas":        rev / spend  if spend else None,
            "conversions": conv,
        })
    results.sort(key=lambda r: r["spend"], reverse=True)
    return results


# ── Claude summary ────────────────────────────────────────────────────────────

def build_executive_summary(campaigns: list, date_start: str, date_end: str,
                            client: str, totals: dict) -> str:
    lines = [
        f"Total spend: ${totals['spend']:.2f}",
        f"Total conversions: {totals['conv']:.0f}",
        f"Blended CPA: ${totals['cpa']:.2f}" if totals["cpa"] else "Blended CPA: N/A",
        f"Blended ROAS: {totals['roas']:.2f}x" if totals["roas"] else "Blended ROAS: N/A",
        "",
        "Campaign breakdown:",
    ]
    for c in campaigns[:8]:
        cpa  = f"CPA ${c['cpa']:.2f}" if c["cpa"] else "no conversions"
        roas = f"ROAS {c['roas']:.2f}x" if c["roas"] else ""
        lines.append(f"  {c['campaign']}: ${c['spend']:.0f} spend, {cpa}{', ' + roas if roas else ''}")

    prompt = (
        f"You are a performance marketing analyst writing a weekly report for {client or 'the client'} "
        f"covering {date_start} to {date_end}.\n\n"
        "Here are the results:\n" + "\n".join(lines) + "\n\n"
        "Write a concise 4-bullet executive summary:\n"
        "• Bullet 1: Overall performance vs typical benchmarks\n"
        "• Bullet 2: Best-performing campaign and why it stood out\n"
        "• Bullet 3: Underperformer or area of concern\n"
        "• Bullet 4: One specific recommended action for next week\n\n"
        "Be direct and specific. No intros, no sign-offs."
    )
    return call_claude(prompt, model="haiku")


# ── PDF generation ────────────────────────────────────────────────────────────

class ReportPDF(FPDF):
    def __init__(self, title: str, subtitle: str):
        super().__init__(format="A4")
        self.set_margins(16, 16, 16)
        self.set_auto_page_break(auto=True, margin=20)
        self.add_font("Arial",   style="",  fname=FONTS["regular"], uni=True)
        self.add_font("Arial",   style="B", fname=FONTS["bold"],    uni=True)
        self.add_font("Arial",   style="I", fname=FONTS["italic"],  uni=True)
        self._title    = title
        self._subtitle = subtitle
        self.add_page()
        self._render_header()

    def _render_header(self):
        self.set_fill_color(*ACCENT)
        self.rect(0, 0, 210, 22, "F")
        self.set_xy(16, 5)
        self.set_font("Arial", "B", 14)
        self.set_text_color(*WHITE)
        self.cell(0, 7, self._title)
        self.set_xy(16, 13)
        self.set_font("Arial", "", 8)
        self.set_text_color(210, 215, 255)
        self.cell(0, 5, self._subtitle)
        self.set_y(28)

    def footer(self):
        self.set_y(-12)
        self.set_font("Arial", "", 7)
        self.set_text_color(*LIGHT)
        self.cell(0, 5, f"Page {self.page_no()} — Confidential", align="C")

    def section(self, title: str):
        self.ln(4)
        self.set_fill_color(*ACCENT)
        self.set_text_color(*WHITE)
        self.set_font("Arial", "B", 8)
        self.set_x(16)
        self.cell(178, 6, f"  {title.upper()}", fill=True, ln=True)
        self.ln(2)

    def kpi_row(self, kpis: list):
        """Render a row of KPI boxes. kpis = [(label, value), ...]"""
        box_w = 178 / len(kpis)
        y = self.get_y()
        for i, (label, value) in enumerate(kpis):
            x = 16 + i * box_w
            self.set_fill_color(*BG)
            self.set_draw_color(*BORDER)
            self.rect(x, y, box_w - 2, 18, "FD")
            self.set_xy(x + 2, y + 2)
            self.set_font("Arial", "", 7)
            self.set_text_color(*LIGHT)
            self.cell(box_w - 4, 4, label)
            self.set_xy(x + 2, y + 7)
            self.set_font("Arial", "B", 12)
            self.set_text_color(*DARK)
            self.cell(box_w - 4, 7, str(value))
        self.set_y(y + 22)

    def table(self, headers: list, rows: list, col_widths: list = None):
        w = col_widths or [178 / len(headers)] * len(headers)
        # Header
        self.set_fill_color(*DARK)
        self.set_text_color(*WHITE)
        self.set_font("Arial", "B", 7)
        self.set_x(16)
        for i, h in enumerate(headers):
            self.cell(w[i], 6, f" {h}", fill=True, border=0)
        self.ln()
        # Rows
        self.set_font("Arial", "", 7)
        for ri, row in enumerate(rows):
            self.set_fill_color(*BG if ri % 2 else WHITE)
            self.set_text_color(*MID)
            self.set_x(16)
            for i, cell in enumerate(row):
                self.cell(w[i], 5.5, f" {cell}", fill=True, border=0)
            self.ln()
        # Bottom border
        self.set_draw_color(*BORDER)
        self.set_line_width(0.2)
        self.line(16, self.get_y(), 194, self.get_y())
        self.ln(3)

    def body(self, text: str):
        self.set_font("Arial", "", 9)
        self.set_text_color(*MID)
        self.set_x(16)
        self.multi_cell(178, 5, text)
        self.ln(2)

    def bullet_list(self, bullets: list):
        self.set_font("Arial", "", 9)
        self.set_text_color(*MID)
        for b in bullets:
            b = b.lstrip("•-– ").strip()
            if not b:
                continue
            self.set_x(18)
            self.cell(4, 5, "•")
            self.set_x(22)
            self.multi_cell(172, 5, b)
        self.ln(2)


def generate_pdf(campaigns: list, totals: dict, summary: str,
                 date_start: str, date_end: str, client: str) -> Path:
    title    = f"Weekly Report — {client}" if client else "Weekly Performance Report"
    subtitle = f"Meta Ads  ·  {date_start} to {date_end}"
    pdf = ReportPDF(title, subtitle)

    # KPI summary row
    pdf.section("Key Metrics")
    pdf.kpi_row([
        ("Total Spend",    f"${totals['spend']:,.2f}"),
        ("Conversions",    f"{totals['conv']:.0f}"),
        ("Blended CPA",    f"${totals['cpa']:.2f}" if totals["cpa"] else "N/A"),
        ("Blended ROAS",   f"{totals['roas']:.2f}x" if totals["roas"] else "N/A"),
        ("Impressions",    f"{totals['impressions']:,}"),
        ("Clicks",         f"{totals['clicks']:,}"),
    ])

    # Campaign table
    pdf.section("Campaign Breakdown")
    headers = ["Campaign", "Spend", "Imps", "Clicks", "CTR", "Conv", "CPA", "ROAS"]
    widths  = [58, 18, 20, 16, 12, 14, 18, 16]
    rows = []
    for c in campaigns:
        rows.append([
            c["campaign"][:35],
            f"${c['spend']:,.0f}",
            f"{c['impressions']:,}",
            str(c["clicks"]),
            f"{c['ctr']:.1f}%",
            f"{c['conversions']:.0f}",
            f"${c['cpa']:.2f}" if c["cpa"] else "—",
            f"{c['roas']:.2f}x" if c["roas"] else "—",
        ])
    pdf.table(headers, rows, widths)

    # Executive summary
    pdf.section("Executive Summary")
    bullets = [line for line in summary.splitlines() if line.strip()]
    pdf.bullet_list(bullets)

    out_path = ROOT / ".tmp" / f"weekly_report_{date_start}_{date_end}.pdf"
    out_path.parent.mkdir(exist_ok=True)
    pdf.output(str(out_path))
    return out_path


# ── Drive upload ──────────────────────────────────────────────────────────────

def upload_to_drive(pdf_path: Path, client: str) -> str:
    sheets_svc, drive_svc = get_services()
    folder_name = f"Weekly Reports{' — ' + client if client else ''}"

    # Find or create folder
    q = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    files = drive_svc.files().list(q=q, fields="files(id)").execute().get("files", [])
    if files:
        folder_id = files[0]["id"]
    else:
        folder_id = drive_svc.files().create(
            body={"name": folder_name, "mimeType": "application/vnd.google-apps.folder"},
            fields="id"
        ).execute()["id"]

    from googleapiclient.http import MediaFileUpload
    file_meta = {"name": pdf_path.name, "parents": [folder_id]}
    media = MediaFileUpload(str(pdf_path), mimetype="application/pdf")
    file = drive_svc.files().create(body=file_meta, media_body=media, fields="id,webViewLink").execute()

    # Make publicly viewable
    drive_svc.permissions().create(
        fileId=file["id"],
        body={"type": "anyone", "role": "reader"}
    ).execute()

    return file["webViewLink"]


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--days",     type=int, default=7)
    parser.add_argument("--dry-run",  action="store_true", help="PDF only, skip Drive + draft")
    parser.add_argument("--client",   default="", help="Client name label for the report")
    args = parser.parse_args()

    token = os.getenv("META_ACCESS_TOKEN")
    account_ids_raw = os.getenv("META_AD_ACCOUNT_ID", "")
    if not token or not account_ids_raw:
        print("Missing credentials. Add to .env:")
        print("  META_ACCESS_TOKEN=<token>")
        print("  META_AD_ACCOUNT_ID=act_XXXXXXXXX")
        sys.exit(1)

    account_ids = [a.strip() for a in account_ids_raw.split(",") if a.strip()]
    date_end   = (date.today() - timedelta(days=1)).isoformat()
    date_start = (date.today() - timedelta(days=args.days)).isoformat()
    client = args.client

    print(f"Pulling {args.days}-day report: {date_start} → {date_end}")
    all_rows = []
    for account_id in account_ids:
        print(f"  {account_id}")
        all_rows.extend(fetch_insights(account_id, token, date_start, date_end))

    if not all_rows:
        print("No data returned. Check your token and account ID.")
        sys.exit(1)

    campaigns = aggregate_campaigns(all_rows)
    total_spend = sum(c["spend"] for c in campaigns)
    total_conv  = sum(c["conversions"] for c in campaigns)
    total_rev   = sum((c["roas"] or 0) * c["spend"] for c in campaigns)
    total_imps  = sum(c["impressions"] for c in campaigns)
    total_clicks = sum(c["clicks"] for c in campaigns)
    totals = {
        "spend":       total_spend,
        "conv":        total_conv,
        "cpa":         total_spend / total_conv if total_conv else None,
        "roas":        total_rev   / total_spend if total_spend else None,
        "impressions": total_imps,
        "clicks":      total_clicks,
    }

    print(f"\n  Total spend:   ${total_spend:,.2f}")
    print(f"  Conversions:   {total_conv:.0f}")
    if totals["cpa"]:  print(f"  Blended CPA:   ${totals['cpa']:.2f}")
    if totals["roas"]: print(f"  Blended ROAS:  {totals['roas']:.2f}x")
    print(f"\nGenerating executive summary...")

    summary = build_executive_summary(campaigns, date_start, date_end, client, totals)
    print(f"\n{summary}\n")

    print("Generating PDF...")
    pdf_path = generate_pdf(campaigns, totals, summary, date_start, date_end, client)
    print(f"  Saved: {pdf_path}")

    if args.dry_run:
        print("\n[dry-run] Skipping Drive upload and Gmail draft.")
        return

    print("Uploading to Google Drive...")
    drive_url = upload_to_drive(pdf_path, client)
    print(f"  URL: {drive_url}")

    subject_label = f" — {client}" if client else ""
    subject = f"Weekly Meta Ads Report{subject_label}  |  {date_start} to {date_end}"
    email_body = (
        f"Weekly report is ready for {date_start} to {date_end}.\n\n"
        f"Summary:\n{summary}\n\n"
        f"Full PDF: {drive_url}"
    )
    html = build_html_body(email_body)
    result = create_draft(to="dondevamosba@gmail.com", subject=subject, body=html, html=True)
    print(f"Gmail draft created: {result['draft_id']}")


if __name__ == "__main__":
    main()
