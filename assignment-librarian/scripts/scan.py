#!/usr/bin/env python3
"""Folder inventory → readiness report JSON for the assignments library.

Read-only: walks the library root, never writes into it. Stdlib only.
A folder WITH a valid project-intake.json auto-populates as a staged packet;
a folder WITHOUT one is still listed, flagged unstaged, never silently ready.

Usage:
    scan.py [ROOT] [--out REPORT.json]
    scan.py /home/cheta/LIVING_DOCUMENTS/new_assignments/ --out /tmp/readiness.json
"""
import argparse
import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

THEMES = (
    "agentic-systems",
    "dev-tooling",
    "security-research",
    "hardware-platforms",
    "creative-products",
    "staging",
)

# Tie-break priority: earlier wins on equal hit counts (see references/periodic-rescan.md).
TIEBREAK = (
    "creative-products",
    "security-research",
    "hardware-platforms",
    "dev-tooling",
    "agentic-systems",
)

KEYWORDS = {
    "agentic-systems": {"agent", "agentic", "orchestrator", "flywheel", "routing",
                        "quota", "prompt", "model", "stack", "unified", "driver",
                        "hunt", "operator", "phase", "deal", "desktop",
                        "sluice", "fragment", "reasoning", "inference", "cost",
                        "aware", "dispatch", "mission", "autonomous", "headless",
                        "poll", "quartermaster", "scan"},
    "dev-tooling": {"repo", "cleanup", "wsl", "atlas", "spec-prep", "tooling",
                    "dev", "reclaim", "t3", "code", "registry", "consolidation",
                    "lint", "sqlite", "skill"},
    "security-research": {"adversarial", "dossier", "greynoise", "swarm", "web",
                          "hack", "hacking", "threat", "security", "research",
                          "vuln", "offensive", "sensor"},
    "hardware-platforms": {"pi", "siri", "remote", "laptop", "hardware",
                           "windows", "input", "chrome", "tab", "extension",
                           "switchboard", "servicing", "raspberry", "bluetooth",
                           "firmware", "touch", "console", "usb", "reaper", "sleep"},
    "creative-products": {"game", "wars", "foundry", "smile", "smiledraft", "draft",
                          "creative", "product", "rpg", "dental", "avatar",
                          "collectible"},
}

LIFECYCLES = {"staged", "specification-prepared", "initiated"}
ASSIGNMENTS = {"unassigned", "assigned", "tooling"}
ISSUE_SEVERITIES = {"info", "conversion", "missing-input"}
SPEC_NAMES = ("requirements", "design", "intent", "constitution")
SPEC_FILES = {"spec.md", "plan.md", "tasks.md"}
PROJECT_ID_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def tokens(name):
    return [t for t in re.split(r"[^a-z0-9]+", name.lower()) if t]


def guess_theme(folder, top_names):
    scores = {theme: 0 for theme in KEYWORDS}
    for text in [folder.name] + top_names:
        for tok in tokens(text):
            for theme, words in KEYWORDS.items():
                if tok in words:
                    scores[theme] += 1
    best = max(scores.values())
    if not best:
        return "staging", "keyword-fallback"
    tied = [t for t, s in scores.items() if s == best]
    for theme in TIEBREAK:
        if theme in tied:
            return theme, "keyword-fallback"
    return tied[0], "keyword-fallback"


def inventory(folder):
    """Flat file list; mirrors catalog.py traversal rules (no dotfiles, no symlinks)."""
    files = []
    for parent, dirs, names in os.walk(folder, followlinks=False):
        dirs[:] = sorted(d for d in dirs
                         if not d.startswith(".") and not (Path(parent) / d).is_symlink())
        for name in sorted(names):
            path = Path(parent) / name
            if name.startswith(".") or path.is_symlink() or not path.is_file():
                continue
            try:
                stat = path.stat()
            except OSError:
                continue
            files.append({"path": path.relative_to(folder).as_posix(),
                          "bytes": stat.st_size})
    return files


def local_file(folder, value):
    if not isinstance(value, str) or not value or Path(value).is_absolute():
        raise ValueError("expected a relative file path: %r" % (value,))
    if ".." in Path(value).parts:
        raise ValueError("path traversal is forbidden: %r" % (value,))
    target = folder / value
    try:
        resolved = target.resolve()
    except OSError as exc:
        raise ValueError("unresolvable path %r: %s" % (value, exc))
    if not str(resolved).startswith(str(folder.resolve()) + os.sep):
        raise ValueError("path escapes the intake folder: %r" % (value,))
    if target.is_symlink() or not target.is_file():
        raise ValueError("missing or symlinked input: %r" % (value,))
    return target


def validate(folder, manifest):
    """Minimal manifest check mirroring .catalog/intake-validator.py."""
    errors = []
    if not isinstance(manifest, dict):
        return ["manifest must be an object"]
    if manifest.get("schemaVersion") != 1:
        errors.append("schemaVersion must be 1")
    if not PROJECT_ID_RE.fullmatch(str(manifest.get("projectId", ""))):
        errors.append("projectId must be kebab-case")
    for key in ("title", "summary", "nextOperation"):
        if not isinstance(manifest.get(key), str) or not manifest[key].strip():
            errors.append("%s must be a nonempty string" % key)
    if manifest.get("lifecycle") not in LIFECYCLES:
        errors.append("invalid lifecycle")
    if manifest.get("assignment") not in ASSIGNMENTS:
        errors.append("invalid assignment")
    for key in ("sources", "readOrder", "issues", "relatedProjects", "externalResources"):
        if not isinstance(manifest.get(key), list):
            errors.append("%s must be an array" % key)
    seen = set()
    for source in manifest.get("sources", []) if isinstance(manifest.get("sources"), list) else []:
        if not isinstance(source, dict):
            errors.append("each source must be an object")
            continue
        try:
            path = local_file(folder, source.get("path"))
            if source["path"] in seen:
                errors.append("duplicate source: %s" % source["path"])
            seen.add(source["path"])
            if not all(isinstance(source.get(k), str) and source[k] for k in ("format", "role")):
                errors.append("source lacks format or role: %s" % source["path"])
            if source.get("sha256"):
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
                if digest != source["sha256"]:
                    errors.append("source hash mismatch: %s" % source["path"])
        except (OSError, ValueError, TypeError) as exc:
            errors.append(str(exc))
    for name in manifest.get("readOrder", []) if isinstance(manifest.get("readOrder"), list) else []:
        try:
            local_file(folder, name)
        except (OSError, ValueError, TypeError) as exc:
            errors.append(str(exc))
    if not manifest.get("readOrder"):
        errors.append("readOrder must name at least one file")
    for item in manifest.get("issues", []) if isinstance(manifest.get("issues"), list) else []:
        if (not isinstance(item, dict) or item.get("severity") not in ISSUE_SEVERITIES
                or not isinstance(item.get("detail"), str)):
            errors.append("issues require severity and detail")
    return errors


def spec_artifacts(files):
    found = []
    for entry in files:
        path = entry["path"]
        base = path.rsplit("/", 1)[-1].lower()
        if base in ("project-intake.json", "start-here.md", "workbench.json"):
            continue
        stem = base[:-3] if base.endswith(".md") else base
        if base in SPEC_FILES or stem in SPEC_NAMES or path.lower().startswith("specs/"):
            found.append(path)
    return sorted(found)


def scan_folder(folder):
    files = inventory(folder)
    manifest_file = folder / "project-intake.json"
    has_manifest = manifest_file.is_file() and not manifest_file.is_symlink()
    manifest = {}
    errors = []
    if has_manifest:
        try:
            manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
            errors = validate(folder, manifest)
        except (ValueError, OSError) as exc:
            manifest = {}
            errors = [str(exc)]
    else:
        errors = ["Add project-intake.json to declare the project, read order and readiness."]
    issues = [x for x in manifest.get("issues", [])] if isinstance(manifest.get("issues"), list) else []
    needs_brief = any(isinstance(x, dict) and x.get("severity") == "missing-input" for x in issues)
    specs = spec_artifacts(files)
    lifecycle = manifest.get("lifecycle") if isinstance(manifest, dict) else None

    if not has_manifest:
        readiness = "unstaged"
    elif errors:
        readiness = "needs-intake"
    elif needs_brief:
        readiness = "needs-intake"
    elif specs or lifecycle in ("specification-prepared", "initiated"):
        readiness = "has-specs"
    else:
        readiness = "ready-for-spec-prep"

    declared = manifest.get("theme") if isinstance(manifest, dict) else None
    if declared in THEMES:
        theme, theme_source = declared, "manifest"
    else:
        top_names = [f["path"].split("/")[0] for f in files[:50]]
        theme, theme_source = guess_theme(folder, top_names)

    staged_at = manifest.get("stagedAt") if isinstance(manifest, dict) else None
    date_source = "folder-mtime"
    staged_date = None
    if isinstance(staged_at, str):
        text = staged_at.strip()
        if DATE_RE.match(text):
            staged_date, date_source = text, "manifest"
        else:
            try:
                staged_date = datetime.fromisoformat(text.replace("Z", "+00:00")).date().isoformat()
                date_source = "manifest"
            except ValueError:
                staged_date = None
    if staged_date is None:
        try:
            mtime = folder.stat().st_mtime
        except OSError:
            mtime = 0
        staged_date = datetime.fromtimestamp(mtime, tz=timezone.utc).date().isoformat()
        date_source = "folder-mtime"

    title = manifest.get("title") if isinstance(manifest.get("title"), str) else None
    return {
        "folder": folder.name,
        "projectId": manifest.get("projectId") if isinstance(manifest.get("projectId"), str) else folder.name,
        "title": title.strip() if title and title.strip() else folder.name.replace("-", " ").replace("_", " ").title(),
        "theme": theme,
        "themeSource": theme_source,
        "hasManifest": has_manifest,
        "manifestValid": has_manifest and not errors,
        "errors": errors,
        "stagedDate": staged_date,
        "stagedDateSource": date_source,
        "specArtifacts": specs,
        "readiness": readiness,
        "fileCount": len(files),
        "bytes": sum(f["bytes"] for f in files),
    }


def scan_root(root):
    projects = []
    for folder in sorted(root.iterdir()):
        if folder.name.startswith(".") or folder.is_symlink() or not folder.is_dir():
            continue
        try:
            projects.append(scan_folder(folder))
        except OSError as exc:
            projects.append({"folder": folder.name, "readiness": "unstaged",
                             "errors": ["unreadable folder: %s" % exc], "theme": "staging",
                             "hasManifest": False, "manifestValid": False,
                             "specArtifacts": [], "fileCount": 0, "bytes": 0,
                             "stagedDate": None, "projectId": folder.name,
                             "title": folder.name})
    by_theme = {t: 0 for t in THEMES}
    by_status = {"unstaged": 0, "needs-intake": 0, "ready-for-spec-prep": 0, "has-specs": 0}
    for project in projects:
        by_theme[project.get("theme", "staging")] = by_theme.get(project.get("theme"), 0) + 1
        by_status[project.get("readiness")] = by_status.get(project.get("readiness"), 0) + 1
    report = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "root": str(root),
        "projectCount": len(projects),
        "projects": projects,
        "summary": {
            "byTheme": by_theme,
            "byStatus": by_status,
            "unstaged": [p["folder"] for p in projects if p.get("readiness") == "unstaged"],
            "needsIntake": [p["folder"] for p in projects if p.get("readiness") == "needs-intake"],
            "oldestUnstaged": sorted(
                (p for p in projects if p.get("readiness") == "unstaged" and p.get("stagedDate")),
                key=lambda p: p["stagedDate"])[:5],
            "largest": [{"folder": p["folder"], "bytes": p["bytes"], "fileCount": p["fileCount"]}
                        for p in sorted(projects, key=lambda p: p.get("bytes", 0), reverse=True)[:5]],
        },
    }
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default="/home/cheta/LIVING_DOCUMENTS/new_assignments/",
                        help="assignments library root to scan")
    parser.add_argument("--out", default=None, help="write report JSON here (never inside the library)")
    args = parser.parse_args()
    root = Path(args.root)
    if not root.is_dir():
        raise SystemExit("not a directory: %s" % root)
    report = scan_root(root)
    text = json.dumps(report, indent=2)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
