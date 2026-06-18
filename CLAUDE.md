# Spire 3.0.0 Bug Burndown Dashboard

**Automated bug tracking dashboard with 3-line projection system and GitHub Pages deployment.**

🔗 **Live Dashboard**: https://DaniloFortis.github.io/spire-burndown-3-0/

---

## 🎯 What This Project Does

Tracks Spire 3.0.0 release bug progress with three projection lines:
- **Ideal Line** (Black) - Required burn rate to hit zero by Code Freeze
- **Estimated Line** (Orange) - Projected trajectory based on historical/recent performance
- **Actual Line** (Green) - Real daily bug counts

**Key Features**:
- ✅ Auto-updates 3x daily (7 AM, 12 PM, 4 PM PT) via GitHub Actions
- ✅ Weekend plateaus (realistic projections - no work on Sat/Sun)
- ✅ Auto-switching rate (historical → last 10 business days when available)
- ✅ Slack-ready content (chart + formatted message)
- ✅ Twilight Towers branding

---

## 🚀 Quick Start with Claude

### First Time Setup

1. **Tell Claude**: "Set up this burndown dashboard for me"
   - Claude will walk you through the setup process

2. **Or manually**:
   ```bash
   pip install -r requirements.txt
   python calculate_burndown_projections.py
   python generate_burndown_projection_chart.py
   ```

3. **View locally**: Open `spire_3_0_projection_dashboard.html` in browser

### Common Claude Commands

**Update the dashboard manually**:
> "Update the burndown dashboard with current data"

**Regenerate everything**:
> "Regenerate the burndown projections and dashboard"

**Check automation status**:
> "Are the automated updates running?"

**View current metrics**:
> "Show me the current burndown metrics"

**Fix GitHub Pages deployment**:
> "The dashboard isn't updating on GitHub Pages, help me debug"

**Generate Slack update**:
> "Create a Slack update for the burndown"

---

## 📁 Project Structure

```
.
├── CLAUDE.md                           # This file - Claude reads this first
├── SETUP.md                            # Initial setup guide
├── MAINTENANCE.md                      # Daily operations
├── TROUBLESHOOTING.md                  # Common issues
├── README.md                           # Public-facing docs
│
├── .github/workflows/
│   └── auto-update-dashboard.yml       # GitHub Actions (3x daily updates)
│
├── Core Scripts (Run in this order):
├── calculate_burndown_projections.py   # 1. Calculate projections
├── generate_burndown_projection_chart.py # 2. Generate HTML dashboard
├── generate_slack_burndown.py          # 3. Create Slack content
│
├── Helper Scripts:
├── update_today_burndown.py            # Quick daily update (used by automation)
├── clickup_batch_fetcher.py            # Fetch bug data from ClickUp
├── calculate_historical_rate.py        # Calculate historical burn rate
├── calculate_historical_actuals.py     # Retroactive daily counts
│
├── Data Files:
├── bugs_with_parsed_dates.json         # Bug data (NOT in git - too large)
├── burndown_projections.json           # Current projections
├── burndown_data.json                  # Historical metrics
├── historical_rate_analysis.json       # Historical rate from past releases
├── historical_actuals_5_11_to_5_21.json # Retroactive actual counts
├── milestone_dates_3.0.0.json          # Milestone configuration
│
├── Output:
├── docs/index.html                     # GitHub Pages dashboard (auto-published)
├── burndown_chart.png                  # Slack chart
├── slack_message.json                  # Slack message blocks
└── spire_3_0_projection_dashboard.html # Local dashboard
```

---

## 🤖 Automated Updates (GitHub Actions)

**Schedule**: Runs 3x daily on weekdays (Mon-Fri)
- 7:00 AM PT (14:00 UTC)
- 12:00 PM PT (19:00 UTC)
- 4:00 PM PT (23:00 UTC)

**What happens automatically**:
1. Counts current active 3.0.0 bugs
2. Updates projections with today's count
3. Recalculates estimated line
4. Regenerates dashboard + Slack content
5. Commits: "Auto-update: X bugs, Y days to freeze"
6. Pushes to GitHub → GitHub Pages auto-deploys

**To verify it's working**:
- Check: https://github.com/DaniloFortis/spire-burndown-3-0/actions
- Or ask Claude: "Show me recent GitHub Actions runs"

**To trigger manually**:
- Go to Actions tab → "Auto-Update Bug Burndown Dashboard" → "Run workflow"

---

## 📊 Understanding the Data

### Metric Cards

1. **Active Bugs** - Current count of non-closed, non-WON'T FIX bugs
2. **Code Freeze** - Business days remaining until freeze (June 2, 2026)
3. **Required Bugs Fixed per Day** - Rate needed to hit zero by Code Freeze (152 bugs ÷ 8 days = 19.0/day)
4. **Estimated/Actual Fix/Find Delta** - Projection rate
   - Shows "Estimated" (historical average) until 10 business days of actual data
   - Switches to "Actual" (last 10 business days) once enough data
5. **Go Live** - Target release date (June 15, 2026)

### The Three Lines

**Ideal Line** (Black):
- Calculated: `current_bugs / business_days_to_freeze`
- Recalculates daily as time passes
- Plateaus on weekends (no progress expected)
- Stops at zero on Code Freeze date

**Estimated Line** (Orange):
- Uses historical rate OR last 10 business days (auto-switches)
- Projects forward from last actual data point
- Shows realistic trajectory based on past performance
- Plateaus on weekends

**Actual Line** (Green):
- Real daily bug counts
- Updated 3x daily by automation
- Transitions seamlessly into Estimated line

---

## 🔧 Manual Operations

### Update Dashboard Manually

```bash
# Quick update (adds today's count, ~6 seconds)
python update_today_burndown.py

# Full recalculation (if needed, ~10 seconds)
python calculate_burndown_projections.py
python generate_burndown_projection_chart.py
python generate_slack_burndown.py
```

### Refresh Bug Data from ClickUp

```bash
# Fetch latest bug data (requires ClickUp API token)
python clickup_batch_fetcher.py
```

**Note**: You'll need `CLICKUP_API_TOKEN` in `.env` file

### Deploy to GitHub Pages

```bash
# Commit and push (GitHub Pages auto-deploys in 1-2 min)
git add docs/index.html burndown_projections.json
git commit -m "Update dashboard - [description]"
git push
```

### Generate Slack Content

```bash
# Creates burndown_chart.png + slack_message.json
python generate_slack_burndown.py

# Then manually post to Slack or use post_to_slack.py
```

---

## 🎨 Customization

### Change Milestone Dates

Edit `milestone_dates_3.0.0.json`:
```json
{
  "code_freeze": "2026-06-02",
  "submit": "2026-06-10",
  "go_live": "2026-06-15"
}
```

### Change Branding

Edit `generate_burndown_projection_chart.py`:
- Colors: Search for `#3B2A5C` (purple) and `#F4C542` (gold)
- Logo: Replace `TwilightTowerslogo.png`
- Title: Search for "3.0.0 Bug Burndown Projection"

### Change Automation Schedule

Edit `.github/workflows/auto-update-dashboard.yml`:
```yaml
schedule:
  - cron: '0 14 * * 1-5'  # 7 AM PT
  - cron: '0 19 * * 1-5'  # 12 PM PT
  - cron: '0 23 * * 1-5'  # 4 PM PT
```

---

## ⚠️ Important Notes

### WON'T FIX Status

Bugs marked as "WON'T FIX" are **excluded** from active counts. They're not counted as active OR closed - they're a decision to do nothing.

The excluded statuses are: `['Closed', 'closed', "won't fix", "Won't Fix", "WON'T FIX"]`

### Weekend Behavior

All projection lines **plateau on weekends** (Sat/Sun). This means:
- No progress expected on weekends
- Lines show Friday's count on Sat/Sun
- Progress resumes Monday

This creates realistic projections - you'll see step patterns on the chart.

### Large Files Not in Git

These files are excluded from git (too large):
- `bugs_with_parsed_dates.json` (843 KB)
- `spire_bugs_complete.json` (121 MB)

They must be regenerated after cloning:
```bash
python clickup_batch_fetcher.py  # Fetches from ClickUp
```

---

## 🆘 Troubleshooting

### Dashboard not updating on GitHub Pages

1. Check GitHub Actions: https://github.com/DaniloFortis/spire-burndown-3-0/actions
2. If failed, check error logs in Actions tab
3. Verify `docs/index.html` exists and is committed
4. GitHub Pages settings: Settings → Pages → Source: `main` branch, `/docs` folder

### "No such file" errors

Missing data files. Run:
```bash
python clickup_batch_fetcher.py  # Fetch bug data
python calculate_burndown_projections.py  # Generate projections
```

### Counts don't match ClickUp

1. Verify WON'T FIX exclusion is working
2. Check milestone filter: `milestone_simplified == '3.0.0'`
3. Refresh bug data: `python clickup_batch_fetcher.py`

### GitHub Actions not running

1. Check workflow file exists: `.github/workflows/auto-update-dashboard.yml`
2. Verify it's enabled: Actions tab → Check workflow isn't disabled
3. Manual trigger: Actions → "Auto-Update..." → "Run workflow"

For more help, see `TROUBLESHOOTING.md` or ask Claude!

---

## 📚 Additional Documentation

- `SETUP.md` - Initial setup walkthrough
- `MAINTENANCE.md` - Daily operations and upkeep
- `TROUBLESHOOTING.md` - Detailed troubleshooting guide
- `README.md` - Public-facing documentation

---

## 🤝 Handing Off to Someone Else

See `HANDOFF_CHECKLIST.md` for a complete onboarding checklist.

**Quick handoff**:
1. Share this repository
2. They open in Claude Code
3. Claude reads this file automatically
4. They say: "Help me get started with this burndown dashboard"

That's it! Claude will guide them through setup.

---

## 💡 Tips for Working with Claude

**Claude is great at**:
- Debugging GitHub Actions failures
- Explaining why metrics changed
- Regenerating everything after changes
- Creating new visualizations
- Updating automation schedules

**Just ask naturally**:
- "Why did the estimated rate change?"
- "The chart looks wrong, help me debug"
- "Add a new metric card for [X]"
- "Change the automation to run 4 times instead of 3"

Claude has full context about this project!

---

*Last updated: May 21, 2026*
*Maintained by: Taylor Westfall*
*Built with: Claude Code*
