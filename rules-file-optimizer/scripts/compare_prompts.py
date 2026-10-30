#!/usr/bin/env python3
"""Compare a rules file against reference rules files.

Builds a concept coverage matrix: which file addresses which concern, so gaps
and better formulations are visible instead of inferred. Also reports size and
rationale density, because the two most useful signals in the 2026-08-23 survey
were that a shipped frontier agent prompt was 46 lines, and that it carried no
rationale at all.

What to look for in the output, in order of value:

  1. Concepts the target lacks entirely. Highest-value additions.
  2. Concepts present in both, where the reference states it better. A rule can
     be present and badly worded -- "proportional to task complexity" beats a
     fixed line cap, because a constant is violated the moment a task needs more,
     and a routinely violated rule teaches that rules are approximate.
  3. Direct contradictions. Surface as a decision, never silently adopt.
  4. Concepts only the target has. Do NOT compress these away: a locally
     invented rule exists because someone hit a problem the reference authors
     did not, and it will appear in no reference file.

Usage:
    compare_prompts.py <target.md> <reference.md> [...] [--json]

Fetching references:
    curl -sL https://raw.githubusercontent.com/<org>/<repo>/main/AGENTS.md
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Concerns worth checking for. Patterns are deliberately broad: a false positive
# costs one manual check, a false negative hides a gap.
CONCEPTS = {
    "reversibility gates action":
        r"\b(revers|undo|undone|destructive|irreversible|blast radius|hard to reverse)\b",
    "approval does not persist":
        r"\b(blank check|approv\w+ once|every later situation|approval in one context|second confirmation)\b",
    "investigate unexpected state":
        r"\b(unexpected state|unfamiliar (files|branches)|in-progress work|before deleting or overwriting)\b",
    "response length discipline":
        r"\b(proportional to|concise|at most \d+ lines|keep .{0,20}responses?|verbose|"
        r"length that comes from|responses? .{0,15}(short|brief))\b",
    "prescribed reply skeleton":
        r"\b(DONE:|status block|three-line|RUNNING:|BLOCKED:)\b",
    "mid-task steering protocol":
        r"\b(steering|mid-task|interject|replan|re-plan|buffer it)\b",
    "prefer specialised tools over shell":
        r"\b(dedicated file tools|specialized tools|instead of cat|reserve bash|prefer the dedicated)\b",
    "parallelise independent calls":
        r"\b(parallel\w*)\b",
    "nested instruction-file precedence":
        r"\b(AGENTS\.md|CLAUDE\.md|project instruction file|more-deeply-nested|scoping rules)\b",
    "evidence before completion":
        r"\b(never claim completion|evidence|verified|unverified|report outcomes faithfully)\b",
    "scope: do not narrow or widen":
        r"\b(broaden scope|narrow, widen|smallest safe change|scope creep|do not refactor)\b",
    "markdown/output formatting":
        r"\b(markdown|GitHub-flavored|CommonMark|bullet lists|inline code)\b",
    "conditional/templated sections":
        r"(\{%-?\s*if|\$\{\{|\{\{\s*\w+\s*\}\})",
    "self-governing (file maintains itself)":
        r"\b(retire|state each rule once|compliance budget|maintaining this file)\b",
}


def load(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def rationale_density(text: str) -> float:
    """Fraction of sentences that justify rather than instruct.

    A justifying sentence cites a measurement, a date, or an outcome. These are
    the sentences that cost tokens on every session to persuade a reader who has
    already accepted the rule -- and they were the single largest saving
    available in the file this skill was built from.
    """
    sents = [s for s in re.split(r"(?<=[.!?])\s+", text) if len(s.split()) > 4]
    if not sents:
        return 0.0
    marker = re.compile(
        r"\b(measured|because|the reason|this is why|on 20\d\d-\d\d-\d\d|"
        r"\d+ of \d+|resulted in|was written after|evidence)\b", re.I)
    return sum(1 for s in sents if marker.search(s)) / len(sents)


def analyse(path: Path) -> dict:
    text = load(path)
    return {
        "file": path.name,
        "path": str(path),
        "lines": text.count("\n") + 1,
        "chars": len(text),
        "rationale_pct": round(100 * rationale_density(text)),
        "concepts": {
            name: bool(re.search(pat, text, re.I))
            for name, pat in CONCEPTS.items()
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("target")
    ap.add_argument("references", nargs="*")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    paths = [Path(args.target).expanduser()] + [Path(r).expanduser() for r in args.references]
    missing = [p for p in paths if not p.is_file()]
    if missing:
        for p in missing:
            print(f"no such file: {p}", file=sys.stderr)
        return 2

    results = [analyse(p) for p in paths]
    target, refs = results[0], results[1:]

    if args.json:
        print(json.dumps({"target": target, "references": refs}, indent=2))
        return 0

    print("== SIZE AND DENSITY ==")
    widest = max(len(r["file"]) for r in results)
    for r in results:
        tag = "  <-- target" if r is target else ""
        print(f"  {r['file']:<{widest}}  {r['lines']:>5} lines  {r['chars']:>7,} chars  "
              f"rationale {r['rationale_pct']:>2}%{tag}")

    if not refs:
        print("\nNo references given. Pass reference files to build the matrix.")
        return 0

    print("\n== CONCEPT COVERAGE ==")
    header = f"  {'concept':<40}{'target':>8}"
    for r in refs:
        header += f"{r['file'][:11]:>13}"
    print(header)
    gaps, unique = [], []
    for name in CONCEPTS:
        in_target = target["concepts"][name]
        in_refs = [r["concepts"][name] for r in refs]
        row = f"  {name:<40}{'YES' if in_target else '--':>8}"
        for hit in in_refs:
            row += f"{'YES' if hit else '--':>13}"
        print(row)
        if not in_target and any(in_refs):
            gaps.append(name)
        if in_target and not any(in_refs):
            unique.append(name)

    if gaps:
        print("\n== GAPS: in a reference, absent from the target ==")
        print("   Highest-value additions. Check each before dismissing it.")
        for g in gaps:
            print(f"   - {g}")

    if unique:
        print("\n== ONLY IN THE TARGET ==")
        print("   Do not compress these away. They exist because someone hit a")
        print("   problem the reference authors did not.")
        for u in unique:
            print(f"   - {u}")

    lean = min(refs, key=lambda r: r["chars"])
    if target["chars"] > lean["chars"]:
        factor = target["chars"] / max(1, lean["chars"])
        print(f"\nThe target is {factor:.1f}x the size of the leanest reference "
              f"({lean['file']}, {lean['lines']} lines).")
        if target["rationale_pct"] > lean["rationale_pct"] + 5:
            print(f"Rationale density {target['rationale_pct']}% against "
                  f"{lean['rationale_pct']}% — moving justification to a separate "
                  "document is usually the largest single saving available.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
