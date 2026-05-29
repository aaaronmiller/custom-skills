# 🧠 Karpathy Wiki — Sleep-Time Compute System

Persistent, self-improving knowledge base + dream agent + `/goal` loop.
**Everything lives here.** One directory to install on any machine.

## One-Line Install

```bash
cd skills-USER/karpathy-wiki && ./install.sh
```

This creates all symlinks and optionally sets up cron.

## Structure

```
karpathy-wiki/
├── README.md                  ← this file
├── install.sh                 ← creates symlinks + cron
├── CHANGELOG.md
│
├── wiki/                      ← THE KNOWLEDGE (grows over time)
│   ├── AGENTS_WIKI.md         ← schema / compiler spec
│   ├── raw/                   ← drop source docs here
│   ├── pages/                 ← auto-compiled knowledge
│   │   ├── index.md           ← content catalog
│   │   ├── log.md             ← append-only action log
│   │   ├── concepts/          ← atomic knowledge articles
│   │   ├── entities/          ← people, orgs, tools
│   │   ├── sources/           ← source summaries
│   │   └── queries/           ← filed QA pairs
│   └── .meta/                 ← runtime state
│       ├── step_counter.py
│       ├── skill_patterns.json
│       └── skills/            ← auto-created skill refs
│
├── dream/                     ← sleep-time compute
│   ├── dream_agent.py         ← background knowledge processor
│   └── scheduler.py           ← cron/daemon scheduler
│
├── hooks/                     ← session lifecycle hooks
│   ├── pre_compact.py
│   └── session_end.py
│
├── plugin/                    ← Pi/Ante extensions
│   ├── plugin.json            ← hook registration
│   └── goal/
│       └── index.ts           ← /goal command
│
└── skill/
    └── SKILL.md               ← Pi/Ante skill definition
```

## Symlinks Created

| Target | Points To |
|--------|-----------|
| `~/.pi/wiki` | `karpathy-wiki/wiki/` |
| `~/ai-wiki` | `karpathy-wiki/wiki/` |
| `~/.pi/agent/skills/karpathy-wiki` | `karpathy-wiki/skill/` |
| `~/.pi/agent/plugins/goal` | `karpathy-wiki/plugin/goal/` |

## How to Install on Another Machine

```bash
# Grab this repo
git clone <url> karpathy-wiki
cd karpathy-wiki

# Install symlinks + optional cron
./install.sh

# Start using it
# Drop sources in wiki/raw/
# The dream agent will process them on schedule
```

## Components

### Wiki (`wiki/`)
Three-layer Karpathy-style knowledge base:
- **raw/** — immutable source documents
- **pages/** — LLM-compiled wiki pages with `[[wikilinks]]`
- **.meta/** — runtime state (skill patterns, scheduler state)

### Dream Agent (`dream/`)
Sleep-time compute — runs in background to:
1. Scan raw/ for unprocessed sources
2. Consolidate observations into wiki pages
3. Detect repeated task patterns (3+ → auto-create skill)
4. Lint wiki for broken links, orphans, contradictions

### Goal Plugin (`plugin/goal/`)
`/goal <task>` command — keeps agent iterating on a goal across turns with judge-based completion checking.

### Hooks (`hooks/`)
Session lifecycle callbacks:
- `pre_compact.py` — captures context before compaction
- `session_end.py` — captures transcripts to raw/

## Redesign

See `REDESIGN.md` for the planned overhaul:
- Percentage-based time budgets
- Dynamic intake vs refinement ratio
- Deliberative refinement confidence scoring
- Model tokens/second allocation
