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

              A skill quoting NO trigger phrases is listed as undeclared: it
              may still activate from its prose, but trigger collisions cannot
              be checked for it.

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
import shutil
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
    # Not preceded by a path character: "/x/public/data/a.json" and
    # "~/.claude/skills/gstack/scripts/y.json" belong to other trees.
    r"`?(?<![/\w~.-])((?:" + "|".join(DISCLOSURE_DIRS) + r")/[A-Za-z0-9_./-]+\.[A-Za-z0-9]{1,6})(?![A-Za-z0-9])`?"
)
# Output-path patterns ("data/reports/YYYY-MM-DD-x.md") name files a run will
# create, not files the skill ships; they are not broken references.
PLACEHOLDER_RE = re.compile(r"YYYY|MM-DD|XXXX|\{\{|<[^>]+>|\*")
# Prefixes that mean "this skill's folder": "${CLAUDE_SKILL_DIR}/scripts/x.py",
# "$SKILL_ROOT/scripts/x.py" and "./scripts/x.py" all name scripts/x.py.
SKILL_VARS = {"CLAUDE_SKILL_DIR", "SKILL_ROOT", "SKILL_DIR"}
SKILL_PREFIX_RE = re.compile(r"\$\{?(?:" + "|".join(SKILL_VARS) + r")\}?/|(?<![\w/.~$-])\./")
# A path rooted in another tree (a Windows drive, a WSL mount, a home
# directory). Relative paths that follow one on the same line belong to that
# tree: system-checkup/SKILL.md names data/annotations.json inside
# C:\Users\...\downloads-desktop-cleanup.livingdoc, not inside the skill.
FOREIGN_ROOT_RE = re.compile(r"(?<![\w])(?:[A-Za-z]:[\\/]|/mnt/|~/|\$HOME/|/home/|/Users/)")
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


def has_skill_frontmatter(t: str) -> bool:
    """True when a file opens with frontmatter holding both name: and description:."""
    t = t.lstrip("﻿").replace("\r\n", "\n")
    if not t.startswith("---\n"):
        return False
    end = t.find("\n---", 4)
    head = t[4:end] if end != -1 else ""
    return bool(re.search(r"^name:", head, re.M) and re.search(r"^description:", head, re.M))


def own_lines(text: str):
    """Yield each line cut at the first path rooted in another tree, with the
    skill-folder prefixes (${CLAUDE_SKILL_DIR}/, $SKILL_ROOT/, ./) removed so a
    prefixed path reads as the skill-relative path it names."""
    for line in text.splitlines():
        line = SKILL_PREFIX_RE.sub(" ", line)
        m = FOREIGN_ROOT_RE.search(line)
        yield line[:m.start()] if m else line


def unfenced(text: str) -> str:
    """The text with fenced code blocks blanked (line count kept). A heading or
    link inside a fence is template text, not part of the document."""
    out, fence = [], None
    for line in text.splitlines():
        m = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
        if fence is None and m:
            fence = m.group(1)[0] * len(m.group(1))
            out.append("")
        elif fence is not None:
            if line.strip().startswith(fence) and not line.strip().strip(fence[0]).strip():
                fence = None
            out.append("")
        else:
            out.append(line)
    return "\n".join(out)


# A word that tells the agent to run or load a file. "sh" and "py" never match
# inside a file name ("install.sh"): the cue may not follow a dot or slash.
RUN_CUE_RE = re.compile(r"(?<![\w./-])(run|execute|invoke|call|python3?|bash|sh|node|bun|uv run|pwsh)\b", re.I)
LOAD_CUE_RE = re.compile(r"(?<![\w./-])(see|read|load|open|follow|consult)\b", re.I)
# Lines that quote an example rather than give an instruction.
ILLUSTRATION_RE = re.compile(r"\bsays?:|\be\.g\.|\bfor example\b|\bexample:", re.I)
# Fences holding a file tree, a template or sample prose, not commands.
EXAMPLE_FENCE_RE = re.compile(r"^ {0,3}(?:`{3,}|~{3,})\s*(?:text|txt|tree|plain|plaintext|markdown|md)\s*$", re.I)


def reference_lines(text: str):
    """Lines of a references/ file that can claim the skill ships a file.

    A references file often describes files in the user's project or files a
    run will create ("Create one script per operation: scripts/get_item.py").
    Only a line that tells the agent to run or load something counts, and
    example fences and quoted illustrations are skipped.
    """
    in_example, fence = False, None
    for line in text.splitlines():
        m = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
        if m and fence is None:
            fence, in_example = m.group(1)[0], bool(EXAMPLE_FENCE_RE.match(line))
            continue
        if m and fence and m.group(1)[0] == fence and not line.strip().strip(fence):
            fence, in_example = None, False
            continue
        if in_example or ILLUSTRATION_RE.search(line):
            continue
        if RUN_CUE_RE.search(line) or LOAD_CUE_RE.search(line):
            yield line


def declared_refs(path: Path, skill_text: str, skill_names: frozenset = frozenset()) -> dict[str, list[str]]:
    """Disclosure targets named in SKILL.md and references/**/*.md, mapped to
    the files that name them when missing (empty list when present).

    SKILL_NAMES are the other skills in the corpus: a path right after one
    ("the humanize-writing skill's references/x.md") belongs to that skill.
    """
    sources = [("SKILL.md", list(own_lines(skill_text)), path)]
    ref_dir = path / "references"
    if ref_dir.is_dir():
        for p in sorted(ref_dir.rglob("*.md")):
            if p.is_file() and not any(s in p.relative_to(path).parts for s in SKIP_DIRS):
                t = p.read_text(encoding="utf-8", errors="replace")
                sources.append((p.relative_to(path).as_posix(),
                                list(own_lines("\n".join(reference_lines(t)))), p.parent))
    siblings = sorted(skill_names - {path.name}, key=len, reverse=True)
    sibling_re = re.compile(r"(?<![\w-])(?:" + "|".join(map(re.escape, siblings)) + r")\W{0,6}$") if siblings else None
    named_skill_re = re.compile(r"(?<![\w-])([\w-]+)\**\s+skill'?s?\W{0,6}$", re.I)

    def other_skill(before: str) -> bool:
        m = named_skill_re.search(before)
        if m and m.group(1).lower() not in {"this", "the", "that", "each", "every", "a", "own", "same", "your", path.name}:
            return True
        return bool(sibling_re and sibling_re.search(before))

    out: dict[str, list[str]] = {}
    for rel, lines, base in sources:
        for line in lines:
            for m in DISCLOSURE_RE.finditer(line):
                ref = m.group(1)
                if PLACEHOLDER_RE.search(ref) or other_skill(line[:m.start()]):
                    continue
                # A reference file may name a sibling relative to itself.
                if (path / ref).exists() or (base / ref).exists():
                    out.setdefault(ref, [])
                else:
                    out.setdefault(ref, []).append(rel)
    return out


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
BACKUP_RE = re.compile(r"\.(?:bak|orig|old)$|~$", re.I)
TEXT_SUFFIXES = {".md", ".txt", ".json", ".yaml", ".yml", ".toml", ".py", ".sh", ".js", ".mjs",
                 ".cjs", ".ts", ".ps1", ".html"}
# Files a skill legitimately ships without naming them in prose.
COMPANIONS = {"readme.md", "changelog.md", "marketplace.json", "package.json",
              "requirements.txt", "pyproject.toml"}
LIVE_DIR_COMPANIONS = {"__init__.py", "package-lock.json", "bun.lockb", "pnpm-lock.yaml"}


COMPANIONS |= {
    "skill.md.tmpl",      # source template a build step renders into SKILL.md
    ".provenance.yaml",   # provenance record of where the skill came from
    ".provenance.json",   # the same record in JSON
}
COMPANION_DIRS = {
    "tests",  # test suites run by a test runner, not loaded by the agent
    "evals",  # eval sets run by skill-creator style harnesses
}


def is_companion(p: Path, root: Path | None = None) -> bool:
    n = p.name.lower()
    if root is not None and p.relative_to(root).parts[0] in COMPANION_DIRS:
        return True
    return n in COMPANIONS or n.startswith(("license", "licence"))


IMPORT_RE = re.compile(r"^\s*(?:from\s+\.?([\w.]+)\s+import|import\s+([\w.]+))", re.M)


def reach(path: Path, skill_text: str, files: list[Path]) -> tuple[set[Path], set[Path]]:
    """Files reachable from SKILL.md, and the subset referenced by path.

    A file is reachable when SKILL.md or a reachable text file names it by
    relative path or basename, or imports it as a Python module. It is
    referenced by path when the naming text holds its path relative to the
    skill root or to the naming file's folder.
    """
    reachable: set[Path] = set()
    by_path: set[Path] = set()
    frontier = [(skill_text, path)]
    while frontier:
        text, base = frontier.pop()
        modules = {part for a, b in IMPORT_RE.findall(text) for part in (a or b).split(".")}
        for p in files:
            rel = p.relative_to(path).as_posix()
            try:
                rel_here = p.relative_to(base).as_posix()
            except ValueError:
                rel_here = rel
            if ("/" in rel and rel in text) or ("/" in rel_here and rel_here in text):
                by_path.add(p)
            if p in reachable:
                continue
            if rel in text or p.name in text or (p.suffix == ".py" and p.stem in modules):
                reachable.add(p)
                if p.suffix in TEXT_SUFFIXES:
                    frontier.append((p.read_text(encoding="utf-8", errors="replace"), p.parent))
    return reachable, by_path


def skill_files(path: Path) -> list[Path]:
    return [p for p in path.rglob("*") if p.is_file() and p != path / "SKILL.md"
            and not any(s in p.relative_to(path).parts for s in SKIP_DIRS)]


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
    # The whole folder ships, so the whole folder is scanned: a SKILL.md.bak at
    # the root sat unflagged in skill-audit itself while only DISCLOSURE_DIRS
    # were walked (independent validation, 2026-11-10).
    every = skill_files(path)
    junk = [p for p in every if {"__pycache__", ".omc", ".pytest_cache", ".mypy_cache", ".ruff_cache"} & set(p.parts)
            or p.suffix in (".pyc", ".pyo") or p.name == ".DS_Store"]
    backups = [p for p in every if p not in junk and BACKUP_RE.search(p.name)]
    root_archives = {p for p in every if p.parent == path and p.suffix.lower() in ARCHIVE_SUFFIXES}
    files = [p for p in every if p not in junk and p not in backups and p not in root_archives
             and not is_companion(p, path)]
    reachable, by_path = reach(path, skill_text, files)
    # Lockfiles and package inits are consumed by tooling, not named in prose:
    # each is live when anything beside it is.
    live_dirs = {p.parent for p in reachable} | {path}
    reachable |= {p for p in files if p.name in LIVE_DIR_COMPANIONS and p.parent in live_dirs}
    orphans = sorted(p.relative_to(path).as_posix() for p in files if p not in reachable)
    if orphans:
        out.append(f"WARN: {len(orphans)} shipped file(s) nothing references: {', '.join(orphans[:6])}"
                   + (" ..." if len(orphans) > 6 else ""))
    if backups:
        names = sorted(p.relative_to(path).as_posix() for p in backups)
        out.append(f"WARN: {len(names)} stray backup file(s) ship with the skill: {', '.join(names[:6])}"
                   " (move them out of the skill folder)")
    # A second skill definition anywhere but references/ (references/ files
    # are covered by the hidden-skill check in effectiveness()). Companions
    # are exempt, and so is a non-backup file SKILL.md (or a file it reaches)
    # names by path: skill-doctor loads `$SKILL_ROOT/scorers/efficiency.md`,
    # an upstream rubric whose name/description keys are its own (b4886c1).
    shadow = []
    for p in every:
        rel = p.relative_to(path)
        if p.name == "SKILL.md" or p in junk or is_companion(p, path) or rel.parts[0] == "references" \
                or (p in by_path and p not in backups):
            continue
        try:
            with p.open("rb") as fh:
                head = fh.read(4096).decode("utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if has_skill_frontmatter(head):
            shadow.append(rel.as_posix())
    if shadow:
        out.append(f"WARN: {len(shadow)} file(s) other than SKILL.md carry skill frontmatter "
                   f"(name + description): {', '.join(sorted(shadow)[:6])}")
    if junk:
        out.append(f"WARN: {len(junk)} cache or session-state file(s) ship with the skill "
                   f"(__pycache__, .omc, .pyc); exclude them")
    archives = sorted(p.name for p in root_archives)
    if archives:
        out.append(f"WARN: packaged archive(s) inside the skill: {', '.join(archives)} (build packages outside the skill folder)")
    nested_skills = sorted(p.parent.relative_to(path).as_posix() for p in path.rglob("SKILL.md")
                           if p.parent != path and not any(s in p.parts for s in SKIP_DIRS))
    if nested_skills:
        out.append(f"WARN: nested skill copy inside the skill: {', '.join(nested_skills)}")
    return out


_WHICH: dict[str, bool] = {}
# Search only Linux-side PATH entries: under WSL, /mnt/<drive> entries are
# Windows directories over a slow mount and made each lookup take seconds.
_LOCAL_PATH = os.pathsep.join(d for d in os.environ.get("PATH", "").split(os.pathsep)
                              if d and not d.startswith("/mnt/"))


def on_path(tool: str) -> bool:
    if tool not in _WHICH:
        _WHICH[tool] = shutil.which(tool, path=_LOCAL_PATH) is not None
    return _WHICH[tool]


def gh_slug(heading: str) -> str:
    return re.sub(r"[^\w\- ]", "", heading.strip().lower()).replace(" ", "-")


MAX_SKILL_BYTES = 25_000


def kb(size: int) -> str:
    """Decimal KB with one decimal plus the exact count: 25,164 B is 25.2 KB,
    never a floor-divided "24 KB" that reads like a pass."""
    return f"{size / 1000:.1f} KB ({size:,} B)"


# Credential shapes. Anything containing EXAMPLE (AWS documents
# AKIAIOSFODNN7EXAMPLE) or an obvious placeholder word is documentation.
SECRET_RE = re.compile(
    r"sk-ant-[A-Za-z0-9_-]{20,}|sk-proj-[A-Za-z0-9_-]{20,}|sk-[A-Za-z0-9]{20,}"
    r"|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}"
    r"|xox[bp]-[A-Za-z0-9-]{10,}|AIza[0-9A-Za-z_-]{35}|AKIA[0-9A-Z]{16}")
PLACEHOLDER_TOKEN_RE = re.compile(r"example|your|placeholder|redacted|dummy|xxxx", re.I)
SECRET_SUFFIXES = {".md", ".txt", ".json", ".yaml", ".yml", ".toml", ".py", ".sh", ".js", ".ts", ".env"}


def is_secret_scanned(p: Path) -> bool:
    n = p.name.lower()
    return p.suffix.lower() in SECRET_SUFFIXES or n == ".env" or n.startswith(".env.")


# Files that live in the user's project, not in the skill: a framework entry
# point ("python manage.py migrate", "node server.js") or any bare name on a
# line that places it in "your project", "the repo" or the user's code. Such a
# name is an instruction about someone else's tree, so it is never a ghost.
PROJECT_ENTRYPOINTS = {"manage.py", "setup.py", "app.py", "main.py", "wsgi.py", "asgi.py",
                       "conftest.py", "server.js", "server.ts", "index.js", "index.ts", "app.js",
                       "app.ts", "main.js", "main.ts", "gulpfile.js", "webpack.config.js",
                       "vite.config.js", "vite.config.ts", "next.config.js", "jest.config.js"}
PROJECT_CUE_RE = re.compile(
    r"\b(?:your|the user'?s|their)\s+(?:own\s+)?(?:project|repo|repository|app|application|codebase|code)\b"
    r"|\bthe\s+(?:repo|repository|project|codebase)\b", re.I)


def ghost_tool(path: Path, src: Path, tok: str, line: str, text: str, names: set[str]) -> str | None:
    """Return the name to report when TOK is a tool the skill runs but does
    not ship, else None. Skill-root prefixes and disclosure paths resolve
    against the skill folder; other variables and other trees are skipped."""
    m = re.match(r"\$\{?(\w+)\}?/", tok)
    strict = False
    if m:
        if m.group(1) not in SKILL_VARS:
            return None  # $CK/scripts/x.py: a variable naming another tree
        rel, strict = tok[m.end():], True
    elif tok.startswith("./"):
        rel = tok[2:]
    else:
        rel = tok
    if "/" in rel or strict:
        if "/" in rel and rel.split("/")[0] not in DISCLOSURE_DIRS:
            return None  # src/server.js: a path in the user's tree
        if PLACEHOLDER_RE.search(rel) or (path / rel).exists() or (src.parent / rel).exists():
            return None
        return rel
    tok = rel
    if tok in names or on_path(tok):
        return None
    if (tok.endswith(".js") and tok[0].isupper()) \
            or f"//{tok}" in text or f"{tok}/" in text \
            or re.match(r"(your|my|example|sample|foo|bar)[_-]|script\.py$", tok, re.I):
        return None  # product name (Node.js), site (crt.sh), or placeholder
    if tok.lower() in PROJECT_ENTRYPOINTS or PROJECT_CUE_RE.search(line):
        return None
    return tok


def effectiveness(path: Path, skill_text: str) -> list[str]:
    """Defects that leave a skill valid but less effective. Each check comes
    from the 2026-11-10 spec-prep review, where every one fired.

    ERROR: shipped private data. WARN: everything else.
    """
    out: list[str] = []
    texts = {p: p.read_text(encoding="utf-8", errors="replace")
             for p in path.rglob("*.md")
             if p.is_file() and not any(s in p.relative_to(path).parts for s in SKIP_DIRS)}
    texts[path / "SKILL.md"] = skill_text

    # 1. Dead links and anchors. A file#anchor target resolves relative to the
    # file that holds it (or, by convention, to the skill root); (#anchor)
    # resolves within the same file. Fenced code is template text: neither
    # its headings nor its links count.
    heads: dict[Path, set[str]] = {}

    def anchors(p: Path) -> set[str]:
        key = p.resolve()
        if key not in heads:
            t = unfenced(texts.get(p) or p.read_text(encoding="utf-8", errors="replace"))
            seen: dict[str, int] = {}
            found = set(re.findall(r"""(?:id|name)=["']([\w-]+)["']|\{#([\w-]+)\}""", t))
            slugs = {a or b for a, b in found}
            for h in re.findall(r"^#{1,6}\s+(.+?)\s*#*\s*$", t, re.M):
                s = gh_slug(h)
                slugs.add(s if s not in seen else f"{s}-{seen[s]}")
                seen[s] = seen.get(s, 0) + 1
            heads[key] = slugs
        return heads[key]

    dead = set()
    file_anchor = re.compile(r"(?<![\w/~:$\\-])([\w.-]+(?:/[\w.-]+)*\.md)#([\w-]+)")
    md_names = {q.name for q in texts}
    for p, t in texts.items():
        rel = p.relative_to(path).as_posix()
        for line in own_lines(unfenced(t)):
            for target, anchor in file_anchor.findall(line):
                cands = [c for c in (p.parent / target, path / target) if c.is_file()]
                if not cands:
                    # A bare file name found nowhere in the skill names a
                    # generated or user document ("intent.md#prior-art" in
                    # spec-prep), not a shipped file. Targets with a
                    # directory part are still checked.
                    if "/" in target or target in md_names:
                        dead.add(f"{target} (missing file)")
                elif not any(anchor in anchors(c) for c in cands):
                    dead.add(f"{target}#{anchor}")
            for anchor in re.findall(r"\]\(#([\w-]+)\)", line):
                if anchor not in anchors(p):
                    dead.add(f"{rel}#{anchor}")
    if dead:
        out.append(f"WARN: {len(dead)} dead link(s) or anchor(s): {', '.join(sorted(dead)[:5])}")

    # 2. Ghost tools: scripts a skill tells the agent to run that do not exist.
    walk = [p for p in path.rglob("*") if not any(s in p.relative_to(path).parts for s in SKIP_DIRS)]
    names = {p.name for p in walk if p.is_file()}
    ghosts = set()
    # Only lines that tell the agent to run something count; naming a file as
    # a source or describing a check is not an instruction to execute it.
    run_cue = RUN_CUE_RE
    tool_re = re.compile(r"(?<![\w/.~$\\-])((?:\$\{?\w+\}?/|\./)?(?:[\w.-]+/)*[\w-]+\.(?:py|sh|mjs|cjs|js|ts|ps1))\b")
    for p, t in texts.items():
        for raw_line in t.splitlines():
            if not run_cue.search(raw_line):
                continue
            cut = FOREIGN_ROOT_RE.search(raw_line)
            line = raw_line[:cut.start()] if cut else raw_line
            for tok in tool_re.findall(line):
                ghost = ghost_tool(path, p, tok, line, t, names)
                if ghost:
                    ghosts.add(ghost)
            for phrase in ("the listed tool", "bundled helper"):
                if phrase in line and f'"{phrase}"' not in line:
                    ghosts.add(f"'{phrase}'")
    if ghosts:
        out.append(f"WARN: {len(ghosts)} tool(s) named but not shipped or on PATH: {', '.join(sorted(ghosts)[:6])}")

    # 3. A second skill hiding in references/ (frontmatter with name+description).
    # Files elsewhere are reported by shipped_but_unreferenced().
    # A file SKILL.md (or a file it reaches) loads by path is a rubric or
    # protocol it uses on purpose, not a hidden skill.
    _, by_path = reach(path, skill_text, [p for p in texts if p.name != "SKILL.md"])
    nested = [p.relative_to(path).as_posix() for p, t in texts.items()
              if p.name != "SKILL.md" and p.relative_to(path).parts[0] == "references"
              and p not in by_path and has_skill_frontmatter(t)]
    if nested:
        out.append(f"WARN: file(s) carrying a whole skill definition: {', '.join(nested[:4])}")

    # 4. Private data in a redistributable skill, in every text file it ships.
    private = set()
    for p in walk:
        if not p.is_file() or not is_secret_scanned(p):
            continue
        try:
            if p.stat().st_size > 2_000_000:
                continue
            t = texts.get(p) or p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        rel = p.relative_to(path).as_posix()
        if re.search(r"claude\.ai/chat/[0-9a-f-]{8,}", t):
            private.add(f"{rel}: claude.ai chat URL")
        if any(not PLACEHOLDER_TOKEN_RE.search(m.group(0)) for m in SECRET_RE.finditer(t)):
            private.add(f"{rel}: credential-shaped token")
    if private:
        out.append(f"ERROR: private data shipped: {', '.join(sorted(private))}")

    # 5. Changelog and history inside SKILL.md (it belongs in CHANGELOG or git).
    # A heading that IS a changelog ("## Changes in 3.1.0"), not a concept
    # heading that merely starts with the word ("## History versus changelog").
    if re.search(r"^#{1,3} (Changes|Changelog|History|Release notes|What's new)"
                 r"(\s+(in|for|since)\s+v?[\d.]+)?\s*$", skill_text, re.M | re.I):
        out.append("WARN: changelog section inside SKILL.md (move to CHANGELOG.md or git history)")

    # 6. Always-read budget, in bytes, and megalines that defeat line limits.
    size = len(skill_text.encode("utf-8"))
    if size > MAX_SKILL_BYTES:
        out.append(f"WARN: SKILL.md is {kb(size)} (always read; keep under {kb(MAX_SKILL_BYTES)})")
    long_lines = sum(1 for line in skill_text.splitlines() if len(line) > 600 and not line.startswith("description:"))
    if long_lines:
        out.append(f"WARN: {long_lines} SKILL.md line(s) over 600 chars")

    # 7. Reference versions that disagree with the skill's version.
    fm = re.match(r"^---\n(.*?)\n---", skill_text, re.S)
    skill_ver = re.search(r'^\s+version:\s*"?([\d.]+)', fm.group(1), re.M) if fm else None
    if skill_ver:
        drift = []
        for p, t in texts.items():
            # Frontmatter under assets/ or templates/ versions the document
            # the skill generates, not the skill.
            parts = p.relative_to(path).parts
            if p.name == "SKILL.md" or not t.startswith("---\n") or "assets" in parts or "templates" in parts:
                continue
            head = t[4:t.find("\n---", 4)]
            m = re.search(r'^ver(?:sion)?:\s*"?([\d.]+)', head, re.M)
            if m and m.group(1) != skill_ver.group(1):
                drift.append(p.name)
        if drift:
            out.append(f"WARN: {len(drift)} reference(s) carry a version other than {skill_ver.group(1)}: {', '.join(drift[:4])}")

    # 8. Dangling symlinks inside the skill.
    broken = [p.relative_to(path).as_posix() for p in walk if p.is_symlink() and not p.exists()]
    if broken:
        out.append(f"WARN: {len(broken)} dangling symlink(s): {', '.join(broken[:4])}")
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
    found = find_skills(root)
    skill_names = frozenset(p.name for p in found)
    for path in found:
        raw = (path / "SKILL.md").read_bytes()
        text = raw.decode("utf-8", errors="replace").replace("\r\n", "\n")
        declared = declared_refs(path, text, skill_names)
        missing = sorted(r if srcs == ["SKILL.md"] else f"{r} (in {', '.join(sorted(set(srcs)))})"
                         for r, srcs in declared.items() if srcs)
        skills[str(path.relative_to(root))] = {
            "triggers": sorted(triggers(description(text))),
            "declared_refs": len(declared),
            "missing_refs": missing,
            "portability": portability(path, raw),
            "unreferenced": shipped_but_unreferenced(path, text),
            "effectiveness": effectiveness(path, text),
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
        "effectiveness": {n: s["effectiveness"] for n, s in skills.items() if s["effectiveness"]},
        "effectiveness_errors": sorted(n for n, s in skills.items() if any(f.startswith("ERROR") for f in s["effectiveness"])),
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

    failed = bool(result["collisions"] or result["portability_errors"] or result["lost_triggers"]
                  or result["effectiveness_errors"])
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
    print("  Each declares no quoted trigger phrases; trigger collisions cannot be checked for it.")
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

    eff = result["effectiveness"]
    print(f"\n== EFFECTIVENESS ({len(eff)}) ==")
    if not eff:
        print("  none")
    for n, findings in sorted(eff.items()):
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
