# Workflow: Publish Approved Posts

**Account:** Fiestas (electronic parties Argentina)
**Trigger:** After reviewing the sheet and marking rows as "approved".
**Output:** Feed post + story published to Instagram. Sheet updated with Post ID.

---

## Required Inputs

- `FIESTAS_APPROVAL_SHEET_ID` set in `.env`
- `FIESTAS_INSTAGRAM_BUSINESS_ACCOUNT_ID=17841402123088874` (already set)
- `FIESTAS_FACEBOOK_PAGE_ID=282931238497562` (already set)
- `INSTAGRAM_ACCESS_TOKEN` — the shared system user token. If this account isn't covered, generate a new one in Meta Business Suite and update the token.

---

## Steps

### 1. Mark posts as approved in the sheet

In the Google Sheet, change Status from `pending` → `approved` for rows you want to publish.

Optionally edit:
- **Feed Caption** before publishing
- **Story Caption**
- **Image URL** — swap in a better image (must be a public URL, e.g. Google Drive shared link)

### 2. Publish

```bash
python3 tools/publish_approved_events.py
```

Options:
- `--dry-run` — shows what would post without actually posting
- `--feed-only` — skip stories
- `--story-only` — skip feed posts

### 3. Confirm

The script prints the Instagram permalink and updates the sheet:
- Status → `posted`
- Post ID → the IG media ID (for reference)

---

## Image Requirements

Instagram Graph API requires images to be hosted at a **public URL** (no auth).

Good sources:
- Google Drive: share file → "Anyone with the link" → use the direct download URL
  Format: `https://drive.google.com/uc?export=download&id=FILE_ID`
- Cloudinary / S3 / CDN public buckets
- RA event flyer URLs (direct from ra.co CDN)

If the image URL returns a 403 or redirects to a login page, the post will fail.

---

## Token Expiry

The `INSTAGRAM_ACCESS_TOKEN` is a long-lived token (~60 days). If posting starts failing with auth errors:
1. Go to Meta Business Suite → Settings → System Users
2. Generate a new token with `instagram_basic`, `instagram_content_publish`, `pages_read_engagement` permissions
3. Update `.env`

---

## Troubleshooting

**"Media container error"**: Image URL is not publicly accessible. Swap it for a CDN or Drive link.

**"Invalid access token"**: Token expired. Regenerate via Meta Business Suite.

**Story posts silently fail**: Stories don't support text captions via API (the caption field is metadata only, not overlaid on the image). If you want text on the story image, add it to the image itself before posting.
