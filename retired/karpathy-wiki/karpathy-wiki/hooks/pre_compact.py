#!/usr/bin/env python3
"""Pre-compaction hook — extracts session context before compression discards it."""
import json, os, sys
from pathlib import Path

AI_WIKI = Path(os.environ.get("AI_WIKI", Path.home() / "ai-wiki"))
RAW_DIR = AI_WIKI / "raw"
PAGES_DIR = AI_WIKI / "pages"
LOG_FILE = PAGES_DIR / "log.md"

RAW_DIR.mkdir(parents=True, exist_ok=True)
PAGES_DIR.mkdir(parents=True, exist_ok=True)

# Read session transcript from hook input
try:
    hook_input = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}
    session_id = hook_input.get("session_id", "unknown")
    transcript_path = hook_input.get("transcript_path", "")
except (json.JSONDecodeError, Exception):
    session_id = "unknown"
    transcript_path = ""

# Write a daily log entry capturing that we hit compaction
from datetime import date
today = date.today().isoformat()
log_entry = f"## {today} | pre-compact | session={session_id}\n"

with open(LOG_FILE, "a") as f:
    f.write(log_entry)

print(json.dumps({"status": "ok", "log_entry": log_entry}))
