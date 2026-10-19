"""build_approval_page.py - embed removal/cleanup-plan.json into the approval console template.

Usage: python -I build_approval_page.py <checkup_dir> [template]
Writes <checkup_dir>/removal/Cleanup-Approvals.html (opens from disk; exports decisions as JSON).
"""
import json, sys
from pathlib import Path

CK = Path(sys.argv[1])
tpl_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).resolve().parent.parent / 'templates' / 'approval-template.html'
plan = json.loads((CK / 'removal' / 'cleanup-plan.json').read_text(encoding='utf-8'))
html = tpl_path.read_text(encoding='utf-8').replace('__PLAN__', json.dumps(plan, separators=(',', ':')).replace('</', '<\\/'))
assert '__PLAN__' not in html
out = CK / 'removal' / 'Cleanup-Approvals.html'
out.write_text(html, encoding='utf-8')
print(out, f'{len(html) // 1024} KB, {len(plan["items"])} items, plan {plan["plan_id"]}')
