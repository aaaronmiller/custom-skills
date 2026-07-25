# cass Field Fidelity

> **When to read:** before Phase 5 (prompt extraction), or when extraction
> yields surprising results.

## What cass normalizes

`cass` (github.com/Dicklesworthstone/coding_agent_session_search) indexes
session histories from 11+ providers — Claude Code, Codex, Cursor, Gemini
CLI, Aider, ChatGPT, and more — into a unified Tantivy index backed by
SQLite. The unification is what makes cass useful, but it flattens away
fields that matter for intent archaeology.

## Fields cass carries

These are documented in cass's CLI output and confirmed by `cass
capabilities --json` and `cass stats --json`:

- `title` — session title
- `content` — message text
- `agent` — `claude`, `codex`, `cursor`, `gemini`, `aider`, `chatgpt`
- `workspace` — project path (when detectable)
- `created_at` — session creation timestamp
- `source_path` — absolute path to the underlying JSONL file
- `line_number` — line within the JSONL (1-indexed)
- `score` — search relevance score
- `snippet` — match excerpt
- `toolUseResult` — flattened into message text (not preserved as
  structured field)

## Fields cass flattens away

These exist in the raw harness JSONL but are NOT in cass's index. The
audit needs them, so the skill does a second-pass extraction from the
raw JSONL on `source_path:line_number`:

| Field | Why it matters | Where to get it back |
|-------|----------------|----------------------|
| `isSidechain` | Agent-written prompts to subagents look identical to user-typed prompts. Feed those into the intent corpus and frequency counts corrupt the constitution. | raw JSONL on `source_path:line_number` |
| `gitBranch` | The spec-kit feature key (`003-chat-system`). Critical for spec archaeology. | raw JSONL |
| `parentUuid` | Rewinds and edited turns get counted as separate instructions instead of revisions of one. | raw JSONL |
| `toolUseResult` structured form | Errors and tool outputs are flattened into message text. The audit needs them as evidence. | raw JSONL, or `cass export <path> --include-tools` |

## The pattern: cass selects, raw JSONL extracts

cass is the selector. The raw JSONL on disk is the extractor. The
round-trip:

```bash
# 1. cass selects relevant sessions (Phase C enumeration)
cass search "" --workspace /abs/path --robot-format sessions --days 30

# 2. For each session, cass exports the structured conversation
cass export /path/to/session.jsonl --format json > session.json

# 3. Optionally include tool calls
cass export /path/to/session.jsonl --include-tools > session_with_tools.json

# 4. For a specific line of interest, cass views it with context
cass view /path/to/session.jsonl -n 42 -C 10 --json

# 5. To expand context around a line, use --line (not -n)
cass expand /path/to/session.jsonl --line 42 -C 3 --json
```

The enrichment pass materializes a derived table:

```sql
CREATE TABLE prompt_audit_fields (
  prompt_id INTEGER PRIMARY KEY REFERENCES prompts(id),
  source_path TEXT NOT NULL,
  line_number INTEGER NOT NULL,
  is_sidechain BOOLEAN NOT NULL,
  git_branch TEXT,
  parent_uuid TEXT,
  tool_use_result_json TEXT,
  FOREIGN KEY (source_path, line_number) REFERENCES cass_index(source_path, line_number)
);
```

This is not duplication — it's the audit fields cass doesn't carry, with
a foreign key back to cass for any future re-derivation.

## Performance note

cass documents degradation above ~500k messages. Run `cass stats --json`
early. If your corpus is near that threshold, prefer `cass search ...
--fields minimal --json` for enumeration (paths only) and reserve
`--fields full` for the actual extraction pass.

## When you can't get the raw JSONL

If the raw JSONL file has been deleted (some harnesses rotate logs),
cass's flattened fields are all you have. Mark the prompt with
`source: "cass-only"` in the `prompts` table and exclude it from any
audit dimension that needs `isSidechain` / `gitBranch` / `parentUuid`.
The wiki shows these prompts with a "⚠️ source-degraded" badge.

## Cross-references

- `references/scope_selectors.md` — how to scope the extraction
- `references/corpus_sources.md` — the 13 corpus sources, of which
  cass is one
- `references/failure_modes.md` #3 — "cass search for Phase C" failure
