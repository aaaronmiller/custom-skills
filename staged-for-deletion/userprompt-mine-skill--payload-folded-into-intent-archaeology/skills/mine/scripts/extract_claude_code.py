#!/usr/bin/env python3
"""
Prompt Mine — Claude Code Conversation Extractor

Extracts conversation history from Claude Code session files (.jsonl)
and optional checkpoint data.

Usage:
    python extract_claude_code.py --projects-dir ~/projects [--include-checkpoints]
                                  [--db-path PATH] [--dry-run]
"""

import argparse
import hashlib
import json
import os
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


PROVIDER = "claude-code"


def compute_file_hash(filepath: str) -> str:
    """Compute SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_jsonl_file(filepath: str) -> list[dict]:
    """Parse a JSONL session file into a list of turns."""
    turns = []
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
                turns.append(record)
            except json.JSONDecodeError:
                # Log but don't fail — skip corrupt lines
                print(f"  WARNING: Corrupt JSON at line {line_num} in {filepath}")
    return turns


def extract_session_metadata(filepath: str, project_name: str) -> dict:
    """Extract session-level metadata from a JSONL file."""
    basename = os.path.basename(filepath)
    # Session ID from filename: 2025-01-15T10-30-00.jsonl → claude-code-2025-01-15T10-30-00
    session_id = f"claude-code-{os.path.splitext(basename)[0]}"

    # Get file modification time as fallback timestamp
    mtime = os.path.getmtime(filepath)
    file_mtime = datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat()

    return {
        "provider": PROVIDER,
        "session_id": session_id,
        "project_name": project_name,
        "source_path": filepath,
        "source_hash": compute_file_hash(filepath),
        "file_mtime": file_mtime,
    }


def map_role(raw_type: str) -> str:
    """Map Claude Code JSONL type to database role."""
    mapping = {
        "user": "user",
        "assistant": "assistant",
        "tool_result": "tool",
        "system": "system",
    }
    return mapping.get(raw_type, "tool")


def generate_summary(text: str, max_length: int = 200) -> str:
    """Generate an extractive summary of text."""
    if len(text) <= max_length:
        return text

    # Simple extractive: take first sentence + last sentence
    sentences = re.split(r'(?<=[.!?])\s+', text)
    if len(sentences) <= 2:
        return text[:max_length]

    first = sentences[0]
    last = sentences[-1]
    summary = f"{first} [...] {last}"
    if len(summary) > max_length:
        return text[:max_length - 3] + "..."
    return summary


def generate_truncated(text: str, last_n_lines: int = 50) -> str:
    """Generate truncated display text: summary + last N lines."""
    summary = generate_summary(text)
    lines = text.splitlines()
    if len(lines) <= last_n_lines + 5:
        return text
    last_lines = "\n".join(lines[-last_n_lines:])
    return f"{summary}\n\n--- last {last_n_lines} lines ---\n\n{last_lines}"


def process_session(
    conn: sqlite3.Connection,
    filepath: str,
    project_name: str,
    dry_run: bool = False,
) -> tuple[int, int, int]:
    """Process a single session file. Returns (added, skipped, errors)."""
    metadata = extract_session_metadata(filepath, project_name)
    turns = parse_jsonl_file(filepath)

    if not turns:
        return 0, 1, 0  # Empty file, skip

    # Check if already ingested (by provider + session_id)
    existing = conn.execute(
        "SELECT id, source_hash FROM conversations WHERE provider = ? AND session_id = ?",
        (metadata["provider"], metadata["session_id"]),
    ).fetchone()

    if existing and existing[1] == metadata["source_hash"]:
        return 0, 1, 0  # Already ingested with same hash

    # Determine session timestamps from turns
    timestamps = []
    for turn in turns:
        ts = turn.get("timestamp") or turn.get("ts")
        if ts:
            timestamps.append(ts)

    created_at = timestamps[0] if timestamps else metadata["file_mtime"]
    updated_at = timestamps[-1] if timestamps else metadata["file_mtime"]

    # Session title from first user message
    session_title = None
    for turn in turns:
        if turn.get("type") == "user":
            content = turn.get("content", "")
            if isinstance(content, str):
                session_title = content[:120]
            break

    if dry_run:
        print(f"  [DRY RUN] Would ingest: {filepath} ({len(turns)} turns)")
        return len(turns), 0, 0

    try:
        with conn:
            # Upsert conversation
            if existing:
                conv_id = existing[0]
                conn.execute(
                    """UPDATE conversations SET
                        session_title = ?, source_path = ?, source_hash = ?,
                        updated_at = ?, ingested_at = strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
                    WHERE id = ?""",
                    (session_title, filepath, metadata["source_hash"], updated_at, conv_id),
                )
                # Delete old turns to re-ingest
                conn.execute("DELETE FROM conversation_turns WHERE conversation_id = ?", (conv_id,))
            else:
                cursor = conn.execute(
                    """INSERT INTO conversations
                        (provider, session_id, session_title, project_name, source_path,
                         source_hash, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (metadata["provider"], metadata["session_id"], session_title,
                     metadata["project_name"], filepath, metadata["source_hash"],
                     created_at, updated_at),
                )
                conv_id = cursor.lastrowid

            # Insert turns
            turn_count = 0
            user_turn_count = 0
            total_chars = 0

            for idx, turn in enumerate(turns):
                role = map_role(turn.get("type", "tool"))
                content = turn.get("content", "")
                if isinstance(content, list):
                    # Anthropic-style content blocks
                    content = " ".join(
                        block.get("text", "") for block in content
                        if isinstance(block, dict) and block.get("type") == "text"
                    )
                content_text = str(content) if content else ""
                char_count = len(content_text)
                total_chars += char_count

                if role == "user":
                    user_turn_count += 1

                # Generate summary/truncated for long assistant responses
                content_summary = None
                content_truncated = None
                if role == "assistant" and char_count > 2000:
                    content_summary = generate_summary(content_text)
                    content_truncated = generate_truncated(content_text)

                # Extract tool calls
                tool_calls_json = None
                if turn.get("tool_uses"):
                    tool_calls_json = json.dumps(turn["tool_uses"])

                # Extract thinking content
                thinking_content = None
                if turn.get("thinking"):
                    thinking_content = str(turn["thinking"])

                timestamp = turn.get("timestamp") or turn.get("ts") or created_at
                model_id = turn.get("model")

                conn.execute(
                    """INSERT INTO conversation_turns
                        (conversation_id, turn_index, role, content_text, content_summary,
                         content_truncated, thinking_content, model_id, tool_calls,
                         char_count, token_estimate, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (conv_id, idx, role, content_text, content_summary, content_truncated,
                     thinking_content, model_id, tool_calls_json, char_count,
                     char_count // 4, timestamp),
                )
                turn_count += 1

            # Update conversation aggregates
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
                (provider, source_path, error_type, error_message, raw_data)
            VALUES (?, ?, ?, ?, ?)""",
            (PROVIDER, filepath, "parse_error", str(e), None),
        )
        return 0, 0, 1


def find_claude_code_sessions(projects_dir: str) -> list[tuple[str, str]]:
    """Find all Claude Code session files under a projects directory."""
    sessions = []
    projects_path = Path(os.path.expanduser(projects_dir))

    if not projects_path.exists():
        print(f"Projects directory not found: {projects_path}")
        return sessions

    # Find .claude/sessions/ directories
    for claude_dir in projects_path.rglob(".claude"):
        sessions_dir = claude_dir / "sessions"
        if sessions_dir.is_dir():
            project_name = claude_dir.parent.name
            for jsonl_file in sessions_dir.glob("*.jsonl"):
                sessions.append((str(jsonl_file), project_name))

    # Also check ~/.claude/projects/ for global session index
    global_projects = Path.home() / ".claude" / "projects"
    if global_projects.exists():
        for project_dir in global_projects.iterdir():
            if project_dir.is_dir():
                sessions_subdir = project_dir / "sessions"
                if sessions_subdir.is_dir():
                    project_name = project_dir.name  # hash-based name
                    for jsonl_file in sessions_subdir.glob("*.jsonl"):
                        sessions.append((str(jsonl_file), project_name))

    return sessions


def extract_checkpoints(
    conn: sqlite3.Connection,
    projects_dir: str,
    dry_run: bool = False,
) -> int:
    """Extract checkpoint data from git repositories."""
    checkpoint_count = 0
    projects_path = Path(os.path.expanduser(projects_dir))

    for git_dir in projects_path.rglob(".git"):
        repo_path = git_dir.parent
        project_name = repo_path.name

        # Find checkpoint commits
        try:
            import subprocess
            result = subprocess.run(
                ["git", "log", "--all", "--grep=claude-code checkpoint",
                 "--format=%H %ai %s"],
                capture_output=True, text=True, cwd=str(repo_path),
                timeout=10,
            )
            if result.returncode != 0 or not result.stdout.strip():
                continue

            for line in result.stdout.strip().split("\n"):
                parts = line.split(" ", 2)
                if len(parts) < 3:
                    continue
                commit_hash, commit_time, message = parts

                # Find the matching conversation by timestamp proximity
                # (This is a heuristic — checkpoint timestamps may not exactly match)
                if dry_run:
                    checkpoint_count += 1
                    continue

                # Get diff summary
                diff_result = subprocess.run(
                    ["git", "diff-tree", "--no-commit-id", "--stat", commit_hash],
                    capture_output=True, text=True, cwd=str(repo_path),
                    timeout=10,
                )
                diff_summary = diff_result.stdout[:500] if diff_result.stdout else ""

                # Get files changed
                files_result = subprocess.run(
                    ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", commit_hash],
                    capture_output=True, text=True, cwd=str(repo_path),
                    timeout=10,
                )
                files_changed = json.dumps(files_result.stdout.strip().split("\n")) if files_result.stdout else "[]"

                # Try to match with a conversation
                conv = conn.execute(
                    """SELECT id FROM conversations
                    WHERE provider = ? AND project_name = ?
                    AND created_at <= ? AND updated_at >= ?
                    LIMIT 1""",
                    (PROVIDER, project_name, commit_time, commit_time),
                ).fetchone()

                if conv:
                    try:
                        conn.execute(
                            """INSERT OR IGNORE INTO checkpoints
                                (conversation_id, commit_hash, diff_summary, files_changed, created_at)
                            VALUES (?, ?, ?, ?, ?)""",
                            (conv[0], commit_hash, diff_summary, files_changed, commit_time),
                        )
                        checkpoint_count += 1
                    except sqlite3.IntegrityError:
                        pass  # Already exists
        except (subprocess.TimeoutExpired, FileNotFoundError):
            continue

    return checkpoint_count


def main():
    parser = argparse.ArgumentParser(description="Extract Claude Code conversations")
    parser.add_argument("--projects-dir", default="~/projects",
                        help="Root directory containing project folders")
    parser.add_argument("--include-checkpoints", action="store_true",
                        help="Also extract git checkpoint data")
    parser.add_argument("--db-path", default=os.path.expanduser("~/.prompt-mine/prompt_mine.db"),
                        help="Path to the SQLite database")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be extracted without writing to DB")
    args = parser.parse_args()

    if not os.path.exists(args.db_path):
        print(f"Database not found at {args.db_path}")
        print("Run init_database.py first.")
        sys.exit(1)

    conn = sqlite3.connect(args.db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")

    sessions = find_claude_code_sessions(args.projects_dir)
    print(f"Found {len(sessions)} Claude Code session files")

    total_added = 0
    total_skipped = 0
    total_errors = 0

    for filepath, project_name in sessions:
        added, skipped, errors = process_session(conn, filepath, project_name, args.dry_run)
        total_added += added
        total_skipped += skipped
        total_errors += errors

    if args.include_checkpoints:
        checkpoint_count = extract_checkpoints(conn, args.projects_dir, args.dry_run)
        print(f"Extracted {checkpoint_count} checkpoints")

    conn.commit()
    conn.close()

    print(f"\nExtraction complete:")
    print(f"  Turns added:    {total_added}")
    print(f"  Sessions skipped: {total_skipped}")
    print(f"  Errors:         {total_errors}")


if __name__ == "__main__":
    main()
