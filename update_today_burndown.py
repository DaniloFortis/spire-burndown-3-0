#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick Daily Burndown Update

Simplified update script for 3x daily automated runs:
1. Count active 3.0.0 bugs from current bug data
2. Add today's count to actual line (or update if already exists for today)
3. Recalculate estimated line from new position
4. Regenerate dashboard & Slack content
5. Commit & push to GitHub

This is much faster than full recalculation - perfect for keeping the chart current.
"""

import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Configuration
BUGS_FILE = "bugs_with_parsed_dates.json"
PROJECTIONS_FILE = "burndown_projections.json"
TODAY = datetime.now().date()


# Active statuses for math calculations (excludes "In QA" per requirement)
ACTIVE_MATH_STATUSES = [
    'to-do',
    'reopened',
    'in progress',
    'design review',
    'art review',
    'code review',
    'build pending',
    'blocked',
    'need more info'
]

# Statuses to exclude from dashboard breakdown (Closed/Won't Fix)
EXCLUDED_FROM_DASHBOARD = ['closed', "won't fix"]


def is_active_for_math(status):
    """Check if a bug status counts as active for math (excludes In QA)."""
    if not status:
        return False
    return status.lower().strip() in ACTIVE_MATH_STATUSES


def is_excluded_from_dashboard(status):
    """Check if a status should be hidden from dashboard breakdown."""
    if not status:
        return True
    return status.lower().strip() in EXCLUDED_FROM_DASHBOARD


def count_active_bugs():
    """
    Count current active 3.0.0 bugs (using ACTIVE_MATH_STATUSES allowlist).
    Excludes In QA per requirement.

    Returns:
        int: Current active bug count
    """
    print(f"📊 Counting active 3.0.0 bugs (excluding In QA)...")

    with open(BUGS_FILE, 'r', encoding='utf-8') as f:
        bugs = json.load(f)

    active_bugs = [
        bug for bug in bugs
        if bug.get('milestone_simplified') == '3.0.0'
        and is_active_for_math(bug.get('status'))
    ]

    count = len(active_bugs)
    print(f"✅ Current active bugs: {count}")
    return count


def get_status_breakdown():
    """
    Get status breakdown for dashboard cards (includes In QA, excludes Closed/Won't Fix).
    Only returns statuses with 1+ bugs.

    Returns:
        dict: {status_name: count}
    """
    with open(BUGS_FILE, 'r', encoding='utf-8') as f:
        bugs = json.load(f)

    milestone_bugs = [
        bug for bug in bugs
        if bug.get('milestone_simplified') == '3.0.0'
        and not is_excluded_from_dashboard(bug.get('status'))
    ]

    status_counts = {}
    for bug in milestone_bugs:
        status = bug.get('status', 'unknown')
        status_counts[status] = status_counts.get(status, 0) + 1

    return {
        status: count
        for status, count in sorted(status_counts.items(), key=lambda x: x[1], reverse=True)
        if count > 0
    }


def update_actual_line(projections, today_count):
    """
    Add or update today's count in actual line.

    Args:
        projections: Projection data
        today_count: Today's bug count

    Returns:
        tuple: (updated_projections, is_new_point)
    """
    today_str = TODAY.strftime('%Y-%m-%d')
    actual_line = projections['projections']['actual']

    # Check if today already exists
    existing_index = next(
        (i for i, p in enumerate(actual_line) if p['date'] == today_str),
        None
    )

    if existing_index is not None:
        # Update existing point
        old_count = actual_line[existing_index]['count']
        actual_line[existing_index]['count'] = today_count
        print(f"📝 Updated today's count: {old_count} → {today_count}")
        is_new = False
    else:
        # Add new point
        actual_line.append({
            "date": today_str,
            "count": today_count
        })
        print(f"➕ Added new point for {TODAY.strftime('%b %d')}: {today_count} bugs")
        is_new = True

    projections['current_active_bugs'] = today_count
    return projections, is_new


def recalculate_estimated_line(projections):
    """
    Recalculate estimated line from last actual point.
    Uses existing rate calculation logic.

    Args:
        projections: Projection data

    Returns:
        dict: Updated projections
    """
    print(f"📈 Recalculating estimated line...")

    actual_line = projections['projections']['actual']
    last_actual = actual_line[-1]
    start_count = last_actual['count']
    start_date = datetime.strptime(last_actual['date'], '%Y-%m-%d')

    # Get rate (using existing calculation or historical)
    rate = projections.get('estimated_line_rate', projections['historical_daily_rate'])
    rate_source = projections.get('estimated_line_rate_source', 'historical average')

    end_date = datetime.strptime(projections['key_dates']['go_live'], '%Y-%m-%d')

    print(f"   From: {start_date.strftime('%b %d')} with {start_count} bugs")
    print(f"   Rate: {rate:.2f} bugs/day ({rate_source})")

    estimated_line = []

    # Include last actual as first estimated (seamless connection)
    estimated_line.append({
        "date": start_date.strftime('%Y-%m-%d'),
        "count": start_count
    })

    current_date = start_date + timedelta(days=1)
    business_days_elapsed = 0
    last_business_day_count = start_count

    while current_date <= end_date:
        is_weekend = current_date.weekday() >= 5

        if is_weekend:
            # Weekend plateau
            count = last_business_day_count
        else:
            # Business day progress
            business_days_elapsed += 1
            count = start_count + (rate * business_days_elapsed)
            last_business_day_count = count

        if count <= 0:
            estimated_line.append({
                "date": current_date.strftime('%Y-%m-%d'),
                "count": 0
            })
            break

        estimated_line.append({
            "date": current_date.strftime('%Y-%m-%d'),
            "count": round(count, 2)
        })

        current_date += timedelta(days=1)

    projections['projections']['estimated'] = estimated_line
    print(f"✅ Estimated line recalculated")
    return projections


def run_script(script_name):
    """Run a Python script."""
    try:
        subprocess.run(
            [sys.executable, script_name],
            check=True,
            capture_output=True
        )
        return True
    except:
        return False


def git_commit_and_push(message):
    """Commit and push to GitHub."""
    try:
        # Check for changes
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            capture_output=True,
            text=True,
            check=True
        )

        if not result.stdout.strip():
            print(f"ℹ️  No changes to commit")
            return True

        # Add, commit, push
        subprocess.run(['git', 'add', 'docs/index.html', 'burndown_projections.json',
                       'burndown_chart.png', 'slack_message.json'], check=True)
        subprocess.run(['git', 'commit', '-m', message], check=True, capture_output=True)
        subprocess.run(['git', 'push'], check=True, capture_output=True)

        return True
    except:
        return False


def main():
    """Main execution."""
    start_time = datetime.now()

    print(f"\n{'='*60}")
    print(f"🔄 Quick Burndown Update - {TODAY.strftime('%b %d, %Y')}")
    print(f"{'='*60}\n")

    # Step 1: Count active bugs
    try:
        current_count = count_active_bugs()
    except FileNotFoundError:
        print(f"❌ Bug data file not found: {BUGS_FILE}")
        print(f"   Make sure to fetch latest bug data first")
        sys.exit(1)

    # Step 2: Load projections
    try:
        with open(PROJECTIONS_FILE, 'r', encoding='utf-8') as f:
            projections = json.load(f)
    except FileNotFoundError:
        print(f"❌ Projections file not found: {PROJECTIONS_FILE}")
        print(f"   Run calculate_burndown_projections.py first")
        sys.exit(1)

    # Step 3: Update actual line
    projections, is_new_point = update_actual_line(projections, current_count)

    # Step 4: Recalculate estimated line
    projections = recalculate_estimated_line(projections)

    # Step 4.5: Update status breakdown for dashboard cards
    status_breakdown = get_status_breakdown()
    projections['status_breakdown'] = status_breakdown
    print(f"\n📋 Status Breakdown:")
    for status, count in status_breakdown.items():
        print(f"   {status}: {count}")

    # Step 5: Update metadata
    projections['generated_date'] = TODAY.strftime('%Y-%m-%d')
    projections['generated_timestamp'] = datetime.now().isoformat()

    # Save projections
    print(f"\n💾 Saving updated projections...")
    with open(PROJECTIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(projections, f, indent=2)
    print(f"✅ Saved")

    # Step 6: Regenerate dashboard
    print(f"\n🎨 Regenerating dashboard...")
    if run_script('generate_burndown_projection_chart.py'):
        print(f"✅ Dashboard regenerated")
    else:
        print(f"⚠️  Dashboard regeneration had issues")

    # Step 7: Regenerate Slack content
    print(f"\n💬 Regenerating Slack content...")
    if run_script('generate_slack_burndown.py'):
        print(f"✅ Slack content regenerated")
    else:
        print(f"⚠️  Slack content generation had issues")

    # Step 8: Commit and push
    print(f"\n🚀 Deploying to GitHub...")
    days_to_freeze = projections.get('business_days_to_code_freeze', 0)
    commit_msg = f"Update: {current_count} bugs, {days_to_freeze} days to freeze\n\n{start_time.strftime('%Y-%m-%d %H:%M')}"

    if git_commit_and_push(commit_msg):
        print(f"✅ Pushed to GitHub")
    else:
        print(f"⚠️  Git push had issues")

    # Summary
    duration = (datetime.now() - start_time).total_seconds()

    print(f"\n{'='*60}")
    print(f"✅ Update Complete!")
    print(f"{'='*60}")
    print(f"Active Bugs: {current_count}")
    print(f"Days to Code Freeze: {days_to_freeze}")
    print(f"Duration: {duration:.1f}s")
    print(f"\n🔗 Dashboard: https://DaniloFortis.github.io/spire-burndown-3-0/")


if __name__ == "__main__":
    main()
