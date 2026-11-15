"""Contract tests for managed harness-rule installation."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "install-living-documents-rules.py"
)
SPEC = importlib.util.spec_from_file_location("rules_installer", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class HarnessRulesInstallerTests(unittest.TestCase):
    def test_append_preserves_existing_rules(self):
        merged = MODULE.merge_rules("# Existing\n\nKeep me.\n", MODULE.START + "\nnew\n" + MODULE.END)
        self.assertIn("# Existing", merged)
        self.assertIn("Keep me.", merged)
        self.assertEqual(merged.count(MODULE.START), 1)

    def test_second_install_replaces_without_duplication(self):
        first = MODULE.merge_rules("prefix\n", MODULE.START + "\none\n" + MODULE.END)
        second = MODULE.merge_rules(first, MODULE.START + "\ntwo\n" + MODULE.END)
        self.assertNotIn("\none\n", second)
        self.assertIn("\ntwo\n", second)
        self.assertEqual(second.count(MODULE.START), 1)

    def test_legacy_section_is_migrated_in_place(self):
        existing = (
            "# Rules\n\n## LIVING DOCUMENTS\n\nold contract\n\n"
            "## CASS SESSION EVIDENCE\n\nkeep cass\n"
        )
        block = MODULE.START + "\nnew contract\n" + MODULE.END
        merged = MODULE.merge_rules(existing, block)
        self.assertNotIn("old contract", merged)
        self.assertIn("new contract", merged)
        self.assertIn("## CASS SESSION EVIDENCE", merged)
        self.assertIn("keep cass", merged)

    def test_mismatched_marker_is_rejected(self):
        with self.assertRaises(ValueError):
            MODULE.merge_rules(MODULE.START + "\nbroken\n", "replacement")


if __name__ == "__main__":
    unittest.main()
