"""Offline regression fixtures for task identity, privacy and publication gates."""
import csv
import importlib.util
import io
import json
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location('task_ledger', Path(__file__).parents[1] / 'scripts/task-ledger.py')
tl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tl)


@pytest.mark.parametrize('args,expected', [
    ({'exit_code': 0}, 'done'), ({'exit_code': '0', 'is_error': True}, 'failed'),
    ({'exit_code': 1}, 'failed'), ({'subtype': 'success'}, 'done'),
    ({'subtype': 'error_max_turns', 'is_error': True}, 'partial'),
    ({'subtype': 'error_max_budget_usd'}, 'partial'),
    ({'subtype': 'error_during_execution'}, 'failed'),
    ({'running': True}, 'running'), ({'running': False}, 'unknown'),
])
def test_outcome(args, expected):
    assert tl.outcome(**args) == expected


def test_project_first_match():
    assert tl.project('Use /home/cheta/code/first/spec.md then /home/cheta/LIVING_DOCUMENTS/projects/second/') == 'first'
    assert tl.project('/home/cheta/LIVING_DOCUMENTS/projects/second/tasks.md') == 'second'
    assert tl.project('no path') == 'masterplan'


def test_task_ids_only_definitions():
    known = tl.task_ids('- [x] MP-13 Work mentions MP-99\n| LD-P3 | Inbox |\n- [ ] DA-M2 Build\n')
    assert known == {'MP-13', 'LD-P3', 'DA-M2'}
    assert tl.extract_ids('MP-13 LD-P3 DA-M2 MP-130 XMP-13 MP-99', known) == ['DA-M2', 'LD-P3', 'MP-13']
    assert tl.extract_ids('MP-130 XMP-13 MP-13b', known) == []


def test_docs(tmp_path):
    doc = tmp_path / 'guide.md'; doc.write_text('hello')
    brief = f'Read `{doc}` then /home/cheta/code/missing/notes.html. Plan: /work/specs/design. Nothing /work/data.bin'
    assert tl.docs(brief) == [str(doc), '/work/specs/design [not found]']
    assert '/home/cheta/code/missing/notes.html [remote]' in tl.docs(brief, remote=True)


def test_redaction_every_output(tmp_path):
    secret = 'sk-' + 'a' * 30
    r = tl.record('mesh', 'peer', 'job', f'Prompt api_key={secret}')
    r.update(result=secret, title=secret, outputs=[secret], docs=[secret], notes=[secret])
    rs = tl.finalize([r], tmp_path / 'runs')
    assert secret not in rs[0]['brief_excerpt']
    assert '[redacted]' in rs[0]['brief_excerpt']
    assert secret not in tl.page(rs[0])
    assert secret.encode() not in tl.csv_bytes(rs)


def test_csv_size_cap_and_no_partial_writes(tmp_path):
    r = tl.record('mesh', 'peer', 'job', 'x' * 2000)
    r.update(docs=['x' * tl.MAX_BYTES])
    with pytest.raises(ValueError, match='publication refused'):
        tl.publish([r], tmp_path / 'out', tmp_path / 'runs')
    assert not (tmp_path / 'runs').exists()
    rs = tl.finalize([tl.record('mesh', 'peer', 'ok')], tmp_path / 'runs')
    data = tl.csv_bytes(rs)
    with pytest.raises(ValueError):
        tl.csv_bytes(rs, len(data))
    assert len(tl.csv_bytes(rs, len(data) + 1)) == len(data)


def test_run_rewrite_only_on_change(tmp_path):
    r = tl.record('mesh', 'peer', 'job', 'Use the plan.\n```\nquoted\n```')
    r.update(started='2026-11-07T00:00:00Z', ended='2026-11-07T00:01:00Z', outcome='done')
    out, runs = tmp_path / 'out', tmp_path / 'runs'
    assert tl.publish([r], out, runs)['run_pages_written'] == 1
    p = runs / '2026-11-07-mesh-job.md'
    before = p.stat().st_mtime_ns
    assert tl.publish([r], out, runs)['run_pages_written'] == 0
    assert before == p.stat().st_mtime_ns
    assert '````' in p.read_text()
    r['result'] = 'new result'
    assert tl.publish([r], out, runs)['run_pages_written'] == 1
    assert 'new result' in p.read_text()


def test_mesh_host_alias_and_last_snapshot(tmp_path):
    summaries = tmp_path / 'tasks'; summaries.mkdir()
    (summaries / 'remote-big-surface.json').write_text(json.dumps({'host': 'Cheta-surface-studio', 'jobs': [
        {'job': 'job', 'brief': 'MP-13', 'exit': '0', 'models': {'opus': 4}, 'out_files': ['a'], 'out_count': 1},
        {'job': '.pytest_cache'}]}))
    snaps = tmp_path / 'jobs.jsonl'
    snaps.write_text('\n'.join(json.dumps(s) for s in [
        {'host': 'big', 'job': 'job', 'running': True, 'cost_usd': 1},
        {'host': 'big', 'job': 'job', 'running': False, 'cost_usd': 2, 'output_tokens': 10}]))
    rs = list(tl.mesh_records(summaries, snaps, {'MP-13'}))
    assert len(rs) == 1
    assert rs[0]['outcome'] == 'done'
    assert rs[0]['cost_usd'] == 2
    assert rs[0]['tokens_out'] == 10


def test_workflow_agent_message_usage_dedup(tmp_path):
    d = tmp_path / 'wf_test'; d.mkdir()
    (d / 'journal.jsonl').write_text('\n'.join(json.dumps(x) for x in [
        {'type': 'started', 'agentId': 'a', 'phase': 'Plan', 'label': 'research'},
        {'type': 'result', 'agentId': 'a', 'result': 'finished'}]))
    entries = [
        {'type': 'user', 'timestamp': '2026-11-07T00:00:00Z', 'message': {'content': 'Build /home/cheta/code/foo. MP-13'}},
        {'type': 'assistant', 'timestamp': '2026-11-07T00:02:00Z', 'message': {'id': 'm', 'model': 'opus', 'usage': {'input_tokens': 2, 'output_tokens': 4}}}]
    (d / 'agent-a.jsonl').write_text('\n'.join(json.dumps(x) for x in entries + [entries[-1]]))
    r = list(tl.workflow_records(tmp_path, {'MP-13'}, 'local'))[0]
    assert r['duration_min'] == 2
    assert r['tokens_out'] == 4
    assert r['subagents'] == 1
    assert r['outcome'] == 'done'
    assert r['phases'] == ['Plan']


def test_codex_total_is_not_output_and_explicit_match(tmp_path):
    (tmp_path / 'c1-build.md').write_text('Build /home/cheta/code/foo with effort high')
    (tmp_path / 'c1.log').write_text('model: test-model\nsession id: session-one\nreasoning effort: medium\n2026-11-07T00:00:00Z init\ncodex\nFinished\ntokens used\n1,234\nEXIT 0\n')
    r = list(tl.codex_records(tmp_path, tmp_path / 'missing.sqlite', set(), 'local'))[0]
    assert r['tokens_total'] == 1234
    assert r['tokens_out'] is None
    assert r['effort'] == 'medium'
    assert r['outcome'] == 'done'
    assert r['result'] == 'Finished'


def test_colliding_hosts_and_redacted_identifiers(tmp_path):
    records = [tl.record('mesh', h, 'same') for h in ['peer', 'big']]
    records += [tl.record('codex', 'local', 'a' * 31 + str(i)) for i in range(2)]
    rs = tl.finalize(records, tmp_path)
    assert len({r['ld_path'] for r in rs}) == 4
    assert len({r['task_key'] for r in rs}) == 4


def test_csv_outputs_first_twenty_full_page_preserved(tmp_path):
    r = tl.record('mesh', 'peer', 'out')
    r['outputs'] = [f'file-{n}.md' for n in range(30)]
    r['out_count'] = 30
    rs = tl.finalize([r], tmp_path)
    row = next(csv.DictReader(io.StringIO(tl.csv_bytes(rs).decode())))
    assert len(row['outputs'].split('; ')) == 20
    assert 'file-29.md' in tl.page(rs[0])


def test_active_codex_quoted_totals_not_terminal(tmp_path):
    (tmp_path / 'c5-task.md').write_text('Build ledger')
    (tmp_path / 'c5.log').write_text('model: model\nuser\nBuild ledger\nexec\nprinted old log:\nERROR: usage limit\ntokens used\n209,339\nEXIT 0\nmore ongoing work\n')
    r = list(tl.codex_records(tmp_path, tmp_path / 'missing', set(), 'local'))[0]
    assert r['outcome'] == 'running'
    assert r['tokens_total'] is None
    assert r['ended'] == ''


def test_little_alias_matches_peer(tmp_path):
    (tmp_path / 'remote-peer.json').write_text(json.dumps({'host': 'omarchy', 'jobs': [{'job': 'one', 'exit': '0'}]}))
    snapshots = tmp_path / 'snap.jsonl'
    snapshots.write_text(json.dumps({'host': 'little', 'job': 'one', 'cost_usd': 1}))
    rs = list(tl.mesh_records(tmp_path, snapshots, set()))
    assert len(rs) == 1
    assert rs[0]['cost_usd'] == 1


def test_codex_sqlite_join_no_double_count(tmp_path):
    import sqlite3
    db = tmp_path / 'calls.sqlite'
    with sqlite3.connect(db) as con:
        con.execute('CREATE TABLE calls (host, session_id, harness, ts, model, tokens_in, tokens_out, tokens_cache_read, tokens_cache_write, list_cost_usd)')
        for sid in ['matched', 'unmatched']:
            con.execute('INSERT INTO calls VALUES (?,?,?,?,?,?,?,?,?,?)', ('local', sid, 'codex', '2026-11-07T00:00:00Z', 'm', 10, 5, 2, 0, None))
    (tmp_path / 'c1-build.md').write_text('Build this')
    (tmp_path / 'c1.log').write_text('session id: matched\nmodel: m\ncodex\nDone\ntokens used\n15\nEXIT 0\n')
    rs = list(tl.codex_records(tmp_path, db, set(), 'local'))
    assert len(rs) == 2
    assert sum(r['tokens_out'] for r in rs) == 10
    assert rs[0]['cost_usd'] is None
    assert rs[1]['outcome'] == 'unknown'


def test_codex_wrapper_repeats_final_after_total(tmp_path):
    (tmp_path / 'c4-build.md').write_text('Build it')
    (tmp_path / 'c4.log').write_text('model: m\ncodex\nFinished\nhook: Stop Completed\ntokens used\n136,807\nFinished again\nEXIT 0\n')
    r = list(tl.codex_records(tmp_path, tmp_path / 'missing', set(), 'local'))[0]
    assert r['tokens_total'] == 136807
    assert r['outcome'] == 'done'
