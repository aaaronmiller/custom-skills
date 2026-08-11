#!/usr/bin/env python3
"""RETIRED: Use weekly-report-dashboard/scripts/build_dashboard.py instead.

This single-week renderer is retained for historic compatibility but is no longer
the canonical dashboard generator. It will not be updated. See
custom-skills/weekly-report-suite/SKILL.md for the canonical command.
Historic per-week bundles are preserved; this script is retired.
"""
from __future__ import annotations
import argparse, json, shutil
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = SKILL_ROOT / 'references' / 'templates' / 'dashboard.html'


def main():

    ap = argparse.ArgumentParser()
    ap.add_argument('--metrics', required=True)
    ap.add_argument('--dad-report', required=False)
    ap.add_argument('--personal-report', required=False)
    ap.add_argument('--out-dir', required=True)
    args = ap.parse_args()
    out = Path(args.out_dir).expanduser(); out.mkdir(parents=True, exist_ok=True)
    metrics_src = Path(args.metrics).expanduser()
    data = json.loads(metrics_src.read_text())
    (out / 'weekly-metrics.json').write_text(json.dumps(data, indent=2))
    for src_arg, name in [(args.dad_report, 'dad-report.md'), (args.personal_report, 'personal-report.md')]:
        if src_arg and Path(src_arg).expanduser().exists():
            (out / name).write_text(Path(src_arg).expanduser().read_text())
        else:
            (out / name).write_text('')
    (out / 'index.html').write_text(TEMPLATE.read_text())
    # Small README for humans and future agents.
    (out / 'README.md').write_text(f"""# Weekly Dashboard Bundle\n\nOpen `index.html` in a browser or serve this directory with:\n\n```bash\npython3 -m http.server 8765\n```\n\nFiles:\n- `weekly-metrics.json` — dashboard data model\n- `dad-report.md` — concise report\n- `personal-report.md` — detailed source report\n- `index.html` — static dashboard\n\nPeriod: {data.get('period',{}).get('start')} to {data.get('period',{}).get('end')}\n""")
    print(out / 'index.html')

if __name__ == '__main__':
    main()
