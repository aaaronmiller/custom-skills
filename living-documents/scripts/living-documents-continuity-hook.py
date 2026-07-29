#!/usr/bin/env python3
"""Non-mutating continuity hook for local coding harnesses.

This hook is deliberately advisory: it locates canonical Living Documents
context and reports whether a durable handoff is present. It never edits a
Living Document from a prompt or tool event, preventing feedback-loop churn.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

HOME = Path.home()
DOCUMENTS = HOME / "LIVING_DOCUMENTS" / "projects"
STATE = HOME / ".local" / "state" / "living-documents" / "handoffs"
LEDGER = HOME / ".local" / "state" / "living-documents" / "ledger"
LEDGER_TOOL = Path(__file__).with_name("ld-ledger")
UNFINISHED = {"active", "interrupted", "unclassified", "blocked"}
ACTIONABLE = {"active", "interrupted", "unclassified"}


def event(payload: dict[str, Any]) -> str:
    return str(payload.get("hook_event_name") or payload.get("event") or payload.get("event_type") or "").lower()


def cwd(payload: dict[str, Any]) -> Path:
    raw = str(payload.get("cwd") or os.getcwd())
    try:
        return Path(raw).expanduser().resolve()
    except OSError:
        return Path(raw)


def project_for(path: Path) -> str:
    """Resolve only existing canonical projects; unknown paths stay universal."""
    for candidate in (path, *path.parents):
        name = candidate.name
        if (DOCUMENTS / name / "start-here.md").is_file():
            return name
    return "living-documents"


def key(project: str, path: Path) -> str:
    return hashlib.sha256(f"{project}:{path}".encode()).hexdigest()[:16]


def latest_handoff(project: str) -> Path | None:
    """Return the newest explicit project handoff, never inventing one."""
    directory = STATE / project
    if not directory.is_dir():
        return None
    candidates = [item for item in directory.glob("*.json") if item.is_file()]
    return max(candidates, key=lambda item: item.stat().st_mtime) if candidates else None


def continuation_state() -> dict[str, Any]:
    """Use the canonical resolver, with a bounded read-only fallback."""
    try:
        completed = subprocess.run(
            [str(LEDGER_TOOL), "next"],
            check=True,
            capture_output=True,
            text=True,
            timeout=2,
        )
        resolved = json.loads(completed.stdout)
        state = resolved.get("state")
        if state == "actionable":
            record = resolved.get("record") or {}
            return {
                "state": "actionable",
                "work_id": record.get("work_id"),
                "project": record.get("project"),
                "next_action": resolved.get("next_action") or record.get("next_action"),
            }
        if state == "review-pending":
            reviews = [{
                "priority": review.get("priority"),
                "option_id": review.get("option_id"),
                "note": review.get("note"),
                "updated_at": review.get("updated_at"),
                "work_ids": review.get("work_ids", []),
                "local_only": True,
            } for review in resolved.get("reviews", [])]
            return {
                "state": "review-pending",
                "reviews": reviews,
                "required_action": "Inspect the local-only review, record any valid authorization canonically, then run only its named gate.",
            }
        if state == "pivot-required":
            return {
                "state": "pivot-required",
                "pivot_project": resolved.get("pivot_project", "living-documents"),
                "blocker_count": len(resolved.get("blockers", [])),
                "required_action": "Create or select an independent Living Documents control-plane pivot; do not end work because the project queue is blocked.",
            }
        if state == "complete":
            return {"state": "no-unfinished-ledger-record"}
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError):
        pass

    # Fallback stays non-mutating if the canonical resolver is unavailable.
    records: list[dict[str, Any]] = []
    if LEDGER.is_dir():
        for item in LEDGER.glob("*.json"):
            try:
                value = json.loads(item.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if isinstance(value, dict) and value.get("status") in UNFINISHED:
                records.append(value)
    actionable = [item for item in records if item.get("status") in ACTIONABLE]
    if actionable:
        selected = max(actionable, key=lambda item: (str(item.get("updated_at", "")), str(item.get("work_id", ""))))
        return {
            "state": "actionable",
            "work_id": selected.get("work_id"),
            "project": selected.get("project"),
            "next_action": selected.get("next_action"),
        }
    if records:
        return {
            "state": "pivot-required",
            "pivot_project": "living-documents",
            "blocker_count": len(records),
            "required_action": "Create or select an independent Living Documents control-plane pivot; do not end work because the project queue is blocked.",
        }
    return {"state": "no-unfinished-ledger-record"}


def result(payload: dict[str, Any]) -> dict[str, Any]:
    path = cwd(payload)
    project = project_for(path)
    start = DOCUMENTS / project / "start-here.md"
    handoff = latest_handoff(project)
    expected = STATE / f"{key(project, path)}.json"
    current_event = event(payload)
    base: dict[str, Any] = {
        "type": "living-documents-continuity",
        "event": current_event or "unknown",
        "project": project,
        "start_here": str(start),
        "handoff": str(handoff or expected),
        "mode": "advisory-no-auto-write",
    }
    if current_event in {"stop", "session_end", "sessionend", "pre_compact", "precompact"}:
        base["handoff_present"] = handoff is not None
        if handoff is not None:
            base["latest_handoff"] = str(handoff)
        base["continuation"] = continuation_state()
        base["required_action"] = (
            "Record a compact handoff only if this session performed substantial work "
            "or changed a material directive, task, decision, blocker, evidence, or next action. "
            "Before a terminal response, inspect continuation: if it is pivot-required, select and record a control-plane pivot instead of stopping."
        )
    else:
        base["required_action"] = (
            "For substantial work, read start-here.md and the active task before acting; "
            "do not write Living Documents for ordinary chat or tool activity."
        )
    return base


def additional_context(record: dict[str, Any]) -> str:
    """Return a compact, model-visible orientation clause."""
    return (
        f"Living Documents project: {record['project']}. "
        f"Start here: {record['start_here']}. "
        "For substantial work, read the canonical page before planning or consequential writes. "
        "Record only material intent, task, decision, evidence, blocker, gate, or next-action changes; "
        "ordinary prompts and tool calls never trigger automatic document edits."
    )


def continuation_prompt(continuation: dict[str, Any]) -> str | None:
    """Translate resolver state into one bounded Stop continuation."""
    state = continuation.get("state")
    if state == "actionable":
        return (
            f"Continue canonical work {continuation.get('work_id')} for "
            f"{continuation.get('project')}. Next action: "
            f"{continuation.get('next_action')}"
        )
    if state == "review-pending":
        reviews = continuation.get("reviews") or []
        review = reviews[0] if reviews else {}
        return (
            "A loopback-local Living Documents review is pending. "
            f"Inspect option {review.get('option_id')} for work IDs "
            f"{review.get('work_ids', [])}; record valid authorization canonically, "
            "then run only the mapped gate."
        )
    if state == "pivot-required":
        return (
            f"All {continuation.get('blocker_count', 0)} queued project items are blocked. "
            "Select and record one independent Living Documents control-plane pivot, "
            "perform its bounded gate, and preserve the project authority blockers."
        )
    return None


def harness_output(payload: dict[str, Any], record: dict[str, Any]) -> dict[str, Any]:
    """Emit only fields accepted by current Claude Code and Codex hooks."""
    current_event = event(payload)
    canonical_events = {
        "sessionstart": "SessionStart",
        "session_start": "SessionStart",
        "userpromptsubmit": "UserPromptSubmit",
        "user_prompt_submit": "UserPromptSubmit",
    }
    if current_event in canonical_events:
        return {
            "continue": True,
            "hookSpecificOutput": {
                "hookEventName": canonical_events[current_event],
                "additionalContext": additional_context(record),
            },
        }
    if current_event == "stop":
        # Both harnesses set this after a Stop hook already continued once.
        # Allowing the second stop prevents an endless continuation loop.
        if bool(payload.get("stop_hook_active")):
            return {"continue": True}
        prompt = continuation_prompt(record.get("continuation") or {})
        if prompt:
            return {"decision": "block", "reason": prompt}
        return {"continue": True}
    return {"continue": True}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--allow-json", action="store_true")
    parser.add_argument(
        "--harness-output",
        action="store_true",
        help="Emit the current Claude Code/Codex hook response contract.",
    )
    args = parser.parse_args()
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        payload = {}
    try:
        record = result(payload)
        if args.harness_output:
            print(json.dumps(harness_output(payload, record), ensure_ascii=False))
        elif args.allow_json:
            print(json.dumps({"type": "allow", "continuity": record}, ensure_ascii=False))
        else:
            print(json.dumps(record, ensure_ascii=False))
    except Exception:
        # Hooks must never block a working session.
        if args.harness_output:
            print('{"continue":true}')
        elif args.allow_json:
            print('{"type":"allow"}')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
