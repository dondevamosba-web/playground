# Canva → Google Drive → Instagram Workflow

## Objective
Take designs exported from Canva, upload them to Google Drive as public files, and publish or schedule them to Instagram via the Graph API.

## Full Pipeline

```
Canva (design) → Export PNG/MP4 → .tmp/posts/ → upload_to_drive.py → post_instagram.py
```

---

## Step 1: Design in Canva

1. Open Canva and use or create a template matching the post type:
   - **Single image:** 1080×1080 px (square) or 1080×1350 px (portrait)
   - **Carousel slides:** 1080×1080 px each (up to 10 slides)
   - **Reel cover:** 1080×1920 px (vertical)

2. Use Ola Digital brand colors:
   - Primary: `#0EA5E9`
   - Accent: `#F97316`
   - Dark: `#0F172A`

3. Export:
   - For images: **Share → Download → PNG** (high quality)
   - For reels: **Share → Download → MP4**

4. Name files clearly:
   ```
   post_01_tip_25mayo.png
   post_02_bts_27mayo.mp4
   post_03_promo_slide1.png
   post_03_promo_slide2.png
   post_03_promo_slide3.png
   ```

5. Place all exported files in `.tmp/posts/`

---

## Step 2: Set Up Google Drive API (one-time)

1. Go to https://console.cloud.google.com
2. Create a project (or select existing)
3. Enable **Google Drive API**
4. Go to **APIs & Services → Credentials → Create Credentials → OAuth 2.0 Client ID**
5. Application type: **Desktop app**
6. Download the JSON → save as `credentials.json` in the project root
7. First run of `upload_to_drive.py` will open a browser for auth and save `token.json`

---

## Step 3: Upload to Google Drive

```bash
# Upload entire folder
python tools/upload_to_drive.py --folder .tmp/posts/ --output .tmp/drive_urls.json

# Upload specific files
python tools/upload_to_drive.py --files .tmp/posts/post_01.png .tmp/posts/post_02.png
```

Files land in **Google Drive → Ola Digital/Instagram Posts/** and are set to public (anyone with link can view).

Output `.tmp/drive_urls.json` looks like:
```json
[
  {"name": "post_01_tip_25mayo.png", "id": "abc123", "url": "https://drive.google.com/uc?export=download&id=abc123"},
  {"name": "post_02_bts_27mayo.mp4", "id": "def456", "url": "https://drive.google.com/uc?export=download&id=def456"}
]
```

---

## Step 4: Post to Instagram

Use the URLs from the previous step. Copy captions from `.tmp/ola_digital_content_calendar.md`.

```bash
# Single image — immediate
python tools/post_instagram.py \
  --type single \
  --image-url "https://drive.google.com/uc?export=download&id=abc123" \
  --caption "Tu caption aquí" \
  --hashtags MarketingDigital OlavarríaNegocios OlaDigital

# Single image — scheduled
python tools/post_instagram.py \
  --type single \
  --image-url "https://drive.google.com/uc?export=download&id=abc123" \
  --caption "Tu caption aquí" \
  --schedule "2026-05-25T13:00:00+00:00"

# Carousel (3 images)
python tools/post_instagram.py \
  --type carousel \
  --image-url "https://...id=slide1" "https://...id=slide2" "https://...id=slide3" \
  --caption "Tu caption aquí"

# Reel — scheduled
python tools/post_instagram.py \
  --type reel \
  --video-url "https://drive.google.com/uc?export=download&id=def456" \
  --caption "Tu caption aquí" \
  --schedule "2026-05-27T13:00:00+00:00"
```

---

## Scheduling Reference (UTC times for 10 AM Argentina)

Argentina (ART) is UTC-3. 10:00 AM ART = 13:00 UTC.

| Post | Date | Schedule string |
|------|------|----------------|
| Post 1 (TIP) | 25 mayo | `2026-05-25T13:00:00+00:00` |
| Post 2 (BTS) | 27 mayo | `2026-05-27T13:00:00+00:00` |
| Post 3 (PRO) | 29 mayo | `2026-05-29T13:00:00+00:00` |
| Post 4 (CASO) | 1 junio | `2026-06-01T13:00:00+00:00` |
| Post 5 (TIP) | 3 junio | `2026-06-03T13:00:00+00:00` |
| Post 6 (BTS) | 5 junio | `2026-06-05T13:00:00+00:00` |
| Post 7 (PRO) | 8 junio | `2026-06-08T13:00:00+00:00` |
| Post 8 (CASO) | 10 junio | `2026-06-10T13:00:00+00:00` |
| Post 9 (TIP) | 12 junio | `2026-06-12T13:00:00+00:00` |
| Post 10 (BTS) | 15 junio | `2026-06-15T13:00:00+00:00` |
| Post 11 (PRO) | 17 junio | `2026-06-17T13:00:00+00:00` |
| Post 12 (CASO) | 19 junio | `2026-06-19T13:00:00+00:00` |

---

## Edge Cases

- **Google Drive direct download links:** Instagram requires a direct file download URL. The `uc?export=download&id=` format works for images. For large videos, consider using a CDN (Cloudinary free tier) instead.
- **Video size limit:** Instagram Reels via API accept videos up to 1 GB and 15 minutes. Ideal: under 100 MB, 15–90 seconds.
- **Reel videos must be MP4** with H.264 codec and AAC audio.
- **Token expiry:** Long-lived Instagram tokens last 60 days. Schedule a reminder to refresh before the 12-week calendar ends.
