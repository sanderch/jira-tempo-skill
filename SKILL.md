---
name: jira-tempo
description: Parse a Jira activity RSS/Atom feed and estimate hours spent per Jira ticket per day. Use this skill when the user wants to: (1) extract activity events (date, ticket, action, description) from a Jira activity feed file into a structured CSV, (2) estimate time spent per ticket based on activity volume and type, or (3) prepare a time-tracking report from Jira activity for Tempo or similar timesheet tools. Expects activity.txt downloaded from the Jira activity stream API.
---

# Jira Tempo

Parse a Jira activity feed into structured CSVs, then estimate hours spent per ticket per day.

## Setup

Download the Jira activity feed and save as `activity.txt`:

```
https://<your-jira-domain>/activity?maxResults=500&streams=user+IS+<username>&os_authType=basic
```

Or with curl:

```bash
curl -u <username>:<password> -o activity.txt \
  "https://<your-jira-domain>/activity?maxResults=500&streams=user+IS+<username>&os_authType=basic"
```


## Workflow

### Step 1 — Parse the feed

```bash
python scripts/parse_activity.py [input] [output]
# Defaults: activity.txt -> activity_parsed.csv
```

Outputs one row per activity event: `date`, `ticket`, `title`, `activity_type`, `description`.

Activity types: `Created`, `Updated`, `Commented`, `Status -> <name>`, `Created / Posted`.

### Step 2 — Estimate hours

```bash
python scripts/estimate_hours.py
# Reads: activity_parsed.csv -> Writes: time_estimates.csv
```

Groups by `(date, ticket)`. Points per event:

| Activity type | Points |
|---|---|
| `Created` | 2.0 |
| `Status -> *` | 1.5 |
| `Commented` | 1.0 |
| `Updated` / `Created / Posted` | 0.5 |

`estimated_hours = clamp(total_points × 0.5, min=0.5, max=4.0)` rounded to nearest 0.5 h.

To tune weights, edit the `WEIGHTS` dict at the top of `scripts/estimate_hours.py`.

## Output columns

`time_estimates.csv`: `date`, `ticket`, `title`, `estimated_hours`, `activity_count`, `activity_breakdown`

`activity_parsed.csv`: `date`, `ticket`, `title`, `activity_type`, `description`

