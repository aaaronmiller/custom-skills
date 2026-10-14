"""build_removal_manifest.py - turn the checkup's read-only census into a reviewed removal manifest.

Nothing is deleted here. Output: <checkup>/removal/removal-manifest.json, consumed by
Remove-CheckupItems.ps1 (dry-run by default). Every item states what it is, why it is safe,
how it regenerates, its risk, and whether it is ON by default.

Usage: python -I build_removal_manifest.py <checkup_dir>
"""
import csv, json, os, re, sys, time
from pathlib import Path

CK = Path(sys.argv[1]); RAW = CK / 'raw'; ST = RAW / 'storage'; OUT = CK / 'removal'
OUT.mkdir(parents=True, exist_ok=True)
HOME = r'C:\Users\Administrator'
items = []

def add(**kw):
    kw.setdefault('default', True); kw.setdefault('risk', 'safe'); kw.setdefault('requires', [])
    kw.setdefault('action', 'delete'); kw['gb'] = round(float(kw.get('gb', 0) or 0), 3)
    kw['id'] = f"{kw['section'][:3].upper()}-{len(items)+1:03d}"
    items.append(kw)

def rows(p):
    try: return list(csv.DictReader(open(p, encoding='utf-8')))
    except FileNotFoundError: return []

GUID = re.compile(r'^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}$')

# ------------------------------------------------------------------ 1. Windows temp
KEEP_TEMP = {'claude', 'wsl-crashes'}
_small_temp = {}
for r in rows(ST / 'temp-items.csv'):
    name, tdir = r['item'], r['tempdir']
    path = os.path.join(tdir, name)
    age = float(r['age_days'] or 0); gbv = float(r['gb'] or 0); lock = r['lock'] or ''
    if name in KEEP_TEMP:
        continue
    # Only real system/user temp is auto-cleaned. C:\tmp, C:\Temp, D:\tmp hold user-created files
    # (notes, scripts) and are classified in the living document instead.
    if tdir.lower() not in (HOME.lower() + r'\appdata\local\temp', r'c:\windows\temp'):
        continue
    if 'swap.vhdx' in lock or (GUID.match(name) and r['type'] == 'dir'):
        add(section='Windows temp', title=f'WSL swap disk folder {name}', path=path, gb=gbv, action='delete-wsl-swap',
            why='WSL creates a fresh swap.vhdx per VM start and never removes old ones.',
            regenerates='WSL makes a new one at next start', risk='low',
            guard='Skipped unless the VHDX opens exclusively AND is older than the running vmmemWSL start time.')
        continue
    if 'LOCKED' in lock or age < 7:
        continue
    if gbv >= 0.1:
        req = ['admin'] if tdir.lower().startswith(r'c:\windows') else []
        add(section='Windows temp', title=name, path=path, gb=gbv, requires=req, action='delete', min_age_days=7,
            why=f'Unlocked temp item, last touched {age:.0f} days ago.', regenerates='Not needed; temp',
            guard='Re-checked at run time: still >= 7 days old and not locked.')
    else:
        _small_temp.setdefault(tdir, []).append((path, gbv))
for tdir, lst in _small_temp.items():
    add(section='Windows temp', title=f'{len(lst)} small stale items in {tdir}', paths=[p for p, _ in lst], gb=sum(g for _, g in lst),
        requires=(['admin'] if tdir.lower().startswith(r'c:\windows') else []), action='delete', min_age_days=7,
        why='Installer leftovers, .tmp files, updater stubs and logs untouched for 7+ days.', regenerates='Not needed; temp',
        guard='Each path re-checked at run time: >= 7 days old, not locked; anything else is skipped.')
add(section='Windows temp', title='WSL crash dumps (%TEMP%\\wsl-crashes)', path=HOME + r'\AppData\Local\Temp\wsl-crashes',
    gb=next((float(r['gb']) for r in rows(ST / 'temp-items.csv') if r['item'] == 'wsl-crashes'), 0), default=False, risk='review',
    why='6+ GB of WSL/cass crash dumps. Evidence for crash triage; the WSL-agent handoff asked to keep crash data.',
    regenerates='No - evidence', action='delete')

# ------------------------------------------------------------------ 2. Windows caches
caches = {r['path']: r for r in rows(ST / 'caches.csv')}
def cache_gb(p): return float(caches.get(p, {}).get('gb', 0) or 0)
add(section='Windows caches', title='uv package cache (Windows)', command='uv cache clean', gb=cache_gb(HOME + r'\AppData\Local\uv\cache'),
    action='command', why='uv download/build cache; 15+ GB of wheels incl. several torch builds.', regenerates='uv re-downloads on next install',
    guard='Runs `uv cache clean`, which waits for any uv process holding the cache lock.')
add(section='Windows caches', title='npm cache (Windows)', command='npm cache clean --force', gb=cache_gb(HOME + r'\AppData\Local\npm-cache'),
    action='command', why='npm content cache.', regenerates='npm refetches')
add(section='Windows caches', title='pip cache (Windows)', command='python -m pip cache purge', gb=cache_gb(HOME + r'\AppData\Local\pip\cache'),
    action='command', why='pip wheel cache.', regenerates='pip refetches')
add(section='Windows caches', title='VS Code downloaded VSIX copies', path=HOME + r'\AppData\Roaming\Code\CachedExtensionVSIXs',
    gb=cache_gb(HOME + r'\AppData\Roaming\Code\CachedExtensionVSIXs'), why='Copies of every extension package ever installed.',
    regenerates='Re-downloaded only if an extension is reinstalled')
add(section='Windows caches', title='Raspberry Pi Imager last-download cache', path=HOME + r'\AppData\Local\Raspberry Pi\Raspberry Pi Imager\cache',
    gb=1.161, why='Cached OS image from the last flash (Feb 2026).', regenerates='Imager re-downloads the image')
add(section='Windows caches', title='Slack offline caches', paths=[HOME + r'\AppData\Roaming\Slack\Service Worker\CacheStorage', HOME + r'\AppData\Roaming\Slack\Cache', HOME + r'\AppData\Roaming\Slack\Code Cache'],
    gb=cache_gb(HOME + r'\AppData\Roaming\Slack\Service Worker\CacheStorage') + cache_gb(HOME + r'\AppData\Roaming\Slack\Cache'),
    requires=['closed:slack'], why='HTTP/service-worker caches only. Login, workspaces and settings live elsewhere (Local Storage, Cookies) and are not touched.',
    regenerates='Slack refills on next launch')
add(section='Windows caches', title='Discord / Obsidian / Antigravity / Kiro HTTP caches', paths=[HOME + rf'\AppData\Roaming\{a}\{s}' for a in ('discord', 'obsidian', 'Antigravity', 'Kiro') for s in ('Cache', 'Code Cache', 'GPUCache')],
    gb=sum(cache_gb(HOME + rf'\AppData\Roaming\{a}\{s}') for a in ('discord', 'obsidian', 'Antigravity', 'Kiro') for s in ('Cache', 'Code Cache', 'GPUCache')),
    requires=['closed:discord', 'closed:obsidian', 'closed:antigravity', 'closed:kiro'],
    why='Electron cache folders only. Obsidian vault, plugins and workspace are never touched; app sign-ins live in Local Storage/Cookies.',
    regenerates='Rebuilt on next launch')
add(section='Windows caches', title='Chrome HTTP/code/GPU caches (all profiles)', paths=[HOME + rf'\AppData\Local\Google\Chrome\User Data\{p}\{s}' for p in ('Default', 'Profile 1') for s in ('Cache', 'Code Cache', 'GPUCache')],
    gb=sum(cache_gb(HOME + rf'\AppData\Local\Google\Chrome\User Data\{p}\{s}') for p in ('Default', 'Profile 1') for s in ('Cache', 'Code Cache', 'GPUCache')),
    default=False, risk='low', requires=['closed:chrome'],
    why='Cache only. Cookies, logins, history, sessions and extensions are separate files and are never touched. Off by default because Chrome must be fully closed.',
    regenerates='Pages re-cache as you browse')
add(section='Windows caches', title='VoiceStudio build cache (xpu-uv-cache)', path=HOME + r'\AppData\Local\VoiceStudioBuild\xpu-uv-cache', gb=6.222,
    default=False, risk='review', why='uv cache from the Sep 30 VoiceStudio XPU build.', regenerates='Re-downloaded on the next VoiceStudio rebuild')
add(section='Windows caches', title='VoiceStudio runtime private uv cache', path=HOME + r'\AppData\Roaming\VoiceStudio\runtime\.uv-cache', gb=0,
    default=False, risk='review', why='Second copy of the torch wheels already installed in the runtime venv.', regenerates='Re-downloaded if the runtime is rebuilt')
add(section='Windows caches', title='Hugging Face hub cache (Windows)', path=HOME + r'\.cache\huggingface', gb=cache_gb(HOME + r'\.cache\huggingface'),
    default=False, risk='review', why='Downloaded model weights. Only remove models you no longer run.', regenerates='Re-download (slow)')
add(section='Windows caches', title='User-mode crash dumps', path=HOME + r'\AppData\Local\CrashDumps', gb=cache_gb(HOME + r'\AppData\Local\CrashDumps'),
    default=False, risk='review', why='CrossDeviceService and other app crash dumps; keep until crash triage is done.', regenerates='No - evidence')
add(section='Windows caches', title='Delivery Optimization cache', command='Delete-DeliveryOptimizationCache -Force', gb=0.86, action='command-ps',
    requires=['admin'], why='Peer-download cache for Windows/Store updates.', regenerates='Windows refills as needed')
add(section='Windows caches', title='Stale Windows Update download (SoftwareDistribution\\Download)', path=r'C:\Windows\SoftwareDistribution\Download', gb=0.34,
    requires=['admin', 'service-stop:wuauserv,bits'], action='delete-contents',
    why='Partial payloads of the 28020.2207 feature update that can never install (expired signing cert).', regenerates='WU re-downloads what it needs')
add(section='Windows caches', title='Cap Volume Shadow Copy storage on C: at 20 GB', command='vssadmin resize shadowstorage /for=C: /on=C: /maxsize=20GB', gb=19.9,
    action='command-ps', requires=['admin'], default=False, risk='review',
    why='Shadow storage is 39.9 GB and UNBOUNDED. Capping deletes the oldest snapshots beyond 20 GB.', regenerates='New restore points/backup snapshots keep working within the cap')

# ------------------------------------------------------------------ 3. WSL (commands run inside Ubuntu)
w1 = {}
try: w1 = json.load(open(CK / 'workers' / 'W1-wsl-audit.json', encoding='utf-8'))
except Exception: pass
def w1gb(fragment):
    for r in w1.get('reclaimable', []):
        if fragment in r.get('path', ''): return round(r.get('bytes', 0) / 1024**3, 2)
    return 0
add(section='WSL', title='uv cache (WSL)', wsl='uv cache clean', gb=w1gb('.cache/uv') or 6.8, action='wsl',
    why='uv archive cache (7 GB).', regenerates='uv re-downloads on next install')
add(section='WSL', title='pnpm store prune (Linux pnpm, not the Windows one on PATH)', wsl='"$HOME/.local/share/pnpm/pnpm" store prune', gb=w1gb('pnpm/store') or 5.7, action='wsl',
    why='Removes packages no project references. Uses the Linux pnpm explicitly because `pnpm` on the WSL PATH is the Windows binary.', regenerates='pnpm refetches on demand')
add(section='WSL', title='npm cache (WSL)', wsl='npm cache clean --force', gb=w1gb('.npm') or 0.97, action='wsl', why='npm _cacache.', regenerates='npm refetches')
add(section='WSL', title='Superseded Rust toolchain 1.98.0 (stable is 1.98.1)', wsl='grep -rqs --include="rust-toolchain*" "1.98.0" ~/git ~/code ~/code2 || rustup toolchain uninstall 1.98.0-x86_64-unknown-linux-gnu',
    gb=1.47, action='wsl', why='Patch release superseded by the active stable 1.98.1.', regenerates='rustup reinstalls if a project pins it',
    guard='Skips itself if any rust-toolchain file pins 1.98.0.')
add(section='WSL', title='Dated nightly toolchain nightly-2026-08-31', wsl='grep -rqs --include="rust-toolchain*" "2026-08-31" ~/git ~/code ~/code2 || rustup toolchain uninstall nightly-2026-08-31-x86_64-unknown-linux-gnu',
    gb=1.50, action='wsl', default=False, risk='review', why='Older pinned nightly next to the current nightly.', regenerates='rustup reinstalls on demand')
add(section='WSL', title='Old Puppeteer browsers (Chrome 127 + leftover zip)', wsl='rm -rf ~/.cache/puppeteer/chrome/linux-127.0.6533.88 ~/.cache/puppeteer/chrome-headless-shell/linux-127.0.6533.88 ~/.cache/puppeteer/chrome/148.0.7778.167-chrome-linux64.zip',
    gb=0.43, action='wsl', why='Chrome 127 is 23 versions old; the zip is an already-extracted download.', regenerates='Puppeteer re-downloads a pinned build if a project asks for it')
add(section='WSL', title='Puppeteer Chrome 148/149 (keep 150)', wsl='rm -rf ~/.cache/puppeteer/chrome/linux-148.0.7778.167 ~/.cache/puppeteer/chrome/linux-149.0.7827.22 ~/.cache/puppeteer/chrome-headless-shell/linux-148.0.7778.167 ~/.cache/puppeteer/chrome-headless-shell/linux-149.0.7827.22',
    gb=1.22, action='wsl', default=False, risk='low', why='Two superseded browser builds.', regenerates='Re-downloaded by projects pinned to them')
add(section='WSL', title='opencode logs older than 14 days', wsl='find ~/.local/share/opencode/log -type f -mtime +14 -delete', gb=0.6, action='wsl',
    why='opencode log dir is 0.9 GB; the opencode binary is not even installed any more.', regenerates='No - logs')
add(section='WSL', title='Old codex app-server releases (keep current)', wsl='cd ~/.codex/packages/app-server-daemon/releases && cur=$(readlink -f ../current | xargs basename) && ls | grep -vx "$cur" | xargs -r rm -rf',
    gb=2.5, action='wsl', default=False, risk='low', why='codex keeps every downloaded app-server release (2.9 GB).', regenerates='codex re-downloads if it needs to roll back')
add(section='WSL', title='Journal vacuum to 200 MB', wsl='sudo -n journalctl --vacuum-size=200M', gb=0.17, action='wsl', default=False, risk='low',
    why='Journald is 367 MB.', regenerates='No - old logs')
add(section='WSL', title='Docker build cache', wsl='docker builder prune -f', gb=1.13, action='wsl', default=False, risk='low',
    why='Build layers only; images/containers untouched.', regenerates='Next build is slower once')
add(section='WSL', title='24 GB /swapfile-cass (swap inside the WSL disk)', wsl='sudo -n swapoff /swapfile-cass && sudo -n rm /swapfile-cass && sudo -n sed -i "\\#/swapfile-cass#d" /etc/fstab',
    gb=24.0, action='wsl', default=False, risk='review',
    why='Added Sep 18 for cass indexing. With swap=4GB + earlyoom already in place, 28 GB of total swap invites the slow-thrash mode you said you never want. Remove only if cass indexing no longer needs it.',
    regenerates='Recreate with fallocate if needed')
for r in w1.get('node_modules', []):
    p = r.get('path', '')
    if r.get('stale') and re.search(r'/tmp/|/\.archive/|__MACOSX|/archive/', p) and r.get('bytes', 0) > 50 * 1024**2:
        nm = p if p.endswith('node_modules') else p.rstrip('/') + '/node_modules'
        add(section='WSL', title=f'Stale node_modules in archived copy: {p.replace("/home/cheta/", "~/")}', wsl=f'rm -rf "{nm}"',
            gb=round(r['bytes'] / 1024**3, 2), action='wsl', why='Dependencies of an archived/tmp copy untouched for 90+ days.',
            regenerates='`pnpm i` / `bun i` if the copy is ever revived')

# ------------------------------------------------------------------ 4. obsolete installs
add(section='Obsolete installs', title='Empty Process Lasso ProgramData remnant', path=r'C:\ProgramData\ProcessLasso', gb=0, requires=['admin'],
    why='Installer default left by the portable repack; engine uses the Desktop Data folder.', regenerates='n/a')
add(section='Obsolete installs', title='Empty Process Lasso Roaming remnant', path=HOME + r'\AppData\Roaming\ProcessLasso', gb=0,
    why='Unused default per-user folder.', regenerates='n/a')
add(section='Obsolete installs', title='Dead Process Lasso config (C:\\Bitsum ...\\Data)', path=r'C:\Bitsum Process Lasso Pro v14.0.0.40 Multilingual Portable [FTUApps]\Data',
    gb=0.003, action='quarantine', requires=['admin'],
    why='v14-era config/log the running engine never reads (HKLM ConfigFolderEx points at the Desktop copy). Quarantined, not deleted.',
    regenerates='n/a', guard='Refuses if HKLM\\SOFTWARE\\ProcessLasso\\ConfigFolderEx points inside it.')

# ------------------------------------------------------------------ 5. duplicates (stage, never hard-delete)
d = rows(ST / 'dupes.csv')
groups = {}
for r in d: groups.setdefault(r['group'], []).append(r)
USERDATA = ('\\pictures\\', '\\videos\\', '\\music\\', '\\documents\\chetaz')
for gid, gs in groups.items():
    keep = next((x for x in gs if x['keep_suggest'] == 'keep'), gs[0])
    for x in gs:
        if x is keep: continue
        p = x['path']; lp = p.lower()
        if any(s in lp for s in ('\\appdata\\', '\\.cache\\', '\\.vscode\\', 'node_modules', '\\site-packages\\', '\\.venv', '\\uv\\cache', 'performance-diagnostics', '0.defenderexclusions')):
            continue   # tool-managed copies (venvs, caches) are handled by cache commands, not file dedupe
        if lp.startswith('d:\\casr-mirror') or keep['path'].lower().startswith('d:\\casr-mirror'):
            continue   # dated backup generations, rotated by session-mirror.sh (7 daily + 3 monthly) - duplicates by design
        if re.match(r'^c:\\users\\administrator\\\.', lp):
            continue   # copies inside tool dot-folders (.lmstudio, .antigravity, .local\share\claude\versions ...) belong to those tools
        full = x['hash'] == 'full'
        # Default-on only for loose top-level files in Downloads/Desktop/Documents, or installers/archives
        # anywhere; a file inside a folder structure (exports, app bundles, backups) is opt-in, because
        # moving one file out of it breaks the folder it belongs to. Security-flagged folders are never default.
        rel_depth = None
        for root in ('\\downloads\\', '\\desktop\\', '\\documents\\'):
            if root in lp: rel_depth = lp.split(root, 1)[1].count('\\'); break
        loose = rel_depth == 0
        packaged = lp.endswith(('.exe', '.msi', '.msix', '.zip', '.7z', '.rar', '.iso', '.img', '.vsix', '.appimage', '.deb'))
        security = any(s in lp for s in ('mdm', 'rodbautis', 'keymaker', 'crack', 'password', 'passview'))
        # (packaged files inside folders are often an app's own binaries, e.g. m5burner\packages\tool\*.exe,
        #  so nested copies stay opt-in even when they look like installers)
        on = bool(full and not any(s in lp for s in USERDATA) and loose and not security)
        add(section='Duplicates', title=os.path.basename(p), path=p, keep=keep['path'], gb=float(x['mb']) / 1024,
            action='stage', default=on, risk=('safe' if full else 'review'),
            why=f"Byte-identical to {keep['path']} ({'full hash' if full else 'size + 3x4 MB sampled hash'}).",
            regenerates='The kept copy remains', guard='Moved to _REVIEW-then-delete next to it, not deleted.')

# ------------------------------------------------------------------ 6. user-folder decisions from the living document (W2)
try:
    data = json.load(open(CK / 'workers' / 'W2-livingdoc-v3-DATA.json', encoding='utf-8'))
except Exception:
    data = None
if data:
    for g in data.get('groups', []):
        if g.get('id') in ('protected', 'resolved-since-july') or not g.get('section', '').startswith('Reclaim'):
            continue
        for f in g.get('files', []):
            add(section='User folders (living doc)', title=f.split('  ')[0], livingdoc_group=g['id'], loc=g.get('loc', ''), note=f,
                action='stage-by-name', default=False, risk='review', gb=0,
                why=g.get('fn', ''), regenerates='Kept in _REVIEW-then-delete until you empty it',
                guard='Applied only from the living document export (your per-file decisions), never blindly.')

# ------------------------------------------------------------------ write
summary = {}
for it in items:
    s = summary.setdefault(it['section'], {'items': 0, 'gb_default': 0.0, 'gb_all': 0.0})
    s['items'] += 1; s['gb_all'] += it['gb']; s['gb_default'] += it['gb'] if it['default'] else 0
for s in summary.values(): s['gb_default'] = round(s['gb_default'], 2); s['gb_all'] = round(s['gb_all'], 2)
manifest = {'generated': time.strftime('%Y-%m-%d %H:%M'), 'checkup': str(CK), 'summary': summary, 'items': items,
            'protected': [r'C:\0.defenderexclusions', r'D:\0.defenderexclusions', HOME + r'\Documents\chetaz',
                          HOME + r'\Desktop\Bitsum Process Lasso Pro v14.0.0.40 Multilingual Portable [FTUApps]',
                          r'C:\performance-diagnostics', HOME + r'\.claude', HOME + r'\.config', HOME + r'\.ssh',
                          HOME + r'\AppData\Local\Packages\CanonicalGroupLimited.Ubuntu_79rhkp1fndgsc',
                          r'D:\SPECTRE-16-UGLYBETTY.tibx', HOME + r'\Downloads\downloads-desktop-cleanup.livingdoc']}
(OUT / 'removal-manifest.json').write_text(json.dumps(manifest, indent=1), encoding='utf-8')
print(json.dumps(summary, indent=1)); print('items', len(items), '->', OUT / 'removal-manifest.json')
