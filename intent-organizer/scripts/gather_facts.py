"""gather_facts.py - step 1 of intent-organizer: collect FACTS about every item in the configured roots.

This script makes no decisions. For every top-level item of each root it records dates (created ~ when it
was downloaded), size, type, a folder summary, a short REDACTED content excerpt for text/markdown/HTML/
Office/PDF/zip listings, config KEY names (never values), installer hints (platform, product tokens,
version, the installed program it may match), hash-identical duplicates, version families, temp markers,
app-owned / tool-folder / live-directory hints, and any earlier note. Security-flagged and protected items
are listed under "untouched" and are never opened.

Usage:  python -I gather_facts.py <organize.config.json> [--only "<root label>,<root label>"] [--facts-only]
        --facts-only refreshes org-items.json without rewriting chunk files (use after decisions exist)
Writes: <workdir>/org-items.json, <workdir>/chunk-<name>.json, <workdir>/installed-programs.txt, installed-appx.txt
Config: see templates/organize.config.example.json
"""
import csv, fnmatch, hashlib, json, os, re, subprocess, sys, time, zipfile
from collections import defaultdict
from pathlib import Path

CFG = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
ONLY = None
if '--only' in sys.argv:
    ONLY = {s.strip().lower() for s in sys.argv[sys.argv.index('--only') + 1].split(',')}
OUT = Path(CFG['workdir']); OUT.mkdir(parents=True, exist_ok=True)
ROOTS = CFG['roots']
ROOT_PATHS = {os.path.normcase(r['path'].rstrip('\\/')) for r in ROOTS}
PROTECTED = {os.path.normcase(p.rstrip('\\/')) for p in CFG.get('protected', [])}
SECURITY = re.compile(CFG.get('security_regex') or r'keymaker|keygen|activator|crack|passview|password|credential|secret|token|wallet|seed ?phrase|\.env$', re.I)
APP_OWNED = [p.lower() for p in CFG.get('app_owned', [])]
LIVE_DAYS = CFG.get('live_days', 14)
WALK_CAP = CFG.get('walk_cap', 60000)

LEAVE_EXT = {'.lnk', '.url'}
LEAVE_NAMES = {'desktop.ini', 'thumbs.db', 'ntuser.dat'}
TEXT_EXT = {'.md', '.txt', '.html', '.htm', '.mhtml', '.csv', '.log', '.ps1', '.psm1', '.sh', '.bat', '.cmd', '.py', '.js', '.ts', '.mjs', '.xml', '.svg', '.rtf', '.srt', '.vtt', '.lua', '.ahk', '.reg', '.sql', '.ipynb', '.tex', '.org', '.rst'}
CONF_EXT = {'.json', '.yaml', '.yml', '.toml', '.ini', '.conf', '.cfg', '.properties', '.jsonc'}
INST_EXT = {'.exe', '.msi', '.msix', '.msixbundle', '.appx', '.appxbundle', '.appinstaller', '.vsix', '.appimage', '.deb', '.rpm', '.apk', '.xapk', '.dmg', '.pkg', '.snap', '.flatpak', '.ipa'}
OTHER_PKG = {'.deb', '.rpm', '.appimage', '.apk', '.xapk', '.dmg', '.pkg', '.snap', '.flatpak', '.ipa'}
OTHER_SYS = re.compile(r'(linux|ubuntu|debian|fedora|arch(?!ive)|macos|mac-?os|darwin|osx|android|aarch64|arm64|armhf|armv7|raspberry|rpi|ios|ipados|chromeos|esp32|esp-?box|m5stack|cardputer|firmware|riscv|jetson|tegra)', re.I)
SECRET_PAT = re.compile(r'(sk-[A-Za-z0-9_\-]{12,}|gh[pousr]_[A-Za-z0-9]{20,}|xox[abp]-[A-Za-z0-9\-]{10,}|AIza[0-9A-Za-z_\-]{20,}|eyJ[A-Za-z0-9_\-]{20,}\.[A-Za-z0-9_\-]+|[A-Fa-f0-9]{32,}|[A-Za-z0-9+/]{40,}={0,2}|((?:api|secret|token|passw(?:or)?d|pwd|key|auth|bearer)[A-Za-z_]*\s*[:=]\s*)\S+)', re.I)
MARKERS = ('.git', 'package.json', 'README.md', 'readme.md', 'SKILL.md', 'setup.exe', 'install.sh', 'Cargo.toml', 'pyproject.toml',
           'requirements.txt', 'index.html', 'Makefile', 'docker-compose.yml', '.obsidian', 'CLAUDE.md', 'AGENTS.md', 'node_modules')


def redact(s):
    return SECRET_PAT.sub(lambda m: (m.group(2) + '[REDACTED]') if m.group(2) else '[REDACTED]', s)


def sniff(path, ext, size):
    """Short redacted excerpt that tells a reader what the file is about."""
    try:
        if ext in TEXT_EXT and size < 20 * 1024**2:
            with open(path, 'rb') as f: raw = f.read(2400)
            t = raw.decode('utf-8', 'replace')
            if ext in ('.html', '.htm', '.mhtml', '.svg', '.xml'):
                title = re.search(r'<title[^>]*>(.*?)</title>', t, re.I | re.S)
                t = (('TITLE: ' + title.group(1).strip() + ' | ') if title else '') + re.sub(r'<[^>]+>', ' ', t)
            return redact(re.sub(r'\s+', ' ', t)).strip()[:700]
        if ext in CONF_EXT and size < 5 * 1024**2:
            with open(path, 'rb') as f: t = f.read(4000).decode('utf-8', 'replace')
            keys = re.findall(r'^\s*"?([A-Za-z_][\w\-. ]{1,40})"?\s*[:=]', t, re.M)
            return 'CONFIG KEYS: ' + ', '.join(dict.fromkeys(keys[:40]))
        if ext in ('.docx', '.pptx', '.xlsx'):
            z = zipfile.ZipFile(path); out = []
            if 'docProps/core.xml' in z.namelist():
                c = z.read('docProps/core.xml').decode('utf-8', 'replace')
                for tag in ('title', 'subject', 'creator', 'created'):
                    m = re.search(rf'<(?:dc|dcterms|cp):{tag}[^>]*>(.*?)</', c)
                    if m and m.group(1).strip(): out.append(f'{tag}: {m.group(1).strip()}')
            body = {'docx': 'word/document.xml', 'pptx': 'ppt/slides/slide1.xml', 'xlsx': 'xl/sharedStrings.xml'}[ext[1:]]
            if body in z.namelist():
                out.append('TEXT: ' + re.sub(r'\s+', ' ', ' '.join(re.findall(r'<[aw]:t[^>]*>([^<]*)</', z.read(body).decode('utf-8', 'replace'))))[:450])
            return redact(' | '.join(out))[:700]
        if ext == '.zip' and size < 4 * 1024**3:
            names = zipfile.ZipFile(path).namelist()
            return redact('ZIP: %d entries; e.g. %s' % (len(names), ', '.join(names[:12])))[:700]
        if ext == '.pdf' and size < 300 * 1024**2:
            with open(path, 'rb') as f: b = f.read(200000)
            m = re.search(rb'/Title\s*\(([^)]{3,200})\)', b)
            return ('PDF TITLE: ' + m.group(1).decode('latin-1', 'replace')) if m else ''
    except Exception as e:
        return f'(unreadable: {type(e).__name__})'
    return ''


def is_link(path):
    """Symlink or Windows junction / reparse point: moving it would break whatever points through it."""
    try:
        st = os.lstat(path)
    except OSError:
        return False
    return os.path.islink(path) or bool(getattr(st, 'st_file_attributes', 0) & 0x400)   # FILE_ATTRIBUTE_REPARSE_POINT


def walk(path):
    """Size, file count, extension mix and newest write under a folder (capped; links are not followed)."""
    n, size, newest, exts, capped = 0, 0, 0.0, defaultdict(int), False
    for dp, dns, fns in os.walk(path, onerror=lambda e: None):
        dns[:] = [d for d in dns if d != '.git' and not is_link(os.path.join(dp, d))]
        for fn in fns:
            try: st = os.stat(os.path.join(dp, fn))
            except OSError: continue
            n += 1; size += st.st_size; newest = max(newest, st.st_mtime)
            exts[os.path.splitext(fn)[1].lower() or '(none)'] += 1
            if n >= WALK_CAP: capped = True; break
        if capped: break
    return n, size, newest, exts, capped


def iso(t): return time.strftime('%Y-%m-%d %H:%M', time.localtime(t)) if t else None


def dir_summary(path):
    n, size, newest, exts, capped = walk(path)
    try: kids = sorted(os.listdir(path))[:14]
    except Exception: kids = []
    markers = [m for m in MARKERS if os.path.exists(os.path.join(path, m))]
    readme = ''
    for m in ('README.md', 'readme.md', 'README.txt', 'SKILL.md', 'CLAUDE.md'):
        rp = os.path.join(path, m)
        if os.path.isfile(rp): readme = sniff(rp, '.md', os.path.getsize(rp))[:400]; break
    s = {'files': n, 'top_ext': sorted(exts.items(), key=lambda kv: -kv[1])[:6], 'children': kids, 'markers': markers,
         'readme': readme, 'newest_write': iso(newest)}
    if capped: s['approx'] = f'stopped counting at {WALK_CAP} files'
    return s, size


# ---------------------------------------------------------------- installed programs (registry, Store apps, or files named in config)
def norm_tokens(s):
    s = re.sub(r'\([^)]*\)', ' ', s.lower())
    return [t for t in re.findall(r'[a-z][a-z0-9+]*', s) if t not in {'x64', 'x86', 'win', 'win64', 'win32', 'windows', 'setup', 'installer', 'install', 'user', 'amd64', 'the', 'for', 'and', 'inc', 'corporation', 'llc', 'ltd', 'version', 'bit', 'multilingual', 'portable', 'stable', 'release', 'latest', 'full', 'offline', 'online', 'msi', 'exe', 'v'}]


def vtuple(s):
    m = re.findall(r'\d+(?:\.\d+)+|\d+', s or '')
    if not m: return None
    v = max(m, key=lambda x: (x.count('.'), len(x)))
    return tuple(int(x) for x in v.split('.')[:4])


def registry_programs():
    out = []
    try:
        import winreg
    except ImportError:
        return out
    hives = [(winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall'),
             (winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall'),
             (winreg.HKEY_CURRENT_USER, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall')]
    for hive, key in hives:
        try: k = winreg.OpenKey(hive, key)
        except OSError: continue
        for i in range(winreg.QueryInfoKey(k)[0]):
            try:
                sk = winreg.OpenKey(k, winreg.EnumKey(k, i))
                def val(n):
                    try: return str(winreg.QueryValueEx(sk, n)[0])
                    except OSError: return ''
                name = val('DisplayName')
                if name and val('SystemComponent') != '1':
                    out.append((name, val('DisplayVersion'), val('Publisher')))
            except OSError:
                pass
    return sorted(set(out))


def appx_packages():
    try:
        r = subprocess.run(['powershell.exe', '-NoProfile', '-Command', 'Get-AppxPackage | ForEach-Object { $_.Name + "|" + $_.Version }'],
                           capture_output=True, text=True, timeout=90)
        return [tuple(l.strip().split('|', 1)) for l in r.stdout.splitlines() if '|' in l]
    except Exception:
        return []


inst_cfg = CFG.get('installed', {})
programs = []
if inst_cfg.get('programs_csv') and os.path.exists(inst_cfg['programs_csv']):
    for r in csv.DictReader(open(inst_cfg['programs_csv'], encoding='utf-8-sig')):
        programs.append((r.get('DisplayName') or r.get('Name', ''), r.get('DisplayVersion') or r.get('Version', ''), r.get('Publisher', '')))
else:
    programs = registry_programs()
appx = []
if inst_cfg.get('appx_csv') and os.path.exists(inst_cfg['appx_csv']):
    appx = [(r['Name'], r.get('Version', '')) for r in csv.DictReader(open(inst_cfg['appx_csv'], encoding='utf-8-sig'))]
elif inst_cfg.get('appx', True):
    appx = appx_packages()
(OUT / 'installed-programs.txt').write_text('\n'.join(f'{n} | {v} | {p}' for n, v, p in programs), encoding='utf-8')
(OUT / 'installed-appx.txt').write_text('\n'.join(f'{n} | {v}' for n, v in appx), encoding='utf-8')
installed = [(n, v, set(norm_tokens(n))) for n, v, p in programs]
installed += [(n, v, set(norm_tokens(re.sub(r'([a-z])([A-Z])', r'\1 \2', n.split('.')[-1])))) for n, v in appx]


def installer_facts(name, ext):
    stem = os.path.splitext(name)[0]
    other = bool(OTHER_SYS.search(name)) or ext in OTHER_PKG
    if re.search(r'arm64|aarch64', name, re.I) and not re.search(r'x64|amd64|x86_64', name, re.I): other = True
    toks = [t for t in norm_tokens(re.sub(r'([a-z])([A-Z])', r'\1 \2', stem)) if not re.fullmatch(r'\d.*', t)]
    ver = vtuple(stem)
    best, score = None, 0
    for disp, iv, it in installed:
        if not toks: break
        overlap = len(set(toks) & it)
        if overlap and toks[0] in it and overlap > score:
            best, score = (disp, iv), overlap
    f = {'platform': 'other-system' if other else 'this-pc', 'product_tokens': toks[:5], 'file_version': '.'.join(map(str, ver)) if ver else None}
    if best:
        f['installed_as'], f['installed_version'] = best
        iv = vtuple(best[1])
        f['vs_installed'] = ('older' if ver < iv else 'same' if ver == iv else 'newer') if ver and iv else 'unknown'
    else:
        f['installed_as'] = None
    return f


# ---------------------------------------------------------------- earlier notes (optional: [{path, note}] or {items:[{path, group, why}]})
notes = {}
np_ = CFG.get('earlier_notes')
if np_ and os.path.exists(np_):
    try:
        data = json.load(open(np_, encoding='utf-8'))
        for it in (data.get('items', []) if isinstance(data, dict) else data):
            if it.get('path'):
                notes[os.path.normcase(it['path'])] = it.get('note') or f"{it.get('group', '')}: {str(it.get('why', ''))[:300]}"
    except Exception as e:
        print('earlier notes unreadable:', e)


# ---------------------------------------------------------------- path references (configs, startup entries, scheduled tasks)
# Only records WHICH file mentions an item's path; the files' contents never leave this script.
REF_TEXT = {}


def registry_refs():
    """Paths the registry points at: sound-scheme files (HKCU\\AppEvents) and Run/RunOnce startup commands."""
    out = []
    try:
        import winreg
    except ImportError:
        return ''
    def walk_key(hive, path, depth=0):
        try: k = winreg.OpenKey(hive, path)
        except OSError: return
        i = 0
        while True:
            try: name, val, typ = winreg.EnumValue(k, i)
            except OSError: break
            if isinstance(val, str) and ('\\' in val or '/' in val): out.append(os.path.expandvars(val))
            i += 1
        if depth < 4:
            j = 0
            while True:
                try: sub = winreg.EnumKey(k, j)
                except OSError: break
                walk_key(hive, path + '\\' + sub, depth + 1); j += 1
    walk_key(winreg.HKEY_CURRENT_USER, r'AppEvents\Schemes\Apps')
    for hive in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
        for p in (r'Software\Microsoft\Windows\CurrentVersion\Run', r'Software\Microsoft\Windows\CurrentVersion\RunOnce'):
            walk_key(hive, p, 3)
    return '\n'.join(out)


if CFG.get('reference_registry', True):
    REF_TEXT['registry (sound scheme / Run keys)'] = registry_refs().lower()
for rp in CFG.get('reference_files', []):
    try:
        if os.path.isfile(rp) and os.path.getsize(rp) < 8 * 1024**2:
            REF_TEXT[rp] = open(rp, 'rb').read().decode('utf-8', 'replace').lower().replace('\\\\', '\\')
    except OSError:
        pass


def referenced_by(path):
    p = path.lower().rstrip('\\/')
    forms = {p, p.replace('\\', '/')}
    m = re.match(r'^([a-z]):\\(.*)$', p)
    if m: forms.add(f"/mnt/{m.group(1)}/{m.group(2).replace(chr(92), '/')}")
    hits = []
    for rp, txt in REF_TEXT.items():
        lab = rp if rp.startswith('registry') else os.path.basename(rp)
        for f in forms:
            i = txt.find(f)
            # whole path component only: the next character must end the path
            while i >= 0:
                nxt = txt[i + len(f):i + len(f) + 1]
                if nxt in ('', '\\', '/', '"', "'", ' ', '\n', '\r', ',', ';', '>', '<', '|', ')'):
                    hits.append(lab); break
                i = txt.find(f, i + 1)
            if hits and hits[-1] == lab: break
    return sorted(set(hits))


# ---------------------------------------------------------------- collect items
items, untouched = [], []


def app_owned_hint(path, name):
    if name.startswith('.'):
        return 'dot-folder or dot-file: tool/app configuration, used in place'
    if name.lower() == 'node_modules':
        return 'node_modules: dependency folder of a project'
    for pat in APP_OWNED:
        if fnmatch.fnmatch(name.lower(), pat) or fnmatch.fnmatch(os.path.normcase(path).replace('\\', '/'), pat.replace('\\', '/')):
            return 'app-owned: an application keeps its data here'
    return None


def consider(path, root):
    name = os.path.basename(path.rstrip('\\/')); key = os.path.normcase(path.rstrip('\\/'))
    if key in PROTECTED or any(key.startswith(p + os.sep) for p in PROTECTED):
        untouched.append({'path': path, 'loc': root['label'], 'why': 'protected'}); return
    if key in ROOT_PATHS:
        untouched.append({'path': path, 'loc': root['label'], 'why': 'is itself a configured root (its contents are organized item by item)'}); return
    if SECURITY.search(name):
        untouched.append({'path': path, 'loc': root['label'], 'why': 'security item - left as is'}); return
    if any(fnmatch.fnmatch(name.lower(), s.lower()) for s in root.get('skip', [])) or (root.get('skip_dot') and name.startswith('.')):
        untouched.append({'path': path, 'loc': root['label'], 'why': 'skipped by config'}); return
    if is_link(path):
        untouched.append({'path': path, 'loc': root['label'], 'why': 'symlink/junction - stays (its target is organized on its own)'}); return
    try: st = os.stat(path)
    except OSError: return
    isdir = os.path.isdir(path)
    ext = '' if isdir else os.path.splitext(name)[1].lower()
    if ext in LEAVE_EXT or name.lower() in LEAVE_NAMES:
        untouched.append({'path': path, 'loc': root['label'], 'why': 'shortcut/system file - stays'}); return
    it = {'id': 'O-' + hashlib.sha1(path.lower().encode()).hexdigest()[:9], 'loc': root['label'], 'root': root.get('dest_root', root['path']),
          'path': path, 'name': name, 'kind': 'dir' if isdir else 'file', 'ext': ext,
          'created': iso(st.st_ctime), 'modified': iso(st.st_mtime)}
    if isdir:
        it['dir'], size = dir_summary(path)
        it['mb'] = round(size / 1024**2, 2)
        nw = it['dir'].get('newest_write')
        if nw and time.time() - time.mktime(time.strptime(nw, '%Y-%m-%d %H:%M')) < LIVE_DAYS * 86400 and \
                set(it['dir']['markers']) & {'.git', 'package.json', 'Cargo.toml', 'pyproject.toml', 'CLAUDE.md', 'AGENTS.md', '.obsidian'}:
            it['live_hint'] = f'project folder written to on {nw}: may be in active use'
    else:
        it['mb'] = round(st.st_size / 1024**2, 2)
        s = sniff(path, ext, st.st_size)
        if s: it['content'] = s
        if ext in INST_EXT or (ext in ('.zip', '.7z', '.tar', '.gz', '.xz') and re.search(r'(setup|install|portable|bin-|win|x64|x86_64|linux|macos|arm64|release)', name, re.I)) or re.search(r'setup|installer', name, re.I):
            it['installer'] = installer_facts(name, ext)
        if st.st_size == 0: it['temp_hint'] = 'zero bytes'
        elif ext in ('.crdownload', '.part', '.partial', '.tmp', '.download') or name.startswith('~$'): it['temp_hint'] = 'incomplete/lock file'
        elif re.match(r'(pasted (text|markdown|image)|untitled|new text document|download(\s*\(\d+\))?\.html?$)', name, re.I): it['temp_hint'] = 'clipboard/download artifact'
    h = app_owned_hint(path, name)
    if h: it['app_owned'] = h
    refs = referenced_by(path)
    if refs: it['referenced_by'] = refs
    n = notes.get(key)
    if n: it['earlier_note'] = n
    items.append(it)


for root in ROOTS:
    if ONLY and root['label'].lower() not in ONLY: continue
    if not os.path.isdir(root['path']):
        print('missing root', root['path']); continue
    for e in sorted(os.scandir(root['path']), key=lambda e: e.name.lower()):
        consider(e.path, root)


# ---------------------------------------------------------------- duplicates (full hash < 256 MB; sampled hash above)
def fhash(p, sampled=False):
    h = hashlib.blake2b(digest_size=16)
    with open(p, 'rb') as f:
        if sampled:
            size = os.fstat(f.fileno()).st_size
            for off in (0, size // 2, max(0, size - 4 * 1024**2)):
                f.seek(off); h.update(f.read(4 * 1024**2))
        else:
            for chunk in iter(lambda: f.read(4 * 1024**2), b''): h.update(chunk)
    return h.hexdigest()


by_size = defaultdict(list)
for it in items:
    if it['kind'] == 'file' and it['mb'] > 0: by_size[os.path.getsize(it['path'])].append(it)
for size, grp in by_size.items():
    if len(grp) < 2: continue
    hs = defaultdict(list)
    for it in grp:
        try: hs[fhash(it['path'], sampled=size >= 256 * 1024**2)].append(it)
        except Exception: pass
    for same in hs.values():
        if len(same) > 1:
            same.sort(key=lambda i: (bool(re.search(r'\(\d+\)|copy', i['name'], re.I)), i['created']))   # keep the plainly named, oldest copy
            for other in same[1:]:
                other['duplicate_of'] = same[0]['path']
                other['dup_method'] = 'sampled hash + equal size' if size >= 256 * 1024**2 else 'full hash'


# ---------------------------------------------------------------- version families (same base name, different version / copy marker)
def base(n):
    s = os.path.splitext(n)[0].lower()
    s = re.sub(r'\s*\(\d+\)$', '', s)
    s = re.sub(r'[-_ .]?v?\d+(?:\.\d+)+(?:[-_.][a-z0-9]+)*', '', s)
    s = re.sub(r'[-_ ](copy|final|new|old|latest|backup|bak)\b', '', s)
    return re.sub(r'[\s_\-.]+', ' ', s).strip()


fam = defaultdict(list)
for it in items:
    if it['kind'] == 'file': fam[(it['loc'], base(it['name']), it['ext'])].append(it)
for (loc, b, ext), members in fam.items():
    if len(members) < 2 or len(b) < 3: continue
    members.sort(key=lambda i: (vtuple(i['name']) or (0,), i['modified']))
    for m in members[:-1]:
        m['version_family'] = {'newest': members[-1]['name'], 'members': [x['name'] for x in members]}


# ---------------------------------------------------------------- write + chunk
items.sort(key=lambda i: (i['loc'], i['created']))
prev = OUT / 'org-items.json'
if ONLY and prev.exists():                       # partial refresh: keep the other roots' items
    old = json.loads(prev.read_text(encoding='utf-8'))
    items = [i for i in old['items'] if i['loc'].lower() not in ONLY] + items
    untouched = [u for u in old['untouched'] if u.get('loc', '').lower() not in ONLY] + untouched
prev.write_text(json.dumps({'generated': time.strftime('%Y-%m-%d %H:%M'), 'items': items, 'untouched': untouched}, indent=1), encoding='utf-8')

if '--facts-only' in sys.argv:
    print('facts refreshed:', len(items), 'items,', len(untouched), 'untouched (chunk files left as they are)')
    sys.exit(0)
size = CFG.get('chunk_size', 190)
by_chunk = defaultdict(dict)
for r in ROOTS:
    if ONLY and r['label'].lower() not in ONLY: continue
    cname = r.get('chunk') or re.sub(r'[^a-z0-9]+', '-', r['label'].lower()).strip('-')
    pre = os.path.normcase(r['path'].rstrip('\\/')) + os.sep
    for i in items:
        if i['loc'] == r['label'] and os.path.normcase(i['path']).startswith(pre):
            by_chunk[cname][i['id']] = i
written = {}
for cname, members in by_chunk.items():
    members = list(members.values())
    parts = max(1, -(-len(members) // size))
    per = -(-len(members) // parts)
    for k in range(parts):
        nm = cname if parts == 1 else f'{cname}-{k + 1}'
        part = members[k * per:(k + 1) * per]
        (OUT / f'chunk-{nm}.json').write_text(json.dumps(part, indent=1), encoding='utf-8')
        written[nm] = len(part)
print('items', len(items), 'untouched', len(untouched), 'chunks', written)
print('installed programs', len(programs), 'store apps', len(appx), '| installers', sum(1 for i in items if 'installer' in i),
      'dupes', sum(1 for i in items if 'duplicate_of' in i), 'version-family olds', sum(1 for i in items if 'version_family' in i),
      'temp hints', sum(1 for i in items if 'temp_hint' in i), 'app-owned', sum(1 for i in items if 'app_owned' in i),
      'live', sum(1 for i in items if 'live_hint' in i))
