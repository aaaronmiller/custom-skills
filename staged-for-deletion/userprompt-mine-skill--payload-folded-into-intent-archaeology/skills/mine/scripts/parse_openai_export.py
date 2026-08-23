#!/usr/bin/env python3
"""
Prompt Mine — OpenAI Data Export Parser

Parses the conversations.json file from an OpenAI data export ZIP.

Usage:
    python parse_openai_export.py --export-dir PATH [--db-path PATH] [--dry-run]
"""

import argparse
import hashlib
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path


PROVIDER = "openai"


def unix_to_iso(ts) -> str:
    if ts is None:
        return datetime.now(timezone.utc).isoformat()
    if isinstance(ts, (int, float)):
        return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
    if isinstance(ts, str):
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


def flatten_content_parts(parts: list) -> str:
    """Concatenate all text parts from an OpenAI content parts array."""
    texts = []
    for part in parts:
        if isinstance(part, dict) and part.get("type") == "text":
            texts.append(part.get("text", ""))
        elif isinstance(part, str):
            texts.append(part)
    return "\n".join(texts)


def walk_tree(mapping: dict, start_id: str) -> list[dict]:
    """Walk the OpenAI conversation tree to extract turns in order."""
    turns = []
    current_id = start_id

    visited = set()
    while current_id and current_id not in visited:
        visited.add(current_id)
        node = mapping.get(current_id)
        if not node:
            break

        message = node.get("message")
        if message and message.get("content"):
            content_parts = message.get("content", {}).get("parts", [])
            content_text = flatten_content_parts(content_parts)

            if content_text.strip():
                role = message.get("author", {}).get("role", "unknown")
                model = message.get("metadata", {}).get("model_slug")
                create_time = message.get("create_time")

                turns.append({
                    "role": role,
                    "content_text": content_text,
                    "model_id": model,
                    "created_at": unix_to_iso(create_time),
                })

        # Follow the first child (main branch)
        children = node.get("children", [])
        if children:
            current_id = children[0]
        else:
            break

    return turns


def process_conversation(
    conn: sqlite3.Connection,
    conv_data: dict,
    export_dir: str,
    dry_run: bool = False,
) -> tuple[int, int, int]:
    """Process a single OpenAI conversation."""
    conv_id_str = conv_data.get("id", "")
    session_id = f"openai-{conv_id_str}"
    title = conv_data.get("title", "Untitled")
    create_time = conv_data.get("create_time")
    update_time = conv_data.get("update_time")
    model = conv_data.get("model")

    mapping = conv_data.get("mapping", {})
    current_node = conv_data.get("current_node")

    # Find root node
    root_id = None
    for node_id, node in mapping.items():
        if node.get("parent") is None:
            root_id = node_id
            break

    if not root_id:
        return 0, 0, 1

    turns = walk_tree(mapping, root_id)
    if not turns:
        return 0, 1, 0

    created_at = unix_to_iso(create_time)
    updated_at = unix_to_iso(update_time)

    # Check existing
    existing = conn.execute(
        "SELECT id FROM conversations WHERE provider = ? AND session_id = ?",
        (PROVIDER, session_id),
    ).fetchone()

    if existing:
        return 0, 1, 0

    if dry_run:
        print(f"  [DRY RUN] Would ingest: {title} ({len(turns)} turns)")
        return len(turns), 0, 0

    try:
        cursor = conn.execute(
            """INSERT INTO conversations
                (provider, session_id, session_title, model_id, source_path,
                 created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (PROVIDER, session_id, title, model, export_dir, created_at, updated_at),
        )
        db_conv_id = cursor.lastrowid

        turn_count = 0
        user_turn_count = 0
        total_chars = 0

        for idx, turn in enumerate(turns):
            role = turn["role"]
            content_text = turn["content_text"]
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
                     content_truncated, model_id, char_count, token_estimate, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (db_conv_id, idx, role, content_text, content_summary, content_truncated,
                 turn.get("model_id"), char_count, char_count // 4, turn.get("created_at", created_at)),
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
    parser = argparse.ArgumentParser(description="Parse OpenAI data export")
    parser.add_argument("--export-dir", required=True,
                        help="Path to the unzipped OpenAI export directory")
    parser.add_argument("--db-path",
                        default=os.path.expanduser("~/.prompt-mine/prompt_mine.db"),
                        help="Path to the SQLite database")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    conv_file = os.path.join(args.export_dir, "conversations.json")
    if not os.path.exists(conv_file):
        print(f"conversations.json not found in {args.export_dir}")
        sys.exit(1)

    if not os.path.exists(args.db_path):
        print(f"Database not found at {args.db_path}")
        print("Run init_database.py first.")
        sys.exit(1)

    print(f"Loading conversations from {conv_file}...")

    try:
        with open(conv_file, "r", encoding="utf-8") as f:
            conversations = json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERROR: Failed to parse conversations.json: {e}")
        print("For large files, consider using ijson for streaming parse.")
        sys.exit(1)

    print(f"Found {len(conversations)} conversations")

    conn = sqlite3.connect(args.db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")

    total_added = 0
    total_skipped = 0
    total_errors = 0

    for conv_data in conversations:
        added, skipped, errors = process_conversation(
            conn, conv_data, args.export_dir, args.dry_run
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
