#!/usr/bin/env python3
"""Session-end hook — captures session transcript as a raw source for the wiki."""
import json, os, sys, shutil
from datetime import date, datetime
from pathlib import Path

AI_WIKI = Path(os.environ.get("AI_WIKI", Path.home() / "ai-wiki"))
RAW_DIR = AI_WIKI / "raw"
PAGES_DIR = AI_WIKI / "pages"
LOG_FILE = PAGES_DIR / "log.md"

RAW_DIR.mkdir(parents=True, exist_ok=True)
PAGES_DIR.mkdir(parents=True, exist_ok=True)

try:
    hook_input = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}
    session_id = hook_input.get("session_id", "unknown")
    transcript_path = hook_input.get("transcript_path", "")
    cwd = hook_input.get("cwd", "")
except (json.JSONDecodeError, Exception):
    session_id = "unknown"
    transcript_path = ""
    cwd = ""

# If we have a transcript, copy it to raw/ as a daily log
if transcript_path and os.path.exists(transcript_path):
    today = date.today().isoformat()
    timestamp = datetime.now().strftime("%H%M%S")
    dest = RAW_DIR / f"{today}-session-{timestamp}.md"
    try:
        shutil.copy2(transcript_path, dest)
        log_entry = f"## {today} | session-end | session={session_id} → {dest.name}\n"
        with open(LOG_FILE, "a") as f:
            f.write(log_entry)
    except (OSError, shutil.Error):
        pass

print(json.dumps({"status": "ok", "captured": bool(transcript_path)}))
