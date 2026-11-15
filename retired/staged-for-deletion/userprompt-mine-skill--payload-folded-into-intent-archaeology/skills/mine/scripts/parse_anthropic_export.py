#!/usr/bin/env python3
"""
Prompt Mine — Anthropic Data Export Parser

Parses the conversations.json file from an Anthropic data export.

Usage:
    python parse_anthropic_export.py --export-file PATH [--db-path PATH] [--dry-run]
"""

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path


PROVIDER = "anthropic"


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


def extract_text_from_content_blocks(content_blocks: list) -> str:
    """Extract text from Anthropic-style content block array."""
    texts = []
    for block in content_blocks:
        if isinstance(block, dict):
            if block.get("type") == "text":
                texts.append(block.get("text", ""))
        elif isinstance(block, str):
            texts.append(block)
    return "\n".join(texts)


def extract_tool_calls_from_content_blocks(content_blocks: list) -> str:
    """Extract tool use/result blocks as JSON."""
    tool_blocks = []
    for block in content_blocks:
        if isinstance(block, dict) and block.get("type") in ("tool_use", "tool_result"):
            tool_blocks.append(block)
    return json.dumps(tool_blocks) if tool_blocks else None


def extract_thinking_from_content_blocks(content_blocks: list) -> str:
    """Extract thinking blocks."""
    for block in content_blocks:
        if isinstance(block, dict) and block.get("type") == "thinking":
            return block.get("thinking", "")
    return None


def process_anthropic_conversation(
    conn: sqlite3.Connection,
    conv_data: dict,
    export_file: str,
    dry_run: bool = False,
) -> tuple[int, int, int]:
    """Process a single Anthropic conversation."""
    conv_id = conv_data.get("id", "")
    session_id = f"anthropic-{conv_id}"
    title = conv_data.get("title", "Untitled")
    project = conv_data.get("project")
    model = conv_data.get("model")
    created_at = conv_data.get("created_at", "")
    updated_at = conv_data.get("updated_at", created_at)

    messages = conv_data.get("messages", [])
    if not messages:
        return 0, 1, 0

    # Check existing
    existing = conn.execute(
        "SELECT id FROM conversations WHERE provider = ? AND session_id = ?",
        (PROVIDER, session_id),
    ).fetchone()

    if existing:
        return 0, 1, 0

    if dry_run:
        print(f"  [DRY RUN] Would ingest: {title} ({len(messages)} turns)")
        return len(messages), 0, 0

    try:
        cursor = conn.execute(
            """INSERT INTO conversations
                (provider, session_id, session_title, project_name, model_id,
                 source_path, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (PROVIDER, session_id, title, project, model,
             export_file, created_at, updated_at),
        )
        db_conv_id = cursor.lastrowid

        turn_count = 0
        user_turn_count = 0
        total_chars = 0

        for idx, msg in enumerate(messages):
            role = msg.get("role", "tool")
            content = msg.get("content", [])
            msg_model = msg.get("model") or model
            msg_created = msg.get("created_at", created_at)

            # Handle both string and array content
            if isinstance(content, str):
                content_text = content
                tool_calls = None
                thinking = None
            elif isinstance(content, list):
                content_text = extract_text_from_content_blocks(content)
                tool_calls = extract_tool_calls_from_content_blocks(content)
                thinking = extract_thinking_from_content_blocks(content)
            else:
                content_text = str(content)
                tool_calls = None
                thinking = None

            char_count = len(content_text)
            total_chars += char_count

            if role == "user":
                user_turn_count += 1

            content_summary = None
            content_truncated = None
            if role == "assistant" and char_count > 2000:
                content_summary = generate_summary(content_text)
                content_truncated = generate_truncated(content_text)

            conn.execute(
                """INSERT INTO conversation_turns
                    (conversation_id, turn_index, role, content_text, content_summary,
                     content_truncated, thinking_content, model_id, tool_calls,
                     char_count, token_estimate, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (db_conv_id, idx, role, content_text, content_summary, content_truncated,
                 thinking, msg_model, tool_calls, char_count, char_count // 4, msg_created),
            )
            turn_count += 1

        conn.execute(
            """UPDATE conversations SET
                turn_count = ?, user_turn_count = ?, total_chars = ?,
                ingested_at = strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
            WHERE id = ?""",
            (turn_count, user_turn_count, total_chars, db_conv_id),
        )

        return turn_count, 0, 0

    except Exception as e:
        print(f"  ERROR processing conversation {session_id}: {e}")
        return 0, 0, 1


def main():
    parser = argparse.ArgumentParser(description="Parse Anthropic data export")
    parser.add_argument("--export-file", required=True,
                        help="Path to the Anthropic export JSON file")
    parser.add_argument("--db-path",
                        default=os.path.expanduser("~/.prompt-mine/prompt_mine.db"),
                        help="Path to the SQLite database")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not os.path.exists(args.export_file):
        print(f"Export file not found: {args.export_file}")
        sys.exit(1)

    if not os.path.exists(args.db_path):
        print(f"Database not found at {args.db_path}")
        print("Run init_database.py first.")
        sys.exit(1)

    print(f"Loading conversations from {args.export_file}...")

    try:
        with open(args.export_file, "r", encoding="utf-8") as f:
            conversations = json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERROR: Failed to parse export file: {e}")
        sys.exit(1)

    # Handle both array and object-with-conversations-key formats
    if isinstance(conversations, dict):
        conversations = conversations.get("conversations", [conversations])

    print(f"Found {len(conversations)} conversations")

    conn = sqlite3.connect(args.db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")

    total_added = 0
    total_skipped = 0
    total_errors = 0

    for conv_data in conversations:
        added, skipped, errors = process_anthropic_conversation(
            conn, conv_data, args.export_file, args.dry_run
        )
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
