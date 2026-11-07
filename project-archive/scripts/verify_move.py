#!/usr/bin/env python3
"""Verify a folder move after a human ran it (read-only).

Usage:
  python3 -I verify_move.py --staging DIR [--json OUT]

Checks, against DIR/readiness.json and DIR/manifest.json written by plan.py:
  1. the destination exists and is a real directory;
  2. the old path is a link that resolves to the destination;
  3. the tree digest of the destination equals the manifest digest
     (every byte, every link target, every executable bit);
  4. for a Git repository: HEAD, branch, `git status --porcelain`,
     `git stash list` and the hash of every changed path's content are unchanged.
Exit 0 when all pass, 1 otherwise. Any failure means: run that row's rollback
(printed by move_dryrun.py) and log it.
"""
import argparse
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import _lib as L  # noqa: E402


def verify(staging):
    r = L.read_json(os.path.join(staging, "readiness.json"))
    m = L.read_json(os.path.join(staging, "manifest.json"))
    src, dest = r["source"], r["dest"]
    checks = []

    def c(name, ok, detail=""):
        checks.append({"check": name, "ok": bool(ok), "detail": detail})

    c("destination exists", os.path.isdir(dest) and not os.path.islink(dest), dest)
    c("old-path link resolves to destination", os.path.islink(src) and os.path.realpath(src) == os.path.realpath(dest),
      os.readlink(src) if os.path.islink(src) else "no link at old path")
    if os.path.isdir(dest):
        d = L.tree_digest(dest)
        c("same bytes as the manifest", d == m["tree_digest"], "%s vs %s" % (d[:12], m["tree_digest"][:12]))
        if m["git"].get("is_repo_root"):
            before = L.git_state(m["git"])
            after = L.git_state(L.git_facts(dest))
            diff = [k for k in before if before[k] != after.get(k)]
            c("Git HEAD, branch, status, stash and diff unchanged", not diff, ", ".join(diff))
    return {"source": src, "dest": dest, "checks": checks, "passed": all(x["ok"] for x in checks), "checked_at": L.now_iso()}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--staging", required=True)
    ap.add_argument("--json")
    a = ap.parse_args()
    res = verify(os.path.abspath(a.staging))
    if a.json:
        L.write_json(a.json, res)
    for x in res["checks"]:
        print("%s  %s  %s" % ("ok  " if x["ok"] else "FAIL", x["check"], x["detail"]))
    print("verified" if res["passed"] else "NOT verified: run the rollback for this row and log it")
    sys.exit(0 if res["passed"] else 1)


if __name__ == "__main__":
    main()
