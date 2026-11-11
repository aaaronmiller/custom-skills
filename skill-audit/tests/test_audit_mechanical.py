"""Fixtures for scripts/audit_mechanical.py.

Each check gets a minimal skill that MUST trip it and a healthy skill that
must NOT. The regression classes pin the false alarms and misses found by the
2026-11-10 independent validation. Credential-shaped strings are assembled at
run time so this file never ships a token the private-data check would flag.

Run from the skill folder:  python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "audit_mechanical.py"
_spec = importlib.util.spec_from_file_location("audit_mechanical", SCRIPT)
am = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(am)

HEALTHY_FM = (
    "---\n"
    "name: {name}\n"
    "description: \"Checks widgets for faults. Use when a widget misbehaves. "
    "Triggers: '{name} alpha', '{name} beta'.\"\n"
    "license: MIT\n"
    "metadata:\n"
    "  version: \"1.0.0\"\n"
    "---\n"
)
HEALTHY_BODY = (
    "\n# Widget Check\n\n"
    "Read `references/guide.md` for the procedure, section `references/guide.md#steps`.\n"
    "Run `python3 scripts/check.py` to collect facts.\n"
    "See [the notes](#notes).\n\n"
    "## Notes\n\nNothing else.\n"
)
HEALTHY_FILES = {
    "references/guide.md": "# Guide\n\n## Steps\n\n1. Look.\n",
    "scripts/check.py": "print('ok')\n",
    "README.md": "# readme\n",
    "LICENSE": "MIT\n",
}


def sk_ant() -> str:
    return "sk-" + "ant-api03-" + "Ab3dE5gH7jK9mN1pQ3sT5vW7"


class AuditCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / "corpus"
        self.root.mkdir()

    def tearDown(self):
        self._tmp.cleanup()

    def skill(self, name: str, body: str | None = None, files: dict | None = None,
              fm: str | None = None, healthy_files: bool = True) -> Path:
        path = self.root / name
        path.mkdir(parents=True)
        all_files = dict(HEALTHY_FILES) if healthy_files else {}
        all_files.update(files or {})
        for rel, content in all_files.items():
            p = path / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            if isinstance(content, bytes):
                p.write_bytes(content)
            else:
                p.write_text(content, encoding="utf-8")
        text = (fm if fm is not None else HEALTHY_FM.format(name=name)) + (
            body if body is not None else HEALTHY_BODY)
        (path / "SKILL.md").write_text(text, encoding="utf-8")
        return path

    def run_audit(self) -> dict:
        return am.audit(self.root, 50)

    def findings(self, result: dict, section: str, name: str) -> list[str]:
        return result[section].get(name, [])

    def assertClean(self, result: dict, name: str):
        for section in ("portability", "unreferenced", "effectiveness", "broken_disclosure"):
            self.assertEqual(result[section].get(name, []), [], f"{section}: {result[section].get(name)}")
        self.assertNotIn(name, result["undeclared_triggers"])
        self.assertEqual(result["collisions"], [])


class HealthySkill(AuditCase):
    def test_healthy_skill_has_no_findings(self):
        self.skill("widget-check")
        self.skill("other-check")
        r = self.run_audit()
        self.assertClean(r, "widget-check")
        self.assertClean(r, "other-check")


class Collision(AuditCase):
    def test_shared_triggers_collide(self):
        fm = HEALTHY_FM.format(name="same")
        self.skill("one", fm=fm.replace("name: same", "name: one"))
        self.skill("two", fm=fm.replace("name: same", "name: two"))
        r = self.run_audit()
        self.assertEqual(len(r["collisions"]), 1)
        self.assertEqual(r["collisions"][0]["overlap_pct"], 100)

    def test_distinct_triggers_do_not_collide(self):
        self.skill("one")
        self.skill("two")
        self.assertEqual(self.run_audit()["collisions"], [])

    def test_undeclared_triggers_listed_with_soft_wording(self):
        fm = "---\nname: quiet\ndescription: Checks widgets for faults.\n---\n"
        self.skill("quiet", fm=fm)
        r = self.run_audit()
        self.assertIn("quiet", r["undeclared_triggers"])
        out = subprocess.run([sys.executable, "-I", "-B", str(SCRIPT), str(self.root)],
                             capture_output=True, text=True).stdout
        self.assertIn("declares no quoted trigger phrases; trigger collisions cannot be checked", out)
        self.assertNotIn("may not activate", out)


class BrokenDisclosure(AuditCase):
    def test_missing_plain_reference(self):
        self.skill("s", body=HEALTHY_BODY + "\nRead `references/missing.md` first.\n")
        self.assertIn("references/missing.md", self.run_audit()["broken_disclosure"]["s"])

    def test_missing_prefixed_scripts(self):
        body = HEALTHY_BODY + (
            "\nRun `python3 ${CLAUDE_SKILL_DIR}/scripts/a.py`.\n"
            "Run `python3 $SKILL_ROOT/scripts/b.py`.\n"
            "Run `./scripts/c.sh`.\n")
        self.skill("s", body=body)
        missing = self.run_audit()["broken_disclosure"]["s"]
        for ref in ("scripts/a.py", "scripts/b.py", "scripts/c.sh"):
            self.assertIn(ref, missing)

    def test_missing_script_named_in_reference_file(self):
        self.skill("s", files={"references/workflow.md": "# Flow\n\nRun python3 scripts/migrate.py now.\n"},
                   body=HEALTHY_BODY + "\nFollow `references/workflow.md`.\n")
        self.assertIn("scripts/migrate.py (in references/workflow.md)",
                      self.run_audit()["broken_disclosure"]["s"])

    def test_present_prefixed_scripts_pass(self):
        body = HEALTHY_BODY + "\nRun `python3 ${CLAUDE_SKILL_DIR}/scripts/check.py` and `./scripts/check.py`.\n"
        self.skill("s", body=body)
        self.assertNotIn("s", self.run_audit()["broken_disclosure"])

    def test_other_variable_is_another_tree(self):
        self.skill("s", body=HEALTHY_BODY + "\nRun `python -I $CK/scripts/build_plan.py`.\n")
        self.assertNotIn("s", self.run_audit()["broken_disclosure"])


class Portability(AuditCase):
    def port(self, name="s", fm=None, body=None, files=None):
        path = self.skill(name, fm=fm, body=body, files=files)
        return am.portability(path, (path / "SKILL.md").read_bytes())

    def test_healthy_has_no_findings(self):
        self.assertEqual(self.port(), [])

    def test_unexpected_key_is_error(self):
        fm = HEALTHY_FM.format(name="s").replace("license: MIT\n", "license: MIT\nversion: 1\n")
        self.assertTrue(any(f.startswith("ERROR: unexpected top-level key") for f in self.port(fm=fm)))

    def test_invalid_yaml_is_error(self):
        fm = "---\nname: s\ndescription: \"open quote\n  continues: here\n---\n"
        self.assertTrue(any("invalid YAML" in f for f in self.port(fm=fm)))

    def test_reserved_name_is_error(self):
        fm = HEALTHY_FM.format(name="claude-helper")
        self.assertTrue(any("reserved word" in f for f in self.port("claude-helper", fm=fm)))

    def test_missing_frontmatter_is_error(self):
        self.assertTrue(any(f.startswith("ERROR: frontmatter") for f in self.port(fm="# no frontmatter\n")))

    def test_local_only_downgrades_errors(self):
        fm = HEALTHY_FM.format(name="s").replace(
            "metadata:\n", "version: 1\nmetadata:\n  portability: \"local-only\"\n")
        out = self.port(fm=fm)
        self.assertFalse(any(f.startswith("ERROR") for f in out))
        self.assertTrue(any(f.startswith("WARN (local-only)") for f in out))

    def test_main_warnings(self):
        cases = {
            "Claude Code-only key": HEALTHY_FM.format(name="s").replace("license: MIT\n", "license: MIT\nargument-hint: x\n"),
            "differs from folder": HEALTHY_FM.format(name="other-name"),
            "not a single-line string": HEALTHY_FM.format(name="s").replace(
                'description: "', 'description: >\n  "'),
            "over 500": HEALTHY_FM.format(name="s").replace("Checks widgets", "Checks widgets " + "x" * 520),
        }
        for i, (needle, fm) in enumerate(cases.items()):
            with self.subTest(needle):
                name = "s"
                path = self.root / f"case{i}" / name
                path.mkdir(parents=True)
                (path / "SKILL.md").write_text(fm + HEALTHY_BODY, encoding="utf-8")
                out = am.portability(path, (path / "SKILL.md").read_bytes())
                self.assertTrue(any(f.startswith("WARN") and needle in f for f in out), out)
                self.assertFalse(any(f.startswith("ERROR") for f in out), out)

    def test_crlf_long_body_nested(self):
        path = self.skill("s", body=HEALTHY_BODY + "line\n" * 501,
                          files={"copy/SKILL.md": HEALTHY_FM.format(name="copy")})
        raw = (path / "SKILL.md").read_bytes().replace(b"\n", b"\r\n")
        out = am.portability(path, raw)
        self.assertTrue(any("CRLF" in f for f in out))
        self.assertTrue(any("body is" in f and "keep under 500" in f for f in out))
        self.assertTrue(any("nested SKILL.md" in f for f in out))


class Unreferenced(AuditCase):
    def test_orphan_in_disclosure_dir(self):
        self.skill("s", files={"references/unused.md": "# Unused\n"})
        self.assertTrue(any("references/unused.md" in f for f in self.run_audit()["unreferenced"]["s"]))

    def test_orphan_outside_disclosure_dirs(self):
        self.skill("s", files={"notes/draft.md": "# Draft\n", "stray.txt": "x\n"})
        msg = " ".join(self.run_audit()["unreferenced"]["s"])
        self.assertIn("notes/draft.md", msg)
        self.assertIn("stray.txt", msg)

    def test_stray_backups(self):
        self.skill("s", files={"SKILL.md.bak": HEALTHY_FM.format(name="s"), "scripts/check.py.orig": "x",
                               "notes.old": "x", "guide.md~": "x"})
        msg = " ".join(self.run_audit()["unreferenced"]["s"])
        self.assertIn("4 stray backup file(s)", msg)
        self.assertIn("SKILL.md.bak", msg)

    def test_skill_frontmatter_outside_references(self):
        # Named only by basename, never by path: not a deliberate load.
        self.skill("s", files={"agents/helper.md": "---\nname: helper\ndescription: x\n---\nbody\n"},
                   body=HEALTHY_BODY + "\nA helper.md exists somewhere.\n")
        msg = " ".join(self.run_audit()["unreferenced"]["s"])
        self.assertIn("carry skill frontmatter", msg)
        self.assertIn("agents/helper.md", msg)

    def test_companions_caches_and_archives(self):
        self.skill("s", files={"CHANGELOG.md": "x", "marketplace.json": "{}", "LICENSE.txt": "x",
                               "package.json": "{}", "requirements.txt": "", "pyproject.toml": "",
                               "scripts/__pycache__/check.cpython-311.pyc": b"\0",
                               "bundle.zip": b"PK"})
        msgs = self.run_audit()["unreferenced"]["s"]
        self.assertFalse(any("nothing references" in f for f in msgs), msgs)
        self.assertTrue(any("cache or session-state" in f for f in msgs))
        self.assertTrue(any("packaged archive" in f for f in msgs))

    def test_development_companions_are_not_orphans(self):
        self.skill("s", files={"tests/test_widget.py": "import unittest\n",
                               "tests/fixtures/deep/sample.json": "{}",
                               "evals/evals.json": "[]",
                               "SKILL.md.tmpl": HEALTHY_FM.format(name="s") + "{{BODY}}\n",
                               ".provenance.yaml": "source: upstream\n",
                               ".provenance.json": "{}"})
        self.assertNotIn("s", self.run_audit()["unreferenced"])

    def test_companion_names_outside_their_dirs_still_count(self):
        self.skill("s", files={"misc/test_widget.py": "x\n"})
        self.assertIn("misc/test_widget.py", " ".join(self.run_audit()["unreferenced"]["s"]))

    def test_directory_reference_covers_its_files(self):
        self.skill("s", body=HEALTHY_BODY + "\nPhase scripts live in this skill's pipeline/ folder.\n",
                   files={"pipeline/00-init.py": "x\n", "pipeline/deep/01-step.py": "x\n",
                          "unrelated/orphan.md": "# Orphan\n"})
        msg = " ".join(self.run_audit()["unreferenced"]["s"])
        self.assertNotIn("pipeline/", msg)
        self.assertIn("unrelated/orphan.md", msg)

    def test_glob_covers_matches(self):
        self.skill("s", body=HEALTHY_BODY + "\nValidate against `schemas/*.schema.json`.\n",
                   files={"schemas/a.schema.json": "{}", "schemas/b.schema.json": "{}",
                          "schemas/notes.txt": "x\n", "other/c.schema.json": "{}"})
        msg = " ".join(self.run_audit()["unreferenced"]["s"])
        self.assertNotIn("a.schema.json", msg)
        self.assertNotIn("b.schema.json", msg)
        self.assertIn("schemas/notes.txt", msg)
        self.assertIn("other/c.schema.json", msg)

    def test_range_covers_its_directory(self):
        body = HEALTHY_BODY + "\nRender `prompts/W1-audit.md` through `prompts/W3-plan.md`.\n"
        self.skill("s", body=body, files={"prompts/W1-audit.md": "x", "prompts/W2-mid.md": "x",
                                          "prompts/W3-plan.md": "x", "briefs/W2-mid.md.txt": "x"})
        msg = " ".join(self.run_audit()["unreferenced"]["s"])
        self.assertNotIn("prompts/", msg)
        self.assertIn("briefs/W2-mid.md.txt", msg)

    def test_range_with_missing_endpoint_does_not_cover(self):
        body = HEALTHY_BODY + "\nRender `prompts/W1-audit.md` through `prompts/W9-gone.md`.\n"
        self.skill("s", body=body, files={"prompts/W1-audit.md": "x", "prompts/W2-mid.md": "x"})
        self.assertIn("prompts/W2-mid.md", " ".join(self.run_audit()["unreferenced"]["s"]))

    def test_generic_disclosure_dir_mention_reaches_nothing(self):
        self.skill("s", body=HEALTHY_BODY + "\nKeep deeper content in references/ and scripts/.\n",
                   files={"references/unused.md": "# Unused\n"})
        self.assertIn("references/unused.md", " ".join(self.run_audit()["unreferenced"]["s"]))

    def test_healthy_companions_only(self):
        self.skill("s", files={"CHANGELOG.md": "x", "marketplace.json": "{}"})
        self.assertNotIn("s", self.run_audit()["unreferenced"])


class Effectiveness(AuditCase):
    def eff(self, body=None, files=None, fm=None):
        self.skill("s", body=body, files=files, fm=fm)
        return self.run_audit()

    def msg(self, r) -> str:
        return " | ".join(r["effectiveness"].get("s", []))

    def test_dead_anchor_other_file(self):
        r = self.eff(body=HEALTHY_BODY + "\nSee `references/guide.md#no-such-step`.\n")
        self.assertIn("references/guide.md#no-such-step", self.msg(r))

    def test_output_document_link_is_healthy(self):
        # intent.md is the document a run produces, not a file the skill ships.
        body = HEALTHY_BODY + ("\nThe run writes `intent.md`; link its record as "
                               "`intent.md#prior-art` and the spec as [spec](spec.md#scope).\n")
        self.assertNotIn("s", self.eff(body=body)["effectiveness"])

    def test_missing_file_with_directory_is_dead(self):
        r = self.eff(body=HEALTHY_BODY + "\nSee `references/missing.md#x`.\n")
        self.assertIn("references/missing.md (missing file)", self.msg(r))

    def test_dead_same_file_anchor(self):
        r = self.eff(body=HEALTHY_BODY + "\nJump to [nowhere](#missing-section).\n")
        self.assertIn("SKILL.md#missing-section", self.msg(r))

    def test_anchor_relative_to_holding_file(self):
        files = {"references/a.md": "# A\n\nSee [b](b.md#target) and [bad](b.md#gone).\n",
                 "references/b.md": "# B\n\n## Target\n"}
        r = self.eff(body=HEALTHY_BODY + "\nRead `references/a.md` and `references/b.md`.\n", files=files)
        self.assertIn("b.md#gone", self.msg(r))
        self.assertNotIn("b.md#target", self.msg(r))

    def test_fenced_heading_is_not_an_anchor(self):
        files = {"references/guide.md": "# Guide\n\n## Steps\n\n```markdown\n## Fake Heading\n```\n"}
        r = self.eff(body=HEALTHY_BODY + "\nSee `references/guide.md#fake-heading`.\n", files=files)
        self.assertIn("references/guide.md#fake-heading", self.msg(r))

    def test_ghost_tool(self):
        r = self.eff(body=HEALTHY_BODY + "\nRun `python3 lint_widgets.py` and `bash ${CLAUDE_SKILL_DIR}/scripts/x.sh`.\n")
        self.assertIn("lint_widgets.py", self.msg(r))
        self.assertIn("scripts/x.sh", self.msg(r))

    def test_ghost_tool_in_reference_file(self):
        files = {"references/workflow.md": "# Flow\n\nRun python3 scripts/migrate.py now.\n"}
        r = self.eff(body=HEALTHY_BODY + "\nFollow `references/workflow.md`.\n", files=files)
        self.assertIn("scripts/migrate.py", self.msg(r))

    def test_hidden_skill_in_references(self):
        # Not loaded by path from anywhere: a second skill riding along.
        files = {"references/second.md": "---\nname: second\ndescription: another skill\n---\n# Second\n"}
        r = self.eff(files=files)
        self.assertIn("whole skill definition", self.msg(r))

    def test_private_data_in_any_text_file(self):
        tokens = {
            "scripts/config.json": '{"key": "%s"}' % sk_ant(),
            ".env": "OPENAI=" + "sk-" + "proj-" + "Zz9Yy8Xx7Ww6Vv5Uu4Tt3Ss2" + "\n",
            "references/slack.md": "# S\n\n" + "xox" + "b-1234567890-abcdef\n",
            "scripts/g.py": "K = '" + "AIza" + "B" * 35 + "'\n",
            "scripts/aws.sh": "AWS=" + "AKIA" + "QWERTYUIOPASDFGH" + "\n",
        }
        body = HEALTHY_BODY + "\nRead `references/slack.md`, `scripts/config.json`, `scripts/g.py`, `scripts/aws.sh`.\n"
        r = self.eff(body=body, files=tokens)
        self.assertIn("s", r["effectiveness_errors"])
        for rel in tokens:
            self.assertIn(f"{rel}: credential-shaped token", self.msg(r))

    def test_chat_url_is_private(self):
        r = self.eff(body=HEALTHY_BODY + "\nSource: https://claude.ai/" + "chat/" + "0123abcd-4567\n")
        self.assertIn("claude.ai chat URL", self.msg(r))

    def test_changelog_in_skill(self):
        r = self.eff(body=HEALTHY_BODY + "\n## Changelog\n\n- 1.0.0 first\n")
        self.assertIn("changelog section", self.msg(r))

    def test_budget_reports_kb_and_bytes(self):
        pad = HEALTHY_BODY + "\n" + ("word " * 15 + "\n") * 300
        fm = HEALTHY_FM.format(name="s")
        target = 25_164
        size = len((fm + pad).encode())
        pad += "y" * (target - size - 1) + "\n"
        r = self.eff(body=pad)
        self.assertIn("25.2 KB (25,164 B)", self.msg(r))
        self.assertIn("keep under 25.0 KB (25,000 B)", self.msg(r))

    def test_version_drift(self):
        files = {"references/guide.md": "---\nversion: 0.9.0\n---\n# Guide\n\n## Steps\n"}
        r = self.eff(files=files)
        self.assertIn("carry a version other than 1.0.0", self.msg(r))

    @unittest.skipIf(os.name == "nt", "symlinks need privileges on Windows")
    def test_dangling_symlink(self):
        path = self.skill("s")
        (path / "references" / "gone.md").symlink_to(path / "nowhere.md")
        self.assertIn("dangling symlink", " ".join(self.run_audit()["effectiveness"]["s"]))

    def test_healthy_effectiveness(self):
        self.assertNotIn("s", self.eff()["effectiveness"])


class RegressionFalseAlarms(AuditCase):
    """The three false alarms the 2026-11-10 validation found, plus the
    documentation key and the KB message."""

    def test_path_in_another_tree(self):
        body = HEALTHY_BODY + (
            "\n## Phase 6 - living document\n"
            "`C:\\Users\\Administrator\\Downloads\\x.livingdoc`: back up `public/app.js` and "
            "`data/annotations.json`, then run `node --check public/app.js`.\n"
            "Also edit `/mnt/c/work/data/other.json` and `~/notes/data/third.json`.\n")
        self.skill("system-checkup", body=body, fm=HEALTHY_FM.format(name="system-checkup"))
        r = self.run_audit()
        self.assertNotIn("system-checkup", r["broken_disclosure"])
        self.assertNotIn("system-checkup", r["effectiveness"])

    def test_user_project_files_are_not_ghosts(self):
        body = HEALTHY_BODY + (
            "\nRun `python manage.py migrate` in your project.\n"
            "Then run `node server.js`.\n"
            "In the repo, run `python tools/seed_db.py` and `bash build_all.sh`.\n")
        self.skill("s", body=body)
        self.assertNotIn("s", self.run_audit()["effectiveness"])

    def test_template_frontmatter_is_not_version_drift(self):
        files = {"assets/intent-template.md": "---\nver: 2.0.0\nversion: 0.1.0\n---\n# Intent\n",
                 "references/templates/report.md": "---\nversion: 3.0.0\n---\n# Report\n"}
        body = HEALTHY_BODY + "\nCopy `assets/intent-template.md` and `references/templates/report.md`.\n"
        self.skill("s", body=body, files=files)
        self.assertNotIn("s", self.run_audit()["effectiveness"])

    def test_documented_example_keys_allowed(self):
        body = HEALTHY_BODY + ("\nAWS documents the example key AKIAIOSFODNN7EXAMPLE.\n"
                               "A Slack token looks like `" + "xox" + "b-your-token-here`.\n")
        self.skill("s", body=body)
        r = self.run_audit()
        self.assertNotIn("s", r["effectiveness_errors"])

    def test_other_skill_reference_is_not_broken(self):
        body = HEALTHY_BODY + "\nFor the full list, see the **humanize-writing** skill's `references/ai-vocabulary-list.md`.\n"
        self.skill("s", body=body)
        self.assertNotIn("s", self.run_audit()["broken_disclosure"])

    def test_referenced_rubric_with_frontmatter_is_healthy(self):
        # skill-doctor loads $SKILL_ROOT/scorers/*.md, upstream rubrics that
        # carry their own name/description keys (judgment kept from b4886c1).
        rubric = "---\nname: efficiency\ndescription: scores efficiency\n---\n# Efficiency\n"
        body = HEALTHY_BODY + ("\nScore with `$SKILL_ROOT/scorers/efficiency.md` and "
                               "`references/protocol.md`.\n")
        self.skill("s", body=body, files={"scorers/efficiency.md": rubric, "references/protocol.md": rubric})
        r = self.run_audit()
        self.assertNotIn("s", r["unreferenced"])
        self.assertNotIn("s", r["effectiveness"])

    def test_unreferenced_rubric_with_frontmatter_is_flagged(self):
        rubric = "---\nname: efficiency\ndescription: scores efficiency\n---\n# Efficiency\n"
        self.skill("s", files={"scorers/efficiency.md": rubric, "references/protocol.md": rubric})
        r = self.run_audit()
        self.assertIn("scorers/efficiency.md", " ".join(
            f for f in r["unreferenced"]["s"] if "carry skill frontmatter" in f))
        self.assertIn("references/protocol.md", " ".join(r["effectiveness"]["s"]))

    def test_referenced_backup_with_frontmatter_is_still_flagged(self):
        self.skill("s", body=HEALTHY_BODY + "\nThe old copy is `old/SKILL.md.bak`.\n",
                   files={"old/SKILL.md.bak": HEALTHY_FM.format(name="s")})
        msg = " ".join(self.run_audit()["unreferenced"]["s"])
        self.assertIn("stray backup", msg)
        self.assertIn("carry skill frontmatter", msg)

    def test_reference_file_describing_outputs_is_not_broken(self):
        files = {"references/patterns.md": (
            "# Patterns\n\nCreate one script per operation:\n\n```text\nscripts/get_item.py\n```\n\n"
            "Store snippets in a `references/starter-code.md` file.\n")}
        self.skill("s", body=HEALTHY_BODY + "\nRead `references/patterns.md`.\n", files=files)
        self.assertNotIn("s", self.run_audit()["broken_disclosure"])


if __name__ == "__main__":
    unittest.main()
