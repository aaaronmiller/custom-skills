#!/usr/bin/env python3
"""Scaffold hunts/hunt-N.md from template. Usage: hunt_report.py --hunt 1 --angle wellfound --date 2026-08-20"""
import argparse, pathlib, datetime
ap = argparse.ArgumentParser()
ap.add_argument("--hunt", required=True); ap.add_argument("--angle", required=True); ap.add_argument("--date", default=datetime.date.today().isoformat())
args = ap.parse_args()
tpl = pathlib.Path("references/hunt-template.md").read_text() if pathlib.Path("references/hunt-template.md").exists() else pathlib.Path(__file__).parent.parent.joinpath("references/hunt-template.md").read_text()
out = pathlib.Path(f"hunts/hunt-{args.hunt}.md"); out.parent.mkdir(parents=True, exist_ok=True)
content = tpl.replace("{{N}}", args.hunt).replace("{{Angle Name}}", args.angle).replace("{{Date}}", args.date)
out.write_text(content)
print(f"Scaffolded {out}")
