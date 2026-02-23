# jira-tempo-skill

Two small Python scripts that turn your **Jira activity RSS feed** into a time-tracking CSV — no third-party packages required.

| Script | Input | Output |
|---|---|---|
| `parse_activity.py` | `activity.txt` (Jira feed) | `activity_parsed.csv` |
| `estimate_hours.py` | `activity_parsed.csv` | `time_estimates.csv` |

See **[skill.md](skill.md)** for the full how-to: how to download the feed, run the scripts, and tune the hour-estimation weights.

## Quick start

```bash
# 1. Download your Jira activity feed and save it as activity.txt
#    (see skill.md for the exact URL)

# 2. Parse the feed
python parse_activity.py

# 3. Estimate hours per ticket per day
python estimate_hours.py
```

## Requirements

Python 3.9+ — stdlib only, nothing to install.
