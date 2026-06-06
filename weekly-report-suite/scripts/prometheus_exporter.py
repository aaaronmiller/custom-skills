#!/usr/bin/env python3
"""Tiny Prometheus-compatible exporter for weekly-report-suite metrics."""
from __future__ import annotations
import argparse, json, time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse


def safe_label(s: str) -> str:
    return str(s).replace('\\','\\\\').replace('"','\\"').replace('\n',' ')


def load(path: Path):
    try:
        return json.loads(path.read_text())
    except Exception as e:
        return {"metrics": {}, "projects": [], "caveats": [f"failed to load metrics: {e}"]}


def prometheus_text(data):
    m = data.get('metrics', {})
    lines = [
        '# HELP weekly_report_projects_total Projects touched in weekly reporting window',
        '# TYPE weekly_report_projects_total gauge',
        f"weekly_report_projects_total {m.get('projects_total',0) or 0}",
        '# HELP weekly_report_sessions_total Sessions detected in weekly reporting window',
        '# TYPE weekly_report_sessions_total gauge',
        f"weekly_report_sessions_total {m.get('sessions_total',0) or 0}",
        '# HELP weekly_report_commits_total Git commits detected in weekly reporting window',
        '# TYPE weekly_report_commits_total gauge',
        f"weekly_report_commits_total {m.get('commits_total',0) or 0}",
        '# HELP weekly_report_files_changed_total Files changed according to git shortstat',
        '# TYPE weekly_report_files_changed_total gauge',
        f"weekly_report_files_changed_total {m.get('files_changed_total',0) or 0}",
        '# HELP weekly_report_momentum_score Heuristic momentum score 0-100',
        '# TYPE weekly_report_momentum_score gauge',
        f"weekly_report_momentum_score {m.get('momentum_score') if m.get('momentum_score') is not None else 0}",
        '# HELP weekly_report_work_items Work items by state',
        '# TYPE weekly_report_work_items gauge',
    ]
    for state, key in [('done','work_done'),('wip','work_in_progress'),('planned','work_planned')]:
        lines.append(f'weekly_report_work_items{{state="{state}"}} {m.get(key,0) or 0}')
    lines += [
        '# HELP weekly_report_kanban_tasks_total Hermes Kanban tasks visible to the weekly report bundle',
        '# TYPE weekly_report_kanban_tasks_total gauge',
        f"weekly_report_kanban_tasks_total {m.get('kanban_tasks_total',0) or 0}",
    ]
    lines += ['# HELP weekly_report_project_commits Commits by project', '# TYPE weekly_report_project_commits gauge']
    for p in data.get('projects', []):
        name = safe_label(p.get('name','unknown'))
        lines.append(f'weekly_report_project_commits{{project="{name}"}} {p.get("commits",0) or 0}')
    lines += ['# HELP weekly_report_project_files_changed Files changed by project', '# TYPE weekly_report_project_files_changed gauge']
    for p in data.get('projects', []):
        name = safe_label(p.get('name','unknown'))
        lines.append(f'weekly_report_project_files_changed{{project="{name}"}} {p.get("files_changed",0) or 0}')
    return '\n'.join(lines) + '\n'


class Handler(BaseHTTPRequestHandler):
    metrics_path: Path = Path('weekly-metrics.json')
    def do_GET(self):
        data = load(self.metrics_path)
        path = urlparse(self.path).path
        if path == '/metrics':
            body = prometheus_text(data).encode()
            self.send_response(200); self.send_header('Content-Type','text/plain; version=0.0.4'); self.send_header('Content-Length',str(len(body))); self.end_headers(); self.wfile.write(body)
        elif path == '/data':
            body = json.dumps(data, indent=2).encode()
            self.send_response(200); self.send_header('Content-Type','application/json'); self.send_header('Content-Length',str(len(body))); self.end_headers(); self.wfile.write(body)
        else:
            body = b'weekly-report-suite exporter: use /metrics or /data\n'
            self.send_response(200); self.send_header('Content-Type','text/plain'); self.send_header('Content-Length',str(len(body))); self.end_headers(); self.wfile.write(body)
    def log_message(self, fmt, *args):
        return


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--metrics', required=True)
    ap.add_argument('--host', default='127.0.0.1')
    ap.add_argument('--port', type=int, default=9109)
    args = ap.parse_args()
    Handler.metrics_path = Path(args.metrics).expanduser()
    httpd = HTTPServer((args.host, args.port), Handler)
    print(f'weekly-report-suite Prometheus exporter on http://{args.host}:{args.port}/metrics using {Handler.metrics_path}')
    httpd.serve_forever()

if __name__ == '__main__':
    main()
