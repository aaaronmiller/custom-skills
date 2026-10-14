"""build_report_data.py - assemble the checkup report's chart/table data into one JSON blob.

Reads only files produced earlier in the checkup (raw/, report/, workers/, removal/) and writes
report/report-data.json. build_report.py then embeds it into the HTML template.

Usage: python -I build_report_data.py <checkup_dir>
"""
import csv, json, re, sys
from collections import defaultdict
from pathlib import Path

CK = Path(sys.argv[1]); RAW = CK / 'raw'; REP = CK / 'report'

def jload(p, default=None):
    try: return json.load(open(p, encoding='utf-8-sig'))
    except Exception: return default

tele = jload(REP / 'telemetry-history.json', {})
ev = jload(REP / 'events.json', {})
man = jload(CK / 'removal' / 'removal-manifest.json', {})
system = jload(RAW / 'system.json', {})
disks = jload(RAW / 'disks.json', [])
pf = jload(RAW / 'pagefile.json', {})

# --- commit composition at collection time (private bytes by owner) ------------------
GROUPS = [
    ('WSL VM (vmmemWSL)', r'^vmmemwsl$'),
    ('Chrome', r'^chrome$'),
    ('Windows Sandbox', r'^(vmmemwindowssandbox|vmmemcmzygote|windowssandboxremotesession|windowssandbox.*)$'),
    ('Intel Connectivity suite', r'^(intelconnect|intelconnectivitynetworkservice|idbwmservice)$'),
    ('Intel PROSet/Wireless (PIE)', r'^intel_pie_service$'),
    ('OpenWhispr + ASR engine', r'^(openwhispr|sherpa-onnx-ws-win32-x64)$'),
    ('Edge WebView2 hosts', r'^msedgewebview2$'),
    ('Joplin', r'^joplin$'),
    ('Claude Code (Windows)', r'^claude$'),
    ('Phone Link', r'^(phoneexperiencehost|crossdeviceservice)$'),
    ('Explorer + DWM', r'^(explorer|dwm)$'),
    ('WezTerm', r'^wezterm-gui$'),
]
agg = defaultdict(float); other = 0.0; total = 0.0
for r in csv.DictReader(open(RAW / 'processes.csv', encoding='utf-8-sig')):
    n = r['Name'].lower(); mb = float(r['Private_MB'] or 0); total += mb
    for label, pat in GROUPS:
        if re.match(pat, n): agg[label] += mb; break
    else: other += mb
commit_now = [{'name': k, 'gb': round(v / 1024, 2)} for k, v in sorted(agg.items(), key=lambda kv: -kv[1])]
commit_now.append({'name': 'Everything else (~300 processes)', 'gb': round(other / 1024, 2)})

# --- WSL disk interior (du, MB) -------------------------------------------------------
wsl_top = []
du = RAW / 'wsl-du' / 'du-root-d4.txt'
if du.exists():
    rows = [l.split('\t') for l in du.read_text(encoding='utf-8', errors='replace').splitlines() if '\t' in l]
    size = {p: int(s) for s, p in rows}
    pick = ['/home/cheta/.local/share/coding-agent-search', '/home/cheta/git', '/home/cheta/code', '/home/cheta/code2',
            '/home/cheta/.hermes', '/var/lib/containerd', '/home/cheta/.cache', '/home/cheta/.litellm', '/home/cheta/.guardian',
            '/home/cheta/.npm-global', '/home/cheta/comfy', '/home/cheta/.rustup', '/home/cheta/.venvs', '/home/cheta/wsl-kernel',
            '/usr/local/lib/ollama', '/home/cheta/.codex']
    for p in pick:
        if p in size: wsl_top.append({'path': p.replace('/home/cheta', '~'), 'gb': round(size[p] / 1024, 1)})
    wsl_top.append({'path': '/swapfile-cass (single file)', 'gb': 24.0})
    wsl_top.sort(key=lambda x: -x['gb'])
    wsl_used_gb = round(size.get('/', 0) / 1024, 1)
else:
    wsl_used_gb = None

# --- C: composition -------------------------------------------------------------------
c = next((d for d in disks if d.get('DeviceID') == 'C:'), {})
c_size = c.get('SizeGB', 947.9); c_free = c.get('FreeGB', 120.3)
parts = [('WSL Ubuntu disk (ext4.vhdx)', 371.8), ('Other AppData', 115.3), ('Pictures', 91.9), ('Shadow copies (VSS)', 39.9),
         ('Downloads + Desktop + Documents + Music', 42.2), ('Windows folder', 33.6), ('Home dot-folders', 31.1),
         ('Pagefile', round((pf.get('AllocatedBaseSize', 29525) if isinstance(pf, dict) else 29525) / 1024, 1))]
known = sum(v for _, v in parts)
c_parts = [{'name': n, 'gb': v} for n, v in parts] + [{'name': 'Program Files, ProgramData, other', 'gb': round(c_size - c_free - known, 1)},
                                                      {'name': 'Free', 'gb': c_free}]

# --- reclaim summary --------------------------------------------------------------------
reclaim = [{'section': k, 'items': v['items'], 'default_gb': v['gb_default'], 'all_gb': v['gb_all']} for k, v in man.get('summary', {}).items()]

out = {
    'generated': system.get('Collected', ''),
    'system': system, 'disks': disks,
    'tele_daily': tele.get('daily', []), 'tele_phase': tele.get('phase', []), 'proc_peaks': tele.get('proc_peaks', {}),
    'wu_weekly': ev.get('wu_fail_weekly', []), 'wu_total': ev.get('wu_fail_total'),
    'exhaustion_daily': ev.get('exhaustion_daily', []), 'exhaustion_total': ev.get('exhaustion_total'),
    'unclean': ev.get('unclean', []), 'bt_daily': ev.get('bt_daily', []),
    'app_errors': ev.get('app_errors_top', []), 'sys_errors': ev.get('sys_errors_top', []),
    'commit_now': commit_now, 'commit_total_gb': round(total / 1024, 1),
    'wsl_top': wsl_top, 'wsl_used_gb': wsl_used_gb, 'c_parts': c_parts, 'reclaim': reclaim,
}
(REP / 'report-data.json').write_text(json.dumps(out, indent=1), encoding='utf-8')
print('report-data.json written:', {k: (len(v) if isinstance(v, list) else v) for k, v in out.items() if k not in ('system', 'disks', 'proc_peaks')})
