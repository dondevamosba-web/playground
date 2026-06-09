"""
Generates a personalized paid media audit PDF for a single prospect.

Used as a cold outreach hook — attach to the email as a "free audit."
The report shows what we found about their current ad presence, what
competitors are doing, and what an optimized campaign would look like.

Usage:
  python3 tools/generate_audit_pdf.py --input .tmp/roofing_leads.json --name "ABC Roofing"
  python3 tools/generate_audit_pdf.py --input .tmp/dental_leads.json --index 0
  python3 tools/generate_audit_pdf.py --input .tmp/landscaping_leads.json --name "Green Lawn Co" --out .tmp/audit.pdf
"""

import argparse
import json
import os
import sys
import warnings
from datetime import date

warnings.filterwarnings("ignore")
from fpdf import FPDF

# ── Colour palette ───────────────────────────────────────────────────────────
ORANGE   = (255, 107, 53)
DARK     = (15,  23,  42)
MID      = (51,  65,  85)
LIGHT    = (100, 116, 136)
WHITE    = (255, 255, 255)
BG_LIGHT = (248, 250, 252)
BG_DARK  = (15,  23,  42)
RED      = (239, 68,  68)
GREEN    = (34,  197, 94)
YELLOW   = (234, 179, 8)
BORDER   = (226, 232, 240)

# ── Layout ───────────────────────────────────────────────────────────────────
PAGE_W, PAGE_H = 210, 297
MARGIN = 15
CONTENT_W = PAGE_W - 2 * MARGIN

FONTS = {
    'regular': '/System/Library/Fonts/Supplemental/Arial.ttf',
    'bold':    '/System/Library/Fonts/Supplemental/Arial Bold.ttf',
    'italic':  '/System/Library/Fonts/Supplemental/Arial Italic.ttf',
}

# ── Vertical context ─────────────────────────────────────────────────────────
VERTICAL_CONTEXT = {
    "roofing": {
        "avg_ticket": "$8,000–$15,000",
        "avg_cpl": "$80–$120",
        "market_note": "Most homeowners search for roofers after storm events — high urgency, fast close cycle.",
        "roi_example": "Closing 1 job from 15 leads at $10K = 10x ROI on a $997/month fee.",
    },
    "hvac": {
        "avg_ticket": "$3,000–$8,000",
        "avg_cpl": "$60–$100",
        "market_note": "HVAC demand peaks in summer and winter — timing campaigns to seasonal demand is critical.",
        "roi_example": "One AC replacement job from 10 leads at $5K = 5x ROI on a $997/month fee.",
    },
    "landscaping": {
        "avg_ticket": "$500–$3,000/project (recurring)",
        "avg_cpl": "$30–$70",
        "market_note": "Landscaping customers are high-LTV — one recurring contract can be worth $5K+/year.",
        "roi_example": "Two recurring customers from 20 leads at $2K/year each = 4x ROI on $997/month.",
    },
    "plumbing": {
        "avg_ticket": "$500–$5,000",
        "avg_cpl": "$50–$90",
        "market_note": "Emergency plumbing searches have the highest intent of any home service category.",
        "roi_example": "One booked job from 10 leads at $2K = 2x ROI on a $997/month fee.",
    },
    "dental": {
        "avg_ticket": "$3,000–$8,000 (high-value cases)",
        "avg_cpl": "$80–$150",
        "market_note": "Implant and cosmetic patients have the highest lifetime value — targeting matters enormously.",
        "roi_example": "One implant case from 15 leads at $5K = 5x ROI on a $997/month fee.",
    },
    "solar": {
        "avg_ticket": "$15,000–$40,000",
        "avg_cpl": "$100–$200",
        "market_note": "Solar homeowners research for weeks before converting — retargeting is essential.",
        "roi_example": "One installation from 20 leads at $20K = 20x ROI on a $997/month fee.",
    },
    "chiropractic": {
        "avg_ticket": "$2,000–$5,000/year (per active patient)",
        "avg_cpl": "$40–$80",
        "market_note": "Chiro patients with recurring visits are worth $200–$400/month for 12+ months.",
        "roi_example": "Three recurring patients from 20 leads at $3K/year = 9x ROI on $997/month.",
    },
}

DEFAULT_CONTEXT = {
    "avg_ticket": "varies by job",
    "avg_cpl": "$50–$120",
    "market_note": "Local service businesses with exclusive leads consistently outperform shared lead platforms.",
    "roi_example": "Even a single closed job typically exceeds the monthly management fee.",
}

AD_STATUS_LABELS = {
    "none":       ("No ads detected",        RED,    "Neither Facebook Pixel nor Google Ads tag found on your website."),
    "fb_only":    ("Facebook only",          YELLOW, "Facebook Pixel detected. Google Ads not in use — opportunity to diversify."),
    "google_only":("Google Ads only",        YELLOW, "Google Ads tag detected. Facebook/Instagram not in use — opportunity to diversify."),
    "both":       ("Running on both platforms", GREEN, "Both Facebook Pixel and Google Ads detected. Focus should be on improving performance."),
    "no_website": ("No website found",       RED,    "No website detected. Harder to run digital ads without a landing page."),
    "unknown":    ("Website unreachable",    LIGHT,  "Could not access the website to check for ad tracking."),
}


class AuditPDF(FPDF):
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
        self.cell(0, 4, 'Storm Digital  |  stormdigitalhq@gmail.com  |  Confidential — prepared exclusively for this business', align='C')

    def header_banner(self, company: str, city: str):
        self.set_fill_color(*BG_DARK)
        self.rect(0, 0, PAGE_W, 35, 'F')
        # Orange accent bar
        self.set_fill_color(*ORANGE)
        self.rect(0, 35, PAGE_W, 3, 'F')

        self.set_xy(MARGIN, 7)
        self.set_font('Arial', 'B', 20)
        self.set_text_color(*WHITE)
        self.cell(0, 9, 'Paid Media Audit Report', align='L')

        self.set_xy(MARGIN, 17)
        self.set_font('Arial', '', 10)
        self.set_text_color(*ORANGE)
        self.cell(0, 6, f'Prepared for: {company}  ·  {city}', align='L')

        self.set_xy(MARGIN, 25)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(150, 160, 180)
        self.cell(0, 5, f'Storm Digital  ·  {date.today().strftime("%B %d, %Y")}', align='L')

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

    def body(self, text: str, size: int = 9):
        self.set_font('Arial', '', size)
        self.set_text_color(*MID)
        self.multi_cell(CONTENT_W, 5, text)
        self.ln(2)

    def status_badge(self, status: str):
        label, color, description = AD_STATUS_LABELS.get(
            status, ("Unknown", LIGHT, "Status could not be determined.")
        )
        y = self.get_y()
        # Badge background
        self.set_fill_color(*BG_LIGHT)
        self.rect(MARGIN, y, CONTENT_W, 18, 'F')
        # Color bar on left
        self.set_fill_color(*color)
        self.rect(MARGIN, y, 4, 18, 'F')
        # Label
        self.set_xy(MARGIN + 7, y + 3)
        self.set_font('Arial', 'B', 10)
        self.set_text_color(*color)
        self.cell(0, 5, label, align='L')
        # Description
        self.set_xy(MARGIN + 7, y + 9)
        self.set_font('Arial', '', 8)
        self.set_text_color(*MID)
        self.cell(0, 5, description, align='L')
        self.set_y(y + 20)

    def metric_row(self, label: str, value: str, note: str = ""):
        y = self.get_y()
        self.set_fill_color(*BG_LIGHT)
        self.rect(MARGIN, y, CONTENT_W, 10, 'F')
        self.set_xy(MARGIN + 3, y + 2)
        self.set_font('Arial', 'B', 8)
        self.set_text_color(*DARK)
        self.cell(70, 5, label)
        self.set_font('Arial', 'B', 8)
        self.set_text_color(*ORANGE)
        self.cell(50, 5, value)
        if note:
            self.set_font('Arial', 'I', 7)
            self.set_text_color(*LIGHT)
            self.cell(0, 5, note)
        self.set_y(y + 12)

    def pricing_table(self):
        plans = [
            ("Starter", "$997/mo", "$1,500 min", "10–15 exclusive leads"),
            ("Growth",  "$1,497/mo", "$2,500 min", "20–30 exclusive leads"),
            ("Scale",   "$2,497/mo", "$4,000 min", "40–60 exclusive leads"),
        ]
        headers = ["Plan", "Management Fee", "Ad Spend (min)", "Leads/Month"]
        col_ws = [35, 42, 42, 61]

        y = self.get_y()
        # Header
        self.set_fill_color(*BG_DARK)
        self.set_font('Arial', 'B', 8)
        self.set_text_color(*WHITE)
        x = MARGIN
        for i, h in enumerate(headers):
            self.set_xy(x, y)
            self.cell(col_ws[i], 6, h, fill=True)
            x += col_ws[i]
        self.set_y(y + 6)

        for ri, (plan, fee, spend, leads) in enumerate(plans):
            y2 = self.get_y()
            fill_color = BG_LIGHT if ri % 2 == 0 else WHITE
            self.set_fill_color(*fill_color)
            row_data = [plan, fee, spend, leads]
            x = MARGIN
            for ci, val in enumerate(row_data):
                self.set_xy(x, y2)
                if ci == 0:
                    self.set_font('Arial', 'B', 8)
                    self.set_text_color(*ORANGE)
                else:
                    self.set_font('Arial', '', 8)
                    self.set_text_color(*MID)
                self.cell(col_ws[ci], 7, val, fill=True)
                x += col_ws[ci]
            self.set_y(y2 + 7)

        self.ln(3)

    def cta_block(self):
        y = self.get_y()
        self.set_fill_color(*ORANGE)
        self.rect(MARGIN, y, CONTENT_W, 22, 'F')
        self.set_xy(MARGIN + 5, y + 4)
        self.set_font('Arial', 'B', 11)
        self.set_text_color(*WHITE)
        self.cell(0, 6, 'Ready to talk? Book a free 15-minute strategy call.')
        self.set_xy(MARGIN + 5, y + 12)
        self.set_font('Arial', '', 9)
        self.set_text_color(255, 230, 220)
        self.cell(0, 5, 'cal.com/guido-carminatti-wvudqi/15min  ·  stormdigitalhq@gmail.com')
        self.set_y(y + 25)


def find_lead(leads: list, name: str = None, index: int = None) -> dict | None:
    if index is not None:
        return leads[index] if 0 <= index < len(leads) else None
    if name:
        name_lower = name.lower()
        for l in leads:
            if name_lower in l.get("name", "").lower():
                return l
    return None


def detect_vertical(input_path: str) -> str:
    base = os.path.basename(input_path).replace("_leads.json", "")
    return base if base in VERTICAL_CONTEXT else "roofing"


def generate(lead: dict, vertical: str, output_path: str):
    company = lead.get("name", "Your Business")
    city = lead.get("city", "")
    website = lead.get("website", "—")
    phone = lead.get("phone", "—")
    rating = lead.get("rating")
    review_count = lead.get("review_count")
    ad_status = lead.get("fb_ads_status") or "unknown"
    priority = lead.get("priority", "—")
    score = lead.get("priority_score")

    ctx = VERTICAL_CONTEXT.get(vertical, DEFAULT_CONTEXT)

    pdf = AuditPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.header_banner(company, city)

    # ── Section 1: What we found ─────────────────────────────────────────────
    pdf.section_title("1. What We Found")
    pdf.body(
        f"We conducted a quick audit of {company}'s online presence to understand your current "
        f"digital marketing footprint before reaching out. Here's a summary of what we found."
    )

    pdf.metric_row("Business",      company)
    pdf.metric_row("Location",      city)
    pdf.metric_row("Website",       website if website else "None found")
    if phone and phone != "—":
        pdf.metric_row("Phone",     phone)
    if rating:
        star_label = f"{rating} ★"
        review_label = f"({review_count} reviews)" if review_count else ""
        pdf.metric_row("Google Rating", star_label, review_label)

    # ── Section 2: Ad presence ───────────────────────────────────────────────
    pdf.section_title("2. Current Ad Presence")
    pdf.status_badge(ad_status)
    pdf.ln(3)

    if ad_status == "none":
        pdf.body(
            "Your website has no Facebook Pixel or Google Ads tag installed. This tells us "
            "you're not currently running paid digital advertising — or if you are, it's not "
            "properly tracked. This is the most common situation we see with local businesses "
            "that are still growing through referrals and word of mouth."
        )
    elif ad_status in ("fb_only", "google_only"):
        pdf.body(
            "You're running ads on one platform but not the other. Businesses that diversify "
            "across Meta and Google typically see 30–50% more leads at a similar budget because "
            "they capture different intent signals — social discovery vs. active search."
        )
    elif ad_status == "both":
        pdf.body(
            "You're running on both Facebook and Google — smart. The opportunity is in optimizing "
            "performance: creative refresh cadence, audience segmentation, and landing page "
            "conversion rate. Small improvements here compound significantly at scale."
        )

    # ── Section 3: Market context ─────────────────────────────────────────────
    pdf.section_title("3. Market Context")
    pdf.body(ctx["market_note"])
    pdf.ln(2)
    pdf.metric_row("Avg. job/ticket value",   ctx["avg_ticket"])
    pdf.metric_row("Avg. cost per lead (CPL)", ctx["avg_cpl"])
    pdf.metric_row("ROI example",              ctx["roi_example"])

    # ── Section 4: What we'd do ───────────────────────────────────────────────
    pdf.section_title("4. What We'd Do Differently")
    recs = [
        "Exclusive leads only — every inquiry goes only to you, not 5 other competitors.",
        "Audience built around your specific service area in " + (city or "your market") + ".",
        "Landing pages optimized for conversion, not just traffic.",
        "Weekly reporting: CPL, leads, booked calls — no black-box agency dashboards.",
        "Month-to-month contracts with a 60-day performance guarantee.",
    ]
    for r in recs:
        pdf.set_font('Arial', '', 8)
        pdf.set_text_color(*MID)
        x = MARGIN
        pdf.set_x(x)
        pdf.cell(5, 5, "→")
        pdf.multi_cell(CONTENT_W - 5, 5, r)
        pdf.ln(1)

    # ── Section 5: Pricing ────────────────────────────────────────────────────
    pdf.section_title("5. Investment & Plans")
    pdf.body("All plans include exclusive leads, weekly reporting, and a 60-day performance guarantee.")
    pdf.pricing_table()

    # ── CTA ───────────────────────────────────────────────────────────────────
    pdf.cta_block()

    pdf.output(output_path)
    print(f"Audit PDF → {output_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to leads JSON")
    parser.add_argument("--name", default=None, help="Business name to find in leads")
    parser.add_argument("--index", type=int, default=None, help="Lead index in JSON array")
    parser.add_argument("--out", default=None, help="Output PDF path")
    parser.add_argument("--vertical", default=None, help="Override vertical detection")
    args = parser.parse_args()

    with open(args.input) as f:
        leads = json.load(f)

    if args.name is None and args.index is None:
        print("Specify --name or --index to select a lead.")
        sys.exit(1)

    lead = find_lead(leads, name=args.name, index=args.index)
    if not lead:
        print(f"Lead not found in {args.input}")
        sys.exit(1)

    vertical = args.vertical or detect_vertical(args.input)
    safe_name = (lead.get("name", "audit") or "audit").replace(" ", "_").replace("/", "-")[:30]

    os.makedirs(os.path.join(os.path.dirname(args.input), "..", ".tmp"), exist_ok=True)
    output = args.out or os.path.join(
        os.path.dirname(args.input), "..", ".tmp", f"audit_{safe_name}.pdf"
    )
    output = os.path.normpath(output)

    generate(lead, vertical, output)


if __name__ == "__main__":
    main()
