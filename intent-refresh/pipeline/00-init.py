#!/usr/bin/env python3
"""Phase 0: create the database and check the environment."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib.common import (  # noqa: E402
    BASE, BATCHES, DB_PATH, DEFAULT_ROOTS, DERIVED, HUMAN, PIPELINE_VERSION,
    have, init_db, log, report, run,
)


def main() -> int:
    conn = init_db()
    log(conn, "init", "done", PIPELINE_VERSION)

    rows = []
    for tool, required in (("cass", False), ("git", True), ("jq", False), ("sqlite3", False)):
        ok = have(tool)
        note = "ok" if ok else ("MISSING (required)" if required else "missing (optional)")
        if tool == "cass" and ok:
            code, out, _ = run(["cass", "health", "--json"], timeout=30)
            note = "ok, index healthy" if code == 0 else "installed, index not ready: run cass index --full"
        rows.append((tool, note))
    report("Environment", rows)

    report("Paths", [
        ("database", str(DB_PATH)),
        ("derived (rebuildable)", str(DERIVED)),
        ("human (never written by scripts)", str(HUMAN)),
        ("batches", str(BATCHES)),
    ])

    report("Scan roots", [(str(r), "found" if r.is_dir() else "MISSING") for r in DEFAULT_ROOTS])

    if not have("git"):
        print("\ngit is required for attribution. Install it before phase 2.")
        return 1

    print(f"\nInitialized at pipeline version {PIPELINE_VERSION}.")
    print("Next: python3 scripts/01-inventory.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
