# Spire 3.0.0 Bug Burndown Dashboard

Interactive bug burndown projection dashboard for the Spire 3.0.0 release.

**👋 Setting up for the first time?** Start with [GET_STARTED.md](GET_STARTED.md) - Load this file in Claude Code and Claude will clone and set up everything for you!

**👋 Already cloned?** Open [CLAUDE.md](CLAUDE.md) in Claude Code for complete project documentation and guidance!

## 📊 Live Dashboard

**🔗 https://DaniloFortis.github.io/spire-burndown-3-0/**

View the interactive dashboard with real-time bug projections, weekend plateaus, and milestone tracking.

## 🎯 What It Shows

- **Ideal Line** (Black): Required burn rate to hit zero bugs by Code Freeze (June 2, 2026)
- **Estimated Line** (Orange): Projected trajectory based on historical or recent performance
- **Actual Line** (Green): Real daily bug counts from ClickUp

### Key Features

- Weekend plateaus (no progress on Sat/Sun)
- Auto-switching rate calculation (historical → last 10 business days)
- Milestone markers for Code Freeze, Submit, and Go Live
- Real-time metrics: Active bugs, required rate, velocity gap

## 🔧 How It Works

### Automated Updates (3x Daily)

The dashboard **automatically updates** via GitHub Actions at:
- **7:00 AM PT** - Morning update before standup
- **12:00 PM PT** - Midday check-in
- **4:00 PM PT** - End-of-day snapshot

Each run:
1. Counts current active 3.0.0 bugs
2. Updates actual line with today's count
3. Recalculates projections
4. Regenerates dashboard + Slack content
5. Auto-commits and pushes to GitHub
6. GitHub Pages deploys in 1-2 minutes

**No manual intervention required!** The dashboard stays current throughout the workday.

### Manual Process

1. **Data Collection**: Fetches bug data from ClickUp
2. **Rate Calculation**: Analyzes historical performance (6-month window)
3. **Projection**: Generates three projection lines with weekend awareness
4. **Dashboard**: Creates interactive Plotly chart with Twilight Towers branding

## 📁 Files

- `calculate_burndown_projections.py` - Generates projection data
- `generate_burndown_projection_chart.py` - Creates HTML dashboard
- `calculate_historical_actuals.py` - Retroactive daily counts (May 11-21)
- `calculate_historical_rate.py` - Historical burndown rate from past releases
- `docs/index.html` - GitHub Pages dashboard (auto-published)

## 🚀 Usage

### Generate Dashboard Locally

```bash
# Calculate projections
python calculate_burndown_projections.py

# Generate dashboard
python generate_burndown_projection_chart.py

# Open spire_3_0_projection_dashboard.html in browser
```

### Update Data

```bash
# Future: Automated daily updates via update_actual_burndown.py
python update_actual_burndown.py
```

## 📅 Milestone Dates

- **Code Freeze**: June 2, 2026
- **Submit**: June 10, 2026
- **Go Live**: June 15, 2026

## 🏢 Twilight Towers Branding

Dashboard features custom Twilight Towers visual identity:
- Purple gradient background (#3B2A5C → #2A1F42)
- Gold accents (#F4C542)
- Logo integration

## 🔄 Use This for Your Own Release

**This repository is also a reusable tool!** Other teams can create their own bug burndown dashboards in ~15 minutes.

### For Other Teams

Download [CREATE_BURNDOWN_DASHBOARD.md](CREATE_BURNDOWN_DASHBOARD.md) and load it in Claude Code:

```
"Help me create a bug burndown dashboard for my release"
```

Claude will:
- Ask for your ClickUp data and milestone dates
- Generate all Python scripts customized for your project
- Set up GitHub Actions automation
- Deploy your dashboard to GitHub Pages
- Create complete documentation

**See [SHARE_WITH_TEAMS.md](SHARE_WITH_TEAMS.md) for instructions on sharing this tool.**

---

*Generated with Claude Code*
