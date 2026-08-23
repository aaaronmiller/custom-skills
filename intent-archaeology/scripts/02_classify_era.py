#!/usr/bin/env python3
"""Phase 2: classify each project's document era (0..5).

See references/era_typology.md.

Usage:
    python scripts/02_classify_era.py --db ~/.intent-archaeology/state.db
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path


def classify_era(project_path: str) -> tuple[int, list[int]]:
    p = Path(project_path)
    markers = {
        5: any((p / f).exists() for f in ["LIVING.md"]) or any(p.glob("*.living.md")),
        4: (p / "requirements.md").exists() and (p / "design.md").exists() and any((p / f).exists() for f in ["plans.md", "plan.md"]),
        3: (p / "requirements.md").exists() and (p / "design.md").exists(),
        2: any((p / f).exists() for f in ["prd.md", "PRD.md"]) or any(p.glob("prd*.md")) or any(p.glob("PRD*.md")),
        1: any(p.glob("*.md")),
    }
    # Check era 5 frontmatter
    if markers[5]:
        living = p / "LIVING.md"
        if living.exists():
            text = living.read_text(errors="ignore")
            if "version:" in text.split("---")[1] if "---" in text else "":
                # Has frontmatter with version - check it's v3.x
                if 'version: "3' in text or "version: '3" in text or "version: 3" in text:
                    return 5, []
        # LIVING.md without v3 frontmatter: treat as era 4
        markers[5] = False
        markers[4] = True

    present = [era for era, found in markers.items() if found]
    if not present:
        return 0, []
    era = max(present)
    overlap = [e for e in present if e != era]
    return era, overlap


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", required=True)
    args = ap.parse_args()

    with sqlite3.connect(args.db) as conn:
        rows = conn.execute("SELECT id, path FROM projects").fetchall()
        for pid, path in rows:
            era, overlap = classify_era(path)
            conn.execute(
                "UPDATE projects SET era = ?, era_overlap = ?, updated_at = datetime('now') WHERE id = ?",
                (era, json.dumps(overlap), pid),
            )
            print(f"  project {pid}: era={era} overlap={overlap} {path}", file=sys.stderr)
        conn.commit()
    print(f"OK: classified {len(rows)} projects", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
