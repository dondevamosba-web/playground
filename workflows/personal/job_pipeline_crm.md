# Job Application Pipeline CRM — Workflow SOP

## Objective
Track every job application through the full funnel — from draft to offer —
without losing follow-ups or forgetting who replied.

## Funnel Stages
```
Drafted → Sent → Replied → Interview Scheduled → Offer | Rejected | Ghosted
```

## Daily Routine (5 min)

### 1. Check what needs follow-up
```bash
python3 tools/job_pipeline.py followups
```
Flags applications that were sent 4+ days ago with no status update.
Follow up with a short 2-line reply. Do not follow up more than once after initial send.

### 2. Update statuses as things move
When a recruiter replies, schedules an interview, or rejects:
```bash
python3 tools/job_pipeline.py update --company "Stripe" --status "Replied"
python3 tools/job_pipeline.py update --company "Stripe" --status "Interview Scheduled"
python3 tools/job_pipeline.py update --company "Stripe" --status "Rejected"
```

### 3. View full funnel
```bash
python3 tools/job_pipeline.py report
```
Shows count per stage with a bar chart. Good for weekly review.

## Weekly Routine (10 min)

1. Run `job_cycle.py` to find and draft new applications
2. Run `log_outreach.py` to sync new drafts into the sheet
3. Run `job_pipeline.py followups` to see what needs follow-up
4. Run `job_pipeline.py report` to assess funnel health

## Manual Add (applied outside job_cycle)
If you applied directly on a company portal, LinkedIn Easy Apply, etc.:
```bash
python3 tools/job_pipeline.py add \
  --company "Stripe" \
  --title "Growth Marketing Manager" \
  --url "https://stripe.com/jobs/..." \
  --location "Remote" \
  --email "recruiter@stripe.com" \
  --notes "Applied via LinkedIn"
```

## Open the Sheet
```bash
python3 tools/job_pipeline.py open
```
Or access directly via Google Sheets → "Outreach Tracker" → Jobs tab.

## Status Definitions
| Status             | Meaning                                              |
|--------------------|------------------------------------------------------|
| Drafted            | Email created in Gmail, not yet sent                 |
| Sent               | Email sent, waiting for response                     |
| Replied            | They responded (positive or neutral)                 |
| Interview Scheduled| Call or interview confirmed                          |
| Offer              | Offer received                                       |
| Rejected           | Formal rejection received                            |
| Ghosted            | No response after 2 follow-up attempts               |

## Files
- `tools/job_pipeline.py` — CLI for viewing and updating the pipeline
- `tools/job_cycle.py` — finds new jobs and creates Gmail drafts
- `tools/log_outreach.py` — syncs drafts into the Google Sheet
- `tools/outreach_tracker.py` — Google Sheets client (shared with Storm Digital)
- `.tmp/seen_jobs.json` — deduplication: jobs already processed
