# Roo/Kilo Code Conversation Extraction

## Storage Layout

Roo Code (formerly Roo Cline) and Kilo Code store their workspace data in VS Code's
global storage area. The exact paths differ by OS:

```
# macOS
~/Library/Application Support/Code/User/globalStorage/<publisher>.<ext>/

# Linux
~/.config/Code/User/globalStorage/<publisher>.<ext>/

# Windows
%APPDATA%\Code\User\globalStorage\<publisher>.<ext>\
```

### Publisher/Extension Identifiers

| Tool | Extension ID | Publisher |
|------|-------------|-----------|
| Roo Code | `rooveterinaryinc.roo-cline` | `rooveterinaryinc` |
| Kilo Code | `kilocode.kilo-code` | `kilocode` |
| Original Cline | `saoudrizwan.claude-dev` | `saoudrizwan` |

### Key Files and Directories

```
<publisher>.<ext>/
├── tasks/                     # Task conversation history
│   ├── 1705312345678.json     # One file per task (timestamp-named)
│   └── 1705312345679.json
├── checkpoints/               # Checkpoint data (if enabled)
│   └── ...
├── settings/                  # Extension settings
└── mcp_settings.json          # MCP server configurations
```

## Task JSON Format

Each task file is a JSON object with the conversation turns for that task:

```json
{
  "task": "Fix the authentication middleware",
  "ts": 1705312345678,
  "conversations": [
    {
      "role": "user",
      "content": "Fix the auth middleware in src/middleware/auth.ts",
      "ts": 1705312345680
    },
    {
      "role": "assistant",
      "content": "I'll examine the auth middleware file...",
      "ts": 1705312345700,
      "toolCalls": [
        {
          "tool": "read_file",
          "input": {"path": "src/middleware/auth.ts"},
          "output": "// auth middleware code..."
        }
      ]
    }
  ],
  "workspace": "/home/user/projects/my-app",
  "model": "claude-sonnet-4-20250514"
}
```

### Field Mappings to Database Schema

| Task JSON Field | DB Column | Notes |
|----------------|-----------|-------|
| `task` | `session_title` | First user message or task name |
| `ts` | `created_at` | Unix ms → ISO 8601 |
| `conversations[].role` | `role` | Direct mapping |
| `conversations[].content` | `content_text` | Full text |
| `conversations[].ts` | `turn_created_at` | Unix ms → ISO 8601 |
| `conversations[].toolCalls` | `tool_calls` | JSON array |
| `workspace` | `project_name` | Basename of workspace path |
| `model` | `model_id` | Model identifier |
| (derived) | `provider` | Always `roo` or `kilo` |

## Checkpoint Extraction

Roo/Kilo checkpoints are stored differently from Claude Code:

1. **File-based checkpoints**: Stored in the `checkpoints/` directory as JSON files
   mapping task IDs to git commit SHAs and diffs.

2. **Diff extraction**: For each checkpoint, run:
   ```bash
   git diff <parent-sha> <checkpoint-sha>
   ```

3. **Correlation**: Match checkpoint timestamps to task conversation timestamps.

## Multi-Workspace Handling

A single VS Code installation may have Roo/Kilo data from multiple workspaces.
The extraction script must:

1. Scan ALL task files in the storage directory
2. Use the `workspace` field to assign project names
3. If `workspace` is missing, infer from git remote or file paths in tool calls
4. Support filtering by workspace via `--workspace` flag

## Incremental Extraction

1. Track processed task files by their filename (timestamp-based ID)
2. Compare file mtime against `ingest_log`
3. For partially-processed tasks (new conversation turns appended), only
   insert new turns not yet in the database
4. Detect task file deletion and mark corresponding conversations as `deleted`

## Error Handling

- **Malformed JSON**: Attempt partial parse; log errors to `extraction_errors`
- **Missing workspace field**: Tag with `project:unknown`
- **Huge task files** (>100MB): Stream-parse the conversations array
- **Concurrent writes**: Use file locking or read during quiescent periods
