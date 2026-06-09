# Instagram Post Workflow

## Objective
Publish or schedule content (single image, carousel, or reel) to an Instagram Business account via the Instagram Graph API.

## Prerequisites

### One-time Setup: Get API Credentials

1. **Create a Facebook App**
   - Go to https://developers.facebook.com/apps
   - Click "Create App" → choose "Business" type
   - Add product: **Instagram Graph API**

2. **Connect your Instagram Business Account**
   - Your Instagram account must be a **Business or Creator** account
   - Connect it to a **Facebook Page** (Instagram Settings → Linked Accounts)

3. **Get a long-lived access token**
   - In the Graph API Explorer (https://developers.facebook.com/tools/explorer/):
     - Select your App
     - Generate a User Token with permissions: `instagram_basic`, `instagram_content_publish`, `pages_read_engagement`
   - Exchange for a long-lived token (valid 60 days):
     ```
     GET https://graph.facebook.com/oauth/access_token
       ?grant_type=fb_exchange_token
       &client_id={app-id}
       &client_secret={app-secret}
       &fb_exchange_token={short-lived-token}
     ```

4. **Find your Instagram Business Account ID**
   ```
   GET https://graph.facebook.com/me/accounts?access_token={token}
   ```
   Then:
   ```
   GET https://graph.facebook.com/{page-id}?fields=instagram_business_account&access_token={token}
   ```

5. **Store credentials in `.env`**
   ```
   INSTAGRAM_ACCESS_TOKEN=your_long_lived_token
   INSTAGRAM_BUSINESS_ACCOUNT_ID=your_ig_business_account_id
   ```

---

## Tool
`tools/post_instagram.py`

---

## Inputs

| Parameter        | Required | Description |
|-----------------|----------|-------------|
| `--type`        | Yes      | `single`, `carousel`, or `reel` |
| `--caption`     | Yes      | Post caption (include hashtags here or use `--hashtags`) |
| `--image-url`   | Depends  | Publicly accessible URL(s) for single/carousel images |
| `--video-url`   | Depends  | Publicly accessible URL for reel video |
| `--hashtags`    | No       | Appended to caption automatically |
| `--schedule`    | No       | ISO 8601 datetime (e.g. `2026-05-21T15:00:00+00:00`) — min 10 min, max 75 days ahead |
| `--dry-run`     | No       | Preview payload without posting |

---

## Process

### Single Image Post
1. Create media container:
   `POST /{ig-user-id}/media` with `image_url`, `caption`, `media_type=IMAGE`
2. Publish (or schedule):
   `POST /{ig-user-id}/media_publish` with `creation_id`

### Carousel Post
1. Create one container per image:
   `POST /{ig-user-id}/media` with `image_url`, `is_carousel_item=true`
2. Create carousel container:
   `POST /{ig-user-id}/media` with `media_type=CAROUSEL`, `children=[id1,id2,...]`, `caption`
3. Publish carousel container

### Reel Post
1. Create reel container:
   `POST /{ig-user-id}/media` with `video_url`, `media_type=REELS`, `caption`, `share_to_feed=true`
2. Poll container status until `status_code=FINISHED`:
   `GET /{container-id}?fields=status_code`
3. Publish reel container

---

## Edge Cases & Known Constraints

- **Image URLs must be publicly accessible** — local files won't work. Upload to a CDN or Google Drive (with public sharing) first.
- **Video URLs must be accessible** — same constraint. Direct download links required for Reels.
- **Rate limit:** Instagram allows 25 API-created posts per 24 hours per account.
- **Reel processing time:** Video containers take time to process. The tool polls every 5 seconds up to 2 minutes before timing out.
- **Token expiry:** Long-lived tokens last 60 days. Refresh before expiry by calling the exchange endpoint again with the current long-lived token.
- **Scheduling window:** Minimum 10 minutes ahead, maximum 75 days ahead. Time must be in UTC.
- **Caption limit:** 2,200 characters max. Hashtags count toward this limit.

---

## Outputs
- On success: prints the published media ID and permalink
- On dry-run: prints the API payload that would be sent

---

## Content Strategy for Ola Digital
- Single images: brand announcements, quotes, single product shots
- Carousels: tutorials, feature walkthroughs, before/after comparisons (3–10 slides)
- Reels: short demos, behind-the-scenes, trend-based content
