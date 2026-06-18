# Create Your Own Bug Burndown Dashboard

**This file will guide you through creating an automated bug burndown dashboard for your release.**

Claude will walk you through collecting your data, customizing the dashboard, and setting up automation. **You don't need to know Python, Git, or GitHub Actions** - Claude handles all the technical details.

---

## 🎯 What You'll Get

An automated dashboard that:
- **Tracks bugs** for your release milestone from ClickUp
- **Projects completion** with 3 lines: Ideal (target), Estimated (realistic), Actual (current)
- **Updates automatically** 3 times a day via GitHub Actions
- **Deploys to GitHub Pages** for easy sharing with your team
- **Shows weekend plateaus** (realistic - no work on Sat/Sun)
- **Calculates rates** automatically from historical data

**Maintenance**: ~5 minutes per week to verify it's working.

---

## 📋 What Claude Needs From You

Before starting, gather this information:

### 1. ClickUp Information
- [ ] **ClickUp API Token** - Get from: ClickUp → Settings → Apps → Generate API Token
- [ ] **Team/Workspace ID** - Your ClickUp team (e.g., "12345678")
- [ ] **Space ID** (optional) - If bugs are in a specific space
- [ ] **Folder ID** (optional) - If bugs are in a specific folder
- [ ] **List ID** (optional) - If bugs are in a specific list

**Don't know your IDs?** Claude can help you find them using your API token.

### 2. Release Information
- [ ] **Milestone name** - What your release is called in ClickUp (e.g., "3.0.0", "Q3 Release")
- [ ] **Code Freeze date** - When you stop adding features (e.g., "2026-06-02")
- [ ] **Submit date** - When you submit to app stores/QA (optional)
- [ ] **Go Live date** - When the release ships to production

### 3. Bug Status Mapping
- [ ] **Active statuses** - Which statuses count as "active" bugs? (e.g., "Open", "In Progress", "Ready for QA")
- [ ] **Excluded statuses** - Which statuses to ignore? (e.g., "Closed", "Won't Fix", "Duplicate")

### 4. Branding (Optional)
- [ ] **Team/Company name** - For the dashboard title
- [ ] **Logo file** - Path to your logo image (optional)
- [ ] **Color scheme** - Primary and accent colors (optional, defaults provided)

### 5. GitHub Setup
- [ ] **GitHub repository** - Create an empty repo for this dashboard
- [ ] **Repository name** - What you named it (e.g., "bug-burndown-v3")

---

## 🚀 Let's Build Your Dashboard

Once you have the information above, tell Claude:

> "I want to create a bug burndown dashboard for my release"

Claude will ask you questions to gather the details, then:
1. **Fetch your bug data** from ClickUp
2. **Calculate historical rates** from past releases (if available)
3. **Generate Python scripts** customized for your project
4. **Create the dashboard HTML** with your branding
5. **Set up GitHub Actions** for automatic updates
6. **Deploy to GitHub Pages**
7. **Generate Slack content** (optional)

**Estimated time**: 15-20 minutes

---

## 📊 Example: What Claude Will Ask

Here's a preview of the interactive setup:

```
Claude: "What's your ClickUp API token? I'll need this to fetch bug data."
You: [paste token]

Claude: "What's the milestone name in ClickUp for this release?"
You: "3.0.0 Global"

Claude: "When is Code Freeze?"
You: "2026-08-15"

Claude: "When is Go Live?"
You: "2026-09-01"

Claude: "Which bug statuses should count as 'active'?"
You: "Open, In Progress, Ready for QA, In QA"

Claude: "Which statuses should be excluded?"
You: "Closed, Won't Fix, Duplicate, Deferred"

Claude: "Great! I'll fetch your bugs and build the dashboard. This will take about 30 seconds..."
```

Claude will then generate all the files and explain what each one does.

---

## 📁 What Gets Created

Claude will create these files in your project:

### Core Scripts
- `calculate_burndown_projections.py` - Calculates the 3 projection lines
- `generate_burndown_projection_chart.py` - Creates the HTML dashboard
- `generate_slack_burndown.py` - Generates Slack content
- `update_today_burndown.py` - Quick daily update script

### Data Files
- `bugs_with_parsed_dates.json` - Your bug data from ClickUp
- `burndown_projections.json` - Current projections
- `milestone_dates_{your_release}.json` - Your milestone dates
- `historical_rate_analysis.json` - Historical burn rates

### Automation
- `.github/workflows/auto-update-dashboard.yml` - GitHub Actions (3x daily updates)

### Documentation
- `CLAUDE.md` - Complete project documentation
- `SETUP.md` - Setup guide
- `MAINTENANCE.md` - Daily/weekly operations
- `TROUBLESHOOTING.md` - Common issues
- `README.md` - Public-facing docs

### Output
- `docs/index.html` - Your live dashboard (GitHub Pages)
- `burndown_chart.png` - Slack-ready chart
- `slack_message.json` - Slack message content

---

## 🎨 Customization Options

Claude can customize:

### Visual Design
- Dashboard title (e.g., "MyApp 3.0 Bug Burndown")
- Color scheme (primary, accent colors)
- Logo integration
- Metric card labels

### Calculations
- Historical window (default: 6 months)
- Business days vs calendar days
- Custom bug filters
- Milestone markers

### Automation
- Update frequency (default: 3x daily at 7 AM, 12 PM, 4 PM)
- Weekday-only or 7 days a week
- Custom commit messages

**Just tell Claude what you want:**
> "Use our company colors: blue (#1E3A8A) and orange (#FB923C)"
> "Update 4 times a day instead of 3"
> "Include bugs from multiple milestones: 3.0.0 and 3.1.0"

---

## ✅ Prerequisites

Before starting, make sure you have:

- [ ] **Python 3.10+** installed (`python --version`)
- [ ] **Git** installed (`git --version`)
- [ ] **GitHub account** with repo created
- [ ] **ClickUp access** with API token
- [ ] **ClickUp bug data** tagged with milestones

**Don't have these?** Tell Claude what's missing:
> "I don't have Python installed"
> "I need help creating a GitHub repository"
> "I don't know how to get a ClickUp API token"

---

## 🆘 During Setup

If you get stuck at any point:

> "I'm not sure how to answer this question"
> "Where do I find my ClickUp Space ID?"
> "This error appeared: [paste error]"
> "Can you explain what you're asking for?"

Claude will help clarify and guide you through.

---

## 📚 After Setup

Once complete, you'll have:
1. **Live dashboard** on GitHub Pages
2. **Automatic updates** 3x daily
3. **Slack-ready content** for team updates
4. **Full documentation** for maintenance

**Maintenance**: Just check GitHub Actions weekly to ensure updates are running.

---

## 🔄 Multiple Releases

Need dashboards for multiple releases?

> "Create another dashboard for the 4.0.0 release"

Claude will:
- Use the same infrastructure
- Create separate projection files
- Generate a new dashboard
- Keep them independent

---

## 🌟 Based on Proven System

This is based on the **Spire 3.0.0 Bug Burndown Dashboard** that's been running successfully since May 2026:
- ✅ Zero-maintenance automation
- ✅ Accurate projections
- ✅ GitHub Pages deployment
- ✅ Slack integration
- ✅ Weekend-aware calculations

**See the original**: https://github.com/DaniloFortis/spire-burndown-3-0

---

## 🎯 Ready to Build Your Dashboard?

Open this file in Claude Code and say:

> "Help me create a bug burndown dashboard for my release"

Claude will take it from here! 🚀

---

## 💡 Tips

**Be ready with your ClickUp API token** - Claude will need it right away to fetch data.

**Have milestone dates handy** - Code Freeze and Go Live are the minimum needed.

**Know your bug statuses** - Which ones count as "active" vs "closed"?

**Don't worry about technical details** - Claude handles Python, Git, GitHub Actions, and deployment.

**Ask questions anytime** - Claude can explain what's happening at each step.

---

**Let's build your dashboard! Tell Claude you're ready to start. →**
