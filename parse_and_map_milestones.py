#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parse bug dates and map milestones to calendar dates for burndown analysis.

This script:
1. Maps ClickUp milestone names to Release Calendar dates
2. Parses bug created/closed dates from spire_bugs_complete.json
3. Filters bugs to a 6-month window leading up to the 3.0.0 release
4. Prepares structured data for burndown visualization
"""

import json
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Tuple
import os
import sys

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# === CONFIGURATION ===
BUGS_FILE = "spire_bugs_complete.json"
OUTPUT_FILE = "bugs_with_parsed_dates.json"
MILESTONE_MAP_FILE = "milestone_date_mapping.json"
ANALYSIS_OUTPUT = "burndown_data.json"

# 6-month window for analysis
WINDOW_START = datetime(2025, 12, 18)  # 6 months before June 18, 2026
WINDOW_END = datetime(2026, 6, 18)     # Today (3.0.0 Feature Complete)

# Key 3.0.0 milestone dates
MILESTONE_3_0_0 = {
    "feature_complete": datetime(2026, 6, 18),
    "bug_fixing_only": datetime(2026, 6, 18),
    "code_freeze": datetime(2026, 6, 26),
    "server_update": datetime(2026, 6, 29),
    "submit": datetime(2026, 7, 1),
    "go_live": datetime(2026, 7, 6)
}

# Milestone name mapping (ClickUp -> simplified)
# 3.0.0 is the primary release; others are kept for historical context
MILESTONE_NAME_MAP = {
    "3.0.0": "3.0.0",
    "2.0.0 Global": "2.0.0 Global",
    "2.1.0 Client Hotfix": "2.1.0",
    "Triage": "Triage",
    "Post-Global": "Post-Global"
}


def parse_clickup_timestamp(timestamp_ms) -> datetime:
    """
    Convert ClickUp timestamp (milliseconds since epoch) to datetime.

    Args:
        timestamp_ms: Timestamp in milliseconds (int or str)

    Returns:
        datetime object or None
    """
    if timestamp_ms is None:
        return None

    # Convert to int if string
    if isinstance(timestamp_ms, str):
        try:
            timestamp_ms = int(timestamp_ms)
        except ValueError:
            return None

    # ClickUp timestamps are in milliseconds
    return datetime.fromtimestamp(timestamp_ms / 1000.0)


def extract_milestone_from_bug(bug: dict) -> str:
    """
    Extract the Spire Release milestone name from a bug.

    Args:
        bug: Bug dictionary from ClickUp

    Returns:
        Milestone name string or "Unknown"
    """
    custom_fields = bug.get("custom_fields", [])

    for field in custom_fields:
        # Field ID for "Spire Release" from analysis
        if field.get("id") == "9a1361a8-e8e6-450e-9ad6-e81f7bb65261":
            # Get the value - it's in type_config -> options
            value = field.get("value")
            if value is not None:
                # Value is an index into the options array
                options = field.get("type_config", {}).get("options", [])
                if isinstance(value, int) and value < len(options):
                    return options[value].get("name", "Unknown")

    return "Unknown"


def parse_bug_data(bugs_file: str) -> List[dict]:
    """
    Parse bug data and extract key information.
    Filters to ONLY Bug-type tasks (custom_item_id == 1002), excluding features/stories.

    Args:
        bugs_file: Path to spire_bugs_complete.json

    Returns:
        List of parsed bug dictionaries (Bug type only)
    """
    print(f"📂 Loading bugs from {bugs_file}...")

    with open(bugs_file, 'r', encoding='utf-8') as f:
        bugs_data = json.load(f)

    bugs = bugs_data.get("bugs", [])
    print(f"✅ Loaded {len(bugs)} total tasks")

    # ClickUp custom_item_id = 1002 is "Bug" type
    BUG_TYPE_ID = 1002
    bugs_only = [b for b in bugs if b.get('custom_item_id') == BUG_TYPE_ID]
    print(f"✅ Filtered to {len(bugs_only)} Bug-type tasks (excluding features/stories)")

    parsed_bugs = []

    for bug in bugs_only:
        # Extract basic info
        bug_id = bug.get("id")
        name = bug.get("name", "")
        status = bug.get("status", {}).get("status", "")
        date_created_ms = bug.get("date_created")
        date_closed_ms = bug.get("date_closed")

        # Parse dates
        date_created = parse_clickup_timestamp(date_created_ms)
        date_closed = parse_clickup_timestamp(date_closed_ms) if date_closed_ms else None

        # Extract milestone
        milestone = extract_milestone_from_bug(bug)

        # Build parsed bug record
        parsed_bug = {
            "id": bug_id,
            "name": name,
            "status": status,
            "milestone": milestone,
            "milestone_simplified": MILESTONE_NAME_MAP.get(milestone, milestone),
            "date_created": date_created.isoformat() if date_created else None,
            "date_created_ts": date_created_ms,
            "date_closed": date_closed.isoformat() if date_closed else None,
            "date_closed_ts": date_closed_ms,
            "in_6month_window": False
        }

        # Check if bug is in 6-month window (created or closed)
        if date_created and WINDOW_START <= date_created <= WINDOW_END:
            parsed_bug["in_6month_window"] = True
        elif date_closed and WINDOW_START <= date_closed <= WINDOW_END:
            parsed_bug["in_6month_window"] = True

        parsed_bugs.append(parsed_bug)

    return parsed_bugs


def analyze_burndown_metrics(parsed_bugs: List[dict]) -> dict:
    """
    Calculate burndown metrics from parsed bug data.

    Args:
        parsed_bugs: List of parsed bug dictionaries

    Returns:
        Dictionary with burndown metrics
    """
    print("\n📊 Calculating burndown metrics...")

    # Filter to 6-month window
    window_bugs = [b for b in parsed_bugs if b["in_6month_window"]]

    print(f"✅ {len(window_bugs)} bugs in 6-month window ({WINDOW_START.date()} - {WINDOW_END.date()})")

    # Count by milestone
    milestone_counts = defaultdict(int)
    for bug in window_bugs:
        milestone_counts[bug["milestone_simplified"]] += 1

    # Count by status
    status_counts = defaultdict(int)
    for bug in window_bugs:
        status_counts[bug["status"]] += 1

    # Bugs opened per day
    bugs_opened_by_date = defaultdict(int)
    for bug in window_bugs:
        if bug["date_created"]:
            date = bug["date_created"][:10]  # YYYY-MM-DD
            bugs_opened_by_date[date] += 1

    # Bugs closed per day
    bugs_closed_by_date = defaultdict(int)
    for bug in window_bugs:
        if bug["date_closed"]:
            date = bug["date_closed"][:10]  # YYYY-MM-DD
            bugs_closed_by_date[date] += 1

    # Cumulative open bugs over time
    cumulative_open = calculate_cumulative_open(window_bugs)

    metrics = {
        "window_start": WINDOW_START.isoformat(),
        "window_end": WINDOW_END.isoformat(),
        "total_bugs_in_window": len(window_bugs),
        "milestone_counts": dict(milestone_counts),
        "status_counts": dict(status_counts),
        "bugs_opened_by_date": dict(sorted(bugs_opened_by_date.items())),
        "bugs_closed_by_date": dict(sorted(bugs_closed_by_date.items())),
        "cumulative_open_bugs": cumulative_open,
        "key_milestone_dates": {
            "3.0.0_bug_fixing_only": MILESTONE_3_0_0["bug_fixing_only"].isoformat(),
            "3.0.0_code_freeze": MILESTONE_3_0_0["code_freeze"].isoformat(),
            "3.0.0_submit": MILESTONE_3_0_0["submit"].isoformat(),
            "3.0.0_go_live": MILESTONE_3_0_0["go_live"].isoformat()
        }
    }

    return metrics


def calculate_cumulative_open(bugs: List[dict]) -> dict:
    """
    Calculate cumulative open bugs over time.

    Args:
        bugs: List of parsed bug dictionaries

    Returns:
        Dictionary mapping dates to cumulative open bug count
    """
    # Collect all date events
    events = []

    for bug in bugs:
        if bug["date_created"]:
            date = bug["date_created"][:10]
            events.append((date, "opened", bug["id"]))

        if bug["date_closed"]:
            date = bug["date_closed"][:10]
            events.append((date, "closed", bug["id"]))

    # Sort events by date
    events.sort(key=lambda x: x[0])

    # Calculate cumulative
    cumulative = {}
    open_bugs = set()

    for date, event_type, bug_id in events:
        if event_type == "opened":
            open_bugs.add(bug_id)
        elif event_type == "closed":
            open_bugs.discard(bug_id)

        cumulative[date] = len(open_bugs)

    return cumulative


def main():
    """Main execution function."""
    print("🚀 Starting milestone parsing and burndown analysis...")
    print(f"📅 Analysis window: {WINDOW_START.date()} to {WINDOW_END.date()}")
    print(f"📌 Key 3.0.0 milestone dates:")
    for key, date in MILESTONE_3_0_0.items():
        print(f"   - {key}: {date.date()}")

    # Parse bug data
    parsed_bugs = parse_bug_data(BUGS_FILE)

    # Save parsed bugs
    print(f"\n💾 Saving parsed bugs to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(parsed_bugs, f, indent=2)
    print(f"✅ Saved {len(parsed_bugs)} parsed bugs")

    # Calculate burndown metrics
    metrics = analyze_burndown_metrics(parsed_bugs)

    # Save burndown data
    print(f"\n💾 Saving burndown metrics to {ANALYSIS_OUTPUT}...")
    with open(ANALYSIS_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(metrics, f, indent=2)

    # Print summary
    print("\n" + "="*60)
    print("📊 BURNDOWN ANALYSIS SUMMARY")
    print("="*60)
    print(f"\n6-Month Window: {WINDOW_START.date()} to {WINDOW_END.date()}")
    print(f"Total bugs in window: {metrics['total_bugs_in_window']}")

    print("\n🎯 Top Milestones in Window:")
    sorted_milestones = sorted(
        metrics['milestone_counts'].items(),
        key=lambda x: x[1],
        reverse=True
    )
    for milestone, count in sorted_milestones[:10]:
        print(f"   {milestone}: {count} bugs")

    print("\n📈 Status Distribution:")
    for status, count in sorted(metrics['status_counts'].items(), key=lambda x: x[1], reverse=True):
        print(f"   {status}: {count} bugs")

    print("\n✅ Analysis complete!")
    print(f"📁 Output files:")
    print(f"   - {OUTPUT_FILE}")
    print(f"   - {ANALYSIS_OUTPUT}")
    print("\n🎯 Ready for Step 3: Generate burndown visualizations")


if __name__ == "__main__":
    main()
