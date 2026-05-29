# Prompt Mine Plugin

A unified conversation mining system for Claude Code. Extract, store, search, and
analyze all your AI model interactions across Claude Code, Roo/Kilo Code, OpenAI,
Gemini, and Anthropic exports.

## Installation

```bash
# Clone or copy the plugin directory
cp -r prompt-mine/ ~/.claude/plugins/prompt-mine/

# Or test locally
claude --plugin-dir ./prompt-mine
```

## Quick Start

### 1. Initialize the database

```bash
python3 ~/.claude/plugins/prompt-mine/skills/mine/scripts/init_database.py
```

### 2. Configure sources

Edit `~/.prompt-mine/config.yaml` to set your source paths:
- Claude Code projects directory
- Roo/Kilo Code storage paths
- OpenAI/Gemini/Anthropic export directories

### 3. Run first ingest

```bash
python3 ~/.claude/plugins/prompt-mine/skills/mine/scripts/daily_ingest.py --all
```

### 4. Browse your conversations

```bash
python3 ~/.claude/plugins/prompt-mine/skills/mine/scripts/web_server.py --port 8420
```

Open http://localhost:8420 in your browser.

## Plugin Components

### Skills

- **mine** (`/prompt-mine:mine`) — Primary skill for all prompt-mine operations

### Agents (Subagents)

- **conversation-miner** — Background agent for full extraction pipelines
- **semantic-analyzer** — Embedding generation, clustering, semantic search
- **relationship-mapper** — Find related conversations across providers

### Hooks

- **PostToolUse** — Triggered after Write/Edit in `.claude/` paths
- **SessionEnd** — Checks for new conversations to ingest

### Scripts

| Script | Purpose |
|--------|---------|
| `init_database.py` | Create database and config |
| `extract_claude_code.py` | Mine Claude Code sessions |
| `extract_roo_kilo.py` | Mine Roo/Kilo Code sessions |
| `parse_openai_export.py` | Parse OpenAI data export |
| `parse_gemini_export.py` | Parse Gemini data export |
| `parse_anthropic_export.py` | Parse Anthropic data export |
| `daily_ingest.py` | Run all extractors + processing |
| `rag_pipeline.py` | Search, tag, cluster, embed |
| `web_server.py` | Web UI + API server |

### Resource Documents (Progressive Disclosure)

- `resources/claude-code-extraction.md` — Claude Code session format details
- `resources/roo-kilo-extraction.md` — Roo/Kilo storage layout
- `resources/provider-export-parsing.md` — Export format specifications
- `resources/database-schema.md` — Full DDL and schema design
- `resources/rag-pipeline.md` — Embedding, chunking, search algorithms
- `resources/metadata-tagging.md` — Auto-tagging and clustering rules
- `resources/browser-capture.md` — Tampermonkey userscripts
- `resources/interface-design.md` — Web UI architecture
- `resources/sizing-estimates.md` — Storage projections
- `resources/daily-ingest-setup.md` — Cron/systemd configuration

## Search Examples

```bash
# Semantic search
python3 scripts/rag_pipeline.py --search "how did I configure the RAG pipeline"

# SQL search
python3 scripts/rag_pipeline.py --sql "SELECT * FROM conversations WHERE provider='openai' LIMIT 10"

# Filtered search
python3 scripts/rag_pipeline.py --search "Python debugging" --provider anthropic --project data-kiln
```

## Browser Capture (Real-Time)

Install the Tampermonkey userscripts from `resources/browser-capture.md` to capture
conversations in real-time from chatgpt.com, gemini.google.com, and claude.ai.

## Storage Estimates

| Usage Level | 1 Month | 1 Year |
|------------|---------|--------|
| Light (web only) | 50 MB | 600 MB |
| Typical mixed | 350 MB | 4.2 GB |
| Heavy (50M tokens/day) | 1.4 GB | 16.8 GB |

## Requirements

- Python 3.9+
- SQLite 3.38+ (with FTS5 support)
- Optional: sqlite-vec (for vector search)
- Optional: sentence-transformers (for local embeddings)
- Optional: Flask + flask-cors (for web UI)
- Optional: scikit-learn + hdbscan (for clustering)
- Optional: PyYAML (for config file)

```bash
pip install pyyaml flask flask-cors sentence-transformers scikit-learn hdbscan
```

## License

MIT
