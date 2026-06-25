#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calculate 3.0.0 Bug Burndown Projections

Generates three projection lines for 3.0.0 bugs:
1. Ideal: Linear decrease to zero by Code Freeze (June 2)
2. Estimated: Projection based on historical 6-month find vs fix rate
3. Actual: Current reality (starts with today, updates daily)

Output: burndown_projections.json
"""

import json
from datetime import datetime, timedelta
import sys

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Configuration
BUGS_FILE = "bugs_with_parsed_dates.json"
HISTORICAL_RATE_FILE = "historical_rate_analysis.json"
# Historical actuals file is now resolved dynamically (see _find_historical_actuals_file below)
HISTORICAL_ACTUALS_FILE = None
MILESTONE_DATES_FILE = "milestone_dates_3.0.0.json"
OUTPUT_FILE = "burndown_projections.json"


def _find_historical_actuals_file():
    """Find the most recent historical_actuals_*.json file in the working directory."""
    import glob
    candidates = sorted(glob.glob("historical_actuals_*.json"))
    return candidates[-1] if candidates else None


def load_milestone_dates():
    """Load milestone dates from milestone_dates_3.0.0.json (source of truth)."""
    with open(MILESTONE_DATES_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['3.0.0']['key_dates']


# Load milestone dates from JSON (single source of truth)
_milestone_dates = load_milestone_dates()

# Key Dates - now loaded from milestone_dates_3.0.0.json
# Chart starts when 3.0.0 tracking begins (kept in sync with first historical actual)
CHART_START = datetime(2026, 6, 11)
TODAY = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
CODE_FREEZE = datetime.strptime(_milestone_dates['code_freeze'], '%Y-%m-%d')
SUBMIT = datetime.strptime(_milestone_dates['submit'], '%Y-%m-%d')
GO_LIVE = datetime.strptime(_milestone_dates['go_live'], '%Y-%m-%d')

# Calculate business days to key milestones
def count_business_days(start_date, end_date):
    """Count business days (Mon-Fri) between two dates."""
    business_days = 0
    current = start_date
    while current < end_date:
        if current.weekday() < 5:  # Monday=0, Sunday=6
            business_days += 1
        current += timedelta(days=1)
    return business_days

# Days to key milestones (business days)
BUSINESS_DAYS_TO_CODE_FREEZE = count_business_days(TODAY, CODE_FREEZE)
DAYS_TO_GO_LIVE = (GO_LIVE - TODAY).days  # Keep calendar days for total projection length


def load_bug_data():
    """Load bug data from JSON file."""
    print(f"📂 Loading bug data from {BUGS_FILE}...")
    with open(BUGS_FILE, 'r', encoding='utf-8') as f:
        bugs = json.load(f)
    print(f"✅ Loaded {len(bugs)} bugs")
    return bugs


def load_historical_rate():
    """Load historical rate from analysis file."""
    print(f"📂 Loading historical rate from {HISTORICAL_RATE_FILE}...")
    with open(HISTORICAL_RATE_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"✅ Loaded historical rate: {data['historical_daily_rate']:.2f} bugs/day")
    return data


def load_historical_actuals():
    """Load historical actual bug counts from the latest historical_actuals_*.json file."""
    actuals_file = _find_historical_actuals_file()
    if actuals_file is None:
        print(f"⚠️  No historical_actuals_*.json file found, will start from today only")
        return None
    print(f"📂 Loading historical actuals from {actuals_file}...")
    try:
        with open(actuals_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        actuals = data['actuals']
        if actuals:
            print(f"✅ Loaded {len(actuals)} historical actual data points ({actuals[0]['date']} - {actuals[-1]['date']})")
        else:
            print(f"⚠️  Historical actuals file is empty")
        return actuals
    except FileNotFoundError:
        print(f"⚠️  Historical actuals file not found, will start from today only")
        return None


# Active statuses for math calculations (now INCLUDES "In QA" per updated requirement)
# Any bug not yet Closed/Won't Fix counts as active toward the burndown
ACTIVE_MATH_STATUSES = [
    'to-do',
    'reopened',
    'in progress',
    'design review',
    'art review',
    'code review',
    'build pending',
    'blocked',
    'need more info',
    'in qa'
]

# Statuses considered "non-active" (excluded from dashboard breakdown cards)
EXCLUDED_FROM_DASHBOARD = ['closed', "won't fix"]


def is_active_for_math(status):
    """Check if a bug status counts as active for math calculations (includes In QA)."""
    if not status:
        return False
    return status.lower().strip() in ACTIVE_MATH_STATUSES


def is_excluded_from_dashboard(status):
    """Check if a bug status should be hidden from dashboard breakdown (Closed/Won't Fix)."""
    if not status:
        return True
    return status.lower().strip() in EXCLUDED_FROM_DASHBOARD


def count_active_2_0_bugs(bugs):
    """
    Count current active 3.0.0 bugs using ACTIVE_MATH_STATUSES allowlist.
    Includes "In QA" per updated requirement (excludes only Closed and Won't Fix).

    Args:
        bugs: List of parsed bug dictionaries

    Returns:
        int: Count of active bugs
    """
    active_bugs = [
        bug for bug in bugs
        if bug.get('milestone_simplified') == '3.0.0'
        and is_active_for_math(bug.get('status'))
    ]

    print(f"\n📊 3.0.0 Bug Analysis:")
    print(f"   Total 3.0.0 bugs: {len([b for b in bugs if b.get('milestone_simplified') == '3.0.0'])}")
    print(f"   Active (includes In QA; excludes Closed, WON'T FIX): {len(active_bugs)}")

    # Show status breakdown
    status_counts = {}
    for bug in active_bugs:
        status = bug.get('status', 'unknown')
        status_counts[status] = status_counts.get(status, 0) + 1

    print(f"\n   Status breakdown:")
    for status, count in sorted(status_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"     - {status}: {count}")

    return len(active_bugs)


def get_status_breakdown(bugs):
    """
    Get count of bugs for each status (for dashboard cards).
    Includes In QA but excludes Closed and WON'T FIX.
    Only returns statuses with 1+ bugs.

    Args:
        bugs: List of parsed bug dictionaries

    Returns:
        dict: {status_name: count} sorted by count descending
    """
    milestone_bugs = [
        bug for bug in bugs
        if bug.get('milestone_simplified') == '3.0.0'
        and not is_excluded_from_dashboard(bug.get('status'))
    ]

    status_counts = {}
    for bug in milestone_bugs:
        status = bug.get('status', 'unknown')
        status_counts[status] = status_counts.get(status, 0) + 1

    # Sort by count descending and only include statuses with 1+ bugs
    return {
        status: count
        for status, count in sorted(status_counts.items(), key=lambda x: x[1], reverse=True)
        if count > 0
    }


def calculate_actual_2_0_rate(bugs):
    """
    Calculate actual rate for 3.0.0 bugs specifically.

    Measures fix vs find rate for 3.0.0 bugs in the current period.
    Uses same methodology as historical rate but only for 3.0.0 milestone.

    Args:
        bugs: List of parsed bug dictionaries

    Returns:
        float: Daily net rate for 3.0.0 bugs
    """
    # Get all 3.0.0 bugs
    milestone_3_0 = [b for b in bugs if b.get('milestone_simplified') == '3.0.0']

    # 3.0.0 milestone window starts at Feature Complete (2026-06-18)
    milestone_start = datetime(2026, 6, 18)
    milestone_end = TODAY
    days_in_period = (milestone_end - milestone_start).days

    # Bugs found during this period
    bugs_found = []
    for bug in milestone_3_0:
        if bug.get('date_created'):
            created = datetime.fromisoformat(bug['date_created'])
            if milestone_start <= created <= milestone_end:
                bugs_found.append(bug)

    # Bugs fixed (currently Closed)
    bugs_fixed = [b for b in milestone_3_0 if b.get('status') == 'Closed']

    # Net bugs removed
    net_bugs_removed = len(bugs_fixed) - len(bugs_found)

    # Daily rate
    actual_rate = net_bugs_removed / days_in_period if days_in_period > 0 else 0

    print(f"\n📊 Actual 3.0.0 Rate Calculation:")
    print(f"   Period: {milestone_start.strftime('%b %d')} to {milestone_end.strftime('%b %d, %Y')} ({days_in_period} days)")
    print(f"   Bugs found in period: {len(bugs_found)}")
    print(f"   Bugs fixed (Closed): {len(bugs_fixed)}")
    print(f"   Net bugs removed: {net_bugs_removed:+d}")
    print(f"   Actual daily rate: {actual_rate:+.2f} bugs/day")

    if actual_rate > 0:
        print(f"   ✅ Burning down (fixing faster than finding)")
    elif actual_rate < 0:
        print(f"   ⚠️  Accumulating (finding faster than fixing)")
    else:
        print(f"   ➖ Stable (no net change)")

    return actual_rate




def generate_ideal_line(chart_start_count, chart_start_date, code_freeze_date, business_days_from_start_to_freeze):
    """
    Generate Ideal projection line: Linear decrease to zero by Code Freeze.

    Starts from chart start date (May 11) with the historical count at that time,
    and shows linear path to zero by Code Freeze. Stops at Code Freeze (no line continuation).

    Args:
        chart_start_count: Bug count at chart start (e.g., 201 on May 11)
        chart_start_date: Start date for chart (e.g., May 11)
        code_freeze_date: Code Freeze date (target zero)
        business_days_from_start_to_freeze: Business days from chart start to Code Freeze

    Returns:
        tuple: (ideal_line list, ideal_rate_per_day)
    """
    # Calculate ideal rate based on BUSINESS days from chart start to Code Freeze
    ideal_rate_per_day = -chart_start_count / business_days_from_start_to_freeze

    print(f"\n📉 Ideal Line Calculation:")
    print(f"   Starting: {chart_start_date.strftime('%B %d, %Y')} with {chart_start_count} bugs")
    print(f"   Target: Zero bugs by {code_freeze_date.strftime('%B %d, %Y')}")
    print(f"   Business days to Code Freeze: {business_days_from_start_to_freeze}")
    print(f"   Required rate: {ideal_rate_per_day:.2f} bugs/day")

    ideal_line = []
    current_date = chart_start_date
    business_days_elapsed = 0
    last_business_day_count = chart_start_count

    # Generate line from chart start until it reaches zero or Code Freeze
    while current_date <= code_freeze_date:
        is_weekend = current_date.weekday() >= 5  # Saturday=5, Sunday=6

        if is_weekend:
            # Weekend: plateau at last business day's count
            count = last_business_day_count
        else:
            # Business day: calculate progress
            count = chart_start_count + (ideal_rate_per_day * business_days_elapsed)
            last_business_day_count = count
            business_days_elapsed += 1

        # If count would go negative, set to 0 and stop
        if count <= 0:
            ideal_line.append({
                "date": current_date.strftime('%Y-%m-%d'),
                "count": 0
            })
            print(f"   Ideal line reaches zero on {current_date.strftime('%B %d, %Y')}")
            break  # Stop rendering after reaching zero

        ideal_line.append({
            "date": current_date.strftime('%Y-%m-%d'),
            "count": round(count, 2)
        })

        current_date += timedelta(days=1)

    return ideal_line, ideal_rate_per_day


def calculate_rate_from_actual_data(actual_line_data):
    """
    Calculate burndown rate from last 10 business days of actual data.

    Args:
        actual_line_data: List of actual data points

    Returns:
        float: Daily rate from last 10 business days, or None if not enough data
    """
    from datetime import datetime

    # Count business days in actual data
    business_days_data = []
    for i, point in enumerate(actual_line_data):
        date = datetime.strptime(point['date'], '%Y-%m-%d')
        if date.weekday() < 5:  # Monday=0, Friday=4
            business_days_data.append({
                'date': date,
                'count': point['count'],
                'index': i
            })

    total_business_days = len(business_days_data)

    print(f"\n📊 Actual Data Rate Calculation:")
    print(f"   Total actual data points: {len(actual_line_data)}")
    print(f"   Business days in actual data: {total_business_days}")

    # Need at least 10 business days to calculate
    if total_business_days < 10:
        print(f"   ⚠️  Not enough business days (<10), using historical rate")
        return None

    # Get last 10 business days
    last_10 = business_days_data[-10:]
    start_count = last_10[0]['count']
    end_count = last_10[-1]['count']
    net_change = end_count - start_count
    rate = net_change / 10

    print(f"   ✅ Using last 10 business days of actual data:")
    print(f"      Start: {last_10[0]['date'].strftime('%b %d')} = {start_count} bugs")
    print(f"      End: {last_10[-1]['date'].strftime('%b %d')} = {end_count} bugs")
    print(f"      Net change: {net_change:+.0f} bugs over 10 business days")
    print(f"      Calculated rate: {rate:+.2f} bugs/day")

    return rate


def generate_estimated_line(actual_line_data, end_date, historical_rate):
    """
    Generate Estimated projection line: Starts from last actual data point.

    Projects forward from the last actual data point using either:
    - Historical rate (if < 10 business days of actual data)
    - Rate calculated from last 10 business days (if >= 10 business days)

    Args:
        actual_line_data: List of actual data points
        end_date: Final date for projection (Go Live)
        historical_rate: Historical daily net rate (fallback)

    Returns:
        tuple: (estimated_line, rate_used, rate_source)
            - estimated_line: List of {"date": "YYYY-MM-DD", "count": float} dictionaries
            - rate_used: The rate used for projection (float)
            - rate_source: Description of rate source (string)
    """
    # Get last actual point as starting point for estimated line
    last_actual = actual_line_data[-1]
    start_count = last_actual['count']
    start_date = datetime.strptime(last_actual['date'], '%Y-%m-%d')

    # Try to calculate rate from actual data
    actual_rate = calculate_rate_from_actual_data(actual_line_data)

    # Use actual rate if available, otherwise fall back to historical
    rate = actual_rate if actual_rate is not None else historical_rate
    rate_source = "last 10 business days" if actual_rate is not None else "historical average"

    print(f"\n📊 Estimated Line Calculation:")
    print(f"   Starting: {start_date.strftime('%b %d')} with {start_count} bugs (last actual point)")
    print(f"   Rate: {rate:.2f} bugs/day ({rate_source})")

    estimated_line = []

    # Include the last actual point as first point to create seamless connection
    estimated_line.append({
        "date": start_date.strftime('%Y-%m-%d'),
        "count": start_count
    })

    current_date = start_date + timedelta(days=1)  # Continue from day after
    business_days_elapsed = 0
    last_business_day_count = start_count

    while current_date <= end_date:
        is_weekend = current_date.weekday() >= 5  # Saturday=5, Sunday=6

        if is_weekend:
            # Weekend: plateau at last business day's count
            count = last_business_day_count
        else:
            # Business day: calculate progress
            business_days_elapsed += 1
            count = start_count + (rate * business_days_elapsed)
            last_business_day_count = count

        # If count would go negative, set to 0 and stop
        if count <= 0:
            estimated_line.append({
                "date": current_date.strftime('%Y-%m-%d'),
                "count": 0
            })
            print(f"   Estimated line reaches zero on {current_date.strftime('%B %d, %Y')}")
            break  # Stop rendering after reaching zero

        estimated_line.append({
            "date": current_date.strftime('%Y-%m-%d'),
            "count": round(count, 2)
        })

        current_date += timedelta(days=1)

    # If line never reached zero, report it
    if current_date > end_date and count > 0:
        print(f"   ⚠️  Projected to never reach zero within projection window")

    return estimated_line, rate, rate_source


def generate_actual_line(historical_actuals, starting_count, today):
    """
    Generate Actual line from historical actuals + current real-time count for today.

    The historical actuals show "active at start of day" for each date.
    For today specifically, we override with the current real-time count so the
    Active Bugs card always matches the chart's last data point.

    Args:
        historical_actuals: List of historical actual data points (or None)
        starting_count: Current active bug count (as of today, real-time)
        today: Today's date

    Returns:
        list: List of {"date": "YYYY-MM-DD", "count": int} dictionaries
    """
    print(f"\n✅ Actual Line:")

    if historical_actuals:
        today_str = today.strftime('%Y-%m-%d')

        # Copy historical actuals and override today's value with real-time count
        actual_line = [dict(p) for p in historical_actuals]
        today_point_idx = next(
            (i for i, p in enumerate(actual_line) if p['date'] == today_str),
            None
        )

        if today_point_idx is not None:
            old_count = actual_line[today_point_idx]['count']
            actual_line[today_point_idx]['count'] = starting_count
            print(f"   Overriding today's historical count ({old_count}) with real-time count ({starting_count})")
        else:
            # Today isn't in historical actuals, append it
            actual_line.append({"date": today_str, "count": starting_count})
            print(f"   Appending today's real-time count: {starting_count}")

        print(f"   Using historical actuals: {len(actual_line)} data points")
        print(f"   Starting: {actual_line[0]['count']} bugs on {actual_line[0]['date']}")
        print(f"   Current: {actual_line[-1]['count']} bugs on {actual_line[-1]['date']}")
        return actual_line
    else:
        # Fallback: just use today's count
        print(f"   Starting point: {starting_count} bugs on {today.strftime('%B %d, %Y')}")
        print(f"   (Will be updated daily with real data)")
        return [{
            "date": today.strftime('%Y-%m-%d'),
            "count": starting_count
        }]


def save_projections(projections, output_file):
    """Save projection data to JSON file."""
    print(f"\n💾 Saving projections to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(projections, f, indent=2)
    print(f"✅ Saved successfully!")


def main():
    """Main execution function."""
    print("🚀 Calculating 3.0.0 Bug Burndown Projections")
    print("="*60)

    # Load data
    bugs = load_bug_data()
    historical_rate_data = load_historical_rate()
    historical_actuals = load_historical_actuals()

    # Calculate current active count
    active_count = count_active_2_0_bugs(bugs)

    # Get status breakdown for dashboard cards (includes In QA, excludes Closed/Won't Fix)
    status_breakdown = get_status_breakdown(bugs)
    print(f"\n📋 Status Breakdown for Dashboard:")
    for status, count in status_breakdown.items():
        print(f"   {status}: {count}")

    # Get historical rate from analysis (for reference)
    historical_rate = historical_rate_data['historical_daily_rate']

    # Calculate actual rate for 3.0.0 bugs specifically
    actual_2_0_rate = calculate_actual_2_0_rate(bugs)

    # Get chart start count from historical actuals
    chart_start_count = historical_actuals[0]['count'] if historical_actuals else active_count

    # Calculate business days from chart start to Code Freeze
    business_days_from_start_to_freeze = count_business_days(CHART_START, CODE_FREEZE)

    print(f"\n📊 Chart Configuration:")
    print(f"   Chart starts: {CHART_START.strftime('%b %d')} with {chart_start_count} bugs")
    print(f"   Today: {TODAY.strftime('%b %d')} with {active_count} bugs")
    print(f"   Business days from start to Code Freeze: {business_days_from_start_to_freeze}")
    print(f"   Business days from today to Code Freeze: {BUSINESS_DAYS_TO_CODE_FREEZE}")

    # Generate actual line first (needed for estimated line)
    actual_line = generate_actual_line(historical_actuals, active_count, TODAY)

    # Generate projection lines
    ideal_line, ideal_rate_from_start = generate_ideal_line(
        chart_start_count, CHART_START, CODE_FREEZE, business_days_from_start_to_freeze
    )

    # Also calculate the rate required FROM TODAY (for dashboard metrics)
    # Guard against division by zero on/after Code Freeze day
    if BUSINESS_DAYS_TO_CODE_FREEZE > 0:
        ideal_rate_from_today = -active_count / BUSINESS_DAYS_TO_CODE_FREEZE
    else:
        # On or past Code Freeze: all remaining bugs need to be fixed immediately
        # Use -active_count as the rate (1 day's worth needed today)
        ideal_rate_from_today = -float(active_count) if active_count > 0 else 0.0

    # Generate estimated line starting from last actual point
    estimated_line, estimated_line_rate, estimated_line_rate_source = generate_estimated_line(
        actual_line, GO_LIVE, historical_rate
    )

    print(f"\n📊 Rate Comparison:")
    print(f"   Ideal rate from chart start ({CHART_START.strftime('%b %d')}): {ideal_rate_from_start:.2f} bugs/day")
    print(f"   Ideal rate from today ({TODAY.strftime('%b %d')}): {ideal_rate_from_today:.2f} bugs/day (what's needed NOW)")

    # Build output structure
    projections = {
        "generated_date": TODAY.strftime('%Y-%m-%d'),
        "generated_timestamp": datetime.now().isoformat(),
        "chart_start_date": CHART_START.strftime('%Y-%m-%d'),
        "chart_start_bug_count": chart_start_count,
        "current_active_bugs": active_count,
        "status_breakdown": status_breakdown,  # All non-Closed/Won't Fix statuses with counts
        "historical_daily_rate": round(historical_rate, 2),  # Kept for reference
        "actual_2_0_rate": round(actual_2_0_rate, 2),  # Actual rate for 3.0.0 bugs
        "ideal_rate_per_day": round(ideal_rate_from_today, 2),  # Required rate from TODAY
        "ideal_rate_from_start": round(ideal_rate_from_start, 2),  # Rate from chart start (for line)
        "estimated_line_rate": round(estimated_line_rate, 2),  # Rate used for estimated line
        "estimated_line_rate_source": estimated_line_rate_source,  # Source of estimated rate
        "business_days_to_code_freeze": BUSINESS_DAYS_TO_CODE_FREEZE,  # Business days from TODAY
        "calendar_days_to_code_freeze": (CODE_FREEZE - TODAY).days,  # Calendar days for reference
        "days_to_go_live": DAYS_TO_GO_LIVE,
        "key_dates": {
            "chart_start": CHART_START.strftime('%Y-%m-%d'),
            "today": TODAY.strftime('%Y-%m-%d'),
            "code_freeze": CODE_FREEZE.strftime('%Y-%m-%d'),
            "submit": SUBMIT.strftime('%Y-%m-%d'),
            "go_live": GO_LIVE.strftime('%Y-%m-%d')
        },
        "projections": {
            "ideal": ideal_line,
            "estimated": estimated_line,
            "actual": actual_line
        },
        "metrics": {
            "velocity_gap": round(abs(ideal_rate_from_today / actual_2_0_rate), 2) if actual_2_0_rate != 0 else float('inf'),
            "on_track": actual_2_0_rate > abs(ideal_rate_from_today)
        }
    }

    # Save to file
    save_projections(projections, OUTPUT_FILE)

    # Print summary
    print("\n" + "="*60)
    print("📊 PROJECTION SUMMARY")
    print("="*60)
    print(f"Chart Start ({CHART_START.strftime('%b %d')}): {chart_start_count} bugs")
    print(f"Current Active Bugs ({TODAY.strftime('%b %d')}): {active_count}")
    print(f"Business Days to Code Freeze: {BUSINESS_DAYS_TO_CODE_FREEZE}")
    print(f"\nRequired Rate from TODAY: {ideal_rate_from_today:.2f} bugs/day")
    print(f"Actual 3.0.0 Rate: {actual_2_0_rate:+.2f} bugs/day")
    print(f"Historical Rate (reference): {historical_rate:.2f} bugs/day")

    if actual_2_0_rate != 0:
        velocity_gap = abs(ideal_rate_from_today / actual_2_0_rate)
        print(f"\nVelocity Gap: {velocity_gap:.1f}x improvement needed")
        if actual_2_0_rate > abs(ideal_rate_from_today):
            print(f"✅ On track to hit Code Freeze target!")
        else:
            print(f"⚠️  Need to accelerate to hit Code Freeze target")
    else:
        print(f"⚠️  Actual rate is zero (stable, no net change)")

    print(f"\nProjections saved to: {OUTPUT_FILE}")
    print("✅ Ready to generate dashboard!")


if __name__ == "__main__":
    main()
