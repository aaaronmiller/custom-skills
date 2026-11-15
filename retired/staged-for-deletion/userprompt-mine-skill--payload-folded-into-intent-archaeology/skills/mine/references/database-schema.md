# Database Schema

## Overview

The database is SQLite with the [sqlite-vec](https://github.com/asg017/sqlite-vec)
extension for vector similarity search. This avoids the need for a separate vector
database while providing hybrid SQL + semantic search in a single query engine.

**Database location**: `~/.prompt-mine/prompt_mine.db`

## Entity-Relationship Diagram

```
┌──────────────────┐     ┌──────────────────────┐     ┌────────────────────┐
│   conversations   │────<│   conversation_turns  │>────│   turn_embeddings  │
│                   │  1:N│                       │  1:1 │                    │
└──────────────────┘     └──────────────────────┘     └────────────────────┘
        │                          │
        │ 1:N                      │ 1:N
        ▼                          ▼
┌──────────────────┐     ┌──────────────────────┐
│  checkpoints      │     │   tool_calls          │
│                   │     │                       │
└──────────────────┘     └──────────────────────┘
        │
        │                          ┌──────────────────────┐
        │                          │   conversation_tags   │
        │                          └──────────────────────┘
        │                                   │ M:N
        ▼                                   ▼
┌──────────────────┐     ┌──────────────────────┐
│   projects        │     │   tags                │
│                   │>────│                       │
└──────────────────┘     └──────────────────────┘

┌──────────────────┐     ┌──────────────────────┐
│   ingest_log      │     │   extraction_errors   │
└──────────────────┘     └──────────────────────┘
```

## DDL

### conversations

```sql
CREATE TABLE conversations (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    provider        TEXT NOT NULL,          -- 'anthropic'|'openai'|'gemini'|'claude-code'|'roo'|'kilo'|'browser-capture'
    session_id      TEXT NOT NULL,          -- Provider's conversation ID
    session_title   TEXT,                   -- Conversation title / first user msg truncated
    project_name    TEXT,                   -- Detected or assigned project name
    model_id        TEXT,                   -- Primary model used (e.g. 'claude-sonnet-4-20250514')
    source_path     TEXT,                   -- File path or URL where this was extracted from
    source_hash     TEXT,                   -- SHA-256 of source file for dedup
    turn_count      INTEGER DEFAULT 0,      -- Number of turns
    user_turn_count INTEGER DEFAULT 0,      -- Number of user turns
    total_chars     INTEGER DEFAULT 0,      -- Total character count across all turns
    created_at      TEXT NOT NULL,          -- First turn timestamp (ISO 8601 UTC)
    updated_at      TEXT NOT NULL,          -- Last turn timestamp
    ingested_at     TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    is_deleted      INTEGER DEFAULT 0,      -- Soft delete flag
    metadata_json   TEXT,                   -- Provider-specific extra data

    UNIQUE(provider, session_id)
);

CREATE INDEX idx_conversations_provider ON conversations(provider);
CREATE INDEX idx_conversations_project ON conversations(project_name);
CREATE INDEX idx_conversations_model ON conversations(model_id);
CREATE INDEX idx_conversations_created ON conversations(created_at);
CREATE INDEX idx_conversations_ingested ON conversations(ingested_at);
```

### conversation_turns

```sql
CREATE TABLE conversation_turns (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    turn_index      INTEGER NOT NULL,       -- 0-based position in conversation
    role            TEXT NOT NULL,           -- 'user'|'assistant'|'system'|'tool'
    content_text    TEXT NOT NULL,           -- Full text content
    content_summary TEXT,                   -- Auto-generated summary (for long responses)
    content_truncated TEXT,                 -- Summary + last 50 lines (for browse display)
    thinking_content TEXT,                  -- Extended thinking content (if available)
    model_id        TEXT,                   -- Per-turn model override
    tool_calls      TEXT,                   -- JSON array of tool invocations
    char_count      INTEGER DEFAULT 0,      -- Character count of content_text
    token_estimate  INTEGER DEFAULT 0,      -- Rough token estimate (chars / 4)
    created_at      TEXT NOT NULL,          -- Turn timestamp
    ingested_at     TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    metadata_json   TEXT,                   -- Provider-specific per-turn data

    UNIQUE(conversation_id, turn_index)
);

CREATE INDEX idx_turns_conversation ON conversation_turns(conversation_id);
CREATE INDEX idx_turns_role ON conversation_turns(role);
CREATE INDEX idx_turns_created ON conversation_turns(created_at);

-- Full-text search index
CREATE VIRTUAL TABLE conversation_turns_fts USING fts5(
    content_text,
    content_summary,
    content='conversation_turns',
    content_rowid='id',
    tokenize='unicode61'
);

-- FTS trigger: insert
CREATE TRIGGER turns_fts_insert AFTER INSERT ON conversation_turns BEGIN
    INSERT INTO conversation_turns_fts(rowid, content_text, content_summary)
    VALUES (new.id, new.content_text, new.content_summary);
END;

-- FTS trigger: delete
CREATE TRIGGER turns_fts_delete AFTER DELETE ON conversation_turns BEGIN
    INSERT INTO conversation_turns_fts(conversation_turns_fts, rowid, content_text, content_summary)
    VALUES ('delete', old.id, old.content_text, old.content_summary);
END;
```

### turn_embeddings (Vector Table)

```sql
-- Requires sqlite-vec extension loaded
CREATE VIRTUAL TABLE turn_embeddings USING vec0(
    turn_id INTEGER PRIMARY KEY,
    embedding float[768]    -- Dimension matches embedding model (default: all-MiniLM-L6-v2)
);

-- Lookup by turn ID
CREATE INDEX idx_embeddings_turn ON turn_embeddings(turn_id);
```

### tool_calls

```sql
CREATE TABLE tool_calls (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    turn_id         INTEGER NOT NULL REFERENCES conversation_turns(id) ON DELETE CASCADE,
    tool_name       TEXT NOT NULL,           -- e.g. 'Read', 'Write', 'Bash', 'Grep'
    tool_input      TEXT,                    -- JSON input parameters
    tool_output     TEXT,                    -- Truncated output (max 10000 chars)
    output_truncated INTEGER DEFAULT 0,     -- Whether output was truncated
    created_at      TEXT,                    -- When the tool was invoked

    FOREIGN KEY (turn_id) REFERENCES conversation_turns(id)
);

CREATE INDEX idx_tool_calls_turn ON tool_calls(turn_id);
CREATE INDEX idx_tool_calls_name ON tool_calls(tool_name);
```

### checkpoints

```sql
CREATE TABLE checkpoints (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    commit_hash     TEXT NOT NULL,           -- Git commit SHA
    diff_summary    TEXT,                    -- First 500 chars of diff + line count
    files_changed   TEXT,                    -- JSON array of file paths
    created_at      TEXT NOT NULL,

    UNIQUE(conversation_id, commit_hash)
);

CREATE INDEX idx_checkpoints_conversation ON checkpoints(conversation_id);
```

### tags

```sql
CREATE TABLE tags (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    tag_name        TEXT NOT NULL UNIQUE,    -- e.g. 'project:data-kiln', 'topic:python', 'type:debugging'
    tag_type        TEXT NOT NULL,           -- 'project'|'topic'|'language'|'framework'|'type'|'custom'
    created_at      TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),

    UNIQUE(tag_name)
);

CREATE INDEX idx_tags_type ON tags(tag_type);
```

### conversation_tags

```sql
CREATE TABLE conversation_tags (
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    tag_id          INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    confidence      REAL DEFAULT 1.0,       -- Auto-tag confidence (0.0-1.0)
    source          TEXT DEFAULT 'auto',     -- 'auto'|'user'|'rule'
    created_at      TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),

    PRIMARY KEY (conversation_id, tag_id)
);
```

### projects

```sql
CREATE TABLE projects (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    project_name    TEXT NOT NULL UNIQUE,    -- Unique project identifier
    project_path    TEXT,                    -- Root directory path (if applicable)
    description     TEXT,                    -- Auto-generated or user-provided description
    conversation_count INTEGER DEFAULT 0,
    first_seen      TEXT,                    -- Earliest conversation date
    last_seen       TEXT,                    -- Latest conversation date
    created_at      TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    metadata_json   TEXT
);

CREATE INDEX idx_projects_name ON projects(project_name);
```

### ingest_log

```sql
CREATE TABLE ingest_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    provider        TEXT NOT NULL,
    source_path     TEXT NOT NULL,
    source_hash     TEXT,
    records_added   INTEGER DEFAULT 0,
    records_skipped INTEGER DEFAULT 0,
    errors          INTEGER DEFAULT 0,
    started_at      TEXT NOT NULL,
    completed_at    TEXT,
    status          TEXT DEFAULT 'running',  -- 'running'|'completed'|'failed'
    notes           TEXT
);

CREATE INDEX idx_ingest_provider ON ingest_log(provider);
CREATE INDEX idx_ingest_status ON ingest_log(status);
```

### extraction_errors

```sql
CREATE TABLE extraction_errors (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    ingest_log_id   INTEGER REFERENCES ingest_log(id),
    provider        TEXT NOT NULL,
    source_path     TEXT,
    error_type      TEXT NOT NULL,           -- 'parse_error'|'io_error'|'dedup_error'|'schema_error'
    error_message   TEXT NOT NULL,
    raw_data        TEXT,                    -- The problematic data (truncated to 2000 chars)
    created_at      TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);
```

## Key Design Decisions

1. **SQLite over PostgreSQL**: Single-file, zero-config, portable. sqlite-vec provides
   vector search without a separate service. Sufficient for single-user workloads up to
   millions of turns.

2. **FTS5 for text search**: SQLite's built-in full-text search handles keyword and
   phrase queries. Combined with vector search for semantic similarity, this provides
   a hybrid search capability.

3. **Truncation columns**: `content_summary` and `content_truncated` are pre-computed
   at ingest time so the browse interface never needs to process raw content on-the-fly.

4. **Soft deletes**: `is_deleted` flag on conversations preserves data integrity when
   source conversations are removed from providers.

5. **Metadata JSON**: Provider-specific fields that don't map to standard columns are
   stored as JSON, allowing flexible schema evolution without ALTER TABLE.
