"""build_report.py - render the checkup report: template + report-data.json -> single HTML file.

Usage: python -I build_report.py <checkup_dir> [--dism "<text>"]
Writes <checkup_dir>/report/SPECTRE-16-checkup.html
"""
import json, sys, time
from pathlib import Path

CK = Path(sys.argv[1]); REP = CK / 'report'
dism = 'Component store repairable (the 187 icon files); 4.6 GB store, nothing to clean'
if '--dism' in sys.argv:
    dism = sys.argv[sys.argv.index('--dism') + 1]
tpl = (REP / 'report-template.html').read_text(encoding='utf-8')
data = json.loads((REP / 'report-data.json').read_text(encoding='utf-8'))
blob = json.dumps(data, separators=(',', ':')).replace('</', '<\\/')   # keep </script> out of the JSON island
html = (tpl.replace('__REPORT_DATA__', blob)
           .replace('__DISM_RESULT__', dism)
           .replace('__GENERATED__', time.strftime('%Y-%m-%d %H:%M')))
for token in ('__REPORT_DATA__', '__DISM_RESULT__', '__GENERATED__'):
    assert token not in html, token
out = REP / 'SPECTRE-16-checkup.html'
out.write_text(html, encoding='utf-8')
print(out, f'{len(html)/1024:.0f} KB')
