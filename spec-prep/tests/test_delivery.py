"""spec-prep-delivery.py: passing input-handoff and native fixtures, and fixtures that break each rule.

Run from the skill directory: python3 -m unittest discover -s tests -v
"""
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True  # keep scripts/ free of __pycache__

SKILL_DIR = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_DIR / "scripts" / "spec-prep-delivery.py"
_spec = importlib.util.spec_from_file_location("spec_prep_delivery", SCRIPT)
d = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(d)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class DeliveryFixture(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.doc = {"schemaVersion": 1, "operation": "input-handoff",
                    "implementationAuthorized": False, "workstreams": []}
        self.add_stream("report")

    def write(self, path, text):
        dest = self.root / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text)
        return dest

    def add_stream(self, name):
        files = {
            "inputs/intent.md": "# Intent\nOperators receive complete reports.\n\n## Prior art\n"
                                "Manual collation is slow; build new.\n\n## Source disposition\n"
                                "- USER-1: preserved in section 1.\n- ../data/README.md: analysis-input, preserved.\n",
            "inputs/requirements.md": "# Requirements\nFR-001: MUST return every record of the month.\n",
            "inputs/design.md": "# Design\nFR-001: a deterministic report serializer.\n",
            "data/README.md": "# Data\nSources, raw layout and dictionary for the report data.\n",
            ".specify/memory/constitution.md": "# Constitution\nEvidence precedes completion.\n",
            "AGENTS.md": "Read .specify/memory/constitution.md and reset-handoff.md before changes.\n"
                         "Preparation only; do not implement.\n",
            "reset-handoff.md": "# Handoff\nPreparation only; implementation not authorized.\nNext: specification preparation.\n",
            "README.md": "# Conversion\nRead inputs/requirements.md and inputs/intent.md for specify; read "
                         "inputs/design.md, generated spec.md, intent and .specify/memory/constitution.md for plan. "
                         "Then tasks and analyze. Stop before implementation.\n",
        }
        for filename, text in files.items():
            self.write(f"{name}/{filename}", text)
        self.doc["workstreams"].append({
            "id": name, "buildRoot": name, "inputRoot": f"{name}/inputs",
            "inputs": {"requirements": "requirements.md", "design": "design.md", "intent": "intent.md"},
            "sourceMap": "intent.md#source-disposition", "conversionGuide": "README.md",
            "nextOperation": "specification-preparation",
            "priorArt": {"status": "done", "record": "intent.md#prior-art"},
            "supporting": [{"path": "../data/README.md", "role": "analysis-input", "why": "data section"}],
            "governance": {"constitution": ".specify/memory/constitution.md",
                           "instructions": "AGENTS.md", "handoff": "reset-handoff.md"},
        })

    @property
    def stream(self):
        return self.doc["workstreams"][0]

    def errors(self):
        return d.validate(self.root, self.doc)

    def assertRejected(self, fragment):
        errors = self.errors()
        self.assertTrue(errors, "expected the delivery to be rejected")
        self.assertTrue(any(fragment in e for e in errors), errors)

    def native(self):
        self.doc["operation"] = "native-preparation"
        self.stream.update(featureRoot="specs/001-report", receipt="preparation.json",
                           nextOperation="await-implementation-authorization")
        self.write("report/reset-handoff.md", "# Handoff\nPreparation complete; implementation not authorized.\n"
                                              "Next: await explicit implementation authorization.\n")
        self.write("report/specs/001-report/intent.md", "# Intent\nOperators receive complete reports.\n")
        self.write("report/specs/001-report/spec.md", "# Spec\n- **FR-001**: System MUST return every record.\n")
        self.write("report/specs/001-report/plan.md", "# Plan\nFR-001 is served by the report query.\n")
        self.write("report/specs/001-report/tasks.md",
                   "- [ ] T001 Build the report query. Gate: the exported record count matches the source.\n")
        build = self.root / "report"
        artifacts = {role: {"path": path, "sha256": sha(build / path)} for role, path in [
            ("spec", "specs/001-report/spec.md"), ("plan", "specs/001-report/plan.md"),
            ("tasks", "specs/001-report/tasks.md"), ("constitution", ".specify/memory/constitution.md"),
            ("handoff", "reset-handoff.md")]}
        for path in ("inputs/intent.md", "inputs/requirements.md", "inputs/design.md",
                     "specs/001-report/intent.md", "AGENTS.md", "README.md"):
            artifacts[path] = {"path": path, "sha256": sha(build / path)}
        gates = {}
        for name in ("constitution", "prerequisites", "analysis", "traceability", "validation"):
            evidence = f"evidence/{name}.md"
            self.write(f"report/{evidence}", "# Synthetic fixture\nGate result for checker tests only.\n")
            gates[name] = {"status": "passed", "command": "fixture-only", "observedAt": "2026-11-10",
                           "evidence": evidence}
        gates["validation"].update(
            command="python3 scripts/spec-prep-validate.py specs/001-report --operation native-preparation "
                    "--build-root . --json", exitStatus=0,
            checks={name: "passed" for name in d.VALIDATION_CHECKS})
        receipt = {"schemaVersion": 1, "lifecycle": "specification-prepared", "implementationAuthorized": False,
                   "skill": {"version": "4.1.0", "sha256": sha(SKILL_DIR / "SKILL.md")},
                   "artifacts": artifacts, "gates": gates}
        self.write("report/preparation.json", json.dumps(receipt))
        return receipt

    def rewrite_receipt(self, receipt):
        self.write("report/preparation.json", json.dumps(receipt))


NUMBERED_INTENT = """# Report Intent v1.0

## 1. Goal
Operators receive complete reports.

## 10. Prior art
| Solution | Strength | Weakness | Gap this fills |
|---|---|---|---|
| Manual collation | Familiar | Slow | Repeatable report |

## 12. Open intent questions
- [NEEDS CLARIFICATION: is the reporting month the calendar month or the fiscal month?]

## Source disposition
- USER-1: preserved in section 1.
- ../data/README.md: analysis-input, preserved.
- prior-art: done; section 10.
"""


class Passing(DeliveryFixture):
    def test_input_handoff_with_two_workstreams_passes(self):
        self.add_stream("platform")
        self.assertEqual(self.errors(), [])

    def test_older_manifest_without_additive_fields_passes(self):
        del self.stream["priorArt"]
        del self.stream["supporting"]
        self.assertEqual(self.errors(), [])

    def test_native_preparation_with_verified_receipt_passes(self):
        self.native()
        self.assertEqual(self.errors(), [])

    def test_claude_adapter_importing_agents_passes(self):
        self.stream["governance"]["adapter"] = "CLAUDE.md"
        self.write("report/CLAUDE.md", "@AGENTS.md\n")
        self.assertEqual(self.errors(), [])

    def test_known_spec_kit_hook_and_disabled_hook_pass(self):
        self.write("report/.specify/extensions.yml",
                   "hooks:\n  after_tasks:\n    - extension: git\n      command: speckit.git.commit\n"
                   "  after_analyze:\n    - command: speckit.implement\n      enabled: false\n")
        self.assertEqual(self.errors(), [])

    def test_numbered_template_headings_resolve_unnumbered_fragments(self):
        # A2: the intent template's '## 10. Prior art' answers '#prior-art' and '#10-prior-art'.
        self.write("report/inputs/intent.md", NUMBERED_INTENT)
        self.assertEqual(self.errors(), [])
        self.stream["priorArt"]["record"] = "intent.md#10-prior-art"
        self.assertEqual(self.errors(), [])

    def test_listed_clarification_markers_pass_in_inputs_and_native_outputs(self):
        # A1: Spec Kit form '[NEEDS CLARIFICATION: question]' is a listed open item, not a stub.
        self.write("report/inputs/intent.md", NUMBERED_INTENT)
        self.native()
        self.write("report/specs/001-report/spec.md", "# Spec\n- **FR-001**: System MUST return every record "
                                                      "[NEEDS CLARIFICATION: fiscal or calendar month?].\n")
        receipt = json.loads((self.root / "report/preparation.json").read_text())
        receipt["artifacts"]["spec"]["sha256"] = sha(self.root / "report/specs/001-report/spec.md")
        self.rewrite_receipt(receipt)
        self.assertEqual(self.errors(), [])

    def test_reviewed_hook_passes(self):
        # A3: a reviewed command listed in reviewedHooks passes.
        self.write("report/.specify/extensions.yml",
                   "hooks:\n  after_tasks:\n    - command: npx prettier --write specs\n")
        self.stream["reviewedHooks"] = [{"command": "npx prettier --write specs",
                                         "review": "formats Markdown only; launches nothing"}]
        self.assertEqual(self.errors(), [])

    def test_reviewed_prompt_hook_passes(self):
        self.write("report/.claude/settings.json", json.dumps(
            {"hooks": {"Stop": [{"hooks": [{"type": "prompt", "prompt": "Summarize the diff."}]}]}}))
        self.stream["reviewedHooks"] = [{"command": "Summarize the diff.", "review": "read-only summary"}]
        self.assertEqual(self.errors(), [])

    def test_prior_art_record_under_build_root_passes(self):
        # L2: the record may be a package file named relative to the build root.
        self.write("report/sources/prior-art.md", "# Prior art\nSearches, closest projects; verdict: build new.\n")
        self.stream["priorArt"]["record"] = "sources/prior-art.md"
        self.assertEqual(self.errors(), [])

    def test_readme_conversion_guide_inside_input_root_passes(self):
        # L3: a README.md guide beside the trio is not a competing entry document.
        guide = (self.root / "report/README.md").read_text()
        (self.root / "report/README.md").unlink()
        self.write("report/inputs/README.md", guide)
        self.stream["conversionGuide"] = "inputs/README.md"
        self.assertEqual(self.errors(), [])

    def test_validation_checks_match_the_validator(self):
        # A8: the receipt gate names the same nine checks the validator reports.
        spec = importlib.util.spec_from_file_location("spv", SKILL_DIR / "scripts" / "spec-prep-validate.py")
        validator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(validator)
        self.assertEqual(list(d.VALIDATION_CHECKS), validator.CHECKS)

    def test_legacy_receipt_normalizes_without_mutation(self):
        receipt = self.native()
        legacy = dict(receipt, artifacts=list(receipt["artifacts"].values()),
                      gates=[dict(item, name=name) for name, item in receipt["gates"].items()])
        before = json.dumps(legacy)
        normalized = d.normalize_receipt(legacy)
        self.assertEqual(normalized["artifacts"]["spec"], receipt["artifacts"]["spec"])
        self.assertEqual(before, json.dumps(legacy))


class Rejected(DeliveryFixture):
    def test_fragmented_core_document(self):
        self.stream["inputs"]["design"] = "hardware-profiles.md"
        self.assertRejected("complete design.md")

    def test_extra_markdown_in_input_root(self):
        self.write("report/inputs/hardware-profiles.md", "# Hardware\nProfiles.\n")
        self.assertRejected("fragmented extra Markdown")

    def test_native_claim_without_native_outputs(self):
        self.doc["operation"] = "native-preparation"
        self.assertTrue(self.errors())

    def test_input_handoff_pointing_at_implementation(self):
        self.stream["nextOperation"] = "implementation"
        self.assertRejected("nextOperation")

    def test_agents_md_without_constitution_pointer(self):
        self.write("report/AGENTS.md", "Read reset-handoff.md. Preparation only; do not implement.\n")
        self.assertRejected("AGENTS.md must load")

    def test_missing_source_disposition_heading(self):
        self.stream["sourceMap"] = "intent.md#missing-heading"
        self.assertRejected("source-disposition")

    def test_claude_adapter_without_import(self):
        self.stream["governance"]["adapter"] = "CLAUDE.md"
        self.write("report/CLAUDE.md", "Unrelated instructions.\n")
        self.assertRejected("@AGENTS.md")

    def test_implementation_authorized_true(self):
        self.doc["implementationAuthorized"] = True
        self.assertRejected("implementationAuthorized")

    def test_checked_task_after_preparation(self):
        self.native()
        self.write("report/specs/001-report/tasks.md", "- [x] T001 Implemented.\n")
        self.assertRejected("unchecked")

    def test_enabled_implement_hook(self):
        self.write("report/.specify/extensions.yml", "hooks:\n  after_tasks:\n    - command: speckit.implement\n")
        self.assertRejected("automatic transition")

    def test_build_root_outside_package(self):
        self.stream["buildRoot"] = "../elsewhere"
        self.assertRejected("safe package-relative path")

    def test_empty_gate_evidence(self):
        self.native()
        self.write("report/evidence/analysis.md", "")
        self.assertTrue(self.errors())

    def test_incomplete_lifecycle(self):
        receipt = self.native()
        receipt["lifecycle"] = "specification-reviewed-incomplete"
        self.write("report/preparation.json", json.dumps(receipt))
        self.assertRejected("specification-prepared")

    def test_changed_consumed_input_invalidates_receipt(self):
        self.native()
        self.write("report/inputs/requirements.md", "# Requirements\nChanged behavior.\n")
        self.assertRejected("hash mismatch")

    def test_receipt_from_another_skill_release(self):
        receipt = self.native()
        receipt["skill"]["sha256"] = "0" * 64
        self.write("report/preparation.json", json.dumps(receipt))
        self.assertRejected("skill digest")

    def test_ambiguous_legacy_role(self):
        receipt = self.native()
        receipt["artifacts"] = list(receipt["artifacts"].values()) + [{"path": "other/spec.md", "sha256": "a" * 64}]
        with self.assertRaises(ValueError):
            d.normalize_receipt(receipt)

    def test_prior_art_unknown_status(self):
        self.stream["priorArt"] = {"status": "skipped", "record": "no time"}
        self.assertRejected("priorArt.status")

    def test_prior_art_done_record_heading_missing(self):
        self.stream["priorArt"] = {"status": "done", "record": "intent.md#competitor-survey"}
        self.assertRejected("priorArt.record")

    def test_prior_art_only_directed_at_native_preparation(self):
        self.native()
        self.stream["priorArt"] = {"status": "directed", "record": "user scheduled the survey next"}
        self.assertRejected("only directed")

    def test_supporting_path_missing(self):
        self.stream["supporting"][0]["path"] = "../data/absent.csv"
        self.assertRejected("missing supporting path")

    def test_supporting_path_not_declared_in_source_map(self):
        self.write("report/references/vendor-guide.md", "# Vendor guide\n")
        self.stream["supporting"].append({"path": "../references/vendor-guide.md", "role": "reference",
                                          "why": "integration limits"})
        self.assertRejected("not declared")

    def test_bare_clarification_marker_is_a_stub(self):
        # A1: a marker with no question is still template content.
        self.write("report/inputs/intent.md", NUMBERED_INTENT.replace(
            "[NEEDS CLARIFICATION: is the reporting month the calendar month or the fiscal month?]",
            "[NEEDS CLARIFICATION]"))
        self.assertRejected("unresolved template content")

    def test_other_template_stub_still_rejected(self):
        # A1: accepting clarification markers does not admit other stubs.
        self.write("report/inputs/requirements.md", "# Requirements for [FEATURE NAME]\nFR-001: MUST return records.\n")
        self.assertRejected("unresolved template content")

    def test_numbered_heading_fragment_must_still_exist(self):
        # A2: normalized matching is not a wildcard.
        self.write("report/inputs/intent.md", NUMBERED_INTENT)
        self.stream["priorArt"]["record"] = "intent.md#11-prior-art-survey"
        self.assertRejected("priorArt.record heading not found")

    def test_unreviewed_hook_rejected(self):
        # A3: a command that is neither a known stage nor reviewed fails.
        self.write("report/.specify/extensions.yml",
                   "hooks:\n  after_tasks:\n    - command: npx prettier --write specs\n")
        self.assertRejected("needs review")

    def test_reviewed_hook_without_note_rejected(self):
        self.write("report/.specify/extensions.yml",
                   "hooks:\n  after_tasks:\n    - command: npx prettier --write specs\n")
        self.stream["reviewedHooks"] = [{"command": "npx prettier --write specs", "review": ""}]
        self.assertRejected("one-line review note")

    def test_review_cannot_admit_an_implement_hook(self):
        self.write("report/.specify/extensions.yml", "hooks:\n  after_tasks:\n    - command: speckit.implement\n")
        self.stream["reviewedHooks"] = [{"command": "speckit.implement", "review": "we trust it"}]
        self.assertRejected("removed or disabled")

    def test_native_receipt_without_validation_gate(self):
        # A8: a run that skipped spec-prep-validate.py fails the delivery check.
        receipt = self.native()
        del receipt["gates"]["validation"]
        self.rewrite_receipt(receipt)
        self.assertRejected("missing passed gate evidence: validation")

    def test_validation_gate_with_a_failed_check(self):
        receipt = self.native()
        receipt["gates"]["validation"]["checks"]["drift"] = "failed"
        self.rewrite_receipt(receipt)
        self.assertRejected("did not pass: drift")

    def test_validation_gate_with_nonzero_exit(self):
        receipt = self.native()
        receipt["gates"]["validation"]["exitStatus"] = 1
        self.rewrite_receipt(receipt)
        self.assertRejected("exitStatus 0")

    def test_validation_gate_missing_a_check(self):
        receipt = self.native()
        del receipt["gates"]["validation"]["checks"]["prior-art"]
        self.rewrite_receipt(receipt)
        self.assertRejected("lacks per-check results: prior-art")

    def test_validation_gate_not_from_the_validator(self):
        receipt = self.native()
        receipt["gates"]["validation"]["command"] = "fixture-only"
        self.rewrite_receipt(receipt)
        self.assertRejected("spec-prep-validate.py")

    def test_prior_art_record_escaping_the_build_root(self):
        # L2: a record path may not leave the package.
        self.write("outside.md", "# Prior art\nNot part of the package.\n")
        self.stream["priorArt"]["record"] = "../../outside.md"
        self.assertRejected("escapes the build root")

    def test_prior_art_record_file_missing(self):
        self.stream["priorArt"]["record"] = "sources/prior-art.md"
        self.assertRejected("missing file")

    def test_supporting_role_outside_the_role_table(self):
        self.stream["supporting"][0]["role"] = "misc"
        self.assertRejected("supporting role")


class CommandLine(unittest.TestCase):
    def test_help_exits_zero(self):
        result = subprocess.run([sys.executable, str(SCRIPT), "--help"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn("delivery.json", result.stdout)

    def test_missing_manifest_exits_one_with_json(self):
        with tempfile.TemporaryDirectory() as temp:
            result = subprocess.run([sys.executable, str(SCRIPT), temp], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertFalse(json.loads(result.stdout)["valid"])


if __name__ == "__main__":
    unittest.main()
