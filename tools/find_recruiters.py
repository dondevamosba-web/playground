"""
Finds active recruiters specializing in paid media / performance marketing.

Strategy (free-plan compatible):
  1. Apollo organizations/search → staffing & recruiting firms in digital/marketing
  2. Firecrawl → scrape each firm's team/about page for recruiter names + emails
  3. Hunter.io → fallback email lookup by domain (if HUNTER_API_KEY set)
  4. Claude Haiku → generate personalized "I'm actively looking" cold email per recruiter
  5. Gmail → create one draft per recruiter, ready to review and send

Deduplicates against .tmp/seen_recruiters.json so no one is emailed twice.

Usage:
  python3 tools/find_recruiters.py
  python3 tools/find_recruiters.py --dry-run      # generate emails, skip Gmail
  python3 tools/find_recruiters.py --limit 20     # cap new recruiter emails (default: 15)
"""

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
SEEN_FILE = os.path.join(TMP_DIR, "seen_recruiters.json")
LOG_FILE = os.path.join(TMP_DIR, "recruiter_outreach_log.json")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tools.claude_call import call_claude

APOLLO_API_KEY = os.getenv("APOLLO_API_KEY", "")
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY", "")
HUNTER_API_KEY = os.getenv("HUNTER_API_KEY", "")

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
EMAIL_BLOCKLIST = {"noreply", "no-reply", "donotreply", "privacy", "support", "info",
                   "jobs", "careers", "talent", "hello", "contact", "example", "test",
                   "recruit-us", "recruit-au", "recruit-uk", "recruit-ca", "recruiting",
                   "admin", "hr", "hire", "apply", "team"}

# Large corps to skip — Apollo org search returns these incorrectly
LARGE_CORP_BLOCKLIST = {
    "google", "amazon", "microsoft", "linkedin", "meta", "apple", "accenture",
    "ibm", "salesforce", "oracle", "sap", "adobe", "netflix", "tesla", "uber",
    "airbnb", "spotify", "twitter", "tiktok", "bytedance", "infosys", "wipro",
    "ted conferences", "forbes", "harvard", "the economist", "bbc",
    "business insider", "wall street journal", "wsj", "unilever", "hays",
    "adecco", "robert half", "insight global", "manpower", "randstad",
    "kelly services", "staffmark", "allegis", "aerotek",
    "deloitte", "pwc", "kpmg", "mckinsey", "nike", "vagas",
    "marketing millennials", "traya",
}

# Staffing/recruiting firms that commonly place digital marketing talent
APOLLO_ORG_KEYWORDS = [
    "digital marketing staffing agency",
    "creative staffing agency",
    "marketing recruitment agency",
    "advertising talent staffing",
    "media buying recruiting firm",
    "performance marketing recruiter",
    "paid social media staffing",
    "growth marketing recruiting",
    "ecommerce marketing staffing",
    "digital advertising recruitment",
]

# Known boutique firms to always include (domain → name)
KNOWN_FIRMS = [
    {"name": "Vitamin T", "website": "https://www.vitamint.com"},
    {"name": "Onward Search", "website": "https://www.onwardsearch.com"},
    {"name": "Mondo", "website": "https://www.mondo.com"},
    {"name": "The Creative Group", "website": "https://www.roberthalf.com/us/en/tcg"},
    {"name": "Profiles", "website": "https://www.profilesnyc.com"},
    {"name": "Digital People", "website": "https://www.digitalpeople.com"},
    {"name": "Artisan Talent", "website": "https://www.artisantalent.com"},
    {"name": "Aquent", "website": "https://aquent.com"},
    {"name": "Coda Search Staffing", "website": "https://www.codasearch.com"},
    {"name": "Antenna", "website": "https://www.antennagroup.com"},
    {"name": "Daggerfinn", "website": "https://www.daggerfinn.com"},
    {"name": "Specialist Staffing Group", "website": "https://www.ssg-global.com"},
]

# Title preference order — pick the best match per firm
TITLE_PRIORITY = [
    "recruiter",
    "talent acquisition",
    "sourcer",
    "talent partner",
    "staffing specialist",
    "placement",
    "people partner",
    "hr business partner",
    "hr manager",
    "human resources",
    "director",
    "vp",
    "chief",
]


def best_contact(contacts):
    """From a list of contacts at one firm, return the single best one."""
    if not contacts:
        return None
    if len(contacts) == 1:
        return contacts[0]
    for keyword in TITLE_PRIORITY:
        for c in contacts:
            if keyword in (c.get("title") or "").lower():
                return c
    return contacts[0]  # fallback: first

SYSTEM_PROMPT = """You write short, human cold emails from a job seeker to a recruiter.

Candidate profile:
- Name: Guido Carminatti
- Email: carminattiguido@gmail.com
- LinkedIn: linkedin.com/in/guidocarminatti
- 8+ years scaling Google & Meta (Facebook/Instagram) ad campaigns
- 4.5x average ROAS across 30+ brands, budgets up to $100K/month
- Strong in paid social, lead generation, full-funnel optimization
- Actively seeking a remote paid media / performance marketing role

Rules:
- Tone: direct, warm, zero fluff. No "I hope this finds you well."
- Mention you came across their profile/firm and are actively looking for your next opportunity.
- One sentence on your background with a concrete number.
- Ask if they work with candidates in paid media / performance marketing and if it's worth connecting.
- 4–5 sentences max.
- Return JSON with keys: subject, body
- Sign off: Guido Carminatti | carminattiguido@gmail.com | linkedin.com/in/guidocarminatti
"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

FILE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "svg", "webp", "ico", "pdf", "zip", "mp4", "mov"}


def extract_emails(text):
    found = EMAIL_RE.findall(text)
    return sorted(set(
        e for e in found
        if not any(bad in e.lower() for bad in EMAIL_BLOCKLIST)
        and len(e) < 80
        and e.split(".")[-1].lower() not in FILE_EXTENSIONS
    ))


def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE) as f:
            return set(json.load(f))
    return set()


def save_seen(seen_set):
    os.makedirs(TMP_DIR, exist_ok=True)
    with open(SEEN_FILE, "w") as f:
        json.dump(sorted(seen_set), f, indent=2)


# ---------------------------------------------------------------------------
# Step 1: Apollo — find recruiting firms
# ---------------------------------------------------------------------------

def find_recruiting_firms(limit=20):
    if not APOLLO_API_KEY:
        print("  No APOLLO_API_KEY — skipping Apollo firm search")
        return []

    headers = {"Content-Type": "application/json", "X-Api-Key": APOLLO_API_KEY}
    firms = []
    seen_ids = set()

    for keyword in APOLLO_ORG_KEYWORDS:
        payload = {
            "q_organization_keyword_tags": keyword.split(),
            "per_page": 10,
            "page": 1,
        }
        print(f"  [Apollo] searching firms: '{keyword}'")
        try:
            r = requests.post(
                "https://api.apollo.io/api/v1/organizations/search",
                json=payload, headers=headers, timeout=20
            )
        except requests.RequestException as e:
            print(f"    Error: {e}")
            continue

        if r.status_code != 200:
            print(f"    HTTP {r.status_code}")
            continue

        for org in r.json().get("organizations", []):
            oid = org.get("id", "")
            if oid in seen_ids:
                continue
            seen_ids.add(oid)
            if any(b in org.get("name", "").lower() for b in LARGE_CORP_BLOCKLIST):
                continue
            website = org.get("website_url", "") or ""
            if website and not website.startswith("http"):
                website = "https://" + website
            firms.append({
                "name": org.get("name", ""),
                "website": website,
                "linkedin_url": org.get("linkedin_url", ""),
                "industry": org.get("industry", ""),
                "employee_count": org.get("estimated_num_employees", 0),
            })

        time.sleep(1)
        if len(firms) >= limit:
            break

    print(f"  Found {len(firms)} recruiting firms via Apollo")
    return firms[:limit]


# ---------------------------------------------------------------------------
# Step 2: Firecrawl — find recruiter contacts at each firm
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


RECRUITER_TITLE_KEYWORDS = ["recruit", "talent", "staffing", "hr ", "human resources",
                            "people", "hiring", "sourcer", "headhunt", "placement"]


def hunter_domain_search(domain, limit=10):
    if not HUNTER_API_KEY:
        return []
    try:
        r = requests.get(
            "https://api.hunter.io/v2/domain-search",
            params={"domain": domain, "api_key": HUNTER_API_KEY, "limit": limit, "type": "personal"},
            timeout=15,
        )
        if r.status_code == 200:
            emails = r.json().get("data", {}).get("emails", [])
            results = []
            for e in emails:
                if e.get("confidence", 0) < 50:
                    continue
                title = (e.get("position") or "").lower()
                # Prefer recruiter titles; if no title info, include anyway (small firm)
                if title and not any(kw in title for kw in RECRUITER_TITLE_KEYWORDS):
                    continue
                results.append({
                    "email": e["value"],
                    "first_name": e.get("first_name", ""),
                    "last_name": e.get("last_name", ""),
                    "title": e.get("position", "Recruiter"),
                })
            return results
    except requests.RequestException:
        pass
    return []


def find_recruiters_at_firm(firm):
    """Returns list of {name, first_name, email, title, company, source}"""
    company = firm["name"]
    website = firm["website"]
    contacts = []

    # Step 1: Hunter.io domain search (primary — returns named contacts with titles)
    if HUNTER_API_KEY and website:
        from urllib.parse import urlparse
        domain = urlparse(website).netloc.replace("www.", "")
        if domain:
            hunter_results = hunter_domain_search(domain)
            for h in hunter_results:
                first = (h.get("first_name") or "").strip()
                last = (h.get("last_name") or "").strip()
                full_name = f"{first} {last}".strip() or ""
                contacts.append({
                    "email": h["email"],
                    "first_name": first,
                    "name": full_name,
                    "title": (h.get("title") or "Recruiter").strip(),
                    "source": "hunter",
                })
            if contacts:
                for c in contacts:
                    c["company"] = company
                    c["company_website"] = website
                return contacts

    # Step 2: Firecrawl search (fallback if Hunter finds nothing)
    if FIRECRAWL_API_KEY:
        hits = firecrawl_search(f'"{company}" recruiter contact email site:{website.replace("https://", "").replace("http://", "").split("/")[0]}' if website else f'"{company}" recruiter email', limit=3)
        for hit in hits:
            desc = hit.get("description", "") + " " + hit.get("title", "")
            emails = extract_emails(desc)
            for email in emails:
                contacts.append({"email": email, "first_name": "", "name": "", "title": "Recruiter", "source": "firecrawl_search"})

        # Scrape team/about page
        if not contacts and website:
            for suffix in ["/team", "/about", "/about-us", "/people", "/staff"]:
                url = website.rstrip("/") + suffix
                md = firecrawl_scrape(url)
                if md:
                    emails = extract_emails(md)
                    for email in emails:
                        # Try to extract name near email
                        idx = md.find(email)
                        snippet = md[max(0, idx-100):idx+50]
                        name_match = re.search(r'\*\*([A-Z][a-z]+ [A-Z][a-z]+)\*\*', snippet)
                        name = name_match.group(1) if name_match else ""
                        first = name.split()[0] if name else ""
                        contacts.append({"email": email, "first_name": first, "name": name, "title": "Recruiter", "source": "firecrawl_page"})
                    if contacts:
                        break
                time.sleep(1)


    # Tag with company info
    for c in contacts:
        c["company"] = company
        c["company_website"] = website

    return contacts


# ---------------------------------------------------------------------------
# Step 3: Also search Google/Firecrawl directly for recruiter profiles
# ---------------------------------------------------------------------------

DIRECT_SEARCHES = [
    "digital marketing recruiter email paid media specialist",
    "performance marketing recruiter contact email remote jobs",
    "paid social media recruiter email talent acquisition",
    "facebook ads specialist recruiter hiring contact",
    "meta ads recruiter email talent partner",
]


def find_recruiters_via_search(seen_emails):
    """Firecrawl-search for individual recruiter contacts, not tied to a firm."""
    if not FIRECRAWL_API_KEY:
        return []

    contacts = []
    for query in DIRECT_SEARCHES:
        hits = firecrawl_search(query, limit=5)
        for hit in hits:
            url = hit.get("url", "")
            desc = hit.get("description", "") + " " + hit.get("title", "")
            emails = extract_emails(desc)
            for email in emails:
                if email in seen_emails:
                    continue
                contacts.append({
                    "email": email,
                    "first_name": "",
                    "name": "",
                    "title": "Recruiter",
                    "company": "",
                    "company_website": url,
                    "source": "firecrawl_direct_search",
                })
                seen_emails.add(email)
        time.sleep(1)

    return contacts


# ---------------------------------------------------------------------------
# Email generation
# ---------------------------------------------------------------------------

def generate_email(recruiter):
    name_parts = recruiter.get("name", "").split()
    first = recruiter.get("first_name") or (name_parts[0] if name_parts else "")
    context = f"""Recruiter first name: {first if first else "(unknown — omit greeting name, open with a direct line)"}
Title: {recruiter.get('title', 'Recruiter')}
Company/Firm: {recruiter.get('company', 'your firm')}"""

    raw = call_claude(
        prompt=f"Write the cold email.\n{context}",
        system_prompt=SYSTEM_PROMPT,
        model="haiku",
    )

    if "```json" in raw:
        raw = raw.split("```json")[1].split("```")[0].strip()
    elif "```" in raw:
        raw = raw.split("```")[1].split("```")[0].strip()

    try:
        parsed = json.loads(raw)
        return parsed.get("subject", ""), parsed.get("body", "")
    except json.JSONDecodeError:
        lines = raw.split("\n", 1)
        return lines[0].replace("Subject:", "").strip(), lines[1].strip() if len(lines) > 1 else raw


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run(dry_run=False, limit=15):
    os.makedirs(TMP_DIR, exist_ok=True)
    print("=== Recruiter Finder ===\n")

    seen = load_seen()
    all_contacts = []
    seen_emails_this_run = set(seen)

    # Step 1+2: Apollo firms + known firms → best 1 contact per firm
    print("Step 1: Finding recruiting firms via Apollo…")
    apollo_firms = find_recruiting_firms(limit=20)

    # Merge known firms, skip any already in Apollo results by domain
    apollo_domains = {f["website"].replace("https://", "").replace("http://", "").split("/")[0].replace("www.", "")
                      for f in apollo_firms if f.get("website")}
    extra_firms = [f for f in KNOWN_FIRMS
                   if f["website"].replace("https://", "").replace("http://", "").split("/")[0].replace("www.", "")
                   not in apollo_domains]
    firms = apollo_firms + extra_firms
    print(f"  Total firms to check: {len(firms)} ({len(apollo_firms)} Apollo + {len(extra_firms)} known)")

    print("\nStep 2: Scraping best recruiter per firm…")
    for firm in firms:
        print(f"  {firm['name']} ({firm.get('website', '?')})")
        contacts = find_recruiters_at_firm(firm)
        new = [c for c in contacts if c["email"] not in seen_emails_this_run]
        best = best_contact(new)
        if best:
            seen_emails_this_run.add(best["email"])
            all_contacts.append(best)
            print(f"    → picked: {best.get('name') or best['email']} ({best.get('title', '')})")
        else:
            print(f"    → no new contacts")
        time.sleep(1.5)

    # Step 3: Direct search for individual recruiters
    print("\nStep 3: Searching for individual recruiter profiles…")
    direct = find_recruiters_via_search(seen_emails_this_run)
    all_contacts.extend(direct)
    print(f"  → {len(direct)} contacts from direct search")

    # Filter to truly new (not in seen registry from past runs)
    new_contacts = [c for c in all_contacts if c["email"] not in seen]
    print(f"\nTotal new recruiters to contact: {len(new_contacts)} (skipped {len(all_contacts) - len(new_contacts)} already contacted)")

    new_contacts = new_contacts[:limit]

    if not new_contacts:
        print("No new recruiters found this run.")
        return []

    # Step 4+5: Generate emails + create drafts
    print(f"\nGenerating emails and creating Gmail drafts…\n")
    results = []
    drafts_created = 0

    for i, rec in enumerate(new_contacts, 1):
        print(f"[{i}/{len(new_contacts)}] {rec.get('name') or rec['email']} @ {rec.get('company', '?')}")

        subject, body = generate_email(rec)
        print(f"  Subject: {subject}")

        draft_id = None
        if not dry_run:
            try:
                from tools.gmail_draft import create_draft
                draft_id = create_draft(rec["email"], subject, body)
                print(f"  Draft created: {draft_id}")
                drafts_created += 1
            except Exception as e:
                print(f"  Gmail error: {e}")
        else:
            print(f"  [dry-run] Body: {body[:100]}…")

        results.append({
            "name": rec.get("name", ""),
            "first_name": rec.get("first_name", ""),
            "title": rec.get("title", ""),
            "company": rec.get("company", ""),
            "email": rec["email"],
            "source": rec.get("source", ""),
            "subject": subject,
            "body": body,
            "draft_id": draft_id,
        })

        seen.add(rec["email"])
        time.sleep(1.5)

    save_seen(seen)

    existing_log = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            existing_log = json.load(f)
    with open(LOG_FILE, "w") as f:
        json.dump(existing_log + results, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*60}")
    print(f"RECRUITER OUTREACH DONE")
    print(f"{'='*60}")
    print(f"Firms searched:           {len(firms)}")
    print(f"New contacts found:       {len(new_contacts)}")
    print(f"Gmail drafts created:     {drafts_created}")
    print(f"Log: {LOG_FILE}")

    return results


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    limit = 15
    if "--limit" in sys.argv:
        idx = sys.argv.index("--limit")
        limit = int(sys.argv[idx + 1])
    run(dry_run=dry_run, limit=limit)
