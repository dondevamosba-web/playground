# Workflow: Job Search Cycle — Paid Media / Meta Ads Specialist

## Objective

Automatically find new paid media / Meta Ads Specialist job openings, generate a tailored cold email for each, and push them as Gmail drafts — ready to review and send.

Skips jobs already seen in previous runs so every execution only produces truly new drafts.

## Tool

`tools/job_cycle.py`

## Usage

```bash
# Standard run (2 pages per LinkedIn query)
python3 tools/job_cycle.py

# Deeper search (4 pages)
python3 tools/job_cycle.py --pages 4

# Test mode — generates emails but does NOT create Gmail drafts
python3 tools/job_cycle.py --dry-run
```

## What It Does (in order)

1. **Search** — runs LinkedIn + Remotive queries (same as `tools/search_jobs.py`)
2. **Filter** — keeps only jobs matching relevance keywords (meta, facebook, instagram, paid social, leads)
3. **Dedup** — skips jobs already in `.tmp/seen_jobs.json` (processed in past runs)
4. **Generate** — calls Claude Haiku via Anthropic SDK to write a tailored cold email per job
5. **Draft** — creates each email as a Gmail draft via Gmail API (`token_gmail.json`)
6. **Log** — saves results to `.tmp/cycle_log.json` and updates the seen-jobs registry

## Outputs

| File | Description |
|------|-------------|
| `.tmp/cycle_log.json` | Full log of this run — jobs found + email content + draft IDs |
| `.tmp/seen_jobs.json` | Registry of all job URLs ever processed (dedup database) |
| Gmail Drafts | New drafts land in your drafts folder, ready to send |

## After Running

1. Open Gmail → Drafts
2. Review each draft — update the **To:** field with the actual hiring contact or company email before sending
3. For jobs with **⚠️ Apply via:** in the body — use that portal link instead of emailing

## How Often to Run

- **Every 2–3 days** for fresh results — LinkedIn job postings turn over quickly
- Run with `--pages 4` on weekends for a deeper crawl
- Don't run more than once per hour — LinkedIn rate-limits aggressive scraping

## Dependencies

- `token_gmail.json` — Gmail OAuth token (already authorized, auto-refreshes)
- `credentials.json` — Google OAuth client credentials
- `ANTHROPIC_API_KEY` in `.env` — used by the Anthropic SDK for email generation

## Known Behaviors

- **New run, zero results**: all current postings were already seen. Wait 2–3 days for new listings to appear on LinkedIn.
- **Haiku timeout**: rare; affected job is skipped and logged. Re-run to retry.
- **LinkedIn 429**: too many requests. Wait 10 minutes before re-running.
- **Gmail 403**: Gmail API disabled. Re-enable at console.developers.google.com.

## Automated Daily Run

Use `tools/job_cycle_auto.py` to run the full pipeline in one command:

```bash
# Standard run — scrapes LATAM boards + runs job_cycle + sends digest draft
python3 tools/job_cycle_auto.py

# Deeper LinkedIn search (weekend crawl)
python3 tools/job_cycle_auto.py --pages 4

# Skip LATAM scrape if you ran it recently (use cached data)
python3 tools/job_cycle_auto.py --no-scrape

# Test mode — no Gmail drafts created, digest printed to terminal only
python3 tools/job_cycle_auto.py --dry-run
```

**What it does in 5 steps:**
1. Scrapes RemoteOK, Jobicy, Working Nomads, Himalayas, Remotive for LATAM-friendly paid media roles
2. Runs `job_cycle.py --pages N` as a subprocess to find LinkedIn/Remotive jobs and generate tailored email drafts
3. Reads pipeline funnel counts from the Outreach Tracker Google Sheet
4. Checks for applications 4+ days old with no status update (follow-ups due)
5. Creates a single Gmail digest draft to dondevamosba@gmail.com summarising all of the above

Run every 2–3 days, same cadence as `job_cycle.py` alone.

## Resetting the Seen-Jobs Registry

To reprocess all jobs (e.g. after a long pause):
```bash
rm .tmp/seen_jobs.json
python3 tools/job_cycle.py
```
