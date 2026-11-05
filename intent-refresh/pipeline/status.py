#!/usr/bin/env python3
"""Where is the pipeline. Safe to run at any time."""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from lib.common import DB_PATH, connect, report  # noqa: E402


def main() -> int:
    if not DB_PATH.exists():
        print("Not initialized. Run: python3 scripts/00-init.py")
        return 1
    conn = connect()
    q = conn.execute

    proj = q("SELECT kind, COUNT(*) c FROM project GROUP BY kind").fetchall()
    report("Projects", [(r["kind"], r["c"]) for r in proj] or [("none", "run 01-inventory.py")])

    sess = q("SELECT COUNT(*) t, SUM(enriched) e FROM session").fetchone()
    rung = q("SELECT COUNT(*) c FROM session WHERE attribution_rung<=4").fetchone()["c"]
    total = sess["t"] or 0
    report("Sessions", [
        ("discovered", total),
        ("enriched", sess["e"] or 0),
        ("deterministically attributed", f"{rung}/{total}" +
         (f" ({100.0*rung/total:.0f}%)" if total else "")),
    ])

    ev = q("SELECT COUNT(*) t, SUM(is_human) h FROM event").fetchone()
    report("Events", [("total", ev["t"] or 0), ("human turns", ev["h"] or 0)])

    it = q("SELECT COUNT(*) t, SUM(CASE WHEN superseded_by IS NULL THEN 1 ELSE 0 END) a"
           " FROM intent").fetchone()
    types = q("SELECT type, COUNT(*) c FROM intent WHERE superseded_by IS NULL"
              " GROUP BY type ORDER BY c DESC").fetchall()
    report("Intents", [("total", it["t"] or 0), ("active", it["a"] or 0)]
           + [(f"  {r['type']}", r["c"]) for r in types])

    b = q("SELECT COUNT(*) t, SUM(CASE WHEN merged_at IS NULL THEN 1 ELSE 0 END) o"
          " FROM batch").fetchone()
    report("Batches", [("emitted", b["t"] or 0), ("awaiting merge", b["o"] or 0)])

    obs = q("SELECT kind, COUNT(*) c FROM observation GROUP BY kind ORDER BY c DESC").fetchall()
    if obs:
        report("Observations (append-only, no effect until a boundary)",
               [(r["kind"], r["c"]) for r in obs])

    if not proj:
        nxt = "python3 scripts/01-inventory.py"
    elif not total:
        nxt = "python3 scripts/02-attribute.py"
    elif (sess["e"] or 0) < total:
        nxt = "python3 scripts/03-enrich.py"
    elif b["o"]:
        nxt = "classify the open batch, then 05-merge.py"
    elif not (it["t"] or 0):
        nxt = "python3 scripts/04-batch.py --project <slug>"
    else:
        nxt = "python3 scripts/06-render.py, or another batch"
    print(f"\nNext: {nxt}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
