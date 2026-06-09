# Workflow: Scrape Remote Job Leads (Global — US/CA primary, Europe secondary)

## Objective

Find remote marketing / paid media / performance marketing roles open to candidates based outside the US. Primary targets: US and Canada. Secondary: Europe. Extract company contact emails for outreach.

## Sources

| Source | API Type | Notes |
|--------|----------|-------|
| **RemoteOK** | Public JSON API | `remoteok.com/api?tag=...` — first array item is legal notice, skip it |
| **Jobicy** | Public JSON API | `jobicy.com/api/v2/remote-jobs?industry=marketing` |
| **Working Nomads** | Public JSON API | `workingnomads.com/api/exposed_jobs/?category=marketing` |
| **Himalayas** | Public JSON API | `himalayas.app/jobs/api?categories=Marketing` — has `locationRestrictions` field for precise filtering |
| **Remotive** | Public JSON API | `remotive.com/api/remote-jobs?category=marketing&search=...` — searched for 5 paid media terms |

**Not used:** We Work Remotely (Cloudflare 403), LinkedIn (ToS).

## Location Status Logic

Each job gets one of five statuses:

| Status | Meaning | Included in leads? |
|--------|---------|---------------------|
| `open` | Explicit LATAM/Americas/Worldwide signal | Yes — best tier |
| `unknown` | Remote but no explicit region signal | Yes — second tier |
| `us_only` | US-only language in description | Yes — flagged, worth checking |
| `europe` | Explicitly EU/UK/EMEA restricted | Yes — secondary option |
| `non_latam` | Explicitly APAC/Middle East/Africa restricted | No — excluded |

## Steps

### Step 1 — Scrape job boards

```bash
python3 tools/scrape_latam_remote_jobs.py
```

Outputs:
- `.tmp/latam_remote_jobs.json` — full dataset with all 280+ jobs
- `.tmp/latam_remote_jobs.csv` — spreadsheet of relevant leads only
- `.tmp/recruiter_leads.json` — merged with existing data, ready for email finder

### Step 2 — Find contact emails

```bash
python3 tools/find_recruiter_emails.py
```

Reads from `.tmp/recruiter_leads.json`, uses Firecrawl to scrape company contact pages, optionally uses Hunter.io for domain-level email lookup.

Outputs:
- `.tmp/small_company_leads.csv` — leads with emails
- `.tmp/small_company_leads.json` — same as JSON

### Step 3 — Generate outreach emails

```bash
python3 tools/generate_email_drafts.py
```

Reads from `.tmp/recruiter_leads.json` (and `small_company_leads.json` if it exists), generates a personalized email per job using Claude, saves to `.tmp/email_drafts.json`.

### Step 4 — Review and send

Open `.tmp/email_drafts.json` and prioritize:
1. `latam_status = open` + has email → send directly
2. `latam_status = unknown` (worldwide/remote) + has email → send
3. `latam_status = europe` + has email → send, mention timezone overlap with EST
4. Manually verify `us_only` flagged jobs before contacting

## Refresh Cadence

Run weekly — RemoteOK and Jobicy refresh their listings daily. New leads are appended to `recruiter_leads.json` without duplicating existing entries.

## Known Behaviors

- **RemoteOK rate limits**: 3s delay between tag requests. Don't run more than once every 10 minutes.
- **Jobicy `design` category returns 400**: Harmless — only `marketing` works.
- **Working Nomads `business-dev` yields 0 new**: Their business-dev category has no marketing overlap; keep it for future use.
- **Himalayas returns 20 jobs per category**: Their API doesn't paginate — coverage is limited but location data is precise.
- **Remotive**: Searched with 5 terms (paid media, performance marketing, facebook ads, meta ads, paid social). Results deduplicated by URL — a job matching multiple terms is only counted once.
- **Europe jobs**: Included as `europe` tier. APAC/Middle East/Africa jobs are still excluded.

## Adding More Job Boards

To add a new source, implement a `scrape_<source>()` function that returns a list of dicts with these fields:

```python
{
    "source": str,
    "title": str,
    "company": str,
    "location": str,      # raw location string from the source
    "date_posted": str,   # YYYY-MM-DD
    "url": str,           # canonical job URL
    "snippet": str,       # description excerpt (400 chars max)
    "latam_status": str,  # open / unknown / us_only / non_latam
    "relevant": bool,     # True if matches RELEVANCE_KEYWORDS
    "emails": str,        # leave empty — filled by find_recruiter_emails.py
}
```

Then add the call to `run()` and merge the results.
