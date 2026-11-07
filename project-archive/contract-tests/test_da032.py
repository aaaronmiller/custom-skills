#!/usr/bin/env python3
"""Contract test DA-032 (owner: project-archive). Prints PASS or FAIL with the reason.

DA-032: Folder moves SHALL always be never-class. WHILE a migration hold is
active, an approved move SHALL additionally first list every consumer of the
folder, pass a sandbox test, and write a manifest, a path map, old-path links,
a working-copy repair and a live-use guard.

Usage: python3 -I -B test_da032.py [--skills DIR | --project-archive DIR] [--tmp DIR]

Part 1 runs the skill's bin/contract and applies the T045 harness rules.
Part 2 drives the skill's scripts on this folder's own fixture (not the
skill's) and checks behaviour with independent code. Fixtures only: every
path written is inside a temporary sandbox.
"""
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import _common as K  # noqa: E402
from fixtures import build as FB  # noqa: E402


def main():
    a = K.args(__doc__)
    R = K.Report("DA-032")
    if not os.path.isfile(os.path.join(a.pa, "SKILL.md")):
        R.check(False, "project-archive skill not found at %s" % a.pa)
        R.finish()
    S = os.path.join(a.pa, "scripts")
    with K.sandbox(a.tmp) as box:
        env = dict(os.environ, PORTFOLIO_LINEAGE_DIR=a.pl)
        rc, out, se = K.contract_output(a.pa, box, env)
        probs = [p for p in K.check_archive_output(out) if p.startswith("DA-032")] if out else []
        R.check(*K.contract_verdict(rc, out, probs, "DA-032"))

        top = FB.build(os.path.join(box, "fx"))
        code = os.path.join(top, "code")
        site = os.path.join(code, "site-old")
        dest = os.path.join(top, "archive", "notes", "site-old")
        h0 = K.tree_hash(site)

        st = os.path.join(box, "st-nohold")
        K.run(os.path.join(S, "plan.py"), "--folder", site, "--dest", dest, "--roots", code, "--staging", st)
        rc, so, _ = K.run(os.path.join(S, "move_dryrun.py"), "--staging", st)
        R.check(rc == 2 and "never-class" in so and K.tree_hash(site) == h0 and not os.path.lexists(dest),
                "no hold, no approval: refused as never-class, folder unchanged")

        st = os.path.join(box, "st-hold-noappr")
        K.run(os.path.join(S, "plan.py"), "--folder", site, "--dest", dest, "--roots", code, "--staging", st,
              "--hold-file", os.path.join(top, "hold.yaml"))
        rc, so, _ = K.run(os.path.join(S, "move_dryrun.py"), "--staging", st)
        R.check(rc == 2 and "approval" in so, "hold without approval: refused")

        st = os.path.join(box, "st")
        rc, so, se = K.run(os.path.join(S, "plan.py"), "--folder", site, "--dest", dest, "--roots", code, "--staging", st,
                           "--hold-file", os.path.join(top, "hold.yaml"), "--approval", os.path.join(top, "approval-site-old.json"))
        R.check(rc == 0, "plan.py ran under hold with approval" if rc == 0 else "plan.py failed: %s" % se.strip()[-200:])
        names = {"consumers": "consumers.json", "sandbox_test": "sandbox-test.json", "manifest": "manifest.json",
                 "path_map": "path-map.json", "old_path_links": "old-path-links.json",
                 "working_copy_repair": "working-copy-repair.json", "live_use_guard": "live-use-guard.json"}
        present = {k: os.path.isfile(os.path.join(st, v)) for k, v in names.items()}
        R.check(all(present.values()), "all seven artifacts written" if all(present.values()) else "missing: %s" % [k for k, v in present.items() if not v])
        if all(present.values()):
            import json
            load = lambda n: json.load(open(os.path.join(st, n), encoding="utf-8"))  # noqa: E731
            cons = sorted((c["kind"], os.path.relpath(c["path"], code)) for c in load("consumers.json")["consumers"])
            want = [("path-reference", "etc/site.yaml"), ("path-reference", "jobs/nightly.cron"), ("symlink", "bin/site-old")]
            R.check(cons == want, "consumer list is exactly the three planted consumers" if cons == want else "consumers %s, want %s" % (cons, want))
            R.check(load("sandbox-test.json").get("passed") is True, "sandbox test passed")
            m = load("manifest.json")
            R.check(m.get("tree_digest") and len([f for f in m["files"] if f["type"] == "file"]) == 2, "manifest lists every file with a digest")
            pm = load("path-map.json")
            R.check(pm["entries"] == [{"old": site, "new": dest}], "path map old to new")
            lk = load("old-path-links.json")
            R.check(lk["links"][0]["at"] == site and lk["links"][0]["points_to"] == dest, "old-path link planned at the old path")
            R.check("never" in load("working-copy-repair.json"), "working-copy repair plan written")
            R.check(load("live-use-guard.json").get("passed") is True, "live-use guard written and passed")
            ready = load("readiness.json")
            R.check(ready.get("move_class") == "never" and ready.get("ready") is True and ready.get("hold_active") is True,
                    "readiness: move class never, hold active, ready for a human-run move")
        rc, so, _ = K.run(os.path.join(S, "move_dryrun.py"), "--staging", st)
        R.check(rc == 0 and "DRY RUN" in so and K.tree_hash(site) == h0 and not os.path.lexists(dest),
                "dry-run mover only prints; nothing moved")
        mtimes = [os.stat(os.path.join(st, n)).st_mtime for n in names.values()]
        os.makedirs(os.path.dirname(dest))
        moved_at = os.stat(os.path.dirname(dest)).st_mtime
        os.rename(site, dest)
        os.symlink(dest, site)
        R.check(max(mtimes) <= moved_at, "all seven artifacts were written before the move")
        rc, so, _ = K.run(os.path.join(S, "verify_move.py"), "--staging", st)
        R.check(rc == 0 and os.path.realpath(site) == os.path.realpath(dest) and K.tree_hash(dest) == h0,
                "after the move the old path resolves through the link and the bytes match")
    R.finish()


if __name__ == "__main__":
    main()
