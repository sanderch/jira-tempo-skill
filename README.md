# jira-tempo-skill

Two small Python scripts that parse your **Jira activity RSS feed** into a structured CSV and estimate hours spent per ticket per day — ready to log in **Tempo** or any timesheet tool. No third-party packages required.

| Script | Input | Output |
|---|---|---|
| `scripts/parse_activity.py` | `activity.txt` (Jira feed) | `activity_parsed.csv` |
| `scripts/estimate_hours.py` | `activity_parsed.csv` | `time_estimates.csv` |

See **[SKILL.md](SKILL.md)** for the full how-to: how to download the feed, run the scripts, and tune the hour-estimation weights.

## Quick start

```bash
# 1. Download your Jira activity feed and save it as activity.txt
#    (see skill.md for the exact URL)

# 2. Parse the feed
python scripts/parse_activity.py

# 3. Estimate hours per ticket per day
python scripts/estimate_hours.py
```

## Example output

**`activity_parsed.csv`** — one row per activity event:

| date | ticket | title | activity_type | description |
|---|---|---|---|---|
| 2026-02-23 14:45 | PROJ-512 | Use rule value as a score | Status -> Implementation | Jane Doe changed the status to Implementation on PROJ-512 |
| 2026-02-23 11:59 | PROJ-515 | Add validation on field name | Updated | Jane Doe changed the Labels to '✅autotested' on PROJ-515 |
| 2026-02-23 09:46 | PROJ-545 | Observability of report processing | Updated | Jane Doe linked 2 issues |
| 2026-02-23 08:35 | SUP-1234 | Button does not respond on mobile | Commented | Jane Doe commented on SUP-1234 |
| 2026-02-20 13:02 | PROJ-548 | S3 storage integration | Created | Jane Doe created PROJ-548 |

**`time_estimates.csv`** — one row per ticket per day, with estimated hours:

| date | ticket | title | estimated_hours | activity_count | activity_breakdown |
|---|---|---|---|---|---|
| 2026-02-23 | PROJ-512 | Use rule value as a score | 1.0 | 2 | Status -> Implementation; Updated |
| 2026-02-23 | PROJ-515 | Add validation on field name | 0.5 | 1 | Updated |
| 2026-02-23 | PROJ-545 | Observability of report processing | 0.5 | 1 | Updated |
| 2026-02-23 | SUP-1234 | Button does not respond on mobile | 1.0 | 2 | Commented; Created / Posted |
| 2026-02-20 | PROJ-548 | S3 storage integration | 1.5 | 3 | Created; Updated; Updated |

## Requirements

Python 3.9+ — stdlib only, nothing to install.
