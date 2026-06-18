#!/usr/bin/env python3
"""
Analyzes bug data to understand available metadata fields, milestones, tags, and distributions.
This helps identify what context we have for burndown analysis.
"""

import json
from collections import defaultdict, Counter
from datetime import datetime

def analyze_custom_field(bugs, field_id, field_name):
    """Analyze a specific custom field across all bugs"""
    print(f"\n{'='*80}")
    print(f"CUSTOM FIELD: {field_name}")
    print(f"ID: {field_id}")
    print('='*80)

    values = []
    value_counts = Counter()
    bugs_with_field = 0
    bugs_without_field = 0

    for bug in bugs:
        field_found = False
        for cf in bug.get('custom_fields', []):
            if cf.get('id') == field_id:
                field_found = True
                bugs_with_field += 1

                # Get the value
                value = cf.get('value')
                if value is not None:
                    # For dropdown fields, get the option name
                    if cf.get('type') == 'drop_down':
                        options = cf.get('type_config', {}).get('options', [])
                        for opt in options:
                            if opt.get('orderindex') == value or opt.get('id') == value:
                                value_name = opt.get('name')
                                values.append(value_name)
                                value_counts[value_name] += 1
                                break
                    else:
                        values.append(str(value))
                        value_counts[str(value)] += 1
                break

        if not field_found:
            bugs_without_field += 1

    print(f"Bugs with this field: {bugs_with_field}")
    print(f"Bugs without this field: {bugs_without_field}")
    print(f"\nValue distribution (top 20):")
    for value, count in value_counts.most_common(20):
        percentage = (count / len(bugs)) * 100
        print(f"  {value}: {count} ({percentage:.1f}%)")

    if len(value_counts) > 20:
        print(f"  ... and {len(value_counts) - 20} more values")

    return value_counts

def analyze_tags(bugs):
    """Analyze tag usage across bugs"""
    print(f"\n{'='*80}")
    print("TAGS")
    print('='*80)

    tag_counts = Counter()
    bugs_with_tags = 0

    for bug in bugs:
        tags = bug.get('tags', [])
        if tags:
            bugs_with_tags += 1
            for tag in tags:
                tag_name = tag.get('name')
                if tag_name:
                    tag_counts[tag_name] += 1

    print(f"Bugs with tags: {bugs_with_tags} ({(bugs_with_tags/len(bugs))*100:.1f}%)")
    print(f"Bugs without tags: {len(bugs) - bugs_with_tags} ({((len(bugs)-bugs_with_tags)/len(bugs))*100:.1f}%)")
    print(f"\nTag distribution:")
    for tag, count in tag_counts.most_common():
        percentage = (count / len(bugs)) * 100
        print(f"  {tag}: {count} ({percentage:.1f}%)")

    return tag_counts

def analyze_status(bugs):
    """Analyze status distribution"""
    print(f"\n{'='*80}")
    print("STATUS")
    print('='*80)

    status_counts = Counter()
    status_type_counts = Counter()

    for bug in bugs:
        status = bug.get('status', {})
        status_name = status.get('status')
        status_type = status.get('type')

        if status_name:
            status_counts[status_name] += 1
        if status_type:
            status_type_counts[status_type] += 1

    print("Status names:")
    for status, count in status_counts.most_common():
        percentage = (count / len(bugs)) * 100
        print(f"  {status}: {count} ({percentage:.1f}%)")

    print("\nStatus types:")
    for stype, count in status_type_counts.most_common():
        percentage = (count / len(bugs)) * 100
        print(f"  {stype}: {count} ({percentage:.1f}%)")

    return status_counts, status_type_counts

def analyze_dates(bugs):
    """Analyze date fields"""
    print(f"\n{'='*80}")
    print("DATE FIELDS")
    print('='*80)

    date_fields = ['date_created', 'date_closed', 'date_updated', 'date_done']

    for field in date_fields:
        values = []
        for bug in bugs:
            val = bug.get(field)
            if val:
                try:
                    # Convert milliseconds timestamp to datetime
                    # Handle both int and string timestamps
                    if isinstance(val, str):
                        val = int(val)
                    dt = datetime.fromtimestamp(val / 1000)
                    values.append(dt)
                except (ValueError, TypeError):
                    # Skip invalid dates
                    pass

        if values:
            values.sort()
            print(f"\n{field}:")
            print(f"  Bugs with this date: {len(values)} ({(len(values)/len(bugs))*100:.1f}%)")
            print(f"  Earliest: {values[0].strftime('%Y-%m-%d')}")
            print(f"  Latest: {values[-1].strftime('%Y-%m-%d')}")
            print(f"  Range: {(values[-1] - values[0]).days} days")

def main():
    print("Loading bug data...")
    with open('spire_bugs_complete.json', encoding='utf-8') as f:
        data = json.load(f)

    bugs = data['bugs']
    metadata = data['metadata']

    print(f"\n{'='*80}")
    print("BUG DATA OVERVIEW")
    print('='*80)
    print(f"Total bugs: {len(bugs)}")
    print(f"Fetched at: {metadata.get('fetched_at')}")
    print(f"Source: {metadata.get('source')}")

    # Analyze key fields
    analyze_dates(bugs)
    analyze_status(bugs)
    analyze_tags(bugs)

    # Analyze important custom fields
    key_fields = {
        '9a1361a8-e8e6-450e-9ad6-e81f7bb65261': 'Spire Release',
        '96c385d3-0b6b-4a3b-9ba2-a407b27d7193': 'Severity (QA)',
        'bcb9a8ad-086a-45b1-9d50-abd2edd44d2e': 'Spire - Game Areas (QA)',
        '37bb0c94-9b2c-4397-acb4-fa8c17524ede': 'Platform (QA)',
        '67ea8f39-eef6-4786-bab9-61586a1a5814': 'QA Status',
        'cd6765de-2999-456f-86fd-b495de5d69c4': 'Environment',
        '23a168ae-c69d-40a0-9192-e7da54306d43': 'Spire - Pod',
        '3989d07e-3815-4c6c-baa2-a341ebf4fe8e': 'Spire - Pods & Others (QA)',
        '8684863f-084f-457a-991f-0d9c9d933251': 'Resolution',
        '42c79c5f-37db-4174-9e7f-afbf8adaf8ac': 'Issue Type',
    }

    results = {}
    for field_id, field_name in key_fields.items():
        results[field_name] = analyze_custom_field(bugs, field_id, field_name)

    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY - FIELDS USEFUL FOR BURNDOWN ANALYSIS")
    print('='*80)
    print("\n✅ PRIMARY MILESTONE FIELD:")
    print("   - Spire Release (63 release/milestone options)")
    print("   - Includes: SL releases, hotfixes, data pushes, and special categories (Triage, Icebox, Cut?)")

    print("\n✅ TIME-BASED FIELDS:")
    print("   - date_created: When bug was reported")
    print("   - date_closed: When bug was closed")
    print("   - date_updated: Last modification")
    print("   - date_done: When marked as done")

    print("\n✅ CATEGORIZATION FIELDS:")
    print("   - Severity (QA): Critical, Major, Minor, Tweak, N/A")
    print("   - Game Areas: UI/UX/Art, Campaign, IAPs/Shop, etc.")
    print("   - Platform: Android, iOS, All mobile")
    print("   - Pod: Tech, PJ, Live Ops, Art, Platform")
    print("   - Environment: Feature, Dev, Stage, Prod, Live")
    print("   - Issue Type: Bug, Improvement")

    print("\n✅ STATUS FIELDS:")
    print("   - Status: Open/Closed/In Progress")
    print("   - QA Status: Detailed workflow status")
    print("   - Resolution: QA Passed, Won't Fix, Duplicated, etc.")

    print("\n✅ METADATA:")
    print("   - Tags: possible-duplicate, etc.")
    print("   - Assignees, Watchers")
    print("   - Custom IDs (SPIRE-XXXXX)")

    print("\n" + "="*80)
    print("Analysis complete! Ready for next step.")
    print("="*80)

if __name__ == '__main__':
    main()
