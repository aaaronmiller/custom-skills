#!/usr/bin/env python3
"""Phase 6a: emit a classification batch for the agent to label.

This script does not call a model. It selects candidate prompts, caps the
batch, interleaves it, and writes a JSON file. You classify that file. Then
`06b_merge_verdicts.py` merges the result with no model involved at all.

That fence exists for two reasons. Models asked to iteratively refine their
own accumulated output drift toward generic content, so the merge must be
deterministic. And a deterministic merge is the only kind you can rerun after
a crash without compounding earlier mistakes.

Two deliberate choices that look wrong and are not:

  Newest first. Reverse-chronological order makes the merge monotonic, so a
  run stopped early is a correct audit with a known cutoff rather than one
  asserting currency for material superseded in the unprocessed remainder.

  Not chronological within a batch. Coherent input degrades attention more
  than shuffled input, and one project's prompts are already maximally
  homogeneous. Items are interleaved across sessions so neighbours are less
  confusable. Do not reorder them.

Usage:
    python scripts/06_distill_intent.py --db ~/.intent-archaeology/state.db \\
        --out ~/.intent-archaeology/batches --items 60 --all
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

# Prompts under ~12 characters are approvals, typos, or single words. Longer
# filler is caught by the taxonomy's 'noise' verdict at classification time.
MIN_CHARS = 12

# 60 is a starting point, not a tuned value. The binding constraint is how many
# mutually similar items a model can hold in useful relation at once, which
# depends on prompting style and project vocabulary. Calibrate it: run
# 30 / 60 / 120 on a project you know well and watch the supersession-detection
# rate, not the extraction rate. Extraction stays accurate long after cross-item
# reasoning starts to slip, so measuring the wrong one produces confidence at
# exactly the wrong batch size.
DEFAULT_ITEMS = 60


def interleave(rows: list[dict]) -> list[dict]:
    """Round-robin across sessions so adjacent items come from different contexts."""
    buckets: dict[str, list[dict]] = {}
    for r in rows:
        key = str(r.get("session_path") or r.get("project_id"))
        buckets.setdefault(key, []).append(r)
    order = sorted(buckets, key=lambda k: -len(buckets[k]))
    out: list[dict] = []
    i = 0
    while any(buckets[k] for k in order):
        k = order[i % len(order)]
        if buckets[k]:
            out.append(buckets[k].pop(0))
        i += 1
    return out


def columns(conn: sqlite3.Connection, table: str) -> set[str]:
    return {r[1] for r in conn.execute(f"PRAGMA table_info({table})")}


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--db", required=True)
    ap.add_argument("--out", default="~/.intent-archaeology/batches",
                    help="directory to write batch files into")
    ap.add_argument("--items", type=int, default=DEFAULT_ITEMS,
                    help="item cap per batch. Calibrate; see the comment in this file.")
    ap.add_argument("--project", help="limit to one project id")
    ap.add_argument("--tranche", type=int, help="limit to one tranche_id")
    ap.add_argument("--all", action="store_true",
                    help="emit every remaining batch, not just the next one")
    args = ap.parse_args()

    out_dir = Path(args.out).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)

    db = Path(args.db).expanduser()
    if not db.exists():
        print(f"ERROR: no state database at {db}. Run init_db.py first.", file=sys.stderr)
        return 1
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row

    cols = columns(conn, "prompts")
    ts_col = next((c for c in ("created_at", "timestamp") if c in cols), "id")
    sess_col = "session_path" if "session_path" in cols else "NULL AS session_path"

    where = ["p.id NOT IN (SELECT prompt_id FROM intents)",
             f"LENGTH(p.prompt_text) >= {MIN_CHARS}"]
    params: list = []
    if args.project:
        where.append("p.project_id = ?")
        params.append(args.project)
    if args.tranche:
        where.append("p.tranche_id = ?")
        params.append(args.tranche)

    rows = [dict(r) for r in conn.execute(
        f"""SELECT p.id, p.tranche_id, p.project_id, p.prompt_text,
                   p.{ts_col} AS ts, {sess_col}
              FROM prompts p
             WHERE {' AND '.join(where)}
             ORDER BY p.{ts_col} DESC""", params).fetchall()]

    if not rows:
        print("No unbatched prompts. Either everything is classified, or Phase 5 "
              "has not run for this scope.", file=sys.stderr)
        return 0

    n_batches = (len(rows) + args.items - 1) // args.items if args.all else 1
    written: list[tuple[Path, int]] = []

    for b in range(n_batches):
        chunk = rows[b * args.items:(b + 1) * args.items]
        if not chunk:
            break
        chunk = interleave(chunk)
        stamp = datetime.now(timezone.utc).isoformat()
        bid = "batch_" + hashlib.sha256(
            f"{chunk[0]['id']}{stamp}{b}".encode()).hexdigest()[:12]

        payload = {
            "batch_id": bid,
            "project_id": args.project,
            "tranche_id": args.tranche,
            "emitted_at": stamp,
            "instructions": (
                "Read references/intent_taxonomy.md before classifying. Emit one "
                "verdict per item. EVERY id below must appear in your output; an "
                "item carrying no intent gets {\"id\": N, \"type\": \"noise\"}. Never "
                "emit a non-noise verdict without a verbatim span quoted from that "
                "item's own text. One item may carry several intents: emit several "
                "verdicts sharing its id. Do not reorder the items."
            ),
            "verdict_schema": {
                "id": "int, required, must match an item id",
                "type": "required, a type from intent_taxonomy.md or 'noise'",
                "summary": "required unless noise. Normalized imperative.",
                "verbatim": "required unless noise. Quoted from this item's own text.",
                "scope": "one of global|project|feature|file",
                "confidence": "0.0 to 1.0",
            },
            "items": [
                {"id": r["id"], "ts": r["ts"], "project_id": r["project_id"],
                 "text": r["prompt_text"]}
                for r in chunk
            ],
        }
        path = out_dir / f"{bid}.json"
        path.write_text(json.dumps(payload, indent=2))
        written.append((path, len(chunk)))

    for path, n in written:
        print(f"wrote {path}  ({n} items)", file=sys.stderr)
    emitted = sum(n for _, n in written)
    print(f"\n{emitted} items emitted, {len(rows) - emitted} still unbatched",
          file=sys.stderr)
    print("\nNext: read references/intent_taxonomy.md, classify each batch, write "
          "verdicts to JSON, then:", file=sys.stderr)
    print(f"  python scripts/06b_merge_verdicts.py --db {args.db} "
          f"--verdicts {out_dir}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
