# Fiestas — Decisions Log

Decisions made and why. Next session should read this before changing anything.

## Venue Sources: Added 7 on 27 Jul 2026

**Decision**: Add @rioelectronicmusic, @creamfieldsargentina, @brigadocrew, @elementsba, @mushroom_arg, @desertinme, @estamosfelices to VENUE_SOURCES.

**Why**: Mined from captions of existing scraped events; all 7 are verified business accounts with >20K followers and recent posts. Follower counts are real, not guesses. They mention each other constantly, so they'll feed the queue faster.

**Tradeoff**: Some are multi-genre (Rio Electronic posts some rock, Mushroom is Ezeiza-only). Acceptable because flyer filter catches false positives.

**How to apply**: If queue dries up, scan more venues. Start with accounts mentioned in top events' captions.

---

## Caption Standards: No "Vía @handle" on 27 Jul 2026

**Decision**: Strip all attribution lines. Only mention venue/artist if they're the subject.

**Why**: Guido said *"nunca pongas via y el handle de donde lo sacamos"*. Naming the source reads as a repost account, not the place to find out what's happening. Venue branding is already baked into the flyer artwork.

**Tradeoff**: No credit to the original poster. Acceptable because we're not claiming it's original; flyers are event promotion, not creative content.

**How to apply**: When writing captions: keep `@crobarclub @clubthebowba`; drop any line that says "Vía @bantalent" or "repost de @account".

---

## Spanish Grammar: Closing-only `?` on 27 Jul 2026

**Decision**: No opening `¿` in question captions. Swap for closing `?` only.

**Why**: Guido: *"perfecto pero no uses mas signo de pregunta al inicio de las preguntas solo al final asi lo hacemos en argentina"*. Argentine style, not RAE.

**Tradeoff**: Looks wrong to Spanish learners outside Argentina. That's fine — Guido's audience is Buenos Aires.

**How to apply**: Before approving any pending post: find `¿` at start of question, replace with nothing. Keep `?` at end.

---

## Publishing Schedule: Every 30 min via Windows Task on 27 Jul 2026

**Decision**: Windows Scheduled Task runs `publish_fiestas_next.py --only-flyers` every 30 minutes.

**Why**: Guido: *"publica cada 30 min todos estos de a1"*. One post at a time, pick soonest event date, no manual intervention.

**Tradeoff**: Fixed interval (can't adapt to engagement). Acceptable because queue is large (28+ posts) and cadence is steady.

**How to apply**: 
- To pause: `schtasks /change /tn "Fiestas publish next" /disable`
- To resume: `schtasks /change /tn "Fiestas publish next" /enable`
- To delete: `schtasks /delete /tn "Fiestas publish next" /f`

Log file: `.tmp/fiestas_publish.log`

---

## Image Mirroring: Google Drive CDN on 27 Jul 2026

**Decision**: Mirror all flyer images to Google Drive before approving. Use drive.google.com download links in the sheet.

**Why**: Venue IG CDN URLs expire. 11 original flyers went to Drive during approval on 27 Jul; links are now permanent.

**Tradeoff**: Adds 30–60 sec per image (upload + share). Acceptable trade for URLs that don't expire in 2 weeks.

**How to apply**: `repost_viral_reels.py` does this automatically. When queuing new venue flyers manually: fetch image → upload to Drive → copy download URL → paste into sheet.

---

## Venue Deduplication: Check Queue tab before queueing on ongoing

**Decision**: `scan_venues.py` dedupes against already-queued shortcodes. Same event never appears twice.

**Why**: Venues repost each other's flyers. Would flood the queue.

**Tradeoff**: None; this is detection, not suppression.

**How to apply**: After scanning, before approving: review `.tmp/candidates.json`. Verify none of the shortcodes are in the Queue tab already. (scan_venues already does this but manual review catches edge cases.)

---

## Encoding Fix: PYTHONIOENCODING=utf-8 on 27 Jul 2026

**Decision**: Windows batch wrapper (`publish_fiestas_next.cmd`) sets `PYTHONIOENCODING=utf-8` before Python runs.

**Why**: Windows console defaults to cp1252. Any accented character or em-dash in a caption crashes the print. This forces UTF-8.

**Tradeoff**: None. It's a Windows-only quirk.

**How to apply**: All publish scripts must run via `.cmd` wrapper, not directly. The wrapper is in the scheduled task.

---

## Scrapers Dead: 18 of 26 IG_VIRAL_SOURCES broken on 27 Jul 2026

**Decision**: Graph API business_discovery can't reach personal accounts. `IG_VIRAL_SOURCES` (Mixmag, Electronic Beats, etc.) return 429 or empty.

**Why**: Endpoint limitation, not a bug.

**Tradeoff**: Lost access to viral reels. Acceptable because venue accounts (VENUE_SOURCES) now provide all the content needed.

**How to apply**: Don't try to fix the viral path. If it's needed again, rebuild using business_discovery on creator accounts only. Mixmag/Electronic Beats are editorial, not local BA events anyway.

---

## No Story Auto-Posting: Manual choice

**Decision**: `publish_fiestas_next.py` publishes to feed only. No auto-story.

**Why**: Not requested. 28 posts × 30-min interval = 14 hours of stories would be noisy.

**How to apply**: If Guido wants stories: uncomment 2 lines in `publish_fiestas_next.py`, redeploy. Otherwise leave off.

---

## Other 5 Accounts: No scheduling yet

**Decision**: Only Fiestas has the 30-min task. Techno, Storm, Ola Digital, Ola Empleo, Talento USA use manual `run_fiestas()` or are dormant.

**Why**: No request to automate them. Their Mac cron tasks aren't running on this Windows PC.

**How to apply**: If Guido wants any of the 5 to auto-publish: create tasks the same way as Fiestas. Use `publish_one_each.py` instead (it cycles through all 6 accounts on a fixed schedule).

---

## Graph API v19.0: Fixed version

**Decision**: Locked to `v19.0` in `publish_fiestas_next.py` and `auto_fiestas_queue.py`.

**Why**: Stability. Older versions had stricter ratelimits.

**How to apply**: Don't upgrade unless Instagram team breaks v19.0. Check changelog before bumping.
