#!/usr/bin/env python3
"""Phase 0+1: discover projects in --code-dirs and write descriptions.

Usage:
    python scripts/01_discover_projects.py \
        --db ~/.intent-archaeology/state.db \
        --code-dirs ~/code ~/code2 \
        [--github-token "$GITHUB_TOKEN"]

Exit criteria: every directory under --code-dirs that has a .git OR a
non-trivial README OR a spec-kit requirements.md is a row. Subfolder
projects are included.
"""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def discover_projects(code_dirs: list[str]) -> list[dict]:
    projects = []
    seen_paths = set()
    for d in code_dirs:
        root = Path(d).expanduser().resolve()
        if not root.is_dir():
            print(f"WARN: {root} is not a directory, skipping", file=sys.stderr)
            continue
        # Top-level project
        if _is_project_dir(root):
            if str(root) not in seen_paths:
                projects.append({"name": root.name, "path": str(root)})
                seen_paths.add(str(root))
        # Subfolder projects (one level deep)
        for child in sorted(root.iterdir()):
            if child.is_dir() and _is_project_dir(child) and str(child) not in seen_paths:
                projects.append({"name": child.name, "path": str(child)})
                seen_paths.add(str(child))
    return projects


def _is_project_dir(p: Path) -> bool:
    return any([
        (p / ".git").exists(),
        (p / "README.md").exists(),
        (p / "README").exists(),
        (p / "requirements.md").exists(),
        (p / "design.md").exists(),
        (p / "prd.md").exists(),
        (p / "LIVING.md").exists(),
        # Heuristic: has >=3 source files
        sum(1 for _ in p.rglob("*.py") if ".venv" not in str(_)) >= 3,
        sum(1 for _ in p.rglob("*.ts") if "node_modules" not in str(_)) >= 3,
    ])


def describe_project(project: dict, github_token: str | None) -> dict:
    p = Path(project["path"])
    # 1. Try README.md
    readme = p / "README.md"
    if readme.exists():
        text = readme.read_text(errors="ignore")
        # First non-empty paragraph
        for line in text.split("\n\n"):
            line = line.strip()
            if line and not line.startswith("#"):
                project["description"] = line[:500]
                break
    # 2. Try git remote → GitHub description
    if "description" not in project:
        try:
            r = subprocess.run(
                ["git", "-C", str(p), "remote", "get-url", "origin"],
                capture_output=True, text=True, check=True,
            )
            remote = r.stdout.strip()
            if "github.com" in remote:
                # Extract owner/repo
                m = remote.replace(".git", "").split("github.com/")[-1]
                if "/" in m:
                    project["github_url"] = f"https://github.com/{m}"
                    if github_token:
                        project["description"] = _github_description(m, github_token) or ""
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
    # 3. Fallback: brief scan
    if "description" not in project:
        project["description"] = f"(no description; {sum(1 for _ in p.iterdir() if _.is_file())} top-level files)"
    return project


def _github_description(repo: str, token: str) -> str | None:
    import urllib.request
    req = urllib.request.Request(
        f"https://api.github.com/repos/{repo}",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.load(r).get("description")
    except Exception:
        return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", required=True)
    ap.add_argument("--code-dirs", nargs="+", default=["~/code", "~/code2"])
    ap.add_argument("--github-token", default=os.environ.get("GITHUB_TOKEN"))
    args = ap.parse_args()

    projects = discover_projects(args.code_dirs)
    print(f"Discovered {len(projects)} projects", file=sys.stderr)

    with sqlite3.connect(args.db) as conn:
        for p in projects:
            p = describe_project(p, args.github_token)
            conn.execute(
                """INSERT OR REPLACE INTO projects
                   (name, path, description, github_url, updated_at)
                   VALUES (?, ?, ?, ?, datetime('now'))""",
                (p["name"], p["path"], p.get("description"), p.get("github_url")),
            )
        conn.commit()

    print(f"OK: wrote {len(projects)} projects to {args.db}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
