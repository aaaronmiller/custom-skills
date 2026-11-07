#!/usr/bin/env python3
"""Contract test DA-034 (owner: portfolio-lineage). Prints PASS or FAIL with the reason.

DA-034: BEFORE anything is archived, a clause-level comparison SHALL mark each
of its clauses covered, partial or unique, and no folder holding a unique
clause without a recorded destination SHALL be archived.

Usage: python3 -I -B test_da034.py [--skills DIR | --portfolio-lineage DIR --project-archive DIR] [--tmp DIR]

Part 1 runs the skill's bin/contract and applies the T045 harness rules.
Part 2 runs the skill's scripts on this folder's own fixtures
(fixtures/lineage: attempt-1 holds a unique clause, attempt-2 does not) and
checks: every clause carries exactly one of the three marks; attempt-1 is
refused naming its unique clause; it passes once a destination is recorded;
a clause added after the comparison blocks the gate; and project-archive's
mine step refuses a folder whose gate refused (the link between the clauses).
"""
import json
import os
import shutil
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, HERE)
import _common as K  # noqa: E402


def load(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def main():
    a = K.args(__doc__)
    R = K.Report("DA-034")
    if not os.path.isfile(os.path.join(a.pl, "SKILL.md")):
        R.check(False, "portfolio-lineage skill not found at %s" % a.pl)
        R.finish()
    PL = os.path.join(a.pl, "scripts")
    with K.sandbox(a.tmp) as box:
        rc, out, se = K.contract_output(a.pl, box)
        probs = K.check_lineage_output(out) if out else []
        R.check(*K.contract_verdict(rc, out, probs, "DA-034"))

        fx = os.path.join(box, "lineage")
        shutil.copytree(os.path.join(HERE, "fixtures", "lineage"), fx)
        cur = os.path.join(fx, "current")
        led = {}
        for name in ("attempt-1", "attempt-2"):
            p = os.path.join(box, "%s.json" % name)
            rc, so, se = K.run(os.path.join(PL, "compare.py"), "--source", os.path.join(fx, name), "--successor", cur, "--out", p)
            R.check(rc == 0, "compare ran on %s" % name)
            led[name] = load(p) if rc == 0 else {"clauses": []}
            marks = [c.get("mark") for c in led[name]["clauses"]]
            R.check(len(marks) == 2 and all(m in ("covered", "partial", "unique") for m in marks),
                    "%s: each of its 2 clauses has exactly one mark (%s)" % (name, ", ".join(map(str, marks))))
        m1 = {c["id"]: c["mark"] for c in led["attempt-1"]["clauses"]}
        m2 = {c["id"]: c["mark"] for c in led["attempt-2"]["clauses"]}
        R.check(m1.get("A1-01") == "covered" and m1.get("A1-02") == "unique", "attempt-1 marks: A1-01 covered, A1-02 unique (got %s)" % m1)
        R.check("unique" not in m2.values(), "attempt-2 has no unique clause (got %s)" % m2)

        g1 = os.path.join(box, "gate-1.json")
        rc, so, _ = K.run(os.path.join(PL, "gate.py"), "--ledger", os.path.join(box, "attempt-1.json"), "--folder", os.path.join(fx, "attempt-1"), "--out", g1)
        R.check(rc != 0 and "A1-02" in so and load(g1)["allowed"] is False, "attempt-1 refused, naming A1-02")
        rc, so, _ = K.run(os.path.join(PL, "gate.py"), "--ledger", os.path.join(box, "attempt-2.json"), "--folder", os.path.join(fx, "attempt-2"))
        R.check(rc == 0, "attempt-2 (covered or partial only) may be archived")

        if os.path.isfile(os.path.join(a.pa, "scripts", "archive.py")):
            rc, _, se = K.run(os.path.join(a.pa, "scripts", "archive.py"), "mine", "--work", os.path.join(box, "w1"), "--folder", os.path.join(fx, "attempt-1"),
                              "--archive-root", os.path.join(box, "arch"), "--project", "p", "--lineage-gate", g1)
            R.check(rc != 0 and "DA-034" in se and not os.path.exists(os.path.join(box, "arch")), "project-archive mine refuses the folder the gate refused")

        copy = os.path.join(box, "copy-outs", "A1-02.md")
        os.makedirs(os.path.dirname(copy))
        with open(copy, "w", encoding="utf-8") as fh:
            fh.write("A1-02 copied out from attempt-1/plan.md\n")
        dest = os.path.join(box, "dest.json")
        with open(dest, "w", encoding="utf-8") as fh:
            json.dump({"A1-02": copy}, fh)
        rc, so, _ = K.run(os.path.join(PL, "gate.py"), "--ledger", os.path.join(box, "attempt-1.json"), "--folder", os.path.join(fx, "attempt-1"), "--destinations", dest)
        R.check(rc == 0, "attempt-1 allowed once A1-02 has a recorded destination")

        with open(os.path.join(fx, "attempt-2", "late.md"), "w", encoding="utf-8") as fh:
            fh.write("- **A2-09**: A late clause SHALL be compared before archiving.\n")
        rc, so, _ = K.run(os.path.join(PL, "gate.py"), "--ledger", os.path.join(box, "attempt-2.json"), "--folder", os.path.join(fx, "attempt-2"))
        R.check(rc != 0 and "A2-09" in so, "a clause not in the comparison blocks archiving")
    R.finish()


if __name__ == "__main__":
    main()
