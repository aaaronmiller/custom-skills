"""spec-prep-validate.py: one passing fixture, and constructed fixtures that make each check fail.

Run from the skill directory: python3 -m unittest discover -s tests -v
Each failing test asserts which checks fail, so a fixture that trips the wrong
check (or none) is itself a test failure.
"""
import contextlib
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True  # keep scripts/ free of __pycache__

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "spec-prep-validate.py"
_spec = importlib.util.spec_from_file_location("spec_prep_validate", SCRIPT)
v = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(v)

INTENT = """# Report Export Intent

## 1. Goal
Operators receive a complete monthly report without manual collation.

## 10. Prior art
| Solution | Strength | Weakness | Gap this fills |
|---|---|---|---|
| Manual spreadsheet collation | Familiar | Error-prone and slow | Repeatable complete report |

Verdict: build new.

## Source disposition
- sources/brief.md: preserved; goal incorporated into section 1.
- prior-art: done; section 10.
"""

SPEC = """# Report Export Specification

## 1. Contract clauses

**SPEC-001** [EVAL-001] WHEN an operator requests the monthly report THE system SHALL return every record dated in that month.
- Traces to: intent section 1

**SPEC-002** [EVAL-002] IF the month has no records THEN the system SHALL return an empty report with a zero count.
- Traces to: intent section 6
"""

CONTEXT = """# Report Export Context (derived)

CTX-001: a single-file relational store (`SQLite`) serves SPEC-001 and SPEC-002 at the stated scale.
"""

SUBSTRATE = """# Substrate Self-Location

## Declared level
S2: the agent drafts changes and a human reviews every line.
"""

LEDGER = "## 1 [0.1] decision\n- What: prepared the export contract and its evaluations.\n"
STANDING = "# Standing\n\n## Where this is\nThe export contract is prepared; implementation has not started.\n"
EVALS = "| EVAL-ID | Asserts |\n|---|---|\n| EVAL-001 | all records of the month are returned |\n| EVAL-002 | an empty month yields a zero count |\n"


class Fixture(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / "project"
        files = {
            "intent.md": INTENT, "spec.md": SPEC, "context.md": CONTEXT, "substrate.md": SUBSTRATE,
            "ledger/ledger.md": LEDGER, "ledger/standing.md": STANDING,
            "sources/brief.md": "# Brief\nA verbatim user prompt asking for a monthly report.\n",
        }
        for name, text in files.items():
            self.write(name, text)
        self.evals = self.base / "evals" / "evals.md"
        self.evals.parent.mkdir()
        self.evals.write_text(EVALS)

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def edit(self, name, old, new):
        path = self.root / name
        text = path.read_text()
        self.assertIn(old, text, f"fixture edit target missing in {name}")
        path.write_text(text.replace(old, new))

    def run_checks(self, operation="standalone", **kw):
        kw.setdefault("build_root", self.root)
        kw.setdefault("evals", str(self.evals))
        result, *_ = v.validate(self.root, operation, **kw)
        return result

    def assertFails(self, expected, **kw):
        result = self.run_checks(**kw)
        self.assertEqual(set(result.failed), set(expected), json.dumps(result.findings, indent=1))
        return result


class PassingFixtures(Fixture):
    def test_standalone_fixture_passes_all_nine_checks(self):
        result = self.run_checks()
        self.assertEqual(result.failed, [], json.dumps(result.findings, indent=1))
        self.assertEqual(set(result.status.values()), {"passed"})
        self.assertEqual(list(result.status), v.CHECKS)

    def test_input_handoff_needs_no_ledger_or_substrate(self):
        for name in ("ledger/ledger.md", "ledger/standing.md", "substrate.md"):
            (self.root / name).unlink()
        (self.root / "spec.md").rename(self.root / "requirements.md")
        (self.root / "context.md").rename(self.root / "design.md")
        result = self.run_checks("input-handoff")
        self.assertEqual(result.failed, [], json.dumps(result.findings, indent=1))
        self.assertEqual(result.status["continuity"], "not_run")
        self.assertEqual(result.status["honesty"], "not_run")

    def test_native_feature_root_binds_evals_through_traceability(self):
        self.write("spec.md", "# Spec\n\n- **FR-001**: System MUST return every record dated in the month.\n"
                              "- **FR-002**: System MUST return a zero count for an empty month.\n")
        (self.root / "context.md").unlink()
        self.write("plan.md", "# Plan\nThe report query serves FR-001; the empty case serves FR-002.\n")
        self.write("traceability.md", "| Clause | Eval |\n|---|---|\n| FR-001 | EVAL-001 |\n| FR-002 | EVAL-002 |\n")
        result = self.run_checks("native-preparation")
        self.assertEqual(result.failed, [], json.dumps(result.findings, indent=1))

    def test_external_continuity_records_not_run(self):
        for name in ("ledger/ledger.md", "ledger/standing.md"):
            (self.root / name).unlink()
        result = self.run_checks(continuity_external=True)
        self.assertEqual(result.failed, [])
        self.assertEqual(result.status["continuity"], "not_run")

    def test_justified_layer_allow_entry_permits_a_user_constraint(self):
        self.edit("intent.md", "## 10. Prior art", "## 3. Constraints\nReports stay in the existing Postgres cluster.\n\n## 10. Prior art")
        self.write("layer-allow.txt", "postgres  # intent section 3: the user mandates the existing cluster\n")
        self.assertFails([])

    def test_products_named_in_prior_art_are_exempt(self):
        self.edit("intent.md", "| Manual spreadsheet collation |", "| A React dashboard on Firebase |")
        self.assertFails([])

    def test_directed_prior_art_passes_before_plan_and_tasks(self):
        self.edit("intent.md", "| Manual spreadsheet collation | Familiar | Error-prone and slow | Repeatable complete report |\n\nVerdict: build new.\n", "")
        self.edit("intent.md", "- prior-art: done; section 10.", "- prior-art: directed; the user scheduled the survey as the next step.")
        self.assertFails([])


class EachCheckFails(Fixture):
    def test_separation_static_token_in_intent(self):
        self.edit("intent.md", "without manual collation", "stored in Postgres")
        self.assertFails(["separation"])

    def test_separation_token_harvested_from_derived_layer(self):
        self.edit("context.md", "CTX-001:", "CTX-002: rendering uses WebGPU.\nCTX-001:")
        self.edit("spec.md", "return every record", "render through WebGPU every record")
        self.assertFails(["separation"])

    def test_separation_unjustified_layer_allow_entry(self):
        self.edit("intent.md", "without manual collation", "kept in the existing Postgres cluster")
        self.write("layer-allow.txt", "postgres\n")
        self.assertFails(["separation"])

    def test_eval_binding_untagged_clause(self):
        self.edit("spec.md", "**SPEC-002** [EVAL-002]", "**SPEC-002**")
        self.assertFails(["eval-binding"])

    def test_eval_binding_dangling_eval(self):
        self.edit("spec.md", "[EVAL-002]", "[EVAL-009]")
        self.assertFails(["eval-binding"])

    def test_eval_binding_store_inside_build_root(self):
        inside = self.write("evals.md", EVALS)
        self.assertFails(["eval-binding"], evals=str(inside))

    def test_eval_binding_missing_store(self):
        self.assertFails(["eval-binding"], evals=str(self.base / "absent" / "evals.md"))

    def test_testability_non_evaluable_language(self):
        self.edit("spec.md", "an empty report with a zero count", "a user-friendly empty report")
        self.assertFails(["testability"])

    def test_identity_duplicate_clause_id(self):
        self.edit("spec.md", "- Traces to: intent section 6\n",
                  "- Traces to: intent section 6\n\n**SPEC-001** [EVAL-001] THE system SHALL label the report month.\n")
        self.assertFails(["identity"])

    def test_identity_empty_specification(self):
        self.write("spec.md", "# Report Export Specification\n\nThe report contract is not written yet.\n")
        result = self.run_checks()
        self.assertIn("identity", result.failed)

    def test_drift_uncited_clause(self):
        self.edit("context.md", "SPEC-001 and SPEC-002", "SPEC-001")
        self.assertFails(["drift"])

    def test_drift_dangling_citation(self):
        self.edit("context.md", "SPEC-001 and SPEC-002", "SPEC-001, SPEC-002 and SPEC-003")
        self.assertFails(["drift"])

    def test_drift_undeclared_supporting_material(self):
        self.write("data/raw-2026-10.csv", "month,count\n2026-10,42\n")
        self.assertFails(["drift"])

    def test_continuity_missing_ledger(self):
        (self.root / "ledger/ledger.md").unlink()
        self.assertFails(["continuity"])

    def test_continuity_disagreeing_aliases(self):
        self.write("ledger.md", "A flat ledger whose content differs from the nested ledger file.\n")
        self.assertFails(["continuity"])

    def test_honesty_no_declared_level(self):
        self.write("substrate.md", "# Substrate Self-Location\n\n## Declared level\nAgents do most of the work.\n")
        self.assertFails(["honesty"])

    def test_authorship_missing_derived_layer(self):
        (self.root / "context.md").unlink()
        self.assertFails(["authorship"])

    def test_authorship_missing_source_disposition_map(self):
        self.edit("intent.md", "## Source disposition\n- sources/brief.md: preserved; goal incorporated into section 1.\n- prior-art: done; section 10.\n", "")
        (self.root / "sources/brief.md").unlink()
        self.assertFails(["authorship"])

    def test_prior_art_no_record(self):
        self.edit("intent.md", "| Manual spreadsheet collation | Familiar | Error-prone and slow | Repeatable complete report |\n\nVerdict: build new.\n", "| ... | ... | ... | ... |\n")
        self.edit("intent.md", "- prior-art: done; section 10.\n", "")
        self.assertFails(["prior-art"])

    def test_prior_art_waived_without_reason(self):
        self.edit("intent.md", "- prior-art: done; section 10.", "- prior-art: waived")
        self.assertFails(["prior-art"])

    def test_prior_art_directed_but_tasks_exist(self):
        self.edit("intent.md", "| Manual spreadsheet collation | Familiar | Error-prone and slow | Repeatable complete report |\n\nVerdict: build new.\n", "")
        self.edit("intent.md", "- prior-art: done; section 10.", "- prior-art: directed; survey is the next step.")
        self.write("tasks.md", "- [ ] T001 Build the report query. Gate: SPEC-001 evaluation passes.\n")
        self.assertFails(["prior-art"])


class CommandLine(unittest.TestCase):
    def run_script(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)

    def test_help_exits_zero(self):
        result = self.run_script("--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("separation", result.stdout)

    def test_bad_operation_is_a_usage_error(self):
        result = self.run_script(".", "--operation", "build-it")
        self.assertEqual(result.returncode, 2)

    def test_failing_tree_exits_one_and_lists_every_check(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "intent.md").write_text("# Intent\nUse React for everything.\n")
            result = self.run_script(str(root), "--json")
            self.assertEqual(result.returncode, 1)
            data = json.loads(result.stdout)
            self.assertEqual([c["name"] for c in data["checks"]], v.CHECKS)
            self.assertFalse(data["valid"])

    def test_audit_flags_a_foreign_spec(self):
        with tempfile.TemporaryDirectory() as temp:
            spec = Path(temp) / "requirements.md"
            spec.write_text("# Requirements\n- **FR-001**: The dashboard MUST be built in React and be intuitive.\n")
            result = self.run_script("--audit", str(spec))
            self.assertEqual(result.returncode, 1)
            self.assertIn("react", result.stdout)
            self.assertIn("intuitive", result.stdout)


if __name__ == "__main__":
    unittest.main()
