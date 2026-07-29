"""Cross-harness contract tests for the Living Documents continuity hook."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "living-documents-continuity-hook.py"
)
SPEC = importlib.util.spec_from_file_location("continuity_hook", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class ContinuityHookContractTests(unittest.TestCase):
    def test_session_start_emits_additional_context(self):
        payload = {"hook_event_name": "SessionStart", "cwd": "/home/cheta"}
        record = MODULE.result(payload)
        output = MODULE.harness_output(payload, record)
        specific = output["hookSpecificOutput"]
        self.assertTrue(output["continue"])
        self.assertEqual(specific["hookEventName"], "SessionStart")
        self.assertIn("Start here:", specific["additionalContext"])

    def test_prompt_submit_emits_matching_event_name(self):
        payload = {"hook_event_name": "UserPromptSubmit", "cwd": "/home/cheta"}
        output = MODULE.harness_output(payload, MODULE.result(payload))
        self.assertEqual(
            output["hookSpecificOutput"]["hookEventName"],
            "UserPromptSubmit",
        )

    def test_actionable_stop_continues_once(self):
        record = {
            "continuation": {
                "state": "actionable",
                "work_id": "wr-002",
                "project": "weekly-reports",
                "next_action": "Collect another checkpoint.",
            }
        }
        output = MODULE.harness_output({"hook_event_name": "Stop"}, record)
        self.assertEqual(output["decision"], "block")
        self.assertIn("wr-002", output["reason"])

    def test_second_stop_allows_exit(self):
        payload = {"hook_event_name": "Stop", "stop_hook_active": True}
        record = {"continuation": {"state": "actionable"}}
        self.assertEqual(
            MODULE.harness_output(payload, record),
            {"continue": True},
        )

    def test_pivot_stop_preserves_authority_gate(self):
        record = {
            "continuation": {
                "state": "pivot-required",
                "blocker_count": 7,
            }
        }
        output = MODULE.harness_output({"hook_event_name": "Stop"}, record)
        self.assertEqual(output["decision"], "block")
        self.assertIn("control-plane pivot", output["reason"])

    def test_question_response_interrupts_stop_with_exact_receipt(self):
        record = {
            "continuation": {
                "state": "review-pending",
                "question_responses": [{
                    "receipt_id": "qr-1234-abcd",
                    "project": "agentic-operating-system",
                    "section_id": "current-project-intake",
                    "source_href": "/projects/agentic-operating-system/#current-project-intake",
                }],
            }
        }
        output = MODULE.harness_output({"hook_event_name": "Stop"}, record)
        self.assertEqual(output["decision"], "block")
        self.assertIn("qr-1234-abcd", output["reason"])
        self.assertIn("Living Documents input received", output["reason"])


if __name__ == "__main__":
    unittest.main()
