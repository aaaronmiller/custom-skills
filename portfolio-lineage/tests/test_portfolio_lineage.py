#!/usr/bin/env python3
"""Tests for the portfolio-lineage skill. Standard library only.

Usage: python3 -I -B tests/test_portfolio_lineage.py [--tmp DIR] [-v]

Each test copies the bundled fixtures into a fresh temporary directory (under
--tmp when given) and removes only that directory afterwards.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
S = os.path.join(HERE, "scripts")
FX = os.path.join(HERE, "tests", "fixtures")
TMP = None

SAMPLE = """# Sample

## Requirements

| ID | Requirement |
|---|---|
| REQ-01 | The table clause SHALL hold. |

- **SPEC-010**: THE list clause SHALL hold,
  across two lines.
- [ ] T045 Bind the skills by contract test.

### CTX-004 Heading clause

The plan MUST keep this normative line.

```text
SPEC-999: inside a code fence, not a clause
```

## Decisions

1. First decision.
2. Second decision.

Plain prose paragraph.
"""


def py(script, *args):
    r = subprocess.run([sys.executable, "-I", "-B", os.path.join(S, script)] + list(args), capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr


def load(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


class Base(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory(dir=TMP)
        self.box = self._td.name
        self.fx = os.path.join(self.box, "fx")
        shutil.copytree(FX, self.fx)

    def tearDown(self):
        self._td.cleanup()

    def ledger(self, name, *extra):
        out = os.path.join(self.box, "%s-ledger.json" % name)
        rc, so, se = py("compare.py", "--source", os.path.join(self.fx, name), "--successor", os.path.join(self.fx, "successor"), "--out", out, *extra)
        self.assertEqual(rc, 0, se)
        return out

    def gate(self, name, ledger, *extra):
        return py("gate.py", "--ledger", ledger, "--folder", os.path.join(self.fx, name), "--out", os.path.join(self.box, "gate.json"), *extra)


class Extract(Base):
    def test_clause_kinds(self):
        p = os.path.join(self.box, "sample.md")
        with open(p, "w") as fh:
            fh.write(SAMPLE)
        out = os.path.join(self.box, "c.json")
        rc, so, se = py("extract_clauses.py", p, "--out", out)
        self.assertEqual(rc, 0, se)
        c = {x["key"]: x for x in load(out)["clauses"]}
        self.assertIn("sample.md#REQ-01", c)
        self.assertEqual(c["sample.md#SPEC-010"]["text"], "THE list clause SHALL hold, across two lines.")
        self.assertIn("sample.md#T045", c)
        self.assertIn("sample.md#CTX-004", c)
        self.assertTrue(any(k.startswith("sample.md:L") and "normative" == v["kind"] for k, v in c.items()))
        self.assertIn("sample.md:decisions:1", c)
        self.assertIn("sample.md:decisions:2", c)
        self.assertNotIn("sample.md#SPEC-999", c)
        self.assertTrue(any("Plain prose" in x["text"] for x in load(out)["paragraphs"]))


class Compare(Base):
    def test_marks_on_proj_c(self):
        led = load(self.ledger("proj-c"))
        marks = {c["id"]: c["mark"] for c in led["clauses"]}
        self.assertEqual(marks, {"SPEC-001": "covered", "SPEC-008": "partial", "SPEC-021": "unique"})
        spec8 = [c for c in led["clauses"] if c["id"] == "SPEC-008"][0]
        self.assertIn("200", spec8["missing_precision"])

    def test_every_clause_has_exactly_one_mark(self):
        for name in ("proj-c", "proj-d"):
            for c in load(self.ledger(name))["clauses"]:
                self.assertIn(c["mark"], ("covered", "partial", "unique"))

    def test_override_recorded_beside_mechanical_mark(self):
        ov = os.path.join(self.box, "ov.json")
        with open(ov, "w") as fh:
            json.dump({"SPEC-021": {"mark": "partial", "reason": "reviewer found it in the hazard register", "by": "test"}}, fh)
        led = load(self.ledger("proj-c", "--overrides", ov))
        c = [x for x in led["clauses"] if x["id"] == "SPEC-021"][0]
        self.assertEqual((c["mark"], c["mechanical_mark"], c["basis"]), ("partial", "unique", "override"))

    def test_bad_override_mark_rejected(self):
        ov = os.path.join(self.box, "ov.json")
        with open(ov, "w") as fh:
            json.dump({"SPEC-021": {"mark": "maybe"}}, fh)
        rc, _, se = py("compare.py", "--source", os.path.join(self.fx, "proj-c"), "--successor", os.path.join(self.fx, "successor"),
                       "--out", os.path.join(self.box, "x.json"), "--overrides", ov)
        self.assertNotEqual(rc, 0)


class Gate(Base):
    def test_unique_without_destination_refused_naming_clause(self):
        rc, so, _ = self.gate("proj-c", self.ledger("proj-c"))
        self.assertEqual(rc, 1)
        self.assertIn("spec.md#SPEC-021", so)
        g = load(os.path.join(self.box, "gate.json"))
        self.assertEqual((g["allowed"], g["unique_without_destination"]), (False, 1))

    def test_destination_recorded_allows(self):
        target = os.path.join(self.box, "hazards.md")
        with open(target, "w") as fh:
            fh.write("copy-out\n")
        d = os.path.join(self.box, "dest.json")
        with open(d, "w") as fh:
            json.dump({"SPEC-021": target}, fh)
        rc, so, _ = self.gate("proj-c", self.ledger("proj-c"), "--destinations", d)
        self.assertEqual(rc, 0, so)

    def test_missing_destination_file_refused_unless_allowed(self):
        d = os.path.join(self.box, "dest.json")
        with open(d, "w") as fh:
            json.dump({"SPEC-021": os.path.join(self.box, "not-there.md")}, fh)
        led = self.ledger("proj-c")
        self.assertEqual(self.gate("proj-c", led, "--destinations", d)[0], 1)
        self.assertEqual(self.gate("proj-c", led, "--destinations", d, "--allow-missing-destination-files")[0], 0)

    def test_non_path_destination_accepted(self):
        d = os.path.join(self.box, "dest.json")
        with open(d, "w") as fh:
            json.dump({"spec.md#SPEC-021": "register row C242 (hazard register)"}, fh)
        self.assertEqual(self.gate("proj-c", self.ledger("proj-c"), "--destinations", d)[0], 0)

    def test_stale_ledger_refused(self):
        led = self.ledger("proj-d")
        with open(os.path.join(self.fx, "proj-d", "spec.md"), "a") as fh:
            fh.write("\nMore text.\n")
        rc, so, _ = self.gate("proj-d", led)
        self.assertEqual(rc, 1)
        self.assertIn("changed since the comparison", so)

    def test_uncompared_clause_refused(self):
        led = self.ledger("proj-d")
        with open(os.path.join(self.fx, "proj-d", "extra.md"), "w") as fh:
            fh.write("- **SPEC-050**: THE system SHALL do something new.\n")
        rc, so, _ = self.gate("proj-d", led)
        self.assertEqual(rc, 1)
        self.assertIn("not in the ledger", so)

    def test_unmarked_clause_refused(self):
        p = self.ledger("proj-d")
        led = load(p)
        led["clauses"][0]["mark"] = "maybe"
        with open(p, "w") as fh:
            json.dump(led, fh)
        rc, so, _ = self.gate("proj-d", p)
        self.assertEqual(rc, 1)
        self.assertIn("not marked covered, partial or unique", so)

    def test_all_covered_or_partial_passes(self):
        rc, so, _ = self.gate("proj-d", self.ledger("proj-d"))
        self.assertEqual(rc, 0, so)


class Contract(unittest.TestCase):
    def test_contract_program_passes(self):
        with tempfile.TemporaryDirectory(dir=TMP) as td:
            r = subprocess.run([sys.executable, "-I", "-B", os.path.join(HERE, "bin", "contract"), "--fixture", "", "--sandbox", os.path.join(td, "s")],
                               capture_output=True, text=True)
            out = json.loads(r.stdout)
            self.assertTrue(out["passed"], out["checks"])
            self.assertEqual(r.returncode, 0)


if __name__ == "__main__":
    if "--tmp" in sys.argv:
        i = sys.argv.index("--tmp")
        TMP = os.path.abspath(sys.argv[i + 1])
        del sys.argv[i:i + 2]
    unittest.main()
