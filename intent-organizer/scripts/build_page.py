"""build_page.py - step 6 of intent-organizer: render the model's verdicts as a group-level approval page.

This script makes NO decisions. Every item's intent, destination and keep/remove/unsure verdict comes from
the LLM decision files (decisions-*.json), overridden by reviewer corrections (review-*.json), with
destination names normalized by the canonicalize pass (canonical.json). This joins those verdicts with the
gathered facts, turns them into concrete moves, groups them by destination and writes:
  <workdir>/org-plan.json     plan for Apply-Plan.ps1 (-Plan org-plan.json -Approvals <export>)
  <workdir>/Organizer.html    the approval page (one toggle per group, sensible groups ON by default)
Mechanical guards only (they never pick a destination): an item whose own folder is also being moved stays
put; two items that would land on the same name are flagged so the apply step skips the second; an item that a
config/registry entry points at (referenced_by) but is still planned to move is flagged and starts unticked.
Usage: python -I build_page.py <organize.config.json>
"""
import glob, hashlib, json, os, sys, time
from collections import Counter, defaultdict
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
CFG = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
WD = Path(CFG['workdir'])
HOME = CFG.get('home') or os.path.expanduser('~')
LABEL_OF = {}
for r in CFG['roots']:
    LABEL_OF.setdefault(os.path.normcase(r.get('dest_root', r['path']).rstrip('\\/')), r['label'])

facts, untouched = {}, []
for p in sorted(glob.glob(str(WD / 'org-items*.json'))):
    d = json.loads(Path(p).read_text(encoding='utf-8'))
    for it in d['items']: facts[it['id']] = it
    untouched += d.get('untouched', [])

verdicts = {}
for p in sorted(glob.glob(str(WD / 'decisions-*.json'))):
    try:
        for d in json.loads(Path(p).read_text(encoding='utf-8')): verdicts[d['id']] = dict(d)
    except Exception as e:
        print('skip', p, e)
FIELDS = ('decision', 'dest', 'intent', 'want', 'confidence', 'evidence', 'newer_or_original')
for p in sorted(glob.glob(str(WD / 'review-*.json'))):
    try:
        for c in json.loads(Path(p).read_text(encoding='utf-8')).get('corrections', []):
            v = verdicts.setdefault(c['id'], {'id': c['id']})
            v.update({k: c[k] for k in FIELDS if c.get(k)})
            v['reviewed'] = c.get('why') or 'changed in review'
    except Exception as e:
        print('skip', p, e)
canon = {'dest_map': {}, 'summaries': {}}
if (WD / 'canonical.json').exists():
    canon.update(json.loads((WD / 'canonical.json').read_text(encoding='utf-8')))


def root_of(f):
    if f.get('root'): return f['root']
    for r in CFG['roots']:
        if r['label'] == f.get('loc'): return r.get('dest_root', r['path'])
    return os.path.dirname(f['path'])


def norm(d):
    return (d or '').strip().replace('\\', '/').strip('/')


def canon_dest(root, dest):
    return norm(canon['dest_map'].get(f'{root}|{dest}', canon['dest_map'].get(dest, dest)))


REMOVE_GROUP = {'remove-superseded': 'Superseded by a newer version', 'remove-duplicate': 'Duplicates', 'remove-temp': 'Temporary leftovers'}
items, missing = [], []
for iid, f in facts.items():
    v = verdicts.get(iid)
    root = root_of(f)
    if not v:
        missing.append(f['path'])
        v = {'decision': 'unsure', 'intent': 'No decision was made for this item (it appeared after the review).', 'confidence': 'low'}
    dec = v.get('decision', 'unsure')
    dest = canon_dest(root, norm(v.get('dest')))
    if dec.startswith('remove'):
        action, target, group, kind = 'stage', os.path.join(root, '_REVIEW-then-delete'), REMOVE_GROUP.get(dec, 'Remove'), 'remove'
    elif dec == 'unsure':
        action, target, group, kind = 'move', os.path.join(root, '_Unsure'), '_Unsure', 'unsure'
    elif dec == 'leave-in-place' or dest in ('', '.'):
        action, target, group, kind = 'none', None, 'Stays where it is', 'stay'
    else:
        target = os.path.join(HOME, *dest[2:].split('/')) if dest.startswith('~/') else os.path.join(root, *dest.split('/'))
        action, group, kind = 'move', dest, 'organize'
        if os.path.normcase(os.path.dirname(f['path'])) == os.path.normcase(target):
            action, group, kind = 'none', 'Stays where it is', 'stay'
    items.append({'id': iid, 'section': LABEL_OF.get(os.path.normcase(root.rstrip('\\/')), f.get('loc')), 'root': root,
                  'name': f['name'], 'path': f['path'], 'kind': f['kind'], 'mb': f.get('mb', 0), 'created': f.get('created'),
                  'action': action, 'target': target, 'group': group, 'gkind': kind, 'decision': dec,
                  'intent': v.get('intent', ''), 'want': v.get('want', ''), 'confidence': v.get('confidence', ''),
                  'evidence': v.get('evidence', ''), 'newer_or_original': v.get('newer_or_original'), 'reviewed': v.get('reviewed'),
                  'referenced_by': f.get('referenced_by')})

# guard 1: an item inside a folder that is itself moving stays put (the folder carries it)
moving = {os.path.normcase(i['path']) for i in items if i['action'] != 'none' and i['kind'] == 'dir'}
for i in items:
    p = os.path.normcase(i['path'])
    if i['action'] != 'none' and any(p.startswith(m + os.sep) for m in moving):
        i.update(action='none', group='Stays where it is', gkind='stay', note='its parent folder is moving and carries it')
# guard 2: two items landing on the same name, or onto an existing file/folder
seen = Counter()
for i in items:
    if i['action'] == 'none': continue
    dst = os.path.normcase(os.path.join(i['target'], i['name']))
    seen[dst] += 1
    if seen[dst] > 1 or os.path.exists(dst):
        i['collision'] = True

plan_items = [{'id': i['id'], 'section': i['section'], 'name': i['name'], 'path': i['path'], 'action': i['action'],
               'target': i['target'], 'group': i['group'], 'gb': round(i['mb'] / 1024, 4), 'collision': i.get('collision', False)}
              for i in items if i['action'] != 'none']
plan_id = 'org-' + hashlib.sha1(json.dumps(sorted((p['id'], p['action'], p['target']) for p in plan_items)).encode()).hexdigest()[:10]
plan = {'plan_id': plan_id, 'generated': time.strftime('%Y-%m-%d %H:%M'), 'items': plan_items,
        'protected': CFG.get('protected', [])}
(WD / 'org-plan.json').write_text(json.dumps(plan, indent=1), encoding='utf-8')

summaries = {}
for k, s in canon.get('summaries', {}).items():
    root, _, dest = k.partition('|')
    summaries[f"{LABEL_OF.get(os.path.normcase(root.rstrip(chr(92) + '/')), root)}|{norm(dest)}"] = s
page = {'plan_id': plan_id, 'generated': plan['generated'], 'items': items, 'summaries': summaries,
        'sections': list(dict.fromkeys(r['label'] for r in CFG['roots'] if any(i['section'] == r['label'] for i in items))),
        'section_paths': {r['label']: r.get('dest_root', r['path']) for r in CFG['roots']},
        'untouched': len(untouched), 'missing': len(missing), 'apply_cmd': CFG.get('apply_cmd', '')}
tpl = Path(CFG.get('page_template') or SKILL / 'templates' / 'organizer.html').read_text(encoding='utf-8')
html = tpl.replace('__DATA__', json.dumps(page, separators=(',', ':')).replace('</', '<\\/'))
out = Path(CFG.get('page_out') or WD / 'Organizer.html')
out.write_text(html, encoding='utf-8')
print('items', len(items), 'planned actions', len(plan_items), 'missing verdicts', len(missing), 'plan', plan_id)
print(Counter(i['gkind'] for i in items), 'collisions', sum(1 for i in items if i.get('collision')))
print('groups', len({(i['section'], i['group']) for i in items}), '->', out)
