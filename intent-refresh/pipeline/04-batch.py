#!/usr/bin/env python3
"""Phase 4: emit a classification batch.

Budget is items, not tokens. The input is prefiltered to human turns, so the
token ceiling almost never binds; what binds is how many mutually similar
items a model can hold in useful relation at once.

Two deliberate choices that look wrong and are not:

  Newest first.  Reverse-chronological order makes the merge monotonic, so a
  run stopped early is still correct with a known cutoff.

  Not chronological within a batch.  Coherent input degrades attention more
  than shuffled input, and this corpus is already maximally homogeneous.
  Items are interleaved across sessions so neighbours are less confusable.
  Do not reorder them.

Crash-terminated sessions are upweighted, not filtered. They are labelled
incompleteness pointing at a specific file.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib.common import (  # noqa: E402
    BATCHES, PIPELINE_VERSION, connect, die, log, now, report, sha,
)

MIN_CHARS = 12


def interleave(rows: list) -> list:
    """Round-robin across sessions so adjacent items come from different contexts."""
    buckets: dict[str, list] = {}
    for r in rows:
        buckets.setdefault(r["session_id"], []).append(r)
    order = sorted(buckets, key=lambda k: -len(buckets[k]))
    out, i = [], 0
    while any(buckets[k] for k in order):
        k = order[i % len(order)]
        if buckets[k]:
            out.append(buckets[k].pop(0))
        i += 1
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Phase 4: emit a classification batch")
    ap.add_argument("--project", required=True, help="project slug")
    ap.add_argument("--items", type=int, default=60,
                    help="item cap per batch (calibrate this, do not guess)")
    ap.add_argument("--tranche", type=int, default=1)
    ap.add_argument("--out", help="output path (default: batches/<project>-<n>.json)")
    args = ap.parse_args()

    conn = connect()
    proj = conn.execute("SELECT id,path,description FROM project WHERE id=?",
                        (args.project,)).fetchone()
    if not proj:
        near = conn.execute(
            "SELECT id FROM project WHERE id LIKE ? LIMIT 10", (f"%{args.project}%",)
        ).fetchall()
        die(f"unknown project '{args.project}'. Close matches: "
            + (", ".join(r["id"] for r in near) or "none"))

    rows = conn.execute(
        """SELECT e.id, e.session_id, e.ts, e.text, e.git_branch, e.slash_command,
                  e.slash_args, s.crashed, s.harness
             FROM event e JOIN session s ON s.id = e.session_id
            WHERE e.project_id = ? AND e.is_human = 1
              AND e.text IS NOT NULL AND LENGTH(e.text) >= ?
              AND e.id NOT IN (SELECT event_id FROM batch_item)
            ORDER BY s.crashed DESC, e.ts DESC""",
        (args.project, MIN_CHARS),
    ).fetchall()

    if not rows:
        print(f"No unbatched human turns for {args.project}.")
        print("Either the project is fully batched, or phase 3 has not enriched its sessions.")
        return 0

    selected = interleave(rows[: args.items * 3])[: args.items]

    bid = "batch_" + sha(args.project, str(args.tranche), now())
    items = []
    for r in selected:
        items.append({
            "id": r["id"],
            "ts": r["ts"],
            "harness": r["harness"],
            "branch": r["git_branch"],
            "slash_command": r["slash_command"],
            "session_ended_mid_tool_call": bool(r["crashed"]),
            "text": r["text"],
        })

    out = Path(args.out) if args.out else BATCHES / f"{args.project}-{args.tranche}-{bid[-6:]}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "batch_id": bid,
        "project": args.project,
        "project_path": proj["path"],
        "tranche": args.tranche,
        "pipeline_version": PIPELINE_VERSION,
        "instructions": (
            "Read references/taxonomy.md before classifying. Emit one verdict per item. "
            "EVERY id below must appear in your output; a turn carrying no intent gets "
            "{\"id\": \"...\", \"type\": \"noise\"}. Never emit a non-noise verdict without "
            "a verbatim span quoted from that item's text. Do not reorder the items."
        ),
        "verdict_schema": {
            "id": "string, required, must match an item id",
            "type": "string, required, one of the taxonomy types or 'noise'",
            "statement": "string, required unless noise. Normalized imperative.",
            "verbatim": "string, required unless noise. Quoted from the item text.",
            "scope": "one of global|project|feature|file",
            "confidence": "0.0 to 1.0",
        },
        "items": items,
    }, indent=2))

    conn.execute(
        "INSERT INTO batch (id,project_id,tranche,item_count,emitted_at,ids_submitted,"
        "pipeline_version) VALUES (?,?,?,?,?,?,?)",
        (bid, args.project, args.tranche, len(items), now(), len(items), PIPELINE_VERSION),
    )
    conn.executemany(
        "INSERT OR IGNORE INTO batch_item (batch_id,event_id) VALUES (?,?)",
        [(bid, it["id"]) for it in items],
    )
    conn.commit()
    log(conn, "batch", "emitted", f"{bid} {len(items)} items")

    remaining = len(rows) - len(selected)
    report("Batch emitted", [
        ("batch id", bid),
        ("items", len(items)),
        ("from crashed sessions", sum(1 for i in items if i["session_ended_mid_tool_call"])),
        ("remaining unbatched", remaining),
        ("file", str(out)),
    ])
    print("\nNow: read references/taxonomy.md, classify the items, write verdicts to a")
    print("JSON file (a list of verdict objects), then run:")
    print(f"  python3 scripts/05-merge.py --verdicts <file> --batch {bid}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
