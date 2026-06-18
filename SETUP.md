# Setup Guide - Spire 3.0.0 Bug Burndown Dashboard

Complete setup instructions for getting the dashboard running on a new machine.

---

## Prerequisites

- Python 3.10+ installed
- Git installed
- GitHub account with access to `DaniloFortis/spire-burndown-3-0`
- ClickUp API access (optional - for data fetching)

---

## Step 1: Clone Repository

```bash
git clone https://github.com/DaniloFortis/spire-burndown-3-0.git
cd spire-burndown-3-0
```

---

## Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

**Installs**:
- `requests` - API calls
- `python-dotenv` - Environment variables
- `plotly` - Interactive charts
- `kaleido` - PNG export for Slack

---

## Step 3: Configure Environment (Optional)

Only needed if fetching data from ClickUp:

```bash
# Create .env file
cp .env.example .env

# Edit .env and add your tokens:
# CLICKUP_API_TOKEN=pk_your_token_here
# SLACK_BOT_TOKEN=xoxb_your_token_here  # Optional for Slack posting
```

---

## Step 4: Generate Initial Data

### Option A: Fetch from ClickUp (Recommended)

```bash
python clickup_batch_fetcher.py
```

This creates:
- `spire_bugs_complete.json` - Raw bug data
- `bugs_with_parsed_dates.json` - Processed bug data

### Option B: Use Existing Data

If you already have bug data files, just ensure they exist in the project root.

---

## Step 5: Calculate Projections

```bash
# Calculate historical rate from past releases
python calculate_historical_rate.py

# Generate current projections
python calculate_burndown_projections.py
```

**Outputs**:
- `historical_rate_analysis.json` - Historical burn rate
- `burndown_projections.json` - Current projections

---

## Step 6: Generate Dashboard

```bash
# Generate HTML dashboard
python generate_burndown_projection_chart.py

# Generate Slack content (optional)
python generate_slack_burndown.py
```

**Outputs**:
- `spire_3_0_projection_dashboard.html` - Local dashboard
- `docs/index.html` - GitHub Pages version
- `burndown_chart.png` - Slack chart
- `slack_message.json` - Slack message

---

## Step 7: View Dashboard Locally

Open `spire_3_0_projection_dashboard.html` in your browser.

**Verify**:
- ✅ Chart loads with 3 lines (Ideal, Estimated, Actual)
- ✅ 5 metric cards show current data
- ✅ Milestone markers appear (Code Freeze, Submit, Go Live)
- ✅ Weekend plateaus visible in projection lines

---

## Step 8: Deploy to GitHub Pages (Optional)

```bash
# Commit and push
git add docs/index.html burndown_projections.json
git commit -m "Initial dashboard deployment"
git push
```

**Verify deployment**:
1. Go to: https://github.com/DaniloFortis/spire-burndown-3-0/actions
2. Wait for "pages-build-deployment" to complete (~1-2 min)
3. Visit: https://DaniloFortis.github.io/spire-burndown-3-0/

---

## Step 9: Verify Automation

GitHub Actions should already be configured to run 3x daily.

**Check status**:
```bash
# View workflow file
cat .github/workflows/auto-update-dashboard.yml

# Or visit:
# https://github.com/DaniloFortis/spire-burndown-3-0/actions
```

**Manual trigger** (for testing):
1. Go to Actions tab on GitHub
2. Select "Auto-Update Bug Burndown Dashboard"
3. Click "Run workflow"

---

## Verification Checklist

After setup, verify everything works:

- [ ] Python dependencies installed (`pip list | grep plotly`)
- [ ] Bug data files exist (`bugs_with_parsed_dates.json`)
- [ ] Projections generated (`burndown_projections.json`)
- [ ] Local dashboard opens and looks correct
- [ ] GitHub Pages dashboard accessible
- [ ] GitHub Actions workflow exists and enabled
- [ ] Can manually trigger workflow from Actions tab

---

## Troubleshooting Setup Issues

### "ModuleNotFoundError: No module named 'plotly'"

```bash
pip install -r requirements.txt
```

### "FileNotFoundError: bugs_with_parsed_dates.json"

You need to fetch bug data:
```bash
python clickup_batch_fetcher.py
```

Or get the file from someone who already has it.

### GitHub Pages shows 404

1. Check Settings → Pages → Source is set to `main` branch, `/docs` folder
2. Verify `docs/index.html` exists and is committed
3. Wait 2-3 minutes after pushing for deployment

### GitHub Actions not running

1. Check the workflow file exists: `.github/workflows/auto-update-dashboard.yml`
2. Ensure it's enabled in Actions tab
3. Check you have write permissions to the repository

---

## Next Steps

- Read `MAINTENANCE.md` for daily operations
- Read `TROUBLESHOOTING.md` for common issues
- Open in Claude Code and ask: "Help me understand this dashboard"

---

**Setup complete!** 🎉

The dashboard should now be running locally and deployed to GitHub Pages with automated updates.
