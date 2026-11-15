#!/usr/bin/env python3
"""Initialize the intent-archaeology SQLite state DB. Idempotent.

Usage:
    python scripts/init_db.py --db ~/.intent-archaeology/state.db
"""
from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

SCHEMA_PATH = Path(__file__).parent / "lib" / "schema.sql"


def init(db_path: str, *, force: bool = False) -> None:
    p = Path(db_path).expanduser()
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists() and force:
        p.unlink()
    schema = SCHEMA_PATH.read_text()
    with sqlite3.connect(str(p)) as conn:
        conn.executescript(schema)
        conn.commit()
    print(f"OK: initialized {p}", file=sys.stderr)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", required=True, help="Path to SQLite DB file")
    ap.add_argument("--force", action="store_true", help="Drop and recreate (destructive)")
    args = ap.parse_args()
    init(args.db, force=args.force)
    return 0


if __name__ == "__main__":
    sys.exit(main())
