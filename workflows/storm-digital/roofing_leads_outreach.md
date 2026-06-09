# Roofing Lead Gen Outreach — Workflow SOP

## Objective
Identify small US roofing companies that are under-marketed, qualify them by ad history, and send personalized cold outreach offering Meta + Google Ads lead generation services.

## Target Profile
- 1–15 employees
- Google Maps reviews: <100 (proxy for "small")
- Annual revenue: estimated $300K–$3M
- Pain: inconsistent leads, relying on word of mouth or HomeAdvisor
- Signal: no Meta ads, or ran ads and stopped (bad results)

## Inputs Required
- List of US cities to target (default list in scrape_roofing_gmaps.py)
- Personalization data per lead: name, city, review count, website

## Step-by-Step

### Step 1 — Scrape leads
```bash
python3 tools/scrape_roofing_gmaps.py --cities "Austin TX,Charlotte NC,Raleigh NC" --limit 30
```
Output: `.tmp/roofing_leads.json`

Fields: name, city, address, phone, website, rating, review_count

### Step 2 — Check ad history
```bash
python3 tools/check_fb_ads.py --limit 50
```
Updates `roofing_leads.json` with `fb_ads_status`:
- `never` = never ran Meta ads → hottest lead
- `inactive` = ran ads, stopped → warm lead (bad experience, can be solved)
- `active` = currently running ads → cold (pitch improvement angle)

### Step 2.5 — Score and rank leads
```bash
python3 tools/score_leads.py --niche roofing --tier A
```
Scores every lead 0–100 based on signals (ad status, review count, website presence, etc.) and writes `score` and `tier` fields back to `roofing_leads.json`. Output is sorted by score descending.

**Tiers:**
- **Tier A** (≥65 pts) — top priority: strong signals, likely to convert. Start here.
- **Tier B** (40–64 pts) — good leads worth contacting after Tier A is exhausted.
- **Tier C** (<40 pts) — weak signals (no website, very few reviews, etc.). Skip unless you have capacity.

Recommended threshold: Tier B and above (`--min-tier B` when generating drafts).

### Step 3 — Filter and prioritize
Use the tier output from Step 2.5 as your primary filter. Within each tier, the leads are already sorted by score descending.

Secondary signals: prefer `never` leads with a website (some marketing investment but no paid ads yet). `never` > `inactive` > `active` still applies within the same tier.

### Step 4 — Send cold DMs
Use the templates below. Pick the variant based on `fb_ads_status`.
Channels: Facebook Messenger DM, Instagram DM (if they have IG), or cold email if website has contact form.

To generate Gmail drafts for Tier B and above:
```bash
python3 tools/generate_roofing_drafts.py --min-tier B
```

### Step 5 — Log and follow up
```bash
python3 tools/log_roofing_outreach.py
```
Syncs drafted leads to the Outreach Tracker → Roofing tab. Each row includes a **Variant** column (A/B/C mapped from fb_ads_status: never→A, inactive→B, active→C).

Update **Status** manually in the sheet as leads progress: Drafted → Sent → Replied → Call Booked → Closed | Lost | Ghosted.

Follow up once after 4 days if no response. Do not follow up a third time.

**Check reply rate by variant:**
```python
from tools.outreach_tracker import OutreachTracker
tracker = OutreachTracker()
print(tracker.reply_rate_by_variant("Roofing"))
# → {"A": {"sent": 12, "replied": 3, "rate": "25.0%"}, "B": {...}, ...}
```

---

## Email Templates

**Preferred format:** HTML email with pricing table and Storm Digital footer (see Lead Flow Angle below).
**Booking link:** https://cal.com/guido-carminatti-wvudqi/15min — always hyperlink the CTA text.

---

### Lead Flow Angle — Primary template (all variants)

HTML structure:
- Opening: personalized to company name + city, reference their current ad situation
- Body: results proof (Charlotte contractor, 3 → 18 leads/week, exclusive)
- CTA: "hop on a 15-min call" hyperlinked to https://cal.com/guido-carminatti-wvudqi/15min
- Pricing table (Starter $997 / Growth $1,497 / Scale $2,497)
- Guarantee line: "Month-to-month. 60-day guarantee — if we miss your target, we work free until we hit it."
- Storm Digital footer: dark background, orange accent, stormdigitalhq@gmail.com

**Variant A — Never ran ads (test version, updated 2026-05-26)**
> Hey [Name],
>
> [Company] came up when I was looking at roofing contractors in [City]. You've got solid reviews — the one thing missing is ads. A few of your competitors are already running Meta campaigns and locking up the same jobs you're bidding on.
>
> Last month we took a contractor in [nearby city] from 3 leads/week to 18 — all exclusive, no HomeAdvisor, no lead-sharing with 4 other roofers.
>
> 60-day guarantee: if we miss your lead target, we work free until we hit it.
>
> I have time Thursday or Friday — does either work for a quick 15 minutes? [Book here.](https://cal.com/guido-carminatti-wvudqi/15min)

**Variant B — Ran ads, now inactive**
> Hey [Name],
>
> Quick note — I saw you ran some Facebook ads but stopped. That's the most common story I hear from roofers: ran ads, got garbage leads, or the agency disappeared after month 2.
>
> We only work with roofing companies and guarantee exclusive leads — the same lead doesn't go to 5 other roofers in your area.
>
> If you're open to it, I'd love to show you what we did differently for a contractor in [state] that had the same experience. [15 minutes, no commitment.](https://cal.com/guido-carminatti-wvudqi/15min)

**Variant C — Currently running ads**
> Hey [Name],
>
> Noticed you're running some ads — good move. Most roofing companies in [City] aren't.
>
> Quick question: are your leads exclusive, or going to 3–5 other contractors at the same time?
>
> We run campaigns where every lead comes only to you. Happy to do a free audit of what you're running now. [Book a quick 15-min call here.](https://cal.com/guido-carminatti-wvudqi/15min)

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

- Average residential roof job: $8,000–$15,000
- Average CPL on Meta for roofing: $80–$120
- Average CPL on Google (non-branded): $124
- Closing 1 job from 15 leads at $10,000 = 10x ROI on $997/month fee alone
- Lead-sharing services (HomeAdvisor, Angi): $100–$250/lead, sold to 5 contractors simultaneously

## Edge Cases & Notes

- Some companies on Google Maps have no website — lower priority (harder to close, less marketing awareness)
- Companies with 4.8+ stars and <30 reviews are ideal: quality work, small enough to want growth
- Avoid companies with review responses that mention "franchise" or "national" — they likely have corporate marketing
- Google Maps scraper may hit CAPTCHA — if it does, re-run with `--limit 10` per city and increase delays
- Facebook Ad Library search is keyword-based; short/generic business names (e.g., "ABC Roofing") may return false positives from other regions — verify manually before outreach

## Files

- `tools/scrape_roofing_gmaps.py` — Google Maps scraper
- `tools/check_fb_ads.py` — Facebook Ad Library checker
- `tools/score_leads.py` — scores and ranks leads (adds `score` and `tier` fields)
- `tools/generate_roofing_drafts.py` — Gmail draft generator (supports `--min-tier`)
- `.tmp/roofing_leads.json` — all leads with status
- `roofing-agency/index.html` — agency landing page to send prospects to
