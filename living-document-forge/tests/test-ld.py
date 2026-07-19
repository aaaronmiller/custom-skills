#!/usr/bin/env python3

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
LD = ROOT / "bin/ld"
VALIDATOR = ROOT / "scripts/validate-living-document.mjs"


class LdCommandTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="ld-test-")
        self.root = Path(self.temp.name)
        self.home = self.root / "living-documents"
        self.project = self.root / "sample-project"
        self.project.mkdir()
        (self.project / ".git").mkdir()
        self.env = os.environ.copy()
        self.env.update({
            "LD_HOME": str(self.home),
            "LD_SKILL_ROOT": str(ROOT),
            "LD_TIMESTAMP": "2026-07-01T00:00:00Z",
        })

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_ld(self, *args: str) -> dict:
        completed = subprocess.run(
            ["python3", str(LD), *args],
            check=True,
            text=True,
            capture_output=True,
            env=self.env,
        )
        return json.loads(completed.stdout)

    def validate(self, root: str) -> None:
        subprocess.run(
            ["node", str(VALIDATOR), root],
            check=True,
            text=True,
            capture_output=True,
            env=self.env,
        )

    def test_universal_create_and_idempotence(self) -> None:
        first = self.run_ld("ensure", "--scope", "universal", "--month", "2026-07")
        second = self.run_ld("--scope", "universal", "--month", "2026-07")
        self.assertEqual(first["action"], "created")
        self.assertEqual(second["action"], "existing")
        self.assertEqual(first["root"], second["root"])
        self.validate(first["root"])
        pointer = json.loads((self.home / "universal/current.json").read_text())
        self.assertEqual(pointer["documentId"], "universal-2026-07")

    def test_project_auto_routing(self) -> None:
        result = self.run_ld("ensure", "--project", str(self.project), "--month", "2026-07")
        self.assertEqual(result["scope"], "project")
        self.assertEqual(Path(result["root"]).parent, self.project / ".living-documents")
        self.validate(result["root"])

    def test_month_rollover_is_non_destructive(self) -> None:
        july = self.run_ld("ensure", "--scope", "universal", "--month", "2026-07")
        july_manifest = Path(july["manifest"])
        before = july_manifest.read_bytes()
        august = self.run_ld("ensure", "--scope", "universal", "--month", "2026-08")
        self.assertEqual(august["rolledOverFrom"], july["root"])
        self.assertEqual(july_manifest.read_bytes(), before)
        manifest = json.loads(Path(august["manifest"]).read_text())
        self.assertEqual(manifest["meta"]["continuity"]["previousDocumentId"], "universal-2026-07")
        self.assertTrue(any(item["kind"] == "rollover" for item in manifest["history"]))
        registry = json.loads((self.home / "living-documents-index.json").read_text())
        states = {item["documentId"]: item["status"] for item in registry["documents"]}
        self.assertEqual(states["universal-2026-07"], "archived")
        self.assertEqual(states["universal-2026-08"], "active")
        self.validate(august["root"])

    def test_dry_run_creates_nothing(self) -> None:
        result = self.run_ld("ensure", "--scope", "universal", "--month", "2026-07", "--dry-run")
        self.assertTrue(result["dryRun"])
        self.assertFalse(self.home.exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
