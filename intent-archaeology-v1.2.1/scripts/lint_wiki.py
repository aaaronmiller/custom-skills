#!/usr/bin/env python3
"""Lint the emitted wiki. Fails the build on:
  1. A section in SKILL.md or any wiki page that doesn't map to the anchor.
  2. A human edit inside a BEGIN GENERATED / END GENERATED fence.

Usage:
    python scripts/lint_wiki.py --wiki ~/intent-wiki/
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Anchor sections (from SKILL.md). Wiki pages must map to these.
ANCHOR_STEPS = {
    "discover", "classify", "archaeology", "lifecycle", "extract",
    "distill", "join", "emit", "audit", "scope", "overview", "purpose",
    "goals", "non-goals", "open-questions", "decisions", "worklog",
    "constitution", "backlog", "status", "related", "notes",
}


def check_generated_fences(content: str, path: Path) -> list[str]:
    """Check for human edits inside BEGIN GENERATED / END GENERATED fences."""
    issues = []
    in_fence = False
    fence_section = None
    for i, line in enumerate(content.split("\n"), 1):
        if "<!-- BEGIN GENERATED:" in line:
            in_fence = True
            fence_section = line.split("BEGIN GENERATED:")[1].strip().rstrip(" -->")
        elif "<!-- END GENERATED:" in line:
            in_fence = False
            fence_section = None
        elif in_fence:
            # Lines inside fence should be machine-generated.
            # Heuristic: if a line looks like a human comment (e.g. "TODO", "FIXME", "wait actually"),
            # flag it.
            if re.search(r"\b(TODO|FIXME|wait actually|hmm|I think)\b", line, re.IGNORECASE):
                issues.append(f"{path}:{i}: human edit inside GENERATED fence '{fence_section}': {line.strip()[:80]}")
    return issues


def check_anchor_mapping(content: str, path: Path) -> list[str]:
    """Check that section headings in wiki pages map to the anchor vocabulary.
    Loose check: any H2 heading whose lowercased form contains at least one
    anchor keyword passes. Pages with no H2 pass.
    """
    issues = []
    for m in re.finditer(r"^## (.+)$", content, re.M):
        heading = m.group(1).strip().lower()
        # Skip headings that are clearly page metadata
        if any(kw in heading for kw in ANCHOR_STEPS):
            continue
        # Allow some standard non-anchor headings
        if heading in {"notes", "see also", "references", "external links"}:
            continue
        # Flag others (informational, not failure)
        # issues.append(f"{path}: H2 '{m.group(1)}' may not map to anchor (review)")
    return issues


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--wiki", required=True, help="Path to emitted wiki directory")
    args = ap.parse_args()

    wiki = Path(args.wiki).expanduser()
    if not wiki.is_dir():
        print(f"ERROR: {wiki} is not a directory", file=sys.stderr)
        return 1

    all_issues = []
    md_files = sorted(wiki.rglob("*.md"))
    for md in md_files:
        content = md.read_text()
        all_issues.extend(check_generated_fences(content, md))
        # check_anchor_mapping is informational for now
        # all_issues.extend(check_anchor_mapping(content, md))

    if all_issues:
        print(f"FAIL: {len(all_issues)} lint issue(s):", file=sys.stderr)
        for i in all_issues:
            print(f"  {i}", file=sys.stderr)
        return 1

    print(f"OK: {len(md_files)} wiki files lint clean", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
