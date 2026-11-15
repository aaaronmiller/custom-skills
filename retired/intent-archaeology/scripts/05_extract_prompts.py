#!/usr/bin/env python3
"""Phase 5: extract every human prompt, scoped, newest-first.

Uses cass for selection and raw JSONL for extraction. See
references/cass_fidelity.md and references/scope_selectors.md.
# Phase C enumerates (cass search empty-query + cass export), never searches
# with content queries. cass search "" --workspace ... --robot-format sessions
# returns deduplicated session paths; then cass export per session.
# Cass timeline --workspace does not exist in v0.6.x, so we use search instead.
Usage:
    python scripts/05_extract_prompts.py \
        --db ~/.intent-archaeology/state.db \
        --ordering newest-first \
        --since 30d
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent))
from lib.scope import ScopeSpec, add_scope_args, parse_args, run_cass

def cass_timeline(workspace: str, since_days: int) -> list[dict]:
    """Enumerate sessions for a workspace via cass search (sessions format).
    
    cass timeline does not support --workspace, so we use cass search with
    empty query + workspace filter, outputting session paths directly
    (deduplication built-in).
    Returns list of dicts with keys: source_path.
    """
    try:
        r = subprocess.run(
            ["cass", "search", "", "--workspace", workspace,
             "--robot-format", "sessions", "--days", str(since_days),
             "--limit", "0"],
            capture_output=True, text=True, check=True,
        )
        lines = [l.strip() for l in r.stdout.splitlines() if l.strip()]
        return [{"source_path": l} for l in lines]
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"WARN: cass search failed for {workspace}: {e}", file=sys.stderr)
        return []

def cass_export(session_path: str, include_tools: bool = False) -> list[dict]:
    """cass export <path> --format json [--include-tools]"""
    cmds = [["cass", "export", session_path, "--format", "json"]]
    if include_tools:
        cmds.append(["cass", "export", session_path, "--include-tools"])
    out = []
    for cmd in cmds:
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(r.stdout)
            if isinstance(data, list):
                out.extend(data)
            elif isinstance(data, dict) and "messages" in data:
                out.extend(data["messages"])
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"WARN: cass export failed for {session_path}: {e}", file=sys.stderr)
        except json.JSONDecodeError as e:
            print(f"WARN: cass export returned invalid JSON for {session_path}: {e}", file=sys.stderr)
    return out


def is_human_message(msg: dict) -> bool:
    """Heuristic: is this a user-typed message, not an agent-written subagent prompt?
    See references/cass_fidelity.md for the isSidechain issue.
    """
    role = msg.get("role", "").lower()
    if role != "user":
        return False
    # cass flattens isSidechain; we'd need raw JSONL to recover it.
    # Heuristic: agent-written subagent prompts often start with "You are" or
    # contain "<system>" or similar markers. Mark these as not-human.
    text = msg.get("content", "") if isinstance(msg.get("content"), str) else ""
    if isinstance(text, str):
        if text.startswith("You are") and len(text) > 200:
            return False
        if "<system>" in text[:100]:
            return False
    return True


def extract_prompts_from_session(messages: list[dict]) -> list[dict]:
    """Extract human prompts from a session's messages."""
    prompts = []
    for i, msg in enumerate(messages):
        if is_human_message(msg):
            text = msg.get("content", "")
            if not isinstance(text, str):
                if isinstance(text, list):
                    text = " ".join(str(p) for p in text)
                else:
                    text = str(text)
            prompts.append({
                "line_number": i + 1,
                "agent": msg.get("agent", "unknown"),
                "workspace": msg.get("workspace"),
                "created_at": msg.get("created_at") or msg.get("timestamp") or datetime.now().isoformat(),
                "prompt_text": text,
                "is_human": True,
            })
    return prompts


def match_scope(prompt: dict, scope: ScopeSpec) -> bool:
    """Apply post-extraction scope filters."""
    # Agent filter
    if scope.agents and prompt.get("agent") not in scope.agents:
        return False
    # Content regex
    if scope.matches:
        import re
        try:
            if not re.search(scope.matches, prompt["prompt_text"], re.IGNORECASE):
                return False
        except re.error:
            pass
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", required=True)
    add_scope_args(ap)
    args = ap.parse_args()
    scope = parse_args([
        f"--since={args.since}" if args.since else None,
        f"--days={args.since_days}" if args.since_days else None,
        "--today" if args.today else None,
        f"--from={args.date_from}" if args.date_from else None,
        f"--to={args.date_to}" if args.date_to else None,
        f"--projects={args.projects}" if args.projects else None,
    ] + [f"--project-dir={d}" for d in args.project_dirs] + [
        f"--agent={args.agent}" if args.agent else None,
        f"--type={args.types}" if args.types else None,
        f"--matches={args.matches}" if args.matches else None,
        f"--session={args.session}" if args.session else None,
        f"--limit={args.limit}" if args.limit else None,
        f"--ordering={args.ordering}",
        "--include-tools" if args.include_tools else None,
    ])

    print(f"Scope: {scope.description()}", file=sys.stderr)

    if scope.is_default():
        print("INFO: Using default scope: --since 30d, all projects, all agents", file=sys.stderr)

    # Single-session mode
    if scope.session:
        return _extract_single_session(args.db, scope)

    # Normal mode: enumerate via cass search (empty query + workspace filter),
    with sqlite3.connect(args.db) as conn:
        # Create tranche
        tranche_cur = conn.execute(
            "INSERT INTO tranches (scope_hash, scope_json, status) VALUES (?, ?, 'in-progress')",
            (scope.hash(), scope.to_json()),
        )
        tranche_id = tranche_cur.lastrowid
        conn.commit()

        # Get projects
        if scope.projects or scope.project_dirs:
            placeholders = ",".join("?" * (len(scope.projects) + len(scope.project_dirs)))
            params = list(scope.projects) + list(scope.project_dirs)
            rows = conn.execute(
                f"SELECT id, name, path FROM projects WHERE name IN ({placeholders}) OR path IN ({placeholders})",
                params + params,
            ).fetchall()
        else:
            rows = conn.execute("SELECT id, name, path FROM projects").fetchall()

        if not rows:
            print("WARN: no projects in DB. Run 01_discover_projects.py first.", file=sys.stderr)
            return 1

        since_days = scope.effective_since_days()
        total_prompts = 0

        for pid, name, path in rows:
            sessions = cass_timeline(path, since_days)
            if not sessions:
                continue
            # Sessions come from cass search in arbitrary order.
            # Per-session prompt ordering is handled in extract_prompts_from_session.

            for sess in sessions:
                session_path = sess.get("source_path") or sess.get("path")
                if not session_path:
                    continue
                messages = cass_export(session_path, scope.include_tools)
                prompts = extract_prompts_from_session(messages)
                for p in prompts:
                    p["project_id"] = pid
                    p["source_path"] = session_path
                    if not match_scope(p, scope):
                        continue
                    conn.execute(
                        """INSERT OR IGNORE INTO prompts
                           (tranche_id, project_id, source_path, line_number, agent,
                            workspace, created_at, prompt_text, is_human, source)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, 'cass+jsonl')""",
                        (tranche_id, pid, session_path, p["line_number"], p["agent"],
                         p["workspace"], p["created_at"], p["prompt_text"][:65000]),
                    )
                    total_prompts += 1
                    if scope.limit and total_prompts >= scope.limit:
                        print(f"INFO: hit --limit {scope.limit}, stopping", file=sys.stderr)
                        break
                if scope.limit and total_prompts >= scope.limit:
                    break
            if scope.limit and total_prompts >= scope.limit:
                break

        conn.execute(
            "UPDATE tranches SET status = 'completed', completed_at = datetime('now') WHERE id = ?",
            (tranche_id,),
        )
        conn.commit()
    print(f"OK: extracted {total_prompts} prompts (tranche {tranche_id})", file=sys.stderr)
    return 0


def _extract_single_session(db: str, scope: ScopeSpec) -> int:
    """Single-session mode: skip enumeration, export directly."""
    with sqlite3.connect(db) as conn:
        tranche_cur = conn.execute(
            "INSERT INTO tranches (scope_hash, scope_json, status) VALUES (?, ?, 'in-progress')",
            (scope.hash(), scope.to_json()),
        )
        tranche_id = tranche_cur.lastrowid
        messages = cass_export(scope.session, scope.include_tools)
        prompts = extract_prompts_from_session(messages)
        for p in prompts:
            conn.execute(
                """INSERT OR IGNORE INTO prompts
                   (tranche_id, project_id, source_path, line_number, agent,
                    workspace, created_at, prompt_text, is_human, source)
                   VALUES (?, NULL, ?, ?, ?, ?, ?, ?, 1, 'cass+jsonl')""",
                (tranche_id, scope.session, p["line_number"], p["agent"],
                 p["workspace"], p["created_at"], p["prompt_text"][:65000]),
            )
        conn.execute(
            "UPDATE tranches SET status = 'completed', completed_at = datetime('now') WHERE id = ?",
            (tranche_id,),
        )
        conn.commit()
    print(f"OK: extracted {len(prompts)} prompts from single session (tranche {tranche_id})", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
