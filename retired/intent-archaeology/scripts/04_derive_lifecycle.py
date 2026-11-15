#!/usr/bin/env python3
"""Phase 4: derive each project's lifecycle state.

See references/lifecycle_states.md. Derivation is a proposal;
confirmation can be automated (confidence > 0.9) or human.

States: not-started | in-progress | completed | under-revision | archive-candidate

Usage:
    python scripts/04_derive_lifecycle.py --db ~/.intent-archaeology/state.db
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import subprocess
import sys
from datetime import datetime, timedelta


def git_last_commit_date(path: str) -> datetime | None:
    try:
        r = subprocess.run(
            ["git", "-C", path, "log", "-1", "--format=%cI"],
            capture_output=True, text=True, check=True,
        )
        return datetime.fromisoformat(r.stdout.strip())
    except Exception:
        return None


def git_commit_count(path: str) -> int:
    try:
        r = subprocess.run(
            ["git", "-C", path, "rev-list", "--count", "HEAD"],
            capture_output=True, text=True, check=True,
        )
        return int(r.stdout.strip())
    except Exception:
        return 0


def git_has_release_tag(path: str) -> bool:
    try:
        r = subprocess.run(
            ["git", "-C", path, "tag", "--list"],
            capture_output=True, text=True, check=True,
        )
        return bool(r.stdout.strip())
    except Exception:
        return False


def cass_session_activity(workspace: str, days: int = 30) -> int:
    """Count unique sessions for a workspace using cass search.
    
    cass timeline does not support --workspace, so we use cass search with
    --robot-format sessions which returns deduplicated session paths.
    Returns 0 on error.
    """
    try:
        r = subprocess.run(
            ["cass", "search", "", "--workspace", workspace,
             "--robot-format", "sessions", "--days", str(days),
             "--limit", "0"],
            capture_output=True, text=True, check=True,
        )
        return len([l for l in r.stdout.splitlines() if l.strip()])
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"WARN: cass search failed for {workspace}: {e}", file=sys.stderr)
        return 0


def derive_state(project: dict) -> tuple[str, float, list[str]]:
    """Returns (state, confidence, evidence)."""
    path = project["path"]
    era = project.get("era", 0)
    evidence = []

    last_commit = git_last_commit_date(path)
    commit_count = git_commit_count(path)
    has_release = git_has_release_tag(path)
    recent_sessions = cass_session_activity(path, days=30)
    older_sessions = cass_session_activity(path, days=180)

    if last_commit:
        evidence.append(f"last commit: {last_commit.date()}")
    evidence.append(f"commits: {commit_count}")
    if has_release:
        evidence.append("has release tag")
    evidence.append(f"sessions last 30d: {recent_sessions}")
    evidence.append(f"sessions last 180d: {older_sessions}")

    # Decision tree
    now = datetime.now()

    if era == 0:
        if commit_count == 0:
            return "not-started", 0.95, evidence
        return "archive-candidate", 0.7, evidence

    if commit_count == 0 and recent_sessions == 0:
        return "not-started", 0.9, evidence

    if has_release and recent_sessions == 0:
        # Completed, possibly dormant
        if last_commit and (now - last_commit) > timedelta(days=180):
            return "archive-candidate", 0.6, evidence
        return "completed", 0.85, evidence

    if has_release and recent_sessions > 0:
        return "under-revision", 0.8, evidence

    if commit_count > 0 and recent_sessions > 0:
        return "in-progress", 0.9, evidence

    if commit_count > 0 and recent_sessions == 0:
        if last_commit and (now - last_commit) > timedelta(days=180):
            return "archive-candidate", 0.65, evidence
        return "in-progress", 0.5, evidence  # low confidence

    return "not-started", 0.4, evidence


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", required=True)
    args = ap.parse_args()

    with sqlite3.connect(args.db) as conn:
        rows = conn.execute("SELECT id, name, path, era FROM projects").fetchall()
        for pid, name, path, era in rows:
            state, conf, evidence = derive_state({"path": path, "era": era})
            # Auto-confirm if confidence > 0.9
            confirmed = state if conf > 0.9 else "proposed"
            conn.execute(
                """UPDATE projects SET
                   derived_lifecycle = ?, lifecycle_confidence = ?,
                   lifecycle_evidence = ?, lifecycle = ?, updated_at = datetime('now')
                   WHERE id = ?""",
                (state, conf, json.dumps(evidence), confirmed, pid),
            )
            print(f"  {name}: derived={state} conf={conf:.2f} confirmed={confirmed}", file=sys.stderr)
        conn.commit()
    print(f"OK: derived lifecycle for {len(rows)} projects", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
