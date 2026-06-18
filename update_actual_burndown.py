#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Update Actual Burndown Line with Daily Data

This script updates the projection chart with new actual bug counts:
1. Adds new actual data point
2. Recalculates historical rate with rolling 6-month window
3. Recalculates estimated line from new actual position
4. Regenerates dashboard

Usage:
    python update_actual_burndown.py <current_bug_count>

Example:
    python update_actual_burndown.py 145

For production use, this would fetch the count from ClickUp API automatically.
"""

import json
import sys
from datetime import datetime, timedelta
import subprocess

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Configuration
PROJECTIONS_FILE = "burndown_projections.json"
BUGS_FILE = "bugs_with_parsed_dates.json"
BURNDOWN_DATA_FILE = "burndown_data.json"
DASHBOARD_SCRIPT = "generate_burndown_projection_chart.py"


def load_json(filepath):
    """Load JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(filepath, data):
    """Save JSON file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def get_next_date(projections):
    """
    Get the next date to update (tomorrow from last actual point).

    Args:
        projections: Projection data dictionary

    Returns:
        datetime: Next date to add
    """
    actual_line = projections['projections']['actual']
    last_actual_date = datetime.strptime(actual_line[-1]['date'], '%Y-%m-%d')
    next_date = last_actual_date + timedelta(days=1)
    return next_date


def calculate_rolling_6month_rate(burndown_data, current_date):
    """
    Calculate historical rate with rolling 6-month window.

    Rolling window: current_date - 180 days → current_date

    Args:
        burndown_data: Historical burndown metrics
        current_date: Current date for window end

    Returns:
        float: Daily net rate (bugs per day)
    """
    window_start = current_date - timedelta(days=180)

    print(f"\n📊 Calculating rolling 6-month rate:")
    print(f"   Window: {window_start.strftime('%b %d, %Y')} → {current_date.strftime('%b %d, %Y')}")

    # Filter to rolling window
    bugs_opened_in_window = sum(
        count for date_str, count in burndown_data['bugs_opened_by_date'].items()
        if window_start <= datetime.strptime(date_str, '%Y-%m-%d') <= current_date
    )

    bugs_closed_in_window = sum(
        count for date_str, count in burndown_data['bugs_closed_by_date'].items()
        if window_start <= datetime.strptime(date_str, '%Y-%m-%d') <= current_date
    )

    # Calculate net rate
    net_change = bugs_closed_in_window - bugs_opened_in_window
    net_rate = net_change / 180

    print(f"   Bugs opened: {bugs_opened_in_window}")
    print(f"   Bugs closed: {bugs_closed_in_window}")
    print(f"   Net change: {net_change}")
    print(f"   Daily rate: {net_rate:.2f} bugs/day")

    return net_rate


def recalculate_estimated_line(current_count, current_date, end_date, historical_rate):
    """
    Recalculate estimated line from current actual position.

    Args:
        current_count: Current actual bug count
        current_date: Current date (starting point)
        end_date: Final projection date (Go Live)
        historical_rate: Updated historical rate

    Returns:
        list: New estimated projection line
    """
    print(f"\n📈 Recalculating Estimated line:")
    print(f"   Starting from: {current_count} bugs on {current_date.strftime('%b %d')}")
    print(f"   Historical rate: {historical_rate:.2f} bugs/day")

    estimated_line = []
    projection_date = current_date

    while projection_date <= end_date:
        days_elapsed = (projection_date - current_date).days
        count = current_count + (historical_rate * days_elapsed)
        count = max(0, count)  # Don't allow negative

        estimated_line.append({
            "date": projection_date.strftime('%Y-%m-%d'),
            "count": round(count, 2)
        })

        projection_date += timedelta(days=1)

    # Find projected zero date
    if historical_rate > 0:
        days_to_zero = current_count / historical_rate
        zero_date = current_date + timedelta(days=days_to_zero)
        print(f"   Projected zero: {zero_date.strftime('%b %d, %Y')} ({days_to_zero:.1f} days)")
    else:
        print(f"   ⚠️  Projected to never reach zero (accumulating)")

    return estimated_line


def update_projections(current_bug_count):
    """
    Update projections with new actual data.

    Args:
        current_bug_count: Current active 3.0.0 bug count

    Returns:
        dict: Updated projection data
    """
    print(f"\n🔄 Updating projections with new data...")
    print(f"   New bug count: {current_bug_count}")

    # Load existing projections
    projections = load_json(PROJECTIONS_FILE)

    # Get next date
    next_date = get_next_date(projections)
    print(f"   Adding point for: {next_date.strftime('%B %d, %Y')}")

    # Check if we're past the end date
    end_date = datetime.strptime(projections['key_dates']['go_live'], '%Y-%m-%d')
    if next_date > end_date:
        print(f"   ⚠️  Next date ({next_date.strftime('%b %d')}) is past Go Live ({end_date.strftime('%b %d')})")
        print(f"   Adding point anyway for tracking purposes")

    # Add new actual point
    projections['projections']['actual'].append({
        "date": next_date.strftime('%Y-%m-%d'),
        "count": current_bug_count
    })

    print(f"   ✅ Added actual point")

    # Load burndown data for rolling window calculation
    burndown_data = load_json(BURNDOWN_DATA_FILE)

    # Recalculate historical rate with rolling window
    new_historical_rate = calculate_rolling_6month_rate(burndown_data, next_date)

    # Update historical rate in projections
    projections['historical_daily_rate'] = round(new_historical_rate, 2)

    # Recalculate estimated line from current actual position
    new_estimated_line = recalculate_estimated_line(
        current_bug_count,
        next_date,
        end_date,
        new_historical_rate
    )

    # Replace estimated line
    projections['projections']['estimated'] = new_estimated_line

    # Update metadata
    projections['last_updated'] = datetime.now().isoformat()
    projections['current_active_bugs'] = current_bug_count

    # Recalculate velocity gap
    ideal_rate = projections['ideal_rate_per_day']
    velocity_gap = abs(ideal_rate / new_historical_rate) if new_historical_rate != 0 else float('inf')
    projections['metrics']['velocity_gap'] = round(velocity_gap, 2)
    projections['metrics']['on_track'] = new_historical_rate > abs(ideal_rate)

    print(f"\n   ✅ Updated estimated line with new historical rate")

    return projections


def regenerate_dashboard():
    """Regenerate dashboard HTML with updated data."""
    print(f"\n🎨 Regenerating dashboard...")

    try:
        result = subprocess.run(
            ['python', DASHBOARD_SCRIPT],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"   ✅ Dashboard regenerated successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Error regenerating dashboard:")
        print(f"   {e.stderr}")
        return False


def main():
    """Main execution function."""
    print("🚀 Update Actual Burndown Data")
    print("="*60)

    # Get current bug count from command line
    if len(sys.argv) < 2:
        print("❌ Error: Missing current bug count argument")
        print("\nUsage: python update_actual_burndown.py <current_bug_count>")
        print("Example: python update_actual_burndown.py 145")
        sys.exit(1)

    try:
        current_bug_count = int(sys.argv[1])
    except ValueError:
        print(f"❌ Error: Invalid bug count '{sys.argv[1]}' (must be an integer)")
        sys.exit(1)

    if current_bug_count < 0:
        print(f"❌ Error: Bug count cannot be negative")
        sys.exit(1)

    # Update projections
    try:
        updated_projections = update_projections(current_bug_count)

        # Save updated projections
        print(f"\n💾 Saving updated projections...")
        save_json(PROJECTIONS_FILE, updated_projections)
        print(f"   ✅ Saved to {PROJECTIONS_FILE}")

        # Regenerate dashboard
        if regenerate_dashboard():
            print("\n" + "="*60)
            print("✅ UPDATE COMPLETE!")
            print("="*60)
            print(f"\nUpdated actual bug count to: {current_bug_count}")
            print(f"New historical rate: {updated_projections['historical_daily_rate']:.2f} bugs/day")
            print(f"\n🎯 Open spire_3_0_projection_dashboard.html to see updated chart")
        else:
            print("\n⚠️  Update complete but dashboard regeneration failed")
            print("Run: python generate_burndown_projection_chart.py")

    except FileNotFoundError as e:
        print(f"\n❌ Error: Required file not found: {e}")
        print("Make sure you've run calculate_burndown_projections.py first")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
