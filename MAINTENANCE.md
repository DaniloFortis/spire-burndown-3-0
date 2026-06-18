# Maintenance Guide - Spire 3.0.0 Bug Burndown Dashboard

Day-to-day operations and upkeep for the dashboard maintainer.

---

## Daily Operations

### Automated Updates (No Action Required)

The dashboard **automatically updates 3 times daily** on weekdays:
- 7:00 AM PT
- 12:00 PM PT
- 4:00 PM PT

**What happens automatically**:
1. GitHub Actions runs `update_today_burndown.py`
2. Counts current active 3.0.0 bugs
3. Updates projections
4. Regenerates dashboard + Slack content
5. Commits and pushes to GitHub
6. GitHub Pages deploys (~1-2 min)

✅ **You don't need to do anything daily!**

### Monitoring Automation

**Check automation status** (weekly):

1. Visit: https://github.com/DaniloFortis/spire-burndown-3-0/actions
2. Verify recent runs are ✅ green
3. If any are ❌ red, click to see error logs

**Or ask Claude**:
> "Show me the status of automated dashboard updates"

---

## Weekly Tasks

### 1. Verify Dashboard Accuracy (Monday mornings)

**Compare dashboard to ClickUp**:
1. Open: https://DaniloFortis.github.io/spire-burndown-3-0/
2. Note "Active Bugs" count
3. In ClickUp, filter: `milestone:"3.0.0"` AND `status != "Closed"` AND `status != "WON'T FIX"`
4. Counts should match (±1-2 for bugs created/closed since last update)

**If counts don't match**:
- Wait for next automated update (runs 3x daily)
- Or manually refresh: `python update_today_burndown.py`
- Or ask Claude: "The bug counts don't match ClickUp, help me debug"

### 2. Review Projection Trends

Check if the team is on track:

**Good signs** 🟢:
- Actual line tracking close to Ideal line
- Estimated Fix/Find Delta is negative (fixing more than finding)
- Gap between Required and Actual rates is narrowing

**Warning signs** 🟡:
- Actual line above Estimated line
- Estimated Fix/Find Delta is positive (finding more than fixing)
- Gap between Required and Actual rates is widening

**Red flags** 🔴:
- Actual line trending away from Ideal
- Bug count increasing week-over-week
- Less than 2 weeks to Code Freeze with >50 bugs

### 3. Post Weekly Update to Slack (Optional)

The Slack content auto-generates, but you need to post it manually:

```bash
# Content is always up-to-date in these files:
# - burndown_chart.png
# - slack_message.json

# Option 1: Manual post
# Upload burndown_chart.png to Slack
# Copy/paste message from slack_message.json

# Option 2: Automated post (if Slack token configured)
python post_to_slack.py #channel-name
```

---

## Monthly Tasks

### 1. Review Historical Rate

The historical rate affects projections. Review it monthly:

```bash
python calculate_historical_rate.py
```

This recalculates based on last 3 milestones. If team velocity has changed significantly, this will reflect it.

### 2. Audit Bug Data Quality

Check for data issues:

**Look for**:
- Bugs without milestone tags
- Bugs with incorrect status
- Duplicate bugs
- Bugs missing created/closed dates

**Ask Claude**:
> "Analyze the bug data for quality issues"

### 3. Archive Old Data (After Release)

After 3.0.0 ships, archive the data:

```bash
# Create archive directory
mkdir -p archives/3.0.0-$(date +%Y-%m-%d)

# Move relevant files
mv burndown_projections.json archives/3.0.0-*/
mv burndown_chart.png archives/3.0.0-*/
mv historical_actuals_*.json archives/3.0.0-*/

# Commit
git add archives/
git commit -m "Archive 3.0.0 dashboard data"
git push
```

---

## As-Needed Tasks

### Manually Update Dashboard

If automated updates fail or you need an immediate update:

```bash
# Quick update (~6 seconds)
python update_today_burndown.py

# This automatically:
# 1. Counts current bugs
# 2. Updates projections
# 3. Regenerates dashboard + Slack
# 4. Commits and pushes to GitHub
```

### Refresh Bug Data from ClickUp

If bug counts are stale (automation uses cached data):

```bash
# Fetch latest from ClickUp API (requires CLICKUP_API_TOKEN in .env)
python clickup_batch_fetcher.py

# Then regenerate everything
python calculate_burndown_projections.py
python generate_burndown_projection_chart.py
python generate_slack_burndown.py

# Commit and push
git add bugs_with_parsed_dates.json burndown_projections.json docs/index.html
git commit -m "Manual bug data refresh"
git push
```

### Adjust Milestone Dates

If Code Freeze or Go Live dates change:

1. Edit `milestone_dates_3.0.0.json`:
   ```json
   {
     "code_freeze": "2026-06-02",  # Update this
     "submit": "2026-06-10",       # Or this
     "go_live": "2026-06-15"       # Or this
   }
   ```

2. Regenerate:
   ```bash
   python calculate_burndown_projections.py
   python generate_burndown_projection_chart.py
   git add milestone_dates_3.0.0.json docs/index.html burndown_projections.json
   git commit -m "Update milestone dates"
   git push
   ```

### Change Automation Schedule

If the 3x daily schedule needs adjustment:

1. Edit `.github/workflows/auto-update-dashboard.yml`
2. Update cron schedules (times are in UTC):
   ```yaml
   schedule:
     - cron: '0 14 * * 1-5'  # 7 AM PT = 14:00 UTC
     - cron: '0 19 * * 1-5'  # 12 PM PT = 19:00 UTC
     - cron: '0 23 * * 1-5'  # 4 PM PT = 23:00 UTC
   ```
3. Commit and push

### Manual GitHub Actions Trigger

To trigger an update immediately without waiting:

1. Go to: https://github.com/DaniloFortis/spire-burndown-3-0/actions
2. Click "Auto-Update Bug Burndown Dashboard"
3. Click "Run workflow" → "Run workflow"
4. Wait ~30 seconds for completion

---

## Maintenance Checklist

### Daily ✅ (Automated - No Action)
- [Auto] Dashboard updates 3x
- [Auto] Commits and pushes to GitHub
- [Auto] GitHub Pages deploys

### Weekly
- [ ] Verify dashboard accuracy vs ClickUp
- [ ] Review projection trends
- [ ] Check GitHub Actions for failures
- [ ] (Optional) Post Slack update

### Monthly
- [ ] Review historical rate calculation
- [ ] Audit bug data quality
- [ ] Check automation is still running

### After Release
- [ ] Archive dashboard data
- [ ] Update for next milestone
- [ ] Clean up old data files

---

## Common Maintenance Questions

**Q: Do I need to do anything daily?**
A: No! Automation handles everything. Just monitor weekly.

**Q: How do I know if automation broke?**
A: Check GitHub Actions: https://github.com/DaniloFortis/spire-burndown-3-0/actions
   Red ❌ means failed, green ✅ means working.

**Q: Dashboard shows wrong count, what do I do?**
A: Wait for next automated update (runs every few hours). If still wrong after 24 hours, ask Claude to debug.

**Q: Can I change the update frequency?**
A: Yes! Edit `.github/workflows/auto-update-dashboard.yml` and add/remove cron schedules.

**Q: How do I hand this off to someone else?**
A: See `HANDOFF_CHECKLIST.md` for the full process. TL;DR: Share repo, they open in Claude, Claude guides them.

---

## Getting Help

**Ask Claude** (fastest):
> "The dashboard isn't updating, help me debug"
> "How do I change the automation schedule?"
> "Why is the bug count wrong?"

**Check documentation**:
- `TROUBLESHOOTING.md` - Common issues
- `SETUP.md` - Setup walkthrough
- `CLAUDE.md` - Full project overview

**GitHub Issues**:
https://github.com/DaniloFortis/spire-burndown-3-0/issues

---

*Maintenance is minimal - the system is designed to be hands-off!*
