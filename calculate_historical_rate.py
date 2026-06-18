#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calculate Historical Burndown Rate from Recent Milestones

Analyzes the final 10 business days before ship for recent milestones:
- 1.7.0 (Refinement 3)
- 1.8.0 (Refinement 4)
- 1.9.0 (Client Hotfix)

For each milestone:
- Count total bugs FOUND during entire milestone period
- Count total bugs FIXED (currently Closed status - assume fixed by ship)
- Calculate net bugs removed: (bugs_fixed - bugs_found)
- Daily rate over final 10 business days: -(net_bugs_removed / 10)
  - Negative = burning down (reducing backlog) ✅
  - Positive = accumulating (growing backlog) ⚠️

Average across the 3 milestones to get historical_daily_rate.
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
OUTPUT_FILE = "historical_rate_analysis.json"

# Milestone configurations
MILESTONES = [
    {
        'name': '1.7.0',
        'clickup_name': '1.7.0',
        'period_start': datetime(2026, 1, 1),   # After 1.6.0
        'ship_date': datetime(2026, 2, 11)       # Go Live
    },
    {
        'name': '1.8.0',
        'clickup_name': '1.8.0',
        'period_start': datetime(2026, 2, 11),  # After 1.7.0
        'ship_date': datetime(2026, 4, 17)       # Go Live
    },
    {
        'name': '1.9.0',
        'clickup_name': '1.9.0',
        'period_start': datetime(2026, 4, 17),  # After 1.8.0
        'ship_date': datetime(2026, 4, 28)       # Go Live
    }
]

BUSINESS_DAYS = 10  # Final 2 weeks before ship


def load_bugs():
    """Load bug data from JSON file."""
    print(f"Loading bugs from {BUGS_FILE}...")
    with open(BUGS_FILE, 'r', encoding='utf-8') as f:
        bugs = json.load(f)
    print(f"Loaded {len(bugs)} bugs")
    return bugs


def analyze_milestone_window(bugs, milestone):
    """
    Analyze bugs for a milestone using net bugs fixed approach.

    Calculates burndown rate over final 10 business days:
    - Bugs FOUND during entire milestone period
    - Bugs FIXED (currently Closed - assume fixed by ship)
    - Net bugs removed from backlog
    - Daily rate = -(net_bugs_removed / 10 business days)

    Args:
        bugs: List of bug dictionaries
        milestone: Milestone configuration dict

    Returns:
        dict: Analysis results
    """
    name = milestone['name']
    clickup_name = milestone['clickup_name']
    period_start = milestone['period_start']
    ship_date = milestone['ship_date']

    print(f"\n{'='*60}")
    print(f"Analyzing {name}")
    print(f"{'='*60}")
    print(f"Ship Date: {ship_date.strftime('%b %d, %Y')}")
    print(f"Period: {period_start.strftime('%b %d')} to {ship_date.strftime('%b %d, %Y')}")

    # Filter to bugs tagged with this milestone
    milestone_bugs = [
        bug for bug in bugs
        if bug.get('milestone_simplified') == clickup_name
    ]

    print(f"Total bugs tagged with {name}: {len(milestone_bugs)}")

    # Bugs FOUND during milestone period
    bugs_found = []
    for bug in milestone_bugs:
        if bug.get('date_created'):
            created = datetime.fromisoformat(bug['date_created'])
            if period_start <= created <= ship_date:
                bugs_found.append(bug)

    # Bugs FIXED: All currently Closed bugs (assume fixed by ship)
    bugs_fixed = [bug for bug in milestone_bugs if bug.get('status') == 'Closed']

    # Net bugs removed from backlog
    net_bugs_removed = len(bugs_fixed) - len(bugs_found)

    # Daily rate over final 10 business days
    # Negative rate = burning down (reducing count)
    daily_rate = -(net_bugs_removed / BUSINESS_DAYS)

    print(f"\nResults:")
    print(f"  Bugs FOUND during period: {len(bugs_found)}")
    print(f"  Bugs FIXED (currently Closed): {len(bugs_fixed)}")
    print(f"  Net bugs removed from backlog: {net_bugs_removed:+d}")
    print(f"  Daily burndown rate (final {BUSINESS_DAYS} days): {daily_rate:.2f} bugs/day")

    if daily_rate < 0:
        print(f"  Status: BURNING DOWN (reducing backlog by {abs(daily_rate):.2f} bugs/day)")
    elif daily_rate > 0:
        print(f"  Status: ACCUMULATING (growing backlog by {daily_rate:.2f} bugs/day)")
    else:
        print(f"  Status: STABLE (no net change)")

    return {
        'milestone': name,
        'ship_date': ship_date.isoformat(),
        'period_start': period_start.isoformat(),
        'business_days': BUSINESS_DAYS,
        'total_milestone_bugs': len(milestone_bugs),
        'bugs_found_in_period': len(bugs_found),
        'bugs_fixed': len(bugs_fixed),
        'net_bugs_removed': net_bugs_removed,
        'daily_rate': round(daily_rate, 2)
    }


def calculate_average_rate(analyses):
    """
    Calculate average daily rate across milestones.

    Args:
        analyses: List of milestone analysis results

    Returns:
        float: Average daily rate
    """
    rates = [a['daily_rate'] for a in analyses]
    avg_rate = sum(rates) / len(rates)

    print(f"\n{'='*60}")
    print(f"AVERAGE ACROSS {len(analyses)} MILESTONES")
    print(f"{'='*60}")

    for i, analysis in enumerate(analyses, 1):
        print(f"{i}. {analysis['milestone']}: {analysis['daily_rate']:+.2f} bugs/day")

    print(f"\nAverage Daily Rate: {avg_rate:+.2f} bugs/day")

    if avg_rate < 0:
        print(f"Overall: BURNING DOWN (average rate is negative)")
    else:
        print(f"Overall: ACCUMULATING (average rate is positive)")

    return avg_rate


def save_analysis(analyses, avg_rate):
    """Save analysis results to JSON."""
    output = {
        'calculated_date': datetime.now().isoformat(),
        'methodology': 'Net bugs fixed over final 10 business days before ship',
        'calculation': 'Daily rate = -((bugs_fixed - bugs_found) / 10 business days)',
        'milestones_analyzed': [m['name'] for m in MILESTONES],
        'business_days': BUSINESS_DAYS,
        'historical_daily_rate': round(avg_rate, 2),
        'rate_interpretation': 'Negative = burning down (reducing backlog), Positive = accumulating (growing backlog)',
        'milestone_analyses': analyses
    }

    print(f"\nSaving analysis to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)
    print(f"Saved!")

    return output


def main():
    """Main execution."""
    print("Historical Burndown Rate Calculation")
    print("="*60)
    print(f"Analyzing last 3 releases: {', '.join(m['name'] for m in MILESTONES)}")
    print(f"Method: Net bugs fixed over final {BUSINESS_DAYS} business days before ship")
    print(f"Formula: -((bugs_fixed - bugs_found) / {BUSINESS_DAYS} days)")
    print()

    # Load bugs
    bugs = load_bugs()

    # Analyze each milestone
    analyses = []
    for milestone in MILESTONES:
        analysis = analyze_milestone_window(bugs, milestone)
        analyses.append(analysis)

    # Calculate average
    avg_rate = calculate_average_rate(analyses)

    # Save results
    save_analysis(analyses, avg_rate)

    print(f"\n{'='*60}")
    print(f"COMPLETE!")
    print(f"{'='*60}")
    print(f"\nHistorical Daily Rate: {avg_rate:+.2f} bugs/day")
    print(f"Results saved to: {OUTPUT_FILE}")
    print(f"\nNext step: Update calculate_burndown_projections.py to use this rate")


if __name__ == "__main__":
    main()
