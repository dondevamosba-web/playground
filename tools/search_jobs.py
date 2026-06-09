"""
Searches LinkedIn (public guest API) and Remotive for Paid Media / Meta Ads
Specialist jobs in the US and Canada.

Saves results to .tmp/jobs.json and .tmp/jobs_summary.csv.

Usage:
  python3 tools/search_jobs.py                     # run all searches
  python3 tools/search_jobs.py --country us        # US only
  python3 tools/search_jobs.py --country ca        # Canada only
  python3 tools/search_jobs.py --pages 3           # pages per LinkedIn query (default 2)
"""

import csv
import json
import os
import sys
import time

import requests
from bs4 import BeautifulSoup

TMP_DIR = os.path.join(os.path.dirname(__file__), "..", ".tmp")
OUTPUT_JSON = os.path.join(TMP_DIR, "jobs.json")
OUTPUT_CSV = os.path.join(TMP_DIR, "jobs_summary.csv")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

RELEVANCE_KEYWORDS = ["meta", "facebook", "instagram", "fb ads", "lead generation", "leads", "paid social", "paid media", "media buyer", "paid analyst"]

LINKEDIN_SEARCHES = [
    {"q": "paid media specialist meta", "location": "United States", "country": "US"},
    {"q": "meta ads specialist", "location": "United States", "country": "US"},
    {"q": "facebook ads specialist", "location": "United States", "country": "US"},
    {"q": "paid social media specialist", "location": "United States", "country": "US"},
    {"q": "performance marketing specialist meta", "location": "United States", "country": "US"},
    {"q": "paid media analyst remote", "location": "United States", "country": "US"},
    {"q": "media buyer facebook ads remote", "location": "United States", "country": "US"},
    {"q": "paid media specialist meta", "location": "Canada", "country": "CA"},
    {"q": "meta ads specialist", "location": "Canada", "country": "CA"},
    {"q": "facebook ads specialist", "location": "Canada", "country": "CA"},
    {"q": "media buyer meta ads", "location": "Canada", "country": "CA"},
]

REMOTIVE_SEARCHES = [
    {"q": "paid media meta", "label": "Remotive — paid media meta"},
    {"q": "facebook ads specialist", "label": "Remotive — facebook ads"},
    {"q": "meta ads", "label": "Remotive — meta ads"},
]

WWR_CATEGORIES = [
    "https://weworkremotely.com/categories/remote-marketing-jobs",
]

JOBICY_URL = "https://jobicy.com/api/v2/remote-jobs?count=50&industry=marketing"


# ---------------------------------------------------------------------------
# LinkedIn
# ---------------------------------------------------------------------------

def linkedin_url(q, location, start):
    q_enc = q.replace(" ", "+")
    loc_enc = location.replace(" ", "+")
    return (
        "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
        f"?keywords={q_enc}&location={loc_enc}&start={start}"
    )


def scrape_linkedin_query(search, pages=2):
    jobs = []
    seen_urls = set()
    label = f"LinkedIn {search['country']} — {search['q']}"

    for page_num in range(pages):
        start = page_num * 10
        url = linkedin_url(search["q"], search["location"], start)
        print(f"  [{label}] page {page_num + 1}: start={start}")

        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
        except requests.RequestException as e:
            print(f"    Request error: {e}")
            break

        if r.status_code != 200:
            print(f"    HTTP {r.status_code} — stopping this query")
            break

        soup = BeautifulSoup(r.text, "html.parser")
        cards = soup.select("li")

        if not cards:
            print(f"    No cards on page {page_num + 1} — stopping")
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

            company = company_el.get_text(strip=True) if company_el else ""
            location = location_el.get_text(strip=True) if location_el else ""
            date_posted = date_el.get("datetime", "") if date_el else ""
            raw_url = link_el.get("href", "") if link_el else ""
            # Strip tracking params — keep only the /jobs/view/... path
            job_url = raw_url.split("?")[0] if raw_url else ""

            if not job_url or job_url in seen_urls:
                continue
            seen_urls.add(job_url)

            jobs.append({
                "title": title,
                "company": company,
                "location": location,
                "country": search["country"],
                "salary": "",
                "date_posted": date_posted,
                "url": job_url,
                "source": "LinkedIn",
                "query_source": label,
                "snippet": "",
            })
            new += 1

        print(f"    → {new} new jobs (running total: {len(jobs)})")
        time.sleep(2)  # polite delay between pages

    return jobs


# ---------------------------------------------------------------------------
# Remotive
# ---------------------------------------------------------------------------

def scrape_remotive(search):
    label = search["label"]
    q_enc = search["q"].replace(" ", "+")
    url = f"https://remotive.com/api/remote-jobs?category=marketing&search={q_enc}"

    print(f"  [{label}]")
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
    except requests.RequestException as e:
        print(f"    Request error: {e}")
        return []

    if r.status_code != 200:
        print(f"    HTTP {r.status_code}")
        return []

    data = r.json()
    raw_jobs = data.get("jobs", [])
    jobs = []

    for j in raw_jobs:
        req_location = j.get("candidate_required_location", "Worldwide")
        # Keep only jobs that explicitly accept US, Canada, Americas, or Worldwide
        loc_lower = req_location.lower()
        if not any(k in loc_lower for k in ["usa", "us", "canada", "ca", "americas", "north america", "worldwide", "anywhere"]):
            continue

        jobs.append({
            "title": j.get("title", ""),
            "company": j.get("company_name", ""),
            "location": req_location,
            "country": "US/CA",
            "salary": j.get("salary", ""),
            "date_posted": j.get("publication_date", "")[:10],
            "url": j.get("url", ""),
            "source": "Remotive",
            "query_source": label,
            "snippet": BeautifulSoup(j.get("description", ""), "html.parser").get_text(separator=" ", strip=True)[:200],
        })

    print(f"    → {len(jobs)} jobs (US/CA/Americas/Worldwide)")
    time.sleep(1)
    return jobs


# ---------------------------------------------------------------------------
# We Work Remotely
# ---------------------------------------------------------------------------

def scrape_wwr(url: str) -> list:
    label = "WeWorkRemotely — marketing"
    print(f"  [{label}]")
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
    except requests.RequestException as e:
        print(f"    Request error: {e}")
        return []

    if r.status_code != 200:
        print(f"    HTTP {r.status_code}")
        return []

    soup = BeautifulSoup(r.text, "html.parser")
    listings = soup.select("section.jobs li:not(.feature--ad)")
    jobs = []

    for item in listings:
        title_el = item.select_one(".new-listing__header__title__text")
        company_el = item.select_one(".new-listing__company-name")
        location_el = item.select_one(".new-listing__company-headquarters")
        date_el = item.select_one(".new-listing__header__icons__date")
        link_el = item.select_one("a.listing-link--unlocked")

        title = title_el.get_text(strip=True) if title_el else ""
        if not title:
            continue

        # company_el may contain a nested icon img; get text only
        company = company_el.get_text(strip=True) if company_el else ""
        location = location_el.get_text(strip=True) if location_el else "Remote"
        date_text = date_el.get_text(strip=True) if date_el else ""
        href = link_el.get("href", "") if link_el else ""
        job_url = f"https://weworkremotely.com{href}" if href else ""

        if not job_url:
            continue

        jobs.append({
            "title": title,
            "company": company,
            "location": location,
            "country": "US/CA",
            "salary": "",
            "date_posted": date_text,
            "url": job_url,
            "source": "WeWorkRemotely",
            "query_source": label,
            "snippet": "",
        })

    print(f"    → {len(jobs)} jobs")
    time.sleep(1)
    return jobs


# ---------------------------------------------------------------------------
# Jobicy
# ---------------------------------------------------------------------------

def scrape_jobicy() -> list:
    label = "Jobicy — marketing"
    print(f"  [{label}]")
    try:
        r = requests.get(JOBICY_URL, headers=HEADERS, timeout=15)
    except requests.RequestException as e:
        print(f"    Request error: {e}")
        return []

    if r.status_code != 200:
        print(f"    HTTP {r.status_code}")
        return []

    raw_jobs = r.json().get("jobs", [])
    jobs = []
    for j in raw_jobs:
        geo = j.get("jobGeo", "Worldwide")
        geo_lower = geo.lower()
        if not any(k in geo_lower for k in ["usa", "us", "canada", "americas", "north america", "worldwide", "anywhere", "remote"]):
            continue

        jobs.append({
            "title": j.get("jobTitle", ""),
            "company": j.get("companyName", ""),
            "location": geo,
            "country": "US/CA",
            "salary": "",
            "date_posted": j.get("pubDate", "")[:10],
            "url": j.get("url", ""),
            "source": "Jobicy",
            "query_source": label,
            "snippet": BeautifulSoup(j.get("jobDescription", ""), "html.parser").get_text(separator=" ", strip=True)[:200],
        })

    print(f"    → {len(jobs)} jobs (US/CA/Americas/Worldwide)")
    time.sleep(1)
    return jobs


# ---------------------------------------------------------------------------
# Relevance filter & main runner
# ---------------------------------------------------------------------------

def is_relevant(job):
    text = (job.get("title", "") + " " + job.get("snippet", "")).lower()
    return any(kw in text for kw in RELEVANCE_KEYWORDS)


def run(pages=2, countries=None):
    os.makedirs(TMP_DIR, exist_ok=True)

    all_jobs = {}  # job_url → job dict

    # LinkedIn
    linkedin_searches = LINKEDIN_SEARCHES
    if countries:
        linkedin_searches = [s for s in LINKEDIN_SEARCHES if s["country"].lower() in countries]

    print("=== LinkedIn ===")
    for search in linkedin_searches:
        jobs = scrape_linkedin_query(search, pages=pages)
        for job in jobs:
            if job["url"] not in all_jobs:
                all_jobs[job["url"]] = job
        time.sleep(3)  # pause between different search queries

    # Remotive (always worldwide; filter by location field)
    print("\n=== Remotive ===")
    for search in REMOTIVE_SEARCHES:
        jobs = scrape_remotive(search)
        for job in jobs:
            if job["url"] not in all_jobs:
                all_jobs[job["url"]] = job

    # We Work Remotely
    print("\n=== We Work Remotely ===")
    for cat_url in WWR_CATEGORIES:
        jobs = scrape_wwr(cat_url)
        for job in jobs:
            if job["url"] not in all_jobs:
                all_jobs[job["url"]] = job

    # Jobicy
    print("\n=== Jobicy ===")
    for job in scrape_jobicy():
        if job["url"] not in all_jobs:
            all_jobs[job["url"]] = job

    # Classify relevance
    all_list = list(all_jobs.values())
    relevant = [j for j in all_list if is_relevant(j)]
    other = [j for j in all_list if not is_relevant(j)]

    for job in relevant:
        job["relevant"] = True
    for job in other:
        job["relevant"] = False

    # Sort relevant: US first, then CA, then others; newest first
    relevant.sort(key=lambda j: (j["country"] not in ("US", "CA"), j.get("date_posted", ""), ), reverse=False)

    final = relevant + other

    # Save JSON
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(final, f, ensure_ascii=False, indent=2)

    # Save CSV — relevant jobs only
    csv_rows = relevant if relevant else final
    csv_fields = ["title", "company", "location", "country", "salary", "date_posted", "url", "source", "query_source", "snippet"]
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=csv_fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(csv_rows)

    # Print summary
    print(f"\n{'='*80}")
    print(f"RESULTS SUMMARY")
    print(f"{'='*80}")
    print(f"Total scraped:  {len(all_list)}")
    print(f"Relevant jobs:  {len(relevant)}  (meta/facebook/instagram/paid social/leads)")
    print(f"Other jobs:     {len(other)}")
    print(f"\nFiles saved:")
    print(f"  JSON (all):      {OUTPUT_JSON}")
    print(f"  CSV (relevant):  {OUTPUT_CSV}")

    print(f"\n{'='*80}")
    print(f"META / PAID SOCIAL JOBS  ({len(relevant)} total)")
    print(f"{'='*80}")
    for i, job in enumerate(relevant, 1):
        sal = f"  [{job['salary']}]" if job.get("salary") else ""
        print(f"\n{i:2}. {job['title']}")
        print(f"    {job['company']} — {job['location']} ({job['country']}){sal}")
        print(f"    Posted: {job.get('date_posted', 'N/A')}  |  {job['source']}")
        print(f"    {job['url']}")

    return final


if __name__ == "__main__":
    pages = 2
    countries = None

    if "--pages" in sys.argv:
        idx = sys.argv.index("--pages")
        pages = int(sys.argv[idx + 1])

    if "--country" in sys.argv:
        idx = sys.argv.index("--country")
        countries = [sys.argv[idx + 1].lower()]

    run(pages=pages, countries=countries)
