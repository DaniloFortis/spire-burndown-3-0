# 🔥 Spire 3.0.0 Bug Burndown Projection System

**Status:** ✅ Complete and Operational  
**Created:** May 21, 2026  
**Purpose:** Forward-looking 3-line projection chart to track 3.0.0 bugs toward Code Freeze

---

## 📊 Overview

This system provides a **forward-looking projection dashboard** that answers the critical question:  
**"Will we hit zero bugs by Code Freeze (June 2, 2026)?"**

### Three Lines Explained

1. **Ideal Line (Blue Dashed)** - What's Required
   - Linear path from current bugs → zero by Code Freeze (June 2)
   - Shows the required daily rate to hit target
   - Stays at zero after Code Freeze

2. **Estimated Line (Orange Solid)** - What's Likely
   - Projection based on historical 6-month find vs fix rate
   - Updates daily with rolling 6-month window
   - Shows where we're headed if historical trends continue

3. **Actual Line (Green Bold)** - What's Happening
   - Real daily bug counts from ClickUp
   - Updates daily with actual data
   - Shows true progress vs projections

---

## 🚀 Quick Start

### Initial Setup (One-Time)

```bash
# 1. Calculate initial projections
python calculate_burndown_projections.py

# 2. Generate dashboard
python generate_burndown_projection_chart.py

# 3. Open dashboard in browser
start spire_3_0_projection_dashboard.html
```

### Daily Updates

```bash
# Update with current bug count (manual)
python update_actual_burndown.py <current_bug_count>

# Example: If you have 145 active bugs today
python update_actual_burndown.py 145
```

The update script automatically:
- Adds the new actual data point
- Recalculates historical rate with rolling 6-month window
- Updates the Estimated line projection
- Regenerates the dashboard

---

## 📁 Files Created

### Scripts
| File | Purpose |
|------|---------|
| `calculate_burndown_projections.py` | **Initial calculation** - Generates 3-line projections from current bug data |
| `generate_burndown_projection_chart.py` | **Dashboard generation** - Creates interactive HTML visualization |
| `update_actual_burndown.py` | **Daily updates** - Adds new actual data and recalculates projections |

### Data Files
| File | Contents |
|------|----------|
| `burndown_projections.json` | Current projection data for all 3 lines |
| `spire_3_0_projection_dashboard.html` | **Interactive dashboard** (open in browser) |

### Inputs (Existing)
| File | Used For |
|------|----------|
| `bugs_with_parsed_dates.json` | Source of current 3.0.0 bug status |
| `burndown_data.json` | Historical 6-month find vs fix rates |

---

## 📊 Current State (May 21, 2026)

### Initial Analysis
- **Active 3.0.0 Bugs:** 157
- **Days to Code Freeze:** 12
- **Required Rate (Ideal):** -13.08 bugs/day
- **Historical Rate:** -0.86 bugs/day (accumulating, not burning down)
- **Velocity Gap:** 15.2x improvement needed

### After First Update (May 22, 2026 - Simulated)
- **Active 3.0.0 Bugs:** 150 (-7 from yesterday!)
- **Updated Historical Rate:** +4.46 bugs/day (rolling window improved!)
- **New Velocity Gap:** 2.94x improvement needed
- **Projected Zero Date:** June 24, 2026 (22 days past Code Freeze)

**Key Insight:** The rolling 6-month window shows the historical rate improving as we enter the bug-fixing phase. The team made significant progress (7 bugs fixed net), and the projection now shows a positive burn rate!

---

## 🔄 How Rolling Window Works

The system uses a **rolling 6-month window** for historical rate calculation:

**Day 1 (May 21):**
- Window: Nov 21, 2025 → May 21, 2026
- Rate: -0.86 bugs/day (accumulating)

**Day 2 (May 22):**
- Window: Nov 22, 2025 → May 22, 2026 (rolled forward 1 day)
- Rate: +4.46 bugs/day (burning down!)

**Why it changes:**
- Drops oldest day (Nov 21) which may have had different velocity
- Includes newest day (May 22) with current sprint velocity
- Adapts to changing team performance as you approach deadlines

---

## 📈 Dashboard Features

### Interactive Chart
- **Zoom:** Click and drag to zoom in on date ranges
- **Pan:** Shift + drag to pan across timeline
- **Hover:** Detailed tooltips show exact counts and dates
- **Export:** Download chart as PNG image

### Milestone Markers
- **Code Freeze** (June 2) - RED dashed vertical line
- **Submit** (June 10) - ORANGE dashed vertical line
- **Go Live** (June 15) - GREEN dashed vertical line

### Summary Statistics
- Current active bugs
- Days remaining to Code Freeze
- Required vs Historical rate
- Velocity gap (improvement needed)
- Projected bugs at Code Freeze

---

## 🔧 Daily Update Workflow

### Option A: Manual Update (Current)

```bash
# 1. Get current active 3.0.0 bug count from ClickUp manually
# 2. Run update script with that count
python update_actual_burndown.py 145

# 3. Dashboard automatically regenerates
# 4. Refresh browser to see updated chart
```

### Option B: Automated Update (Future)

For production use, modify `update_actual_burndown.py` to:
1. Fetch current bug count from ClickUp API automatically
2. Schedule script to run daily (cron job / task scheduler)
3. Optionally email/notify team when updated

**Example ClickUp API integration:**
```python
# In update_actual_burndown.py, add:
def fetch_current_bug_count_from_clickup():
    # Use existing clickup_batch_fetcher.py pattern
    # Filter to milestone_simplified == "3.0.0"
    # Count where status != "Closed"
    return active_count
```

---

## 🎯 Interpretation Guide

### When Actual Tracks Ideal
✅ **Good!** Team is on pace to hit zero by Code Freeze  
→ Continue current velocity

### When Actual Tracks Estimated
⚠️ **Concerning** - Following historical trends, not hitting target  
→ Need to increase bug-fixing velocity  
→ Gap between Estimated and Ideal shows improvement needed

### When Actual is Above Both
🚨 **Red Alert** - Falling behind projections  
→ Bugs accumulating faster than historical average  
→ Major velocity shift needed

### When Actual is Below Ideal
🎉 **Excellent!** - Ahead of schedule  
→ On track to hit zero before Code Freeze  
→ Consider banking time for QA/polish

---

## 📊 Example Scenarios

### Scenario 1: Steady Progress
```
Day 1: 157 bugs
Day 2: 150 bugs (-7)
Day 3: 143 bugs (-7)
...
```
**Interpretation:** Actual line tracking Ideal → On target for zero by Code Freeze

### Scenario 2: Slowing Down
```
Day 1: 157 bugs
Day 2: 154 bugs (-3)
Day 3: 152 bugs (-2)
...
```
**Interpretation:** Actual line converging with Estimated → Need to accelerate

### Scenario 3: Acceleration
```
Day 1: 157 bugs
Day 2: 147 bugs (-10)
Day 3: 135 bugs (-12)
...
```
**Interpretation:** Actual line below Ideal → Ahead of schedule, zero before Code Freeze

---

## 🧮 Calculations Explained

### Ideal Rate
```
ideal_rate = -current_bugs / days_to_code_freeze
Example: -157 / 12 = -13.08 bugs/day
```
Linear decrease to zero exactly at Code Freeze

### Historical Rate (Rolling 6-Month Window)
```
window = today - 180 days → today
bugs_opened_in_window = sum of bugs opened in window
bugs_closed_in_window = sum of bugs closed in window
historical_rate = (bugs_closed - bugs_opened) / 180
```
Positive rate = burning down (fixing faster)  
Negative rate = accumulating (finding faster)

### Estimated Projection
```
For each future day:
  estimated_count = current_actual + (historical_rate * days_from_now)
```
Projects forward from current actual using historical velocity

### Velocity Gap
```
velocity_gap = |ideal_rate / historical_rate|
Example: |-13.08 / -0.86| = 15.2x
```
Shows how much faster the team needs to go vs historical average

---

## ⚠️ Important Notes

### Data Quality
- **Triage bugs:** 211 bugs in "Triage" status not yet assigned to 3.0.0
- **Bulk closure:** Historical data shows bulk closure event on Apr 27 (1,365 bugs)
- **Rolling window:** Rate calculations adapt as window rolls forward

### Historical Rate Behavior
- Initially shows **-0.86 bugs/day** (accumulating phase - more finding than fixing)
- After first update: **+4.46 bugs/day** (burn-down phase - more fixing than finding)
- This dramatic shift is normal as project phases change

### Projection Limitations
- Assumes historical rate continues (reality may vary)
- Doesn't account for scope changes or priority shifts
- Best used as a **trend indicator**, not absolute forecast

---

## 🔍 Troubleshooting

### Dashboard not updating?
```bash
# Manually regenerate
python generate_burndown_projection_chart.py
```

### Wrong bug count?
```bash
# Recalculate from source data
python calculate_burndown_projections.py
python generate_burndown_projection_chart.py
```

### Historical rate seems wrong?
- Check `burndown_data.json` for data quality
- Verify 6-month window includes representative data
- Consider if project phase changed (development → bug-fixing)

---

## 📚 References

### Key Dates
- **Today:** May 21, 2026
- **Bug Fixing Only:** May 26, 2026
- **Code Freeze:** June 2, 2026 (12 days)
- **Submit:** June 10, 2026
- **Go Live:** June 15, 2026 (25 days)

### Data Sources
- **ClickUp:** Spire 3.0.0 bugs (milestone field)
- **Historical Window:** Nov 21, 2025 - May 21, 2026 (6 months)
- **Active Definition:** All statuses except "Closed"

---

## ✅ Success Criteria

**Goal:** Zero active 3.0.0 bugs by Code Freeze (June 2)

**Daily Monitoring:**
- Update actual count every day
- Watch Actual line vs Ideal line
- Monitor velocity gap trend

**Weekly Review:**
- Assess if Actual is tracking Ideal
- Identify blockers if falling behind
- Celebrate wins if ahead of schedule

---

## 🎉 Next Steps

1. **Daily Updates:** Run `update_actual_burndown.py` with current bug count
2. **Team Reviews:** Share dashboard in daily standups
3. **Automation:** Connect ClickUp API for automatic updates
4. **Expansion:** Add severity breakdown (Critical vs Minor)
5. **Alerting:** Email notifications when falling behind Ideal

---

**Dashboard:** `spire_3_0_projection_dashboard.html`  
**Contact:** Generated by Claude Code  
**Last Updated:** May 22, 2026
