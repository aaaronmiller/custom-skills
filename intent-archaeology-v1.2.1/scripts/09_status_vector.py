#!/usr/bin/env python3
"""Phase 8b: emit status vectors per project as standalone JSON + optional beads.

Usage:
    python scripts/09_status_vector.py --db ~/.intent-archaeology/state.db
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib.metric_vector import COMPONENTS, ANTI_METRICS, assert_no_anti_metric


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", required=True)
    ap.add_argument("--out", default="~/.intent-archaeology/status_vectors.json")
    ap.add_argument("--write-beads", action="store_true", help="Also write to beads CLI if installed")
    args = ap.parse_args()

    with sqlite3.connect(args.db) as conn:
        rows = conn.execute(
            f"""SELECT p.name, p.lifecycle, sv.{", sv.".join(COMPONENTS)}
                FROM status_vectors sv
                JOIN projects p ON sv.project_id = p.id
                ORDER BY p.name""",
        ).fetchall()

    vectors = []
    for row in rows:
        name = row[0]
        lifecycle = row[1]
        comps = dict(zip(COMPONENTS, row[2:]))
        # Anti-metric check
        assert_no_anti_metric(comps)
        vectors.append({
            "project": name,
            "lifecycle": lifecycle,
            "status_vector": comps,
        })

    out_path = Path(args.out).expanduser()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(vectors, indent=2))
    print(f"OK: {len(vectors)} status vectors written to {out_path}", file=sys.stderr)

    # Print summary
    for v in vectors:
        comps = v["status_vector"]
        nonzero = {k: f"{v:.2f}" for k, v in comps.items() if v > 0}
        print(f"  {v['project']:20s} [{v['lifecycle']:18s}] {nonzero}", file=sys.stderr)

    # Optional: write to beads
    if args.write_beads:
        try:
            for v in vectors:
                subprocess.run(
                    ["beads", "add", "--priority", "medium" if v["lifecycle"] == "in-progress" else "low",
                     "--title", f"[{v['project']}] status: {v['status_vector']}"],
                    check=False,
                )
            print(f"OK: wrote {len(vectors)} beads", file=sys.stderr)
        except FileNotFoundError:
            print("WARN: beads CLI not installed, skipping --write-beads", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
