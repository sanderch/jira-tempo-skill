"""
Parses a Jira activity RSS/Atom feed and extracts:
  - Date
  - Jira ticket number
  - Ticket title/summary
  - Activity type and description of what was done

Usage:
    python parse_activity.py [input_file] [output_file]
    Defaults: activity.txt  activity_parsed.csv

To download the feed for a user:
    https://<your-jira-domain>/activity?maxResults=500&streams=user+IS+<username>&os_authType=basic
Save the page as activity.txt before running this script.
"""

import re
import html
import csv
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

# Ensure the terminal can output UTF-8 (Jira data may contain non-ASCII chars)
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# XML namespace map
NS = {
    'atom':     'http://www.w3.org/2005/Atom',
    'activity': 'http://activitystrea.ms/spec/1.0/',
}


def strip_html(text: str) -> str:
    """Strip HTML tags and normalize whitespace."""
    text = html.unescape(text or '')
    text = re.sub(r'<[^>]+>', ' ', text)
    return ' '.join(text.split())


def derive_activity_type(entry, verbs: list[str], categories: list[str]) -> str:
    """Return a human-readable activity type label."""
    # Category gives the most specific info for transitions / comments / created
    if categories:
        cat = categories[0].strip()
        if cat.lower() == 'comment':
            return 'Commented'
        if cat.lower() == 'created':
            return 'Created'
        # status transitions: term contains the target status name
        return f'Status -> {cat}'

    # Fall back to activity verb
    for v in verbs:
        if v.endswith('/post'):
            return 'Created / Posted'
        if v.endswith('/update'):
            return 'Updated'
        if v.endswith('/delete'):
            return 'Deleted'

    return 'Activity'


def get_issue_info(entry):
    """
    Return (issue_key, summary) from <activity:target> (preferred) or
    <activity:object> when it represents a Jira issue.
    """
    issue_type_uri = 'http://streams.atlassian.com/syndication/types/issue'

    for tag in ('activity:target', 'activity:object'):
        node = entry.find(tag, NS)
        if node is None:
            continue
        obj_type = node.find('activity:object-type', NS)
        if obj_type is None or obj_type.text != issue_type_uri:
            continue
        title_node   = node.find('atom:title', NS)
        summary_node = node.find('atom:summary', NS)
        key     = (title_node.text   or '').strip() if title_node   is not None else ''
        summary = (summary_node.text or '').strip() if summary_node is not None else ''
        if key:
            return key, summary

    return '', ''


def parse_entries(filepath: str) -> list[dict]:
    tree = ET.parse(filepath)
    root = tree.getroot()

    results = []

    for entry in root.findall('atom:entry', NS):
        # ── Date ────────────────────────────────────────────────────────────
        pub_node = entry.find('atom:published', NS)
        raw_date = pub_node.text if pub_node is not None else ''
        try:
            dt = datetime.fromisoformat(raw_date.replace('Z', '+00:00'))
            date_str = dt.strftime('%Y-%m-%d %H:%M')
        except ValueError:
            date_str = raw_date

        # ── Activity verbs & categories ──────────────────────────────────────
        verbs      = [v.text or '' for v in entry.findall('activity:verb', NS)]
        categories = [c.get('term', '') for c in entry.findall('atom:category', NS)]

        activity_type = derive_activity_type(entry, verbs, categories)

        # ── Ticket info ──────────────────────────────────────────────────────
        issue_key, issue_summary = get_issue_info(entry)

        # ── Human-readable description from <title> ──────────────────────────
        title_node = entry.find('atom:title', NS)
        title_html = title_node.text if title_node is not None else ''
        description = strip_html(title_html)

        # If still no issue key, fall back to parsing the title HTML
        if not issue_key:
            m = re.search(r'browse/([A-Z]+-\d+)', title_html or '')
            if m:
                issue_key = m.group(1)

        results.append({
            'date':          date_str,
            'ticket':        issue_key,
            'title':         issue_summary,
            'activity_type': activity_type,
            'description':   description,
        })

    return results


def print_table(entries: list[dict]) -> None:
    COL = {'date': 18, 'ticket': 12, 'activity_type': 28, 'title': 48}
    header = (
        f"{'Date':<{COL['date']}} "
        f"{'Ticket':<{COL['ticket']}} "
        f"{'Activity':<{COL['activity_type']}} "
        f"{'Summary':<{COL['title']}} "
        f"Description"
    )
    print(header)
    print('-' * (len(header) + 30))
    for e in entries:
        desc = e['description']
        if len(desc) > 100:
            desc = desc[:97] + '...'
        print(
            f"{e['date']:<{COL['date']}} "
            f"{e['ticket']:<{COL['ticket']}} "
            f"{e['activity_type']:<{COL['activity_type']}} "
            f"{e['title'][:COL['title']]:<{COL['title']}} "
            f"{desc}"
        )


def write_csv(entries: list[dict], out_path: str) -> None:
    fieldnames = ['date', 'ticket', 'title', 'activity_type', 'description']
    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(entries)
    print(f'\nCSV written to: {out_path}')


def main():
    input_file = 'activity.txt'
    output_csv = None

    # Simple arg handling: python parse_activity.py [input] [output.csv]
    if len(sys.argv) >= 2:
        input_file = sys.argv[1]
    if len(sys.argv) >= 3:
        output_csv = sys.argv[2]

    entries = parse_entries(input_file)
    print(f'Parsed {len(entries)} activity entries.\n')
    print_table(entries)

    if output_csv:
        write_csv(entries, output_csv)
    else:
        # Auto-write CSV alongside the script
        write_csv(entries, 'activity_parsed.csv')


if __name__ == '__main__':
    main()
