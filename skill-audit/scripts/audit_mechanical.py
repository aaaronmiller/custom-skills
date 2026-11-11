#!/usr/bin/env python3
"""Mechanical skill-ecosystem checks: collision, disclosure and portability.

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

  PORTABILITY A skill that loads in Claude Code can still be rejected by the
              claude.ai uploader, the Claude API, Codex or Gemini. Claude Code
              parses frontmatter leniently; the others do not. Measured case:
              create-viral-content (issue #2, 2026-06-10) failed claude.ai upload
              with "malformed YAML frontmatter in SKILL.md" for five months
              while working locally, because its description closed a quoted
              string and continued on an indented line, and it carried five
              top-level keys outside the allowed set. Rules are the union of
              anthropics/skills quick_validate.py, gemini-cli validate_skill.cjs
              and the agentskills.io spec, checked 2026-11-10.

Usage:
    python3 audit_mechanical.py <skills-root> [--json] [--threshold 50]

Exit status is non-zero when a collision at or above the threshold exists or
any skill has a portability ERROR, so this can gate a commit.
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
# Double-quoted phrases, or single-quoted ones not touching a letter (so the
# apostrophes in "user's" or "don't" never pair up into a false trigger).
# Single quotes matter: Gemini's validator forbids inner double quotes in a
# double-quoted description, so portable skills quote triggers with ' '.
QUOTED_RE = re.compile(r'"([^"]{3,60})"|(?<![A-Za-z])\'([^\']{3,60})\'(?![A-Za-z])')

# Portability rules (sources in the module docstring).
ALLOWED_KEYS = {"name", "description", "license", "allowed-tools", "metadata", "compatibility"}
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
RESERVED_NAME_WORDS = ("anthropic", "claude")
MAX_BODY_LINES = 500

try:  # PyYAML is optional; without it the YAML parse is reported as unchecked.
    import yaml  # type: ignore
except ImportError:  # pragma: no cover
    yaml = None


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
    return {(a or b).strip().lower() for a, b in QUOTED_RE.findall(desc)}


def portability(path: Path, raw: bytes) -> list[str]:
    """Return 'ERROR: ...' and 'WARN: ...' findings for one skill folder.

    ERROR means at least one target platform rejects the skill outright.
    WARN means a platform degrades it or a convention is broken.
    """
    out: list[str] = []
    if raw.startswith(b"\xef\xbb\xbf"):
        out.append("ERROR: UTF-8 BOM before the opening ---")
        raw = raw[3:]
    text = raw.decode("utf-8", errors="replace")
    if "\r\n" in text:
        out.append("WARN: CRLF line endings in SKILL.md (use LF)")
        text = text.replace("\r\n", "\n")
    m = re.match(r"^---\n(.*?)\n---[ \t]*\n", text, re.S)
    if not m:
        return out + ["ERROR: frontmatter must open with --- on line 1 and close with --- on its own line"]
    fm_text = m.group(1)
    body_lines = text[m.end():].count("\n")

    data = None
    if yaml is None:
        out.append("WARN: PyYAML not installed; YAML parse unchecked")
    else:
        try:
            data = yaml.safe_load(fm_text)
        except yaml.YAMLError as e:
            first = str(e).splitlines()[0]
            return out + [f"ERROR: invalid YAML in frontmatter ({first}); claude.ai reports 'malformed YAML frontmatter in SKILL.md'"]
        if not isinstance(data, dict):
            return out + ["ERROR: frontmatter is not a YAML mapping"]

    if data is not None:
        extra = sorted(set(data) - ALLOWED_KEYS)
        if extra:
            out.append(f"ERROR: unexpected top-level key(s) {extra}; claude.ai and the Claude API reject them (move under metadata)")
        name = data.get("name")
        if not isinstance(name, str) or not NAME_RE.match(name) or len(name) > 64:
            out.append(f"ERROR: name {name!r} must be kebab-case, 1-64 chars")
        else:
            if name != path.name:
                out.append(f"WARN: name {name!r} differs from folder {path.name!r} (agentskills spec, opencode)")
            if any(w in name for w in RESERVED_NAME_WORDS):
                out.append(f"ERROR: name {name!r} contains a reserved word (anthropic, claude)")
        desc = data.get("description")
        if not isinstance(desc, str) or not desc.strip():
            out.append("ERROR: description missing or not a string")
        else:
            if len(desc) > 1024:
                out.append(f"ERROR: description is {len(desc)} chars (max 1024)")
            if "<" in desc or ">" in desc:
                out.append("ERROR: description contains < or > (claude.ai rejects XML-like text)")
        meta = data.get("metadata")
        if meta is not None and (not isinstance(meta, dict)
                                 or any(not isinstance(v, str) for v in meta.values())):
            out.append("WARN: metadata should map string keys to string values (quote numbers)")
        comp = data.get("compatibility")
        if isinstance(comp, str) and len(comp) > 500:
            out.append("ERROR: compatibility longer than 500 chars")

    # Gemini's validator reads the description line with a regex, not YAML:
    # it must be one physical line, and a double-quoted value may not contain ".
    line = re.search(r'^description:[ \t]*(.*)$', fm_text, re.M)
    if not line or not line.group(1).strip() or line.group(1).strip()[0] in "|>":
        out.append("WARN: description is not a single-line string (Gemini CLI validator rejects block scalars)")
    else:
        v = line.group(1).strip()
        if v.startswith('"') and '"' in v[1:-1]:
            out.append('WARN: double-quoted description contains inner " (Gemini parser truncates it); quote triggers with single quotes')

    if body_lines > MAX_BODY_LINES:
        out.append(f"WARN: body is {body_lines} lines (keep under {MAX_BODY_LINES})")
    nested = [p for p in path.rglob("*") if p.name.lower() == "skill.md"
              and p.parent != path and not any(s in p.parts for s in SKIP_DIRS)]
    if nested:
        out.append(f"WARN: {len(nested)} nested SKILL.md file(s); the OpenAI API rejects the bundle and opencode registers each as a skill")
    return out


def audit(root: Path, threshold: int) -> dict:
    skills: dict[str, dict] = {}
    for path in find_skills(root):
        raw = (path / "SKILL.md").read_bytes()
        text = raw.decode("utf-8", errors="replace").replace("\r\n", "\n")
        declared = {m.group(1) for m in DISCLOSURE_RE.finditer(text)}
        missing = sorted(r for r in declared if not (path / r).exists())
        skills[str(path.relative_to(root))] = {
            "triggers": sorted(triggers(description(text))),
            "declared_refs": len(declared),
            "missing_refs": missing,
            "portability": portability(path, raw),
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
        "portability": {n: s["portability"] for n, s in skills.items() if s["portability"]},
        "portability_errors": sorted(
            n for n, s in skills.items() if any(f.startswith("ERROR") for f in s["portability"])
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

    failed = bool(result["collisions"] or result["portability_errors"])
    if args.json:
        print(json.dumps(result, indent=2))
        return 1 if failed else 0

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

    port = result["portability"]
    print(f"\n== PORTABILITY ({len(result['portability_errors'])} with errors, "
          f"{len(port)} with findings) ==")
    if not port:
        print("  none")
    for n, findings in sorted(port.items()):
        print(f"  {n}")
        for f in findings:
            print(f"      {f}")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
