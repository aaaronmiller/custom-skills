#!/usr/bin/env python3
"""Create a lightweight self-improvement note from a metrics bundle."""
from __future__ import annotations
import argparse, json
from pathlib import Path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--metrics', required=True)
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    data = json.loads(Path(args.metrics).expanduser().read_text())
    m = data.get('metrics', {})
    notes = ['# Weekly Report Suite Self-Improvement Notes\n']
    notes.append('## Evidence coverage\n')
    if m.get('sessions_total', 0) == 0:
        notes.append('- CASS/session activity is missing or zero; improve timeline parsing or use broader CASS queries.\n')
    if not data.get('projects'):
        notes.append('- Git project detection found no active repos; verify roots and date window.\n')
    notes.append('\n## Dashboard improvements to consider\n')
    notes.append('- Add week-over-week trend loading from prior dashboard bundles.\n')
    notes.append('- Add carry-over task closure rate once personal reports have stable checkbox parsing.\n')
    notes.append('- Add evidence confidence per project and expose it as a Prometheus label/metric.\n')
    notes.append('\n## Narrative improvements to consider\n')
    notes.append('- Check dad report length against recent examples and trim if over 750 words.\n')
    notes.append('- Verify designed/scaffolded work is not described as shipped or running.\n')
    out = Path(args.out).expanduser(); out.parent.mkdir(parents=True, exist_ok=True); out.write_text(''.join(notes)); print(out)
if __name__ == '__main__':
    main()
