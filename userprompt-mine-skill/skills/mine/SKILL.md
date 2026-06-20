---
name: prompt-mine
description: >
  Mine, store, search, report, and continuously improve across all your coding agent
  sessions (Claude Code, Codex, Cursor, ChatGPT, Aider, Gemini, Cline, and 15+ more).
  Backed by CASS (coding-agent-search). Use when you need to find a past session,
  generate project activity reports, get weekly/daily digests, discover incomplete work,
  or analyze tool usage patterns across all your projects.
  Self-improves: each run logs performance, adapts search strategies, and refines
  reporting templates. Trigger phrases: "search sessions", "project activity report",
  "weekly digest", "what happened this week", "find when I fixed", "agent usage report",
  "incomplete projects", "todays brief", "sprint retro", "error patterns", "tech radar".
when_to_use: >
  Activate for ANY request involving past coding agent sessions, project activity
  analysis, cross-project reporting, agent utilization metrics, or finding information
  buried in session history. Also activate for indexing, setup, and system health tasks.
  In case of ambiguity, default to `cass triage --json` as the opening move.
argument-hint: "[search-query] | report:<type> | index | status | browse | reflect"
arguments: action query
disable-model-invocation: false
user-invocable: true
allowed-tools: Read Write Edit Bash Grep Glob
model: inherit
effort: high
context: inline
paths: "**/.claude/**,**/.codex/**,**/.cursor/**,**/.gemini/**,**/.cass/**,**/.local/share/coding-agent-search/**"
---

# Prompt Mine — CASS-Powered Session Mining & Reporting

Backed by **CASS** (coding-agent-search), which indexes sessions from 21+ coding
agents into a unified SQLite database with Tantivy FTS, ANN vector search, and
a cross-encoder reranker.

## 0. Pre-Flight Check

```bash
if ! command -v cass &>/dev/null; then
  echo "MISSING: CASS not installed — tell user to install"
  # See references/cass-install-guide.md for full instructions
fi
cass --version
cass health --json     # must return {"healthy": true} before proceeding
```

If health fails, run `cass index --full`. Do not proceed until healthy.

## 1. Core Workflows

### 1.1 Search (Primary)

```bash
# Always use --robot for JSON output
cass search "<query>" --robot --limit 10

# Key fields per hit: title, snippet, agent, workspace, score, match_type,
# source_path, created_at, line_number

# Common patterns:
cass search "<q>" --robot --agent claude                      # by agent
cass search "<q>" --robot --workspace /path                   # by project
cass search "<q>" --robot --days 7                            # recent
cass search "<q>" --robot --since 2026-01-01 --until 2026-03-01  # date range
cass search "<q>" --robot --mode semantic                     # conceptual
cass search "<q>" --robot --mode hybrid                       # best of both
cass search "<q>" --robot --fields minimal                    # token-efficient
cass search "<q>" --robot --aggregate agent,workspace,date    # server-side counts
```

### 1.2 Deep Dive

```bash
cass view /path/to/session.jsonl -n 42 --json        # peek at match
cass expand /path/to/session.jsonl -n 42 -C 5 --json # widen context
cass export /path/to/session.jsonl --format markdown  # export session
```

### 1.3 Diagnostics & Setup

```bash
cass triage --json       # best first command — tells you what to do
cass status --json       # full snapshot
cass capabilities --json # feature discovery
cass index               # incremental (fast)
cass index --full        # first-time or full rebuild
cass index --watch       # real-time background watcher
```

### 1.4 Model Installation (for --mode semantic)

```bash
cass models install minilm  # default (~90 MB)
cass models list --json     # verify
```

---

## 2. Quick Reference: Actions

| Action | What | CASS Command |
|--------|------|-------------|
| `init` | First-time setup | `cass index --full` |
| `index` | Incremental | `cass index` |
| `search <q>` | Find anything | `cass search "<q>" --robot --limit 10` |
| `view <path> -n N` | Session context | `cass view <path> -n N --json` |
| `sessions` | List sessions | `cass sessions --current --json` |
| `timeline` | Recent activity | `cass timeline --days 7 --json` |
| `stats` | System stats | `cass stats --json` |
| `health` | Readiness | `cass health --json` |
| `report:<type>` | Generate a report | See `references/cass-report-patterns.md` |
| `reflect` | Post-run improvement | See `references/cass-self-improvement.md` |
| `watch` | Start watcher | `cass index --watch` |
| `browse` | Web UI | `cass serve --port 8420` or `python scripts/web_server.py` |
| `models` | Embedders | `cass models install <model>` |

---

## 3. Report Types (15 Patterns)

> Full detail in `references/cass-report-patterns.md` — read that file when
> any `report:<type>` action is triggered.

| # | Report | Purpose | Key Commands |
|---|--------|---------|-------------|
| 1 | Daily Brief | Today's activity | `cass timeline --today --json` |
| 2 | Weekly Digest | 7-day summary | `cass timeline --days 7 --json` |
| 3 | Monthly Review | 30-day trends | `cass timeline --days 30 --json` + aggregation |
| 4 | Sprint Retro | Activity since date | `cass search "error|TODO" --since YYYY-MM-DD` |
| 5 | Project Deep Dive | All sessions for a project | `cass search "" --workspace PATH` |
| 6 | Cross-Project Dashboard | All projects at once | `cass search "" --aggregate workspace` |
| 7 | Stale Projects | Untouched in N days | Cross-reference workspaces with `--days N` |
| 8 | Agent Utilization | Per-agent usage stats | `cass stats --json` + aggregation |
| 9 | Agent Cross-Reference | Multi-agent projects | Query workspaces with >1 distinct agent |
| 10 | Work-in-Progress | Open/unresolved sessions | `cass sessions --current` + search for "in progress" |
| 11 | Outstanding TODOs | Technical debt markers | `cass search "TODO|FIXME|HACK|XXX"` |
| 12 | Error Patterns | Common failures | `cass search "error|crash|panic|timeout"` |
| 13 | Technology Radar | Languages/frameworks used | Extract tech names from session snippets |
| 14 | Activity Heatmap | Day-by-day density | `cass search "" --days 90 --aggregate date` |
| 15 | Learning Summary | What was learned in period | `cass search "learned|discovered"` + error patterns |

**Composition rule:** If the user's request doesn't match exactly, run the closest
report + supplementary searches and combine the results.

---

## 4. Self-Improvement Loop

> Full protocol in `references/cass-self-improvement.md` — read that file when
> the `reflect` action is triggered or at end of any prompt-mine invocation.

After every invocation, silently:
1. **Log** the session to `~/.prompt-mine/refinement-log/$(date +%Y-%m).md`
2. **Assess** tool use (--robot consistent? Limits right? Mode chosen correctly?)
3. **Check** for pattern emergence (same suggestion 3+ times → propose refinement)
4. **Apply** refinements with user approval when thresholds are met

---

## 5. Subagent Dispatch

| Agent | Trigger | Task |
|-------|---------|------|
| `@conversation-miner` | `init`, `index`, `watch` | Runs `cass index`, verifies health, reports stats |
| `@semantic-analyzer` | Semantic/fuzzy/hybrid search | Installs models, runs `--mode semantic`, interprets scores |
| `@relationship-mapper` | Cross-referencing, handoff detection | Multi-agent searches, pipeline mode, aggregation |
| `@report-architect` | Any `report:<type>` | Executes report commands, formats output |
| `@skill-refiner` | Post-run or explicit `reflect` | Analyzes reflection log, manages refinement lifecycle |

---

## 6. Error Handling

| Situation | Action |
|-----------|--------|
| `cass` not found | **Block.** Show install instructions. Do not proceed until `cass health --json` passes. |
| `healthy: false` | Run `cass index --full`. If still fails: `cass index --full --force-rebuild` |
| No index exists | Run `cass index --full`. Warn user this may take a few minutes. |
| Stale index | Run `cass index` (incremental) |
| Semantic = 0 results | Fall back to `--mode lexical` or `--mode hybrid` |
| Malformed --robot output | Re-run without `--robot` to see stderr diagnostics |
| Context limit risk | Use `--fields minimal`, `--max-tokens N`, `--limit 5` |

---

## 7. Fallback: Legacy Python Scripts

The original Python scripts in `scripts/` work independently on their own
`~/.prompt-mine/prompt_mine.db`. Use them only if CASS is unavailable.

---

## 8. File Map

```
userprompt-mine-skill/
└── skills/mine/
    ├── SKILL.md                   ← THIS FILE
    ├── agents/                    ← Subagent definitions
    ├── scripts/                   ← Legacy Python fallback scripts
    ├── references/                 ← Progressive-disclosure docs
    │   ├── cass-report-patterns.md   ← 15 report types (referenced from §3)
    │   ├── cass-self-improvement.md  ← Reflection protocol (referenced from §4)
    │   └── <legacy docs>             ← Original Python-era docs (fallback reference)
    └── refinement-log/            ← Auto-created post-run reflections
```
