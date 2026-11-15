#!/usr/bin/env python3
"""
Prompt Mine — Database Initialization

Creates the SQLite database with all tables, indexes, FTS, and vector index.
Also creates the default config.yaml if one does not exist.

Usage:
    python init_database.py [--db-path PATH] [--force]
"""

import argparse
import os
import sys
import yaml

DEFAULT_DB_DIR = os.path.expanduser("~/.prompt-mine")
DEFAULT_DB_PATH = os.path.join(DEFAULT_DB_DIR, "prompt_mine.db")
DEFAULT_CONFIG_PATH = os.path.join(DEFAULT_DB_DIR, "config.yaml")

SCHEMA_SQL = """
-- ============================================================
-- conversations
-- ============================================================
CREATE TABLE IF NOT EXISTS conversations (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    provider        TEXT NOT NULL,
    session_id      TEXT NOT NULL,
    session_title   TEXT,
    project_name    TEXT,
    model_id        TEXT,
    source_path     TEXT,
    source_hash     TEXT,
    turn_count      INTEGER DEFAULT 0,
    user_turn_count INTEGER DEFAULT 0,
    total_chars     INTEGER DEFAULT 0,
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL,
    ingested_at     TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    is_deleted      INTEGER DEFAULT 0,
    metadata_json   TEXT,
    UNIQUE(provider, session_id)
);

CREATE INDEX IF NOT EXISTS idx_conversations_provider ON conversations(provider);
CREATE INDEX IF NOT EXISTS idx_conversations_project ON conversations(project_name);
CREATE INDEX IF NOT EXISTS idx_conversations_model ON conversations(model_id);
CREATE INDEX IF NOT EXISTS idx_conversations_created ON conversations(created_at);
CREATE INDEX IF NOT EXISTS idx_conversations_ingested ON conversations(ingested_at);

-- ============================================================
-- conversation_turns
-- ============================================================
CREATE TABLE IF NOT EXISTS conversation_turns (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    turn_index      INTEGER NOT NULL,
    role            TEXT NOT NULL,
    content_text    TEXT NOT NULL,
    content_summary TEXT,
    content_truncated TEXT,
    thinking_content TEXT,
    model_id        TEXT,
    tool_calls      TEXT,
    char_count      INTEGER DEFAULT 0,
    token_estimate  INTEGER DEFAULT 0,
    created_at      TEXT NOT NULL,
    ingested_at     TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    metadata_json   TEXT,
    UNIQUE(conversation_id, turn_index)
);

CREATE INDEX IF NOT EXISTS idx_turns_conversation ON conversation_turns(conversation_id);
CREATE INDEX IF NOT EXISTS idx_turns_role ON conversation_turns(role);
CREATE INDEX IF NOT EXISTS idx_turns_created ON conversation_turns(created_at);

-- ============================================================
-- FTS5 full-text search
-- ============================================================
CREATE VIRTUAL TABLE IF NOT EXISTS conversation_turns_fts USING fts5(
    content_text,
    content_summary,
    content='conversation_turns',
    content_rowid='id',
    tokenize='unicode61'
);

CREATE TRIGGER IF NOT EXISTS turns_fts_insert AFTER INSERT ON conversation_turns BEGIN
    INSERT INTO conversation_turns_fts(rowid, content_text, content_summary)
    VALUES (new.id, new.content_text, new.content_summary);
END;

CREATE TRIGGER IF NOT EXISTS turns_fts_delete AFTER DELETE ON conversation_turns BEGIN
    INSERT INTO conversation_turns_fts(conversation_turns_fts, rowid, content_text, content_summary)
    VALUES ('delete', old.id, old.content_text, old.content_summary);
END;

-- ============================================================
-- tool_calls
-- ============================================================
CREATE TABLE IF NOT EXISTS tool_calls (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    turn_id         INTEGER NOT NULL REFERENCES conversation_turns(id) ON DELETE CASCADE,
    tool_name       TEXT NOT NULL,
    tool_input      TEXT,
    tool_output     TEXT,
    output_truncated INTEGER DEFAULT 0,
    created_at      TEXT,
    FOREIGN KEY (turn_id) REFERENCES conversation_turns(id)
);

CREATE INDEX IF NOT EXISTS idx_tool_calls_turn ON tool_calls(turn_id);
CREATE INDEX IF NOT EXISTS idx_tool_calls_name ON tool_calls(tool_name);

-- ============================================================
-- checkpoints
-- ============================================================
CREATE TABLE IF NOT EXISTS checkpoints (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    commit_hash     TEXT NOT NULL,
    diff_summary    TEXT,
    files_changed   TEXT,
    created_at      TEXT NOT NULL,
    UNIQUE(conversation_id, commit_hash)
);

CREATE INDEX IF NOT EXISTS idx_checkpoints_conversation ON checkpoints(conversation_id);

-- ============================================================
-- tags
-- ============================================================
CREATE TABLE IF NOT EXISTS tags (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    tag_name        TEXT NOT NULL UNIQUE,
    tag_type        TEXT NOT NULL,
    created_at      TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_tags_type ON tags(tag_type);

-- ============================================================
-- conversation_tags
-- ============================================================
CREATE TABLE IF NOT EXISTS conversation_tags (
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    tag_id          INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    confidence      REAL DEFAULT 1.0,
    source          TEXT DEFAULT 'auto',
    created_at      TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    PRIMARY KEY (conversation_id, tag_id)
);

-- ============================================================
-- projects
-- ============================================================
CREATE TABLE IF NOT EXISTS projects (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    project_name    TEXT NOT NULL UNIQUE,
    project_path    TEXT,
    description     TEXT,
    conversation_count INTEGER DEFAULT 0,
    first_seen      TEXT,
    last_seen       TEXT,
    created_at      TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    metadata_json   TEXT
);

CREATE INDEX IF NOT EXISTS idx_projects_name ON projects(project_name);

-- ============================================================
-- ingest_log
-- ============================================================
CREATE TABLE IF NOT EXISTS ingest_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    provider        TEXT NOT NULL,
    source_path     TEXT NOT NULL,
    source_hash     TEXT,
    records_added   INTEGER DEFAULT 0,
    records_skipped INTEGER DEFAULT 0,
    errors          INTEGER DEFAULT 0,
    started_at      TEXT NOT NULL,
    completed_at    TEXT,
    status          TEXT DEFAULT 'running',
    notes           TEXT
);

CREATE INDEX IF NOT EXISTS idx_ingest_provider ON ingest_log(provider);
CREATE INDEX IF NOT EXISTS idx_ingest_status ON ingest_log(status);

-- ============================================================
-- extraction_errors
-- ============================================================
CREATE TABLE IF NOT EXISTS extraction_errors (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    ingest_log_id   INTEGER REFERENCES ingest_log(id),
    provider        TEXT NOT NULL,
    source_path     TEXT,
    error_type      TEXT NOT NULL,
    error_message   TEXT NOT NULL,
    raw_data        TEXT,
    created_at      TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);
"""

VECTOR_SQL = """
-- sqlite-vec virtual table for embeddings
-- Only created if the sqlite-vec extension is available
CREATE VIRTUAL TABLE IF NOT EXISTS turn_embeddings USING vec0(
    turn_id INTEGER PRIMARY KEY,
    embedding float[768]
);
"""

DEFAULT_CONFIG = {
    "database": {
        "path": DEFAULT_DB_PATH,
    },
    "sources": {
        "claude_code": {
            "enabled": True,
            "projects_dir": "~/projects",
            "include_checkpoints": True,
            "last_ingested": None,
        },
        "roo_kilo": {
            "enabled": True,
            "storage_path": "~/.config/Code/User/globalStorage/rooveterinaryinc.roo-cline",
            "include_kilo": True,
            "kilo_path": "~/.config/Code/User/globalStorage/kilocode.kilo-code",
        },
        "openai": {
            "enabled": False,
            "export_dir": None,
        },
        "gemini": {
            "enabled": False,
            "export_dir": None,
        },
        "anthropic": {
            "enabled": False,
            "export_file": None,
        },
    },
    "embedding": {
        "model": "all-MiniLM-L6-v2",
        "dimensions": 768,
        "device": "cpu",
        "batch_size": 64,
    },
    "summarization": {
        "method": "extractive",
        "max_summary_length": 200,
        "response_truncation_lines": 50,
        "full_response_threshold": 20000,
    },
    "capture_api": {
        "enabled": False,
        "port": 8420,
    },
    "tagging": {
        "auto_tag": True,
        "confidence_threshold": 0.3,
    },
    "clustering": {
        "enabled": True,
        "recluster_threshold": 500,
        "last_clustered": None,
    },
}


def init_database(db_path: str, force: bool = False) -> None:
    """Create the database and all tables."""
    if os.path.exists(db_path) and not force:
        print(f"Database already exists at {db_path}")
        print("Use --force to drop and recreate, or just run ingest to add data.")
        return

    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    if force and os.path.exists(db_path):
        os.remove(db_path)
        print(f"Removed existing database: {db_path}")

    import sqlite3
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")

    # Create main tables
    conn.executescript(SCHEMA_SQL)

    # Try to load sqlite-vec extension
    try:
        conn.enable_load_extension(True)
        # Try common paths for sqlite-vec
        vec_paths = [
            "vec0",  # If compiled into SQLite
            os.path.expanduser("~/.prompt-mine/lib/sqlite_vec"),
        ]
        loaded = False
        for vec_path in vec_paths:
            try:
                conn.load_extension(vec_path)
                loaded = True
                break
            except sqlite3.OperationalError:
                continue

        if loaded:
            conn.executescript(VECTOR_SQL)
            print("sqlite-vec extension loaded — vector search enabled")
        else:
            print("WARNING: sqlite-vec extension not found — vector search disabled")
            print("  Install it from: https://github.com/asg017/sqlite-vec")
            print("  You can still use FTS5 text search and SQL queries.")
    except Exception as e:
        print(f"WARNING: Could not set up vector search: {e}")
        print("  Text search and SQL queries will still work.")

    conn.commit()
    conn.close()
    print(f"Database created at: {db_path}")


def init_config(config_path: str) -> None:
    """Create default config.yaml if it doesn't exist."""
    if os.path.exists(config_path):
        print(f"Config already exists at {config_path}")
        return

    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, "w") as f:
        yaml.dump(DEFAULT_CONFIG, f, default_flow_style=False, sort_keys=False)
    print(f"Config created at: {config_path}")
    print("Edit this file to configure your source paths and preferences.")


def main():
    parser = argparse.ArgumentParser(description="Initialize the Prompt Mine database")
    parser.add_argument("--db-path", default=DEFAULT_DB_PATH, help="Path to the SQLite database")
    parser.add_argument("--force", action="store_true", help="Drop and recreate the database")
    args = parser.parse_args()

    init_database(args.db_path, args.force)
    init_config(os.path.join(os.path.dirname(args.db_path), "config.yaml"))

    print("\nSetup complete! Next steps:")
    print("  1. Edit ~/.prompt-mine/config.yaml to configure your source paths")
    print("  2. Run: python scripts/daily_ingest.py --all")
    print("  3. Browse: python scripts/web_server.py --port 8420")


if __name__ == "__main__":
    main()
