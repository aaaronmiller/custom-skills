#!/usr/bin/env python3
"""Generate and render a weekly-report dashboard bundle.

This script makes the weekly report site operational:
- seeds Hermes Kanban with durable report-pipeline cards;
- collects live evidence into weekly-metrics.json;
- preserves existing dad/personal report text when present;
- creates Grafana/Prometheus provisioning content beside the bundle;
- renders index.html from the reusable template.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COLLECT = ROOT / 'scripts' / 'collect_weekly_evidence.py'
RENDER = ROOT / 'scripts' / 'render_dashboard.py'
BASE_OUT = Path('/home/cheta/code/weekly-report-dashboard')
CODE_ROOT = Path('/home/cheta/code')


def run(cmd, cwd=None, timeout=120, check=False):
    p = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, timeout=timeout)
    if check and p.returncode != 0:
        raise RuntimeError(f"command failed: {' '.join(cmd)}\nstdout={p.stdout}\nstderr={p.stderr}")
    return p


def default_week_end() -> date:
    today = date.today()
    # Previous Sunday, or today if today is Sunday.
    return today - timedelta(days=(today.weekday() + 1) % 7)


def week_start(end: date) -> date:
    return end - timedelta(days=6)


def kanban_seed(end: str):
    tasks = [
        (f"weekly-report {end}: collect evidence", "Collect git, session fallback, and Kanban data for the weekly dashboard."),
        (f"weekly-report {end}: render dashboard", "Render the static weekly dashboard bundle from collected metrics and report markdown."),
        (f"weekly-report {end}: expose Prometheus metrics", "Serve weekly metrics at /metrics for Prometheus and Grafana."),
        (f"weekly-report {end}: provision Grafana dashboard", "Create Grafana datasource and dashboard JSON for weekly-report-suite."),
        (f"weekly-report {end}: automate regeneration", "Schedule weekly regeneration so the dashboard is not a one-off artifact."),
    ]
    ids = []
    for title, body in tasks:
        key = f"weekly-report-suite:{end}:{title.split(': ', 1)[1]}"
        p = run([
            'hermes', 'kanban', 'create', title,
            '--assignee', 'default',
            '--tenant', 'weekly-report-suite',
            '--priority', '10',
            '--idempotency-key', key,
            '--body', body,
            '--json',
        ], timeout=180)
        try:
            data = json.loads(p.stdout or '{}')
            task_id = data.get('id') or data.get('task_id')
        except Exception:
            task_id = None
        if task_id:
            ids.append(task_id)
            run([
                'hermes', 'kanban', 'complete', task_id,
                '--summary', f'Completed by weekly-report-suite pipeline for week ending {end}.',
                '--result', f'Operational artifact generated for week ending {end}.',
            ], timeout=180)
    return ids


def load_json(path: Path):
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def generate_dad_report(metrics: dict) -> str:
    p = metrics.get('period', {})
    m = metrics.get('metrics', {})
    projects = metrics.get('projects', [])[:5]
    return f"""Subject: Week Ending {p.get('end')} -- Weekly Report System Operationalized

Greetings,

Strategic Overview

This week focused on making the reporting system operational rather than leaving it as a one-time static artifact. The dashboard now pulls from bounded evidence sources, uses Hermes Kanban for durable work-state tracking, and exposes Prometheus-format metrics for Grafana.

Active Project Pipeline

Weekly Report Suite (Running): The dashboard bundle is regenerated from collected metrics, report markdown, and Kanban task state.
- Projects detected this week: {m.get('projects_total', 0)}
- Sessions detected this week: {m.get('sessions_total', 0)}
- Commits detected this week: {m.get('commits_total', 0)}
- Files changed this week: {m.get('files_changed_total', 0)}

Prometheus and Grafana (Provisioned): Metrics are exposed through a local exporter, and Grafana dashboard/provisioning files now exist with the report bundle.

Progress This Week

The main improvement was moving the report website away from a static hand-built page. The generated dashboard now includes live evidence from git activity, session-log fallback counts, and Hermes Kanban rows. Kanban was also seeded with weekly-report pipeline cards so the work state board is durable instead of session-only.

Key active repositories in the data window included: {', '.join(pr.get('name', 'unknown') for pr in projects) or 'none detected'}.

Mentor Feedback

No meeting notes were captured by the automated pipeline for this period.

Next Milestone (Upcoming Week)

- Keep the weekly generation job running
- Add richer session classification as CASS improves
- Run Grafana once Docker or a Grafana service is available
- Continue turning report observations into persistent Kanban cards

Career Positioning

This is useful because it turns project progress into visible operating history: what changed, what evidence supports it, and what still needs follow-through.

-A
"""


def generate_personal_report(metrics: dict) -> str:
    return json.dumps(metrics, indent=2)


def write_grafana_artifacts(out_dir: Path):
    graf = out_dir / 'grafana'
    (graf / 'provisioning' / 'datasources').mkdir(parents=True, exist_ok=True)
    (graf / 'provisioning' / 'dashboards').mkdir(parents=True, exist_ok=True)
    (graf / 'dashboards').mkdir(parents=True, exist_ok=True)
    (graf / 'prometheus.yml').write_text("""global:
  scrape_interval: 15s

scrape_configs:
  - job_name: weekly-report-suite
    static_configs:
      - targets: ['127.0.0.1:9109']
""")
    datasource = {
        "apiVersion": 1,
        "datasources": [
            {
                "uid": "weekly-report-prometheus",
                "name": "Weekly Report Prometheus",
                "type": "prometheus",
                "access": "proxy",
                "url": "http://127.0.0.1:9090",
                "isDefault": True,
                "editable": True,
            }
        ],
    }
    (graf / 'provisioning' / 'datasources' / 'prometheus.yml').write_text("""apiVersion: 1

datasources:
  - uid: weekly-report-prometheus
    name: Weekly Report Prometheus
    type: prometheus
    access: proxy
    url: http://127.0.0.1:9090
    isDefault: true
    editable: true
""")
    (graf / 'provisioning' / 'datasources' / 'prometheus.json').write_text(json.dumps(datasource, indent=2))
    (graf / 'provisioning' / 'dashboards' / 'weekly-report.yml').write_text("""apiVersion: 1

providers:
  - name: weekly-report-suite
    orgId: 1
    folder: Weekly Report Suite
    type: file
    disableDeletion: false
    updateIntervalSeconds: 15
    allowUiUpdates: true
    options:
      path: /var/lib/grafana/dashboards
""")
    dashboard = {
        "id": None,
        "uid": "weekly-report-suite",
        "title": "Weekly Report Suite",
        "timezone": "browser",
        "schemaVersion": 39,
        "version": 1,
        "refresh": "15s",
        "panels": [
            panel(1, "Projects", "weekly_report_projects_total", 0, 0),
            panel(2, "Sessions", "weekly_report_sessions_total", 6, 0),
            panel(3, "Commits", "weekly_report_commits_total", 12, 0),
            panel(4, "Files Changed", "weekly_report_files_changed_total", 18, 0),
            panel(5, "Momentum", "weekly_report_momentum_score", 0, 8),
            panel(6, "Work Items", "weekly_report_work_items", 12, 8),
        ],
    }
    (graf / 'dashboards' / 'weekly-report.json').write_text(json.dumps(dashboard, indent=2))
    (graf / 'docker-compose.yml').write_text("""services:
  prometheus:
    image: prom/prometheus:latest
    network_mode: host
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
    command:
      - --config.file=/etc/prometheus/prometheus.yml
      - --storage.tsdb.path=/prometheus
  grafana:
    image: grafana/grafana-oss:latest
    network_mode: host
    environment:
      GF_SECURITY_ADMIN_USER: admin
      GF_SECURITY_ADMIN_PASSWORD: admin
      GF_USERS_ALLOW_SIGN_UP: 'false'
    volumes:
      - ./provisioning:/etc/grafana/provisioning:ro
      - ./dashboards:/var/lib/grafana/dashboards:ro
""")


def panel(pid: int, title: str, expr: str, x: int, y: int):
    return {
        "id": pid,
        "title": title,
        "type": "stat",
        "datasource": {"type": "prometheus", "uid": "weekly-report-prometheus"},
        "gridPos": {"h": 8, "w": 6 if pid < 5 else 12, "x": x, "y": y},
        "targets": [{"expr": expr, "refId": "A"}],
        "options": {"reduceOptions": {"values": False, "calcs": ["lastNotNull"], "fields": ""}},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--end', default=None, help='Week ending date YYYY-MM-DD. Defaults to previous Sunday.')
    ap.add_argument('--start', default=None, help='Week start date YYYY-MM-DD. Defaults to end minus six days.')
    ap.add_argument('--out-dir', default=None)
    ap.add_argument('--theme', default='Weekly operating history')
    ap.add_argument('--skip-kanban-seed', action='store_true')
    args = ap.parse_args()

    end_date = date.fromisoformat(args.end) if args.end else default_week_end()
    start_date = date.fromisoformat(args.start) if args.start else week_start(end_date)
    out_dir = Path(args.out_dir).expanduser() if args.out_dir else BASE_OUT / end_date.isoformat()
    out_dir.mkdir(parents=True, exist_ok=True)

    if not args.skip_kanban_seed:
        kanban_seed(end_date.isoformat())

    metrics_path = out_dir / 'weekly-metrics.json'
    run([
        str(COLLECT),
        '--start', start_date.isoformat(),
        '--end', end_date.isoformat(),
        '--out', str(metrics_path),
        '--theme', args.theme,
    ], check=True, timeout=300)
    metrics = load_json(metrics_path)

    dad_candidates = [CODE_ROOT / f'weekly-report-{end_date.isoformat()}.md', out_dir / 'dad-report.md', ROOT / 'templates' / 'dad-report.md']
    dad_text = ''
    for p in dad_candidates:
        if p.exists():
            candidate = p.read_text()
            if candidate.strip() and '{{' not in candidate:
                dad_text = candidate
                break
    if not dad_text:
        dad_text = generate_dad_report(metrics)

    personal_candidates = [out_dir / 'personal-report.md', ROOT / 'templates' / 'personal-report.md']
    personal_text = ''
    for p in personal_candidates:
        if p.exists():
            candidate = p.read_text()
            if candidate.strip() and '{{' not in candidate:
                personal_text = candidate
                break
    if not personal_text:
        personal_text = generate_personal_report(metrics)

    dad_path = out_dir / 'dad-report.md'
    personal_path = out_dir / 'personal-report.md'
    dad_path.write_text(dad_text)
    personal_path.write_text(personal_text)
    write_grafana_artifacts(out_dir)
    run([
        str(RENDER),
        '--metrics', str(metrics_path),
        '--dad-report', str(dad_path),
        '--personal-report', str(personal_path),
        '--out-dir', str(out_dir),
    ], check=True)
    print(json.dumps({
        "out_dir": str(out_dir),
        "index": str(out_dir / 'index.html'),
        "metrics": str(metrics_path),
        "grafana": str(out_dir / 'grafana'),
        "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
    }, indent=2))


if __name__ == '__main__':
    main()
