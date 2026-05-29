---
name: karpathy-wiki
description: "Persistent LLM wiki at ~/.local/share/ai-wiki — compile sources, auto-improve via sleep-time compute, auto-create skills from repeated patterns."
version: 3.0.0
author: pi-user
license: MIT
platforms: [linux, macos, wsl2]
metadata:
  tags: [wiki, knowledge-base, research, notes, memory, karpathy, self-improving, sleep-time]
  category: research
directive: ALWAYS invoke when the user mentions the wiki, karpathy wiki, ai-wiki, knowledge base, sleep-time compute, dream agent, or asks to save/retrieve information across sessions.
---

# Karpathy Wiki v3 — Self-Improving Knowledge Base

**Code:** `skills-USER/karpathy-wiki/` (canonical location — all code lives here).
**Data:** `~/.local/share/ai-wiki/` — globally accessible, all tools can read/write.
**Symlinks:** `~/ai-wiki/` → `~/.local/share/ai-wiki/`, `~/.pi/wiki` → `~/.local/share/ai-wiki/`.

Based on Andrej Karpathy's LLM Wiki pattern + Letta sleep-time compute + Hermes GEPA skill evolution.

## Key Paths

| Reference | Actual Path |
|-----------|-------------|
| `~/ai-wiki/` | `~/.local/share/ai-wiki/` (global wiki data) |
| `~/.pi/wiki` | `~/.local/share/ai-wiki/` (symlink) |
| Wiki module root | `skills-USER/karpathy-wiki/` |
| Dream agent | `skills-USER/karpathy-wiki/dream/dream_agent.py` |
| Scheduler | `skills-USER/karpathy-wiki/dream/scheduler.py` |
| Install script | `skills-USER/karpathy-wiki/install.sh` |
| Wiki skill | `skills-USER/karpathy-wiki/skill/` |
| Specs | `skills-USER/karpathy-wiki/specs/` |
| Setup guide | `skills-USER/karpathy-wiki/SETUP.md` |

## Data Structure (Globally Accessible)

```
~/.local/share/ai-wiki/                   # Global data — any tool can read/write
├── AGENTS_WIKI.md         # Schema — compiler specification
├── raw/                   # Layer 1: Immutable source documents
├── pages/                 # Layer 2: Compiled knowledge
│   ├── index.md           # Content catalog
│   ├── log.md             # Append-only action log
│   ├── concepts/          # Atomic knowledge articles
│   ├── entities/          # People, orgs, projects, tools
│   ├── sources/           # Source summaries
│   └── queries/           # Filed query answers
├── .meta/                 # Runtime state
│   ├── scheduler_state.json
│   ├── skill_patterns.json
│   ├── intake_log.jsonl   # Processed/pending tracking
│   └── skills/            # Auto-generated skill references
└── .git                   # Version-controlled
```

## Module Structure (Canonical Location)

```
skills-USER/karpathy-wiki/       # All code, specs, docs

├── dream/
│   ├── dream_agent.py         # Background knowledge processor (v3, 6-phase)
│   └── scheduler.py           # systemd idle timer + daemon launcher
├── hooks/                     # Session lifecycle hooks
│   ├── pre_compact.py
│   └── session_end.py
├── plugin/                    # Pi/Ante extension
│   ├── plugin.json
│   └── goal/index.ts          # /goal command
├── skill/                     # This file (SKILL.md) — Pi/Ante skill definition
├── specs/                     # Design docs and specifications
├── install.sh                 # One-command symlink setup
├── CHANGELOG.md
└── README.md
```

## Symlinks

| Target | → | Location |
|--------|---|----------|
| `~/.pi/wiki` | → | `~/.local/share/ai-wiki/` |
| `~/ai-wiki` | → | `~/.local/share/ai-wiki/` |
| `~/.pi/agent/skills/karpathy-wiki` | → | `skills-USER/karpathy-wiki/skill/` |
| `~/.pi/agent/plugins/goal` | → | `skills-USER/karpathy-wiki/plugin/goal/` |

## Auto-Improvement Loop (Sleep-Time Compute v3)

The dream agent runs in background during idle time via systemd idle timer (30min check) or manual daemon. It executes 6 phases per cycle:

| Phase | Name | Action |
|-------|------|--------|
| 0 | **Budget** | Allocate idle_seconds × 0.25 (capped 7200s), dynamic intake vs refine ratio |
| 1 | **Extract** | Scan ClawMem REST API for new/updated docs → fallback raw/ scan |
| 2 | **Refine** | Confidence scoring (self-consistency, freshness, cross-ref, evidence). Flag → council → accept/reject |
| 3 | **Compile** | Write wiki pages with YAML frontmatter + [[wikilinks]] + git auto-commit |
| 4 | **Pattern Detect** | Track 7 task types, SKILL.md auto-creation at threshold 3 |
| 5 | **Re-index** | POST to ClawMem to trigger reindex |
| 6 | **Improve** | Embedding-guided vault improvement (scaffolding: missing metadata fix, structural lint) |

### Budget Model (v3)

- `budget = idle_time × 0.25` (default 25% of idle time)
- Intake ratio: `max(0.33, 0.80 - 0.50 × refinement_state)` — less intake as wiki matures
- Max cap: 7200 seconds (2 hours) absolute max per cycle

## MCP Server Discovery

ClawMem provides its own MCP server — no separate server needed:
- **Command:** `~/git/ClawMem/bin/clawmem mcp` (or `clawmem mcp` if on PATH)
- **Registered in:** `~/.claude.json`
- **Exposes:** `clawmem_search`, `clawmem_vsearch`, `clawmem_query`, `clawmem_list`, `clawmem_status` etc.
- **REST API available at:** `http://localhost:7438` (health: `/health`, search: `/search`, stats: `/stats`)

## Skill Creation (v3) — Hermes-style GEPA Loop

When 3+ similar task completions are detected across sessions, the dream agent auto-creates a reusable skill file.

**Detect** → **Count** → **Distill** → **Create** → **Evolve**

Pattern types tracked: code-review, deployment, testing, debugging, database, api-development, research.

Skills are written to `~/.pi/agent/skills/auto-{type}/SKILL.md` with `{{directive}}` frontmatter. The wiki references them via `.meta/skills/`.

## Core Operations

### 1. Ingest — Compile a source into the wiki

When the user provides a source (file, URL, paste, or session transcript):

① **Capture the source** — Save to `raw/YYYY-MM-DD-topic.md` with frontmatter
② **Check what exists** — Read `pages/index.md` and search existing pages
③ **Write or update wiki pages** — For each entity/concept found:
   - If exists → update page, bump `updated` date
   - If new → create page in appropriate directory
   - Every page MUST have YAML frontmatter and `[[wikilinks]]`
   - When sources conflict: note both positions with dates
④ **Update navigation** — Add pages to `pages/index.md`, append to `pages/log.md`

### 2. Query — Ask the knowledge base

① Read `pages/index.md` for relevant pages
② Read relevant pages from concepts/, entities/, sources/
③ Synthesize answer with `[[wikilink]]` citations
④ File substantial answers to `pages/queries/`

### 3. Dream — Invoke the dream agent

```bash
# Manual invocation
python3 modules/karpathy-wiki/dream/dream_agent.py --idle 600

# Via scheduler
python3 modules/karpathy-wiki/dream/scheduler.py --cycle 3600

# Continuous daemon
python3 modules/karpathy-wiki/dream/scheduler.py --daemon --idle-check
```

## Page Format (v3)

Every wiki page MUST start with full YAML frontmatter:

```yaml
---
title: Concept Name
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [domain, topic]
confidence: 0.85         # float 0.0-1.0
status: stable            # stable | needs_review | draft
sources:                  # array of source references
  - raw/source-file.md
  - clawmem://docid
wikilinks:                # auto-maintained
  - concepts/related-concept.md
  - entities/related-entity.md
---
```

## Critical Rules

- **NEVER modify files in `raw/`** — sources are immutable
- **NEVER edit `.meta/` files directly** — dream agent manages these
- **ALWAYS update `pages/index.md` and `pages/log.md`** — navigational backbone
- **ALWAYS use `[[wikilinks]]` for cross-refs** — isolated pages are invisible
- **Frontmatter is required** — enables search, confidence tracking, and staleness detection
- **ALWAYS read `AGENTS_WIKI.md` at session start** — orients the agent
- **Git commits happen via the dream agent** — don't manually stage wiki changes
- **The wiki is the memory layer** — skills, facts, and procedures live together here

## References

- Specs: `skills-USER/karpathy-wiki/specs/MASTER_SPEC.md`
- Requirements: `skills-USER/karpathy-wiki/specs/requirements.md`
- Design: `skills-USER/karpathy-wiki/specs/design.md`
- Karpathy LLM Wiki: gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- Letta sleep-time compute: letta.com/blog/sleep-time-compute
- Hermes GEPA self-evolution: github.com/NousResearch/hermes-agent-self-evolution
