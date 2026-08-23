#!/usr/bin/env python3
"""Phase 3: spec archaeology — find the canonical PRD via cass.

For era 5 projects: skip archaeology, use the living document.
For era 0 projects: skip (no spec to find).
For eras 1-4: search cass for 'specify.spec' and 'requirements.md' in
  the project's workspace; identify which version of the PRD was live
  at the time of the first /specify.plan or first coding session.

For under-revision projects: produce change-level specs, not
whole-system reconstruction. See references/lifecycle_states.md.

Usage:
    python scripts/03_spec_archaeology.py --db ~/.intent-archaeology/state.db
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import subprocess
import sys
from pathlib import Path


def cass_search(query: str, workspace: str) -> list[dict]:
    """Run cass search and parse JSON."""
    try:
        r = subprocess.run(
            ["cass", "search", query, "--workspace", workspace, "--fields", "full", "--json", "--limit", "10"],
            capture_output=True, text=True, check=True,
        )
        data = json.loads(r.stdout)
        return data.get("hits", [])
    except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError) as e:
        print(f"WARN: cass search failed: {e}", file=sys.stderr)
        return []


def find_canonical_prd(project: dict) -> tuple[str | None, list[dict]]:
    """Return (canonical_prd_path, spec_lineage)."""
    path = project["path"]
    era = project["era"]

    # Era 5: use living document directly
    if era == 5:
        living = Path(path) / "LIVING.md"
        if living.exists():
            return str(living), [{"path": str(living), "role": "living-document", "version": "3.x"}]
        # Fallback
        for cand in Path(path).glob("*.living.md"):
            return str(cand), [{"path": str(cand), "role": "living-document"}]

    # Era 0: nothing
    if era == 0:
        return None, []

    # Eras 1-4: archaeology
    lineage = []
    # Find all PRD/requirements versions in the project
    candidates = []
    for pattern in ["prd*.md", "PRD*.md", "requirements*.md", "design*.md"]:
        candidates.extend(Path(path).glob(pattern))
    for c in candidates:
        lineage.append({"path": str(c), "role": "candidate"})

    # Search cass for /specify.plan and /specify.spec invocations
    plan_hits = cass_search("specify.plan", path)
    spec_hits = cass_search("specify.spec", path)
    req_hits = cass_search("requirements.md", path)

    # Heuristic: the version of requirements.md that was attached at the
    # first /specify.plan is the canonical one. We can't fully reconstruct
    # file contents from cass, but we can record the timestamps.
    if plan_hits:
        first_plan = min(plan_hits, key=lambda h: h.get("created_at", ""))
        lineage.append({
            "path": "cass://specify.plan",
            "role": "plan-invocation",
            "attached_at": first_plan.get("created_at"),
        })

    # Git history resolution: find the version of each candidate file
    # that existed at the time of the first coding session.
    # This resolves from git history rather than just picking by filename.
    session_timestamps = []
    for hit in plan_hits + spec_hits + req_hits:
        ts = hit.get("created_at")
        if ts:
            session_timestamps.append(ts)
    # Also check for any session activity in the repo
    try:
        r = subprocess.run(
            ["cass", "search", "", "--workspace", path, "--fields", "minimal",
             "--limit", "5", "--json"],
            capture_output=True, text=True, timeout=15,
        )
        if r.returncode == 0:
            sess_data = json.loads(r.stdout)
            for h in sess_data.get("hits", []):
                ts = h.get("created_at")
                if ts:
                    session_timestamps.append(ts)
    except Exception:
        pass

    # If we have session timestamps, try git history resolution
    if session_timestamps and candidates:
        earliest_session = min(session_timestamps)
        # Try to find which file version was live at session time
        # Use git log to check if the file existed at that point
        best = None
        best_commit = None
        for c in candidates:
            try:
                # Check git log for this file
                r = subprocess.run(
                    ["git", "-C", path, "log", "--all", "--oneline",
                     "--diff-filter=A", "--", str(c.relative_to(Path(path)))],
                    capture_output=True, text=True, timeout=10,
                )
                if r.returncode == 0 and r.stdout.strip():
                    # File was added at some point. Check if before our session.
                    first_commit = r.stdout.strip().split("\n")[-1].split()[0]
                    cr = subprocess.run(
                        ["git", "-C", path, "log", "--format=%aI", "-1", first_commit],
                        capture_output=True, text=True, timeout=10,
                    )
                    if cr.returncode == 0 and cr.stdout.strip():
                        add_date = cr.stdout.strip()
                        if add_date <= earliest_session:
                            best = str(c)
                            best_commit = first_commit
            except Exception:
                continue
        if best:
            canonical = best
            lineage.append({
                "path": best,
                "role": "canonical",
                "resolved_by": "git-history",
                "commit": best_commit,
                "added_before_session": earliest_session,
            })
            return canonical, lineage

    # Fallback: pick by filename convention
    canonical = None
    for cand in candidates:
        if cand.name == "requirements.md":
            canonical = str(cand)
            break
    if not canonical:
        prds = sorted([c for c in candidates if "prd" in c.name.lower() or "PRD" in c.name])
        if prds:
            canonical = str(prds[-1])  # last version alphabetically
            lineage.append({
                "path": canonical,
                "role": "canonical",
                "resolved_by": "filename-convention",
            })


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", required=True)
    args = ap.parse_args()

    with sqlite3.connect(args.db) as conn:
        rows = conn.execute("SELECT id, name, path, era FROM projects").fetchall()
        for pid, name, path, era in rows:
            canonical, lineage = find_canonical_prd({"path": path, "era": era})
            conn.execute(
                "UPDATE projects SET canonical_prd_path = ?, spec_lineage = ?, updated_at = datetime('now') WHERE id = ?",
                (canonical, json.dumps(lineage), pid),
            )
            print(f"  {name}: era={era} canonical={canonical}", file=sys.stderr)
        conn.commit()
    print(f"OK: spec archaeology for {len(rows)} projects", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
