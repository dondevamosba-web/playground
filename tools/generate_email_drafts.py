"""
Generates personalized cold-outreach email drafts for job leads.

Reads from .tmp/recruiter_leads.json, skips companies already in
.tmp/email_drafts.json, then uses the Anthropic API to write a
subject line + short email body for each new lead.

Profile used:
  - Guido Carminatti | carminattiguido@gmail.com
  - 8+ years scaling Google & Meta campaigns
  - 4.5x avg ROAS across 30+ brands, budgets up to $100K/month

Output: appends new drafts to .tmp/email_drafts.json

Usage:
  python3 tools/generate_email_drafts.py
  python3 tools/generate_email_drafts.py --only-with-emails   # skip leads with no email
"""

import json
import os
import subprocess
import sys
import time

TMP_DIR = os.path.join(os.path.dirname(__file__), "..", ".tmp")
LEADS_JSON = os.path.join(TMP_DIR, "recruiter_leads.json")
SMALL_LEADS_JSON = os.path.join(TMP_DIR, "small_company_leads.json")
DRAFTS_JSON = os.path.join(TMP_DIR, "email_drafts.json")

SYSTEM_PROMPT = """You write concise, professional cold-outreach emails for a digital marketing job seeker.

Candidate profile:
- Name: Guido Carminatti
- Email: carminattiguido@gmail.com
- LinkedIn: linkedin.com/in/guidocarminatti
- 8+ years scaling Google & Meta (Facebook/Instagram) ad campaigns
- 4.5x average ROAS across 30+ brands
- Managed budgets exceeding $100K/month
- Strong focus on lead generation, full-funnel optimization, A/B testing
- Worked across e-commerce, SaaS, and service businesses

Tone: confident but not boastful, concise, specific to the role.
Length: 4–6 sentences max. No filler phrases like "I hope this email finds you well."
Always end with the signature block:
  Guido Carminatti | carminattiguido@gmail.com | linkedin.com/in/guidocarminatti
"""


def load_existing_drafts():
    if os.path.exists(DRAFTS_JSON):
        with open(DRAFTS_JSON) as f:
            return json.load(f)
    return []


def already_drafted(drafts, company, job_url):
    for d in drafts:
        if d.get("job_url") == job_url:
            return True
        if d.get("company", "").lower() == company.lower() and d.get("job_url", ""):
            return True
    return False


def load_leads():
    # Merge both files; prefer the entry with an email when URLs collide
    by_url = {}

    for path in [LEADS_JSON, SMALL_LEADS_JSON]:
        if not os.path.exists(path):
            continue
        with open(path) as f:
            data = json.load(f)
        for j in data:
            url = j.get("url", "")
            if not url:
                continue
            emails = j.get("emails", "") or j.get("emails_found", "")
            entry = {
                "title": j.get("title", ""),
                "company": j.get("company", ""),
                "location": j.get("location", ""),
                "url": url,
                "source": j.get("source", ""),
                "emails": emails,
                "description_preview": j.get("description_preview", ""),
            }
            existing = by_url.get(url)
            if existing is None or (emails and not existing["emails"]):
                by_url[url] = entry

    return list(by_url.values())


def generate_draft(job):
    desc = job["description_preview"][:400] if job["description_preview"] else "(no description available)"
    prompt = (
        SYSTEM_PROMPT + "\n\n"
        f"Write a cold-outreach email for this job posting.\n\n"
        f"Job title: {job['title']}\n"
        f"Company: {job['company']}\n"
        f"Location: {job['location']}\n"
        f"Description excerpt: {desc}\n\n"
        "Return a JSON object with exactly two keys:\n"
        '  "subject": the email subject line (max 12 words, specific to this role/company)\n'
        '  "body": the email body (4-6 sentences, ends with the signature block)\n\n'
        "Return only the raw JSON object, no markdown fences."
    )

    result = subprocess.run(
        ["claude", "-p", prompt, "--output-format", "json", "--model", "haiku"],
        capture_output=True, text=True, timeout=60,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "claude CLI failed")

    outer = json.loads(result.stdout.strip())
    raw = outer.get("result", result.stdout.strip())

    # Handle if raw is already a dict
    if isinstance(raw, dict):
        return raw

    # Strip optional markdown fences
    if isinstance(raw, str):
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()
        return json.loads(raw)

    raise ValueError(f"Unexpected output type: {type(raw)}")


def run(only_with_emails=False):
    os.makedirs(TMP_DIR, exist_ok=True)
    leads = load_leads()
    existing_drafts = load_existing_drafts()

    print(f"Loaded {len(leads)} leads, {len(existing_drafts)} existing drafts")

    to_process = []
    for lead in leads:
        if not lead["title"] or not lead["company"]:
            continue
        if already_drafted(existing_drafts, lead["company"], lead["url"]):
            continue
        if only_with_emails and not lead["emails"]:
            continue
        to_process.append(lead)

    print(f"New leads to draft: {len(to_process)}")
    if not to_process:
        print("Nothing new to draft.")
        return existing_drafts

    new_drafts = []
    for i, job in enumerate(to_process, 1):
        print(f"  [{i}/{len(to_process)}] {job['title']} @ {job['company']}")
        try:
            result = generate_draft(job)
            draft = {
                "source": job["source"],
                "job_title": job["title"],
                "company": job["company"],
                "location": job["location"],
                "job_url": job["url"],
                "to": job["emails"],
                "subject": result["subject"],
                "body": result["body"],
            }
            new_drafts.append(draft)
            print(f"    Subject: {result['subject']}")
        except Exception as e:
            print(f"    Error: {e}")

        time.sleep(0.5)

    all_drafts = existing_drafts + new_drafts

    with open(DRAFTS_JSON, "w", encoding="utf-8") as f:
        json.dump(all_drafts, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*60}")
    print(f"Added {len(new_drafts)} new drafts  (total: {len(all_drafts)})")
    print(f"Saved: {DRAFTS_JSON}")

    with_emails = [d for d in new_drafts if d["to"]]
    without_emails = [d for d in new_drafts if not d["to"]]
    print(f"\nNew drafts with email address:    {len(with_emails)}")
    print(f"New drafts without email address: {len(without_emails)}")

    if with_emails:
        print(f"\n{'='*60}")
        print(f"READY TO SEND ({len(with_emails)})")
        print(f"{'='*60}")
        for d in with_emails:
            print(f"\n  To: {d['to']}")
            print(f"  Subject: {d['subject']}")
            print(f"  Role: {d['job_title']} @ {d['company']}")

    return all_drafts


if __name__ == "__main__":
    only_with_emails = "--only-with-emails" in sys.argv
    run(only_with_emails=only_with_emails)
