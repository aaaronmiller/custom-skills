# Weekly Report Dashboard and Metrics Spec

## Goal

Create a weekly project-history site that pairs a written report with analytics and graphics. The dashboard should become a living record of work done, work in progress, and work planned.

The written component contextualizes the graphics; the graphics should not attempt to replace narrative judgment.

## Sections

1. **Hero / Week Summary**
   - Week ending date
   - Theme
   - Momentum score
   - Evidence status: verified / partial / estimated

2. **Written Reports**
   - Dad-facing report panel
   - Personal report panel
   - Toggle or side-by-side layout

3. **Work State Board**
   - Done
   - In progress
   - Planned / carried over

4. **Project Activity**
   - Project name
   - State
   - Sessions
   - Commits
   - Files changed
   - Last activity
   - Evidence level

5. **Agent / Session Activity**
   - Agent usage counts if CASS data exists
   - Session count by day
   - Tool/provider notes if available

6. **Git and Filesystem Activity**
   - Commits by project
   - Files changed by project
   - New docs/specs/tests if detectable

7. **Trend Placeholders**
   - Week-over-week projects touched
   - Week-over-week sessions
   - Momentum score trend
   - Carry-over task closure rate

8. **Caveats and Evidence Gaps**
   - Missing CASS data
   - Unrun pipelines
   - Designed-but-not-tested components
   - Manual user-provided metrics

9. **Self-Improvement Backlog**
   - New metrics to add
   - Categories needing refinement
   - Visualizations to improve
   - Scripts/data sources to harden

## Prometheus + Grafana

Prometheus is the metrics scraper/storage layer; Grafana is the dashboard/visualization partner. The included `scripts/prometheus_exporter.py` exposes `/metrics` in Prometheus text format from a weekly metrics JSON file.

Recommended local flow:

```bash
python3 scripts/prometheus_exporter.py --metrics weekly-metrics.json --port 9109
# Prometheus scrape config target: localhost:9109
# Grafana reads from Prometheus and charts time series.
```

Metric naming convention:

```text
weekly_report_projects_total
weekly_report_commits_total
weekly_report_files_changed_total
weekly_report_sessions_total
weekly_report_work_items{state="done|wip|planned"}
weekly_report_momentum_score
weekly_report_project_commits{project="..."}
weekly_report_project_files_changed{project="..."}
```

## Data model

The dashboard JSON should contain:

```json
{
  "period": {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"},
  "generated_at": "ISO timestamp",
  "theme": "...",
  "summary": "...",
  "metrics": {
    "projects_total": 0,
    "sessions_total": 0,
    "commits_total": 0,
    "files_changed_total": 0,
    "work_done": 0,
    "work_in_progress": 0,
    "work_planned": 0,
    "momentum_score": null
  },
  "projects": [
    {
      "name": "daily-radar",
      "path": "/home/cheta/code2/daily-radar",
      "state": "designed/scaffolded",
      "sessions": 0,
      "commits": 0,
      "files_changed": 0,
      "last_activity": "YYYY-MM-DD",
      "evidence": "verified|estimated|manual",
      "done": [],
      "wip": [],
      "planned": []
    }
  ],
  "agent_activity": [],
  "daily_activity": [],
  "caveats": [],
  "self_improvement": []
}
```

## Improvement loop

Each week, attempt one dashboard improvement. Examples:

- Add a new classification category.
- Improve stale-project detection.
- Add a Prometheus metric.
- Add a new chart to the static dashboard.
- Improve the carry-over task parser.
- Add a manual corrections section so Aaron can override noisy data.
