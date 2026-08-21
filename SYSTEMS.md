# Fiestas — Four Systems Setup

These four systems work together to keep Fiestas running without constant babysitting.

## 1. Seed Doc (SEED.md)

**What it is**: One file with all the project context. Read it once per session.

**When to use**: Start of every Claude session about Fiestas.

**Content**:
- What each script does
- Sheet structure & column meanings
- Venue sources (with follower counts)
- Caption standards
- Recent changes & known limits

**Why it matters**: When context compacts mid-session, the plan lives on disk. Next session reads SEED and picks up where you left off without re-explaining the whole project.

---

## 2. Decisions Log (DECISIONS.md)

**What it is**: Why each decision was made. When to change it, when to leave it alone.

**When to use**: Before you consider changing anything (adding sources, tweaking captions, etc.).

**Content**:
- Why 7 venues were added on 27 Jul
- Why "Vía @" is banned and what to do instead
- Why only closing `?`, not opening `¿`
- Why publish every 30 min
- Why images go to Google Drive
- Why viral scrapers don't work anymore
- Limitations and tradeoffs

**Why it matters**: Without this, next session re-litigates "should we use Mixmag posts?" It's already documented.

---

## 3. Stop Hook (.claude/hooks.json)

**What it is**: Claude Code runs a check at the end of every turn. If it fails, the turn doesn't end — you have to fix it.

**When to use**: Automatically. You don't call it; it runs after every message.

**What it checks** (`tools/check_captions.py`):
- No "Vía @handle" in pending captions
- No opening `¿` (only closing ?)
- Has hashtags
- Has image or VIDEO: note

**Exit codes**:
- 0 = all pending posts pass → session ends
- 2 = blocker found → session stuck until you fix it

**Why it matters**: You can't accidentally approve a post with "Vía @crobarclub" or an opening ¿. The gate doesn't read prose, it checks the sheet.

**How to run manually**:
```bash
python3 tools/check_captions.py --verbose
```

---

## 4. Monitor (tools/monitor_publish.py)

**What it is**: A background watcher that prints new log lines as they arrive.

**When to use**: Claude's Monitor tool (not a native command).

**What it does**:
- Watches `.tmp/fiestas_publish.log`
- Every 30 sec, prints any new lines
- Marks ✅ for success, ❌ for errors, 📝 for info

**Why it matters**: Real-time awareness of what published without polling or checking the file manually. Each line becomes a Claude notification.

**Usage** (in a Claude session, if you want live awareness):
```
I'll start a monitor to track what's publishing.
```

Then call Monitor with:
```
python3 tools/monitor_publish.py
```

---

## Quick Start for Next Session

1. **Read SEED.md** (2 min) — know what the scripts do
2. **Glance DECISIONS.md** (30 sec) — remember why things are the way they are
3. **Check hook status** — if you edit captions, the stop hook validates them automatically
4. **(Optional) Start Monitor** — if you want real-time publish notifications

That's it. The rest is automated.

---

## When to Update These Files

- **SEED.md**: After you add new scripts, change sheet structure, or realize the docs are wrong
- **DECISIONS.md**: Every time you make a non-trivial choice (add sources, change caption rule, etc.)
- **Stop hook**: If new standards appear (e.g., "all captions must mention the artista")
- **Monitor**: If the log format changes or you want different alerts

---

## Example: Adding a New Venue Source

1. Decide it's a good fit
2. Edit VENUE_SOURCES in `tools/scan_venues.py`
3. **Add entry to DECISIONS.md** — why this venue, when, what it adds
4. Next time someone asks "why are we scraping @xyz?", it's documented

Example decision entry:

```markdown
## Venue Source: Added @futuroclubba on 2026-08-05

**Decision**: Add @futuroclubba to VENUE_SOURCES.

**Why**: Mentioned in 3 recent posts from @bantalent. 25K followers, posts weekly, good signal-to-noise.

**Tradeoff**: Mostly rock (10%), will need flyer filter. Acceptable.

**How to apply**: If queue dries up, scan who gets mentioned most in top events.
```

---

## Troubleshooting

**"Stop hook won't let me end the session"**
- Run `python3 tools/check_captions.py --verbose` to see what's blocked
- Fix the captions in the sheet
- Hook will pass on next turn

**"I added a venue but nothing new is in the queue"**
- Run `python3 tools/scan_venues.py --handles @newvenue` to test
- Review `.tmp/candidates.json` — are the shortcodes already in the Queue tab?
- If all shortcodes match existing posts, deduplication is working

**"Monitor isn't showing new publishes"**
- Is the scheduled task running? Check `schtasks /query /tn "Fiestas publish next"`
- Is the log file being written? Check `.tmp/fiestas_publish.log` timestamp
- Is Monitor actually running? (It should say "Monitoring Fiestas publish log...")

---

## Files to Keep in Sync

After every major session, update:

1. **SEED.md** — if scripts changed or you added/removed sources
2. **DECISIONS.md** — if you made a choice that future-you should know about
3. **.claude/hooks.json** — if new standards require new checks
4. **tools/check_captions.py** — if the hook needs new rules

Don't update these:
- Individual script files (they change often; the doc doesn't)
- Google Sheet (it's live data, not a doc)
- .tmp/ files (they're temporary)
