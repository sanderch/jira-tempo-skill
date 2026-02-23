"""
Estimates time spent per Jira ticket per day based on activity volume and type.

Scoring logic (per activity entry):
  - Created            : 2.0 pts  (defining/creating a ticket is substantial)
  - Status -> <status> : 1.5 pts  (implies real implementation/verification work)
  - Commented          : 1.0 pts  (investigation, analysis, communication)
  - Updated            : 0.5 pts  (metadata tweaks: labels, sprint, description, links)
  - Created / Posted   : 0.5 pts  (attaching a file)
  - anything else      : 0.5 pts  (fallback)

Hours = clamp(total_score * 0.5, 0.5, 4.0), rounded to nearest 0.5 h
"""

import csv
from collections import defaultdict

# ── Config ───────────────────────────────────────────────────────────────────
# Change these paths if needed
INPUT_FILE  = 'activity_parsed.csv'   # output of parse_activity.py
OUTPUT_FILE = 'time_estimates.csv'

# ── Weights ──────────────────────────────────────────────────────────────────

WEIGHTS: dict[str, float] = {
    'Created':          2.0,
    'Commented':        1.0,
    'Created / Posted': 0.5,   # file attachment
    'Updated':          0.5,
}


def activity_weight(activity_type: str) -> float:
    if activity_type.startswith('Status ->'):
        return 1.5
    return WEIGHTS.get(activity_type, 0.5)


def score_to_hours(score: float) -> float:
    """Convert raw score to hours in [0.5, 4.0], rounded to nearest 0.5."""
    raw = score * 0.5
    clamped = max(0.5, min(4.0, raw))
    return round(clamped * 2) / 2     # round to nearest 0.5


# ── Read & aggregate ─────────────────────────────────────────────────────────

# Key: (date, ticket)  Value: {title, score, activity_list}
groups: dict[tuple, dict] = defaultdict(lambda: {
    'title': '',
    'score': 0.0,
    'activities': [],
})

with open(INPUT_FILE, newline='', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        date   = row['date'].split()[0]      # keep only YYYY-MM-DD
        ticket = row['ticket']
        atype  = row['activity_type']
        key    = (date, ticket)

        groups[key]['title'] = row['title']  # last title wins (fine for renames)
        groups[key]['score'] += activity_weight(atype)
        groups[key]['activities'].append(atype)

# ── Write output ─────────────────────────────────────────────────────────────

rows_written = 0
with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['date', 'ticket', 'title', 'estimated_hours',
                     'activity_count', 'activity_breakdown'])

    for (date, ticket), info in sorted(groups.items()):
        hours     = score_to_hours(info['score'])
        breakdown = '; '.join(info['activities'])
        writer.writerow([date, ticket, info['title'], hours,
                         len(info['activities']), breakdown])
        rows_written += 1

print(f"Written {rows_written} rows -> {OUTPUT_FILE}")
