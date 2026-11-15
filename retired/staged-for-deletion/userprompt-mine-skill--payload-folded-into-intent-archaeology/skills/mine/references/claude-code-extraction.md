# Claude Code Conversation Extraction

## Where Claude Code Stores Conversations

Claude Code stores session data in the project's `.claude/` directory and also maintains
a global conversation database. The primary locations are:

### Project-Level Sessions
```
<project-root>/.claude/
├── sessions/           # JSONL conversation logs
│   ├── 2025-01-15T10-30-00.jsonl
│   └── 2025-01-16T14-22-00.jsonl
├── checkpoints/        # Git checkpoint commits (if enabled)
│   └── ...
└── CLAUDE.md           # Project instructions
```

### Global Session Index
```
~/.claude/
├── projects/           # Per-project session indexes
│   └── <project-hash>/
│       ├── sessions/
│       │   └── <session-id>.jsonl
│       └── session-meta.json
└── memory/             # Auto-memory entries
```

## Session JSONL Format

Each `.jsonl` file contains one JSON object per line, representing a conversation turn:

```json
{"type": "user", "content": "Fix the auth bug in login.py", "timestamp": "2025-01-15T10:30:00Z"}
{"type": "assistant", "content": "I'll examine the auth module...", "timestamp": "2025-01-15T10:30:05Z", "tool_uses": [...]}
{"type": "tool_result", "tool": "Read", "input": {"file_path": "/src/login.py"}, "output": "...", "timestamp": "2025-01-15T10:30:06Z"}
```

### Field Mappings to Database Schema

| JSONL Field | DB Column | Notes |
|-------------|-----------|-------|
| `type` | `role` | `user` → `user`, `assistant` → `assistant`, `tool_result` → `tool` |
| `content` | `content_text` | Full text content |
| `timestamp` | `created_at` | ISO 8601 |
| `tool_uses` | `tool_calls` | JSON array of tool invocations |
| (derived from file path) | `project_name` | Basename of project root |
| (derived from session file) | `session_id` | Filename without extension |

## Checkpoint Extraction

When Claude Code checkpoints are enabled, each checkpoint creates a git commit. To extract
the conversation context that produced each checkpoint:

1. **Parse git log** for checkpoint commits (they have a specific message format):
   ```bash
   git log --all --grep="claude-code checkpoint" --format="%H %ai %s"
   ```

2. **For each checkpoint commit**, extract the diff and the parent commit to understand
   what changed. The conversation that led to the checkpoint can be correlated by timestamp
   with the session JSONL files.

3. **Link checkpoints to conversations** by matching the checkpoint timestamp to the
   session's timestamp range. A single session may produce multiple checkpoints.

### Checkpoint Data Model

Checkpoints are stored in the `checkpoints` table with:
- `commit_hash` — The git commit SHA
- `session_id` — FK to the parent conversation session
- `diff_summary` — A truncated diff (first 500 chars + line count)
- `files_changed` — JSON array of file paths modified
- `created_at` — Commit timestamp

## Incremental Extraction Strategy

To avoid re-processing already-ingested conversations:

1. Track the last-ingested timestamp per project in `ingest_log`
2. Only process `.jsonl` files with mtime > last_ingested_at
3. Use file hash (SHA-256 of file contents) for deduplication
4. On re-ingest, skip files whose hash matches an existing record

## Error Handling

- **Corrupt JSONL lines**: Skip and log to `extraction_errors` table
- **Missing timestamps**: Infer from file mtime or session metadata
- **Large files**: Stream-parse (do not load entire file into memory)
- **Permission errors**: Log and continue, do not halt the pipeline
