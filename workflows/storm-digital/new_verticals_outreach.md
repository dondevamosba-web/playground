# New Verticals Lead Outreach — Workflow SOP

## Objective
Expand Storm Digital's lead outreach beyond roofing and HVAC using the same proven pipeline:
scrape → qualify → draft → send → log.

## Supported Verticals
| Vertical        | Search query used          | Leads file                     |
|-----------------|----------------------------|--------------------------------|
| landscaping     | landscaping company        | .tmp/landscaping_leads.json    |
| plumbing        | plumber                    | .tmp/plumbing_leads.json       |
| dental          | dentist                    | .tmp/dental_leads.json         |
| solar           | solar panel installation   | .tmp/solar_leads.json          |
| chiropractic    | chiropractor               | .tmp/chiropractic_leads.json   |
| pest_control    | pest control company       | .tmp/pest_control_leads.json   |
| electrician     | electrician                | .tmp/electrician_leads.json    |
| painting        | painting contractor        | .tmp/painting_leads.json       |

## Target Profile (all verticals)
- 1–15 employees
- Google Maps reviews: <100 (small = more likely to need help)
- Pain: inconsistent leads, word of mouth, or bad experience with shared lead platforms
- Signal: no ads running, or ran ads and stopped

## Step-by-Step

### Step 1 — Scrape leads
```bash
python3 tools/scrape_gmaps.py --vertical landscaping --limit 20
```
Add `--cities "Austin TX,Charlotte NC"` to target specific markets.
Output: `.tmp/{vertical}_leads.json`

### Step 2 — Check ad pixels
```bash
python3 tools/check_fb_ads.py --input .tmp/landscaping_leads.json
```
Updates the leads file with `fb_ads_status`:
- `none` = no FB pixel, no Google Ads → hottest lead
- `fb_only` / `google_only` / `both` = running ads (different angle)
- `no_website` = lower priority

### Step 3 — Find emails
```bash
python3 tools/scrape_emails.py --input .tmp/landscaping_leads.json
```
Attempts to extract contact emails from each lead's website.
Updates leads in-place with `email` field.

### Step 4 — Generate Gmail drafts
```bash
python3 tools/generate_outreach_drafts.py --vertical landscaping
```
Creates personalized HTML drafts in Gmail for all leads that have an email.
Templates are personalized by vertical and `fb_ads_status`.

Add `--limit 10` to process a subset first. Add `--rebuild` to recreate all drafts.

### Step 5 — Review and send
Open Gmail drafts folder. Review each draft. Send manually or in batches.
Do not blast all at once — send 10–20/day per vertical to avoid spam flags.

### Step 6 — Log and follow up
Track in a Google Sheet: company name, vertical, city, date sent, response, status.
Follow up once after 4 days if no response. No third follow-up.

---

## Priority Order by Vertical (estimated ROI)

1. **Solar** — highest ticket ($15K–$40K installs), leads are expensive on platforms
2. **Dental** — recurring revenue (implants, Invisalign), $3K–$8K per case
3. **Plumbing** — emergency intent = high urgency, fast close cycle
4. **Landscaping** — recurring contracts = LTV play
5. **Chiropractic** — steady new patient flow, relatively easy to close
6. **Electrician / Painting / Pest Control** — solid but more commoditized

## Pricing to Share When Asked

| Plan    | Monthly Fee | Ad Spend (min) | Leads/Month     |
|---------|-------------|----------------|-----------------|
| Starter | $997        | $1,500         | 10–15 exclusive |
| Growth  | $1,497      | $2,500         | 20–30 exclusive |
| Scale   | $2,497      | $4,000         | 40–60 exclusive |

**Guarantee:** Month-to-month. 60-day guarantee — if we miss your target, we work free until we hit it.

## Files
- `tools/scrape_gmaps.py` — generic GMaps scraper for any vertical
- `tools/check_fb_ads.py` — pixel/ad checker (use `--input` flag for non-roofing files)
- `tools/scrape_emails.py` — email finder
- `tools/generate_outreach_drafts.py` — draft generator with per-vertical templates
- `.tmp/{vertical}_leads.json` — leads per vertical

## Edge Cases
- Companies with no website → skip or do Instagram/Facebook DM manually
- Dental/chiro: decision-maker is usually the owner or office manager; address them by first name if available
- Solar: avoid leads in states with poor net metering policy (check state before scaling)
- If GMaps scraper hits CAPTCHA: re-run with `--limit 10` per city and increase delays
