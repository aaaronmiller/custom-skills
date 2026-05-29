---
name: prompt-mine
description: >
  Mine, store, search, and analyze all your AI model interactions. Use when you need to:
  extract conversation history from Claude Code / Roo / Kilo / OpenAI / Gemini / Anthropic exports;
  initialize or update the prompt-mine database; run semantic or SQL searches across conversations;
  tag conversations with project/topic metadata; find related conversations across providers;
  launch the browse interface; set up automated ingestion pipelines or browser capture scripts.
  Trigger phrases: "mine my prompts", "search my conversations", "find when I asked about X",
  "ingest new conversations", "what did I tell the model about Y", "show my project history".
when_to_use: >
  Activate whenever the user wants to extract, search, browse, tag, or analyze their past
  AI conversations from any provider. Also activate for setup tasks like database initialization,
  scheduled ingestion, or Tampermonkey script deployment.
argument-hint: "[action] [query-or-source]"
arguments: action query
disable-model-invocation: false
user-invocable: true
allowed-tools: Read Write Edit Bash Grep Glob
model: inherit
effort: high
context: inline
paths: "**/.claude/**,**/prompt-mine/**,**/conversations/**,**/claude-code/**"
---

# Prompt Mine — Unified Conversation Mining System

You are operating the **prompt-mine** plugin, a system that extracts, stores, searches, and
analyzes every AI conversation the user has across all providers and tools. Your job is to
guide the user through mining their data and to execute the appropriate scripts and workflows.

## Core Architecture

The system has five layers:

1. **Extraction Layer** — Scripts that pull conversations from each source
2. **Storage Layer** — SQLite + SQLite-vec for relational and vector data
3. **Processing Layer** — Metadata tagging, project clustering, summarization
4. **Search Layer** — Hybrid SQL + RAG semantic search
5. **Interface Layer** — Web UI for browsing, expanding, and interacting with conversations

## Quick Reference: Actions

| Action | What It Does | Script / Command |
|--------|-------------|-----------------|
| `init` | Create the database and schema | `scripts/init_database.py` |
| `extract-claude` | Mine Claude Code history & checkpoints | `scripts/extract_claude_code.py` |
| `extract-roo` | Mine Roo/Kilo Code sessions | `scripts/extract_roo_kilo.py` |
| `parse-openai` | Parse OpenAI data export | `scripts/parse_openai_export.py` |
| `parse-gemini` | Parse Google Gemini data export | `scripts/parse_gemini_export.py` |
| `parse-anthropic` | Parse Anthropic data export | `scripts/parse_anthropic_export.py` |
| `ingest-all` | Run all extractors + update DB | `scripts/daily_ingest.py` |
| `search` | Hybrid SQL + semantic search | `scripts/rag_pipeline.py --search` |
| `tag` | Auto-tag conversations with metadata | `scripts/rag_pipeline.py --tag` |
| `cluster` | Cluster conversations by topic/project | `scripts/rag_pipeline.py --cluster` |
| `browse` | Launch the web browse interface | `scripts/web_server.py` |
| `status` | Show DB stats and last ingest times | `scripts/daily_ingest.py --status` |
| `export-browser-capture` | Install Tampermonkey capture scripts | See `resources/browser-capture.md` |

## Step-by-Step Workflow

### 1. First-Time Setup

```
1. Run: python scripts/init_database.py
   This creates the SQLite database at ~/.prompt-mine/prompt_mine.db
   with all tables, indexes, and the vector index.

2. Verify: python scripts/daily_ingest.py --status
   Should show 0 conversations, ready for first ingest.
```

### 2. Extract Conversations

For each source, point the script at the appropriate directory or file:

```bash
# Claude Code — scans ~/.claude/ projects/
python scripts/extract_claude_code.py --projects-dir ~/projects

# Claude Code — also extract checkpoint diffs
python scripts/extract_claude_code.py --projects-dir ~/projects --include-checkpoints

# Roo/Kilo Code — scans workspace storage
python scripts/extract_roo_kilo.py --storage-path ~/.roo/storage

# OpenAI export — point at the unzipped export folder
python scripts/parse_openai_export.py --export-dir ~/Downloads/chatgpt-export

# Gemini export — point at the Takeout folder
python scripts/parse_gemini_export.py --export-dir ~/Downloads/takeout

# Anthropic export — point at the export JSON/ZIP
python scripts/parse_anthropic_export.py --export-file ~/Downloads/anthropic-export.json
```

### 3. Run Full Ingest

```bash
python scripts/daily_ingest.py --all
```

This runs all extractors that have configured source paths, then runs the
processing pipeline: embedding generation, metadata tagging, and project clustering.

### 4. Search

```bash
# Semantic search (natural language)
python scripts/rag_pipeline.py --search "how did I configure the RAG pipeline"

# SQL search (structured)
python scripts/rag_pipeline.py --sql "SELECT * FROM conversations WHERE provider='openai' AND created_at > '2025-01-01'"

# Filtered semantic search
python scripts/rag_pipeline.py --search "Python debugging" --provider anthropic --project data-kiln --limit 20
```

### 5. Browse

```bash
python scripts/web_server.py --port 8420
```

Opens a web UI at http://localhost:8420 where you can:
- Scroll through all conversations with collapsed previews (2-3 lines)
- Expand individual user prompts or model responses
- For responses over the size threshold: see summary + last N lines, with option to view full text
- Filter by provider, project, topic, date range
- Run semantic search directly from the UI

## Response Size Handling

The system applies configurable truncation to model responses:

| Response Size | Storage | Browse Display |
|--------------|---------|----------------|
| < 2,000 chars | Full verbatim | Full text |
| 2,000–20,000 chars | Full text + auto-summary | Summary + last 50 lines (expandable) |
| > 20,000 chars | Full text + auto-summary + chunk embeddings | Summary + last 50 lines (expandable, searchable) |

User prompts are always stored in full.

Configuration is in `~/.prompt-mine/config.yaml` (created on `init`).

## Automated Ingestion

To set up daily automated ingestion, see `resources/daily-ingest-setup.md` for cron
and systemd timer configurations. The Tampermonkey scripts for real-time browser
capture are detailed in `resources/browser-capture.md`.

## Progressive Disclosure References

For deep-dive instructions on specific subsystems, read these resource files
on demand (do NOT load them all into context at once):

- `resources/claude-code-extraction.md` — Claude Code session format, checkpoint parsing, conversation replay
- `resources/roo-kilo-extraction.md` — Roo/Kilo workspace storage layout, state files, task history
- `resources/provider-export-parsing.md` — OpenAI, Gemini, Anthropic export formats and field mappings
- `resources/database-schema.md` — Full schema DDL, indexes, relationships, vector table design
- `resources/rag-pipeline.md` — Embedding model selection, chunking strategy, hybrid search algorithm
- `resources/metadata-tagging.md` — Auto-tagging rules, project detection, topic clustering, NLP pipeline
- `resources/browser-capture.md` — Tampermonkey userscripts for OpenAI, Gemini, Anthropic web UIs
- `resources/interface-design.md` — Web UI architecture, API endpoints, component layout
- `resources/sizing-estimates.md` — Storage projections based on token usage patterns
- `resources/daily-ingest-setup.md` — Cron/systemd configuration, incremental extraction, deduplication

## Subagent Dispatch

For complex multi-step operations, dispatch to specialized subagents:

- **@conversation-miner** — Full extraction pipeline across all sources (runs as background agent)
- **@semantic-analyzer** — Embedding generation, clustering, topic modeling (forked context)
- **@relationship-mapper** — Find related conversations, aggregate by project/topic, inject metadata

These agents are defined in the plugin's `agents/` directory and can be invoked with
`@agent-name` or deployed for async background execution.

## Hooks

This plugin registers hooks for:

- **PostToolUse** (on Write/Edit to `.claude/` paths): Auto-captures Claude Code conversation
  turns if the user has enabled real-time capture in their config
- **SessionEnd**: Runs a lightweight diff to check for new conversations since last ingest

Hook configuration is in `hooks/hooks.json`.
