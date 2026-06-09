"""
From the existing job leads, filters to smaller companies, then uses Firecrawl
to find each company's website and extract recruiter/HR contact emails.

Adds a HUNTER_API_KEY column placeholder if you later get a Hunter.io key.

Usage:
  python3 tools/find_recruiter_emails.py
  python3 tools/find_recruiter_emails.py --rescrape   # re-scrape LinkedIn first

Output: .tmp/small_company_leads.csv / .json
"""

import csv
import json
import os
import re
import sys
import time

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

TMP_DIR = os.path.join(os.path.dirname(__file__), "..", ".tmp")
INPUT_JSON = os.path.join(TMP_DIR, "recruiter_leads.json")
OUTPUT_CSV = os.path.join(TMP_DIR, "small_company_leads.csv")
OUTPUT_JSON = os.path.join(TMP_DIR, "small_company_leads.json")

FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY", "")
HUNTER_API_KEY = os.getenv("HUNTER_API_KEY", "")

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
EMAIL_BLOCKLIST = {
    "noreply", "no-reply", "donotreply", "privacy", "support",
    "example", "test", "sentry", "amazon", "google",
}

# Known large corporations to skip — not worth cold-emailing
LARGE_CORP_KEYWORDS = [
    "harman", "condé nast", "conde nast", "pandora", "pepsico", "citrix",
    "lucid motors", "bentley systems", "iherb", "california state university",
    "avery dennison", "m+c saatchi", "jobs via dice", "chamberlain advisors",
    "searchbloom",  # seo agency, not paid media focused
    "california state",
]

# Extra LinkedIn search queries targeting smaller agencies / boutique shops
EXTRA_QUERIES = [
    {"q": "paid media specialist agency remote", "location": "United States"},
    {"q": "meta ads manager remote agency", "location": "United States"},
    {"q": "facebook ads specialist boutique agency", "location": "United States"},
    {"q": "paid social media manager small agency", "location": "United States"},
    {"q": "performance marketing specialist agency startup", "location": "United States"},
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def extract_emails(text):
    found = EMAIL_RE.findall(text)
    return sorted(set(
        e for e in found
        if not any(bad in e.lower() for bad in EMAIL_BLOCKLIST)
        and len(e) < 80
    ))


def is_large_corp(company_name):
    name = company_name.lower()
    return any(kw in name for kw in LARGE_CORP_KEYWORDS)


# ---------------------------------------------------------------------------
# LinkedIn scraper (for re-scrape mode)
# ---------------------------------------------------------------------------

def scrape_linkedin_extra(pages=2):
    jobs = []
    seen = set()
    for search in EXTRA_QUERIES:
        q_enc = search["q"].replace(" ", "+")
        loc_enc = search["location"].replace(" ", "+")
        for page in range(pages):
            url = (
                "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
                f"?keywords={q_enc}&location={loc_enc}"
                "&f_JT=F&f_WT=2&sortBy=R"
                f"&start={page * 10}"
            )
            print(f"  [LinkedIn extra] '{search['q']}' page {page + 1}")
            try:
                r = requests.get(url, headers=HEADERS, timeout=15)
            except requests.RequestException as e:
                print(f"    Error: {e}")
                break
            if r.status_code != 200:
                break

            soup = BeautifulSoup(r.text, "html.parser")
            new = 0
            for card in soup.select("li"):
                title_el = card.select_one("h3.base-search-card__title")
                company_el = card.select_one("h4.base-search-card__subtitle")
                location_el = card.select_one("span.job-search-card__location")
                date_el = card.select_one("time")
                link_el = card.select_one("a.base-card__full-link")

                title = title_el.get_text(strip=True) if title_el else ""
                if not title:
                    continue
                raw_url = link_el.get("href", "") if link_el else ""
                job_url = raw_url.split("?")[0] if raw_url else ""
                if not job_url or job_url in seen:
                    continue
                seen.add(job_url)

                company = company_el.get_text(strip=True) if company_el else ""
                if is_large_corp(company):
                    continue

                jobs.append({
                    "source": "LinkedIn",
                    "title": title,
                    "company": company,
                    "location": location_el.get_text(strip=True) if location_el else "",
                    "date_posted": date_el.get("datetime", "") if date_el else "",
                    "url": job_url,
                    "company_website": "",
                    "emails_found": "",
                    "hunter_email": "",
                    "notes": "",
                })
                new += 1

            print(f"    → {new} new")
            time.sleep(2)
        time.sleep(3)
    return jobs


# ---------------------------------------------------------------------------
# Firecrawl helpers
# ---------------------------------------------------------------------------

def firecrawl_search(query, limit=3):
    if not FIRECRAWL_API_KEY:
        return []
    try:
        r = requests.post(
            "https://api.firecrawl.dev/v1/search",
            json={"query": query, "limit": limit},
            headers={"Authorization": f"Bearer {FIRECRAWL_API_KEY}", "Content-Type": "application/json"},
            timeout=20,
        )
        if r.status_code == 200:
            return r.json().get("data", [])
    except requests.RequestException:
        pass
    return []


def firecrawl_scrape(url):
    if not FIRECRAWL_API_KEY:
        return ""
    try:
        r = requests.post(
            "https://api.firecrawl.dev/v1/scrape",
            json={"url": url, "formats": ["markdown"], "onlyMainContent": True},
            headers={"Authorization": f"Bearer {FIRECRAWL_API_KEY}", "Content-Type": "application/json"},
            timeout=25,
        )
        if r.status_code == 200:
            return r.json().get("data", {}).get("markdown", "")
    except requests.RequestException:
        pass
    return ""


# ---------------------------------------------------------------------------
# Hunter.io (if API key available)
# ---------------------------------------------------------------------------

def hunter_domain_search(domain):
    if not HUNTER_API_KEY:
        return []
    try:
        r = requests.get(
            f"https://api.hunter.io/v2/domain-search",
            params={"domain": domain, "api_key": HUNTER_API_KEY, "limit": 5, "type": "personal"},
            timeout=15,
        )
        if r.status_code == 200:
            emails = r.json().get("data", {}).get("emails", [])
            return [e["value"] for e in emails if e.get("confidence", 0) >= 70]
    except requests.RequestException:
        pass
    return []


# ---------------------------------------------------------------------------
# Email finder for a single company
# ---------------------------------------------------------------------------

def find_company_emails(company_name):
    """
    1. Firecrawl search for '<company> contact email careers'
    2. Extract emails from search snippet (fast path)
    3. If no email in snippet, scrape the contact/careers URL
    4. If HUNTER_API_KEY available, also try domain search
    """
    result = {"website": "", "emails": [], "source": ""}

    # Step 1: Firecrawl search
    queries = [
        f'"{company_name}" contact email',
        f'"{company_name}" careers hiring contact',
    ]

    all_urls = []
    for query in queries:
        hits = firecrawl_search(query, limit=3)
        for hit in hits:
            url = hit.get("url", "")
            desc = hit.get("description", "") + " " + hit.get("title", "")

            # Skip LinkedIn/job boards in search results
            if any(skip in url for skip in ["linkedin.com", "indeed.com", "glassdoor", "dice.com", "remotive"]):
                continue

            # Try to extract email directly from snippet
            emails = extract_emails(desc)
            if emails:
                result["emails"].extend(emails)
                result["website"] = url
                result["source"] = "firecrawl_search_snippet"

            # Collect potential contact/careers URLs to scrape
            if any(kw in url.lower() for kw in ["contact", "about", "careers", "team", "hire"]):
                all_urls.insert(0, url)  # prioritize
            elif not result["website"] and url:
                all_urls.append(url)
                if not result["website"]:
                    result["website"] = url

        if result["emails"]:
            break
        time.sleep(1)

    # Step 2: If no email yet, scrape the best candidate URLs
    if not result["emails"] and all_urls:
        for url in all_urls[:2]:
            print(f"    Scraping {url}")
            md = firecrawl_scrape(url)
            if md:
                emails = extract_emails(md)
                if emails:
                    result["emails"].extend(emails)
                    result["website"] = url
                    result["source"] = "firecrawl_page_scrape"
                    break
            time.sleep(1.5)

    # Step 3: Hunter.io by domain
    if HUNTER_API_KEY and result["website"]:
        from urllib.parse import urlparse
        domain = urlparse(result["website"]).netloc.replace("www.", "")
        if domain:
            hunter_emails = hunter_domain_search(domain)
            if hunter_emails:
                result["emails"].extend(hunter_emails)
                result["source"] += "+hunter"

    result["emails"] = sorted(set(result["emails"]))
    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run(rescrape=False):
    os.makedirs(TMP_DIR, exist_ok=True)

    # Load existing jobs + optionally scrape more
    jobs = []

    if os.path.exists(INPUT_JSON):
        with open(INPUT_JSON) as f:
            existing = json.load(f)
        # Filter to small companies only
        for j in existing:
            if not is_large_corp(j.get("company", "")):
                jobs.append({
                    "source": j.get("source", "LinkedIn"),
                    "title": j.get("title", ""),
                    "company": j.get("company", ""),
                    "location": j.get("location", ""),
                    "date_posted": j.get("date_posted", ""),
                    "url": j.get("url", ""),
                    "company_website": "",
                    "emails_found": j.get("emails", ""),  # emails already in description
                    "hunter_email": "",
                    "notes": "",
                })
        print(f"Loaded {len(jobs)} small/mid companies from existing data")

    if rescrape:
        print("\n=== Scraping extra LinkedIn queries for smaller agencies ===")
        extra = scrape_linkedin_extra(pages=2)
        # Deduplicate by URL
        existing_urls = {j["url"] for j in jobs}
        new = [j for j in extra if j["url"] not in existing_urls]
        jobs.extend(new)
        print(f"Added {len(new)} new jobs from extra queries")

    print(f"\nTotal small/mid companies to process: {len(jobs)}")

    # Find emails for companies that don't have them yet
    needs_email = [j for j in jobs if not j.get("emails_found")]
    print(f"Companies needing email lookup: {len(needs_email)}")
    print(f"Companies already have emails:  {len(jobs) - len(needs_email)}")

    print("\n=== Finding emails via Firecrawl ===")
    for i, job in enumerate(needs_email, 1):
        company = job["company"]
        print(f"  [{i}/{len(needs_email)}] {company}")

        found = find_company_emails(company)
        job["company_website"] = found["website"]
        job["emails_found"] = ", ".join(found["emails"])
        job["notes"] = found["source"]

        if found["emails"]:
            print(f"    Found: {', '.join(found['emails'])}")
        else:
            print(f"    No emails found")

        time.sleep(2)

    # Sort: jobs with emails first
    with_emails = [j for j in jobs if j["emails_found"]]
    without_emails = [j for j in jobs if not j["emails_found"]]
    sorted_jobs = with_emails + without_emails

    # Save
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(sorted_jobs, f, ensure_ascii=False, indent=2)

    fields = [
        "source", "title", "company", "location", "date_posted",
        "emails_found", "company_website", "hunter_email", "notes", "url",
    ]
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(sorted_jobs)

    print(f"\n{'='*70}")
    print(f"RESULTS")
    print(f"{'='*70}")
    print(f"Total companies:     {len(jobs)}")
    print(f"With emails:         {len(with_emails)}")
    print(f"Without emails:      {len(without_emails)}")
    print(f"\nSaved:")
    print(f"  CSV:  {OUTPUT_CSV}")
    print(f"  JSON: {OUTPUT_JSON}")

    if with_emails:
        print(f"\n{'='*70}")
        print(f"LEADS WITH EMAILS ({len(with_emails)})")
        print(f"{'='*70}")
        for j in with_emails:
            print(f"\n  {j['title']} @ {j['company']}")
            print(f"  Email(s): {j['emails_found']}")
            print(f"  Apply:    {j['url']}")

    return sorted_jobs


if __name__ == "__main__":
    rescrape = "--rescrape" in sys.argv
    run(rescrape=rescrape)
