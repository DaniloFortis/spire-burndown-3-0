#!/usr/bin/env python3
"""
ClickUp Batch Bug Fetcher
Fetches all bugs from ClickUp using REST API and saves to local JSON file.
Avoids MCP tools - uses direct API calls with pagination for efficiency.
"""

import os
import json
import time
import requests
from datetime import datetime
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ClickUp API Configuration
API_KEY = os.getenv('CLICKUP_API_KEY')
# Support comma-separated list of list IDs to fetch from
# Default includes all lists where 3.0.0 bugs currently live:
# - Spire 3.0.0 (dedicated 3.0.0 list)
# - Backlog/product/triage lists where bugs originate before milestone tagging
# - Active sprints during the 3.0.0 cycle
DEFAULT_LIST_IDS = ','.join([
    '901326883737',  # Spire 3.0.0 (dedicated list)
    '901207871711',  # Spire Bug Backlog
    '901206064082',  # Spire Product Backlog
    '901211328806',  # Triage List - Tasks created from Slack
    '901326883162',  # Sprint AG (5/12 - 5/26)
    '901326883179',  # Sprint AH (5/26 - 6/9)
    '901326883209',  # Sprint AI (6/9 - 6/23)
    '901327316653',  # Sprint AJ (6/23 - 7/7)
])
LIST_IDS = os.getenv('CLICKUP_LIST_IDS', os.getenv('CLICKUP_LIST_ID', DEFAULT_LIST_IDS)).split(',')
LIST_IDS = [lid.strip() for lid in LIST_IDS if lid.strip()]
BASE_URL = 'https://api.clickup.com/api/v2'

# Output file configuration
OUTPUT_FILE = 'spire_bugs_complete.json'
CHECKPOINT_FILE = 'fetch_checkpoint.json'

# API request configuration
HEADERS = {
    'Authorization': API_KEY,
    'Content-Type': 'application/json'
}

# Rate limiting (ClickUp has rate limits, be respectful)
RATE_LIMIT_DELAY = 0.5  # seconds between requests


class ClickUpBatchFetcher:
    """Fetches tasks from multiple ClickUp lists and deduplicates by task ID."""

    def __init__(self, api_key: str, list_ids: List[str]):
        self.api_key = api_key
        self.list_ids = list_ids
        self.headers = {
            'Authorization': api_key,
            'Content-Type': 'application/json'
        }
        self.base_url = BASE_URL
        self.all_bugs = []
        self.bugs_by_id = {}  # For deduplication: {task_id: task_data}
        self.total_fetched = 0

    def fetch_all_tasks(self, include_closed: bool = True) -> List[Dict[str, Any]]:
        """
        Fetch all tasks from each configured ClickUp list, deduplicating by task ID.
        Tasks that appear in multiple lists (e.g. backlog + sprint) are only counted once.

        Args:
            include_closed: Whether to include closed/completed tasks

        Returns:
            Deduplicated list of all tasks with full details
        """
        print(f"\n{'='*60}")
        print(f"Starting batch fetch from {len(self.list_ids)} ClickUp lists")
        print(f"Include closed tasks: {include_closed}")
        for lid in self.list_ids:
            print(f"  - {lid}")
        print(f"{'='*60}\n")

        for list_idx, list_id in enumerate(self.list_ids, 1):
            print(f"\n[{list_idx}/{len(self.list_ids)}] Fetching from list {list_id}...")
            self._fetch_list(list_id, include_closed)

        # Build deduplicated list
        self.all_bugs = list(self.bugs_by_id.values())

        print(f"\n{'='*60}")
        print(f"Batch fetch complete!")
        print(f"Total tasks fetched (with duplicates): {self.total_fetched}")
        print(f"Unique bugs after deduplication: {len(self.all_bugs)}")
        print(f"{'='*60}\n")

        return self.all_bugs

    def _fetch_list(self, list_id: str, include_closed: bool):
        """Fetch all tasks from a single list, adding to bugs_by_id for deduplication."""
        page = 0
        list_total = 0
        has_more = True

        while has_more:
            url = f"{self.base_url}/list/{list_id}/task"
            params = {
                'page': page,
                'include_closed': str(include_closed).lower(),
                'subtasks': 'false',
            }

            try:
                response = requests.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                data = response.json()
                tasks = data.get('tasks', [])

                if not tasks:
                    has_more = False
                else:
                    # Deduplicate by task ID as we collect
                    new_count = 0
                    for task in tasks:
                        task_id = task.get('id')
                        if task_id and task_id not in self.bugs_by_id:
                            self.bugs_by_id[task_id] = task
                            new_count += 1

                    list_total += len(tasks)
                    self.total_fetched += len(tasks)
                    print(f"  Page {page}: {len(tasks)} tasks ({new_count} new). List total: {list_total}, Unique overall: {len(self.bugs_by_id)}")

                    self._save_checkpoint(list_id, page, self.total_fetched)
                    page += 1
                    time.sleep(RATE_LIMIT_DELAY)

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 404:
                    print(f"  ⚠️  List {list_id} not found, skipping")
                    return
                elif e.response.status_code == 401:
                    print(f"  ❌ Authentication failed. Check your API key.")
                    raise
                elif e.response.status_code == 429:
                    print(f"  ⏱️  Rate limited. Waiting 60 seconds...")
                    time.sleep(60)
                    continue
                else:
                    print(f"  ❌ HTTP Error: {e}")
                    print(f"  Response: {e.response.text}")
                    raise

            except Exception as e:
                print(f"  ❌ Error fetching page {page} of list {list_id}: {e}")
                raise

        print(f"  ✅ List {list_id}: {list_total} tasks fetched")

    def _save_checkpoint(self, list_id: str, page: int, total: int):
        """Save progress checkpoint for resumability."""
        checkpoint = {
            'last_list_id': list_id,
            'last_page': page,
            'total_fetched': total,
            'unique_bugs': len(self.bugs_by_id),
            'timestamp': datetime.now().isoformat(),
            'list_ids': self.list_ids
        }

        with open(CHECKPOINT_FILE, 'w') as f:
            json.dump(checkpoint, f, indent=2)

    def save_to_file(self, filename: str, pretty: bool = True):
        """
        Save all fetched bugs to a JSON file.

        Args:
            filename: Output filename
            pretty: Whether to pretty-print JSON (indent=2)
        """
        print(f"Saving {len(self.all_bugs)} bugs to {filename}...")

        # Prepare output data with metadata
        output = {
            'metadata': {
                'total_bugs': len(self.all_bugs),
                'list_ids': self.list_ids,
                'fetched_at': datetime.now().isoformat(),
                'source': 'ClickUp REST API (multi-list, deduplicated)'
            },
            'bugs': self.all_bugs
        }

        with open(filename, 'w', encoding='utf-8') as f:
            if pretty:
                json.dump(output, f, indent=2, ensure_ascii=False)
            else:
                json.dump(output, f, ensure_ascii=False)

        print(f"[OK] Saved successfully to {filename}")
        print(f"  File size: {os.path.getsize(filename) / 1024:.2f} KB")

    def print_summary(self):
        """Print a summary of fetched data."""
        if not self.all_bugs:
            print("No bugs fetched yet.")
            return

        print(f"\n{'='*60}")
        print("FETCH SUMMARY")
        print(f"{'='*60}")
        print(f"Total bugs: {len(self.all_bugs)}")

        # Status breakdown
        statuses = {}
        for bug in self.all_bugs:
            status_name = bug.get('status', {}).get('status', 'Unknown')
            statuses[status_name] = statuses.get(status_name, 0) + 1

        print(f"\nStatus breakdown:")
        for status, count in sorted(statuses.items(), key=lambda x: x[1], reverse=True):
            print(f"  {status}: {count}")

        # Check for required fields
        print(f"\nData quality check:")
        has_date_created = sum(1 for b in self.all_bugs if b.get('date_created'))
        has_date_closed = sum(1 for b in self.all_bugs if b.get('date_closed'))
        has_custom_fields = sum(1 for b in self.all_bugs if b.get('custom_fields'))

        print(f"  [OK] date_created: {has_date_created}/{len(self.all_bugs)}")
        print(f"  [OK] date_closed: {has_date_closed}/{len(self.all_bugs)}")
        print(f"  [OK] custom_fields: {has_custom_fields}/{len(self.all_bugs)}")

        # Sample bug IDs
        print(f"\nSample bug IDs (first 5):")
        for bug in self.all_bugs[:5]:
            bug_id = bug.get('id')
            name = bug.get('name', 'No name')[:50]
            print(f"  {bug_id}: {name}")

        print(f"{'='*60}\n")


def main():
    """Main execution function."""
    # Validate configuration
    if not API_KEY:
        print("ERROR: CLICKUP_API_KEY not found in environment")
        print("Please create a .env file with your ClickUp API key:")
        print("  CLICKUP_API_KEY=your_api_key_here")
        print("  CLICKUP_LIST_ID=901207871711")
        return

    if not LIST_IDS:
        print("ERROR: No list IDs configured (CLICKUP_LIST_IDS or CLICKUP_LIST_ID)")
        return

    # Create fetcher
    fetcher = ClickUpBatchFetcher(API_KEY, LIST_IDS)

    # Fetch all tasks (including closed ones for burndown analysis)
    bugs = fetcher.fetch_all_tasks(include_closed=True)

    if bugs:
        # Save to file
        fetcher.save_to_file(OUTPUT_FILE, pretty=True)

        # Print summary
        fetcher.print_summary()

        print(f"\n[SUCCESS!]")
        print(f"All bug data saved to: {OUTPUT_FILE}")
        print(f"Checkpoint saved to: {CHECKPOINT_FILE}")
        print(f"\nNext steps:")
        print(f"  1. Review the data in {OUTPUT_FILE}")
        print(f"  2. Run analysis scripts to process burndown metrics")
        print(f"  3. Generate dashboard visualizations")
    else:
        print("\n[WARNING] No bugs were fetched. Check your configuration and try again.")


if __name__ == '__main__':
    main()
