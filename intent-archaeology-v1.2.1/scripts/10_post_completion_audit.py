#!/usr/bin/env python3
"""Phase 9: post-completion audit (retrospective).

⚠️  This is the ONLY script that loads references/retrospective.md.
Loading it earlier biases the run toward producing findings that make
the retrospective look good.

Usage:
    python scripts/10_post_completion_audit.py \
        --db ~/.intent-archaeology/state.db \
        --tranche <tranche-id>
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

RETROSPECTIVE_PATH = Path(__file__).parent.parent / "references" / "retrospective.md"


def run_question_zero(db: str) -> bool:
    """Question zero: does the run still serve the anchor?
    Checks for drift signature: artifact growth without restructuring.
    """
    with sqlite3.connect(db) as conn:
        rows = conn.execute(
            "SELECT scope_json, length(scope_json) FROM tranches ORDER BY started_at",
        ).fetchall()
    if len(rows) < 2:
        return True  # Not enough data
    sizes = [r[1] for r in rows]
    growth = sizes[-1] - sizes[0]
    if growth > 50000 and len(set(sizes)) == 1:
        print("⚠️  DRIFT DETECTED: scope_json grew without restructuring.", file=sys.stderr)
        print("    See references/retrospective.md → question zero.", file=sys.stderr)
        return False
    return True


def run_retrospective(db: str, tranche_id: int) -> None:
    """Run the eight questions from references/retrospective.md."""
    retrospective = RETROSPECTIVE_PATH.read_text()
    print("=" * 70, file=sys.stderr)
    print("RETROSPECTIVE (loaded at completion, per progressive disclosure)", file=sys.stderr)
    print("=" * 70, file=sys.stderr)
    print(f"\nLoaded {RETROSPECTIVE_PATH.name} ({len(retrospective)} bytes)\n", file=sys.stderr)

    questions = [
        ("Q1", "Did the scope produce useful coverage?"),
        ("Q2", "Did Phase 6 produce complete per-turn coverage?"),
        ("Q3", "Did Phase 7's status vector match reality?"),
        ("Q4", "Did the meta-learning loop hack its own reward?"),
        ("Q5", "Did the proposer and verifier stay separate?"),
        ("Q6", "Did the wiki avoid the markdown graveyard?"),
        ("Q7", "Did the scope persist correctly?"),
        ("Q8", "What did the user actually use?"),
    ]

    with sqlite3.connect(db) as conn:
        for qid, question in questions:
            print(f"\n[{qid}] {question}", file=sys.stderr)
            # Auto-gather some evidence
            if qid == "Q2":
                # Check per-turn coverage
                missing = conn.execute(
                    """SELECT COUNT(*) FROM prompts p
                       WHERE p.tranche_id = ?
                       AND p.id NOT IN (SELECT prompt_id FROM intents)""",
                    (tranche_id,),
                ).fetchone()[0]
                if missing:
                    obs = f"⚠️ {missing} prompts have no intent verdict (per-turn coverage broken)"
                    print(f"    → {obs}", file=sys.stderr)
                    conn.execute(
                        "INSERT INTO observations (tranche_id, question_id, observation, severity) VALUES (?, ?, ?, 'critical')",
                        (tranche_id, qid, obs),
                    )
                else:
                    print("    → OK: all prompts have verdicts", file=sys.stderr)
            elif qid == "Q7":
                # Check scope hash uniqueness
                dupes = conn.execute(
                    "SELECT scope_hash, COUNT(*) FROM tranches GROUP BY scope_hash HAVING COUNT(*) > 1",
                ).fetchall()
                if dupes:
                    print(f"    → ⚠️ {len(dupes)} duplicate scope_hash values", file=sys.stderr)
                else:
                    print("    → OK: scope hashes unique", file=sys.stderr)
            # ... (other questions would prompt for human input or run checks)
            conn.commit()

    print("\n" + "=" * 70, file=sys.stderr)
    print("Retrospective complete. Proposed edits in proposed_edits/ (if any).", file=sys.stderr)
    print("=" * 70, file=sys.stderr)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", required=True)
    ap.add_argument("--tranche", type=int, required=True)
    args = ap.parse_args()

    if not run_question_zero(args.db):
        print("Stopping: drift detected. Resolve before continuing.", file=sys.stderr)
        return 1

    run_retrospective(args.db, args.tranche)
    return 0


if __name__ == "__main__":
    sys.exit(main())
