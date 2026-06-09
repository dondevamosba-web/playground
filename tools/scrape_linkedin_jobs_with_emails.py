"""
Scrapes paid media specialist job listings from LinkedIn, Indeed, We Work Remotely, and Remotive.

LinkedIn:
  - keywords: paid media specialist
  - job type: full-time (f_JT=F)
  - work type: remote (f_WT=2)
  - location: United States (geoId=103644278)
  - sorted by: recent

Indeed (via Firecrawl for JS-rendered pages):
  - q: paid media specialist
  - l: Remote United States

We Work Remotely:
  - RSS feed for remote marketing jobs, filtered by paid media/meta/facebook keywords

Remotive:
  - Public JSON API, marketing category, multiple search queries

Fetches each job description and extracts any recruiter emails.
Saves results to .tmp/recruiter_leads.csv and .tmp/recruiter_leads.json.

Usage:
  python3 tools/scrape_linkedin_jobs_with_emails.py
  python3 tools/scrape_linkedin_jobs_with_emails.py --pages 5
  python3 tools/scrape_linkedin_jobs_with_emails.py --source linkedin
  python3 tools/scrape_linkedin_jobs_with_emails.py --source indeed
  python3 tools/scrape_linkedin_jobs_with_emails.py --source wwr
  python3 tools/scrape_linkedin_jobs_with_emails.py --source remotive
"""

import csv
import json
import os
import re
import sys
import time
import xml.etree.ElementTree as ET
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

TMP_DIR = os.path.join(os.path.dirname(__file__), "..", ".tmp")
OUTPUT_CSV = os.path.join(TMP_DIR, "recruiter_leads.csv")
OUTPUT_JSON = os.path.join(TMP_DIR, "recruiter_leads.json")

FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY", "")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
EMAIL_BLOCKLIST = {
    "noreply", "no-reply", "donotreply", "privacy", "support",
    "info", "jobs", "careers", "talent", "example", "test",
}


def extract_emails(text):
    found = EMAIL_RE.findall(text)
    return sorted(set(
        e for e in found
        if not any(bad in e.lower() for bad in EMAIL_BLOCKLIST)
    ))


# ---------------------------------------------------------------------------
# LinkedIn (public guest API — no auth needed)
# ---------------------------------------------------------------------------

def scrape_linkedin(pages=3):
    base = (
        "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
        "?keywords=paid+media+specialist"
        "&f_JT=F"
        "&f_WT=2"
        "&geoId=103644278"
        "&sortBy=R"
    )
    jobs = []
    seen = set()

    for page in range(pages):
        url = f"{base}&start={page * 10}"
        print(f"  [LinkedIn] page {page + 1}")

        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
        except requests.RequestException as e:
            print(f"    Request error: {e}")
            break

        if r.status_code != 200:
            print(f"    HTTP {r.status_code} — stopping")
            break

        soup = BeautifulSoup(r.text, "html.parser")
        cards = soup.select("li")
        if not cards:
            print("    No cards — stopping")
            break

        new = 0
        for card in cards:
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

            jobs.append({
                "source": "LinkedIn",
                "title": title,
                "company": company_el.get_text(strip=True) if company_el else "",
                "location": location_el.get_text(strip=True) if location_el else "",
                "date_posted": date_el.get("datetime", "") if date_el else "",
                "url": job_url,
                "description_preview": "",
                "emails": "",
                "recruiter_name": "",
                "recruiter_title": "",
            })
            new += 1

        print(f"    → {new} new (total: {len(jobs)})")
        time.sleep(2)

    return jobs


def fetch_linkedin_detail(job):
    try:
        r = requests.get(job["url"], headers=HEADERS, timeout=15)
    except requests.RequestException:
        return

    if r.status_code != 200:
        return

    soup = BeautifulSoup(r.text, "html.parser")

    desc_el = (
        soup.select_one("div.show-more-less-html__markup")
        or soup.select_one("div.description__text")
    )
    desc_text = desc_el.get_text(separator=" ", strip=True) if desc_el else ""
    job["description_preview"] = desc_text[:500]

    emails = extract_emails(desc_text)
    job["emails"] = ", ".join(emails)

    recruiter_el = soup.select_one("div.hirer-card__hirer-information")
    if recruiter_el:
        name_el = recruiter_el.select_one("span.hirer-card__hirer-name") or recruiter_el.select_one("a")
        title_el = recruiter_el.select_one("span.hirer-card__hirer-title")
        job["recruiter_name"] = name_el.get_text(strip=True) if name_el else ""
        job["recruiter_title"] = title_el.get_text(strip=True) if title_el else ""


# ---------------------------------------------------------------------------
# Indeed (via Firecrawl for JS-rendered content)
# ---------------------------------------------------------------------------

def firecrawl_scrape(url):
    """Use Firecrawl to scrape a URL and return markdown text."""
    if not FIRECRAWL_API_KEY:
        return None

    endpoint = "https://api.firecrawl.dev/v1/scrape"
    payload = {
        "url": url,
        "formats": ["markdown"],
        "onlyMainContent": True,
    }
    headers = {
        "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        r = requests.post(endpoint, json=payload, headers=headers, timeout=30)
        if r.status_code == 200:
            data = r.json()
            return data.get("data", {}).get("markdown", "")
        else:
            print(f"    Firecrawl HTTP {r.status_code}: {r.text[:200]}")
            return None
    except requests.RequestException as e:
        print(f"    Firecrawl error: {e}")
        return None


def scrape_indeed(pages=3):
    """Scrape Indeed jobs using Firecrawl (handles JS rendering)."""
    if not FIRECRAWL_API_KEY:
        print("  [Indeed] No FIRECRAWL_API_KEY — skipping")
        return []

    jobs = []
    seen = set()

    for page in range(pages):
        start = page * 10
        url = (
            f"https://www.indeed.com/jobs"
            f"?q=paid+media+specialist"
            f"&l=Remote"
            f"&sc=0kf%3Aattr(DSQF7)%3B"  # Remote filter
            f"&fromage=14"  # last 14 days
            f"&start={start}"
        )

        print(f"  [Indeed] page {page + 1}")
        markdown = firecrawl_scrape(url)

        if not markdown:
            print("    No content returned — stopping")
            break

        # Parse job links from markdown
        # Indeed job URLs look like /rc/clk?jk=... or /viewjob?jk=...
        job_ids = re.findall(r'jk=([a-f0-9]{16})', markdown)
        job_titles_raw = re.findall(r'\[([^\]]+)\]\(https://www\.indeed\.com/rc/clk[^\)]+\)', markdown)

        # Also try to parse structured job entries
        lines = markdown.split("\n")
        current_title = ""
        current_company = ""

        new = 0
        for jk in set(job_ids):
            if jk in seen:
                continue
            seen.add(jk)

            job_url = f"https://www.indeed.com/viewjob?jk={jk}"
            jobs.append({
                "source": "Indeed",
                "title": "",  # filled in detail fetch
                "company": "",
                "location": "Remote",
                "date_posted": "",
                "url": job_url,
                "description_preview": "",
                "emails": "",
                "recruiter_name": "",
                "recruiter_title": "",
            })
            new += 1

        print(f"    → {new} new (total: {len(jobs)})")
        time.sleep(2)

    return jobs


def fetch_indeed_detail(job):
    """Fetch an Indeed job detail page via Firecrawl."""
    markdown = firecrawl_scrape(job["url"])
    if not markdown:
        return

    # Extract title (usually first H1/H2 in markdown)
    title_match = re.search(r'^#{1,2}\s+(.+)$', markdown, re.MULTILINE)
    if title_match and not job["title"]:
        job["title"] = title_match.group(1).strip()

    # Extract company name
    company_match = re.search(r'\*\*([^\*]+)\*\*', markdown)
    if company_match and not job["company"]:
        job["company"] = company_match.group(1).strip()

    # Description preview
    job["description_preview"] = markdown[:500].replace("\n", " ").strip()

    # Extract emails
    emails = extract_emails(markdown)
    job["emails"] = ", ".join(emails)


# ---------------------------------------------------------------------------
# We Work Remotely (RSS feed)
# ---------------------------------------------------------------------------

# Title keywords that must match for a WWR/Remotive job to be considered relevant
PAID_MEDIA_TITLE_KEYWORDS = [
    "paid media", "meta ads", "facebook ads", "paid social",
    "media buyer", "fb ads", "performance marketing",
    "paid advertising", "ppc specialist", "social media buyer",
]


def scrape_wwr():
    # WWR RSS title format: "Company Name: Job Title"
    rss_url = "https://weworkremotely.com/remote-jobs.rss"
    print(f"  [WWR] Fetching full jobs RSS…")
    try:
        r = requests.get(rss_url, headers=HEADERS, timeout=15)
    except requests.RequestException as e:
        print(f"    Request error: {e}")
        return []

    if r.status_code != 200:
        print(f"    HTTP {r.status_code} — skipping")
        return []

    try:
        root = ET.fromstring(r.content)
    except ET.ParseError as e:
        print(f"    XML parse error: {e}")
        return []

    jobs = []
    seen = set()

    for item in root.findall(".//item"):
        raw_title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        pub_date = (item.findtext("pubDate") or "")[:16]
        description_html = (item.findtext("description") or "")
        description_text = BeautifulSoup(description_html, "html.parser").get_text(" ", strip=True)

        if not link or link in seen:
            continue

        # WWR title format: "Company Name: Job Title"
        company = ""
        job_title = raw_title
        if ":" in raw_title:
            company, job_title = raw_title.split(":", 1)
            company = company.strip()
            job_title = job_title.strip()

        # Filter strictly by title keywords — avoids false matches in descriptions
        title_lower = job_title.lower()
        if not any(kw in title_lower for kw in PAID_MEDIA_TITLE_KEYWORDS):
            continue

        seen.add(link)
        emails = extract_emails(description_text)

        jobs.append({
            "source": "WeWorkRemotely",
            "title": job_title,
            "company": company,
            "location": "Remote",
            "date_posted": pub_date,
            "url": link,
            "description_preview": description_text[:500],
            "emails": ", ".join(emails),
            "recruiter_name": "",
            "recruiter_title": "",
        })

    print(f"    → {len(jobs)} relevant jobs")
    return jobs


# ---------------------------------------------------------------------------
# Remotive (public JSON API)
# ---------------------------------------------------------------------------

REMOTIVE_QUERIES = [
    "paid media meta",
    "facebook ads specialist",
    "meta ads",
    "paid social media",
    "performance marketing meta",
]

REMOTIVE_LOC_ACCEPT = ["usa", "us", "canada", "ca", "americas", "north america", "worldwide", "anywhere", ""]


def scrape_remotive():
    jobs = []
    seen = set()

    for q in REMOTIVE_QUERIES:
        q_enc = q.replace(" ", "+")
        url = f"https://remotive.com/api/remote-jobs?category=marketing&search={q_enc}"
        print(f"  [Remotive] '{q}'")
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
        except requests.RequestException as e:
            print(f"    Error: {e}")
            time.sleep(1)
            continue

        if r.status_code != 200:
            print(f"    HTTP {r.status_code}")
            time.sleep(1)
            continue

        for j in r.json().get("jobs", []):
            job_url = j.get("url", "")
            if not job_url or job_url in seen:
                continue

            loc = j.get("candidate_required_location", "Worldwide").lower()
            if not any(a in loc for a in REMOTIVE_LOC_ACCEPT):
                continue

            # Only keep jobs where the title is actually relevant
            title_lower = j.get("title", "").lower()
            if not any(kw in title_lower for kw in PAID_MEDIA_TITLE_KEYWORDS):
                continue

            description_text = BeautifulSoup(j.get("description", ""), "html.parser").get_text(" ", strip=True)
            emails = extract_emails(description_text)
            seen.add(job_url)
            jobs.append({
                "source": "Remotive",
                "title": j.get("title", ""),
                "company": j.get("company_name", ""),
                "location": j.get("candidate_required_location", "Worldwide"),
                "date_posted": (j.get("publication_date") or "")[:10],
                "url": job_url,
                "description_preview": description_text[:500],
                "emails": ", ".join(emails),
                "recruiter_name": "",
                "recruiter_title": "",
            })

        time.sleep(1.5)

    print(f"    → {len(jobs)} total Remotive jobs")
    return jobs


# ---------------------------------------------------------------------------
# Jobicy (public JSON API)
# ---------------------------------------------------------------------------

JOBICY_TAGS = ["paid media", "facebook ads", "meta ads", "paid social", "performance marketing"]
JOBICY_LOC_ACCEPT = ["usa", "us ", "worldwide", "anywhere", "north america", "canada", "remote", ""]


def scrape_jobicy():
    jobs = []
    seen = set()

    for tag in JOBICY_TAGS:
        tag_enc = tag.replace(" ", "+")
        url = f"https://jobicy.com/api/v2/remote-jobs?count=50&tag={tag_enc}"
        print(f"  [Jobicy] '{tag}'")
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
        except requests.RequestException as e:
            print(f"    Error: {e}")
            time.sleep(1)
            continue

        if r.status_code != 200:
            print(f"    HTTP {r.status_code}")
            time.sleep(1)
            continue

        for j in r.json().get("jobs", []):
            job_url = j.get("url", "")
            if not job_url or job_url in seen:
                continue

            geo = j.get("jobGeo", "").lower()
            if geo and not any(a in geo for a in JOBICY_LOC_ACCEPT):
                continue

            title = j.get("jobTitle", "")
            if not any(kw in title.lower() for kw in PAID_MEDIA_TITLE_KEYWORDS):
                continue

            seen.add(job_url)
            desc_html = j.get("jobDescription", j.get("jobExcerpt", ""))
            description_text = BeautifulSoup(desc_html, "html.parser").get_text(" ", strip=True)
            emails = extract_emails(description_text)

            jobs.append({
                "source": "Jobicy",
                "title": title,
                "company": j.get("companyName", ""),
                "location": j.get("jobGeo", "Remote"),
                "date_posted": (j.get("pubDate") or "")[:10],
                "url": job_url,
                "description_preview": description_text[:500],
                "emails": ", ".join(emails),
                "recruiter_name": "",
                "recruiter_title": "",
            })

        time.sleep(1.5)

    print(f"    → {len(jobs)} total Jobicy jobs")
    return jobs


# ---------------------------------------------------------------------------
# RemoteOK (public JSON API)
# ---------------------------------------------------------------------------

REMOTEOK_TAGS = ["marketing", "paid-social", "ppc", "advertising"]


def scrape_remoteok():
    jobs = []
    seen = set()

    for tag in REMOTEOK_TAGS:
        url = f"https://remoteok.com/api?tag={tag}"
        print(f"  [RemoteOK] tag='{tag}'")
        try:
            r = requests.get(url, headers=HEADERS, timeout=20)
        except requests.RequestException as e:
            print(f"    Error: {e}")
            time.sleep(2)
            continue

        if r.status_code != 200:
            print(f"    HTTP {r.status_code}")
            time.sleep(2)
            continue

        for j in r.json():
            if not isinstance(j, dict) or "position" not in j:
                continue

            job_url = j.get("url", "")
            if not job_url or job_url in seen:
                continue

            title = j.get("position", "")
            if not any(kw in title.lower() for kw in PAID_MEDIA_TITLE_KEYWORDS):
                continue

            seen.add(job_url)
            desc_html = j.get("description", "")
            description_text = BeautifulSoup(desc_html, "html.parser").get_text(" ", strip=True) if desc_html else ""
            emails = extract_emails(description_text)

            jobs.append({
                "source": "RemoteOK",
                "title": title,
                "company": j.get("company", ""),
                "location": "Remote",
                "date_posted": (j.get("date") or "")[:10],
                "url": job_url,
                "description_preview": description_text[:500],
                "emails": ", ".join(emails),
                "recruiter_name": "",
                "recruiter_title": "",
            })

        time.sleep(2)

    print(f"    → {len(jobs)} total RemoteOK jobs")
    return jobs


# ---------------------------------------------------------------------------
# ATS career pages via Firecrawl search (Lever, Greenhouse, Ashby)
# ---------------------------------------------------------------------------

ATS_SEARCH_QUERIES = [
    "paid media specialist remote jobs lever.co",
    "paid social media manager remote jobs lever.co",
    "performance marketing manager remote lever.co",
    "paid media specialist remote boards.greenhouse.io",
    "paid social media manager remote greenhouse.io jobs",
    "performance marketing remote boards.greenhouse.io",
    "paid media remote jobs.ashbyhq.com",
    "paid social performance marketing ashbyhq.com",
]


def _extract_company_from_ats_url(url):
    m = re.search(r"jobs\.lever\.co/([^/?#]+)", url)
    if m:
        return m.group(1).replace("-", " ").title()
    m = re.search(r"boards\.greenhouse\.io/([^/?#]+)", url)
    if m:
        return m.group(1).replace("-", " ").title()
    m = re.search(r"jobs\.ashbyhq\.com/([^/?#]+)", url)
    if m:
        return m.group(1).replace("-", " ").title()
    return ""


def _firecrawl_search(query, limit=5):
    if not FIRECRAWL_API_KEY:
        return []
    try:
        r = requests.post(
            "https://api.firecrawl.dev/v1/search",
            json={"query": query, "limit": limit},
            headers={"Authorization": f"Bearer {FIRECRAWL_API_KEY}", "Content-Type": "application/json"},
            timeout=25,
        )
        if r.status_code == 200:
            return r.json().get("data", [])
    except requests.RequestException:
        pass
    return []


def scrape_ats_firecrawl():
    if not FIRECRAWL_API_KEY:
        print("  [ATS] No FIRECRAWL_API_KEY — skipping")
        return []

    ATS_DOMAINS = ["jobs.lever.co", "boards.greenhouse.io", "jobs.ashbyhq.com"]
    jobs = []
    seen = set()

    for query in ATS_SEARCH_QUERIES:
        ats_label = "Lever" if "lever" in query else "Greenhouse" if "greenhouse" in query else "Ashby"
        print(f"  [ATS/{ats_label}] '{query[:55]}'")

        hits = _firecrawl_search(query, limit=5)
        new = 0
        for hit in hits:
            url = hit.get("url", "")
            if not url or url in seen:
                continue
            if not any(d in url for d in ATS_DOMAINS):
                continue

            title = hit.get("title", "").strip()
            desc = hit.get("description", "").strip()
            combined = (title + " " + desc).lower()
            if not any(kw in combined for kw in PAID_MEDIA_TITLE_KEYWORDS):
                continue

            seen.add(url)
            company = _extract_company_from_ats_url(url)
            emails = extract_emails(desc)
            source = "Lever" if "lever.co" in url else "Greenhouse" if "greenhouse.io" in url else "Ashby"

            jobs.append({
                "source": source,
                "title": title,
                "company": company,
                "location": "Remote",
                "date_posted": "",
                "url": url,
                "description_preview": desc[:500],
                "emails": ", ".join(emails),
                "recruiter_name": "",
                "recruiter_title": "",
            })
            new += 1

        print(f"    → {new} new")
        time.sleep(1.5)

    print(f"  [ATS] Total: {len(jobs)} jobs")
    return jobs


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

def run(pages=3, sources=None):
    os.makedirs(TMP_DIR, exist_ok=True)

    if sources is None:
        sources = ["linkedin", "indeed", "wwr", "remotive", "jobicy", "remoteok", "ats"]

    # Load existing jobs to deduplicate
    existing_urls = set()
    if os.path.exists(OUTPUT_JSON):
        with open(OUTPUT_JSON) as f:
            existing_jobs = json.load(f)
        existing_urls = {j.get("url", "") for j in existing_jobs}
        print(f"Loaded {len(existing_jobs)} existing leads (will skip duplicates)")
    else:
        existing_jobs = []

    all_jobs = list(existing_jobs)
    new_jobs = []

    if "linkedin" in sources:
        print("\n=== LinkedIn ===")
        linkedin_jobs = scrape_linkedin(pages=pages)
        fresh = [j for j in linkedin_jobs if j["url"] not in existing_urls]
        print(f"\nFetching LinkedIn job descriptions ({len(fresh)} new jobs)...")
        for i, job in enumerate(fresh, 1):
            print(f"  [{i}/{len(fresh)}] {job['company']} — {job['title']}")
            fetch_linkedin_detail(job)
            time.sleep(1.5)
        new_jobs.extend(fresh)
        existing_urls.update(j["url"] for j in fresh)

    if "indeed" in sources:
        print("\n=== Indeed ===")
        indeed_jobs = scrape_indeed(pages=pages)
        fresh = [j for j in indeed_jobs if j["url"] not in existing_urls]
        print(f"\nFetching Indeed job descriptions ({len(fresh)} new jobs)...")
        for i, job in enumerate(fresh, 1):
            print(f"  [{i}/{len(fresh)}] {job['url']}")
            fetch_indeed_detail(job)
            time.sleep(2)
            if job["title"]:
                print(f"    → {job['title']} @ {job['company']}")
        new_jobs.extend(fresh)
        existing_urls.update(j["url"] for j in fresh)

    if "wwr" in sources:
        print("\n=== We Work Remotely ===")
        wwr_jobs = scrape_wwr()
        fresh = [j for j in wwr_jobs if j["url"] not in existing_urls]
        print(f"  {len(fresh)} new (skipped {len(wwr_jobs) - len(fresh)} dupes)")
        new_jobs.extend(fresh)
        existing_urls.update(j["url"] for j in fresh)

    if "remotive" in sources:
        print("\n=== Remotive ===")
        remotive_jobs = scrape_remotive()
        fresh = [j for j in remotive_jobs if j["url"] not in existing_urls]
        print(f"  {len(fresh)} new (skipped {len(remotive_jobs) - len(fresh)} dupes)")
        new_jobs.extend(fresh)
        existing_urls.update(j["url"] for j in fresh)

    if "jobicy" in sources:
        print("\n=== Jobicy ===")
        jobicy_jobs = scrape_jobicy()
        fresh = [j for j in jobicy_jobs if j["url"] not in existing_urls]
        print(f"  {len(fresh)} new (skipped {len(jobicy_jobs) - len(fresh)} dupes)")
        new_jobs.extend(fresh)
        existing_urls.update(j["url"] for j in fresh)

    if "remoteok" in sources:
        print("\n=== RemoteOK ===")
        remoteok_jobs = scrape_remoteok()
        fresh = [j for j in remoteok_jobs if j["url"] not in existing_urls]
        print(f"  {len(fresh)} new (skipped {len(remoteok_jobs) - len(fresh)} dupes)")
        new_jobs.extend(fresh)
        existing_urls.update(j["url"] for j in fresh)

    if "ats" in sources:
        print("\n=== ATS Career Pages (Firecrawl) ===")
        ats_jobs = scrape_ats_firecrawl()
        fresh = [j for j in ats_jobs if j["url"] not in existing_urls]
        print(f"  {len(fresh)} new (skipped {len(ats_jobs) - len(fresh)} dupes)")
        new_jobs.extend(fresh)
        existing_urls.update(j["url"] for j in fresh)

    all_jobs = existing_jobs + new_jobs

    with_emails = [j for j in all_jobs if j.get("emails")]
    without_emails = [j for j in all_jobs if not j.get("emails")]
    with_recruiter = [j for j in all_jobs if j.get("recruiter_name")]

    print(f"\n{'='*70}")
    print(f"RESULTS")
    print(f"{'='*70}")
    print(f"Total jobs scraped:      {len(all_jobs)}")
    print(f"Jobs with emails:        {len(with_emails)}")
    print(f"Jobs with recruiter:     {len(with_recruiter)}")

    # Save (jobs with emails/recruiter first)
    sorted_jobs = with_emails + [j for j in without_emails if j not in with_emails]

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(sorted_jobs, f, ensure_ascii=False, indent=2)

    fields = [
        "source", "title", "company", "location", "date_posted",
        "emails", "recruiter_name", "recruiter_title", "url", "description_preview",
    ]
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(sorted_jobs)

    print(f"\nSaved:")
    print(f"  CSV: {OUTPUT_CSV}")
    print(f"  JSON: {OUTPUT_JSON}")

    if with_emails:
        print(f"\n{'='*70}")
        print(f"JOBS WITH CONTACT EMAILS ({len(with_emails)})")
        print(f"{'='*70}")
        for j in with_emails:
            print(f"\n  [{j['source']}] {j['title']} @ {j['company']}")
            print(f"  Email(s): {j['emails']}")
            print(f"  {j['url']}")

    if with_recruiter:
        print(f"\n{'='*70}")
        print(f"JOBS SHOWING RECRUITER ({len(with_recruiter)})")
        print(f"{'='*70}")
        for j in with_recruiter:
            print(f"  {j['recruiter_name']} ({j['recruiter_title']}) @ {j['company']} — {j['title']}")

    if not with_emails and not with_recruiter:
        print("\nNo direct emails found in job descriptions (typical for LinkedIn).")
        print("Next step: use the CSV with company names in Hunter.io to find recruiter emails.")

    return sorted_jobs


if __name__ == "__main__":
    pages = 3
    sources = None

    if "--pages" in sys.argv:
        idx = sys.argv.index("--pages")
        pages = int(sys.argv[idx + 1])

    if "--source" in sys.argv:
        idx = sys.argv.index("--source")
        sources = [sys.argv[idx + 1].lower()]

    if "--sources" in sys.argv:
        idx = sys.argv.index("--sources")
        sources = [s.strip().lower() for s in sys.argv[idx + 1].split(",")]

    run(pages=pages, sources=sources)
