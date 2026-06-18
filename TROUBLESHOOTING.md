# Troubleshooting Guide - Spire 3.0.0 Bug Burndown Dashboard

Solutions to common issues and error messages.

---

## Quick Diagnostics

**First, ask Claude**:
> "Help me debug the burndown dashboard"

Claude has full context and can diagnose most issues faster than this guide.

---

## Dashboard Issues

### Dashboard Not Updating on GitHub Pages

**Symptoms**: Live dashboard shows old data, even after automation runs.

**Check**:
1. View recent GitHub Actions: https://github.com/DaniloFortis/spire-burndown-3-0/actions
2. Look for ✅ green checkmarks (success) or ❌ red X's (failure)

**If Actions are green but dashboard is stale**:
```bash
# Hard refresh your browser (clear cache)
# Windows/Linux: Ctrl + Shift + R
# Mac: Cmd + Shift + R

# Or open in incognito/private window
```

**If Actions are failing**:
1. Click the failed run
2. Read error message
3. Ask Claude: "GitHub Actions failed with: [error message]"

**Common fixes**:
- Verify `docs/index.html` exists and is committed
- Check GitHub Pages settings: Settings → Pages → Source = `main` `/docs`
- Wait 2-3 minutes after push for deployment

### Bug Counts Don't Match ClickUp

**Symptoms**: Dashboard shows different active bug count than ClickUp.

**Expected difference**: ±1-2 bugs (automation runs 3x daily, not realtime)

**If difference is large (>5 bugs)**:

1. **Verify filter in ClickUp**:
   - Milestone: "3.0.0"
   - Status: NOT "Closed" AND NOT "WON'T FIX"

2. **Check excluded statuses** (these are NOT counted):
   ```python
   excluded = ['Closed', 'closed', "won't fix", "Won't Fix", "WON'T FIX"]
   ```

3. **Refresh bug data**:
   ```bash
   python clickup_batch_fetcher.py
   python calculate_burndown_projections.py
   python generate_burndown_projection_chart.py
   ```

4. **Ask Claude**:
   > "Dashboard shows 152 bugs but ClickUp shows 148, why?"

### Charts Not Showing / Blank Dashboard

**Symptoms**: Dashboard loads but charts are missing.

**Fixes**:
```bash
# Reinstall Plotly
pip install --upgrade plotly kaleido

# Regenerate dashboard
python generate_burndown_projection_chart.py
```

**Check browser console** (F12 → Console tab):
- If you see JavaScript errors, report them to Claude

### Weekend Plateaus Look Wrong

**Symptoms**: Lines should be flat on Sat/Sun but aren't.

**This is normal if**:
- Actual line shows change on weekend (manual bug triage happened)
- You're viewing a weekday (plateaus only visible on Sat/Sun dates)

**This is a bug if**:
- Ideal or Estimated lines change on Saturday/Sunday
- Ask Claude: "Weekend plateaus aren't working"

---

## Automation Issues

### GitHub Actions Not Running

**Symptoms**: No automatic updates at scheduled times.

**Check if workflow is enabled**:
1. Go to: https://github.com/DaniloFortis/spire-burndown-3-0/actions
2. Click "Auto-Update Bug Burndown Dashboard"
3. Look for "This workflow is disabled" message
4. If disabled, click "Enable workflow"

**Check schedule syntax**:
```bash
cat .github/workflows/auto-update-dashboard.yml
# Should show:
#   - cron: '0 14 * * 1-5'  # 7 AM PT
#   - cron: '0 19 * * 1-5'  # 12 PM PT
#   - cron: '0 23 * * 1-5'  # 4 PM PT
```

**Manual trigger** (to test):
1. Actions → "Auto-Update..." → "Run workflow"
2. If this fails, check error logs
3. Share error with Claude

### Actions Failing with "No such file"

**Error**: `FileNotFoundError: bugs_with_parsed_dates.json`

**Cause**: Bug data file is missing (not in git - too large)

**Fix**:
```bash
# Fetch bug data from ClickUp
python clickup_batch_fetcher.py

# Add to git (optional, increases repo size)
git add bugs_with_parsed_dates.json
git commit -m "Add bug data for automation"
git push
```

**Better solution**: Set up ClickUp API integration in Actions
- Add `CLICKUP_API_TOKEN` to GitHub Secrets
- Modify workflow to fetch data before update

### Actions Failing with "Permission denied"

**Error**: `fatal: unable to push to remote`

**Cause**: GitHub Actions doesn't have write permissions.

**Fix**:
1. Go to: Settings → Actions → General
2. Scroll to "Workflow permissions"
3. Select "Read and write permissions"
4. Click "Save"

---

## Data Issues

### "Invalid date" or "NoneType" Errors

**Error when running**: `TypeError: unsupported operand type(s) for -: 'NoneType' and 'datetime.datetime'`

**Cause**: Some bugs are missing `date_created` or `date_closed` fields.

**Fix**:
```bash
# Re-fetch bug data
python clickup_batch_fetcher.py

# Or ask Claude:
```
> "I'm getting NoneType errors in date calculations, help debug"

### Historical Rate Seems Wrong

**Symptoms**: `historical_daily_rate` is unexpected (e.g., positive when it should be negative)

**Check calculation**:
```bash
python calculate_historical_rate.py

# Review output - it shows:
# - Bugs found in each milestone
# - Bugs fixed in each milestone
# - Net change
# - Daily rate
```

**Common issues**:
- Milestone dates wrong in past releases
- Bugs tagged with wrong milestone
- "Closed" bugs aren't actually fixed (status mapping issue)

**Recalculate**:
```bash
python calculate_historical_rate.py
python calculate_burndown_projections.py
python generate_burndown_projection_chart.py
```

### Estimated Line Not Switching to "Actual"

**Symptoms**: After 10 business days, still shows "historical average" instead of "last 10 business days"

**Check actual data count**:
```python
# Run in Python:
import json
from datetime import datetime

with open('burndown_projections.json') as f:
    data = json.load(f)

actual = data['projections']['actual']
business_days = [
    p for p in actual
    if datetime.strptime(p['date'], '%Y-%m-%d').weekday() < 5
]

print(f"Business days in actual data: {len(business_days)}")
# Should be >= 10 to switch
```

**Fix**:
- Add more actual data points (wait for more daily updates)
- Or ask Claude: "Why isn't the rate switching to actual?"

---

## File Issues

### "File not found" Errors

**Common missing files**:
- `bugs_with_parsed_dates.json` - Run `python clickup_batch_fetcher.py`
- `burndown_projections.json` - Run `python calculate_burndown_projections.py`
- `historical_rate_analysis.json` - Run `python calculate_historical_rate.py`
- `milestone_dates_3.0.0.json` - Should be in git, re-clone if missing

**Regenerate all data files**:
```bash
python clickup_batch_fetcher.py          # Fetch bugs
python calculate_historical_rate.py       # Calculate rate
python calculate_burndown_projections.py  # Generate projections
python generate_burndown_projection_chart.py  # Create dashboard
```

### Git Conflicts

**Error**: `error: Your local changes to the following files would be overwritten by merge`

**Common conflict**: `docs/index.html` or `burndown_projections.json`

**Safe resolution** (local changes are auto-generated):
```bash
# Stash local changes
git stash

# Pull latest
git pull

# Regenerate (don't apply stash)
python generate_burndown_projection_chart.py

# Commit new version
git add docs/index.html
git commit -m "Regenerate dashboard"
git push
```

---

## Environment Issues

### "ModuleNotFoundError"

**Error**: `ModuleNotFoundError: No module named 'plotly'`

**Fix**:
```bash
pip install -r requirements.txt

# Or install individually:
pip install plotly kaleido requests python-dotenv
```

### Kaleido / PNG Export Issues

**Error**: `ValueError: The kaleido package is required for image export`

**Fix**:
```bash
# Uninstall and reinstall
pip uninstall kaleido
pip install kaleido

# Or try specific version
pip install kaleido==0.2.1
```

**Windows-specific** issues:
```bash
# May need to add to PATH
# Or use plotly-orca instead:
pip install plotly-orca
```

---

## Performance Issues

### Scripts Running Slowly

**Symptoms**: `calculate_burndown_projections.py` takes >30 seconds

**Possible causes**:
- Very large bug data file (>10 MB)
- Slow disk I/O
- Loading all data into memory

**Optimizations**:
```bash
# Use quick update instead of full recalculation
python update_today_burndown.py  # ~6 seconds vs ~30 seconds

# Or ask Claude:
```
> "Scripts are running slowly, help optimize"

---

## Getting More Help

### Talk to Claude (Fastest)

Open this project in Claude Code and ask:
> "I'm getting this error: [paste error]"
> "The dashboard looks wrong, help me debug"
> "Walk me through troubleshooting [specific issue]"

Claude has full project context and can:
- Read error logs
- Check file contents
- Suggest fixes
- Run commands for you

### Check GitHub

- **Actions logs**: https://github.com/DaniloFortis/spire-burndown-3-0/actions
- **Issues**: Create issue if you find a bug
- **Recent commits**: Check what changed recently

### Manual Inspection

```bash
# Check file sizes
ls -lh *.json

# Check last modified times
ls -lt *.json | head -5

# Verify data integrity
python -c "import json; json.load(open('burndown_projections.json'))" && echo "Valid JSON"

# Check git status
git status
git log --oneline -5
```

---

## Error Reference

| Error | Likely Cause | Quick Fix |
|-------|--------------|-----------|
| `FileNotFoundError: bugs_with_parsed_dates.json` | Missing bug data | Run `python clickup_batch_fetcher.py` |
| `KeyError: 'milestone_simplified'` | Bug data structure changed | Re-fetch: `python clickup_batch_fetcher.py` |
| `TypeError: unsupported operand type(s)` | Missing date field | Check bug data for null dates |
| `ModuleNotFoundError: No module named 'X'` | Missing dependency | Run `pip install -r requirements.txt` |
| `git push` permission denied | Actions lacks write access | Settings → Actions → Read and write permissions |
| Chart not rendering | Plotly/Kaleido issue | Reinstall: `pip install --upgrade plotly kaleido` |
| Wrong bug count | Filter mismatch | Verify WON'T FIX exclusion |

---

**Still stuck? Ask Claude!**
