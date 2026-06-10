# Storm Digital — Content Calendar & Auto-Post

## Objective
Maintain a Google Sheets content calendar for Storm Digital's Instagram and Facebook, auto-generate captions with Claude, and automatically post content when it's due.

Creative source: post designs live in `brand-toolkit/storm-posts/` (20 HTML templates, violet-midnight + electric-lime kit). Screenshot with `tools/screenshot_storm.py`, upload, and paste the public URL into the calendar.

---

## Architecture

```
Google Sheet (Storm — Content Calendar)
  ↑ fill_content_storm.py   ← generates captions with Claude
  ↓ auto_post_storm.py → post_instagram.py → Instagram / Facebook
```

---

## 1. Fill the Content Calendar

```bash
python3 tools/fill_content_storm.py             # generate sheet + captions
python3 tools/fill_content_storm.py --dry-run   # preview without writing
```

Creates the "Storm — Content Calendar" sheet and saves the ID to `.env` as `STORM_CONTENT_CALENDAR_SHEET_ID`. Same column layout as the Ola Digital calendar (see `workflows/ola-digital/content_calendar_autopost.md`): you fill **Media URL** (column H), leave Status as `pending`.

---

## 2. Auto-Post

```bash
python3 tools/auto_post_storm.py            # posts whatever is due now
python3 tools/auto_post_storm.py --dry-run  # preview
```

Posts every `pending` row with a Media URL whose datetime ≤ now, then marks it `posted` with the Post ID. Set Status to `skip` to ignore a row.

### Scheduling (already automated)
A local cron runs the auto-poster twice daily at 9:30 and 18:30 (AR time); output goes to `.tmp/cron_autopost.log`. Approved rows in the unified approval sheet are also published on the same schedule via `tools/publish_all_approved.py` (sheet ID comes from `UNIFIED_APPROVAL_SHEET_ID` in `.env`).

---

## Related undocumented tools

- `tools/generate_storm_images.py` — generate branded Storm images
- `tools/generate_storm_reels.py` — generate Storm reel concepts
- `tools/screenshot_storm.py` — screenshot the HTML post templates to PNG

---

## Edge Cases

- Media URL must be a public direct-access link (CDN or Drive direct-download)
- Instagram rate limit: 25 API posts per 24h per account
- Token health: run `python3 tools/check_token_health.py` (also runs Mondays via cron) — the system-user token doesn't expire on a timer but can be revoked
