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

              Claude Code-only keys (argument-hint, disable-model-invocation and
              the rest of CLAUDE_CODE_KEYS) are WARN: they work in Claude Code
              and must be stripped only when packaging for upload. A skill that
              is deliberately not portable declares `metadata.portability:
              "local-only"` (with a reason in `metadata.portability-reason`);
              its ERRORs are then reported as WARN.

  TRIGGER LOSS  With --baseline REF, each skill's quoted trigger phrases are
              compared with the same SKILL.md at git REF. A phrase present at
              REF and absent now is an ERROR. This is the gate for any
              description rewrite: the description is the activation
              mechanism, so shortening it must not silently drop a trigger.
              A SKILL.md absent at REF (new, moved or renamed) is skipped.

Usage:
    python3 audit_mechanical.py <skills-root> [--json] [--threshold 50] [--baseline REF]

Exit status is non-zero when a collision at or above the threshold exists, any
skill has a portability ERROR, or (with --baseline) any trigger was lost, so
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

# Directories that hold other skills rather than being one. `sources` holds
# upstream reference copies (evidence, not deployed skills); counting them
# inflated the 2026-11-10 run from 54 live skills to 94.
SKIP_DIRS = {".git", "staged-for-deletion", "archive", "inactive", "deprecated",
             "node_modules", "sources", ".omc"}

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
# Functional in Claude Code (code.claude.com skills docs, checked 2026-11-10);
# rejected by claude.ai and the Claude API, so strip them when packaging.
CLAUDE_CODE_KEYS = {"argument-hint", "arguments", "disable-model-invocation", "user-invocable",
                    "when_to_use", "disallowed-tools", "model", "effort", "context", "agent",
                    "background", "hooks", "paths", "shell"}
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
RESERVED_NAME_WORDS = ("anthropic", "claude")
MAX_BODY_LINES = 500
MAX_DESC = 1024        # hard limit: Anthropic, agentskills.io, Codex interface
SOFT_DESC = 500        # Codex shortens long descriptions first when its skill
                       # list exceeds its budget; front-load the key use case

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
    if not m:
        return ""
    value = " ".join(m.group(1).split())
    # Strip the YAML scalar's own outer quotes, or a short quoted description
    # would be read as one giant trigger phrase.
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        value = value[1:-1]
    return value


def triggers(desc: str) -> set[str]:
    """Quoted trigger phrases, lowercased.

    Only quoted phrases count. An unquoted description may still activate well,
    but it declares no phrase this check can compare, so it is reported as
    'undeclared' rather than as a collision candidate. Treating prose as
    triggers produced false pairs on common words in early versions.
    """
    # Fold the typographic apostrophe: portable descriptions write "what’s" so
    # the apostrophe cannot close a single-quoted trigger, and the baseline
    # must still recognise it as the same phrase as an older "what's".
    return {(a or b).strip().lower().replace("’", "'") for a, b in QUOTED_RE.findall(desc)}


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
        extra = set(data) - ALLOWED_KEYS
        cc_only = sorted(extra & CLAUDE_CODE_KEYS)
        foreign = sorted(extra - CLAUDE_CODE_KEYS)
        if foreign:
            out.append(f"ERROR: unexpected top-level key(s) {foreign}; claude.ai and the Claude API reject them (move under metadata)")
        if cc_only:
            out.append(f"WARN: Claude Code-only key(s) {cc_only}; keep for Claude Code, strip when packaging for claude.ai or the API")
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
            if len(desc) > MAX_DESC:
                out.append(f"ERROR: description is {len(desc)} chars (max {MAX_DESC})")
            elif len(desc) > SOFT_DESC and not (
                    isinstance(data.get("metadata"), dict)
                    and data["metadata"].get("description-reviewed")):
                # metadata.description-reviewed records a hand review that
                # confirmed the use case leads; the trigger gate still applies.
                out.append(f"WARN: description is {len(desc)} chars (over {SOFT_DESC}: Codex shortens it under budget; key use case must come first)")
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
    meta = (data or {}).get("metadata") if isinstance(data, dict) else None
    if isinstance(meta, dict) and str(meta.get("portability", "")).strip() == "local-only":
        out = [("WARN (local-only): " + f[len("ERROR: "):]) if f.startswith("ERROR") else f for f in out]
    return out


ARCHIVE_SUFFIXES = {".zip", ".skill", ".tar", ".gz", ".tgz"}


def shipped_but_unreferenced(path: Path, skill_text: str) -> list[str]:
    """Inverse of disclosure integrity: files that ship with the skill but
    nothing loads, plus packaged copies of skills inside the skill.

    A file counts as reachable when SKILL.md names it (by relative path or
    basename) or when a reachable text file names it, transitively.
    Measured case (2026-11-10): spec-prep shipped 3 of 29 reference files
    that nothing referenced (an entire second skill, a research paper and a
    Reddit draft), plus an 84 KB packaged zip and a nested full copy.
    """
    out: list[str] = []
    every = [p for d in DISCLOSURE_DIRS if (path / d).is_dir()
             for p in (path / d).rglob("*") if p.is_file()]
    junk = [p for p in every if "__pycache__" in p.parts or ".omc" in p.parts
            or p.suffix in (".pyc", ".pyo") or p.name == ".DS_Store"]
    files = [p for p in every if p not in junk]
    import_re = re.compile(r"^\s*(?:from\s+\.?([\w.]+)\s+import|import\s+([\w.]+))", re.M)
    reachable: set[Path] = set()
    frontier = [skill_text]
    while frontier:
        text = frontier.pop()
        modules = {part for a, b in import_re.findall(text) for part in (a or b).split(".")}
        for p in files:
            if p in reachable:
                continue
            rel = p.relative_to(path).as_posix()
            if rel in text or p.name in text or (p.suffix == ".py" and p.stem in modules):
                reachable.add(p)
                if p.suffix in (".md", ".txt", ".json", ".yaml", ".yml", ".py", ".sh", ".js", ".mjs", ".ts"):
                    frontier.append(p.read_text(encoding="utf-8", errors="replace"))
    # Companion files are consumed by tooling, not named in prose: a package
    # init, a node manifest or a lockfile is live when anything beside it is.
    companions = {"__init__.py", "package.json", "package-lock.json", "requirements.txt",
                  "pyproject.toml", "bun.lockb", "pnpm-lock.yaml"}
    live_dirs = {p.parent for p in reachable}
    reachable |= {p for p in files if p.name in companions and p.parent in live_dirs}
    orphans = sorted(p.relative_to(path).as_posix() for p in files if p not in reachable)
    if orphans:
        out.append(f"WARN: {len(orphans)} shipped file(s) nothing references: {', '.join(orphans[:6])}"
                   + (" ..." if len(orphans) > 6 else ""))
    if junk:
        out.append(f"WARN: {len(junk)} cache or session-state file(s) ship with the skill "
                   f"(__pycache__, .omc, .pyc); exclude them")
    archives = sorted(p.name for p in path.iterdir()
                      if p.is_file() and p.suffix.lower() in ARCHIVE_SUFFIXES)
    if archives:
        out.append(f"WARN: packaged archive(s) inside the skill: {', '.join(archives)} (build packages outside the skill folder)")
    nested_skills = sorted(p.parent.relative_to(path).as_posix() for p in path.rglob("SKILL.md")
                           if p.parent != path and not any(s in p.parts for s in SKIP_DIRS))
    if nested_skills:
        out.append(f"WARN: nested skill copy inside the skill: {', '.join(nested_skills)}")
    return out


def baseline_triggers(root: Path, rel_skill_md: str, ref: str) -> set[str] | None:
    """Quoted triggers of a SKILL.md at git REF, or None when absent there."""
    import subprocess
    top = subprocess.run(["git", "-C", str(root), "rev-parse", "--show-toplevel"],
                         capture_output=True, text=True)
    if top.returncode != 0:
        return None
    repo = Path(top.stdout.strip())
    path_in_repo = (root / rel_skill_md).resolve().relative_to(repo.resolve()).as_posix()
    shown = subprocess.run(["git", "-C", str(repo), "show", f"{ref}:{path_in_repo}"],
                           capture_output=True, text=True)
    if shown.returncode != 0:
        return None
    return triggers(description(shown.stdout.replace("\r\n", "\n")))


def audit(root: Path, threshold: int, baseline: str | None = None) -> dict:
    skills: dict[str, dict] = {}
    lost: dict[str, list[str]] = {}
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
            "unreferenced": shipped_but_unreferenced(path, text),
        }
        if baseline:
            rel = str((path / "SKILL.md").relative_to(root))
            before = baseline_triggers(root, rel, baseline)
            if before:
                gone = sorted(before - set(skills[str(path.relative_to(root))]["triggers"]))
                if gone:
                    lost[str(path.relative_to(root))] = gone

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
        "baseline": baseline,
        "lost_triggers": lost,
        "unreferenced": {n: s["unreferenced"] for n, s in skills.items() if s["unreferenced"]},
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("root")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--threshold", type=int, default=50)
    ap.add_argument("--baseline", metavar="REF",
                    help="git ref to compare quoted triggers against (lost trigger = ERROR)")
    args = ap.parse_args()

    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        print(f"no such directory: {root}", file=sys.stderr)
        return 2

    result = audit(root, args.threshold, args.baseline)

    failed = bool(result["collisions"] or result["portability_errors"] or result["lost_triggers"])
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

    unref = result["unreferenced"]
    print(f"\n== SHIPPED BUT UNREFERENCED ({len(unref)}) ==")
    if not unref:
        print("  none")
    for n, findings in sorted(unref.items()):
        print(f"  {n}")
        for f in findings:
            print(f"      {f}")

    if args.baseline:
        print(f"\n== TRIGGERS LOST since {args.baseline} ({len(result['lost_triggers'])}) ==")
        if not result["lost_triggers"]:
            print("  none")
        for n, gone in sorted(result["lost_triggers"].items()):
            print(f"  {n}: {', '.join(gone)}")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
