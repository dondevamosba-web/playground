"""
Scrapes email addresses from roofing lead websites.
Strategy: requests → contact/about pages → regex extract emails.
Falls back to Firecrawl API for JS-heavy sites that return thin HTML.

Updates .tmp/roofing_leads.json with an "email" field.

Usage:
  python3 tools/scrape_emails.py                  # all leads without email
  python3 tools/scrape_emails.py --status none    # only no-pixel leads
  python3 tools/scrape_emails.py --limit 20
"""

import argparse
import json
import os
import re
import random
import ssl
import time
import urllib.request
import urllib.parse

from dotenv import load_dotenv

load_dotenv()

DEFAULT_LEADS_PATH = os.path.join(os.path.dirname(__file__), "..", ".tmp", "roofing_leads.json")
FIRECRAWL_KEY = os.getenv("FIRECRAWL_API_KEY", "")

CONTACT_PATHS = ["/contact", "/contact-us", "/about", "/about-us", "/get-in-touch", "/free-estimate", "/estimate"]

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")

# Emails to ignore (generic / CMS artifacts)
IGNORE_DOMAINS = {"sentry.io", "example.com", "wixpress.com", "squarespace.com",
                  "wordpress.com", "godaddy.com", "google.com", "facebook.com",
                  "schema.org", "w3.org"}
IGNORE_PREFIXES = {"noreply", "no-reply", "donotreply", "support@", "help@",
                   "privacy@", "legal@", "abuse@", "postmaster@"}

# File extensions mistakenly captured as TLDs (e.g. chosen-sprite@2x.png)
IGNORE_TLDS = {"png", "jpg", "jpeg", "gif", "svg", "webp", "ico", "bmp",
               "blink", "mhtml", "html", "css", "js", "json", "xml", "pdf"}


def is_valid_email(email: str) -> bool:
    email = email.lower()
    domain = email.split("@")[-1]
    tld = domain.rsplit(".", 1)[-1]
    if domain in IGNORE_DOMAINS:
        return False
    if tld in IGNORE_TLDS:
        return False
    if any(email.startswith(p) for p in IGNORE_PREFIXES):
        return False
    if len(email) > 80:
        return False
    return True


def fetch_html(url: str, timeout: int = 10) -> str:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; contact-finder/1.0)"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
            return r.read(200_000).decode("utf-8", errors="ignore")
    except Exception:
        return ""


def firecrawl_fetch(url: str) -> str:
    if not FIRECRAWL_KEY:
        return ""
    import json as _json
    api_url = "https://api.firecrawl.dev/v1/scrape"
    payload = _json.dumps({"url": url, "formats": ["html"]}).encode()
    req = urllib.request.Request(
        api_url,
        data=payload,
        headers={
            "Authorization": f"Bearer {FIRECRAWL_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            data = _json.loads(r.read())
            return data.get("data", {}).get("html", "")
    except Exception:
        return ""


def extract_emails(html: str) -> list[str]:
    found = EMAIL_RE.findall(html)
    seen = set()
    result = []
    for e in found:
        e = e.lower().rstrip(".")
        if e not in seen and is_valid_email(e):
            seen.add(e)
            result.append(e)
    return result


def get_base_url(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"


def scrape_lead_email(website: str):
    base = get_base_url(website)
    urls_to_try = [website] + [base + path for path in CONTACT_PATHS]

    all_emails = []
    for url in urls_to_try:
        html = fetch_html(url)

        # If homepage returns very little content, try Firecrawl
        if url == website and len(html) < 3000:
            html = firecrawl_fetch(url) or html

        emails = extract_emails(html)
        all_emails.extend(emails)

        if emails:
            break  # Found something — stop here
        time.sleep(random.uniform(0.3, 0.7))

    if not all_emails:
        return None

    # Prefer emails from the company's own domain
    domain = urllib.parse.urlparse(website).netloc.replace("www.", "")
    own_domain = [e for e in all_emails if domain in e]
    return own_domain[0] if own_domain else all_emails[0]


def load_leads(path: str) -> list[dict]:
    with open(path) as f:
        return json.load(f)


def save_leads(leads: list[dict], path: str):
    with open(path, "w") as f:
        json.dump(leads, f, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--status", default=None, help="Filter by fb_ads_status (e.g. none, google_only)")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--input", default=None, help="Path to leads JSON (default: roofing_leads.json)")
    args = parser.parse_args()

    leads_path = args.input if args.input else DEFAULT_LEADS_PATH
    leads = load_leads(leads_path)

    targets = [
        l for l in leads
        if l.get("website")
        and l.get("email") is None
        and (args.status is None or l.get("fb_ads_status") == args.status)
    ]
    if args.limit:
        targets = targets[: args.limit]

    print(f"Scraping emails for {len(targets)} leads...")
    found = 0

    for i, lead in enumerate(targets):
        email = scrape_lead_email(lead["website"])
        lead["email"] = email
        status = email if email else "not found"
        found += 1 if email else 0
        print(f"  [{i+1}/{len(targets)}] {lead['name'][:38]:<38} → {status}")

        if (i + 1) % 10 == 0:
            save_leads(leads, leads_path)

        time.sleep(random.uniform(0.8, 1.8))

    save_leads(leads, leads_path)
    print(f"\nDone. Found emails for {found}/{len(targets)} leads.")


if __name__ == "__main__":
    main()
