# Ola Digital — Content Calendar & Auto-Post

## Objective
Maintain a Google Sheets content calendar for Ola Digital's Instagram and Facebook, auto-generate captions with Claude, and automatically post content when it's due. Also capture website leads and draft follow-up emails.

---

## Architecture

```
Google Sheet (Content Calendar)
  ↑ fill_content_calendar.py  ← generates captions with Claude
  ↓ auto_post_from_calendar.py → post_instagram.py → Instagram / Facebook

Website Form (Netlify)
  ↓ draft_ola_leads.py → Gmail draft (Guido reviews + sends)
```

---

## 1. Fill the Content Calendar

```bash
python3 tools/fill_content_calendar.py             # 4 weeks
python3 tools/fill_content_calendar.py --weeks 8   # 8 weeks
python3 tools/fill_content_calendar.py --dry-run   # preview without writing
```

Creates a Google Sheet called "Ola Digital — Content Calendar" and saves the ID to `.env` as `CONTENT_CALENDAR_SHEET_ID`.

### Sheet columns
| Col | Field | Who fills it |
|-----|-------|-------------|
| A | Date | Auto |
| B | Time (AR, UTC-3) | Auto |
| C | Day | Auto |
| D | Content Type | Auto |
| E | Post Type (reel/carousel/single) | Auto |
| F | Caption | Claude (auto-generated) |
| G | Hashtags | Auto |
| H | **Media URL** | **You** |
| I | Status (pending/posted/skip) | Auto |
| J | Post ID | Auto |

### Weekly posting schedule
| Day | Time | Format |
|-----|------|--------|
| Monday | 8:00 AM | Reel |
| Tuesday | 12:00 PM | Reel |
| Wednesday | 7:00 PM | Carousel |
| Thursday | 12:00 PM | Reel |
| Friday | 7:00 PM | Carousel |

5 posts/week. Times are Argentina time (UTC-3).

### Your workflow
1. Run `fill_content_calendar.py` → opens the sheet
2. For each row: upload your video/image to Google Drive (public link) or a CDN, paste the URL in **column H (Media URL)**
3. Edit captions if you want (column F)
4. Leave Status as "pending"

---

## 2. Auto-Post

```bash
python3 tools/auto_post_from_calendar.py            # posts whatever is due now
python3 tools/auto_post_from_calendar.py --dry-run  # preview
python3 tools/auto_post_from_calendar.py --force    # post all pending regardless of time
```

Reads every row where:
- Status == "pending"
- Media URL is set
- Post datetime ≤ now (Argentina time)

Posts via `post_instagram.py`, then marks the row as "posted" with the Post ID.

### To skip a post
Change Status to `skip` in the sheet. The auto-poster ignores it.

### Scheduling (automated)
Run `/schedule` to set this up as a cron that runs twice daily:
```
python3 tools/auto_post_from_calendar.py
```

---

## 3. Website Lead Form

The contact form on `website/index.html` submits to Netlify Forms (form name: `ola-digital-leads`).

Fields captured: nombre, email, negocio, telefono, servicio, mensaje.

### Draft follow-up emails

```bash
python3 tools/draft_ola_leads.py            # create Gmail drafts for new leads
python3 tools/draft_ola_leads.py --dry-run  # preview without creating drafts
```

Pulls new form submissions from Netlify, creates a Gmail draft TO each lead's email (short warm email in Spanish offering a free call). Guido reviews the draft in Gmail and hits Send.

Deduplicates against `.tmp/ola_leads_seen.json`.

Schedule this to run daily.

---

## Edge Cases

- **Media URL must be a public direct-access link** — Google Drive "anyone with link" won't work for videos; use Google Drive direct download URL or upload to a CDN
- **Instagram rate limit**: 25 API posts per 24h — don't over-fill the calendar
- **Reel processing**: the tool polls until the video container is ready (up to 2 minutes); if it times out, re-run
- **Netlify Forms**: requires the site to be deployed on Netlify; the form won't appear in the dashboard until at least one submission has been received
- **Token expiry**: `INSTAGRAM_ACCESS_TOKEN` expires every 60 days — refresh via the Graph API exchange endpoint before it expires
