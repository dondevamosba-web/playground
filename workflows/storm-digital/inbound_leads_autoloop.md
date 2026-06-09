# Storm Digital — Inbound Leads Auto-Loop

## Objective

Automatically pull inbound lead form submissions from Netlify Forms, score them, and generate Gmail reply drafts — so no warm lead goes cold waiting for a manual response.

## Pipeline Overview

```
Netlify Forms API
      ↓
tools/import_netlify_leads.py     → .tmp/inbound_leads.json
      ↓
tools/score_inbound_leads.py      → adds score + tier to each lead
      ↓
tools/draft_inbound_leads.py      → creates Gmail drafts in dondevamosba@gmail.com
```

---

## Prerequisites

### 1. Add credentials to `.env`

```
NETLIFY_TOKEN=<your personal access token>
NETLIFY_SITE_ID=<your site's netlify ID>
```

**Getting NETLIFY_TOKEN:**
1. Go to https://app.netlify.com/user/applications
2. Under "Personal access tokens", click "New access token"
3. Give it a name (e.g. `storm-digital-autoloop`) and copy the token immediately
4. Paste it into `.env` as `NETLIFY_TOKEN`

**Getting NETLIFY_SITE_ID:**
1. Go to https://app.netlify.com and open the site
2. Go to Site configuration → General → Site details
3. Copy the "Site ID" (looks like `abc12345-...`)
4. Paste it into `.env` as `NETLIFY_SITE_ID`

### 2. Get Netlify Form IDs (optional — needed for `--form-id` flag)

1. Go to your Netlify site dashboard → Forms tab
2. Click on a form — the URL will contain the form ID: `https://app.netlify.com/sites/<site>/forms/<form_id>`
3. Copy the form ID for use with `--form-id` below

### 3. Name your forms for niche auto-detection

The import script detects niche from the form name. Include one of these keywords in the form name in your HTML:

| Keyword in form name | Detected niche |
|---------------------|----------------|
| `roofing`           | roofing        |
| `hvac`              | hvac           |
| `plumbing`          | plumbing       |
| `windows`           | windows        |
| `siding`            | siding         |

Example: `<form name="roofing-contact" ...>` → niche = `roofing`

---

## Running the Pipeline

### Step 1 — Import new submissions

```bash
# Pull all forms for the configured site
python3 tools/import_netlify_leads.py

# Or target a specific form
python3 tools/import_netlify_leads.py --form-id <form_id>

# Preview without writing files
python3 tools/import_netlify_leads.py --dry-run
```

**Output:** `.tmp/inbound_leads.json` (appended), `.tmp/imported_netlify_lead_ids.json` (dedup log)

### Step 2 — Score leads

```bash
python3 tools/score_inbound_leads.py

# View only top tier
python3 tools/score_inbound_leads.py --tier A

# Print top 10
python3 tools/score_inbound_leads.py --top 10
```

**Scoring breakdown (max 100 pts):**

| Signal          | Points | Notes                              |
|-----------------|--------|------------------------------------|
| has_email       | 30     | Required to reply                  |
| has_phone       | 20     | Faster follow-up channel           |
| has_website     | 15     | Digital-savvy prospect             |
| message_length  | 10     | >50 chars = thoughtful inquiry     |
| niche_match     | 25     | roofing or hvac = core niches      |

**Tiers:**
- **A (≥65):** Reply same day — high-intent lead with full contact info
- **B (40–64):** Good prospect, reply within 24h
- **C (<40):** Lower priority, monitor for now

**Output:** `.tmp/inbound_leads.json` updated with `score` and `tier` fields

### Step 3 — Create Gmail drafts

```bash
# Draft Tier A and B leads (default)
python3 tools/draft_inbound_leads.py

# Draft Tier A only
python3 tools/draft_inbound_leads.py --tier A

# Preview drafts without creating them
python3 tools/draft_inbound_leads.py --dry-run
```

**Output:** Gmail drafts in `dondevamosba@gmail.com`, `.tmp/inbound_drafted_ids.json` (dedup log)

### Full pipeline (one-liner)

```bash
python3 tools/import_netlify_leads.py && \
python3 tools/score_inbound_leads.py && \
python3 tools/draft_inbound_leads.py
```

---

## Intermediate Files

| File | Purpose |
|------|---------|
| `.tmp/inbound_leads.json` | All imported inbound leads with scores and tiers |
| `.tmp/imported_netlify_lead_ids.json` | Seen Netlify submission IDs (prevents re-import) |
| `.tmp/inbound_drafted_ids.json` | Lead IDs with existing drafts (prevents duplicate drafts) |

All files in `.tmp/` are regenerable — safe to delete and re-run if needed.

---

## Draft Template

Each draft is a warm reply (not cold outreach) that:
1. Thanks the lead for reaching out
2. Confirms the service they inquired about
3. Provides a 15-min booking link: https://cal.com/guido-carminatti-wvudqi/15min
4. Includes the Storm Digital email signature

Drafts go to `dondevamosba@gmail.com` (the account used for all Storm Digital outreach).

---

## Edge Cases

- **Form field names vary:** The import script tries common aliases (`phone`/`telephone`, `company`/`business`, etc.). If a form uses custom names, add them to the `map_submission()` function in `tools/import_netlify_leads.py`.
- **Unknown niche:** If no keyword matches, niche is set to `unknown` and gets 0 niche-match points. Still gets drafted if score is ≥40 from other signals.
- **No new submissions:** The pipeline exits cleanly at Step 1 with "No new leads found."
- **Draft already exists:** `inbound_drafted_ids.json` prevents duplicate drafts on re-runs.

---

## Automating with a Schedule

To run this pipeline daily, use the `/schedule` skill to create a cron job:

```
/schedule run the inbound leads pipeline daily at 9am
```

Or manually via cron:
```
0 9 * * * cd /path/to/playground && python3 tools/import_netlify_leads.py && python3 tools/score_inbound_leads.py && python3 tools/draft_inbound_leads.py
```
