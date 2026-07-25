#!/usr/bin/env python3
"""Helper: cass selects, raw JSONL extracts.

Materializes the prompt_audit_fields table by going back to the raw
JSONL on disk for fields cass flattens away (isSidechain, gitBranch,
parentUuid, toolUseResult).

See references/cass_fidelity.md.

Usage:
    python scripts/cass_select.py --db ~/.intent-archaeology/state.db
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path


def read_jsonl_line(path: str, line_number: int) -> dict | None:
    """Read a specific 1-indexed line from a JSONL file."""
    p = Path(path)
    if not p.exists():
        return None
    try:
        with p.open() as f:
            for i, line in enumerate(f, 1):
                if i == line_number:
                    return json.loads(line)
    except (OSError, json.JSONDecodeError):
        return None
    return None


def enrich_prompt(conn: sqlite3.Connection, prompt_id: int, source_path: str, line_number: int) -> bool:
    """Read raw JSONL and populate prompt_audit_fields. Returns True on success."""
    msg = read_jsonl_line(source_path, line_number)
    if msg is None:
        # Mark as cass-only
        conn.execute(
            """INSERT OR REPLACE INTO prompt_audit_fields
               (prompt_id, source_path, line_number, is_sidechain, git_branch, parent_uuid, tool_use_result_json)
               VALUES (?, ?, ?, 0, NULL, NULL, NULL)""",
            (prompt_id, source_path, line_number),
        )
        return False

    is_sidechain = bool(msg.get("isSidechain", False))
    git_branch = msg.get("gitBranch")
    parent_uuid = msg.get("parentUuid")
    tool_use_result = msg.get("toolUseResult")
    tool_use_result_json = json.dumps(tool_use_result) if tool_use_result else None

    conn.execute(
        """INSERT OR REPLACE INTO prompt_audit_fields
           (prompt_id, source_path, line_number, is_sidechain, git_branch, parent_uuid, tool_use_result_json)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (prompt_id, source_path, line_number, is_sidechain, git_branch, parent_uuid, tool_use_result_json),
    )
    # If is_sidechain, mark the prompt as not human (it was an agent-written subagent prompt)
    if is_sidechain:
        conn.execute(
            "UPDATE prompts SET is_human = 0 WHERE id = ?",
            (prompt_id,),
        )
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", required=True)
    ap.add_argument("--tranche", type=int, help="Limit to a specific tranche_id")
    args = ap.parse_args()

    with sqlite3.connect(args.db) as conn:
        where = "WHERE source = 'cass+jsonl'"
        if args.tranche:
            where += f" AND tranche_id = {args.tranche}"
        rows = conn.execute(
            f"SELECT id, source_path, line_number FROM prompts {where}",
        ).fetchall()
        enriched = 0
        degraded = 0
        for pid, sp, ln in rows:
            if enrich_prompt(conn, pid, sp, ln):
                enriched += 1
            else:
                degraded += 1
                conn.execute(
                    "UPDATE prompts SET source = 'cass-only' WHERE id = ?",
                    (pid,),
                )
        conn.commit()
    print(f"OK: enriched={enriched} degraded(cass-only)={degraded}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
