"""Receipt and acknowledgement tests for browser-submitted change requests."""
from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "ld-ledger"


class ChangeRequestLedgerTests(unittest.TestCase):
    def test_pending_change_preempts_work_and_can_be_acknowledged(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            project = home / "LIVING_DOCUMENTS" / "projects" / "living-documents"
            project.mkdir(parents=True)
            (project / "start-here.md").write_text("# Start\n", encoding="utf-8")
            receipt_id = "cr-1234-abcd"
            receipt = (
                home
                / ".local"
                / "state"
                / "living-documents"
                / "change-requests"
                / "living-documents"
                / f"{receipt_id}.json"
            )
            receipt.parent.mkdir(parents=True)
            receipt.write_text(
                json.dumps(
                    {
                        "schema": "living-documents-change-request/v1",
                        "receiptId": receipt_id,
                        "projectId": "living-documents",
                        "changeCount": 2,
                        "request": {"annotations": [{"text": "first"}, {"text": "second"}]},
                        "submittedAt": "2026-07-29T00:00:00Z",
                        "status": "pending",
                        "localOnly": True,
                        "sourceHref": "/projects/living-documents/#view=changes",
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            environment = {**os.environ, "HOME": str(home)}
            pending = subprocess.run(
                [str(SCRIPT), "next"],
                check=True,
                capture_output=True,
                text=True,
                env=environment,
            )
            result = json.loads(pending.stdout)
            self.assertEqual(result["state"], "review-pending")
            self.assertEqual(result["change_requests"][0]["receipt_id"], receipt_id)
            acknowledged = subprocess.run(
                [str(SCRIPT), "ack-change", "--receipt-id", receipt_id],
                check=True,
                capture_output=True,
                text=True,
                env=environment,
            )
            self.assertIn(str(receipt), acknowledged.stdout)
            saved = json.loads(receipt.read_text(encoding="utf-8"))
            self.assertEqual(saved["status"], "consumed")
            self.assertIn("consumedAt", saved)


if __name__ == "__main__":
    unittest.main()
