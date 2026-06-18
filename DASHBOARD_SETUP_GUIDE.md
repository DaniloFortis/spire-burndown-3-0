# Dashboard Setup Guide - For Claude

**This file contains instructions for Claude Code on how to interactively set up a bug burndown dashboard for a new team.**

When a user loads `CREATE_BURNDOWN_DASHBOARD.md` and asks you to help them create a dashboard, follow this guide to collect their requirements and generate all necessary files.

---

## Setup Flow

### Phase 1: Gather Requirements (Interactive Q&A)

Ask the user these questions **one at a time** to avoid overwhelming them:

#### 1.1 ClickUp Authentication
```
"Let's get started! First, I need your ClickUp API token to fetch bug data.

To get your token:
1. Go to ClickUp → Settings → Apps
2. Click 'Generate' under 'API Token'
3. Copy the token (starts with 'pk_')

Paste your ClickUp API token:"
```

**Store as**: `clickup_api_token`

#### 1.2 ClickUp Project Location
```
"Great! Now I need to know where your bugs are in ClickUp.

What's your ClickUp Team ID? (You can find this in the URL when logged into ClickUp - it's the number after 'team/')"
```

**Store as**: `clickup_team_id`

**Then ask** (optional):
```
"Do your bugs live in a specific Space, Folder, or List? Or should I search the entire team?

Options:
1. Entire team (search all spaces)
2. Specific Space (provide Space ID)
3. Specific Folder (provide Folder ID)
4. Specific List (provide List ID)

Enter option number:"
```

**If they don't know their IDs**, offer:
```
"I can help you find these IDs. I'll fetch your team structure and show you the names and IDs. Would you like me to do that? (yes/no)"
```

If yes, use the ClickUp API to fetch spaces/folders/lists and display them.

#### 1.3 Release Information
```
"What's the milestone name in ClickUp for this release?

For example: '3.0.0', 'Q3 2026 Release', 'Version 3.0'

Milestone name:"
```

**Store as**: `milestone_name`

```
"When is Code Freeze? (The date when you stop adding features and focus on bugs)

Format: YYYY-MM-DD (example: 2026-06-02)

Code Freeze date:"
```

**Validate date format** and **store as**: `code_freeze_date`

```
"When is Go Live? (The date when this release ships to production)

Format: YYYY-MM-DD (example: 2026-06-15)

Go Live date:"
```

**Validate**: Go Live must be after Code Freeze.  
**Store as**: `go_live_date`

**Optional**:
```
"Is there a Submit date? (When you submit to app stores, QA, etc.)

If not, just press Enter to skip.

Submit date (YYYY-MM-DD or leave blank):"
```

**Store as**: `submit_date` (can be null)

#### 1.4 Bug Status Mapping
```
"Which bug statuses should count as 'active' bugs?

For example: Open, In Progress, Ready for QA, In QA, Blocked

Enter status names separated by commas:"
```

**Store as**: `active_statuses` (list)

```
"Which bug statuses should be excluded from counts?

For example: Closed, Won't Fix, Duplicate, Deferred

Enter status names separated by commas:"
```

**Store as**: `excluded_statuses` (list)

#### 1.5 Branding (Optional)
```
"What's your team or product name? This will appear in the dashboard title.

For example: 'MyApp', 'Spire', 'Platform Team'

Team/Product name:"
```

**Store as**: `team_name`

```
"Would you like to customize the dashboard colors?

Default colors are purple (#3B2A5C) and gold (#F4C542).

Enter 'yes' to customize or 'no' to use defaults:"
```

If yes:
```
"Primary color (hex code, e.g., #1E3A8A):"
"Accent color (hex code, e.g., #FB923C):"
```

**Store as**: `primary_color`, `accent_color`

#### 1.6 GitHub Repository
```
"What's your GitHub repository for this dashboard?

Format: username/repo-name (example: myteam/bug-dashboard)

GitHub repository:"
```

**Store as**: `github_repo`

**Validate** that the repo exists or offer to help create it.

---

### Phase 2: Fetch Bug Data

```
"Perfect! I have everything I need. Let me fetch your bug data from ClickUp...

This will take about 30-60 seconds depending on how many bugs you have."
```

**Actions**:
1. Use ClickUp API with their token to fetch bugs
2. Filter by milestone name
3. Parse dates (created, closed)
4. Save to `bugs_with_parsed_dates.json`
5. Count active bugs
6. Report results:

```
"✅ Found [X] bugs in milestone '[milestone_name]'
   - [Y] active bugs
   - [Z] closed bugs
   - Date range: [earliest] to [latest]"
```

---

### Phase 3: Generate Files

```
"Now I'll generate all the files for your dashboard. This includes:
- Python scripts for calculations and visualization
- GitHub Actions workflow for automation
- HTML dashboard
- Documentation files

Generating files..."
```

**Create these files** with user's custom values:

#### 3.1 Configuration Files

**`milestone_dates_{milestone_name}.json`**:
```json
{
  "code_freeze": "{code_freeze_date}",
  "submit": "{submit_date}",
  "go_live": "{go_live_date}"
}
```

**`.env`**:
```
CLICKUP_API_TOKEN={clickup_api_token}
CLICKUP_TEAM_ID={clickup_team_id}
```

**`.gitignore`** (ensure sensitive files excluded):
```
.env
bugs_with_parsed_dates.json
spire_bugs_complete.json
*.pyc
__pycache__/
```

#### 3.2 Python Scripts

**Customize these files** with user's values:
- `calculate_burndown_projections.py` - Update milestone name, excluded statuses
- `generate_burndown_projection_chart.py` - Update title, colors, branding
- `update_today_burndown.py` - Update milestone name, excluded statuses
- `generate_slack_burndown.py` - Update title, branding
- `clickup_batch_fetcher.py` - Update team ID, space/folder/list filters

**Key customizations**:
```python
# In all scripts, replace:
milestone_name = "3.0.0"  → milestone_name = "{milestone_name}"
excluded_statuses = ['Closed', 'closed', "won't fix", "Won't Fix", "WON'T FIX"]  → excluded_statuses = {excluded_statuses}

# In generate_burndown_projection_chart.py:
title = "Spire 3.0.0 Bug Burndown"  → title = "{team_name} {milestone_name} Bug Burndown"
primary_color = "#3B2A5C"  → primary_color = "{primary_color}"
accent_color = "#F4C542"  → accent_color = "{accent_color}"
```

#### 3.3 GitHub Actions Workflow

**`.github/workflows/auto-update-dashboard.yml`**:
```yaml
name: Auto-Update Bug Burndown Dashboard

on:
  schedule:
    - cron: '0 14 * * 1-5'  # 7 AM PT
    - cron: '0 19 * * 1-5'  # 12 PM PT
    - cron: '0 23 * * 1-5'  # 4 PM PT
  workflow_dispatch:

permissions:
  contents: write

jobs:
  update-dashboard:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Update dashboard
        env:
          CLICKUP_API_TOKEN: ${{ secrets.CLICKUP_API_TOKEN }}
        run: python update_today_burndown.py
      
      - name: Commit changes
        run: |
          git config user.name "GitHub Actions Bot"
          git config user.email "actions@github.com"
          git add -A
          git diff --quiet && git diff --staged --quiet || git commit -m "Auto-update: $(date +'%Y-%m-%d %H:%M')"
          git push
```

#### 3.4 Documentation Files

Generate customized versions of:
- `CLAUDE.md` - Replace Spire 3.0.0 references with their milestone
- `README.md` - Update title, links, milestone dates
- `SETUP.md` - Standard setup guide
- `MAINTENANCE.md` - Standard maintenance guide
- `TROUBLESHOOTING.md` - Standard troubleshooting guide

#### 3.5 Requirements File

**`requirements.txt`**:
```
requests>=2.31.0
python-dotenv>=1.0.0
plotly>=5.18.0
kaleido>=0.2.1
```

---

### Phase 4: Calculate Projections

```
"Files generated! Now calculating initial projections..."
```

**Run**:
```bash
python calculate_burndown_projections.py
python generate_burndown_projection_chart.py
python generate_slack_burndown.py
```

**Report**:
```
"✅ Dashboard generated!
   - Current active bugs: [X]
   - Days to Code Freeze: [Y]
   - Required burn rate: [Z] bugs/day
   - Historical rate: [W] bugs/day"
```

---

### Phase 5: Set Up GitHub

```
"Almost done! Now let's set up GitHub..."
```

**Actions**:
1. Initialize git (if not already): `git init`
2. Add all files: `git add .`
3. Commit: `git commit -m "Initial dashboard setup for {milestone_name}"`
4. Set remote: `git remote add origin https://github.com/{github_repo}.git`
5. Push: `git push -u origin main`

**Then guide them to configure GitHub**:
```
"To enable automatic updates and GitHub Pages deployment:

1. Add your ClickUp API token to GitHub Secrets:
   - Go to: https://github.com/{github_repo}/settings/secrets/actions
   - Click 'New repository secret'
   - Name: CLICKUP_API_TOKEN
   - Value: [your token]
   - Click 'Add secret'

2. Enable GitHub Pages:
   - Go to: https://github.com/{github_repo}/settings/pages
   - Source: Deploy from branch
   - Branch: main
   - Folder: /docs
   - Click 'Save'

3. Enable write permissions for Actions:
   - Go to: https://github.com/{github_repo}/settings/actions
   - Scroll to 'Workflow permissions'
   - Select 'Read and write permissions'
   - Click 'Save'

I can wait while you do this, or we can continue and you can do it later. What would you prefer?"
```

---

### Phase 6: Test and Verify

```
"Let's verify everything works..."
```

**Check**:
1. ✅ Bug data fetched (`bugs_with_parsed_dates.json` exists)
2. ✅ Projections calculated (`burndown_projections.json` exists)
3. ✅ Dashboard generated (`docs/index.html` exists)
4. ✅ Slack content created (`burndown_chart.png` and `slack_message.json` exist)

**Open local dashboard**:
```
"You can view your dashboard locally by opening:
{project_path}/docs/index.html

Would you like me to open it for you? (yes/no)"
```

If yes, open in browser.

---

### Phase 7: Next Steps

```
"🎉 Your dashboard is ready!

Here's what you have:
- ✅ Local dashboard: docs/index.html
- ✅ Automated updates: .github/workflows/auto-update-dashboard.yml
- ✅ Slack content: burndown_chart.png + slack_message.json
- ✅ Full documentation: CLAUDE.md, SETUP.md, MAINTENANCE.md

Next steps:
1. Complete GitHub setup (secrets, Pages, permissions) if you haven't already
2. Wait for GitHub Pages to deploy (~2 min): https://{github_user}.github.io/{repo_name}/
3. Check that automation runs at 7 AM, 12 PM, 4 PM PT
4. Share the dashboard link with your team!

Your dashboard will automatically update 3 times daily on weekdays.

Need help with anything? Just ask!"
```

---

## Troubleshooting During Setup

### ClickUp API Issues

**Error: Invalid token**
```
"The ClickUp API token seems invalid. Let's try again.

Make sure you:
1. Copy the entire token (starts with 'pk_')
2. Don't include any extra spaces
3. Generated it for the correct workspace

Paste your token again:"
```

**Error: No bugs found**
```
"I didn't find any bugs with milestone '{milestone_name}'.

Possible issues:
1. The milestone name doesn't match exactly (case-sensitive)
2. Bugs aren't tagged with this milestone yet
3. The team/space/folder ID is wrong

Would you like to:
1. Try a different milestone name
2. Search all milestones and show what's available
3. Check the team/space/folder ID"
```

### Date Format Issues

**Invalid date**:
```
"That date format isn't valid. Please use YYYY-MM-DD format.

Examples:
- 2026-06-02
- 2026-12-31

Try again:"
```

**Illogical dates**:
```
"The Go Live date must be after Code Freeze.

Code Freeze: {code_freeze_date}
Go Live: {go_live_date}

Please enter a Go Live date after {code_freeze_date}:"
```

### GitHub Issues

**Repo doesn't exist**:
```
"I can't access the repository {github_repo}.

Options:
1. Create the repo on GitHub first, then come back
2. Give me a different repo name
3. I can help you create it via GitHub CLI (if you have it installed)

What would you like to do?"
```

---

## Customization Requests

If the user asks for customizations during or after setup:

### "Change the update frequency"
```
"I can change the automation schedule. Current schedule is 3x daily (7 AM, 12 PM, 4 PM PT).

What frequency would you like?
1. Custom times (you specify)
2. More frequent (e.g., hourly)
3. Less frequent (e.g., once daily)"
```

### "Use different colors"
```
"I'll update the dashboard colors.

Primary color (main background): [current]
Accent color (highlights, buttons): [current]

Enter new colors as hex codes (e.g., #1E3A8A) or press Enter to keep current:"
```

### "Include multiple milestones"
```
"I'll modify the scripts to include bugs from multiple milestones.

Enter milestone names separated by commas:"
```

Then update filtering logic in all scripts.

---

## Post-Setup Support

After initial setup, help with:

- **Viewing current metrics**: Read `burndown_projections.json` and explain
- **Debugging automation**: Check GitHub Actions logs
- **Updating milestone dates**: Edit `milestone_dates_{milestone_name}.json` and regenerate
- **Refreshing bug data**: Run `clickup_batch_fetcher.py`
- **Customizing visuals**: Edit `generate_burndown_projection_chart.py`

**Always**:
1. Explain what you're doing
2. Show the commands you're running
3. Verify results
4. Offer to regenerate the dashboard

---

## Key Principles

1. **One question at a time** - Don't overwhelm the user
2. **Validate inputs** - Check formats, dates, API connectivity
3. **Explain as you go** - Tell them what's happening and why
4. **Offer help** - If they're stuck, provide options
5. **Test everything** - Verify each phase before moving on
6. **Generate complete files** - Don't leave placeholders or TODOs
7. **Customize thoroughly** - Replace ALL Spire 3.0.0 references with their values

---

**This guide ensures every team gets a fully functional, customized dashboard with minimal effort.**
