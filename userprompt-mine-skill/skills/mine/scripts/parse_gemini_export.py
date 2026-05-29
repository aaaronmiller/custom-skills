#!/usr/bin/env python3
"""
Prompt Mine — Google Gemini Data Export Parser

Parses conversation JSON files from a Google Takeout export.

Usage:
    python parse_gemini_export.py --export-dir PATH [--db-path PATH] [--dry-run]
"""

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path


PROVIDER = "gemini"


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


def process_gemini_file(
    conn: sqlite3.Connection,
    filepath: str,
    dry_run: bool = False,
) -> tuple[int, int, int]:
    """Process a single Gemini conversation JSON file."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"  ERROR reading {filepath}: {e}")
        return 0, 0, 1

    conv_id = data.get("conversation_id", Path(filepath).stem)
    session_id = f"gemini-{conv_id}"
    title = data.get("title", "Untitled Gemini Conversation")
    if not title or title == "":
        # Generate from first user input
        turns_data = data.get("turns", [])
        if turns_data:
            first_text = turns_data[0].get("user_input", {}).get("text", "")
            title = first_text[:80] or "Untitled"
    create_time = data.get("create_time", "")
    model = data.get("metadata", {}).get("model", "gemini-1.5-pro")

    # Check existing
    existing = conn.execute(
        "SELECT id FROM conversations WHERE provider = ? AND session_id = ?",
        (PROVIDER, session_id),
    ).fetchone()

    if existing:
        return 0, 1, 0

    turns_data = data.get("turns", [])
    if not turns_data:
        return 0, 1, 0

    created_at = create_time or datetime.now(timezone.utc).isoformat()

    if dry_run:
        print(f"  [DRY RUN] Would ingest: {title} ({len(turns_data) * 2} turns)")
        return len(turns_data) * 2, 0, 0

    try:
        cursor = conn.execute(
            """INSERT INTO conversations
                (provider, session_id, session_title, model_id, source_path, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (PROVIDER, session_id, title, model, filepath, created_at, created_at),
        )
        db_conv_id = cursor.lastrowid

        turn_count = 0
        user_turn_count = 0
        total_chars = 0
        turn_index = 0
        last_updated = created_at

        for turn_data in turns_data:
            # User turn
            user_text = turn_data.get("user_input", {}).get("text", "")
            user_ts = turn_data.get("user_input", {}).get("timestamp", created_at)
            if user_text:
                char_count = len(user_text)
                total_chars += char_count
                user_turn_count += 1

                conn.execute(
                    """INSERT INTO conversation_turns
                        (conversation_id, turn_index, role, content_text,
                         char_count, token_estimate, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (db_conv_id, turn_index, "user", user_text,
                     char_count, char_count // 4, user_ts),
                )
                turn_index += 1
                turn_count += 1
                last_updated = user_ts

            # Model turn
            model_text = turn_data.get("model_output", {}).get("text", "")
            model_ts = turn_data.get("model_output", {}).get("timestamp", created_at)
            model_for_turn = turn_data.get("model_output", {}).get("model", model)
            if model_text:
                char_count = len(model_text)
                total_chars += char_count

                content_summary = None
                content_truncated = None
                if char_count > 2000:
                    content_summary = generate_summary(model_text)
                    content_truncated = generate_truncated(model_text)

                conn.execute(
                    """INSERT INTO conversation_turns
                        (conversation_id, turn_index, role, content_text, content_summary,
                         content_truncated, model_id, char_count, token_estimate, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (db_conv_id, turn_index, "assistant", model_text, content_summary,
                     content_truncated, model_for_turn, char_count, char_count // 4, model_ts),
                )
                turn_index += 1
                turn_count += 1
                last_updated = model_ts

        conn.execute(
            """UPDATE conversations SET
                turn_count = ?, user_turn_count = ?, total_chars = ?,
                updated_at = ?, ingested_at = strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
            WHERE id = ?""",
            (turn_count, user_turn_count, total_chars, last_updated, db_conv_id),
        )

        return turn_count, 0, 0

    except Exception as e:
        print(f"  ERROR processing {filepath}: {e}")
        return 0, 0, 1


def main():
    parser = argparse.ArgumentParser(description="Parse Google Gemini data export")
    parser.add_argument("--export-dir", required=True,
                        help="Path to the Gemini Takeout export directory")
    parser.add_argument("--db-path",
                        default=os.path.expanduser("~/.prompt-mine/prompt_mine.db"),
                        help="Path to the SQLite database")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    # Find conversation files
    conv_dir = Path(args.export_dir)
    # Try common Takeout paths
    possible_dirs = [
        conv_dir / "Takeout" / "Gemini Apps" / "conversations",
        conv_dir / "Gemini Apps" / "conversations",
        conv_dir / "conversations",
        conv_dir,
    ]

    target_dir = None
    for d in possible_dirs:
        if d.is_dir():
            target_dir = d
            break

    if not target_dir:
        print(f"No conversations directory found in {args.export_dir}")
        sys.exit(1)

    conv_files = sorted(target_dir.glob("conversation_*.json")) + sorted(target_dir.glob("*.json"))
    print(f"Found {len(conv_files)} Gemini conversation files in {target_dir}")

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

    for filepath in conv_files:
        added, skipped, errors = process_gemini_file(conn, str(filepath), args.dry_run)
        total_added += added
        total_skipped += skipped
        total_errors += errors

    conn.commit()
    conn.close()

    print(f"\nParsing complete:")
    print(f"  Turns added:      {total_added}")
    print(f"  Conversations skipped: {total_skipped}")
    print(f"  Errors:           {total_errors}")


if __name__ == "__main__":
    main()
