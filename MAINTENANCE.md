# IG Pipeline — Maintenance Checklist

**Mode**: Autopilot with weekly reviews. 10 systems run without you.

---

## Weekly (5 min)

**Every Monday 9 AM**:
```bash
# Check logs from last week
tail -50 .tmp/fiestas_publish.log
tail -50 .tmp/retention.log
tail -50 .tmp/metrics_auto.log
```

- ✓ All 7 accounts published?
- ✓ Any errors in logs?
- ✓ Story stickers applied?

**What to look for**:
- ERROR lines = action needed
- OK lines = working
- "duplicate found" = dedup working (expected)

---

## Monthly (20 min)

**First Tuesday of month, 10 AM**:

1. **Open dashboard**:
   ```bash
   # Metrics
   open .tmp/metrics_dashboard.html
   
   # Revenue
   python3 tools/monetize_pipeline.py --revenue-report
   
   # Retention
   cat .tmp/retention_analysis.json | jq '.artists[0:5]'
   ```

2. **Review data**:
   - Top 3 artistas (retention)
   - Top 3 venues (engagement)
   - Total revenue potential
   - Follower growth (check Fiestas @count)

3. **Decisions**:
   - Which artistas to pre-queue next?
   - Which sponsors to reach out to?
   - Any broken tasks?

---

## If Something Breaks

**Task didn't publish** (check logs):
```bash
# Most recent error?
grep "ERROR" .tmp/fiestas_publish.log | tail -1

# Is it a credential issue?
grep "ERROR" .tmp/fiestas_publish.log | grep -i "access"

# If yes → token expired, need refresh
```

**Story stickers didn't apply**:
```bash
tail .tmp/story_stickers.log
```

**Tasks stopped running**:
```bash
# Check Windows Task Scheduler
schtasks /query /tn "IG*" | grep "Ready\|Disabled"

# If Disabled → enable it
schtasks /change /tn "Fiestas publish next" /enable
```

---

## Escalation Path

| Issue | Fix |
|-------|-----|
| Account token expired | Refresh via Facebook/Meta Business Suite |
| No posts published in 24h | Check credentials + network |
| Logs full of errors | Run with --dry-run to debug |
| Random skips (duplicates) | Dedup working (expected) |

---

## Health Metrics

Check weekly:
- **Posts published**: should grow by 7-8/week (1 per account)
- **Engagement avg**: track in metrics_dashboard.html
- **Revenue logged**: should see clicks in revenue.log
- **No errors**: if >3 errors/week, investigate

---

## Disable/Pause (if needed)

To pause Fiestas feed publishing:
```bash
schtasks /change /tn "Fiestas publish next" /disable
```

To pause all 6 accounts:
```bash
for acct in fiestas techno storm ola_digital ola_empleo talento_usa; do
  schtasks /change /tn "IG_publish_$acct" /disable
done
```

To disable completely:
```bash
schtasks /delete /tn "IG*" /f
```

---

## When to Involve Claude

- Task won't publish (error diagnosis)
- Metrics dropped suddenly (investigate)
- New venue to add (scan + integrate)
- Automation broken (debug + fix)

Say: *"Check logs, why is X failing?"*

---

## Success Looks Like

✅ Posts going out on schedule (check logs)  
✅ Metrics show engagement trends (retention data)  
✅ Revenue opportunities logged (monetization pipeline)  
✅ Zero manual interventions needed  
✅ Email list growing (if email activated)  
✅ Sponsors asking to be featured (if pitching)
