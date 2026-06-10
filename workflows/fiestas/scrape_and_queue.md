# Workflow: Scrape Events & Queue for Approval

**Account:** Fiestas (electronic parties Argentina)
**Trigger:** Runs daily at 9:00 AM (AR) via local cron (`.tmp/cron_fiestas_queue.log`); can also be run manually anytime.
**Output:** New rows added to the Google Sheet with Status=pending. You review and change to "approved".

---

## Required Inputs

- `.env` keys set: `FIRECRAWL_API_KEY`, `FIESTAS_APPROVAL_SHEET_ID` (auto-created on first run)
- Optional: `FIESTAS_IG_SOURCE_ACCOUNTS=@handle1,@handle2` for IG account monitoring

---

## Steps

### 1. Run the queue orchestrator

```bash
python3 tools/queue_event_posts.py
```

Options:
- `--city buenos-aires` — filter RA by city (default: all Argentina)
- `--skip-ig` — RA only, no IG scraping
- `--ig-only` — IG accounts only, skip RA
- `--dry-run` — preview without writing to sheet

### 2. Review the sheet

Open the link printed by the script:
```
https://docs.google.com/spreadsheets/d/<FIESTAS_APPROVAL_SHEET_ID>/edit
```

Review columns:
- **Event Name** — confirm it's the right event
- **Feed Caption** — edit if needed (Claude draft, your voice on top)
- **Story Caption** — edit the short text
- **Image URL** — paste a better image if the RA flyer URL doesn't load
- **Status** — change from `pending` → `approved` when ready to post

### 3. Publish approved posts

```bash
python3 tools/publish_approved_events.py
```

---

## What Gets Scraped

| Source | What | Tool |
|--------|------|------|
| Resident Advisor `/events/ar` | Upcoming electronic events in Argentina | `scrape_ra_events.py` |
| IG accounts in `.env` | Recent posts flagged as events | `scrape_ig_posts.py` |

---

## Duplicate Prevention

`queue_event_posts.py` checks existing sheet rows before adding new ones.
It skips any event where (Event Name + Event Date) already exists in the sheet.

---

## Troubleshooting

**No events scraped from RA:**
- Check Firecrawl credits (`FIRECRAWL_API_KEY`)
- RA may have changed their HTML structure — inspect the page and update the extraction schema in `scrape_ra_events.py`

**IG posts empty:**
- Instagram is JS-heavy and blocks scrapers. Try adding `--actions wait:5000` or use the Firecrawl docs for JS rendering hints.
- If the account is private or requires login, it cannot be scraped automatically.

**Sheet not found:**
- `FIESTAS_APPROVAL_SHEET_ID` in `.env` may be wrong. Clear it and run again to recreate.

---

## Related Tools (unified approval sheet)

These work against the multi-account approval sheet (`UNIFIED_APPROVAL_SHEET_ID` in `.env`, tabs: Ola Digital / Storm / Fiestas / Techno):

- `tools/create_unified_approval_sheet.py` — create the unified sheet (one-time setup)
- `tools/seed_approval_sheet.py` — seed it with draft rows
- `tools/seed_fiestas_upcoming.py` — seed upcoming RA events into the Fiestas tab
- `tools/fetch_next_posts.py` — list the next scheduled/approved posts
- `tools/publish_all_approved.py` — publish every approved row across all 4 tabs (runs 2x daily via cron)
- `tools/generate_fiestas_news_image.py` — branded news image generator (macOS-only font paths; photo URL passed per event)
