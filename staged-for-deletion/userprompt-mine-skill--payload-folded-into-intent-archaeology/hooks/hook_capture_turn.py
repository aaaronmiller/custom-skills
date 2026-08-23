#!/usr/bin/env python3
"""
Prompt Mine — Claude Code Hook Script

Captures conversation turns via Claude Code hooks. This script is triggered
by PostToolUse and SessionEnd events to record new conversation data.

Hook events receive JSON on stdin with event details.

Usage (invoked automatically by Claude Code hooks):
    python hook_capture_turn.py post-tool-use
    python hook_capture_turn.py session-end
"""

import json
import os
import sqlite3
import sys
from datetime import datetime, timezone

DB_PATH = os.path.expanduser("~/.prompt-mine/prompt_mine.db")
CAPTURE_ENABLED_FILE = os.path.expanduser("~/.prompt-mine/.realtime-capture-enabled")


def is_capture_enabled() -> bool:
    """Check if real-time capture is enabled."""
    if not os.path.exists(CAPTURE_ENABLED_FILE):
        return False
    try:
        with open(CAPTURE_ENABLED_FILE, "r") as f:
            return f.read().strip().lower() in ("true", "1", "yes")
    except IOError:
        return False


def read_hook_input() -> dict:
    """Read JSON input from stdin (provided by Claude Code hook system)."""
    try:
        input_data = sys.stdin.read()
        if input_data.strip():
            return json.loads(input_data)
    except json.JSONDecodeError:
        pass
    return {}


def handle_post_tool_use(event_data: dict):
    """Handle PostToolUse event — record the tool use if capture is enabled."""
    if not is_capture_enabled():
        return

    if not os.path.exists(DB_PATH):
        return

    tool_name = event_data.get("tool_name", "")
    tool_input = event_data.get("tool_input", {})
    # We don't capture tool output from hooks — that's in the extraction scripts
    # This hook is mainly for triggering incremental ingest checks


def handle_session_end(event_data: dict):
    """Handle SessionEnd event — check for new conversations to ingest."""
    if not os.path.exists(DB_PATH):
        return

    # Light check: see if there are new session files since last ingest
    try:
        conn = sqlite3.connect(DB_PATH)
        last_ingest = conn.execute(
            """SELECT MAX(completed_at) FROM ingest_log
               WHERE provider = 'claude-code' AND status = 'completed'"""
        ).fetchone()[0]

        # If no ingest in the last hour, suggest running incremental ingest
        if last_ingest:
            from datetime import datetime
            last_dt = datetime.fromisoformat(last_ingest.replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            hours_since = (now - last_dt).total_seconds() / 3600
            if hours_since > 1:
                # Write a flag file indicating ingest is needed
                flag_path = os.path.expanduser("~/.prompt-mine/.ingest-needed")
                with open(flag_path, "w") as f:
                    f.write(now.isoformat())

        conn.close()
    except Exception:
        pass


def main():
    if len(sys.argv) < 2:
        print("Usage: hook_capture_turn.py [post-tool-use|session-end]", file=sys.stderr)
        sys.exit(1)

    hook_type = sys.argv[1]
    event_data = read_hook_input()

    if hook_type == "post-tool-use":
        handle_post_tool_use(event_data)
    elif hook_type == "session-end":
        handle_session_end(event_data)
    else:
        print(f"Unknown hook type: {hook_type}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
