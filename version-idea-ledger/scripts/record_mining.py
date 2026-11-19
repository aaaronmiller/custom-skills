#!/usr/bin/env python3
"""Record which files a reader mined, so a rerun does not mine them again.

Usage:
  python3 -I -B record_mining.py --ledger DOSSIER/ledgers/file-ledger.jsonl \
      --coverage coverage-<slice>.jsonl [--coverage ...] [--date YYYY-MM-DD]

Each coverage row is {"path": ABS, "status": "mined" | "no-ideas", "note": "..."} and is
written by the reader beside its ideas file. The file ledger row gets ideas_status, mined
(date) and mined_sha256 (the hash that was read). A path not in the ledger is an error:
run inventory.py first. A file whose hash changed after it was read goes back to pending
on the next inventory run, because mined_sha256 no longer matches.
"""
import argparse
import datetime as dt
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import read_jsonl, write_jsonl  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--coverage", action="append", required=True)
    ap.add_argument("--date", default=dt.date.today().isoformat())
    a = ap.parse_args()
    rows = read_jsonl(a.ledger)
    by_path = {r["path"]: r for r in rows}
    errors, n = [], 0
    for cov in a.coverage:
        for c in read_jsonl(cov):
            path = os.path.abspath(os.path.expanduser(c.get("path", "")))
            if path not in by_path:
                errors.append(f"{cov}: not in file ledger: {path}")
                continue
            if c.get("status") not in ("mined", "no-ideas"):
                errors.append(f"{cov}: bad status for {path}: {c.get('status')}")
                continue
            row = by_path[path]
            row.update({"ideas_status": c["status"], "mined": a.date, "mined_sha256": row["sha256"]})
            if c.get("note"):
                row["mining_note"] = c["note"]
            n += 1
    if errors:
        print("\n".join(errors), file=sys.stderr)
        raise SystemExit(1)
    write_jsonl(a.ledger, rows)
    print(f"recorded {n} files")


if __name__ == "__main__":
    main()
