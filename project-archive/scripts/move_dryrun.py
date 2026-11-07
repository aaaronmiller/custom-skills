#!/usr/bin/env python3
"""Dry-run mover: check the gate for one planned move and print the commands. Never executes them.

Usage:
  python3 -I move_dryrun.py --staging DIR [--recent-minutes 60]

Reads DIR/readiness.json and the seven artifacts written by plan.py, and
refuses (exit 2, "REFUSED (never-class)") when any of these hold:
  - there is no readiness record, or it lists blockers;
  - there is no operator approval naming this exact source and destination;
  - any of the seven artifacts is missing, or its bytes changed since plan.py
    hashed it, or it was written after the readiness record;
  - the sandbox test did not pass;
  - the live-use guard, re-run now, finds recent changes or a process inside;
  - the destination now exists, or source and destination are on different
    filesystems (mv would copy and then delete the source).

When everything holds it prints, and only prints, the commands a human runs:
metadata backups, the move, the old-path link, worktree repair, consumer
rewrites, post-move verification and the per-row rollback. Exit 0.
This program contains no call that moves, renames, links or deletes anything.
"""
import argparse
import os
import shlex
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import _lib as L  # noqa: E402
import plan as P  # noqa: E402

q = shlex.quote


def nearest_existing(p):
    while not os.path.exists(p):
        p = os.path.dirname(p)
    return p


def check(staging, minutes):
    reasons = []
    rp = os.path.join(staging, "readiness.json")
    if not os.path.isfile(rp):
        return None, ["no readiness record at %s; run plan.py first" % rp]
    r = L.read_json(rp)
    reasons += r.get("blockers", [])
    appr = r.get("approval", {})
    if not appr.get("present") or not appr.get("matches_exact_move"):
        if not any("approval" in b for b in reasons):
            reasons.append("no operator approval for this exact move: folder moves are never-class")
    for key, name in P.ARTIFACTS:
        rec = r.get("artifacts", {}).get(key)
        p = os.path.join(staging, name)
        if not rec or not os.path.isfile(p):
            reasons.append("artifact %s is missing" % key)
            continue
        if L.sha256_file(p) != rec["sha256"]:
            reasons.append("artifact %s changed after it was recorded" % key)
        if rec.get("written_at", "") > r.get("written_at", ""):
            reasons.append("artifact %s was written after the readiness record" % key)
    sb = os.path.join(staging, "sandbox-test.json")
    if os.path.isfile(sb) and not L.read_json(sb).get("passed"):
        if not any("sandbox" in b for b in reasons):
            reasons.append("sandbox test did not pass")
    src, dest = r["source"], r["dest"]
    if not os.path.isdir(src) or os.path.islink(src):
        reasons.append("source %s is not a real directory now" % src)
    else:
        g = P.live_use_guard(src, minutes)
        if not g["passed"]:
            reasons.append("live-use guard now: %d recent files, %d processes inside; defer this row" % (g["recent_files_count"], len(g["processes"])))
        if os.lstat(os.path.dirname(src)).st_dev != os.stat(nearest_existing(os.path.dirname(dest))).st_dev:
            reasons.append("source and destination are on different filesystems; mv would delete the source after copying")
    if os.path.lexists(dest):
        reasons.append("destination %s exists now" % dest)
    return r, sorted(set(reasons))


def commands(r, staging):
    src, dest = r["source"], r["dest"]
    load = lambda n: L.read_json(os.path.join(staging, n))  # noqa: E731
    pm, links, repair = load("path-map.json"), load("old-path-links.json"), load("working-copy-repair.json")
    out = ["# DRY RUN. Nothing below has been executed. A human runs these by hand after review.",
           "# Source: %s" % src, "# Destination: %s" % dest, "", "# 1. Pre-checks",
           "test ! -e %s" % q(dest), "test -d %s" % q(src), "mkdir -p -- %s" % q(os.path.dirname(dest))]
    if repair.get("backups"):
        out += ["", "# 2. Back up the Git metadata the repair will change"]
        bdir = os.path.join(staging, "metadata-backup")
        out.append("mkdir -p -- %s" % q(bdir))
        for i, b in enumerate(repair["backups"]):
            out.append("cp -p -- %s %s" % (q(b["file"]), q(os.path.join(bdir, "%02d-%s" % (i, os.path.basename(b["file"]))))))
    out += ["", "# 3. Move (same filesystem, plain mv, nothing deleted)", "mv -- %s %s" % (q(src), q(dest))]
    out += ["", "# 4. Old-path link"]
    for l in links["links"]:
        out.append(l["command"] if l["method"] != "symlink" else "ln -s -- %s %s" % (q(l["points_to"]), q(l["at"])))
    if repair.get("commands"):
        out += ["", "# 5. Working-copy repair"] + repair["commands"]
    if pm.get("relinks") or pm.get("rewrites"):
        out += ["", "# 6. Consumers to repoint (old paths keep working through the link meanwhile)"]
        for x in pm.get("relinks", []):
            out.append("ln -sfn -- %s %s" % (q(x["new_target"]), q(x["link"])))
        for x in pm.get("rewrites", []):
            out.append("#   edit %s line %s: %s -> %s" % (x["file"], x["line"], x["old"], x["new"]))
    here = os.path.dirname(os.path.realpath(__file__))
    out += ["", "# 7. Post-move verification (target exists, old-path link resolves, same HEAD, same status, same bytes)",
            "python3 -I %s --staging %s" % (q(os.path.join(here, "verify_move.py")), q(staging)),
            "", "# 8. Rollback for this row, if any check fails",
            "unlink -- %s   # removes only the link" % q(src), "mv -- %s %s" % (q(dest), q(src))]
    if repair.get("commands"):
        out.append("git -C %s worktree repair" % q(src))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--staging", required=True)
    ap.add_argument("--recent-minutes", type=int, default=60)
    a = ap.parse_args()
    staging = os.path.abspath(a.staging)
    r, reasons = check(staging, a.recent_minutes)
    if reasons:
        print("REFUSED (never-class): this move cannot go ahead.")
        for x in reasons:
            print("  - %s" % x)
        sys.exit(2)
    print("\n".join(commands(r, staging)))


if __name__ == "__main__":
    main()
