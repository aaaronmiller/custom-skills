"""build_cleanup_plan.py - one reviewable plan for everything the cleanup could do, organized by folder.

Merges (a) the removal manifest (temp, caches, WSL, system, hash duplicates), (b) the living document's
per-file organize/delete decisions (W2 v3 data) and (c) type-based sorting suggestions for Downloads items
nothing else classified. Every item gets a stable id (hash of action + path), a plain-language reason,
and a functional-impact note. Security-flagged items are excluded entirely (the user keeps them as-is).

Output: <checkup>/removal/cleanup-plan.json  (read by Cleanup-Approvals.html and Remove-CheckupItems.ps1)
Usage:  python -I build_cleanup_plan.py <checkup_dir>
"""
import csv, hashlib, json, os, re, sys, time
from pathlib import Path

CK = Path(sys.argv[1]); ST = CK / 'raw' / 'storage'
HOME = r'C:\Users\Administrator'
ROOTS = {'Downloads': HOME + r'\Downloads', 'Desktop': HOME + r'\Desktop', 'Documents': HOME + r'\Documents',
         'Pictures': HOME + r'\Pictures', 'Music': HOME + r'\Music', 'Videos': HOME + r'\Videos',
         'home root': HOME, 'D:\\': 'D:\\', 'Temp': HOME + r'\AppData\Local\Temp'}
SECURITY = re.compile(r'keymaker|keygen|activator|crack|mdm|rodbautis|passview|password|harvest|darkweb|serial|api key|NETGEAR|\[filecr\]|filecr', re.I)
PROTECTED = [r'C:\0.defenderexclusions', r'D:\0.defenderexclusions', HOME + r'\Documents\chetaz',
             HOME + r'\Desktop\Bitsum Process Lasso Pro v14.0.0.40 Multilingual Portable [FTUApps]',
             HOME + r'\Downloads\downloads-desktop-cleanup.livingdoc', r'C:\performance-diagnostics', HOME + r'\.claude',
             HOME + r'\.config', HOME + r'\.ssh', HOME + r'\AppData\Local\Packages\CanonicalGroupLimited.Ubuntu_79rhkp1fndgsc',
             r'D:\SPECTRE-16-UGLYBETTY.tibx', r'D:\Recovery', r'D:\chetaz']   # D:\chetaz = vault mirror; never pull files out of it

FOLDERS = [  # display order
    ('downloads', 'Downloads', ROOTS['Downloads']), ('desktop', 'Desktop', ROOTS['Desktop']),
    ('documents', 'Documents', ROOTS['Documents']), ('pictures', 'Pictures', ROOTS['Pictures']),
    ('music', 'Music', ROOTS['Music']), ('home', 'Home folder', HOME), ('d', 'D:\\ drive', 'D:\\'),
    ('appcache', 'App caches (Windows)', HOME + r'\AppData'), ('devcache', 'Developer caches (Windows)', HOME),
    ('temp', 'Temp folders', ROOTS['Temp']), ('system', 'System (needs admin)', 'C:\\Windows'),
    ('wsl', 'WSL / Linux home', '/home/cheta')]

items, unresolved, seen = [], [], set()

def sid(prefix, *parts):
    return prefix + '-' + hashlib.sha1('|'.join(parts).lower().encode()).hexdigest()[:8]

def protected(p):
    lp = p.lower().rstrip('\\')
    return any(lp == r.lower() or lp.startswith(r.lower() + '\\') for r in PROTECTED)

def add(folder, group, name, action, why, impact, level, gb, recommended, path=None, **kw):
    key = (action, (path or kw.get('command') or kw.get('wsl') or name).lower())
    if key in seen: return
    seen.add(key)
    if path and (protected(path) or SECURITY.search(path)): return
    if SECURITY.search(name): return
    it = dict(id=sid(folder[:3].upper(), action, path or kw.get('command') or kw.get('wsl') or name), folder=folder, group=group,
              name=name, action=action, why=why, impact=impact, impact_level=level, gb=round(float(gb or 0), 3),
              recommended=bool(recommended))
    if path: it['path'] = path
    it.update({k: v for k, v in kw.items() if v is not None})
    items.append(it)

def rows(p):
    try: return list(csv.DictReader(open(p, encoding='utf-8')))
    except FileNotFoundError: return []

# ---------------------------------------------------------------- inventories (for path resolution and sizes)
top = {}      # (root_key, name_lower) -> (path, gb, type)
for key, inv in (('Downloads', 'inv-Downloads.csv'), ('Desktop', 'inv-Desktop.csv'), ('Documents', 'inv-Documents.csv'),
                 ('Pictures', 'inv-Pictures.csv'), ('Music', 'inv-Music.csv'), ('home root', 'inv-HOME_ROOT.csv'), ('D:\\', 'inv-D_ROOT.csv')):
    for r in rows(ST / inv):
        if r.get('type') == 'skipped': continue
        top[(key, r['name'].lower())] = (os.path.join(ROOTS[key], r['name']), float(r['mb'] or 0) / 1024, r['type'])
for r in rows(ST / 'temp-items.csv'):
    top[('Temp', r['item'].lower())] = (os.path.join(r['tempdir'], r['item']), float(r['gb'] or 0), r['type'])
nested = {}   # basename_lower -> [(path, gb)]
for key, fl in (('Downloads', 'files-Downloads.csv'), ('Desktop', 'files-Desktop.csv'), ('Documents', 'files-Documents.csv')):
    for r in rows(ST / fl):
        p = os.path.join(ROOTS[key], r['rel'])
        nested.setdefault(os.path.basename(r['rel']).lower(), []).append((p, float(r['mb'] or 0) / 1024))
for r in rows(ST / 'large-files.csv'):
    nested.setdefault(os.path.basename(r['path']).lower(), []).append((r['path'], float(r['gb'])))

def resolve(name, loc, note):
    """Return (path, gb) or None. Top-level match in the group's locations first, then nested by basename,
    narrowed by an "in '<folder>'" hint in the note. Ambiguous -> None (never guess)."""
    locs = [k for k in ROOTS if k.lower() in loc.lower()] or list(ROOTS)
    if 'D:\\modelsx' in loc or 'D:\\modelsx' in note:
        p = os.path.join(r'D:\modelsx', name)
        hit = [x for x in nested.get(name.lower(), []) if x[0].lower() == p.lower()]
        if hit: return hit[0]
    for k in locs:
        t = top.get((k, name.lower()))
        if t: return t[0], t[1]
    cands = nested.get(name.lower(), [])
    cands = [c for c in cands if any(c[0].lower().startswith(ROOTS[k].lower() + '\\') for k in locs)] or cands
    m = re.search(r"in (?:Desktop |Downloads |Documents )?'([^']+)'", note)
    if m: cands = [c for c in cands if m.group(1).lower() in c[0].lower()] or []
    if len(cands) == 1: return cands[0]
    return None

def folder_of(path):
    lp = path.lower()
    for key, _, root in FOLDERS[:7]:
        r = root.lower()
        if key == 'home':
            if lp.startswith(HOME.lower() + '\\.') or (lp.startswith(HOME.lower() + '\\') and lp.count('\\') == 3 and not any(lp.startswith(ROOTS[k].lower()) for k in ('Downloads', 'Desktop', 'Documents', 'Pictures', 'Music', 'Videos'))):
                return 'home'
            continue
        if lp.startswith(r.rstrip('\\') + '\\') or lp == r.rstrip('\\'):
            return key
    return 'temp' if '\\temp\\' in lp else 'home'

# ---------------------------------------------------------------- (b) living document decisions
D = json.load(open(CK / 'workers' / 'W2-livingdoc-v3-DATA.json', encoding='utf-8'))
SKIP_GROUPS = {'protected', 'resolved-since-july', 'media-keep', 'droot-media', 'crash-evidence', 'temp-stale', 'proj-cheta-docs'}
GROUP_LABEL = {'exact-dupes': 'Duplicate downloads', 'old-versions': 'Superseded versions', 'stale-system': 'Old driver packages and logs',
               'dead-files': 'Empty files', 'installers': 'Installers for apps already installed', 'disk-images': 'Disk and OS images',
               'archives-extracted': 'Zips already extracted next to themselves', 'model-consolidation': 'AI model weights',
               'redundant-builds': 'Redundant tool builds', 'heavy-new': 'Big new arrivals (decide each)', 'screenshots': 'Screenshots and generated images'}
for g in D['groups']:
    gid = g['id']
    if gid in SKIP_GROUPS: continue
    rec = g['rec']['label']
    mv = re.search(r'Move into (?:Pictures/)?/?([A-Za-z0-9_\- ]+)', rec)
    for f in g['files']:
        name, _, note = f.partition('  ')
        name = name.strip(); note = note.strip().strip('()')
        if '+' in name and not os.path.splitext(name)[1]:   # combined descriptive entries
            unresolved.append({'group': gid, 'entry': f, 'reason': 'combined entry'}); continue
        res = resolve(name, g['loc'], note)
        if not res:
            unresolved.append({'group': gid, 'entry': f, 'reason': 'not found or ambiguous'}); continue
        path, gb = res
        folder = folder_of(path)
        label = GROUP_LABEL.get(gid, g['title'])
        if mv:
            dest_name = mv.group(1).strip()
            if gid == 'screenshots':
                target = ROOTS['Pictures'] + r'\Screenshots'
                if path.lower().startswith(target.lower()): continue
            else:
                root = next((ROOTS[k] for k in ('Downloads', 'Desktop', 'Documents') if path.lower().startswith(ROOTS[k].lower() + '\\')), ROOTS['Downloads'])
                target = root + '\\' + dest_name
            add(folder, f'Organize: {dest_name}', name, 'move', g['fn'] + (f' ({note})' if note else ''),
                'Moves into a folder. Shortcuts, scripts or recent-file lists that point at the old location will need the new path.',
                'moves', gb, True, path=path, target=target)
        else:
            confirmed = bool(re.search(r'identical|same bytes|confirmed', note, re.I))
            rec_on = {'exact-dupes': confirmed, 'old-versions': True, 'stale-system': True, 'dead-files': True,
                      'installers': 'verify' not in note.lower() and 'no installed' not in note.lower(),
                      'archives-extracted': True, 'redundant-builds': 'sycl' not in name.lower(),
                      'disk-images': False, 'model-consolidation': False, 'heavy-new': False}.get(gid, False)
            add(folder, label, name, 'stage', (note + '. ' if note else '') + g['fn'],
                'Moved into _REVIEW-then-delete beside it, not deleted. Nothing stops working; empty that folder yourself later.',
                'staged', gb, rec_on, path=path)

# ---------------------------------------------------------------- (c) type-based sorting for the rest of Downloads
covered = {it['path'].lower() for it in items if it.get('path')}
BUCKETS = [('_Installers', ('.exe', '.msi', '.msix', '.msixbundle', '.appx', '.appinstaller', '.vsix', '.appimage', '.deb', '.rpm', '.apk', '.dmg', '.pkg'), True),
           ('_Archives', ('.zip', '.7z', '.rar', '.tar', '.gz', '.tgz', '.xz', '.bz2', '.zst'), True),
           ('_Documents', ('.pdf', '.docx', '.doc', '.xlsx', '.xls', '.pptx', '.odt', '.rtf', '.epub', '.csv'), True),
           ('_Images', ('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.bmp', '.ico', '.heic', '.avif'), True),
           ('_Media', ('.mp4', '.mkv', '.mov', '.webm', '.mp3', '.wav', '.flac', '.m4a', '.ogg', '.opus'), True),
           ('_Notes', ('.md', '.txt', '.html', '.htm', '.mhtml', '.log'), True),
           ('_Scripts', ('.ps1', '.sh', '.bat', '.cmd', '.py', '.js', '.ts', '.reg', '.ahk'), False),
           ('_Configs', ('.json', '.yaml', '.yml', '.toml', '.ini', '.conf', '.env.example'), False)]
for r in rows(ST / 'inv-Downloads.csv'):
    path = os.path.join(ROOTS['Downloads'], r['name'])
    if path.lower() in covered or r['type'] != 'file' or protected(path) or SECURITY.search(r['name']) or r['name'].lower() == 'desktop.ini':
        continue
    ext = (r['ext'] or '').lower()
    b = next(((n, rec) for n, exts, rec in BUCKETS if ext in exts), None)
    if not b: continue
    n, rec = b
    add('downloads', f'Sort by type: {n}', r['name'], 'move',
        f'No project fits this {ext} file, so it is sorted by type. Move it into a project folder later if one fits better.',
        'Moves into a folder.' + (' Scripts and configs are often run or read by path, so check nothing points here first.' if not rec else ' Nothing else changes.'),
        'moves', float(r['mb'] or 0) / 1024, rec, path=path, target=ROOTS['Downloads'] + '\\' + n)

# ---------------------------------------------------------------- (a) removal manifest (temp, caches, WSL, system, dupes)
man = json.load(open(CK / 'removal' / 'removal-manifest.json', encoding='utf-8'))
IMPACT = {  # by manifest title keyword -> (folder, impact text, level)
    'uv package cache': ('devcache', 'No functional change. The next uv install re-downloads packages it needs, so that one install is slower.', 'slower'),
    'npm cache (Windows)': ('devcache', 'No functional change. npm re-downloads packages on the next install.', 'slower'),
    'pip cache': ('devcache', 'No functional change. pip re-downloads wheels on the next install.', 'slower'),
    'VS Code downloaded VSIX': ('appcache', 'No functional change. Installed extensions keep working; only the stored installer copies go.', 'none'),
    'Raspberry Pi Imager': ('appcache', 'No functional change. The Imager downloads the OS image again next time you flash.', 'slower'),
    'Slack offline caches': ('appcache', 'You stay signed in to every workspace. Slack re-downloads images and its offline message cache, so the first launch is slower. Requires Slack closed.', 'slower'),
    'Discord / Obsidian': ('appcache', 'You stay signed in everywhere. Obsidian vaults, plugins and settings are not touched. Each app rebuilds its web cache on next launch. Requires the apps closed.', 'slower'),
    'Chrome HTTP': ('appcache', 'No sign-outs: cookies, saved passwords, history, sessions, open tabs and extensions are separate files and are not touched. Pages and images re-download as you browse, so the first visits are slower. Requires Chrome fully closed.', 'slower'),
    'VoiceStudio build cache': ('appcache', 'VoiceStudio keeps working. The next VoiceStudio rebuild re-downloads about 6 GB of packages.', 'redownload'),
    'VoiceStudio runtime private': ('appcache', 'VoiceStudio keeps working (its venv is separate). A runtime rebuild would re-download.', 'redownload'),
    'Hugging Face': ('devcache', 'Any tool that loads these models will re-download them on next use (several GB). Remove only if you no longer run them.', 'redownload'),
    'User-mode crash dumps': ('temp', 'No functional change. You lose the crash dumps (evidence for diagnosing those app crashes).', 'history'),
    'WSL crash dumps': ('temp', 'No functional change. You lose the WSL crash dumps, which are the evidence for the WSL crash triage.', 'history'),
    'Delivery Optimization': ('system', 'No functional change. Windows refills the update peer cache when needed.', 'none'),
    'Stale Windows Update download': ('system', 'No functional change. Those partial payloads can never install (expired certificate).', 'none'),
    'Cap Volume Shadow Copy': ('system', 'Restore points and backup snapshots beyond 20 GB are deleted, oldest first. New ones keep working within the cap.', 'history'),
    'Empty Process Lasso': ('system', 'No functional change. Empty leftover folders.', 'none'),
    'Dead Process Lasso config': ('system', 'No functional change. The running engine reads the Desktop config; this copy is moved to a quarantine folder, not deleted.', 'none'),
    'uv cache (WSL)': ('wsl', 'No functional change. uv re-downloads on next install.', 'slower'),
    'pnpm store prune': ('wsl', 'No functional change. Removes only packages no project references; pnpm re-fetches if one is needed again.', 'slower'),
    'npm cache (WSL)': ('wsl', 'No functional change. npm re-downloads on next install.', 'slower'),
    'Superseded Rust toolchain': ('wsl', 'No functional change. Stable 1.98.1 stays the default; it skips itself if any project pins 1.98.0.', 'none'),
    'Dated nightly toolchain': ('wsl', 'A project pinned to that nightly would re-download it (1.5 GB) on next build.', 'redownload'),
    'Old Puppeteer browsers (Chrome 127': ('wsl', 'No functional change for current projects. A project still pinned to Chrome 127 would re-download it.', 'slower'),
    'Puppeteer Chrome 148/149': ('wsl', 'Projects pinned to Chrome 148 or 149 re-download that browser (about 350 MB each) on next run.', 'redownload'),
    'opencode logs': ('wsl', 'No functional change. Old log files only.', 'history'),
    'Old codex app-server': ('wsl', 'Codex keeps working on its current release; rolling back would need a re-download.', 'none'),
    'Journal vacuum': ('wsl', 'No functional change. Older system logs inside WSL are dropped.', 'history'),
    'Docker build cache': ('wsl', 'Images and containers are untouched. The next docker build of each project is slower once.', 'slower'),
    '24 GB /swapfile-cass': ('wsl', 'WSL keeps its 4 GB swap. Very large cass indexing runs could hit the memory limit sooner. Choose this only if you no longer need the extra swap.', 'functional'),
    'Stale node_modules': ('wsl', 'Archived copy only. If you ever revive that copy, run pnpm/bun install.', 'slower'),
    'small stale items': ('temp', 'No functional change. Installer leftovers, .tmp files and logs untouched for 7+ days; each is re-checked for locks at run time.', 'none'),
    'WSL swap disk folder': ('temp', 'No functional change. Old WSL swap disks; skipped automatically if the running VM uses it.', 'none'),
}
for it in man['items']:
    if it['section'] == 'User folders (living doc)': continue
    title = it['title']
    hit = next((v for k, v in IMPACT.items() if title.startswith(k) or k in title), None)
    if it['section'] == 'Duplicates':
        p = it['path']; f = folder_of(p)
        add(f, 'Duplicates (hash-verified)', os.path.basename(p), 'stage', it['why'],
            'Moved into _REVIEW-then-delete beside it; the identical copy stays. Breaks nothing unless the copy sat inside a folder another program uses as a set.',
            'staged', it['gb'], it['default'], path=p, keep=it.get('keep'))
        continue
    if hit: folder, impact, level = hit
    elif it['section'] == 'Windows temp': folder, impact, level = 'temp', 'No functional change. Temp file untouched for 7+ days; re-checked for locks at run time.', 'none'
    else: folder, impact, level = 'system', 'See reason.', 'none'
    extra = {k: it.get(k) for k in ('paths', 'command', 'wsl', 'requires', 'min_age_days', 'guard')}
    add(folder, it['section'] if it['section'] not in ('Windows caches',) else ('Developer caches' if folder == 'devcache' else 'App caches' if folder == 'appcache' else 'System'),
        title, it['action'], it['why'] + ' ' + it.get('regenerates', ''), impact, level, it['gb'], it['default'],
        path=it.get('path'), **extra)

# ---------------------------------------------------------------- write
order = {k: i for i, (k, _, _) in enumerate(FOLDERS)}
items.sort(key=lambda x: (order.get(x['folder'], 99), x['group'], -x['gb'], x['name'].lower()))
plan = {'plan_id': time.strftime('plan-%Y%m%d-%H%M%S'), 'generated': time.strftime('%Y-%m-%d %H:%M'),
        'folders': [{'key': k, 'label': l, 'root': r} for k, l, r in FOLDERS],
        'items': items, 'unresolved': unresolved, 'protected': PROTECTED,
        'excluded_note': 'Security-related items (keymakers, activators, cracked installers, MDM tools, credential files) are excluded on purpose and left exactly as they are.'}
(CK / 'removal' / 'cleanup-plan.json').write_text(json.dumps(plan, indent=1), encoding='utf-8')
from collections import Counter
c = Counter(i['folder'] for i in items)
print('items', len(items), dict(c)); print('unresolved', len(unresolved))
print('recommended GB', round(sum(i['gb'] for i in items if i['recommended'] and i['action'] != 'move'), 1), 'moves', sum(1 for i in items if i['action'] == 'move'))
