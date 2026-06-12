# Prior Work Audit: Reports and Dashboards

Generated while creating `weekly-report-suite`.

## CASS / session findings

CASS is installed at `/home/cheta/.local/bin/cass` and supports:

- `cass health --json`
- `cass timeline --since <date> --until <date> --json --group-by day`
- `cass search <query> --json`
- `cass export-html`

Direct CASS search for `weekly report dashboard analytics prometheus grafana` returned no matches. Broader `cass search "daily radar"` returned relevant prior work, including project_dashboard session-history design and Daily Radar context.

## Daily Radar

Path: `/home/cheta/code2/daily-radar/`

Daily Radar is the closest prior scaffold:

- `README.md` describes cross-provider daily/weekly/monthly reports with live dashboard.
- `purposes/weekly-purpose.md` defines weekly metrics: project summary, topic distribution, agent utilization, stale projects, deliverable tracking, error patterns, knowledge synthesis, commit/file audit, momentum score.
- `dashboard/index.html` is a static dashboard scaffold.
- `dashboard/server.py` is a dashboard server.
- `scripts/daily-run.sh` and `scripts/pi-radar.sh` exist.

Known caveat from the May 31 in-depth audit: Daily Radar was scaffolded but not run end-to-end; output directories and generated reports were absent at that time. Do not treat Daily Radar as operational unless a fresh run verifies output.

## project_dashboard

Prior CASS content indicates `/home/cheta/code/project_dashboard/` was built as a git project monitor and later scoped for CLI session history and live git comparison. Relevant concepts to borrow:

- Session adapter pattern for Claude Code, Codex, Qwen, Hermes, OpenCode.
- Normalized session schema: tool, start/end, cwd, project, status, models, token stats, activity.
- SQLite storage for sessions, activity, scan history, and git events.
- Live git panel using server-sent events or polling.
- Project cards with last session date and session count.

## Prometheus/Grafana

The user referred to Prometheus and "the other program"; that partner is Grafana. This skill includes a simple Prometheus exporter script so Grafana can chart weekly report metrics later.

## Existing weekly report examples

Recent local examples used for style:

- `/home/cheta/code/weekly-report-2026-05-23.md`
- `/home/cheta/code/weekly-report-2026-05-24.md`
- `/home/cheta/code/weekly-report-2026-05-31.md`
- `/home/cheta/code/weekly-report-2026-05-31-in-depth.md` for caveats and evidence discipline.

The Claude-online source examples from Aug-Nov 2025 and Jan-May 2026 establish the durable structure: Strategic Overview, Active Project Pipeline, Progress This Week, Mentor Feedback, Next Milestone, Career Positioning, signed `-A`.
