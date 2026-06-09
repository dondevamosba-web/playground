"""
Generates a branded client performance report PDF from Meta Ads report data.

Reads the JSON output of pull_meta_report.py and produces a professional
weekly/monthly PDF to send to clients.

Usage:
  python3 tools/generate_client_report.py --input .tmp/meta_report_2025-05-19.json
  python3 tools/generate_client_report.py --input .tmp/meta_report_2025-05-19.json \
    --client "ABC Roofing" --out .tmp/report_abc_roofing.pdf
  python3 tools/generate_client_report.py --input .tmp/meta_report_2025-05-19.json --draft
    # --draft creates a Gmail draft with the PDF attached
"""

import argparse
import json
import os
import sys
import warnings
from datetime import date

warnings.filterwarnings("ignore")
from fpdf import FPDF

TMP_DIR = os.path.join(os.path.dirname(__file__), "..", ".tmp")

# ── Colour palette ───────────────────────────────────────────────────────────
ORANGE  = (255, 107, 53)
DARK    = (15,  23,  42)
MID     = (51,  65,  85)
LIGHT   = (100, 116, 136)
WHITE   = (255, 255, 255)
BG_CARD = (248, 250, 252)
GREEN   = (34,  197, 94)
RED     = (239, 68,  68)
BORDER  = (226, 232, 240)
BG_DARK = (15,  23,  42)

PAGE_W, PAGE_H = 210, 297
MARGIN     = 15
CONTENT_W  = PAGE_W - 2 * MARGIN

FONTS = {
    'regular': '/System/Library/Fonts/Supplemental/Arial.ttf',
    'bold':    '/System/Library/Fonts/Supplemental/Arial Bold.ttf',
    'italic':  '/System/Library/Fonts/Supplemental/Arial Italic.ttf',
}


def delta_color(current, prior):
    if prior and prior > 0:
        pct = (current - prior) / prior * 100
        return GREEN if pct >= 0 else RED, pct
    return LIGHT, 0.0


def fmt_money(v): return f"${v:,.2f}" if v is not None else "—"
def fmt_int(v):   return f"{v:,}" if v is not None else "—"
def fmt_pct(v):   return f"{v:.2f}%" if v is not None else "—"


class ReportPDF(FPDF):
    def __init__(self):
        super().__init__(format='A4')
        self.set_margins(MARGIN, MARGIN, MARGIN)
        self.set_auto_page_break(auto=True, margin=15)
        self.add_font('Arial', style='',  fname=FONTS['regular'], uni=True)
        self.add_font('Arial', style='B', fname=FONTS['bold'],    uni=True)
        self.add_font('Arial', style='I', fname=FONTS['italic'],  uni=True)

    def footer(self):
        self.set_y(-12)
        self.set_font('Arial', 'I', 7)
        self.set_text_color(*LIGHT)
        self.cell(0, 4, 'Storm Digital  ·  stormdigitalhq@gmail.com  ·  Confidential client report', align='C')

    def header_banner(self, client: str, period: str):
        self.set_fill_color(*BG_DARK)
        self.rect(0, 0, PAGE_W, 35, 'F')
        self.set_fill_color(*ORANGE)
        self.rect(0, 35, PAGE_W, 3, 'F')

        self.set_xy(MARGIN, 6)
        self.set_font('Arial', 'B', 18)
        self.set_text_color(*WHITE)
        self.cell(0, 9, 'Performance Report', align='L')

        self.set_xy(MARGIN, 16)
        self.set_font('Arial', '', 10)
        self.set_text_color(*ORANGE)
        self.cell(0, 6, f'Client: {client}  ·  {period}', align='L')

        self.set_xy(MARGIN, 25)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(150, 160, 180)
        self.cell(0, 5, f'Storm Digital  ·  Prepared {date.today().strftime("%B %d, %Y")}', align='L')

        self.set_y(42)

    def section_title(self, text: str):
        self.ln(4)
        y = self.get_y()
        self.set_fill_color(*ORANGE)
        self.rect(MARGIN, y, 3, 6, 'F')
        self.set_xy(MARGIN + 5, y)
        self.set_font('Arial', 'B', 11)
        self.set_text_color(*DARK)
        self.cell(0, 6, text.upper(), align='L')
        self.ln(8)

    def kpi_card(self, label: str, value: str, change_pct: float = None, color=None):
        w = 43
        y = self.get_y()
        x = self.get_x()

        self.set_fill_color(*BG_CARD)
        self.rect(x, y, w, 22, 'F')
        self.set_fill_color(*ORANGE)
        self.rect(x, y, w, 2, 'F')

        self.set_xy(x + 2, y + 4)
        self.set_font('Arial', '', 7)
        self.set_text_color(*LIGHT)
        self.cell(w - 4, 4, label.upper())

        self.set_xy(x + 2, y + 10)
        self.set_font('Arial', 'B', 12)
        self.set_text_color(color or DARK)
        self.cell(w - 4, 6, value)

        if change_pct is not None:
            arrow = "▲" if change_pct >= 0 else "▼"
            clr = GREEN if change_pct >= 0 else RED
            self.set_xy(x + 2, y + 17)
            self.set_font('Arial', '', 7)
            self.set_text_color(*clr)
            self.cell(w - 4, 4, f"{arrow} {abs(change_pct):.1f}% vs prior period")

        return x + w + 3   # next x position

    def campaign_table(self, campaigns: list):
        headers = ["Campaign", "Spend", "Leads", "CPL", "CTR", "CPM"]
        col_ws  = [72,         22,       16,     20,    18,    22]

        y = self.get_y()
        self.set_fill_color(*BG_DARK)
        self.set_font('Arial', 'B', 7)
        self.set_text_color(*WHITE)
        x = MARGIN
        for i, h in enumerate(headers):
            self.set_xy(x, y)
            self.cell(col_ws[i], 6, h, fill=True)
            x += col_ws[i]
        self.set_y(y + 6)

        for ri, c in enumerate(campaigns[:15]):   # max 15 rows
            y2 = self.get_y()
            fill = ri % 2 == 0
            if fill:
                self.set_fill_color(*BG_CARD)
                self.rect(MARGIN, y2, CONTENT_W, 7, 'F')

            vals = [
                c["name"][:40],
                fmt_money(c.get("spend")),
                str(c.get("leads", 0)) if c.get("leads") else "—",
                fmt_money(c.get("cpl")),
                fmt_pct(c.get("ctr")),
                fmt_money(c.get("cpm")),
            ]
            x = MARGIN
            for ci, val in enumerate(vals):
                self.set_xy(x, y2)
                if ci == 0:
                    self.set_font('Arial', '', 7)
                    self.set_text_color(*MID)
                else:
                    self.set_font('Arial', 'B' if ci in (1, 2, 3) else '', 7)
                    self.set_text_color(*DARK if ci in (1, 2, 3) else MID)
                self.cell(col_ws[ci], 7, val)
                x += col_ws[ci]
            self.set_y(y2 + 7)

        self.ln(3)

    def insights_block(self, insights: list[str]):
        for insight in insights:
            y = self.get_y()
            self.set_xy(MARGIN, y)
            self.set_font('Arial', '', 8)
            self.set_text_color(*MID)
            self.cell(5, 5, "→")
            self.multi_cell(CONTENT_W - 5, 5, insight)
            self.ln(1)

    def next_steps_block(self, steps: list[str]):
        for i, step in enumerate(steps, 1):
            y = self.get_y()
            self.set_xy(MARGIN, y)
            self.set_font('Arial', 'B', 8)
            self.set_text_color(*ORANGE)
            self.cell(6, 5, f"{i}.")
            self.set_font('Arial', '', 8)
            self.set_text_color(*MID)
            self.multi_cell(CONTENT_W - 6, 5, step)
            self.ln(1)

    def cta_block(self):
        y = self.get_y()
        self.set_fill_color(*BG_CARD)
        self.rect(MARGIN, y, CONTENT_W, 18, 'F')
        self.set_fill_color(*ORANGE)
        self.rect(MARGIN, y, 3, 18, 'F')
        self.set_xy(MARGIN + 7, y + 4)
        self.set_font('Arial', 'B', 9)
        self.set_text_color(*DARK)
        self.cell(0, 5, 'Questions or want to review results together?')
        self.set_xy(MARGIN + 7, y + 11)
        self.set_font('Arial', '', 8)
        self.set_text_color(*MID)
        self.cell(0, 5, 'Book a call: cal.com/guido-carminatti-wvudqi/15min  ·  stormdigitalhq@gmail.com')
        self.set_y(y + 21)


def generate_insights(data: dict) -> list[str]:
    s = data["summary"]
    p = data["prior_summary"]
    insights = []

    if s["leads"] and p["leads"]:
        delta = s["leads"] - p["leads"]
        if delta > 0:
            insights.append(f"Lead volume increased by {delta} compared to the prior period — positive momentum.")
        elif delta < 0:
            insights.append(f"Lead volume decreased by {abs(delta)} vs prior period. Review creative freshness and audience overlap.")

    if s["cpl"] and p["cpl"] and p["cpl"] > 0:
        pct = (s["cpl"] - p["cpl"]) / p["cpl"] * 100
        if pct < -5:
            insights.append(f"CPL improved by {abs(pct):.1f}% — efficiency is trending in the right direction.")
        elif pct > 10:
            insights.append(f"CPL increased by {pct:.1f}%. Likely cause: creative fatigue or audience saturation. Recommend refreshing top ad sets.")

    campaigns = data.get("campaigns", [])
    if campaigns:
        top = campaigns[0]
        insights.append(
            f"Top campaign by spend: '{top['name']}' at {fmt_money(top['spend'])} "
            f"with {top.get('leads', 0)} leads."
        )
        no_leads = [c for c in campaigns if c.get("leads", 0) == 0 and c.get("spend", 0) > 50]
        if no_leads:
            insights.append(
                f"{len(no_leads)} campaign(s) spent ${sum(c['spend'] for c in no_leads):,.0f} "
                f"with zero leads — recommend pausing or restructuring."
            )

    if not insights:
        insights.append("Performance is tracking within expected ranges for this period.")

    return insights


def generate_next_steps(data: dict) -> list[str]:
    steps = []
    s = data["summary"]
    campaigns = data.get("campaigns", [])

    if s.get("cpl") and s["cpl"] > 150:
        steps.append("Test new creative angles — current CPL is above benchmark. Try testimonial or before/after formats.")
    else:
        steps.append("Maintain current creative rotation and monitor frequency. Refresh any ad sets above 3.0 frequency.")

    no_leads = [c for c in campaigns if c.get("leads", 0) == 0 and c.get("spend", 0) > 50]
    if no_leads:
        steps.append(f"Pause or restructure {len(no_leads)} zero-lead campaign(s) to reallocate budget to performers.")
    else:
        steps.append("Scale budget on top-performing campaigns by 15–20% if CPL is holding below target.")

    steps.append("Review landing page conversion rate — even strong ad performance can be capped by a weak landing page.")
    return steps


def generate(data: dict, client: str, output: str):
    s = data["summary"]
    p = data["prior_summary"]
    period_str = f"{data['period']['since']} → {data['period']['until']} ({data['period']['days']}d)"

    pdf = ReportPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.header_banner(client, period_str)

    # ── KPI Cards ─────────────────────────────────────────────────────────────
    pdf.section_title("Performance Summary")
    pdf.set_x(MARGIN)

    spend_clr, spend_pct = delta_color(s["spend"], p["spend"])
    leads_clr, leads_pct = delta_color(s["leads"], p["leads"])
    cpl_clr,   cpl_pct   = delta_color(
        s["cpl"] or 0, p["cpl"] or 0
    )
    # For CPL, lower is better — invert the color
    cpl_clr = RED if cpl_pct > 0 else GREEN

    x = MARGIN
    pdf.set_xy(x, pdf.get_y())
    x = pdf.kpi_card("Total Spend",  fmt_money(s["spend"]),  spend_pct, color=DARK)
    pdf.set_xy(x, pdf.get_y() - 22)
    x = pdf.kpi_card("Total Leads",  fmt_int(s["leads"]),    leads_pct)
    pdf.set_xy(x, pdf.get_y() - 22)
    x = pdf.kpi_card("Cost Per Lead", fmt_money(s["cpl"]),   cpl_pct,   color=cpl_clr)
    pdf.set_xy(x, pdf.get_y() - 22)
    pdf.kpi_card("CTR",             fmt_pct(s["ctr"]))
    pdf.set_y(pdf.get_y() + 6)

    # Row 2
    pdf.set_xy(MARGIN, pdf.get_y())
    x = MARGIN
    pdf.set_xy(x, pdf.get_y())
    x = pdf.kpi_card("Impressions", fmt_int(s["impressions"]))
    pdf.set_xy(x, pdf.get_y() - 22)
    x = pdf.kpi_card("Clicks",      fmt_int(s["clicks"]))
    pdf.set_xy(x, pdf.get_y() - 22)
    x = pdf.kpi_card("CPC",         fmt_money(s["cpc"]))
    pdf.set_xy(x, pdf.get_y() - 22)
    pdf.kpi_card("CPM",             fmt_money(s["cpm"]))
    pdf.set_y(pdf.get_y() + 8)

    # ── Campaign breakdown ────────────────────────────────────────────────────
    if data.get("campaigns"):
        pdf.section_title("Campaign Breakdown")
        pdf.campaign_table(data["campaigns"])

    # ── Insights ──────────────────────────────────────────────────────────────
    pdf.section_title("Key Insights")
    insights = generate_insights(data)
    pdf.insights_block(insights)

    # ── Next steps ────────────────────────────────────────────────────────────
    pdf.section_title("Recommended Next Steps")
    steps = generate_next_steps(data)
    pdf.next_steps_block(steps)

    pdf.ln(4)
    pdf.cta_block()

    pdf.output(output)
    print(f"Report PDF → {output}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input",  required=True, help="Path to meta_report JSON")
    parser.add_argument("--client", default="Client", help="Client name for the report header")
    parser.add_argument("--out",    default=None)
    parser.add_argument("--draft",  action="store_true", help="Create Gmail draft with PDF attached")
    args = parser.parse_args()

    with open(args.input) as f:
        data = json.load(f)

    safe_client = args.client.replace(" ", "_")[:30]
    period = data["period"]["since"]
    output = args.out or os.path.join(TMP_DIR, f"report_{safe_client}_{period}.pdf")
    output = os.path.normpath(output)
    os.makedirs(os.path.dirname(output), exist_ok=True)

    generate(data, args.client, output)

    if args.draft:
        # Import here to avoid hard dep when not needed
        sys.path.insert(0, os.path.dirname(__file__))
        from gmail_draft import create_draft
        subject = f"Performance Report — {args.client} ({data['period']['since']} → {data['period']['until']})"
        body = (
            f"Hi,\n\n"
            f"Please find attached your paid media performance report for the period "
            f"{data['period']['since']} → {data['period']['until']}.\n\n"
            f"Highlights:\n"
            f"  • Spend: {fmt_money(data['summary']['spend'])}\n"
            f"  • Leads: {data['summary']['leads']}\n"
            f"  • CPL: {fmt_money(data['summary']['cpl'])}\n\n"
            f"Happy to walk through the results on a call. Reply here or book at "
            f"cal.com/guido-carminatti-wvudqi/15min\n\n"
            f"— Guido\nStorm Digital"
        )
        result = create_draft(to="", subject=subject, body=body, attachment=output)
        print(f"Gmail draft created: {result.get('draft_id')}")


if __name__ == "__main__":
    main()
