#!/usr/bin/env python3
"""Phase 1: identify projects under the scan roots and describe them.

A folder is not a project. Three cases are handled separately:
  - repo is the project      (.git at root)
  - folder holds projects    (no .git at root, manifests below)
  - repo holds projects      (.git at root plus several manifests)

Directories that score ambiguously go to `unclassified` and are reported
rather than guessed at. Guessing here poisons every later phase.

Idempotent. Rerunning updates rows in place.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib.common import (  # noqa: E402
    DEFAULT_ROOTS, MANIFESTS, PIPELINE_VERSION, SKIP_DIRS, SOURCE_EXT,
    connect, git, init_db, log, now, report, slug,
)

MONOREPO_DIRS = ("packages", "apps", "crates", "services", "libs")


def count_sources(path: Path, cap: int = 4000) -> int:
    n = 0
    for p in path.rglob("*"):
        if n >= cap:
            break
        if p.is_dir():
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if p.suffix in SOURCE_EXT:
            n += 1
    return n


def find_manifest(path: Path) -> str | None:
    for m in MANIFESTS:
        if (path / m).is_file():
            return m
    return None


def child_dirs(path: Path) -> list[Path]:
    try:
        return [d for d in sorted(path.iterdir())
                if d.is_dir() and d.name not in SKIP_DIRS and not d.name.startswith(".")]
    except OSError:
        return []


def manifest_count(path: Path, depth: int = 2) -> int:
    n = 0
    for d in child_dirs(path):
        if find_manifest(d):
            n += 1
        if depth > 1:
            for sub in MONOREPO_DIRS:
                p = d / sub
                if p.is_dir():
                    n += sum(1 for c in child_dirs(p) if find_manifest(c))
    return n


def read_description(path: Path) -> tuple[str | None, list[dict]]:
    """Gather every description candidate with provenance. Do not choose blindly."""
    sources: list[dict] = []

    readme = None
    for name in ("README.md", "readme.md", "README.rst", "README.txt", "README"):
        p = path / name
        if p.is_file():
            readme = p
            break
    if readme:
        try:
            text = readme.read_text(encoding="utf-8", errors="replace")
            body = re.sub(r"^\s*#.*$", "", text, count=1, flags=re.M)
            body = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", body)
            body = re.sub(r"^\s*\[!\[.*$", "", body, flags=re.M)
            para = next((b.strip() for b in body.split("\n\n") if len(b.strip()) > 30), None)
            if para:
                sources.append({
                    "source": "readme",
                    "text": " ".join(para.split())[:400],
                    "mtime": readme.stat().st_mtime,
                })
        except OSError:
            pass

    for m in ("package.json", "composer.json", "deno.json"):
        p = path / m
        if p.is_file():
            try:
                d = json.loads(p.read_text(encoding="utf-8", errors="replace"))
                if isinstance(d, dict) and d.get("description"):
                    sources.append({"source": m, "text": str(d["description"])[:400],
                                    "mtime": p.stat().st_mtime})
            except (OSError, json.JSONDecodeError):
                pass

    p = path / "Cargo.toml"
    if p.is_file():
        try:
            txt = p.read_text(encoding="utf-8", errors="replace")
            m = re.search(r'^\s*description\s*=\s*"([^"]+)"', txt, re.M)
            if m:
                sources.append({"source": "Cargo.toml", "text": m.group(1)[:400],
                                "mtime": p.stat().st_mtime})
        except OSError:
            pass

    desc = sources[0]["text"] if sources else None
    return desc, sources


def stale_flag(sources: list[dict], last_commit_ts: str | None) -> int | None:
    """A description much older than the newest code is a drift signal, not noise."""
    if not sources or not last_commit_ts:
        return None
    try:
        newest_desc = max(s["mtime"] for s in sources)
        commit = float(last_commit_ts)
    except (ValueError, TypeError, KeyError):
        return None
    return 1 if commit - newest_desc > 60 * 60 * 24 * 90 else 0


def classify(path: Path) -> tuple[str, dict]:
    has_git = (path / ".git").exists()
    manifest = find_manifest(path)
    sources = count_sources(path)
    kids_with_manifest = manifest_count(path)
    kids = child_dirs(path)
    kids_with_git = sum(1 for d in kids if (d / ".git").exists())

    facts = {
        "has_git": has_git, "manifest": manifest, "source_files": sources,
        "child_manifests": kids_with_manifest, "child_git": kids_with_git,
    }

    if has_git and kids_with_manifest >= 2 and sources > 0:
        return "monorepo", facts
    if has_git or (manifest and sources > 0):
        return "project", facts
    if kids_with_git >= 1 or kids_with_manifest >= 1:
        return "container", facts
    if sources >= 3:
        return "project", facts
    return "unclassified", facts


def upsert(conn, pid, path, root, kind, parent, facts):
    p = Path(path)
    remote = git(p, "config", "--get", "remote.origin.url") if facts["has_git"] else None
    initial = None
    if facts["has_git"]:
        out = git(p, "rev-list", "--max-parents=0", "HEAD")
        initial = out.splitlines()[-1] if out else None
    last_commit = git(p, "log", "-1", "--format=%ct") if facts["has_git"] else None

    desc, dsources = read_description(p)
    stale = stale_flag(dsources, last_commit)

    try:
        mtime = str(p.stat().st_mtime)
    except OSError:
        mtime = None

    conn.execute(
        """INSERT INTO project (id,path,root,kind,parent_id,git_remote,git_initial_sha,
             manifest,has_git,source_files,last_commit_ts,last_mtime,description,
             description_sources,description_stale,pipeline_version,created_at)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
           ON CONFLICT(id) DO UPDATE SET
             path=excluded.path, kind=excluded.kind, parent_id=excluded.parent_id,
             git_remote=excluded.git_remote, git_initial_sha=excluded.git_initial_sha,
             manifest=excluded.manifest, has_git=excluded.has_git,
             source_files=excluded.source_files, last_commit_ts=excluded.last_commit_ts,
             last_mtime=excluded.last_mtime, description=excluded.description,
             description_sources=excluded.description_sources,
             description_stale=excluded.description_stale,
             pipeline_version=excluded.pipeline_version""",
        (pid, str(path), root, kind, parent, remote, initial, facts["manifest"],
         int(facts["has_git"]), facts["source_files"], last_commit, mtime, desc,
         json.dumps(dsources), stale, PIPELINE_VERSION, now()),
    )


def scan(conn, roots: list[Path]) -> dict[str, int]:
    counts = {"project": 0, "container": 0, "monorepo": 0, "unclassified": 0}
    for root in roots:
        if not root.is_dir():
            print(f"  skip (missing): {root}")
            continue
        for d in child_dirs(root):
            kind, facts = classify(d)
            pid = slug(f"{root.name}-{d.name}")
            upsert(conn, pid, d, str(root), kind, None, facts)
            counts[kind] += 1

            if kind in ("container", "monorepo"):
                for sub in child_dirs(d):
                    skind, sfacts = classify(sub)
                    if skind == "unclassified":
                        continue
                    # inside a monorepo, children are features of one project,
                    # not separate projects. Record them as children only.
                    child_kind = "project" if kind == "container" else "container"
                    spid = slug(f"{root.name}-{d.name}-{sub.name}")
                    upsert(conn, spid, sub, str(root), child_kind, pid, sfacts)
                    counts[child_kind] = counts.get(child_kind, 0) + 1
    conn.commit()
    return counts


def main() -> int:
    ap = argparse.ArgumentParser(description="Phase 1: project inventory")
    ap.add_argument("--roots", nargs="*", default=None,
                    help="scan roots (default: ~/code ~/code2)")
    args = ap.parse_args()

    roots = [Path(r).expanduser() for r in args.roots] if args.roots else DEFAULT_ROOTS
    conn = init_db()
    log(conn, "inventory", "start", json.dumps([str(r) for r in roots]))

    print("Scanning roots:", ", ".join(str(r) for r in roots))
    counts = scan(conn, roots)

    rows = conn.execute(
        "SELECT kind, COUNT(*) c FROM project GROUP BY kind ORDER BY c DESC"
    ).fetchall()
    report("Inventory", [(r["kind"], r["c"]) for r in rows])

    unc = conn.execute(
        "SELECT path FROM project WHERE kind='unclassified' ORDER BY path"
    ).fetchall()
    if unc:
        print(f"\nUnclassified ({len(unc)}). Resolve these by hand before phase 2:")
        for r in unc:
            print(f"  {r['path']}")
        print("\n  Fix with: sqlite3 ~/.intent-archaeology/archaeology.db \\")
        print("    \"UPDATE project SET kind='project' WHERE path='<path>'\"")

    stale = conn.execute(
        "SELECT COUNT(*) c FROM project WHERE description_stale=1"
    ).fetchone()["c"]
    nodesc = conn.execute(
        "SELECT COUNT(*) c FROM project WHERE kind='project' AND description IS NULL"
    ).fetchone()["c"]
    print(f"\nDescriptions: {stale} stale (code much newer than docs), {nodesc} missing")
    print("Stale descriptions are drift evidence, not noise. They feed the audit.")

    log(conn, "inventory", "done", json.dumps(counts))
    print("\nExit criterion: unclassified list above has been read. Next: 02-attribute.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
