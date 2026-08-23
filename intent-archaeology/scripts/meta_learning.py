#!/usr/bin/env python3
"""Meta-learning loop: append observations during tranche, propose edits
at boundaries, accept only if held-out score improves without regressing
any metric vector component.

Two timescales:
  - Observe continuously (append-only during tranche, zero effect on run)
  - Change discretely (edits proposed only at boundaries)

Three-tranche rule: merge-logic edits untouchable until three consecutive
tranches show no prompt-level gain.

Usage:
    python scripts/meta_learning.py --db ~/.intent-archaeology/state.db \
        --mode observe --tranche <id> --question Q1 --observation "..."
    python scripts/meta_learning.py --db ~/.intent-archaeology/state.db \
        --mode propose --tranche <id>
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path


def observe(db: str, tranche: int, question: str, observation: str, severity: str = "info") -> None:
    with sqlite3.connect(db) as conn:
        conn.execute(
            "INSERT INTO observations (tranche_id, question_id, observation, severity) VALUES (?, ?, ?, ?)",
            (tranche, question, observation, severity),
        )
        conn.commit()
    print(f"OK: observation recorded for {question}", file=sys.stderr)


def propose_edits(db: str, tranche: int) -> None:
    """Propose edits based on observations. Acceptance requires held-out eval."""
    with sqlite3.connect(db) as conn:
        obs = conn.execute(
            "SELECT question_id, observation, severity FROM observations WHERE tranche_id = ?",
            (tranche,),
        ).fetchall()

    if not obs:
        print("No observations for this tranche.", file=sys.stderr)
        return

    # Group by question
    by_q = {}
    for qid, o, sev in obs:
        by_q.setdefault(qid, []).append((o, sev))

    print(f"Proposing edits based on {len(obs)} observations:", file=sys.stderr)
    for qid, items in by_q.items():
        print(f"\n[{qid}] {len(items)} observation(s):", file=sys.stderr)
        for o, sev in items:
            print(f"  ({sev}) {o}", file=sys.stderr)

    # Check three-tranche rule for merge-logic edits
    with sqlite3.connect(db) as conn:
        recent = conn.execute(
            """SELECT DISTINCT tranche_id FROM observations
               WHERE tranche_id <= ? ORDER BY tranche_id DESC LIMIT 4""",
            (tranche,),
        ).fetchall()
        if len(recent) >= 4:
            print("\n⚠️  Three-tranche rule: merge-logic edits may be eligible.", file=sys.stderr)
            print("    Verify three consecutive tranches show no prompt-level gain first.", file=sys.stderr)

    print("\nNext step: run held-out eval (references/eval_protocol.md).", file=sys.stderr)
    print("Accept edits only if score improves without regressing any metric vector component.", file=sys.stderr)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", required=True)
    ap.add_argument("--mode", choices=["observe", "propose"], required=True)
    ap.add_argument("--tranche", type=int, required=True)
    ap.add_argument("--question", help="Question ID (e.g. Q1) for observe mode")
    ap.add_argument("--observation", help="Observation text for observe mode")
    ap.add_argument("--severity", default="info", choices=["info", "warning", "critical"])
    args = ap.parse_args()

    if args.mode == "observe":
        if not args.question or not args.observation:
            print("ERROR: --question and --observation required for observe mode", file=sys.stderr)
            return 1
        observe(args.db, args.tranche, args.question, args.observation, args.severity)
    else:
        propose_edits(args.db, args.tranche)
    return 0


if __name__ == "__main__":
    sys.exit(main())
