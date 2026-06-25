#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calculate Historical Daily Bug Counts (5/11 - 5/21)

Retroactively calculates daily active bug counts for 3.0.0
by examining created/closed dates in bug data.

For each day, count bugs that:
- Were created on or before that date
- Were NOT closed before that date (still active)

Output: Historical actual counts for 5/11 through 5/21
"""

import json
from datetime import datetime, timedelta
from collections import defaultdict
import sys

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Configuration
BUGS_FILE = "bugs_with_parsed_dates.json"
# Output file is named based on the date range (auto-generated)
OUTPUT_FILE = "historical_actuals_06_11_to_06_18.json"

# Date range — chart starts on Thu Jun 11 (one week before 3.0.0 Feature Complete)
START_DATE = datetime(2026, 6, 11)
END_DATE = datetime(2026, 6, 18)

# Active statuses for math calculations (now INCLUDES "In QA" per updated requirement)
# A bug currently in one of these statuses is considered active for math purposes
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


def is_active_for_math(status):
    """Check if a bug status counts as active for math calculations (includes In QA)."""
    if not status:
        return False
    return status.lower().strip() in ACTIVE_MATH_STATUSES


def load_bugs():
    """Load bug data from JSON file."""
    print(f"📂 Loading bugs from {BUGS_FILE}...")
    with open(BUGS_FILE, 'r', encoding='utf-8') as f:
        bugs = json.load(f)
    print(f"✅ Loaded {len(bugs)} bugs")
    return bugs


def calculate_daily_counts(bugs, start_date, end_date):
    """
    Calculate active bug count for each day in the range.

    For each day, count 3.0.0 bugs that:
    - Were created on or before that date
    - Were NOT closed before that date

    Args:
        bugs: List of bug dictionaries
        start_date: First date to calculate
        end_date: Last date to calculate

    Returns:
        dict: {date_str: count} for each day
    """
    print(f"\n📊 Calculating daily counts from {start_date.strftime('%b %d')} to {end_date.strftime('%b %d, %Y')}...")
    print(f"   Including 'In QA' in active math (per updated requirement)")

    # Filter to 3.0.0 bugs that are currently active for math
    # (includes In QA; excludes Closed and Won't Fix)
    milestone_3_0_active = [
        bug for bug in bugs
        if bug.get('milestone_simplified') == '3.0.0'
        and (
            # Either the bug is currently active (for math)
            is_active_for_math(bug.get('status'))
            # OR the bug is now closed (we still need to count it on dates before it closed)
            or bug.get('status', '').lower().strip() == 'closed'
        )
    ]

    print(f"   Total 3.0.0 bugs (after filter): {len(milestone_3_0_active)}")

    daily_counts = {}
    current_date = start_date

    while current_date <= end_date:
        # Count active bugs on this date
        active_on_date = []

        for bug in milestone_3_0_active:
            # Parse dates
            date_created_str = bug.get('date_created')
            date_closed_str = bug.get('date_closed')

            if not date_created_str:
                continue  # Skip bugs without creation date

            date_created = datetime.fromisoformat(date_created_str)

            # Was this bug created by this date?
            if date_created > current_date:
                continue  # Not created yet

            # Was this bug already closed by this date?
            if date_closed_str:
                date_closed = datetime.fromisoformat(date_closed_str)
                if date_closed < current_date:
                    continue  # Already closed

            # Bug was active on this date
            active_on_date.append(bug)

        daily_counts[current_date.strftime('%Y-%m-%d')] = len(active_on_date)

        print(f"   {current_date.strftime('%b %d')}: {len(active_on_date)} active bugs")

        current_date += timedelta(days=1)

    return daily_counts


def save_results(daily_counts, output_file):
    """Save historical actuals to JSON file."""
    # Convert to list format for easy use in projections
    actuals = []
    for date_str, count in sorted(daily_counts.items()):
        actuals.append({
            "date": date_str,
            "count": count
        })

    output = {
        "calculated_date": datetime.now().isoformat(),
        "method": "Retroactive calculation from bug created/closed dates",
        "start_date": START_DATE.strftime('%Y-%m-%d'),
        "end_date": END_DATE.strftime('%Y-%m-%d'),
        "days_included": len(actuals),
        "actuals": actuals
    }

    print(f"\n💾 Saving to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)
    print(f"✅ Saved {len(actuals)} daily counts")


def main():
    """Main execution."""
    print("🔍 Calculating Historical Daily Bug Counts")
    print("="*60)
    print(f"Date range: {START_DATE.strftime('%b %d')} - {END_DATE.strftime('%b %d, %Y')}")
    print(f"Milestone: 3.0.0")
    print()

    # Load bugs
    bugs = load_bugs()

    # Calculate daily counts
    daily_counts = calculate_daily_counts(bugs, START_DATE, END_DATE)

    # Save results
    save_results(daily_counts, OUTPUT_FILE)

    print(f"\n{'='*60}")
    print(f"✅ COMPLETE!")
    print(f"{'='*60}")

    # Show summary
    counts_list = [daily_counts[date_str] for date_str in sorted(daily_counts.keys())]
    print(f"\nSummary:")
    print(f"  Starting count (5/11): {counts_list[0]}")
    print(f"  Ending count (5/21): {counts_list[-1]}")
    print(f"  Net change: {counts_list[-1] - counts_list[0]:+d} bugs")
    print(f"  Average daily change: {(counts_list[-1] - counts_list[0]) / len(counts_list):.2f} bugs/day")

    print(f"\nOutput saved to: {OUTPUT_FILE}")
    print(f"Next step: Update calculate_burndown_projections.py to use these as starting actuals")


if __name__ == "__main__":
    main()
