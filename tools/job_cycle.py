"""
Full job search cycle: find new jobs → generate tailored emails → create Gmail drafts.

Skips jobs already seen in previous runs (tracked in .tmp/seen_jobs.json).

Usage:
    python3 tools/job_cycle.py              # run with defaults
    python3 tools/job_cycle.py --pages 3    # deeper LinkedIn search
    python3 tools/job_cycle.py --dry-run    # generate emails but skip Gmail
"""

import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date

import subprocess

# Allow importing from tools/
sys.path.insert(0, os.path.dirname(__file__))
from search_jobs import run as search_jobs
from claude_call import call_claude

TMP = os.path.join(os.path.dirname(__file__), "..", ".tmp")
SEEN_FILE = os.path.join(TMP, "seen_jobs.json")
LOG_FILE = os.path.join(TMP, "cycle_log.json")
SMALL_LEADS_FILE = os.path.join(TMP, "small_company_leads.json")
RECRUITER_LEADS_FILE = os.path.join(TMP, "recruiter_leads.json")

PROFILE = """Candidate: Guido Carminatti
8+ years paid media specialist. Remote from Argentina, works EST hours (UTC-3).
Key results:
- Scaled Meta ad spend $10K → $100K+/month
- CPA reduced 30% through systematic creative testing
- 4.5x average ROAS across 30+ US brands (DTC, e-commerce, SaaS, lead gen)
Currently: Marketing Producer & Campaign Manager — owns Meta, Google Ads, and email end-to-end.
Tools: Meta Ads Manager, Google Ads, GoHighLevel, Looker Studio, GA4.
Looking for: fully remote roles with US or Canada companies, Meta/paid social focus.
Contact: carminattiguido@gmail.com | linkedin.com/in/guidocarminatti"""


# ── Email lookup ──────────────────────────────────────────────────────────────

_EMAIL_GOOD = {"recruit", "recruiting", "recruitment", "hiring", "talent", "ta",
               "hr", "career", "careers", "jobs", "people", "apply", "staffing"}
_EMAIL_BAD  = {"info", "contact", "support", "help", "hello", "customerservice",
               "customer", "feedback", "privacy", "legal", "vendor", "disability",
               "noreply", "operations", "admin", "general", "media", "press",
               "sales", "marketing", "team", "office", "enquiries", "hello"}


def _email_score(email: str) -> int:
    local = email.split("@")[0].lower().replace("-", "").replace("_", "")
    for word in _EMAIL_GOOD:
        if word in local:
            return 2
    for word in _EMAIL_BAD:
        if word in local:
            return -1
    if "." in local and 4 < len(local) < 30:  # personal name pattern
        return 1
    return 0


def _best_email(emails) -> str | None:
    if isinstance(emails, str):
        emails = [e.strip() for e in emails.split(",") if e.strip()]
    scored = sorted(((e, _email_score(e)) for e in emails if e), key=lambda x: x[1], reverse=True)
    for email, score in scored:
        if score >= 0:
            return email
    return None


def _cache_email_result(company_name: str, result: dict):
    data = []
    if os.path.exists(SMALL_LEADS_FILE):
        with open(SMALL_LEADS_FILE, encoding="utf-8") as f:
            data = json.load(f)
    if any(d.get("company", "").lower().strip() == company_name.lower().strip() for d in data):
        return
    data.append({
        "company": company_name,
        "company_website": result.get("website", ""),
        "emails_found": ", ".join(result.get("emails", [])),
        "notes": result.get("source", "firecrawl_lookup"),
    })
    with open(SMALL_LEADS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def lookup_recruiter_email(company_name: str) -> str | None:
    """Check cached files, then try Firecrawl. Returns best recruiting email or None."""
    name_lower = company_name.lower().strip()

    for cache_path in [SMALL_LEADS_FILE, RECRUITER_LEADS_FILE]:
        if not os.path.exists(cache_path):
            continue
        with open(cache_path, encoding="utf-8") as f:
            data = json.load(f)
        for entry in data:
            if entry.get("company", "").lower().strip() == name_lower:
                emails = entry.get("emails_found", "") or entry.get("emails", "")
                email = _best_email(emails)
                if email:
                    return email

    if os.getenv("FIRECRAWL_API_KEY"):
        try:
            from find_recruiter_emails import find_company_emails
            result = find_company_emails(company_name)
            _cache_email_result(company_name, result)
            return _best_email(result.get("emails", []))
        except Exception:
            pass

    return None


def load_seen() -> set:
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, encoding="utf-8") as f:
            return set(json.load(f).get("urls", []))
    return set()


def save_seen(urls: set):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump({"urls": sorted(urls), "last_updated": str(date.today())}, f, indent=2)


_EMAIL_SYSTEM_PROMPT = f"""You are a concise cold outreach email writer for a paid media specialist.

Candidate profile:
{PROFILE}

Rules:
- 4-6 sentences max, no fluff
- Lead with the most relevant stat for this specific role
- Mention 1-2 results from the profile
- End with a CTA: 15-minute call
- Sign off: Guido Carminatti | carminattiguido@gmail.com | linkedin.com/in/guidocarminatti
- Plain text only"""


def generate_email(job: dict) -> dict:
    """Generate subject + body for a job. PROFILE is cached in system prompt."""
    job_info = (
        f"Title: {job['title']}\n"
        f"Company: {job['company']}\n"
        f"Location: {job['location']} ({job['country']})\n"
        f"Context: {job.get('snippet', '')} {job.get('query_source', '')}"
    )

    body = call_claude(
        f"Write a cold outreach email applying for this job (no subject line in body):\n\n{job_info}",
        system_prompt=_EMAIL_SYSTEM_PROMPT,
        model="haiku",
    )

    subject = call_claude(
        f"Write an 8-10 word subject line for a cold email applying to: {job['title']} at {job['company']}. "
        "Lead with a result stat. No brackets. Plain text only. Just the subject line.",
        model="haiku",
    )

    return {"subject": subject, "body": body}


def run_cycle(pages: int = 2, dry_run: bool = False):
    os.makedirs(TMP, exist_ok=True)

    print("=" * 60)
    print(f"JOB CYCLE — {date.today()}")
    print("=" * 60)

    # 1. Search
    print("\n[1/5] Searching for jobs...")
    all_jobs = search_jobs(pages=pages)
    relevant = [j for j in all_jobs if j.get("relevant")]
    print(f"  Found {len(all_jobs)} total, {len(relevant)} relevant")

    # 2. Dedup + auto-filter known non-fits
    SKIP_COMPANIES = {"meta", "nasdaq", "jockey", "belfor", "tenaquip"}
    SKIP_LOCATION_KEYWORDS = ["in-office", "on-site", "on site"]

    seen = load_seen()
    seen_companies = set()
    new_jobs = []
    for j in relevant:
        company_key = j.get("company", "").lower().strip()
        if (
            j["url"] not in seen
            and company_key not in SKIP_COMPANIES
            and not any(kw in j.get("location", "").lower() for kw in SKIP_LOCATION_KEYWORDS)
            and company_key not in seen_companies
        ):
            new_jobs.append(j)
            seen_companies.add(company_key)

    skipped = len(relevant) - len(new_jobs)
    print(f"\n[2/5] Dedup: {len(new_jobs)} new jobs (skipping {skipped} already seen or duplicate company)")

    if not new_jobs:
        print("\nNothing new this run. Try again tomorrow or add --pages 4.")
        return []

    # 3. Generate emails in parallel
    WORKERS = min(8, len(new_jobs))
    print(f"\n[3/5] Generating {len(new_jobs)} emails ({WORKERS} parallel workers)...")
    drafts = []

    def _generate(job):
        return job, generate_email(job)

    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = {pool.submit(_generate, job): job for job in new_jobs}
        for future in as_completed(futures):
            job = futures[future]
            label = f"{job['title']} @ {job['company']}"
            try:
                _, email = future.result()
                drafts.append({**job, **email, "draft_id": None, "recruiter_email": None})
                seen.add(job["url"])
                print(f"  ✓ {label}")
            except Exception as e:
                print(f"  ✗ {label}: {e}")

    # 4. Look up recruiter emails in parallel
    print(f"\n[4/5] Looking up recruiter emails ({min(4, len(drafts))} parallel workers)...")
    email_map = {}

    def _lookup(draft):
        return draft["company"], lookup_recruiter_email(draft["company"])

    with ThreadPoolExecutor(max_workers=min(4, len(drafts))) as pool:
        futures = {pool.submit(_lookup, d): d for d in drafts}
        for future in as_completed(futures):
            company, email = future.result()
            email_map[company] = email
            tag = f"→ {email}" if email else "→ not found"
            print(f"  {company}: {tag}")

    found_count = sum(1 for e in email_map.values() if e)
    print(f"  Emails found: {found_count}/{len(drafts)}")

    for draft in drafts:
        draft["recruiter_email"] = email_map.get(draft["company"])

    # 5. Create Gmail drafts
    if dry_run:
        print("\n[5/5] Dry run — skipping Gmail. Emails saved to cycle_log.json.")
    else:
        print(f"\n[5/5] Creating {len(drafts)} Gmail drafts...")
        from gmail_draft import create_draft

        # Label_8 = 🔄 Auto Draft (always applied)
        AUTO_LABEL = "Label_8"

        for draft in drafts:
            recruiter_email = draft.get("recruiter_email")
            to_addr = recruiter_email or "dondevamosba@gmail.com"
            subject = draft["subject"] if recruiter_email else f"⚠️ NO EMAIL — {draft['subject']}"
            recipient_line = (
                f"To: {recruiter_email}\n"
                if recruiter_email
                else "⚠️ Find recruiter email before sending\n"
            )
            try:
                result = create_draft(
                    to=to_addr,
                    subject=subject,
                    body=(
                        f"Job: {draft['title']} @ {draft['company']}\n"
                        f"Apply: {draft['url']}\n"
                        f"{recipient_line}"
                        "\n---\n\n"
                        f"{draft['body']}"
                    ),
                    label_ids=[AUTO_LABEL]
                )
                draft["draft_id"] = result["draft_id"]
                draft["message_id"] = result["message_id"]
                tag = f"({recruiter_email})" if recruiter_email else "(no email — flagged)"
                print(f"  ✓ {draft['company']} {tag}")
            except Exception as e:
                print(f"  ✗ {draft['company']}: {e}")

    # Save seen registry and log
    save_seen(seen)
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(drafts, f, indent=2, ensure_ascii=False)

    # Summary
    pushed = sum(1 for d in drafts if d.get("draft_id"))
    with_email = sum(1 for d in drafts if d.get("recruiter_email"))
    needs_email = len(drafts) - with_email
    print(f"\n{'=' * 60}")
    print(f"CYCLE COMPLETE")
    print(f"  New jobs found:       {len(new_jobs)}")
    print(f"  Emails generated:     {len(drafts)}")
    print(f"  Recruiter email found:{with_email}")
    print(f"  Needs email (⚠️):    {needs_email}")
    if not dry_run:
        print(f"  Gmail drafts:         {pushed}")
    print(f"  Log:                  {LOG_FILE}")
    print(f"{'=' * 60}")

    return drafts


if __name__ == "__main__":
    pages = 2
    dry_run = False

    if "--pages" in sys.argv:
        pages = int(sys.argv[sys.argv.index("--pages") + 1])
    if "--dry-run" in sys.argv:
        dry_run = True

    run_cycle(pages=pages, dry_run=dry_run)
