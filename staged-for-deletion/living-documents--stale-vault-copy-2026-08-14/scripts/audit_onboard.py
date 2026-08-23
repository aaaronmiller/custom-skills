#!/usr/bin/env python3
"""audit_onboard — score onboard supplementation quality (stdlib, offline).

Scores prompt completeness %, file-desc coverage, story extract, provenance.
Mirrors weekly audit_viz → meta_improve loop: propose deltas that raise
overall_avg/Actionability without regressing Truthfulness/Provenance.

Usage: python3 scripts/audit_onboard.py --json
       python3 scripts/audit_onboard.py --project living-documents-system --json
"""

import argparse
import json
import pathlib

REPO_HOME = pathlib.Path.home() / "LIVING_DOCUMENTS" / "projects"

def audit(project: str) -> dict:
    root = REPO_HOME / project
    scores = {}
    problems = []
    if not root.is_dir():
        return {"project": project, "error": "missing", "overall_avg": 0}
    # prompt completeness: prompt-corpus.md exists and non-placeholder?
    pc = root / "prompt-corpus.md"
    if pc.is_file():
        txt = pc.read_text(encoding="utf-8", errors="replace")
        scores["promptCompleteness"] = 0.9 if "spell-fixed" in txt or len(txt) > 500 else 0.4
        if "Placeholder" in txt:
            scores["promptCompleteness"] = 0.3
            problems.append("prompt-corpus placeholder not filled")
    else:
        scores["promptCompleteness"] = 0.0
        problems.append("missing prompt-corpus.md")
    # file-desc coverage
    fi = root / "file-index.md"
    if fi.is_file():
        lines = fi.read_text(encoding="utf-8", errors="replace").splitlines()
        # expect at least fileCount-ish lines
        scores["fileDescCoverage"] = min(1.0, len([l for l in lines if l.strip().startswith("-") or l.strip().endswith(".md")]) / 10)
    else:
        scores["fileDescCoverage"] = 0.0
    # provenance: project.md has source-root?
    pm = root / "project.md"
    if pm.is_file():
        txt = pm.read_text(encoding="utf-8", errors="replace")
        scores["provenance"] = 1.0 if "source-root" in txt else 0.5
    else:
        scores["provenance"] = 0.0
    overall = sum(scores.values()) / len(scores) if scores else 0
    return {"project": project, "scores": scores, "overall_avg": round(overall, 3), "Actionability": scores.get("fileDescCoverage", 0), "Truthfulness": scores.get("provenance", 0), "problems": problems}

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--project", default="living-documents-system")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    result = audit(args.project)
    print(json.dumps(result, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
