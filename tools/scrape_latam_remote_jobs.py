"""
Scrapes LATAM-friendly remote job boards for marketing / paid media roles.
Uses only public APIs and RSS feeds — no ToS violations.

Sources:
  - RemoteOK       https://remoteok.com/api  (public JSON API)
  - Jobicy         https://jobicy.com/api/v2/remote-jobs  (public JSON API)
  - Working Nomads https://www.workingnomads.com/api/exposed_jobs/  (public JSON API)
  - We Work Remotely  RSS feed (public)

Outputs:
  .tmp/latam_remote_jobs.json   full dataset
  .tmp/latam_remote_jobs.csv    spreadsheet
  .tmp/recruiter_leads.json     merged with existing, ready for find_recruiter_emails.py

Usage:
  python3 tools/scrape_latam_remote_jobs.py
  python3 tools/scrape_latam_remote_jobs.py --all      # skip relevance filter
"""

import csv
import datetime
import json
import os
import re
import sys
import time

import requests
from bs4 import BeautifulSoup

TMP_DIR = os.path.join(os.path.dirname(__file__), "..", ".tmp")
OUTPUT_JSON = os.path.join(TMP_DIR, "latam_remote_jobs.json")
OUTPUT_CSV = os.path.join(TMP_DIR, "latam_remote_jobs.csv")
LEADS_JSON = os.path.join(TMP_DIR, "recruiter_leads.json")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; job-research-bot/1.0)",
    "Accept": "application/json, text/html, */*",
}

RELEVANCE_KEYWORDS = [
    "paid media", "meta ads", "facebook ads", "instagram ads",
    "paid social", "performance marketing", "google ads", "ppc", "sem",
    "digital marketing", "media buyer", "ads manager", "growth marketing",
    "programmatic", "biddable media",
]

# Phrases that indicate the job is open to LATAM / non-US workers
LATAM_OPEN = [
    "latam", "latin america", "latin american", "americas", "worldwide",
    "anywhere", "global", "south america", "all locations",
    "no location restriction", "open to all", "work from anywhere",
]

# European regions — secondary tier (included as "europe" status)
EUROPE_REGIONS = [
    "uk", "united kingdom", "great britain", "england", "scotland", "wales",
    "europe", "european union", "eu only", "emea", "eea",
    "germany", "france", "spain", "italy", "netherlands", "belgium",
    "sweden", "norway", "denmark", "finland", "poland", "austria",
    "switzerland", "portugal", "ireland", "czech republic", "romania",
    "hungary", "slovakia", "bulgaria", "croatia", "serbia", "ukraine",
    "russia", "turkey",
]

# Regions fully outside Americas + Europe — excluded
NON_LATAM_REGIONS = [
    # Asia-Pacific
    "apac", "asia", "asia pacific", "southeast asia",
    "india", "philippines", "indonesia", "vietnam", "thailand", "malaysia",
    "singapore", "taiwan", "south korea", "japan", "china", "hong kong",
    "australia", "new zealand",
    # Middle East / Africa
    "middle east", "africa", "mena", "israel", "uae", "dubai",
    "south africa", "nigeria", "kenya",
]

# Phrases that suggest US-only (flag but don't hard-exclude)
US_ONLY_SIGNALS = [
    "us only", "united states only", "must be located in the us",
    "authorized to work in the us", "us-based only", "us based only",
    "must reside in the us", "us residents only",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def is_relevant(title, description=""):
    text = (title + " " + description).lower()
    return any(kw in text for kw in RELEVANCE_KEYWORDS)


def latam_status(location, description=""):
    loc = location.lower()
    text = (location + " " + description).lower()
    if any(s in text for s in US_ONLY_SIGNALS):
        return "us_only"
    # Explicit LATAM-open signal — but don't let it override a clearly non-LATAM location
    if any(s in text for s in LATAM_OPEN):
        if any(r in loc for r in NON_LATAM_REGIONS):
            return "non_latam"
        return "open"
    # APAC / Middle East / Africa — hard exclude
    if any(r in loc for r in NON_LATAM_REGIONS):
        return "non_latam"
    # Europe-only — secondary tier, keep but flag
    if any(r in loc for r in EUROPE_REGIONS):
        return "europe"
    # If location is specifically US, treat as unknown (not excluded, not confirmed open)
    if any(r in loc for r in ["usa", "united states", "us remote", "usa remote"]):
        return "unknown"
    return "unknown"  # remote but no explicit LATAM signal


def strip_html(html_text):
    return BeautifulSoup(html_text or "", "html.parser").get_text(separator=" ", strip=True)


# ---------------------------------------------------------------------------
# Source 1: RemoteOK (public JSON API)
# ---------------------------------------------------------------------------

def scrape_remoteok():
    """
    Docs: https://remoteok.com/api
    First array item is a legal/credit notice — skip it.
    Rate limit: be polite, 1 request per tag.
    """
    tags = ["marketing", "social-media", "growth"]
    jobs = []
    seen = set()

    for tag in tags:
        url = f"https://remoteok.com/api?tag={tag}"
        print(f"  [RemoteOK] tag={tag}")
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

        data = r.json()
        # First item is the legal notice object
        for item in data[1:]:
            if not isinstance(item, dict):
                continue
            job_id = str(item.get("id", ""))
            if job_id in seen:
                continue
            seen.add(job_id)

            title = item.get("position", "")
            company = item.get("company", "")
            location = item.get("location", "Worldwide")
            desc_raw = item.get("description", "")
            desc = strip_html(desc_raw)[:400]
            job_url = item.get("url", f"https://remoteok.com/l/{job_id}")
            date_posted = item.get("date", "")[:10] if item.get("date") else ""

            jobs.append({
                "source": "RemoteOK",
                "title": title,
                "company": company,
                "location": location if location else "Worldwide",
                "date_posted": date_posted,
                "url": job_url,
                "snippet": desc,
                "latam_status": latam_status(location, desc),
                "relevant": is_relevant(title, desc),
                "emails": "",
            })

        print(f"    → {len(jobs)} total so far")
        time.sleep(3)  # RemoteOK asks for polite delays

    return jobs


# ---------------------------------------------------------------------------
# Source 2: Jobicy (public JSON API)
# ---------------------------------------------------------------------------

def scrape_jobicy():
    """
    API docs: https://jobicy.com/jobs-rss-feed
    Endpoint: https://jobicy.com/api/v2/remote-jobs
    """
    industries = ["marketing", "design"]  # marketing covers paid media roles
    jobs = []
    seen = set()

    for industry in industries:
        url = f"https://jobicy.com/api/v2/remote-jobs?industry={industry}&count=50"
        print(f"  [Jobicy] industry={industry}")
        try:
            r = requests.get(url, headers=HEADERS, timeout=20)
        except requests.RequestException as e:
            print(f"    Error: {e}")
            continue

        if r.status_code != 200:
            print(f"    HTTP {r.status_code}")
            continue

        data = r.json()
        raw_jobs = data.get("jobs", [])

        for item in raw_jobs:
            job_url = item.get("url", "")
            if not job_url or job_url in seen:
                continue
            seen.add(job_url)

            title = item.get("jobTitle", "")
            company = item.get("companyName", "")
            location = item.get("jobGeo", "Worldwide")
            desc = strip_html(item.get("jobDescription", ""))[:400]
            date_posted = (item.get("pubDate", "") or "")[:10]

            jobs.append({
                "source": "Jobicy",
                "title": title,
                "company": company,
                "location": location if location else "Worldwide",
                "date_posted": date_posted,
                "url": job_url,
                "snippet": desc,
                "latam_status": latam_status(location, desc),
                "relevant": is_relevant(title, desc),
                "emails": "",
            })

        print(f"    → {len(jobs)} total so far")
        time.sleep(2)

    return jobs


# ---------------------------------------------------------------------------
# Source 3: Working Nomads (public JSON API)
# ---------------------------------------------------------------------------

def scrape_working_nomads():
    """
    Public API: https://www.workingnomads.com/api/exposed_jobs/
    Categories: marketing, business-dev, sales
    """
    categories = ["marketing", "business-dev"]
    jobs = []
    seen = set()

    for cat in categories:
        url = f"https://www.workingnomads.com/api/exposed_jobs/?category={cat}"
        print(f"  [Working Nomads] category={cat}")
        try:
            r = requests.get(url, headers=HEADERS, timeout=20)
        except requests.RequestException as e:
            print(f"    Error: {e}")
            continue

        if r.status_code != 200:
            print(f"    HTTP {r.status_code}")
            continue

        raw_jobs = r.json()
        if not isinstance(raw_jobs, list):
            raw_jobs = raw_jobs.get("jobs", [])

        for item in raw_jobs:
            job_url = item.get("url", "")
            if not job_url or job_url in seen:
                continue
            seen.add(job_url)

            title = item.get("title", "")
            company = item.get("company", "")
            location = item.get("region", "Worldwide")
            desc = strip_html(item.get("description", ""))[:400]
            date_posted = (item.get("pub_date", "") or "")[:10]

            jobs.append({
                "source": "Working Nomads",
                "title": title,
                "company": company,
                "location": location if location else "Worldwide",
                "date_posted": date_posted,
                "url": job_url,
                "snippet": desc,
                "latam_status": latam_status(location, desc),
                "relevant": is_relevant(title, desc),
                "emails": "",
            })

        print(f"    → {len(jobs)} total so far")
        time.sleep(2)

    return jobs


# ---------------------------------------------------------------------------
# Source 4: Himalayas (public JSON API)
# ---------------------------------------------------------------------------

HIMALAYAS_CATEGORIES = ["Marketing", "Growth"]

HIMALAYAS_LATAM_OK = {
    "", "worldwide", "anywhere", "global", "americas", "latin america",
    "south america", "latam",
}

HIMALAYAS_LATAM_BLOCKED = {
    "united states", "us", "usa", "canada", "united kingdom", "uk",
    "europe", "eu", "emea", "apac", "australia", "india", "philippines",
}

HIMALAYAS_EUROPE_ONLY = {
    "united kingdom", "uk", "europe", "eu", "emea", "eea",
    "germany", "france", "spain", "italy", "netherlands", "sweden",
    "norway", "denmark", "finland", "poland", "ireland", "switzerland",
}


def himalayas_latam_status(restrictions):
    """
    restrictions: list of strings from the API's locationRestrictions field.
    Empty list = worldwide = open.
    """
    if not restrictions:
        return "open"
    normalized = {r.lower().strip() for r in restrictions}
    if normalized & HIMALAYAS_LATAM_OK:
        return "open"
    if normalized <= HIMALAYAS_LATAM_BLOCKED:
        if normalized <= {"united states", "us", "usa", "canada"}:
            return "us_only"
        if normalized <= HIMALAYAS_EUROPE_ONLY:
            return "europe"
        return "non_latam"
    return "unknown"


def scrape_himalayas():
    """
    Public API: https://himalayas.app/jobs/api
    locationRestrictions field is authoritative for where candidates can be.
    """
    jobs = []
    seen = set()

    for category in HIMALAYAS_CATEGORIES:
        url = f"https://himalayas.app/jobs/api?categories={category}&remote=true"
        print(f"  [Himalayas] category={category}")
        try:
            r = requests.get(url, headers=HEADERS, timeout=20)
        except requests.RequestException as e:
            print(f"    Error: {e}")
            continue

        if r.status_code != 200:
            print(f"    HTTP {r.status_code}")
            continue

        data = r.json()
        raw_jobs = data.get("jobs", [])

        for item in raw_jobs:
            job_url = item.get("applicationLink", item.get("guid", ""))
            if not job_url or job_url in seen:
                continue
            seen.add(job_url)

            title = item.get("title", "")
            company = item.get("companyName", "")
            restrictions = item.get("locationRestrictions", [])
            location = ", ".join(restrictions) if restrictions else "Worldwide"
            desc = strip_html(item.get("description", ""))[:400]
            pub_ts = item.get("pubDate", 0)
            date_posted = datetime.datetime.fromtimestamp(pub_ts).strftime("%Y-%m-%d") if pub_ts else ""

            status = himalayas_latam_status(restrictions)

            jobs.append({
                "source": "Himalayas",
                "title": title,
                "company": company,
                "location": location,
                "date_posted": date_posted,
                "url": job_url,
                "snippet": desc,
                "latam_status": status,
                "relevant": is_relevant(title, desc),
                "emails": "",
            })

        print(f"    → {len(jobs)} total so far")
        time.sleep(2)

    return jobs


# ---------------------------------------------------------------------------
# Source 5: Remotive (public JSON API)
# ---------------------------------------------------------------------------

def scrape_remotive():
    """
    Public API: https://remotive.com/api/remote-jobs
    Searches marketing category for paid media / performance terms.
    """
    searches = ["paid media", "performance marketing", "facebook ads", "meta ads", "paid social"]
    jobs = []
    seen = set()

    for q in searches:
        url = f"https://remotive.com/api/remote-jobs?category=marketing&search={q.replace(' ', '+')}"
        print(f"  [Remotive] search={q}")
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

        raw_jobs = r.json().get("jobs", [])

        for item in raw_jobs:
            job_url = item.get("url", "")
            if not job_url or job_url in seen:
                continue
            seen.add(job_url)

            title = item.get("title", "")
            company = item.get("company_name", "")
            location = item.get("candidate_required_location", "Worldwide") or "Worldwide"
            desc = strip_html(item.get("description", ""))[:400]
            date_posted = (item.get("publication_date", "") or "")[:10]

            jobs.append({
                "source": "Remotive",
                "title": title,
                "company": company,
                "location": location,
                "date_posted": date_posted,
                "url": job_url,
                "snippet": desc,
                "latam_status": latam_status(location, desc),
                "relevant": is_relevant(title, desc),
                "emails": "",
            })

        print(f"    → {len(jobs)} total so far")
        time.sleep(2)

    return jobs


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run(show_all=False):
    os.makedirs(TMP_DIR, exist_ok=True)

    print("=== RemoteOK ===")
    jobs_rok = scrape_remoteok()

    print("\n=== Jobicy ===")
    jobs_jcy = scrape_jobicy()

    print("\n=== Working Nomads ===")
    jobs_wn = scrape_working_nomads()

    print("\n=== Himalayas ===")
    jobs_him = scrape_himalayas()

    print("\n=== Remotive ===")
    jobs_rem = scrape_remotive()

    # Merge and deduplicate by URL
    all_jobs = {}
    for job in jobs_rok + jobs_jcy + jobs_wn + jobs_him + jobs_rem:
        url = job.get("url", "")
        if url and url not in all_jobs:
            all_jobs[url] = job

    all_list = list(all_jobs.values())

    # Split into tiers
    relevant_open = [j for j in all_list if j["relevant"] and j["latam_status"] == "open"]
    relevant_unknown = [j for j in all_list if j["relevant"] and j["latam_status"] == "unknown"]
    relevant_us_only = [j for j in all_list if j["relevant"] and j["latam_status"] == "us_only"]
    relevant_europe = [j for j in all_list if j["relevant"] and j["latam_status"] == "europe"]
    other = [j for j in all_list if not j["relevant"] or j["latam_status"] == "non_latam"]

    for group in (relevant_open, relevant_unknown, relevant_us_only, relevant_europe, other):
        group.sort(key=lambda j: j.get("date_posted", ""), reverse=True)

    final = relevant_open + relevant_unknown + relevant_us_only + relevant_europe + other

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(final, f, ensure_ascii=False, indent=2)

    csv_rows = final if show_all else (relevant_open + relevant_unknown + relevant_us_only + relevant_europe)
    fields = ["source", "title", "company", "location", "date_posted", "latam_status", "url", "snippet"]
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(csv_rows)

    # Merge into recruiter_leads.json for find_recruiter_emails.py
    existing_leads = []
    if os.path.exists(LEADS_JSON):
        with open(LEADS_JSON) as f:
            try:
                existing_leads = json.load(f)
            except json.JSONDecodeError:
                pass

    existing_urls = {j.get("url", "") for j in existing_leads}
    new_leads = []
    for j in relevant_open + relevant_unknown + relevant_us_only + relevant_europe:
        if j["url"] not in existing_urls:
            new_leads.append({
                "source": j["source"],
                "title": j["title"],
                "company": j["company"],
                "location": j["location"],
                "date_posted": j["date_posted"],
                "latam_status": j["latam_status"],
                "url": j["url"],
                "emails": j.get("emails", ""),
                "description_preview": j.get("snippet", ""),
            })

    merged = existing_leads + new_leads
    with open(LEADS_JSON, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)

    # Summary
    print(f"\n{'='*70}")
    print(f"RESULTS")
    print(f"{'='*70}")
    non_latam_count = len([j for j in all_list if j["relevant"] and j["latam_status"] == "non_latam"])
    print(f"Total scraped:                  {len(all_list)}")
    print(f"Relevant + LATAM/Worldwide:     {len(relevant_open)}  ← best leads")
    print(f"Relevant + location unclear:    {len(relevant_unknown)}  ← worth contacting")
    print(f"Relevant but US-only:           {len(relevant_us_only)}  ← flagged")
    print(f"Relevant + Europe-only:         {len(relevant_europe)}  ← secondary option")
    print(f"Relevant but APAC/MENA:         {non_latam_count}  ← excluded")
    print(f"Not relevant:                   {len([j for j in all_list if not j['relevant']])}")
    print(f"\nNew leads added to recruiter_leads.json: {len(new_leads)}")
    print(f"\nFiles:")
    print(f"  Full data:    {OUTPUT_JSON}")
    print(f"  Spreadsheet:  {OUTPUT_CSV}")
    print(f"  Leads merged: {LEADS_JSON}")

    for tier_label, tier_jobs in [
        (f"LATAM / WORLDWIDE CONFIRMED ({len(relevant_open)})", relevant_open),
        (f"LOCATION UNCLEAR — remote, no restriction listed ({len(relevant_unknown)})", relevant_unknown),
        (f"EUROPE-ONLY — secondary option ({len(relevant_europe)})", relevant_europe),
    ]:
        if tier_jobs:
            print(f"\n{'='*70}")
            print(tier_label)
            print(f"{'='*70}")
            for i, j in enumerate(tier_jobs[:20], 1):
                print(f"\n{i:2}. {j['title']}")
                print(f"    {j['company']} — {j['location']} ({j['source']})")
                print(f"    {j['url']}")

    return final


if __name__ == "__main__":
    show_all = "--all" in sys.argv
    run(show_all=show_all)
