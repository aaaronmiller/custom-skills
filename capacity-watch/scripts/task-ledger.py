#!/usr/bin/env python3
"""Offline task summaries and full redacted Living Documents run records.

No dispatch, ingestion, network, or model calls. Missing evidence stays blank.
CSV overflow fails before publication instead of dropping tasks or prompt excerpts.
"""
import argparse
import csv
import hashlib
import io
import json
import re
import socket
import sqlite3
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, '/home/cheta/code/custom-skills/project-archive/scripts')
from _lib import redact

STATE = Path.home() / '.local/state/capacity-watch'
RUNS = Path('/home/cheta/LIVING_DOCUMENTS/projects/masterplan/runs')
TASKS = RUNS.parent / 'tasks.md'
SESSION = 'aa76eea5-1ba8-47d3-8585-7efb52d1c6ec'
WORKFLOWS = Path.home() / '.claude/projects/-home-cheta-tmp' / SESSION / 'subagents/workflows'
DISPATCH = Path('/tmp/claude-1000/-home-cheta-tmp') / SESSION / 'scratchpad/dispatch'
MAX_BYTES = 256_000
FIELDS = ('task_key source host title project ld_task_ids outcome started ended duration_min models effort '
          'tokens_in tokens_out cache_read cache_write cost_usd billing turns subagents tool_errors api_errors '
          'api_retries docs outputs out_count brief_excerpt result_excerpt ld_path tokens_total phases labels').split()
HOSTS = {'big': 'big-surface', 'Cheta-surface-studio': 'big-surface',
         'omarchy': 'peer', 'little': 'peer', 'peer': 'peer', 'big-surface': 'big-surface'}
PATH_RE = re.compile(r'/(?:home|tmp|mnt|work|opt|var)/[^\s`<>\[\]"\'|;,()]+')


def clean(value):
    if isinstance(value, str):
        return redact(value)
    if isinstance(value, list):
        return [clean(x) for x in value]
    if isinstance(value, dict):
        return {redact(str(k)): clean(v) for k, v in value.items()}
    return value


def read(path):
    return path.read_text(encoding='utf-8', errors='replace') if path.exists() else ''


def events(path):
    for line in read(path).splitlines():
        try:
            obj = json.loads(line)
        except ValueError:
            continue  # Active writers can leave a partial trailing line.
        if isinstance(obj, dict):
            yield obj


def text(value):
    return value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2)


def iso(value):
    if value in (None, ''):
        return ''
    try:
        dt = (datetime.fromtimestamp(value, timezone.utc) if isinstance(value, (float, int))
              else datetime.fromisoformat(value.replace('Z', '+00:00')))
        return dt.replace(tzinfo=dt.tzinfo or timezone.utc).astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')
    except (ValueError, TypeError, OverflowError):
        return ''


def duration(start, end):
    if start and end:
        return round(max(0, (datetime.fromisoformat(end.replace('Z', '+00:00')) -
                             datetime.fromisoformat(start.replace('Z', '+00:00'))).total_seconds()) / 60, 3)
    return None


def outcome(exit_code=None, is_error=None, subtype='', running=None):
    sub = str(subtype or '').lower()
    if any(x in sub for x in ('max_turn', 'max_budget', 'partial', 'interrupt', 'cancel', 'usage_limit')):
        return 'partial'
    if is_error or (exit_code is not None and str(exit_code) not in ('', '0')) or any(x in sub for x in ('error', 'fail')):
        return 'failed'
    if str(exit_code) == '0' or sub in ('success', 'done', 'completed'):
        return 'done'
    if running is False:
        return 'unknown'  # finished, but no exit or result evidence
    return 'running'


def project(brief):
    m = re.search(r'/home/cheta/(?:code|LIVING_DOCUMENTS/projects)/([\w.-]+)', brief)
    return m[1].rstrip('.') if m else 'masterplan'


def task_ids(task_text):
    # Only definitions, not IDs mentioned incidentally in evidence prose.
    return set(re.findall(r'(?m)^\s*(?:- \[[ xX]\]\s*|\|\s*)([A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-\d+[a-z]?|[A-Z][A-Z0-9]*-[A-Z]+\d+)\b', task_text))


def extract_ids(brief, known):
    return sorted(k for k in known if re.search(r'(?<![\w-])' + re.escape(k) + r'(?![\w-])', brief))


def docs(brief, remote=False):
    found = []
    for m in PATH_RE.finditer(brief):
        p = m[0].rstrip('.:')
        context = re.split(r'[.\n]', brief[max(0, m.start()-45):m.start()])[-1].lower() + p.lower()
        is_doc = p.endswith(('.md', '.html', '.json'))
        named_plan = bool(re.search(r'\b(?:specs?|plans?)\b', context))
        exists = Path(p).exists()
        if (is_doc and (exists or remote)) or named_plan:
            mark = '' if exists else (' [remote]' if remote else ' [not found]')
            if p + mark not in found:
                found.append(p + mark)
    return found


def effort(brief):
    m = re.search(r'(?:reasoning[ _]effort|model_reasoning_effort|--effort|\beffort)\s*[=:]?\s*[\"\']?(none|minimal|low|medium|high|xhigh|max|ultra)\b', brief, re.I)
    return m[1].lower() if m else ''


def record(source, host, job, brief='', known=()):
    r = dict.fromkeys(FIELDS)
    r.update(task_key=f'{source}:{host}:{job}', source=source, host=host, title=job,
             project=project(brief), ld_task_ids=extract_ids(brief, known), outcome='running',
             started='', ended='', models=[], effort=effort(brief), docs=docs(brief, source == 'mesh'),
             outputs=[], out_count=None, billing='subscription', phases=[], labels=[], notes=[],
             brief=brief, result='', brief_excerpt='', result_excerpt='')
    return r


def set_usage(r, usage):
    if not usage:
        return
    for dest, src in [('tokens_in', 'input_tokens'), ('tokens_out', 'output_tokens'),
                      ('cache_read', 'cache_read_input_tokens'), ('cache_write', 'cache_creation_input_tokens')]:
        r[dest] = usage.get(src, 0)


def mesh_records(summary_dir, snapshots, known):
    latest = {}
    for s in events(snapshots):
        h = HOSTS.get(s.get('host'), s.get('host', 'unknown'))
        latest[(h, s.get('job', 'unknown'))] = s
    jobs = {}
    for p in sorted(summary_dir.glob('remote-*.json')):
        d = json.loads(read(p))
        h = HOSTS.get(d.get('host'), d.get('host', p.stem[7:]))
        for j in d.get('jobs', []):
            # The remote collector also walks .pytest_cache, which is not a job.
            if j['job'].startswith('.') and not j.get('brief') and not j.get('log_bytes'):
                continue
            jobs[(h, j['job'])] = j
    for h, job in sorted(jobs.keys() | latest.keys()):
        j, s = jobs.get((h, job), {}), latest.get((h, job), {})
        result = j.get('result') or {}
        r = record('mesh', h, job, j.get('brief', ''), known)
        r['billing'] = 'unknown'
        r['models'] = sorted(j.get('models') or ([s['model']] if s.get('model') else []))
        r.update(started=iso(j.get('first_ts')), ended=iso(j.get('last_ts')),
                 result=result.get('text', ''), out_count=j.get('out_count'), outputs=j.get('out_files', []))
        for k in ('subagents', 'tool_errors', 'api_errors', 'api_retries'):
            r[k] = j.get(k)
        r['outcome'] = outcome(j.get('exit') if j.get('exit') is not None else s.get('exit'),
                               result.get('is_error', s.get('is_error')), result.get('subtype'), s.get('running'))
        ms = result.get('duration_ms', s.get('duration_ms'))
        r['duration_min'] = round(ms / 60000, 3) if ms is not None else duration(r['started'], r['ended'])
        if not r['ended'] and r['outcome'] != 'running' and s.get('ts'):
            r['ended'] = iso(s['ts'])
            r['notes'].append('End time is the last telemetry observation, not an exact completion timestamp.')
        if not r['started'] and r['ended'] and ms is not None:
            r['started'] = iso(datetime.fromisoformat(r['ended'].replace('Z', '+00:00')).timestamp() - ms / 1000)
            r['notes'].append('Start time inferred from telemetry end observation minus reported duration.')
        if r['outcome'] == 'running':
            r['ended'] = ''
        r['turns'] = result.get('num_turns', s.get('turns'))
        r['cost_usd'] = result.get('total_cost_usd', s.get('cost_usd'))
        set_usage(r, result.get('usage'))
        for k, sk in [('tokens_in', 'input_tokens'), ('tokens_out', 'output_tokens'), ('cache_read', 'cache_read'), ('cache_write', 'cache_write')]:
            if r[k] is None:
                r[k] = s.get(sk)
        r['notes'].append('Mesh cost is reported list price; the cached summary does not identify the billing route. Result text is limited by the remote collector to 4000 characters.')
        yield r


def workflow_records(root, known, host):
    for p in sorted(root.glob('*/journal.jsonl')):
        rows = list(events(p))
        starts = [e for e in rows if e.get('type') == 'started']
        ends = [e for e in rows if e.get('type') in ('result', 'error', 'failed')]
        agents = sorted({e['agentId'] for e in starts if e.get('agentId')})
        r = record('workflow', host, p.parent.name, known=known)
        stamps, briefs, models, calls, files = [], [], set(), {}, set()
        tool_errors = api_errors = api_retries = 0
        for agent in agents:
            for e in events(p.parent / f'agent-{agent}.jsonl'):
                if iso(e.get('timestamp')):
                    stamps.append(iso(e['timestamp']))
                m = e.get('message') or {}
                content = m.get('content', '')
                if e.get('type') == 'user' and isinstance(content, str) and content not in briefs:
                    briefs.append(content)
                if e.get('type') == 'assistant':
                    if m.get('model'):
                        models.add(m['model'])
                    if m.get('usage'):
                        calls[(agent, m.get('id', e.get('uuid')))] = m['usage']
                    api_errors += bool(e.get('error') or m.get('error'))
                api_retries += e.get('subtype') == 'api_retry'
                for c in content if isinstance(content, list) else []:
                    if not isinstance(c, dict):
                        continue
                    tool_errors += c.get('type') == 'tool_result' and bool(c.get('is_error'))
                    if c.get('type') == 'tool_use' and c.get('name') in ('Write', 'Edit', 'MultiEdit'):
                        f = (c.get('input') or {}).get('file_path')
                        if f:
                            files.add(f)
        # Keep the complete relayed user request and computed agent instructions.
        brief = '\n\n'.join(briefs)
        r.update(brief=brief, project=project(brief), ld_task_ids=extract_ids(brief, known), docs=docs(brief),
                 phases=list(dict.fromkeys(e['phase'] for e in starts if e.get('phase'))),
                 labels=list(dict.fromkeys(e['label'] for e in starts if e.get('label'))),
                 subagents=len(agents), models=sorted(models), tool_errors=tool_errors,
                 api_errors=api_errors, api_retries=api_retries, turns=len(calls) if calls else None,
                 outputs=sorted(files), out_count=len(files), effort=effort(brief))
        r['title'] = p.parent.name + (': ' + ', '.join(r['phases']) if r['phases'] else '')
        pending = {e.get('agentId', e.get('key')) for e in starts} - {e.get('agentId', e.get('key')) for e in ends}
        failed = any(e.get('type') in ('error', 'failed') or e.get('is_error') for e in ends)
        r['outcome'] = 'partial' if failed and ends else 'running'
        if starts and not pending and not failed:
            r['outcome'] = 'done'
        if failed and all(e.get('type') in ('error', 'failed') for e in ends):
            r['outcome'] = 'failed'
        if stamps:
            r['started'] = min(stamps)
            r['ended'] = max(stamps) if r['outcome'] != 'running' else ''
            r['duration_min'] = duration(min(stamps), max(stamps))
        if calls:
            set_usage(r, {k: sum(u.get(k, 0) or 0 for u in calls.values()) for k in
                         ('input_tokens', 'output_tokens', 'cache_read_input_tokens', 'cache_creation_input_tokens')})
        r['result'] = text(ends[-1].get('result', ends[-1].get('error', ''))) if ends else ''
        r['notes'].append('Workflow completion means every launched agent has a result. Timing and tokens come from adjacent agent transcripts; cost is unavailable. Output paths are observed Write/Edit targets, not proof that each write succeeded.')
        yield r


def codex_groups(db):
    groups = defaultdict(list)
    if db.exists():
        with sqlite3.connect(f'file:{db}?mode=ro', uri=True) as con:
            con.row_factory = sqlite3.Row
            for row in con.execute("SELECT * FROM calls WHERE harness='codex' ORDER BY ts"):
                groups[(row['host'], row['session_id'])].append(dict(row))
    return groups


def add_calls(r, rows):
    if not rows:
        return
    r['models'] = sorted({x['model'] for x in rows if x['model']})
    for dest, col in [('tokens_in', 'tokens_in'), ('tokens_out', 'tokens_out'), ('cache_read', 'tokens_cache_read'),
                      ('cache_write', 'tokens_cache_write'), ('cost_usd', 'list_cost_usd')]:
        vals = [x[col] for x in rows if x[col] is not None]
        r[dest] = sum(vals) if len(vals) == len(rows) else None
    r['turns'] = len(rows)
    r['started'] = iso(rows[0]['ts'])
    r['notes'].append('Call-ledger metrics cover recorded calls only; no session completion or tool/subagent counts are recorded there.')


def codex_records(dispatch, db, known, host):
    groups = codex_groups(db)
    used = set()
    briefs = {p.name.split('-')[0].split('.')[0]: p for p in sorted(dispatch.glob('c*.md'))}
    logs = list(sorted(dispatch.glob('c*.log')))
    for key, p in briefs.items():
        if not any(log.stem.split('-')[0] == key for log in logs):
            logs.append(p.with_suffix('.log'))
    for p in logs:
        prefix = p.stem.split('-')[0]
        brief = read(briefs[prefix]) if prefix in briefs else ''
        raw = read(p)
        header = raw[:5000]
        sid = re.search(r'^session id:\s*(\S+)', header, re.M)
        matched = [(h, s) for h, s in groups if sid and s == sid[1]]
        h = matched[0][0] if len(matched) == 1 else host
        r = record('codex', h, p.stem, brief, known)
        r['title'] = briefs[prefix].stem if prefix in briefs else p.stem
        if '-' in p.stem:
            r['title'] += ' (' + p.stem + ')'
        if len(matched) == 1:
            add_calls(r, groups[matched[0]])
            used.add(matched[0])
        model = re.search(r'^model:\s*(\S+)', header, re.M)
        if model:
            r['models'] = sorted(set(r['models']) | {model[1]})
        r['effort'] = effort(header) or effort(brief)
        stamps = re.findall(r'(?m)^(\d{4}-\d\d-\d\dT[\d:.]+Z)', raw)
        if stamps:
            r['started'] = iso(stamps[0])
        terminal = re.search(r'(?m)^EXIT[ \t]+(-?\d+)[ \t]*\s*\Z', raw)
        totals = list(re.finditer(r'(?m)^tokens used[ \t]*\n([\d,]+)[ \t]*\n?(?:EXIT[ \t]+-?\d+[ \t]*)?\s*\Z', raw))
        if terminal:
            # Some wrappers append the final answer again after the CLI total.
            # An explicit terminal EXIT permits the last near-tail total; an
            # active log must have a terminal token footer to establish one.
            totals = list(re.finditer(r'(?m)^tokens used[ \t]*\n([\d,]+)[ \t]*$', raw[-20000:]))
        # Restrict error classification to terminal output, not quoted source/tool output.
        tail = raw[-20000:] if terminal else raw[-1500:]
        limit = bool((terminal or totals) and re.search(r'^ERROR:.*(?:usage limit|quota)', tail, re.M | re.I))
        r['outcome'] = outcome(terminal[1] if terminal else None, subtype='usage_limit' if limit and (totals or r['turns']) else '')
        if totals:
            r['tokens_total'] = int(totals[-1][1].replace(',', ''))
            if r['outcome'] == 'running':
                r['outcome'] = 'done'
        if r['outcome'] != 'running' and p.exists():
            r['ended'] = iso(p.stat().st_mtime)
            r['notes'].append('End time is log modification time, an approximate completion time.')
        r['duration_min'] = duration(r['started'], r['ended'])
        # Codex labels the final answer with a standalone codex line.
        answers = re.split(r'(?m)^codex\s*$', raw)
        if len(answers) > 1 and r['outcome'] != 'running':
            r['result'] = re.split(r'(?m)^tokens used\s*$|^EXIT\s+\d+\s*$', answers[-1])[0].strip()
        elif limit:
            r['result'] = 'Stopped at the subscription usage limit. No final answer was recorded.'
        if r['result'] and not limit:
            r['outputs'] = sorted({m[0].rstrip('.:') for m in PATH_RE.finditer(r['result']) if Path(m[0].rstrip('.:')).is_file()})
            r['out_count'] = len(r['outputs'])
            r['notes'].append('Output paths are existing files named in the final answer, not a complete filesystem change audit.')
        r['notes'].append('Codex total tokens are preserved separately; they are not treated as output tokens. Missing call-ledger matches leave split usage and list cost unknown. Tool failures and subagents are not inferred from arbitrary console text.')
        yield r
    for (h, sid), rows in sorted(groups.items()):
        if (h, sid) in used:
            continue
        r = record('codex', h, sid, known=known)
        r['title'] = 'Codex session ' + sid[:8]
        add_calls(r, rows)
        # Call outcomes describe calls, not task success. A historical session with
        # no terminal evidence is unknown, never manufactured into a completed task.
        r['outcome'] = 'unknown'
        r['notes'].append('Unmatched historical session. Brief, final result and terminal status unavailable. Last observed call: ' + rows[-1]['ts'])
        yield r


def slug(s):
    return re.sub(r'[^a-z0-9.-]+', '-', s.lower()).strip('.-') or 'unknown'


def finalize(records, runs):
    names = defaultdict(list)
    result = []
    for r in records:
        key = r['task_key']
        r = clean(r)
        if r['task_key'] != key:
            r['task_key'] = f"{r['source']}:{r['host']}:id-{hashlib.sha256(key.encode()).hexdigest()[:16]}"
        r['brief_excerpt'] = r['brief'][:1200]
        r['result_excerpt'] = r['result'][:600]
        name = f"{r['started'][:10] or 'undated'}-{r['source']}-{slug(r['task_key'].split(':', 2)[-1])}"
        names[name].append(r)
        result.append(r)
    for name, rs in names.items():
        for r in rs:
            suffix = '-' + slug(r['host']) if len(rs) > 1 else ''
            r['ld_path'] = str(runs / (name + suffix + '.md'))
    return sorted(result, key=lambda r: (r['started'], r['task_key']), reverse=True)


def flat(v):
    if v is None:
        return ''
    return '; '.join(str(x) for x in v) if isinstance(v, list) else str(v)


def csv_bytes(records, limit=MAX_BYTES):
    out = io.StringIO(newline='')
    w = csv.DictWriter(out, FIELDS, extrasaction='ignore')
    w.writeheader()
    for r in records:
        row = {k: flat(v[:20] if k == 'outputs' else v) for k, v in r.items()}
        # Reapply at the serialization boundary, even for synthetic/external callers.
        w.writerow(clean(row))
    data = out.getvalue().encode('utf-8')
    if len(data) >= limit:
        raise ValueError(f'tasks.csv would be {len(data)} bytes (limit {limit}); full task coverage retained, publication refused')
    return data


def fence(s):
    ticks = '`' * max(3, 1 + max((len(x) for x in re.findall(r'`+', s)), default=0))
    return ticks + '\n' + s + '\n' + ticks


def cell(s):
    return flat(s).replace('|', '&#124;').replace('\n', '<br>')


def page(r):
    fm = {k: r[k] for k in ('title', 'task_key', 'project', 'ld_task_ids', 'outcome')}
    fm['updated'] = (r['ended'] or r['started'] or '')[:10] or 'unknown'
    front = '\n'.join(k + ': ' + json.dumps(v, ensure_ascii=False) for k, v in fm.items())
    metrics = [k for k in FIELDS if k not in ('title', 'project', 'ld_task_ids', 'docs', 'outputs', 'brief_excerpt', 'result_excerpt', 'ld_path', 'notes')]
    purpose = r['brief'].split('\n\n')[0] if r['brief'] else 'Purpose unavailable in the supplied source records.'
    body = f'---\n{front}\n---\n\n# {r["title"]}\n\n## Purpose\n\n{fence(purpose)}\n\n## Prompt\n\n{fence(r["brief"] or "Brief unavailable.")}\n\n## Documents\n\n'
    body += '\n'.join('- ' + d for d in r['docs']) or 'No documents recorded.'
    body += '\n\n## Outputs\n\nCount: ' + flat(r['out_count']) + '\n\n'
    body += '\n'.join('- ' + d for d in r['outputs']) or 'No output paths recorded.'
    body += '\n\n## Metrics\n\n| Metric | Value |\n|---|---|\n'
    body += '\n'.join(f'| {k} | {cell(r[k]) if r[k] is not None else "unknown"} |' for k in metrics)
    body += '\n\n## Result\n\n' + fence(r['result'] or 'Final result unavailable.')
    body += '\n\n## Source limits\n\n' + '\n'.join('- ' + n for n in r['notes']) + '\n'
    return redact(body)


def write_changed(path, content):
    data = content.encode('utf-8') if isinstance(content, str) else content
    if path.is_symlink():
        raise ValueError('Refusing symlink output')
    if path.exists() and path.read_bytes() == data:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name('.' + path.name + '.tmp')
    if temp.is_symlink():
        raise ValueError('Refusing symlink temporary output')
    temp.write_bytes(data)
    temp.replace(path)
    return True


def publish(records, out, runs):
    records = finalize(records, runs)
    data = csv_bytes(records)  # Decisive size gate before any page is written.
    pages = [(Path(r['ld_path']), page(r)) for r in records]
    # Never replace an unrelated operator page.
    for p, body in pages:
        if p.exists() and 'task_key: ' not in read(p):
            raise ValueError('Run page already exists without task-ledger identity')
    written = sum(write_changed(p, body) for p, body in pages)
    index = '---\ntitle: Task runs\ntype: index\n---\n\n# Task runs\n\nNewest first. Costs are list-price equivalents; subscription is not an extra charge. Blank metrics are unavailable.\n\n| Started | Task | Project | Outcome | Run |\n|---|---|---|---|---|\n'
    index += '\n'.join(f'| {cell(r["started"])} | {cell(r["title"])} | {cell(r["project"])} | {r["outcome"]} | [record]({Path(r["ld_path"]).name}) |' for r in records) + '\n'
    write_changed(runs / 'index.md', redact(index))
    write_changed(out / 'tasks.csv', data)
    return {'rows': len(records), 'bytes': len(data), 'run_pages_written': written, 'run_pages': len(records)}


def build(out=STATE / 'dashboard', runs=RUNS, state=STATE, workflows=WORKFLOWS, dispatch=DISPATCH,
          snapshots=Path.home() / '.local/state/mesh-telemetry/jobs.jsonl', tasks=TASKS):
    known = task_ids(read(tasks))
    host = socket.gethostname()
    records = list(mesh_records(state / 'tasks', snapshots, known))
    records += list(workflow_records(workflows, known, host))
    records += list(codex_records(dispatch, state / 'ledger.sqlite', known, host))
    return publish(records, out, runs)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=STATE / 'dashboard')
    parser.add_argument('--runs', type=Path, default=RUNS)
    args = parser.parse_args()
    print(json.dumps(build(args.out, args.runs)))


if __name__ == '__main__':
    main()
