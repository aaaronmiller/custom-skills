#!/usr/bin/env python3
"""
Prompt Mine — Daily Ingest Pipeline

Orchestrates extraction from all configured sources and runs the
processing pipeline (embedding, tagging, clustering).

Usage:
    python daily_ingest.py --all
    python daily_ingest.py --incremental
    python daily_ingest.py --status
"""

import argparse
import json
import os
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = os.path.expanduser("~/.prompt-mine/prompt_mine.db")
CONFIG_PATH = os.path.expanduser("~/.prompt-mine/config.yaml")

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))


def load_config():
    """Load configuration from config.yaml."""
    try:
        import yaml
        with open(CONFIG_PATH, "r") as f:
            return yaml.safe_load(f)
    except (ImportError, FileNotFoundError):
        # Return defaults if no config
        return {
            "sources": {
                "claude_code": {"enabled": True, "projects_dir": "~/projects"},
                "roo_kilo": {"enabled": True,
                             "storage_path": "~/.config/Code/User/globalStorage/rooveterinaryinc.roo-cline"},
                "openai": {"enabled": False},
                "gemini": {"enabled": False},
                "anthropic": {"enabled": False},
            }
        }


def run_extractor(script_name: str, extra_args: list[str] = None) -> tuple[int, int, int]:
    """Run an extraction script and return (added, skipped, errors)."""
    script_path = os.path.join(SCRIPTS_DIR, script_name)
    cmd = [sys.executable, script_path] + (extra_args or [])
    print(f"\n{'='*60}")
    print(f"Running: {' '.join(cmd)}")
    print('='*60)

    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr)

    return result.returncode


def run_ingest(conn: sqlite3.Connection, provider: str, config: dict, force: bool = False):
    """Run the ingest for a specific provider."""
    sources = config.get("sources", {})
    source_config = sources.get(provider, {})

    if not source_config.get("enabled", False):
        print(f"\n[SKIP] {provider} — not enabled in config")
        return

    if provider == "claude_code":
        projects_dir = source_config.get("projects_dir", "~/projects")
        include_checkpoints = source_config.get("include_checkpoints", True)
        args = ["--projects-dir", os.path.expanduser(projects_dir)]
        if include_checkpoints:
            args.append("--include-checkpoints")
        run_extractor("extract_claude_code.py", args)

    elif provider == "roo_kilo":
        storage_path = source_config.get("storage_path", "")
        kilo_path = source_config.get("kilo_path", "")
        args = ["--storage-path", os.path.expanduser(storage_path)]
        if kilo_path:
            args.extend(["--kilo-path", os.path.expanduser(kilo_path)])
        run_extractor("extract_roo_kilo.py", args)

    elif provider == "openai":
        export_dir = source_config.get("export_dir")
        if export_dir:
            run_extractor("parse_openai_export.py", ["--export-dir", os.path.expanduser(export_dir)])
        else:
            print("[SKIP] openai — no export_dir configured")

    elif provider == "gemini":
        export_dir = source_config.get("export_dir")
        if export_dir:
            run_extractor("parse_gemini_export.py", ["--export-dir", os.path.expanduser(export_dir)])
        else:
            print("[SKIP] gemini — no export_dir configured")

    elif provider == "anthropic":
        export_file = source_config.get("export_file")
        if export_file:
            run_extractor("parse_anthropic_export.py", ["--export-file", os.path.expanduser(export_file)])
        else:
            print("[SKIP] anthropic — no export_file configured")


def show_status(conn: sqlite3.Connection):
    """Display database statistics."""
    print("\n" + "=" * 60)
    print("Prompt Mine Ingest Status")
    print("=" * 60)

    # Database size
    db_path = DB_PATH
    if os.path.exists(db_path):
        size_mb = os.path.getsize(db_path) / (1024 * 1024)
        print(f"\nDatabase: {db_path}")
        print(f"Size: {size_mb:.1f} MB")

    # Total counts
    total_convs = conn.execute("SELECT COUNT(*) FROM conversations WHERE is_deleted = 0").fetchone()[0]
    total_turns = conn.execute("SELECT COUNT(*) FROM conversation_turns").fetchone()[0]
    user_turns = conn.execute("SELECT COUNT(*) FROM conversation_turns WHERE role = 'user'").fetchone()[0]
    total_tags = conn.execute("SELECT COUNT(*) FROM conversation_tags").fetchone()[0]
    total_embeddings = 0
    try:
        total_embeddings = conn.execute("SELECT COUNT(*) FROM turn_embeddings").fetchone()[0]
    except Exception:
        pass

    print(f"\nTotals:")
    print(f"  Conversations: {total_convs}")
    print(f"  Total turns:   {total_turns}")
    print(f"  User turns:    {user_turns}")
    print(f"  Tags applied:  {total_tags}")
    print(f"  Embeddings:    {total_embeddings}")

    # Per-provider stats
    print(f"\nBy Provider:")
    providers = conn.execute(
        """SELECT provider, COUNT(*) as cnt, SUM(turn_count) as turns
           FROM conversations WHERE is_deleted = 0
           GROUP BY provider ORDER BY cnt DESC"""
    ).fetchall()
    for provider, cnt, turns in providers:
        print(f"  {provider:15s}: {cnt:5d} conversations, {turns or 0:6d} turns")

    # Per-project stats (top 10)
    print(f"\nTop Projects:")
    projects = conn.execute(
        """SELECT project_name, COUNT(*) as cnt
           FROM conversations WHERE is_deleted = 0 AND project_name IS NOT NULL
           GROUP BY project_name ORDER BY cnt DESC LIMIT 10"""
    ).fetchall()
    for project, cnt in projects:
        print(f"  {project:25s}: {cnt:5d} conversations")

    # Last ingest
    print(f"\nLast Ingest:")
    ingests = conn.execute(
        """SELECT provider, MAX(completed_at) as last_run, SUM(records_added) as added
           FROM ingest_log WHERE status = 'completed'
           GROUP BY provider"""
    ).fetchall()
    if ingests:
        for provider, last_run, added in ingests:
            print(f"  {provider:15s}: {last_run or 'never':25s} ({added or 0} records)")
    else:
        print("  No ingest records found")

    print()


def main():
    parser = argparse.ArgumentParser(description="Prompt Mine Daily Ingest")
    parser.add_argument("--all", action="store_true", help="Run full ingest from all sources")
    parser.add_argument("--incremental", action="store_true", help="Only process new data (default)")
    parser.add_argument("--status", action="store_true", help="Show database statistics")
    parser.add_argument("--db-path", default=DB_PATH)
    args = parser.parse_args()

    if not os.path.exists(args.db_path):
        print(f"Database not found at {args.db_path}")
        print("Run init_database.py first.")
        sys.exit(1)

    conn = sqlite3.connect(args.db_path)
    conn.execute("PRAGMA journal_mode=WAL")

    try:
        if args.status:
            show_status(conn)
            return

        if not args.all and not args.incremental:
            args.incremental = True  # Default to incremental

        config = load_config()

        # Record ingest start
        started_at = datetime.now(timezone.utc).isoformat()

        # Run each enabled extractor
        providers = ["claude_code", "roo_kilo", "openai", "gemini", "anthropic"]
        for provider in providers:
            run_ingest(conn, provider, config)

        # Run processing pipeline
        print(f"\n{'='*60}")
        print("Running processing pipeline...")
        print('='*60)

        # Auto-tag
        tag_config = config.get("tagging", {})
        if tag_config.get("auto_tag", True):
            print("\nAuto-tagging conversations...")
            from rag_pipeline import auto_tag_conversations
            count = auto_tag_conversations(conn)
            print(f"Applied {count} tags")

        # Clustering
        cluster_config = config.get("clustering", {})
        if cluster_config.get("enabled", True):
            print("\nClustering conversations...")
            from rag_pipeline import cluster_conversations
            count = cluster_conversations(conn)
            print(f"Clustered {count} conversations")

        # Record ingest completion
        completed_at = datetime.now(timezone.utc).isoformat()
        conn.execute(
            """INSERT INTO ingest_log (provider, source_path, started_at, completed_at, status)
               VALUES ('all', 'daily_ingest', ?, ?, 'completed')""",
            (started_at, completed_at),
        )
        conn.commit()

        print(f"\n{'='*60}")
        print("Ingest complete!")
        print('='*60)
        show_status(conn)

    finally:
        conn.close()


if __name__ == "__main__":
    main()
