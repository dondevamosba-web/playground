# Client Performance Reporting — Workflow SOP

## Objective
Deliver weekly/monthly branded PDF performance reports to clients —
pulls live data from Meta Ads API, generates insights, auto-drafts the email.

## Prerequisites

### One-time setup: Meta Ads API token
1. Go to [business.facebook.com](https://business.facebook.com) → Settings → System Users
2. Create a system user with Admin role on the client's Ad Account
3. Generate a token with `ads_read` and `ads_management` permissions
4. Add to `.env`:
   ```
   META_ACCESS_TOKEN=your_long_lived_token
   META_AD_ACCOUNT_ID=act_XXXXXXXXXX
   ```
   The Ad Account ID is found in Meta Ads Manager → Account Overview → Account ID.
   Prepend `act_` to the numeric ID.

## Step-by-Step

### Step 1 — Pull data from Meta Ads API
```bash
python3 tools/pull_meta_report.py --days 7
```
Output: `.tmp/meta_report_YYYY-MM-DD.json`

For monthly reports:
```bash
python3 tools/pull_meta_report.py --days 30
```

### Step 2 — Generate the PDF report
```bash
python3 tools/generate_client_report.py \
  --input .tmp/meta_report_2025-05-19.json \
  --client "ABC Roofing"
```
Output: `.tmp/report_ABC_Roofing_2025-05-19.pdf`

### Step 3 — Create Gmail draft with PDF attached
```bash
python3 tools/generate_client_report.py \
  --input .tmp/meta_report_2025-05-19.json \
  --client "ABC Roofing" \
  --draft
```
Opens Gmail drafts with the report attached and a personalized summary email body.
Review, add the client's email address, and send.

## Full one-liner (weekly report)
```bash
python3 tools/pull_meta_report.py --days 7 && \
python3 tools/generate_client_report.py \
  --input $(ls -t .tmp/meta_report_*.json | head -1) \
  --client "CLIENT NAME" \
  --draft
```

## Report Contents
1. **KPI Cards** — Spend, Leads, CPL, CTR, CPC, CPM vs prior period
2. **Campaign Breakdown** — Per-campaign spend, leads, CPL, CTR, CPM
3. **Key Insights** — Auto-generated analysis of what moved and why
4. **Recommended Next Steps** — Actionable items for the next period

## Report Cadence
- **Weekly**: Every Monday for the prior week (Mon–Sun)
- **Monthly**: First Monday of the month for the prior month
- Send within 48 hours of period close

## Multiple Clients
For each client, maintain a separate `.env` variable or override at runtime:
```bash
META_AD_ACCOUNT_ID=act_111111 python3 tools/pull_meta_report.py --days 7 \
  --out .tmp/meta_report_client_a.json
```

## Edge Cases
- **No lead conversion events**: CPL will show "—" — check that lead events are
  properly configured in Meta Events Manager
- **API rate limits**: If you hit limits, wait 1 hour. Token allows ~200 calls/hour
- **Token expires**: Long-lived tokens last ~60 days. Renew before expiry via
  the Meta Graph API Explorer or by regenerating via System Users
- **Zero spend days**: The prior period comparison may look dramatic if campaigns
  were paused — add a note in the Gmail draft body

## Files
- `tools/pull_meta_report.py` — Meta Ads API data puller
- `tools/generate_client_report.py` — PDF generator + Gmail draft creator
- `.tmp/meta_report_*.json` — raw API data (keep for audit trail)
- `.tmp/report_*.pdf` — generated client reports
