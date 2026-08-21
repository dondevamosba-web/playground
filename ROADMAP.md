# IG Pipeline & Fiestas — Master Roadmap

**Status**: Full build mode. All 6 accounts automating end-to-end.  
**Timeline**: 4 weeks to full deployment  
**Owner**: Guido (with Claude)

---

## 🚀 Phase 1: Stabilize — ✅ DONE

✅ **Completed**:
- Stories auto-publish (every 60 min)
- Metrics script (fetch engagement)
- Cleanup vencidas (mark expired posts)
- Auto-schedule 5 accounts (every 60 min via Windows tasks)
- Feed + story auto-publishing for all 6 accounts
- 12 venue sources scraped

**This Week**:
- [ ] Run metrics once → see what's actually working
- [ ] Run cleanup → remove 580 dead posts from other 5 accounts
- [ ] Verify 5 new tasks are publishing (check logs tomorrow)
- [ ] Update memory with initial data

**Expected output**: 6 accounts auto-publishing, baseline metrics captured.

---

## 📊 Phase 2: Visibility & Predict — ✅ DONE

✅ **Completed**:
- Metrics Dashboard Auto (3 AM daily, refreshes HTML)
- Ticket Link Automation (auto-detect URLs in captions)
- Prediction Model (rank artistas by engagement)
- Cross-Account Dedup (don't republish same event)
- Integration to all publishers (feed + stories)

**Output**: Know what's working. Artistas ranked by stickiness. No duplicate events.

---

## 🔮 Phase 3: Premium Features — 🟡 IN PROGRESS

### 3.1 **Story Stickers** ✅ (Just finished)
- Countdown stickers (days until event)
- Poll stickers ("Vas a ir?")
- Swipe-up links (if 10K+ followers)
- Auto-apply when story publishes
- Windows task: manual trigger or auto via publish pipeline

### 3.2 **Retention Analysis** ✅ (Just finished)
- Track which artistas drive engagement
- Identify content that sticks vs. causes churn
- Daily report (4 AM)
- Ranks artistas by avg engagement
- Input for next quarter's curation

**This Week**: Test stickers, review retention data. Decide on Phase 4 direction.

---

## 💎 Phase 4: Revenue & Scale (Next Week) — TBD

### 4.1 **Monetization Model**
- Affiliate links (Ticketmaster → commission)
- Sponsored posts (Creamfields, Bombo, etc. pay for placement)
- Premium tier (email list: "Exclusive events before IG")
- **Decision needed**: Pure content vs. revenue play?

### 4.2 **Advanced Segmentation**
- Audience personas (by artist preference)
- A/B test caption styles (tease vs. info)
- Optimal posting times (per day/venue)

**Expected output**: Revenue stream + data-driven curation.

---

## 🔄 Phase 5: Scale (Ongoing)

### 5.1 **IG Pipeline Ecosystem**
- Integrate all 6 accounts into one unified command center
- Shared metrics, shared dedup, shared prediction
- One dashboard showing all 6 accounts' health

### 5.2 **Recruitment Content**
- Reuse IG pipeline for Talento USA recruitment
- Same automation, different domain (jobs instead of events)
- Apply prediction to hiring trends

### 5.3 **TikTok/YouTube Shorts Expansion**
- Auto-repurpose Fiestas content to TikTok
- Same scheduling, different API

---

## 📅 Weekly Checklist

### Every Monday
- [ ] Run metrics → review dashboard
- [ ] Check logs: all 6 accounts published?
- [ ] Update DECISIONS.md with any learnings

### Every Wednesday
- [ ] Review top 3 events → are they trending?
- [ ] Check prediction model: any false positives?

### Every Friday
- [ ] Analyze engagement trends (weekly summary)
- [ ] Plan next week's double-posts (high-ROI events)

---

## Estimated Effort

| Phase | Hours | When | Blocker? |
|-------|-------|------|----------|
| 1. Stabilize | 3 | Now | No |
| 2. Visibility | 10 | Week 2 | No |
| 3. Predict | 12 | Week 3 | Maybe (if Graph API changes) |
| 4. Premium | 14 | Week 4+ | No |
| 5. Scale | Ongoing | Parallel | No |

**Total**: ~40 hours (1 week full-time, 2-3 weeks part-time)

---

## What Success Looks Like

- ✅ All 6 accounts auto-publishing (no manual posts)
- ✅ Metrics show clear winners (which events convert?)
- ✅ Prediction model pre-queues trending events
- ✅ Engagement tracking per venue/artist
- ✅ Audience knows where to get tickets
- ✅ Zero expired posts in queue
- ✅ Logs + monitoring for 24/7 awareness

---

## Parallel Track: Job Search (Week 2-3)

While IG pipeline stabilizes, activate job search:
- [ ] Build recruiter list (5-10 active leads)
- [ ] One-page positioning doc
- [ ] Interview talking points (IG pipeline, Meta Ads audit, Aspire wins)
- [ ] Weekly calls with recruiters
- [ ] Data collection: market rates, roles, companies

**Why parallel**: IG pipeline runs autonomously; job search takes personal time.

---

## Notes

- **Graph API stability**: Scraping works now (business_discovery). If it breaks again, we pivot to web scraping.
- **Sheet limits**: Google Sheets can handle 10K rows. We're at ~3K. Safe.
- **Logs**: Keep .tmp/\*.log files for 30 days, then archive.
- **Decision**: Do we monetize Fiestas (sponsored posts) or keep it pure? **Pending Guido's call.**

---

## Quick Wins (Start Now)

1. **Metrics dashboard** (2 hours) → Know what works
2. **Cleanup vencidas** (30 min) → Stop publishing dead posts
3. **Verify tasks** (15 min) → Check logs tomorrow
4. **Prediction model sketch** (1 hour) → Plan the algorithm

**This week total**: ~4 hours → 80% of Phase 1 + Phase 2 kick-off

Ready?
