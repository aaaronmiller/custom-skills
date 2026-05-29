#!/usr/bin/env python3
"""
Prompt Mine — Roo/Kilo Code Conversation Extractor

Extracts conversation history from Roo Code and Kilo Code VS Code
extension storage directories.

Usage:
    python extract_roo_kilo.py --storage-path PATH [--kilo-path PATH]
                               [--db-path PATH] [--dry-run]
"""

import argparse
import hashlib
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


def compute_file_hash(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def unix_ms_to_iso(ts) -> str:
    """Convert Unix millisecond timestamp to ISO 8601."""
    if ts is None:
        return datetime.now(timezone.utc).isoformat()
    if isinstance(ts, (int, float)):
        return datetime.fromtimestamp(ts / 1000.0, tz=timezone.utc).isoformat()
    if isinstance(ts, str):
        try:
            return datetime.fromisoformat(ts.replace("Z", "+00:00")).isoformat()
        except ValueError:
            return ts
    return str(ts)


def generate_summary(text: str, max_length: int = 200) -> str:
    if len(text) <= max_length:
        return text
    sentences = text.split(". ")
    if len(sentences) <= 2:
        return text[:max_length - 3] + "..."
    return f"{sentences[0]}. [...] {sentences[-1]}"[:max_length]


def generate_truncated(text: str, last_n_lines: int = 50) -> str:
    summary = generate_summary(text)
    lines = text.splitlines()
    if len(lines) <= last_n_lines + 5:
        return text
    return f"{summary}\n\n--- last {last_n_lines} lines ---\n\n" + "\n".join(lines[-last_n_lines:])


def process_task_file(
    conn: sqlite3.Connection,
    filepath: str,
    provider: str,
    dry_run: bool = False,
) -> tuple[int, int, int]:
    """Process a single Roo/Kilo task file."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"  ERROR reading {filepath}: {e}")
        return 0, 0, 1

    # Extract session info
    task_ts = data.get("ts", 0)
    session_id = f"{provider}-{Path(filepath).stem}"
    workspace = data.get("workspace", "")
    project_name = Path(workspace).name if workspace else "unknown"
    session_title = data.get("task", "")[:120] or None
    model_id = data.get("model")
    source_hash = compute_file_hash(filepath)

    # Check for existing
    existing = conn.execute(
        "SELECT id, source_hash FROM conversations WHERE provider = ? AND session_id = ?",
        (provider, session_id),
    ).fetchone()

    if existing and existing[1] == source_hash:
        return 0, 1, 0

    conversations = data.get("conversations", [])
    if not conversations:
        return 0, 1, 0

    # Determine timestamps
    first_ts = conversations[0].get("ts", task_ts) if conversations else task_ts
    last_ts = conversations[-1].get("ts", task_ts) if conversations else task_ts
    created_at = unix_ms_to_iso(first_ts)
    updated_at = unix_ms_to_iso(last_ts)

    if dry_run:
        print(f"  [DRY RUN] Would ingest: {filepath} ({len(conversations)} turns)")
        return len(conversations), 0, 0

    try:
        if existing:
            conv_id = existing[0]
            conn.execute(
                """UPDATE conversations SET
                    session_title = ?, source_hash = ?, updated_at = ?,
                    ingested_at = strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
                WHERE id = ?""",
                (session_title, source_hash, updated_at, conv_id),
            )
            conn.execute("DELETE FROM conversation_turns WHERE conversation_id = ?", (conv_id,))
        else:
            cursor = conn.execute(
                """INSERT INTO conversations
                    (provider, session_id, session_title, project_name, model_id,
                     source_path, source_hash, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (provider, session_id, session_title, project_name, model_id,
                 filepath, source_hash, created_at, updated_at),
            )
            conv_id = cursor.lastrowid

        turn_count = 0
        user_turn_count = 0
        total_chars = 0

        for idx, conv in enumerate(conversations):
            role = conv.get("role", "tool")
            if role not in ("user", "assistant", "system", "tool"):
                role = "tool"

            content = conv.get("content", "")
            if isinstance(content, list):
                content = " ".join(
                    block.get("text", "") for block in content
                    if isinstance(block, dict) and block.get("type") == "text"
                )
            content_text = str(content) if content else ""
            char_count = len(content_text)
            total_chars += char_count

            if role == "user":
                user_turn_count += 1

            content_summary = None
            content_truncated = None
            if role == "assistant" and char_count > 2000:
                content_summary = generate_summary(content_text)
                content_truncated = generate_truncated(content_text)

            tool_calls_json = None
            if conv.get("toolCalls"):
                tool_calls_json = json.dumps(conv["toolCalls"])

            turn_ts = conv.get("ts", task_ts)
            turn_created = unix_ms_to_iso(turn_ts)

            conn.execute(
                """INSERT INTO conversation_turns
                    (conversation_id, turn_index, role, content_text, content_summary,
                     content_truncated, model_id, tool_calls, char_count,
                     token_estimate, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (conv_id, idx, role, content_text, content_summary, content_truncated,
                 model_id, tool_calls_json, char_count, char_count // 4, turn_created),
            )
            turn_count += 1

        conn.execute(
            """UPDATE conversations SET
                turn_count = ?, user_turn_count = ?, total_chars = ?,
                updated_at = ?, ingested_at = strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
            WHERE id = ?""",
            (turn_count, user_turn_count, total_chars, updated_at, conv_id),
        )

        return turn_count, 0, 0

    except Exception as e:
        print(f"  ERROR processing {filepath}: {e}")
        conn.execute(
            """INSERT INTO extraction_errors
                (provider, source_path, error_type, error_message)
            VALUES (?, ?, ?, ?)""",
            (provider, filepath, "parse_error", str(e)),
        )
        return 0, 0, 1


def find_task_files(storage_path: str, provider: str) -> list[str]:
    """Find all task JSON files in a Roo/Kilo storage directory."""
    tasks_dir = Path(os.path.expanduser(storage_path)) / "tasks"
    if not tasks_dir.exists():
        return []
    return sorted(str(f) for f in tasks_dir.glob("*.json"))


def main():
    parser = argparse.ArgumentParser(description="Extract Roo/Kilo Code conversations")
    parser.add_argument("--storage-path",
                        default="~/.config/Code/User/globalStorage/rooveterinaryinc.roo-cline",
                        help="Path to Roo Code storage directory")
    parser.add_argument("--kilo-path",
                        default="~/.config/Code/User/globalStorage/kilocode.kilo-code",
                        help="Path to Kilo Code storage directory")
    parser.add_argument("--db-path",
                        default=os.path.expanduser("~/.prompt-mine/prompt_mine.db"),
                        help="Path to the SQLite database")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not os.path.exists(args.db_path):
        print(f"Database not found at {args.db_path}")
        print("Run init_database.py first.")
        sys.exit(1)

    conn = sqlite3.connect(args.db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")

    total_added = 0
    total_skipped = 0
    total_errors = 0

    # Process Roo Code
    roo_files = find_task_files(args.storage_path, "roo")
    print(f"Found {len(roo_files)} Roo Code task files")
    for filepath in roo_files:
        added, skipped, errors = process_task_file(conn, filepath, "roo", args.dry_run)
        total_added += added
        total_skipped += skipped
        total_errors += errors

    # Process Kilo Code
    if args.kilo_path:
        kilo_files = find_task_files(args.kilo_path, "kilo")
        print(f"Found {len(kilo_files)} Kilo Code task files")
        for filepath in kilo_files:
            added, skipped, errors = process_task_file(conn, filepath, "kilo", args.dry_run)
            total_added += added
            total_skipped += skipped
            total_errors += errors

    conn.commit()
    conn.close()

    print(f"\nExtraction complete:")
    print(f"  Turns added:    {total_added}")
    print(f"  Sessions skipped: {total_skipped}")
    print(f"  Errors:         {total_errors}")


if __name__ == "__main__":
    main()
