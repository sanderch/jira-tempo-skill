# Skill: Jira Activity → Time Estimates

Parses your personal Jira activity RSS feed and produces two artefacts:
1. **`activity_parsed.csv`** — every activity event with date, ticket, activity type, and description.
2. **`time_estimates.csv`** — one row per (date, ticket) with an estimated number of hours spent.

---

## Step 1 — Download the activity feed

Open this URL in a browser **while logged in to Jira** (replace `<username>` with your Jira username):

```
https://<your-jira-domain>/activity?maxResults=500&streams=user+IS+<username>&os_authType=basic&title=undefined
```

Save the raw XML response as **`activity.txt`** in this folder.  
You can do this by:
- Using *File → Save As* in the browser (choose "All Files" / plain text), or
- Running in a terminal (with basic auth):
  ```
  curl -u <username>:<password> -o activity.txt \
    "https://<your-jira-domain>/activity?maxResults=500&streams=user+IS+<username>&os_authType=basic"
  ```

> `maxResults=500` is the maximum the API allows. To cover a longer period, adjust the date range with the `dateFilter` parameter (e.g. `&dateFilter=5%20weeks`).

---

## Step 2 — Parse the feed

```bash
python parse_activity.py
```

**Input:** `activity.txt`  
**Output:** `activity_parsed.csv`

Columns:

| Column | Description |
|---|---|
| `date` | Local date and time of the activity |
| `ticket` | Jira ticket key (e.g. `AUTO-332`) |
| `title` | Ticket summary/title |
| `activity_type` | Human-readable action: `Created`, `Updated`, `Commented`, `Status -> <name>`, etc. |
| `description` | Full plain-text description of what was done |

Optional arguments:
```bash
python parse_activity.py [input_file] [output_csv]
# Defaults: activity.txt  activity_parsed.csv
```

---

## Step 3 — Estimate hours

```bash
python estimate_hours.py
```

**Input:** `activity_parsed.csv`  
**Output:** `time_estimates.csv`

Columns:

| Column | Description |
|---|---|
| `date` | Date (`YYYY-MM-DD`) |
| `ticket` | Jira ticket key |
| `title` | Ticket summary |
| `estimated_hours` | Estimated hours (0.5 – 4.0, in 0.5 h steps) |
| `activity_count` | Number of activity events that day |
| `activity_breakdown` | Semicolon-separated list of activity types |

### Scoring model

Each activity event earns points based on its type:

| Activity type | Points | Rationale |
|---|---|---|
| `Created` | 2.0 | Ticket creation involves substantial thinking |
| `Status -> *` | 1.5 | Implies real implementation or verification work |
| `Commented` | 1.0 | Investigation, analysis, or communication |
| `Updated` | 0.5 | Metadata change (label, sprint, description, link) |
| `Created / Posted` | 0.5 | File attachment |
| *(anything else)* | 0.5 | Fallback |

**Formula:**
```
hours = clamp(total_points × 0.5,  min=0.5,  max=4.0)
        rounded to the nearest 0.5 h
```

You can tune the weights by editing the `WEIGHTS` dict and `activity_weight()` function at the top of `estimate_hours.py`.

---

## File overview

```
activity.txt            ← raw Jira RSS feed (you download this)
parse_activity.py       ← Step 2: parses the feed → activity_parsed.csv
estimate_hours.py       ← Step 3: estimates hours → time_estimates.csv
activity_parsed.csv     ← generated
time_estimates.csv      ← generated
skill.md                ← this file
```

## Requirements

- Python 3.9+ (no third-party packages needed — only stdlib: `xml`, `csv`, `re`, `html`)
