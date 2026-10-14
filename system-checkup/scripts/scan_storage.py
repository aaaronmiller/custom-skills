"""scan_storage.py - read-only storage census for the periodic Windows checkup.

Never deletes, moves or modifies anything. Writes CSV/JSON into OUT (argv[1]).
Run with:  python -I scan_storage.py <out_dir> [--no-dupes]

Sections
  appdata-sizes.csv      AppData\\{Local,Roaming,LocalLow} children (+ grandchildren of anything >1 GB)
  caches.csv             known regenerable caches with category, size, owner process, notes
  temp-items.csv         top-level items in temp dirs, with lock state for files (vhdx etc.)
  inv-<folder>.csv       top-level inventory of each user folder (Downloads, Desktop, ...)
  files-<folder>.csv     every file in Downloads/Desktop/Documents (path,size,mtime) for classification
  node_modules.csv       node_modules trees + which package manager's lockfile owns them
  large-files.csv        files >= 500 MB (user profile + D:)
  dupes.csv              duplicate groups (size + sampled/full blake2b)
  summary.json           headline numbers
"""
import csv, hashlib, json, os, stat, sys, time
from pathlib import Path

OUT = Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
DO_DUPES = '--no-dupes' not in sys.argv
HOME = Path(os.environ.get('USERPROFILE', r'C:\Users\Administrator'))
LOCAL = HOME / 'AppData' / 'Local'; ROAMING = HOME / 'AppData' / 'Roaming'
EXCLUDE_ROOTS = [Path(r'C:\0.defenderexclusions'), Path(r'D:\0.defenderexclusions'),
                 Path(r'D:\System Volume Information'), Path(r'D:\$RECYCLE.BIN'),
                 Path(r'C:\$Recycle.Bin'), Path(r'C:\System Volume Information')]
REPARSE = getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0x400)
T0 = time.time()

def excluded(p: Path) -> bool:
    s = str(p).lower()
    return any(s == str(e).lower() or s.startswith(str(e).lower() + '\\') for e in EXCLUDE_ROOTS)

def is_reparse(entry) -> bool:
    try:
        return bool(entry.stat(follow_symlinks=False).st_file_attributes & REPARSE)
    except Exception:
        return True

def walk_size(path: Path, skip_names=(), collect=None):
    """Return (bytes, files, newest_mtime). Does not follow reparse points."""
    total = files = 0; newest = 0.0
    stack = [path]
    while stack:
        d = stack.pop()
        if excluded(d):
            continue
        try:
            it = os.scandir(d)
        except Exception:
            continue
        with it:
            for e in it:
                try:
                    if is_reparse(e):
                        continue
                    if e.is_dir(follow_symlinks=False):
                        if e.name in skip_names:
                            continue
                        stack.append(Path(e.path))
                    else:
                        st = e.stat(follow_symlinks=False)
                        total += st.st_size; files += 1
                        if st.st_mtime > newest: newest = st.st_mtime
                        if collect is not None: collect(e.path, st)
                except Exception:
                    continue
    return total, files, newest

def item_size(p: Path):
    try:
        if p.is_dir() and not (p.stat().st_file_attributes & REPARSE):
            return walk_size(p)
        st = p.stat(); return st.st_size, 1, st.st_mtime
    except Exception:
        return 0, 0, 0.0

def ts(t):
    return time.strftime('%Y-%m-%d %H:%M', time.localtime(t)) if t else ''

def gb(b):
    return round(b / 1024**3, 3)

def write_csv(name, rows, fields):
    with open(OUT / name, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore'); w.writeheader(); w.writerows(rows)

def log(msg):
    print(f'[{time.time()-T0:7.1f}s] {msg}', flush=True)

summary = {}

# ---------------------------------------------------------------- AppData
log('AppData sizes')
rows = []
for base in (LOCAL, ROAMING, HOME / 'AppData' / 'LocalLow'):
    try: kids = list(base.iterdir())
    except Exception: kids = []
    for k in kids:
        b, n, newest = item_size(k)
        rows.append(dict(path=str(k), gb=gb(b), files=n, newest=ts(newest), depth=1))
        if b > 1024**3 and k.is_dir():
            try: gkids = list(k.iterdir())
            except Exception: gkids = []
            for g in gkids:
                gb_, gn, gnew = item_size(g)
                if gb_ > 100 * 1024**2:
                    rows.append(dict(path=str(g), gb=gb(gb_), files=gn, newest=ts(gnew), depth=2))
rows.sort(key=lambda r: -r['gb'])
write_csv('appdata-sizes.csv', rows, ['path', 'gb', 'files', 'newest', 'depth'])
summary['appdata_total_gb'] = round(sum(r['gb'] for r in rows if r['depth'] == 1), 1)

# ---------------------------------------------------------------- caches
log('known caches')
CHROME = LOCAL / 'Google' / 'Chrome' / 'User Data'
def chrome_profiles():
    out = []
    try:
        for p in CHROME.iterdir():
            if p.is_dir() and (p.name == 'Default' or p.name.startswith('Profile ')):
                out.append(p)
    except Exception:
        pass
    return out
# (path, category, owner_process, safe, note)
C = []
def add(p, cat, owner, safe, note):
    C.append((Path(p), cat, owner, safe, note))
add(LOCAL / 'npm-cache', 'pkg-cache', 'node', 'yes', 'npm content cache; `npm cache clean --force` regenerates')
add(LOCAL / 'pnpm' / 'store', 'pkg-cache', 'pnpm', 'prune', '`pnpm store prune` removes unreferenced only')
add(LOCAL / 'pnpm-cache', 'pkg-cache', 'pnpm', 'yes', 'pnpm metadata cache')
add(HOME / '.bun' / 'install' / 'cache', 'pkg-cache', 'bun', 'yes', 'bun install cache')
add(LOCAL / 'pip' / 'cache', 'pkg-cache', 'python', 'yes', '`pip cache purge`')
add(LOCAL / 'uv' / 'cache', 'pkg-cache', 'uv', 'yes', '`uv cache clean`')
add(HOME / '.cache' / 'uv', 'pkg-cache', 'uv', 'yes', '`uv cache clean`')
add(LOCAL / 'Yarn' / 'Cache', 'pkg-cache', 'yarn', 'yes', '`yarn cache clean`')
add(HOME / '.nuget' / 'packages', 'pkg-cache', 'dotnet', 'caution', 'global NuGet packages; restore re-downloads')
add(LOCAL / 'NuGet' / 'v3-cache', 'pkg-cache', 'dotnet', 'yes', 'NuGet http cache')
add(HOME / '.cargo' / 'registry', 'pkg-cache', 'cargo', 'yes', 'crate sources; cargo re-fetches')
add(HOME / '.gradle' / 'caches', 'pkg-cache', 'gradle', 'yes', 'gradle caches')
add(HOME / '.m2' / 'repository', 'pkg-cache', 'maven', 'caution', 'maven repo')
add(LOCAL / 'go-build', 'build-cache', 'go', 'yes', '`go clean -cache`')
add(HOME / '.cache' / 'huggingface', 'model-cache', 'python', 'caution', 'model weights; re-download cost')
add(HOME / '.cache' / 'lm-studio', 'model-cache', 'lmstudio', 'caution', 'LM Studio')
add(HOME / '.lmstudio' / 'models', 'model-store', 'lmstudio', 'NO', 'user-chosen local models (data)')
add(HOME / '.ollama' / 'models', 'model-store', 'ollama', 'NO', 'user-chosen local models (data)')
add(LOCAL / 'ms-playwright', 'tool-cache', 'playwright', 'yes', 'browser binaries; `npx playwright install` restores')
add(HOME / '.cache' / 'puppeteer', 'tool-cache', 'puppeteer', 'yes', 'browser binaries')
add(LOCAL / 'Temp', 'temp', '-', 'see temp-items.csv', 'per-user temp; lock-checked separately')
add(LOCAL / 'CrashDumps', 'crash', '-', 'yes', 'user-mode crash dumps')
add(LOCAL / 'D3DSCache', 'shader-cache', 'gpu', 'yes', 'DirectX shader cache')
add(LOCAL / 'Intel' / 'ShaderCache', 'shader-cache', 'gpu', 'yes', 'Intel shader cache')
add(LOCAL / 'NVIDIA' / 'DXCache', 'shader-cache', 'gpu', 'yes', '')
add(LOCAL / 'Microsoft' / 'Windows' / 'INetCache', 'browser-cache', 'edge/ie', 'yes', 'WinINet cache')
add(LOCAL / 'Microsoft' / 'Windows' / 'Explorer', 'thumb-cache', 'explorer', 'yes', 'thumbcache_*.db; rebuilt on demand')
add(LOCAL / 'Microsoft' / 'Windows' / 'WER', 'crash', '-', 'yes', 'user WER reports')
add(LOCAL / 'Packages', 'appx-data', '-', 'NO', 'Store app data (contains WSL distro VHDX!) - never bulk-clean')
add(ROAMING / 'Code' / 'Cache', 'electron-cache', 'Code', 'yes-when-closed', 'VS Code http cache')
add(ROAMING / 'Code' / 'CachedData', 'electron-cache', 'Code', 'yes-when-closed', 'VS Code compiled cache (old versions)')
add(ROAMING / 'Code' / 'CachedExtensionVSIXs', 'electron-cache', 'Code', 'yes', 'downloaded VSIX copies')
add(ROAMING / 'Code' / 'logs', 'logs', 'Code', 'yes', 'VS Code logs')
add(ROAMING / 'Code' / 'User' / 'workspaceStorage', 'app-state', 'Code', 'caution', 'per-workspace state (some extension data)')
add(ROAMING / 'Code' / 'User' / 'History', 'app-state', 'Code', 'caution', 'local file history (recoverable edits)')
for app in ('discord', 'Slack', 'Beeper', 'obsidian', 'Notion', 'Claude', 'Antigravity', 'Kiro', 'Cursor', 'Joplin', 'OpenWhispr', 'open-whispr', 'Comet'):
    for sub, safe in (('Cache', 'yes-when-closed'), ('Code Cache', 'yes-when-closed'), ('GPUCache', 'yes-when-closed'),
                      ('DawnCache', 'yes-when-closed'), ('DawnGraphiteCache', 'yes-when-closed'), ('DawnWebGPUCache', 'yes-when-closed'),
                      ('Service Worker' + os.sep + 'CacheStorage', 'yes-when-closed'), ('logs', 'yes')):
        add(ROAMING / app / sub, 'electron-cache', app, safe, 'Electron http/code/gpu cache - never touch Local Storage/IndexedDB/Cookies')
add(ROAMING / 'open-whispr' / 'audio', 'app-data', 'OpenWhispr', 'NO', 'voice recordings archive (user data; prior recovery used it)')
for prof in chrome_profiles():
    for sub in ('Cache', 'Code Cache', 'GPUCache', 'DawnGraphiteCache', 'DawnWebGPUCache'):
        add(prof / sub, 'browser-cache', 'chrome', 'yes-when-closed', 'HTTP/code/GPU cache only - NOT cookies/history/logins')
    add(prof / 'Service Worker' / 'CacheStorage', 'browser-cache', 'chrome', 'caution', 'PWA offline caches; regenerates but sites may re-download')
add(CHROME / 'ShaderCache', 'browser-cache', 'chrome', 'yes', '')
add(CHROME / 'GrShaderCache', 'browser-cache', 'chrome', 'yes', '')
add(CHROME / 'component_crx_cache', 'browser-cache', 'chrome', 'yes', '')
add(CHROME / 'optimization_guide_model_store', 'browser-cache', 'chrome', 'yes', 'on-device model downloads; re-fetched')
add(CHROME / 'OptGuideOnDeviceModel', 'browser-cache', 'chrome', 'caution', 'Gemini Nano weights (~2-4GB); re-download if AI features used')
add(LOCAL / 'Microsoft' / 'Edge' / 'User Data' / 'Default' / 'Cache', 'browser-cache', 'msedge', 'yes-when-closed', '')
add(LOCAL / 'Temp' / 'WinGet', 'pkg-cache', 'winget', 'yes', 'winget download cache')
add(LOCAL / 'Docker' / 'wsl', 'vm-disk', 'docker', 'NO', 'Docker Desktop VHDX - use Docker prune, not delete')
add(HOME / '.claude' / 'file-history', 'agent-state', 'claude', 'caution', 'Claude Code checkpoints (rewind data)')
add(HOME / '.claude' / 'projects', 'agent-state', 'claude', 'NO', 'session transcripts (history)')
add(HOME / '.unsloth', 'model-store', 'unsloth', 'caution', 'Unsloth studio + weights')
crows = []
running = set()
try:
    import subprocess
    out = subprocess.run(['tasklist', '/fo', 'csv', '/nh'], capture_output=True, text=True, timeout=30).stdout
    for line in out.splitlines():
        if line.startswith('"'):
            running.add(line.split('","')[0].strip('"').lower().replace('.exe', ''))
except Exception:
    pass
for p, cat, owner, safe, note in C:
    if not p.exists():
        continue
    b, n, newest = item_size(p)
    if b == 0:
        continue
    crows.append(dict(path=str(p), category=cat, owner=owner, owner_running=('yes' if owner.lower() in running else 'no'),
                      safe=safe, gb=gb(b), files=n, newest=ts(newest), note=note))
crows.sort(key=lambda r: -r['gb'])
write_csv('caches.csv', crows, ['path', 'category', 'owner', 'owner_running', 'safe', 'gb', 'files', 'newest', 'note'])
summary['caches_total_gb'] = round(sum(r['gb'] for r in crows if r['category'] != 'temp'), 1)

# ---------------------------------------------------------------- temp
log('temp dirs')
def lock_state(path):
    try:
        with open(path, 'rb'):   # read-only probe; exclusive holders (e.g. Hyper-V on swap.vhdx) refuse it
            return 'unlocked'
    except PermissionError:
        return 'LOCKED'
    except Exception as ex:
        return f'err:{type(ex).__name__}'
trows = []
for tdir in (LOCAL / 'Temp', Path(r'C:\Windows\Temp'), Path(r'C:\Temp'), Path(r'C:\tmp'), Path(r'D:\tmp'), Path(r'D:\Temp')):
    try: kids = list(tdir.iterdir())
    except Exception: continue
    for k in kids:
        b, n, newest = item_size(k)
        locked = ''
        if k.is_file():
            locked = lock_state(k)
        else:
            vh = list(k.glob('*.vhdx'))
            if vh:
                locked = ';'.join(f'{v.name}={lock_state(v)}' for v in vh)
        age_days = round((time.time() - newest) / 86400, 1) if newest else ''
        trows.append(dict(tempdir=str(tdir), item=k.name, type=('dir' if k.is_dir() else 'file'), gb=gb(b), files=n,
                          newest=ts(newest), age_days=age_days, lock=locked))
trows.sort(key=lambda r: -r['gb'])
write_csv('temp-items.csv', trows, ['tempdir', 'item', 'type', 'gb', 'files', 'newest', 'age_days', 'lock'])
summary['temp_total_gb'] = round(sum(r['gb'] for r in trows), 1)

# ---------------------------------------------------------------- user folders
log('user folder inventories')
USER_FOLDERS = ['Downloads', 'Desktop', 'Documents', 'Pictures', 'Videos', 'Music', 'Favorites', 'Links', 'Contacts', 'Saved Games', 'Searches', '3D Objects', 'OneDrive']
DETAIL = {'Downloads', 'Desktop', 'Documents'}
inv_summary = {}
for name in USER_FOLDERS:
    root = HOME / name
    if not root.exists():
        continue
    rows = []
    try: kids = list(root.iterdir())
    except Exception: kids = []
    for k in kids:
        b, n, newest = item_size(k)
        try: mt = k.stat().st_mtime
        except Exception: mt = 0
        rows.append(dict(name=k.name, type=('dir' if k.is_dir() else 'file'), ext=(k.suffix.lower() if k.is_file() else ''),
                         mb=round(b / 1024**2, 1), files=n, mtime=ts(mt), newest=ts(newest)))
    rows.sort(key=lambda r: -r['mb'])
    write_csv(f'inv-{name.replace(" ", "_")}.csv', rows, ['name', 'type', 'ext', 'mb', 'files', 'mtime', 'newest'])
    inv_summary[name] = dict(items=len(rows), gb=round(sum(r['mb'] for r in rows) / 1024, 2))
    if name in DETAIL:
        frows = []
        def coll(path, st, frows=frows, root=root):
            if len(frows) < 200000:
                frows.append(dict(rel=os.path.relpath(path, root), mb=round(st.st_size / 1024**2, 3), mtime=ts(st.st_mtime)))
        walk_size(root, skip_names=('node_modules', '.git', '.venv', '__pycache__'), collect=coll)
        write_csv(f'files-{name}.csv', frows, ['rel', 'mb', 'mtime'])
# home root (dirs/files directly in C:\Users\Administrator, except AppData and the known folders)
rows = []
for k in HOME.iterdir():
    if k.name in USER_FOLDERS or k.name in ('AppData', 'NTUSER.DAT') or k.name.lower().startswith('ntuser'):
        continue
    b, n, newest = item_size(k)
    rows.append(dict(name=k.name, type=('dir' if k.is_dir() else 'file'), ext=(k.suffix.lower() if k.is_file() else ''),
                     mb=round(b / 1024**2, 1), files=n, mtime='', newest=ts(newest)))
rows.sort(key=lambda r: -r['mb'])
write_csv('inv-HOME_ROOT.csv', rows, ['name', 'type', 'ext', 'mb', 'files', 'mtime', 'newest'])
inv_summary['HOME_ROOT'] = dict(items=len(rows), gb=round(sum(r['mb'] for r in rows) / 1024, 2))
# C:\ root and D:\ root (top level only)
for drv in ('C:\\', 'D:\\'):
    rows = []
    try: kids = list(Path(drv).iterdir())
    except Exception: kids = []
    for k in kids:
        if excluded(k) or k.name in ('Windows', 'Program Files', 'Program Files (x86)', 'ProgramData', 'Users', 'Recovery', '$Recycle.Bin', '$RECYCLE.BIN', 'pagefile.sys', 'swapfile.sys', 'hiberfil.sys', 'DumpStack.log.tmp'):
            rows.append(dict(name=k.name, type='skipped', ext='', mb='', files='', mtime='', newest=''))
            continue
        b, n, newest = item_size(k)
        rows.append(dict(name=k.name, type=('dir' if k.is_dir() else 'file'), ext=(k.suffix.lower() if k.is_file() else ''),
                         mb=round(b / 1024**2, 1), files=n, mtime='', newest=ts(newest)))
    write_csv(f'inv-{drv[0]}_ROOT.csv', rows, ['name', 'type', 'ext', 'mb', 'files', 'mtime', 'newest'])
summary['user_folders'] = inv_summary

# ---------------------------------------------------------------- node_modules
log('node_modules search')
LOCKS = [('pnpm-lock.yaml', 'pnpm'), ('bun.lock', 'bun'), ('bun.lockb', 'bun'), ('yarn.lock', 'yarn'), ('package-lock.json', 'npm')]
nm_rows = []
def find_nm(root: Path, maxdepth=7):
    stack = [(root, 0)]
    while stack:
        d, depth = stack.pop()
        if excluded(d) or depth > maxdepth:
            continue
        try: it = list(os.scandir(d))
        except Exception: continue
        for e in it:
            try:
                if not e.is_dir(follow_symlinks=False) or is_reparse(e):
                    continue
            except Exception:
                continue
            if e.name == 'node_modules':
                proj = Path(d); pm = 'none'
                p = proj
                for _ in range(4):
                    hit = next((m for f, m in LOCKS if (p / f).exists()), None)
                    if hit: pm = hit; break
                    if p.parent == p: break
                    p = p.parent
                b, n, newest = walk_size(Path(e.path))
                try: pmt = proj.stat().st_mtime
                except Exception: pmt = 0
                nm_rows.append(dict(project=str(proj), pm=pm, gb=gb(b), files=n, project_mtime=ts(pmt),
                                    stale_90d=('yes' if pmt and time.time() - pmt > 90 * 86400 else 'no')))
            elif e.name in ('.git', 'AppData', '.venv', 'venv', '__pycache__', '$Recycle.Bin', 'Windows', 'Program Files', 'Program Files (x86)'):
                continue
            else:
                stack.append((Path(e.path), depth + 1))
for root in (HOME, Path(r'D:\CODE'), Path(r'D:\chetaz'), Path(r'D:\desktop'), Path(r'C:\code'), Path(r'C:\dev')):
    if root.exists():
        find_nm(root)
nm_rows.sort(key=lambda r: -r['gb'])
write_csv('node_modules.csv', nm_rows, ['project', 'pm', 'gb', 'files', 'project_mtime', 'stale_90d'])
summary['node_modules'] = dict(count=len(nm_rows), gb=round(sum(r['gb'] for r in nm_rows), 1),
                               npm_gb=round(sum(r['gb'] for r in nm_rows if r['pm'] == 'npm'), 1),
                               stale_gb=round(sum(r['gb'] for r in nm_rows if r['stale_90d'] == 'yes'), 1))

# ---------------------------------------------------------------- large files + dupes
log('large files + duplicate candidates')
MIN_DUP = 5 * 1024**2
by_size = {}; large = []
def coll_big(path, st):
    if st.st_size >= MIN_DUP:
        by_size.setdefault(st.st_size, []).append(path)
    if st.st_size >= 500 * 1024**2:
        large.append(dict(path=path, gb=gb(st.st_size), mtime=ts(st.st_mtime)))
SCAN_ROOTS = [HOME, Path('D:\\')]
for r in SCAN_ROOTS:
    if r.exists():
        walk_size(r, skip_names=('node_modules', '.git', '$RECYCLE.BIN', 'System Volume Information'), collect=coll_big)
large.sort(key=lambda r: -r['gb'])
write_csv('large-files.csv', large, ['path', 'gb', 'mtime'])
summary['large_files'] = dict(count=len(large), gb=round(sum(r['gb'] for r in large), 1))

def sampled_hash(path, size):
    h = hashlib.blake2b(digest_size=16)
    with open(path, 'rb') as f:
        if size <= 64 * 1024**2:
            while True:
                chunk = f.read(4 * 1024**2)
                if not chunk: break
                h.update(chunk)
            return 'full:' + h.hexdigest()
        for off in (0, size // 2, max(0, size - 4 * 1024**2)):
            f.seek(off); h.update(f.read(4 * 1024**2))
        h.update(str(size).encode())
        return 'sampled:' + h.hexdigest()

drows = []
if DO_DUPES:
    cands = {s: ps for s, ps in by_size.items() if len(ps) > 1}
    log(f'hashing {sum(len(v) for v in cands.values())} files in {len(cands)} size groups')
    gid = 0
    for size, paths in sorted(cands.items(), key=lambda kv: -kv[0] * (len(kv[1]) - 1)):
        hashes = {}
        for p in paths:
            if p.lower().endswith(('.vhdx', '.vhd', '.tibx', 'pagefile.sys', 'swapfile.sys')):
                continue
            try: hashes.setdefault(sampled_hash(p, size), []).append(p)
            except Exception: continue
        for hv, ps in hashes.items():
            if len(ps) > 1:
                gid += 1
                for i, p in enumerate(sorted(ps, key=len)):
                    try: mt = os.stat(p).st_mtime
                    except Exception: mt = 0
                    drows.append(dict(group=gid, keep_suggest=('keep' if i == 0 else 'dup'), mb=round(size / 1024**2, 1),
                                      hash=hv.split(':')[0], path=p, mtime=ts(mt)))
    write_csv('dupes.csv', drows, ['group', 'keep_suggest', 'mb', 'hash', 'path', 'mtime'])
    summary['dupes'] = dict(groups=gid, files=len(drows), reclaim_gb=round(sum(r['mb'] for r in drows if r['keep_suggest'] == 'dup') / 1024, 2))

summary['elapsed_s'] = round(time.time() - T0)
(OUT / 'summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
log('done ' + json.dumps(summary))
