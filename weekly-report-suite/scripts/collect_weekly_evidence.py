#!/usr/bin/env python3
"""Collect weekly evidence for weekly-report-suite.

No external dependencies. Produces a JSON bundle for the static dashboard,
Prometheus exporter, and Grafana provisioning. Data sources are deliberately
bounded: git metadata, session-file mtimes, CASS if available, and Hermes Kanban
rows. The collector does not read secrets files.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_ROOTS = [Path('/home/cheta/code'), Path('/home/cheta/code2')]
SESSION_SOURCES = [
    ('hermes', Path('/home/cheta/.hermes/sessions'), ['**/*']),
    ('codex', Path('/home/cheta/.codex/sessions'), ['**/*.jsonl']),
    ('claude-code', Path('/home/cheta/.claude/sessions'), ['**/*.json', '**/*.jsonl']),
    ('pi-agent', Path('/home/cheta/.pi/agent/sessions'), ['**/*.jsonl']),
]
KANBAN_DB = Path('/home/cheta/.hermes/kanban.db')


def run(cmd, cwd=None, timeout=20):
    try:
        p = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, timeout=timeout)
        return {"ok": p.returncode == 0, "code": p.returncode, "stdout": p.stdout.strip(), "stderr": p.stderr.strip()}
    except Exception as e:
        return {"ok": False, "code": -1, "stdout": "", "stderr": repr(e)}


def is_git_repo(path: Path) -> bool:
    return (path / '.git').exists()


def iter_git_repos(roots):
    seen = set()
    for root in roots:
        if not root.exists():
            continue
        for child in root.iterdir():
            if child.is_dir() and is_git_repo(child):
                rp = str(child.resolve())
                if rp not in seen:
                    seen.add(rp)
                    yield child


def git_stats(repo: Path, start: str, end: str):
    fmt = '--format=%H|%aN|%ai|%s'
    log = run(['git', 'log', f'--since={start}T00:00:00', f'--until={end}T23:59:59', fmt, '--shortstat'], cwd=repo)
    commits = 0
    insertions = 0
    deletions = 0
    files_changed = 0
    subjects = []
    if log['ok'] and log['stdout']:
        for line in log['stdout'].splitlines():
            if '|' in line and len(line.split('|')) >= 4:
                commits += 1
                subjects.append(line.split('|', 3)[3])
            elif 'file' in line and 'changed' in line:
                parts = [p.strip() for p in line.split(',')]
                for part in parts:
                    toks = part.split()
                    if not toks:
                        continue
                    try:
                        n = int(toks[0])
                    except ValueError:
                        continue
                    if 'file' in part:
                        files_changed += n
                    elif 'insertion' in part:
                        insertions += n
                    elif 'deletion' in part:
                        deletions += n
    last = run(['git', 'log', '-1', '--format=%ai'], cwd=repo)
    return {
        "commits": commits,
        "insertions": insertions,
        "deletions": deletions,
        "files_changed": files_changed,
        "subjects": subjects[:12],
        "last_activity": last['stdout'][:10] if last['ok'] else None,
    }


def cass_health():
    if not run(['bash', '-lc', 'command -v cass'], timeout=5)['ok']:
        return {"available": False, "healthy": False, "error": "cass not found"}
    out = run(['cass', 'health', '--json'], timeout=10)
    if not out['ok']:
        return {"available": True, "healthy": False, "error": out['stderr'] or out['stdout']}
    try:
        data = json.loads(out['stdout'] or '{}')
    except Exception:
        data = {"raw": out['stdout']}
    data.setdefault('available', True)
    return data


def cass_timeline(start: str, end: str):
    out = run(['cass', 'timeline', '--since', start, '--until', end, '--json', '--group-by', 'day'], timeout=30)
    if not out['ok'] or not out['stdout']:
        return {"ok": False, "error": out['stderr'] or out['stdout'], "daily_activity": [], "agent_activity": []}
    try:
        data = json.loads(out['stdout'])
    except Exception as e:
        return {"ok": False, "error": f"json parse failed: {e}", "daily_activity": [], "agent_activity": []}
    daily = []
    agents = Counter()
    if isinstance(data, dict) and isinstance(data.get('groups'), dict):
        for day, sessions in sorted(data['groups'].items()):
            sessions = sessions if isinstance(sessions, list) else []
            daily.append({"date": str(day)[:10], "sessions": len(sessions)})
            for s in sessions:
                if isinstance(s, dict):
                    agents[s.get('agent', 'unknown')] += 1
    else:
        buckets = data.get('buckets') or data.get('timeline') or data.get('items') or [] if isinstance(data, dict) else []
        if isinstance(buckets, dict):
            buckets = [{"date": k, **(v if isinstance(v, dict) else {"count": v})} for k, v in buckets.items()]
        for b in buckets if isinstance(buckets, list) else []:
            date = b.get('date') or b.get('day') or b.get('bucket') or b.get('start')
            count = b.get('sessions') or b.get('count') or b.get('session_count') or 0
            daily.append({"date": str(date)[:10], "sessions": count})
            for a in b.get('agents', []) if isinstance(b.get('agents'), list) else []:
                if isinstance(a, dict):
                    agents[a.get('agent', 'unknown')] += int(a.get('sessions') or a.get('count') or 0)
                else:
                    agents[str(a)] += 1
    return {"ok": True, "raw_shape": list(data.keys())[:20] if isinstance(data, dict) else type(data).__name__, "daily_activity": daily, "agent_activity": [{"agent": k, "sessions": v} for k, v in agents.most_common()]}


def in_range(ts: float, start_dt: datetime, end_dt: datetime) -> bool:
    dt = datetime.fromtimestamp(ts, timezone.utc)
    return start_dt <= dt <= end_dt


def session_file_fallback(start: str, end: str):
    start_dt = datetime.fromisoformat(start).replace(tzinfo=timezone.utc)
    end_dt = datetime.fromisoformat(end).replace(hour=23, minute=59, second=59, tzinfo=timezone.utc)
    daily = Counter()
    agents = Counter()
    files_seen = set()
    for agent, root, globs in SESSION_SOURCES:
        if not root.exists():
            continue
        for glob in globs:
            for p in root.glob(glob):
                if not p.is_file() or p in files_seen:
                    continue
                files_seen.add(p)
                try:
                    st = p.stat()
                except OSError:
                    continue
                if in_range(st.st_mtime, start_dt, end_dt):
                    day = datetime.fromtimestamp(st.st_mtime, timezone.utc).date().isoformat()
                    daily[day] += 1
                    agents[agent] += 1
    return {
        "ok": True,
        "source": "session-file-mtime-fallback",
        "daily_activity": [{"date": k, "sessions": v} for k, v in sorted(daily.items())],
        "agent_activity": [{"agent": k, "sessions": v} for k, v in agents.most_common()],
    }


def kanban_summary(db_path: Path = KANBAN_DB):
    empty = {"available": False, "tasks": [], "counts": {}, "done": [], "wip": [], "planned": []}
    if not db_path.exists():
        return {**empty, "error": f"missing kanban db: {db_path}"}
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""
            SELECT id, title, body, assignee, status, priority, tenant, created_at, completed_at, result
            FROM tasks
            WHERE status != 'archived'
            ORDER BY priority DESC, created_at DESC
        """).fetchall()
        conn.close()
    except Exception as e:
        return {**empty, "available": True, "error": repr(e)}
    tasks = [dict(r) for r in rows]
    counts = Counter(t.get('status') or 'unknown' for t in tasks)
    done = []
    wip = []
    planned = []
    for t in tasks:
        label = f"{t.get('title')} [{t.get('status')}]"
        status = t.get('status') or ''
        if status == 'done':
            done.append(label)
        elif status in {'running', 'ready', 'todo', 'review'}:
            wip.append(label)
        elif status in {'triage', 'scheduled', 'blocked'}:
            planned.append(label)
    return {
        "available": True,
        "db_path": str(db_path),
        "tasks": tasks[:50],
        "counts": dict(counts),
        "done": done[:10],
        "wip": wip[:10],
        "planned": planned[:10],
    }


def merge_activity(cass_result, fallback_result):
    if cass_result.get('ok') and sum(int(d.get('sessions') or 0) for d in cass_result.get('daily_activity', [])) > 0:
        cass_result['source'] = 'cass'
        return cass_result
    fallback_result['cass_error'] = cass_result.get('error')
    return fallback_result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--start', required=True, help='YYYY-MM-DD')
    ap.add_argument('--end', required=True, help='YYYY-MM-DD')
    ap.add_argument('--out', required=True)
    ap.add_argument('--roots', nargs='*', default=[str(p) for p in DEFAULT_ROOTS])
    ap.add_argument('--theme', default='')
    args = ap.parse_args()
    roots = [Path(p).expanduser() for p in args.roots]

    projects = []
    totals = defaultdict(int)
    for repo in iter_git_repos(roots):
        st = git_stats(repo, args.start, args.end)
        if st['commits'] or st['files_changed']:
            projects.append({
                "name": repo.name,
                "path": str(repo),
                "state": "active",
                "sessions": 0,
                "commits": st['commits'],
                "files_changed": st['files_changed'],
                "last_activity": st['last_activity'],
                "evidence": "git",
                "recent_commit_subjects": st['subjects'],
                "done": [],
                "wip": [],
                "planned": [],
            })
            totals['commits_total'] += st['commits']
            totals['files_changed_total'] += st['files_changed']

    ch = cass_health()
    ct = cass_timeline(args.start, args.end) if ch.get('available') else {"ok": False, "daily_activity": [], "agent_activity": [], "error": "cass unavailable"}
    sf = session_file_fallback(args.start, args.end)
    activity = merge_activity(ct, sf)
    sessions_total = sum(int(d.get('sessions') or 0) for d in activity.get('daily_activity', []))

    kb = kanban_summary()
    work_done = len(kb.get('done', []))
    work_wip = len(kb.get('wip', []))
    work_planned = len(kb.get('planned', []))

    momentum = min(100, int((sessions_total * 2) + (len(projects) * 8) + (totals['commits_total'] * 3) + min(totals['files_changed_total'], 100) * 0.25 + (work_done * 4))) if (sessions_total or projects or work_done) else None
    data = {
        "period": {"start": args.start, "end": args.end},
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "theme": args.theme,
        "summary": "Live weekly report data from git activity, session-file fallback, Hermes Kanban, and report artifacts.",
        "metrics": {
            "projects_total": len(projects),
            "sessions_total": sessions_total,
            "commits_total": totals['commits_total'],
            "files_changed_total": totals['files_changed_total'],
            "work_done": work_done,
            "work_in_progress": work_wip,
            "work_planned": work_planned,
            "momentum_score": momentum,
            "kanban_tasks_total": len(kb.get('tasks', [])),
        },
        "projects": sorted(projects, key=lambda p: (p['commits'], p['files_changed']), reverse=True),
        "done": kb.get('done', []),
        "wip": kb.get('wip', []),
        "planned": kb.get('planned', []),
        "daily_activity": activity.get('daily_activity', []),
        "agent_activity": activity.get('agent_activity', []),
        "caveats": [],
        "self_improvement": [
            "Dashboard now reads Hermes Kanban state instead of hand-only task lists.",
            "Prometheus exporter and Grafana provisioning artifacts are generated with the bundle.",
            "Session counts use CASS when populated and bounded session-file mtimes as fallback.",
        ],
        "evidence": {
            "cass_health": ch,
            "activity_source": activity.get('source'),
            "cass_timeline": {k: v for k, v in ct.items() if k != 'raw'},
            "kanban": {k: v for k, v in kb.items() if k != 'tasks'},
        },
    }
    if activity.get('source') != 'cass':
        data['caveats'].append('CASS did not provide populated session groups; session counts use bounded file-mtime fallback.')
    if not kb.get('tasks'):
        data['caveats'].append('No Hermes Kanban tasks were found; run the weekly pipeline with Kanban seeding enabled.')
    if not projects:
        data['caveats'].append('No git repositories with commits were detected in the selected window; check roots or rely on session evidence.')
    out = Path(args.out).expanduser()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=2))
    print(out)


if __name__ == '__main__':
    main()
