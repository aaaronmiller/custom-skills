#!/usr/bin/env python3
"""Mechanical skill-ecosystem checks: trigger collision and disclosure integrity.

The rest of this skill is judgement work - is a description good, is a skill
junk, does it earn its slot. These two checks are not judgement. They are
arithmetic over the corpus, they are the two that found every real defect in
the 2026-08-22 audit of ~/code/custom-skills, and neither is reliable done by
eye.

  COLLISION   Two skills that quote the same trigger phrases compete for the
              same activation. Which one loads is arbitrary. Measured on that
              corpus: `deprecated/strata` and `strata-authoring` shared 100% of
              their quoted triggers, and three separate skills opened with the
              identical sentence "ALWAYS invoke when the user wants to start a
              new project". Name similarity found none of this - two of those
              three had unrelated names - and two skills with near-identical
              names turned out to be a pipeline split rather than a duplicate.
              Only the trigger sets show it.

              The inverse matters as much: a skill quoting NO trigger phrases
              cannot activate on intent at all. It is a resource in everything
              but filing. `backtranslation-spec-auditor` sat in that state.

  DISCLOSURE  A skill whose references/, scripts/ or assets/ targets are absent
              is inert no matter how good its prose is. On that same corpus 21
              of 39 skills had every single target missing, silently, because a
              script had emptied the directories five weeks earlier. The
              SKILL.md files were untouched, so nothing looked wrong.

Usage:
    python3 audit_mechanical.py <skills-root> [--json] [--threshold 50]

Exit status is non-zero when a collision at or above the threshold exists, so
this can gate a commit.
"""

from __future__ import annotations

import argparse
import itertools
import json
import os
import re
import sys
from pathlib import Path

# Directories that hold other skills rather than being one.
SKIP_DIRS = {".git", "staged-for-deletion", "archive", "inactive", "deprecated", "node_modules"}

# Progressive-disclosure roots, by convention across every skill format seen.
DISCLOSURE_DIRS = ("references", "reference", "scripts", "assets", "templates", "data", "bin")

DISCLOSURE_RE = re.compile(
    r"`?((?:" + "|".join(DISCLOSURE_DIRS) + r")/[A-Za-z0-9_./-]+\.[A-Za-z]{2,6})`?"
)
QUOTED_RE = re.compile(r'"([^"]{3,60})"')


def find_skills(root: Path) -> list[Path]:
    """Every directory holding a SKILL.md, not descending into one."""
    out: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        if "SKILL.md" in filenames:
            out.append(Path(dirpath))
            dirnames[:] = []  # a skill does not contain another skill
    return sorted(out)


def frontmatter(text: str) -> str:
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    return m.group(1) if m else ""


def description(text: str) -> str:
    fm = frontmatter(text)
    m = re.search(r"^description:\s*(.+?)(?=\n[a-zA-Z_-]+:|\Z)", fm, re.S | re.M)
    return " ".join(m.group(1).split()) if m else ""


def triggers(desc: str) -> set[str]:
    """Quoted trigger phrases, lowercased.

    Only quoted phrases count. An unquoted description may still activate well,
    but it declares no phrase this check can compare, so it is reported as
    'undeclared' rather than as a collision candidate. Treating prose as
    triggers produced false pairs on common words in early versions.
    """
    return {q.strip().strip("'\"").lower() for q in QUOTED_RE.findall(desc)}


def audit(root: Path, threshold: int) -> dict:
    skills: dict[str, dict] = {}
    for path in find_skills(root):
        text = (path / "SKILL.md").read_text(encoding="utf-8", errors="replace")
        declared = {m.group(1) for m in DISCLOSURE_RE.finditer(text)}
        missing = sorted(r for r in declared if not (path / r).exists())
        skills[str(path.relative_to(root))] = {
            "triggers": sorted(triggers(description(text))),
            "declared_refs": len(declared),
            "missing_refs": missing,
        }

    collisions = []
    names = sorted(skills)
    for a, b in itertools.combinations(names, 2):
        ta, tb = set(skills[a]["triggers"]), set(skills[b]["triggers"])
        if not ta or not tb:
            continue
        shared = ta & tb
        if not shared:
            continue
        pct = 100 * len(shared) // min(len(ta), len(tb))
        if pct >= threshold:
            collisions.append(
                {"a": a, "b": b, "shared": sorted(shared), "overlap_pct": pct}
            )
    collisions.sort(key=lambda c: -c["overlap_pct"])

    return {
        "root": str(root),
        "skill_count": len(skills),
        "collisions": collisions,
        "undeclared_triggers": sorted(n for n in skills if not skills[n]["triggers"]),
        "broken_disclosure": {
            n: s["missing_refs"] for n, s in skills.items() if s["missing_refs"]
        },
        "fully_broken": sorted(
            n for n, s in skills.items()
            if s["declared_refs"] and len(s["missing_refs"]) == s["declared_refs"]
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("root")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--threshold", type=int, default=50)
    args = ap.parse_args()

    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        print(f"no such directory: {root}", file=sys.stderr)
        return 2

    result = audit(root, args.threshold)

    if args.json:
        print(json.dumps(result, indent=2))
        return 1 if result["collisions"] else 0

    print(f"{result['skill_count']} skills under {result['root']}\n")

    print(f"== TRIGGER COLLISIONS at or above {args.threshold}% ==")
    if not result["collisions"]:
        print("  none")
    for c in result["collisions"]:
        print(f"  {c['overlap_pct']:3d}%  {c['a']}  x  {c['b']}")
        print(f"        shared: {', '.join(c['shared'][:8])}")

    print(f"\n== NO DECLARED TRIGGERS ({len(result['undeclared_triggers'])}) ==")
    print("  These cannot be compared, and may not activate on intent at all.")
    for n in result["undeclared_triggers"]:
        print(f"    {n}")

    print(f"\n== BROKEN PROGRESSIVE DISCLOSURE ({len(result['broken_disclosure'])}) ==")
    if not result["broken_disclosure"]:
        print("  none")
    for n, missing in sorted(result["broken_disclosure"].items()):
        flag = "  [FULLY BROKEN]" if n in result["fully_broken"] else ""
        print(f"  {n}: {len(missing)} missing{flag}")
        for m in missing[:4]:
            print(f"      {m}")

    return 1 if result["collisions"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
