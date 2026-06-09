# Content Repurposing Pipeline — Workflow SOP

## Objective
Take a single source video (reel, recording, or long-form clip) and repurpose it
into multiple platform-ready formats with auto-captions, resized outputs, and
caption copy for each platform.

## Step-by-Step

### Step 1 — Generate or receive source video
Source video comes from:
- `tools/generate_reels_v2.py` (programmatic reels)
- A recorded talking-head or screen-capture video
- A downloaded video from another platform

### Step 2 — Repurpose for all platforms
```bash
python3 tools/repurpose_video.py \
  --input .tmp/reels/reel_01.mp4 \
  --platforms reels feed youtube \
  --hashtags marketing
```

Outputs to `.tmp/repurposed/reel_01/`:
- `reel_01_instagram_reels.mp4` — 1080×1920, burned-in captions
- `reel_01_instagram_feed.mp4` — 1080×1080 cropped
- `reel_01_youtube.mp4` — 1920×1080 horizontal
- `reel_01.srt` — subtitle file
- `caption_reels.txt` — caption copy for Instagram Reels
- `caption_feed.txt` — caption copy for Feed post
- `caption_youtube.txt` — caption copy for YouTube

### Step 3 — Review and edit captions
Open `.tmp/repurposed/reel_01/caption_reels.txt`, review the auto-generated caption,
edit if needed, then use it when posting.

### Step 4 — Schedule the week
```bash
python3 tools/schedule_posts.py --plan --draft
```
Prints the optimal posting schedule for the week and creates a Gmail draft
with the full plan.

To assign specific videos to the schedule:
```bash
python3 tools/schedule_posts.py --plan --draft \
  --content reel_01.mp4 reel_02.mp4 reel_03.mp4
```

### Step 5 — Post (manual upload or via API)
**Via API (if video is hosted on a public URL):**
```bash
python3 tools/post_instagram.py \
  --type reel \
  --video-url "https://..." \
  --caption "$(cat .tmp/repurposed/reel_01/caption_reels.txt)"
```

**Scheduled post:**
```bash
python3 tools/post_instagram.py \
  --type reel \
  --video-url "https://..." \
  --caption "$(cat caption_reels.txt)" \
  --schedule 2026-05-26T15:00:00+00:00
```

**Manual**: Download the resized files and upload directly in the app.
Burn-in captions are already embedded in the video.

## Platform Formats
| Platform         | Dimensions | Use case                        |
|------------------|------------|---------------------------------|
| Instagram Reels  | 1080×1920  | Main distribution, TikTok too   |
| Instagram Feed   | 1080×1080  | Static grid posts               |
| YouTube / Shorts | 1080×1920  | YouTube Shorts channel          |
| YouTube Video    | 1920×1080  | Long-form repurpose (landscape) |

## Caption-Only Mode
If you just want the caption without reprocessing the video:
```bash
python3 tools/repurpose_video.py --input video.mp4 --caption-only
```

## No-Burn-In Mode
If you prefer to add captions in the app (Instagram's built-in captions):
```bash
python3 tools/repurpose_video.py --input video.mp4 --no-captions
```

## Best Posting Times (EST) — Ola Digital
| Day       | Slots                  |
|-----------|------------------------|
| Monday    | 9:00 AM, 6:00 PM       |
| Tuesday   | 8:00 AM, 5:00 PM       |
| Wednesday | 11:00 AM, 7:00 PM      |
| Thursday  | 9:00 AM, 6:00 PM       |
| Friday    | 10:00 AM               |
| Saturday  | 10:00 AM               |
| Sunday    | (skip — low engagement)|

## Hashtag Sets
- `marketing` — English, paid ads / digital marketing focus
- `agency` — Spanish, Argentina agency / entrepreneur audience
- `general` — broad English mix

## Files
- `tools/repurpose_video.py` — resize + caption + copy generator
- `tools/schedule_posts.py` — weekly posting schedule + Gmail draft
- `tools/post_instagram.py` — Meta Graph API poster with scheduling
- `.tmp/repurposed/` — all repurposed outputs organized by video
- `.tmp/schedule_*.json` — weekly schedule files

## Edge Cases
- **No audio / silent video**: Whisper returns empty — add captions manually
- **Long video (>3 min)**: API upload may time out; use Meta's resumable upload or upload manually
- **Aspect ratio extremes**: Very wide or very tall source videos may crop aggressively —
  check outputs before posting
- **API video posting**: Instagram requires the video to be hosted on a public HTTPS URL.
  Upload to Google Drive (make public) or use a CDN, then pass the URL.
