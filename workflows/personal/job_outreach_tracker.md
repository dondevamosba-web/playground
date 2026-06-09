# Workflow: Job Outreach Tracker

## Objective

Keep a Google Sheet called **"Job Outreach Tracker"** in sync with your email drafts, and surface follow-ups that are overdue.

## The Sheet

| Column | Purpose |
|--------|---------|
| Company | Hiring company name |
| Job Title | Role title |
| Location | City / remote |
| Job URL | Source posting URL (deduplication key) |
| Email To | Recruiter / contact email |
| Subject | Email subject line |
| **Status** | Lifecycle stage (see below) |
| Date Added | When the row was created |
| **Follow-up Date** | Fill this in when you send the email |
| Notes | Anything worth remembering about this lead |

### Status lifecycle

`Drafted` → `Sent` → `Replied` → `Interview Scheduled` → `Offer` / `Rejected` / `Ghosted`

Update Status and Follow-up Date manually in the sheet as things progress.

## Full pipeline (all steps)

### Step 1 — Find jobs
```bash
python3 tools/search_jobs.py
```
Output: `.tmp/jobs_summary.csv`, `.tmp/jobs.json`

### Step 2 — Find recruiter emails
```bash
python3 tools/find_recruiter_emails.py
```
Output: `.tmp/recruiter_leads.json`

### Step 3 — Generate email drafts
```bash
python3 tools/generate_email_drafts.py --only-with-emails
```
Output: `.tmp/email_drafts.json`

### Step 4 — Sync to Google Sheet
```bash
python3 tools/log_outreach.py
```
- Creates "Job Outreach Tracker" in your Google Drive if it doesn't exist
- Adds new drafts as rows with Status = "Drafted"
- Never overwrites existing rows (your manual edits are safe)
- Prints the sheet URL

### Step 5 — Send emails manually

Open the sheet. Copy the subject + body from `.tmp/email_drafts.json` (or Gmail drafts if you created them there), send each email, then:
1. Change Status → `Sent`
2. Set Follow-up Date to 5–7 days from now

### Step 6 — Check follow-ups (run daily)
```bash
python3 tools/check_followups.py
```
Prints everyone with Status = `Sent` and a Follow-up Date that has passed.

To see the full pipeline at a glance:
```bash
python3 tools/check_followups.py --all
```

## Auth (one-time setup)

These tools use Google Sheets + Drive APIs and store credentials in `token_sheets.json`.

The first time you run `log_outreach.py`, a browser window will open for OAuth consent. After that, the token auto-refreshes.

Required APIs (already enabled if Drive upload works):
- Google Sheets API
- Google Drive API

If you get a scope error, delete `token_sheets.json` and re-run to re-auth.

## Quick reference

| Task | Command |
|------|---------|
| Sync drafts → sheet | `python3 tools/log_outreach.py` |
| Get sheet URL | `python3 tools/log_outreach.py --url` |
| Check today's follow-ups | `python3 tools/check_followups.py` |
| See full pipeline status | `python3 tools/check_followups.py --all` |
