# Workflow: Search Job Opportunities — Paid Media / Meta Ads Specialist

## Objective

Find open positions for Paid Media Specialist roles in the US and Canada, specifically targeting Meta (Facebook/Instagram) advertising with a focus on lead generation campaigns. Results are saved locally as JSON and CSV for review.

## Data Sources

| Source | Why |
|--------|-----|
| **LinkedIn** (public guest API) | Best coverage for US/CA roles, no auth needed, returns structured HTML |
| **Remotive API** | Remote-first roles open to US/CA/Americas/Worldwide |

No browser automation needed — both sources work with simple HTTP requests.

## Required Inputs

None — queries are pre-configured in the tool.

Optional flags:
- `--country us` or `--country ca` to narrow LinkedIn to one country
- `--pages N` to control how many pages per LinkedIn query (default: 2, each page = 10 jobs)

## Tool

`tools/search_jobs.py`

## LinkedIn Search Queries (pre-configured)

| Query | Location |
|-------|----------|
| paid media specialist meta | United States |
| meta ads specialist | United States |
| facebook ads specialist | United States |
| paid social media specialist | United States |
| performance marketing specialist meta | United States |
| paid media specialist meta | Canada |
| meta ads specialist | Canada |
| facebook ads specialist | Canada |

## Steps

### 1. Run the scraper

```bash
python3 tools/search_jobs.py
```

US only:
```bash
python3 tools/search_jobs.py --country us
```

Canada only:
```bash
python3 tools/search_jobs.py --country ca
```

More pages (deeper results):
```bash
python3 tools/search_jobs.py --pages 4
```

### 2. Review outputs

**CSV — open in Excel or upload to Google Sheets:**
```
.tmp/jobs_summary.csv
```
Contains only relevant jobs (title/description mentions meta, facebook, instagram, paid social, or leads). Ready for review.

**JSON — full dataset:**
```
.tmp/jobs.json
```
All scraped jobs with `relevant: true/false` flag.

### 3. Refine if needed

To add queries: edit the `LINKEDIN_SEARCHES` or `REMOTIVE_SEARCHES` list in `tools/search_jobs.py`.

To adjust relevance: edit `RELEVANCE_KEYWORDS` in the same file.

## Output Fields

| Field | Description |
|-------|-------------|
| title | Job title |
| company | Hiring company |
| location | City / state / remote status |
| country | US, CA, or US/CA (Remotive) |
| salary | Salary if listed (LinkedIn rarely shows it; Remotive often does) |
| date_posted | ISO date or relative (LinkedIn) |
| url | Direct link to the job posting |
| source | LinkedIn or Remotive |
| query_source | Which search query found this job |
| snippet | Short description preview (Remotive only) |
| relevant | true if matches relevance keywords |

## Known Behaviors

- **LinkedIn rate limiting**: The tool adds 2s between pages and 3s between queries. If you run it too frequently (multiple times in a few minutes), LinkedIn may return fewer results temporarily. Wait a few minutes before re-running.
- **Deduplication**: Jobs found across multiple queries are deduplicated by URL. The `query_source` field shows which query first captured each job.
- **Remotive coverage**: Remotive only lists ~20 marketing jobs total at any time. Results are filtered to exclude positions that explicitly restrict to non-US/CA regions (e.g., Europe only, LATAM only).
- **Sorted output**: Relevant jobs in the CSV are sorted with US first, then CA, then global roles, newest first.

## Export to Google Sheets (optional)

Open `.tmp/jobs_summary.csv` and upload to Google Drive:
- In Google Drive: New → File upload → select the CSV
- Then: Open with Google Sheets
- Share the sheet for collaborative review
