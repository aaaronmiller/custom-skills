#!/usr/bin/env python3
"""Run the three contract tests and print both skill digests.

Usage: python3 -I -B run_all.py [--skills DIR] [--tmp DIR] [--mutants]

Exit 0 only when DA-032, DA-033 and DA-034 all print PASS.

--mutants also proves the tests can fail: it copies each skill into a
temporary folder, breaks the one rule a clause depends on, and expects the
matching test to print FAIL:
  DA-032  move_dryrun.py ignores a missing approval
  DA-033  archive.py lets link run before move
  DA-034  gate.py lets a unique clause through without a destination
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.realpath(__file__))

MUTANTS = [
    ("DA-032", "test_da032.py", "project-archive", [
        ("scripts/move_dryrun.py", 'if not appr.get("present") or not appr.get("matches_exact_move"):', "if False:"),
        ("scripts/plan.py", '        blockers.append("no operator approval: folder moves are never-class")', "        pass")]),
    ("DA-033", "test_da033.py", "project-archive", [
        ("scripts/archive.py", 'ORDER = ["mine", "index", "move", "link"]', 'ORDER = ["mine", "index", "link", "move"]')]),
    ("DA-034", "test_da034.py", "portfolio-lineage", [
        ("scripts/gate.py", "            if not dest:\n                unique_without += 1", "            if False:\n                unique_without += 1")]),
]


def run_test(name, skills, tmp, extra=()):
    cmd = [sys.executable, "-I", "-B", os.path.join(HERE, name), "--skills", skills] + (["--tmp", tmp] if tmp else []) + list(extra)
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skills", default=os.path.dirname(HERE))
    ap.add_argument("--tmp")
    ap.add_argument("--mutants", action="store_true")
    a = ap.parse_args()
    skills = os.path.abspath(a.skills)
    ok = True
    for t in ("test_da032.py", "test_da033.py", "test_da034.py"):
        rc, out = run_test(t, skills, a.tmp)
        print(out)
        ok = ok and rc == 0 and out.startswith("PASS")
    if a.mutants and not ok:
        print("\nMutant check skipped: the unmodified skills must pass first, or a FAIL proves nothing.")
    elif a.mutants:
        print("\nMutant check (each broken copy must FAIL its clause test):")
        for clause, test, skill, edits in MUTANTS:
            with tempfile.TemporaryDirectory(prefix="mutant-", dir=a.tmp) as td:
                for s in ("project-archive", "portfolio-lineage"):
                    shutil.copytree(os.path.join(skills, s), os.path.join(td, s))
                applied = True
                for rel, old, new in edits:
                    p = os.path.join(td, skill, rel)
                    with open(p, encoding="utf-8") as fh:
                        src = fh.read()
                    if old not in src:
                        applied = False
                        break
                    with open(p, "w", encoding="utf-8") as fh:
                        fh.write(src.replace(old, new, 1))
                rel = ", ".join(e[0] for e in edits)
                if not applied:
                    print("  %s mutant of %s: could not apply (source changed); counts as a failure of this check" % (clause, rel))
                    ok = False
                    continue
                rc, out = run_test(test, td, a.tmp)
                caught = rc != 0 and out.startswith("FAIL")
                ok = ok and caught
                print("  %s mutant (%s): %s" % (clause, rel, "caught, test printed FAIL" if caught else "NOT caught"))
                print("    " + out.splitlines()[0][:300])
    print("\nSkill digests for the import register:")
    r = subprocess.run([sys.executable, "-I", "-B", os.path.join(HERE, "skill_digest.py"),
                        os.path.join(skills, "project-archive"), os.path.join(skills, "portfolio-lineage")], capture_output=True, text=True)
    print(r.stdout.strip())
    print("\nOVERALL: %s" % ("PASS" if ok else "FAIL"))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
