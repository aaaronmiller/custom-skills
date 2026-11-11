#!/usr/bin/env python3
"""Contract test DA-033 (owner: project-archive). Prints PASS or FAIL with the reason.

DA-033: WHEN a folder is archived, THE procedure SHALL mine, index, move and
link it in that order, keeping identity, locators, predecessor and successor,
a tested recovery, and its uncommitted and working-copy state; the archive
root SHALL be excluded from discovery and the lineage SHALL show in Living
Documents.

Usage: python3 -I -B test_da033.py [--skills DIR | --project-archive DIR --portfolio-lineage DIR] [--tmp DIR]

Part 1 runs the skill's bin/contract and applies the T045 harness rules.
Part 2 archives this folder's own fixture repository (uncommitted edit,
untracked file, stash entry) with the skill's scripts, and checks the result
with independent code: raw git output, its own tree hash, its own recovery
copy and its own discovery walk. The live archive root (~/archive), if it
exists, is listed before and after and must not change.
"""
import hashlib
import json
import os
import shutil
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import _common as K  # noqa: E402
from fixtures import build as FB  # noqa: E402


def listing_hash(root):
    if not os.path.isdir(root):
        return "absent"
    h = hashlib.sha256()
    for d, dirs, files in os.walk(root):
        dirs.sort()
        if d.count(os.sep) - root.count(os.sep) >= 2:
            dirs[:] = []
        for n in sorted(files + dirs):
            h.update(os.path.join(d, n).encode() + b"\0")
    return h.hexdigest()


def load(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def main():
    a = K.args(__doc__)
    R = K.Report("DA-033")
    live = os.path.expanduser("~/archive")
    live0 = listing_hash(live)
    for d, n in ((a.pa, "project-archive"), (a.pl, "portfolio-lineage")):
        if not os.path.isfile(os.path.join(d, "SKILL.md")):
            R.check(False, "%s skill not found at %s" % (n, d))
            R.finish()
    S, PL = os.path.join(a.pa, "scripts"), os.path.join(a.pl, "scripts")
    arch_py = os.path.join(S, "archive.py")
    with K.sandbox(a.tmp) as box:
        env = dict(os.environ, PORTFOLIO_LINEAGE_DIR=a.pl)
        rc, out, se = K.contract_output(a.pa, box, env)
        probs = [p for p in K.check_archive_output(out) if p.startswith("DA-033")] if out else []
        R.check(*K.contract_verdict(rc, out, probs, "DA-033"))

        top = FB.build(os.path.join(box, "fx"))
        code = os.path.join(top, "code")
        repo = os.path.join(code, "notes-repo")
        archive_root = os.path.join(top, "archive")
        dest = os.path.join(archive_root, "notes", "notes-repo")
        page = os.path.join(top, "living", "history.md")
        work = os.path.join(box, "work")
        st0, stash0, head0 = K.git_out(repo, "status", "--porcelain"), K.git_out(repo, "stash", "list"), K.git_out(repo, "rev-parse", "HEAD")
        h0 = K.tree_hash(repo)
        R.check(b"?? b-untracked.md" in st0 and b" M a.md" in st0 and stash0.count(b"\n") == 1, "fixture has an uncommitted edit, an untracked file and one stash entry")

        ledger, gate = os.path.join(box, "ledger.json"), os.path.join(box, "gate.json")
        K.run(os.path.join(PL, "compare.py"), "--source", repo, "--successor", os.path.join(code, "current"), "--out", ledger)
        rc, so, _ = K.run(os.path.join(PL, "gate.py"), "--ledger", ledger, "--folder", repo, "--out", gate)
        R.check(rc == 0, "portfolio-lineage gate allows the folder before archiving")

        rc, _, _ = K.run(arch_py, "index", "--work", work)
        R.check(rc != 0, "index before mine is refused")
        rc, so, se = K.run(arch_py, "mine", "--work", work, "--folder", repo, "--archive-root", archive_root, "--project", "notes",
                           "--lineage-gate", gate, "--predecessor", "notes v0 (paper)", "--successor", "code/current", "--reason", "contract test")
        R.check(rc == 0, "mine ran" if rc == 0 else "mine failed: %s" % se.strip()[-200:])
        rc, _, _ = K.run(arch_py, "move", "--work", work, "--sandbox-root", top)
        R.check(rc != 0 and os.path.isdir(repo) and not os.path.islink(repo), "move before index is refused and nothing moves")
        rc, _, _ = K.run(arch_py, "link", "--work", work, "--ld-page", page, "--discovery-config", os.path.join(top, "discovery.json"), "--apply")
        R.check(rc != 0, "link before move is refused")
        rc, _, se = K.run(arch_py, "index", "--work", work)
        R.check(rc == 0, "index ran" if rc == 0 else "index failed: %s" % se.strip()[-200:])
        K.run(os.path.join(S, "plan.py"), "--folder", repo, "--dest", dest, "--roots", code, "--staging", os.path.join(work, "plan"),
              "--hold-file", os.path.join(top, "hold.yaml"), "--approval", os.path.join(top, "approval-notes-repo.json"))
        rc, so, se = K.run(arch_py, "move", "--work", work, "--sandbox-root", top)
        R.check(rc == 0, "move ran (sandbox)" if rc == 0 else "move failed: %s" % (so + se).strip()[-300:])
        rc, so, se = K.run(os.path.join(S, "recovery_test.py"), "--work", work, "--scratch", os.path.join(box, "scratch"))
        R.check(rc == 0, "skill's recovery test passed" if rc == 0 else "recovery test failed: %s" % (so + se).strip()[-200:])
        rc, so, se = K.run(arch_py, "link", "--work", work, "--ld-page", page, "--discovery-config", os.path.join(top, "discovery.json"), "--apply")
        R.check(rc == 0, "link ran" if rc == 0 else "link failed: %s" % (so + se).strip()[-200:])

        receipts = []
        if os.path.isfile(os.path.join(work, "receipts.jsonl")):
            with open(os.path.join(work, "receipts.jsonl")) as fh:
                receipts = [json.loads(l) for l in fh if l.strip()]
        steps = [r["step"] for r in receipts]
        seqs = [r["seq"] for r in receipts]
        times = [r["at"] for r in receipts]
        R.check(steps == ["mine", "index", "move", "link"] and seqs == sorted(seqs) and times == sorted(times),
                "receipts: mine < index < move < link by sequence and time" if steps == ["mine", "index", "move", "link"] else "receipts show %s" % steps)
        ok = os.path.isdir(dest)
        R.check(ok and K.git_out(dest, "status", "--porcelain") == st0, "git status --porcelain byte-equal after the move")
        R.check(ok and K.git_out(dest, "stash", "list") == stash0 and K.git_out(dest, "rev-parse", "HEAD") == head0, "git stash list and HEAD byte-equal after the move")
        R.check(ok and K.tree_hash(dest) == h0, "archived folder byte-identical (independent tree hash)")
        R.check(os.path.islink(repo) and os.path.realpath(repo) == os.path.realpath(dest), "old path is a link to the archived folder")
        rec = load(os.path.join(work, "archive-record.json")) if os.path.isfile(os.path.join(work, "archive-record.json")) else {}
        loc = rec.get("locators", {})
        R.check(rec.get("identity", {}).get("project_id") == "notes" and loc.get("original_path") == repo and loc.get("archive_path") == dest,
                "record keeps identity and locators")
        R.check(rec.get("predecessor") == "notes v0 (paper)" and rec.get("successor") == "code/current", "record keeps predecessor and successor")
        R.check(rec.get("uncommitted_state", {}).get("status_porcelain") == st0.decode() and rec.get("working_copy_state", {}).get("stash_list") == stash0.decode(),
                "record keeps the uncommitted and working-copy state")
        R.check(rec.get("recovery", {}).get("tested") is True, "record says the recovery was tested")
        if ok:
            scratch = os.path.join(box, "own-recovery", "notes-repo")
            shutil.copytree(dest, scratch, symlinks=True)
            R.check(K.tree_hash(scratch) == h0 and K.git_out(scratch, "status", "--porcelain") == st0 and K.git_out(scratch, "stash", "list") == stash0,
                    "independent recovery copy restores bytes, status and stash")
        cfg = load(os.path.join(top, "discovery.json"))
        excl = [os.path.abspath(e) for e in cfg["exclude"]]
        listed = []
        for r in cfg["roots"]:
            for d, dirs, files in os.walk(r):
                dirs[:] = [x for x in dirs if os.path.abspath(os.path.join(d, x)) not in excl and not os.path.islink(os.path.join(d, x))]
                if (".git" in dirs or ".git" in files) and os.path.realpath(d).startswith(os.path.realpath(archive_root) + os.sep):
                    listed.append(d)
        R.check(archive_root in excl and not listed, "archive root excluded from discovery; a walk of the roots lists nothing under it")
        with open(page, encoding="utf-8") as fh:
            text = fh.read()
        R.check("Lineage: notes-repo archived" in text and dest in text, "lineage entry shows on the Living Documents page")
    R.check(listing_hash(live) == live0, "live archive root %s unchanged" % live)
    R.finish()


if __name__ == "__main__":
    main()
