# HVAC Lead Gen Outreach — Workflow SOP

## Objective
Identify small US HVAC companies that are under-marketed, qualify them by ad history, and send personalized cold outreach offering Meta + Google Ads lead generation services.

## Target Profile
- 1–15 employees
- Google Maps reviews: <100 (proxy for "small")
- Annual revenue: estimated $400K–$4M
- Pain: inconsistent leads, slow season gaps, relying on referrals or Angi/HomeAdvisor
- Signal: no Meta ads, or ran ads and stopped (bad results)
- Best seasons to outreach: spring (before AC season) and fall (before heating season)

## Inputs Required
- List of US cities to target (default list in scrape_hvac_gmaps.py)
- Personalization data per lead: name, city, review count, website

## Step-by-Step

### Step 1 — Scrape leads
```bash
python3 tools/scrape_hvac_gmaps.py --cities "Austin TX,Charlotte NC,Raleigh NC" --limit 30
```
Output: `.tmp/hvac_leads.json`

Fields: name, city, address, phone, website, rating, review_count

Search terms rotated per city (defined in `SEARCH_QUERIES` in the script):
- `HVAC contractor`
- `AC repair company`
- `heating and cooling company`
- `air conditioning repair`

### Step 2 — Check ad history
```bash
python3 tools/check_fb_ads.py --input .tmp/hvac_leads.json --limit 50
```
Updates `hvac_leads.json` with `fb_ads_status`:
- `none` = no FB pixel, no Google Ads tag → hottest lead (Variant A DM)
- `fb_only` = FB pixel only → pitch Google Ads
- `google_only` = Google Ads tag only → pitch Facebook Ads
- `both` = both present → pitch better results / lower CPL
- `unknown` = website unreachable

Note: `check_fb_ads.py` detects tracking pixels on the website (more reliable than Ad Library). Always pass `--input .tmp/hvac_leads.json` explicitly — it defaults to `roofing_leads.json`.

### Step 2.5 — Score and rank leads
```bash
python3 tools/score_leads.py --niche hvac --tier A
```
Scores every lead 0–100 based on signals (ad status, review count, website presence, etc.) and writes `score` and `tier` fields back to `hvac_leads.json`. Output is sorted by score descending.

**Tiers:**
- **Tier A** (≥65 pts) — top priority: strong signals, likely to convert. Start here.
- **Tier B** (40–64 pts) — good leads worth contacting after Tier A is exhausted.
- **Tier C** (<40 pts) — weak signals (no website, very few reviews, etc.). Skip unless you have capacity.

Recommended threshold: Tier B and above (`--min-tier B` when generating drafts).

### Step 3 — Filter and prioritize
Use the tier output from Step 2.5 as your primary filter. Within each tier, leads are already sorted by score descending.

Secondary signals: prefer leads with a website and `none`/`fb_only` ad status. `none` > `inactive` > `active` still applies within the same tier.

Timing note: outreach before peak season converts better — HVAC owners are anxious about lead volume heading into summer (AC) or winter (heating).

### Step 3.5 — Scrape emails
```bash
python3 tools/scrape_emails.py --input .tmp/hvac_leads.json
```
Visits each lead's website and contact pages to extract email addresses. Updates `hvac_leads.json` with an `email` field. Defaults to `roofing_leads.json` — always pass `--input` explicitly.

### Step 3.6 — Generate Gmail drafts
```bash
python3 tools/generate_hvac_drafts.py --min-tier B         # recommended: Tier B and above
python3 tools/generate_hvac_drafts.py --min-tier B --limit 10   # test batch first
python3 tools/generate_hvac_drafts.py --min-tier B --rebuild    # delete and recreate all
```
Creates personalized HTML email drafts in Gmail for all leads that have an email address. Template is selected based on `fb_ads_status`. Use `--min-tier A` to restrict to top-priority leads only. Leads without a `tier` field (scoring not yet run) are included with a warning.

### Step 4 — Send cold DMs
Use the templates below. Pick the variant based on `fb_ads_status`.
Channels: Gmail drafts (generated above), Facebook Messenger DM, Instagram DM (if they have IG).

### Step 5 — Log and follow up
```bash
python3 tools/log_hvac_outreach.py
```
Syncs leads with emails into "Storm Digital — HVAC Outreach" Google Sheet.
Follow up once after 4 days if no response. Do not follow up a third time.

---

## Cold DM Templates

### Variant A — Never ran ads (most common, coldest lead)

> Hey [Name] 👋
>
> Found your HVAC company in [City] and noticed you don't have any ads running — most of your competitors are already using Meta and Google to lock up local AC and heating calls.
>
> We run paid ads exclusively for HVAC contractors. Last month we helped a company in [nearby city] go from 4 service calls/week to 22, on exclusive leads — no Angi, no lead-sharing.
>
> Would it make sense to hop on a 15-min call this week to see if there's a fit? No pitch, just want to understand what your slow season looks like.
>
> — [Your name]

---

### Variant B — Ran ads, now inactive (warm lead, show empathy)

> Hey [Name],
>
> Quick note — I saw you ran some Facebook ads a while back but stopped. That's the most common story I hear from HVAC owners: ran ads, got garbage leads, or the agency disappeared after month 2.
>
> We only work with HVAC companies (no roofers, plumbers, etc.) and we guarantee exclusive leads — the same job doesn't go to 5 other contractors in your area.
>
> If you're open to it, I'd love to show you what we did differently for a company in [state] that had the same experience. 15 minutes, no commitment.
>
> — [Your name]

---

### Variant C — Currently running ads (improvement pitch)

> Hey [Name],
>
> Noticed you're running some ads — good move. Most HVAC companies in your market aren't.
>
> Quick question: are your leads exclusive, or are they going to 3–5 other contractors at the same time?
>
> We run campaigns where every lead comes only to you. Higher close rate, less time chasing people who already booked someone else.
>
> Happy to do a free audit of what you're running now and show you exactly where leads are leaking. No strings attached.
>
> — [Your name]

---

## Pricing to Share When Asked

| Plan      | Monthly Fee | Ad Spend (min) | Leads/Month    |
|-----------|-------------|----------------|----------------|
| Starter   | $997        | $1,500         | 10–15 exclusive|
| Growth    | $1,497      | $2,500         | 20–30 exclusive|
| Scale     | $2,497      | $4,000         | 40–60 exclusive|

**Guarantee:** If we don't hit your lead target in 60 days, we work free until we do.
**Contract:** Month-to-month. Cancel anytime.

## Market Context (for closing conversations)

- Average HVAC service call: $150–$500; full system replacement: $5,000–$12,000
- Average CPL on Meta for HVAC: $60–$110
- Average CPL on Google (non-branded local): $90–$150
- Closing 1 replacement job from 15 leads at $7,000 = 7x ROI on $997/month fee alone
- Lead-sharing services (Angi, HomeAdvisor): $50–$150/lead, sold to multiple contractors simultaneously
- HVAC owners are highly seasonal — they feel urgency before summer (AC) and before winter (heating)

## Edge Cases & Notes

- Some companies on Google Maps have no website — lower priority (harder to close, less marketing awareness)
- Companies with 4.8+ stars and <30 reviews are ideal: quality work, small enough to want growth
- Avoid companies with review responses mentioning "franchise" or "authorized dealer network" — likely have corporate marketing
- Google Maps scraper may hit CAPTCHA — if it does, re-run with `--limit 10` per city and increase delays
- HVAC search terms are more generic than roofing; expect more noise (e.g., large chains showing up). The <100 review filter handles most of it but verify manually when in doubt
- Facebook Ad Library: short names like "A&B HVAC" may match unrelated ads — verify the page location before outreach
- `check_fb_ads.py` defaults to the roofing leads path — always pass `--input .tmp/hvac_leads.json` explicitly

## Files

- `tools/scrape_hvac_gmaps.py` — Google Maps scraper
- `tools/check_fb_ads.py` — Pixel/tag checker (shared with roofing; use `--input` to target HVAC)
- `tools/score_leads.py` — scores and ranks leads (adds `score` and `tier` fields; use `--niche hvac`)
- `tools/scrape_emails.py` — Email scraper (shared with roofing; use `--input` to target HVAC)
- `tools/generate_hvac_drafts.py` — Gmail draft generator for HVAC leads (supports `--min-tier`)
- `tools/log_hvac_outreach.py` — Google Sheets logger
- `.tmp/hvac_leads.json` — all leads with status
- `hvac-agency/index.html` — agency landing page to send prospects to
