# Loyalty Status Match Monitor

## Objective
Weekly scan for status match and upgrade opportunities available from current loyalty statuses. Surface new offers before they expire.

## Current Statuses
| Program | Tier | Alliance Equivalent |
|---------|------|---------------------|
| Lufthansa Miles & More | Senator | Star Alliance Gold |
| SAS EuroBonus | Gold | Star Alliance Gold |

Star Alliance Gold unlocks a wide network of hotel, car rental, and airline matches.

## Trigger
Run weekly (Mondays recommended). Outputs a Gmail draft to dondevamosba@gmail.com.

## Tool
```bash
python3 tools/scrape_status_matches.py
```

Flags:
- `--force` — send draft even if no new offers since last run
- `--dry-run` — print HTML output without creating a draft

## How It Works
1. Compares `KNOWN_OFFERS` list in the tool against `.tmp/status_matches_seen.json` cache
2. Scrapes StatusMatcher.com for live community-reported offers for Lufthansa + SAS
3. If new offers exist (or `--force`), generates an HTML digest and creates a Gmail draft
4. Updates cache so already-seen offers aren't flagged again

## Adding New Offers
When you find a new match offer (via FlyerTalk, OMAAT, The Points Guy, etc.):
1. Add it to the `KNOWN_OFFERS` list in `tools/scrape_status_matches.py`
2. Use a unique `id` (kebab-case)
3. Set `expires` to the actual date (e.g. `"2025-12-31"`), `"ongoing"`, or `"periodic"`
4. Run `--force` to send an immediate draft

## Key Sources to Monitor
- StatusMatcher.com — best aggregator of community-reported matches
- FlyerTalk forums (Miles & More, EuroBonus boards)
- View from the Wing (VFTW) — blog that covers targeted/public match offers
- One Mile at a Time (OMAAT) — covers airline + hotel match promos
- The Points Guy — hotel and car rental match roundups

## Known Ongoing Matches (as of mid-2025)

### Hotels
| Program | Target Tier | Notes |
|---------|-------------|-------|
| Marriott Bonvoy | Gold Elite | Star Alliance Gold → Gold Elite (90 days, extendable with 4 stays) |
| Hilton Honors | Gold | Via Lufthansa Miles & More partnership |
| IHG One Rewards | Platinum Elite | Periodic — check statusmatch page |
| Radisson Rewards | Gold | Periodic |

### Car Rentals
| Program | Target Tier | Notes |
|---------|-------------|-------|
| Hertz Gold Plus Rewards | Five Star | Ongoing via Star Alliance Gold |
| Avis Preferred | Preferred Plus | Ongoing via Star Alliance Gold |
| Sixt | Platinum | Via Lufthansa Miles & More partnership |
| Budget Fastbreak | Business | Via Star Alliance Gold |

### Airlines
| Program | Target Tier | Notes |
|---------|-------------|-------|
| TAP Miles&Go | Gold | Periodic challenge offers |
| Aegean Miles+Bonus | Gold | Periodic match offers |

## Edge Cases
- Some matches are **targeted** (emailed to you directly) — no scraper will catch these. Keep an eye on your inbox.
- Marriott match link may 404 periodically — check marriott.com/loyalty/statusMatch.mi directly.
- Hertz Star Alliance page sometimes requires login to complete; the match can also be done via phone.

## Output Format
Gmail draft to dondevamosba@gmail.com with:
- New offers highlighted with a green banner
- Full table of all known offers grouped by category (Hotel / Car Rental / Airline)
- Direct apply links
- Live snippets from StatusMatcher.com if found

## Improvement Loop
After each run, update this doc with:
- Any new match offers discovered
- Offers that have expired
- StatusMatcher.com scraping quality (did it return useful results?)
- New sources worth monitoring
