"""metrics.py - step 3 facts for the meta-analysis. Measures decision files; decides nothing.

Usage: python -I metrics.py <organize.config.json> [--chunks A,B]   (default: every decisions-*.json)
Prints, per chunk and overall: decision mix, confidence mix, distinct destinations per item (fragmentation),
single-item folders, depth violations, project-name style violations, removals lacking evidence or with low
confidence, dot/app-owned/live folders that were moved, items whose folder is also moved (nesting
conflicts), and items missing a decision. Writes <workdir>/metrics.json for the retrospective.
"""
import glob, json, os, re, sys
from collections import Counter, defaultdict
from pathlib import Path

CFG = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
WD = Path(CFG['workdir'])
want = sys.argv[sys.argv.index('--chunks') + 1].split(',') if '--chunks' in sys.argv else None

facts = {}
for p in glob.glob(str(WD / 'org-items*.json')):
    for it in json.loads(Path(p).read_text(encoding='utf-8'))['items']: facts[it['id']] = it
corr = {}
for p in glob.glob(str(WD / 'review-*.json')):
    for c in json.loads(Path(p).read_text(encoding='utf-8')).get('corrections', []): corr[c['id']] = c

dmap = {}
if (WD / 'canonical.json').exists():
    dmap = json.loads((WD / 'canonical.json').read_text(encoding='utf-8')).get('dest_map', {})


def final(r):
    """Apply review corrections and the canonical destination map, as build_page.py does."""
    if r['id'] in corr: r = {**r, **{k: v for k, v in corr[r['id']].items() if v and k != 'why'}}
    d = (r.get('dest') or '').replace('\\', '/').strip('/')
    root = facts.get(r['id'], {}).get('root', '')
    r['dest'] = dmap.get(f'{root}|{d}', d).replace('\\', '/').strip('/')
    return r


PROJ = re.compile(r'^\d{4}-\d{2} [A-Za-z0-9][^/]*$')
report, all_rows, seen_ids = {}, [], set()
for p in sorted(glob.glob(str(WD / 'decisions-*.json'))):
    chunk = Path(p).stem[len('decisions-'):]
    if want and chunk not in want: continue
    rows = json.loads(Path(p).read_text(encoding='utf-8'))
    for r in rows:
        r = final(r); seen_ids.add(r['id'])
        r['_chunk'] = chunk; all_rows.append(r)
for p in sorted(glob.glob(str(WD / 'review-*.json'))):          # items decided only by the reviewer
    chunk = Path(p).stem[len('review-'):]
    if want and chunk not in want: continue
    for c in json.loads(Path(p).read_text(encoding='utf-8')).get('corrections', []):
        if c['id'] not in seen_ids and c.get('decision'):
            r = final({'id': c['id']}); r['_chunk'] = chunk; all_rows.append(r); seen_ids.add(c['id'])
    try: n_in = len(json.loads((WD / f'chunk-{chunk}.json').read_text(encoding='utf-8')))
    except Exception: n_in = None
    report[chunk] = {'in': n_in, 'out': len(rows)}


HOME = CFG.get('home', '')


def place(r):
    """(folder the dest is relative to, dest) - '~/Documents/Projects/X' counts as Projects/X inside ~/Documents,
    so cross-root moves are measured together with the folder they join."""
    d = (r.get('dest') or '').strip('/')
    if d.startswith('~/'):
        top, _, rest = d[2:].partition('/')
        return (HOME + '\\' + top, rest)
    return (facts.get(r['id'], {}).get('root', ''), d)


def measure(rows):
    m = {'items': len(rows), 'decisions': Counter(r.get('decision') for r in rows), 'confidence': Counter(r.get('confidence') for r in rows)}
    dests = Counter(place(r) for r in rows if r.get('decision') in ('keep-organize',))
    m['distinct_dests'] = len(dests)
    m['dests_per_item'] = round(len(dests) / max(1, len(rows)), 2)
    m['single_item_folders'] = sorted(d for (root, d), n in dests.items() if n == 1 and d.count('/') >= 1 and not d.startswith('Projects/'))
    m['too_deep'] = sorted({d for (root, d) in dests if d.count('/') > (3 if d.startswith('Projects/') else 2)})
    m['bad_project_names'] = sorted({d.split('/')[1] for (root, d) in dests if d.startswith('Projects/') and not PROJ.match(d.split('/')[1])})
    m['unsure_share'] = round(m['decisions'].get('unsure', 0) / max(1, len(rows)), 3)
    m['weak_removals'] = [(facts.get(r['id'], {}).get('name'), r.get('confidence'), r.get('evidence')) for r in rows
                          if str(r.get('decision', '')).startswith('remove') and (r.get('confidence') == 'low' or not r.get('evidence'))]
    m['moved_protected_kind'] = [(f.get('name'), r.get('decision'), r.get('dest')) for r in rows for f in [facts.get(r['id'], {})]
                                 if (f.get('app_owned') or f.get('live_hint')) and r.get('decision') not in ('leave-in-place', 'unsure')]
    paths = {facts[r['id']]['path'].lower(): r for r in rows if r['id'] in facts}
    m['nesting_conflicts'] = sorted({facts[r['id']]['name'] for r in rows if r['id'] in facts and r.get('decision') != 'leave-in-place'
                                     and any(q.startswith(facts[r['id']]['path'].lower() + '\\') for q in paths)})
    return m


out = {'chunks': {}, 'overall': None}
for chunk in report:
    rows = [r for r in all_rows if r['_chunk'] == chunk]
    out['chunks'][chunk] = {**report[chunk], **measure(rows)}
out['overall'] = measure(all_rows)
ids = {r['id'] for r in all_rows}
out['overall']['missing_decisions'] = sum(1 for i in facts if i not in ids)
(WD / 'metrics.json').write_text(json.dumps(out, indent=1, default=list), encoding='utf-8')

for chunk, m in list(out['chunks'].items()) + [('OVERALL', out['overall'])]:
    print(f"\n== {chunk}: {m['items']} items" + (f" (input {m.get('in')})" if m.get('in') is not None else ''))
    print('  decisions ', dict(m['decisions']))
    print('  confidence', dict(m['confidence']))
    print(f"  dests {m['distinct_dests']} ({m['dests_per_item']}/item, target <= 0.25)  unsure {m['unsure_share']:.1%}")
    for k in ('single_item_folders', 'too_deep', 'bad_project_names', 'weak_removals', 'moved_protected_kind', 'nesting_conflicts'):
        if m[k]: print(f'  {k} ({len(m[k])}):', m[k][:12])
if out['overall'].get('missing_decisions'): print('\nitems without a decision:', out['overall']['missing_decisions'])
