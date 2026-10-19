"""render_briefs.py - fill the prompt templates for one or more chunks (no decisions, text substitution only).

Usage:  python -I render_briefs.py <organize.config.json> [--kind worker|review|canonicalize] [--chunks A-downloads-1,B-...] [--paths wsl|windows]
--paths: how file paths are written in the brief. Default wsl for worker (omp runs in WSL), windows for review and
canonicalize (Claude agents on Windows).
Default kind: worker. Default chunks: every chunk-*.json in the workdir that has no decisions-*.json yet
(for review: every chunk that has decisions but no review-*.json).
Writes: <workdir>/briefs/<KIND>-<chunk>.md  (canonicalize: <workdir>/briefs/CANONICALIZE.md)
"""
import glob, json, os, re, sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
CFG = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
WD = Path(CFG['workdir'])
kind = sys.argv[sys.argv.index('--kind') + 1] if '--kind' in sys.argv else 'worker'
want = sys.argv[sys.argv.index('--chunks') + 1].split(',') if '--chunks' in sys.argv else None
pstyle = sys.argv[sys.argv.index('--paths') + 1] if '--paths' in sys.argv else ('wsl' if kind == 'worker' else 'windows')


def wsl(p):
    p = str(p)
    if pstyle == 'windows':
        return p
    if p.startswith('\\\\wsl.localhost\\') or p.startswith('//wsl.localhost/'):
        return '/' + '/'.join(re.split(r'[\\/]+', p)[3:])
    m = re.match(r'^([A-Za-z]):[\\/](.*)$', p)
    return f"/mnt/{m.group(1).lower()}/{m.group(2).replace(chr(92), '/')}" if m else p.replace('\\', '/')


def section(md, title):
    m = re.search(rf'^## {re.escape(title)}\s*\n(.*?)(?=^## |\Z)', md, re.S | re.M)
    return m.group(1).strip() if m else ''


profile = Path(CFG.get('profile') or SKILL / 'references' / 'user-profile.md').read_text(encoding='utf-8')
owner = section(profile, 'Who') + '\n\nProjects and interests (strong intent signals):\n' + section(profile, 'Projects and interests (strong intent signals)')
app_owned = section(profile, 'App-owned folders (leave in place)')
if CFG.get('app_owned'):
    app_owned += '\nPatterns from config: ' + ', '.join(f'`{p}`' for p in CFG['app_owned'])

projects = set()
for f in glob.glob(str(WD / 'decisions-*.json')):
    try:
        for d in json.load(open(f, encoding='utf-8')):
            dest = (d.get('dest') or '').replace('\\', '/')
            if dest.startswith('Projects/'): projects.add(dest.split('/')[1])
    except Exception:
        pass
canon = WD / 'canonical.json'
if canon.exists():
    for v in json.loads(canon.read_text(encoding='utf-8')).get('dest_map', {}).values():
        if v.startswith('Projects/'): projects.add(v.split('/')[1])
# show names in the canonical style (YYYY-MM then spaced words) so new chunks converge on it
projects = {(p[:8] + re.sub(r'(?<=\w)-(?=\w)', ' ', p[8:])) if re.match(r'\d{4}-\d{2} ', p) else p for p in projects}
existing = ', '.join(f'`{p}`' for p in sorted(projects)) or '(none yet)'

roots = {}
for r in CFG['roots']:
    cname = r.get('chunk') or re.sub(r'[^a-z0-9]+', '-', r['label'].lower()).strip('-')
    roots.setdefault(cname, []).append(r)


def chunk_roots(chunk):
    """Roots behind a chunk: by the config's chunk name, else by the loc labels of the chunk's items."""
    rs = roots.get(re.sub(r'-\d+$', '', chunk)) or roots.get(chunk)
    if not rs:
        try:
            locs = {i['loc'] for i in json.loads((WD / f'chunk-{chunk}.json').read_text(encoding='utf-8'))}
            rs = [r for r in CFG['roots'] if r['label'] in locs]
        except Exception:
            rs = []
    return rs


def root_text(chunk):
    parts = []
    for r in chunk_roots(chunk):
        t = f"{r['label']} = {r['path']}"
        if r.get('dest_root') and r['dest_root'] != r['path']:
            t += f" (a dump folder: dests for its items are relative to {r['dest_root']}, so they join that root's structure)"
        parts.append(t)
    return '; '.join(parts) or chunk


subs = {'{{WORKDIR}}': wsl(WD), '{{SKILL}}': wsl(SKILL), '{{OWNER}}': owner, '{{APP_OWNED}}': app_owned,
        '{{EXISTING_PROJECTS}}': existing, '{{INSTALLED_PROGRAMS}}': wsl(WD / 'installed-programs.txt'),
        '{{INSTALLED_APPX}}': wsl(WD / 'installed-appx.txt')}
tpl = (SKILL / 'prompts' / {'worker': 'worker-brief.md', 'review': 'review-brief.md', 'canonicalize': 'canonicalize-brief.md'}[kind]).read_text(encoding='utf-8')
out = WD / 'briefs'; out.mkdir(exist_ok=True)

if kind == 'canonicalize':
    t = tpl
    for k, v in subs.items(): t = t.replace(k, v)
    (out / 'CANONICALIZE.md').write_text(t, encoding='utf-8'); print(out / 'CANONICALIZE.md'); sys.exit(0)

chunks = sorted(Path(p).stem[len('chunk-'):] for p in glob.glob(str(WD / 'chunk-*.json')))
if want: chunks = [c for c in chunks if c in want]
elif kind == 'worker': chunks = [c for c in chunks if not (WD / f'decisions-{c}.json').exists()]
else: chunks = [c for c in chunks if (WD / f'decisions-{c}.json').exists() and not (WD / f'review-{c}.json').exists()]
facts_ids = set()
if (WD / 'org-items.json').exists():
    facts_ids = {i['id'] for i in json.loads((WD / 'org-items.json').read_text(encoding='utf-8'))['items']}


def missing(c):
    # ids whose root belongs to this chunk but that no decision file covers (e.g. new files since the worker ran)
    try:
        labels = {r['label'] for r in chunk_roots(c)}
        decided = set()
        for f in glob.glob(str(WD / 'decisions-*.json')):
            decided |= {d['id'] for d in json.load(open(f, encoding='utf-8'))}
        items = json.loads((WD / 'org-items.json').read_text(encoding='utf-8'))['items']
        miss = [i for i in items if i['loc'] in labels and i['id'] not in decided]
        if c.endswith('-1') or not re.search(r'-\d+$', c):   # split chunks: list missing items once, on part 1
            return ', '.join(f"`{i['id']}` ({i['name']})" for i in miss) or 'none'
        return 'none'
    except Exception:
        return 'none'


for c in chunks:
    t = tpl
    for k, v in {**subs, '{{CHUNK}}': c, '{{CHUNKFILE}}': f'chunk-{c}.json', '{{ROOT}}': root_text(c), '{{MISSING}}': missing(c)}.items():
        t = t.replace(k, v)
    p = out / f'{kind.upper()}-{c}.md'
    p.write_text(t, encoding='utf-8')
    print(p)
