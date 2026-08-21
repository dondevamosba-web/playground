# Fiestas Electronicas Buenos Aires — Setup & Architecture

**Date**: 2026-07-27  
**Status**: Active — auto-publishes every 30 minutes  
**Feed**: [@fiestaselectronicasbuenosaires](https://www.instagram.com/fiestaselectronicasbuenosaires/) (Business Account)

## Core Scripts

| Script | Purpose | Trigger | Output |
|--------|---------|---------|--------|
| `scan_venues.py` | Mine new events from 12 venue accounts | Manual (ad-hoc) | `.tmp/candidates.json` |
| `auto_fiestas_queue.py` | Scrape viral reels from 8 IG news sources | Not used (deprecated endpoint 429) | `.tmp/viral_reels.json` |
| `repost_viral_reels.py` | Download, caption & queue viral reels | Manual | Google Drive + Sheet |
| `publish_fiestas_next.py` | Publish one approved post | Windows Task every 30min | Feed + `.tmp/fiestas_publish.log` |
| `build_queue_dashboard.py` | Preview all 6 accounts' pending posts | Manual | `.tmp/*_review.html` |

## Sheet Structure

**File**: Google Sheet `Fiestas Approval Queue`  
**Tab**: `Queue` (publishing venue flyers) + `Hoja 1` (other 5 accounts)

Columns (A–N):
- A: Date added
- B: Source (e.g., "IG @crobarclub (flyer)")
- C: Event name
- D: Event date (YYYY-MM-DD)
- E: Location
- F: Venue
- G: Notes / alt captions
- H: Primary text (feed caption)
- I: Story caption
- J: Image URL (Google Drive)
- K: IG post link
- L: Status (`pending` → `approved` → `posted`)
- M: Media ID (assigned on publish)
- N: Errors / notes

## Venue Sources (12 accounts)

Active right now:
1. @bantalent (159K) — early scans, high signal
2. @mandarineparkoficial — venue
3. @crobarclub — venue (Club AMK events)
4. @clubthebowba — venue
5. @pmopenair — open air events
6. **@rioelectronicmusic** (160K) — NEW 27 Jul
7. **@creamfieldsargentina** (112K) — NEW 27 Jul
8. **@brigadocrew** (75K) — NEW 27 Jul
9. **@elementsba** (50K) — NEW 27 Jul
10. **@mushroom_arg** (31K) — NEW 27 Jul
11. **@desertinme** (29K) — NEW 27 Jul (most active)
12. **@estamosfelices** (22K) — NEW 27 Jul

**Missing** (can't resolve via Graph API business_discovery):
- Club AMK, Under Club, Palacio Alsina, Morocco (personal accounts?)

## Caption Standards

- **No opening ¿** — Only closing `?` in Spanish
- **No "Vía @handle"** — No attribution lines. Venue/artist tags are the subject, not credits
- **Always hashtag** — #FiestasElectronicas #BuenosAires #MusicaElectronica #Underground
- **Mention the venue** — @crobarclub, @clubthebowba still belong in copy

## Publishing Schedule

- **Frequency**: Every 30 minutes
- **Source**: Windows Scheduled Task "Fiestas publish next" → `publish_fiestas_next.cmd`
- **Logic**: Pick soonest event date (not sheet order)
- **Status**: One press `schtasks /delete /tn "Fiestas publish next" /f` to disable

## Recent Changes

- **27 Jul 2026**: Added 7 new venue sources (Rio Electronic, Creamfields, Brigado, Elements, Mushroom, Desertinme, Estamos Felices)
- **27 Jul 2026**: Fixed encoding crash (PYTHONIOENCODING=utf-8 in wrapper)
- **27 Jul 2026**: Cleaned 26 captions: removed "Vía @", fixed opening `¿` to closing only
- **27 Jul 2026**: Mirrored 11 flyer images to Google Drive (CDN URLs expire)

## Known Limitations

- Graph API business_discovery only reaches business/creator accounts (8 of 26 original sources dead)
- Video view counts not exposed; ranked by likes+comments instead
- No story auto-posting (currently)
- Manual caption writing (no API auth for claude_call.py on Windows)
