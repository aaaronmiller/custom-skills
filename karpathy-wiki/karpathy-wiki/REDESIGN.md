# Sleep-Time Compute Redesign

## Problem Summary

Current system is structurally wired but **dead in the water**:
- No daemon, cron, or hook infrastructure actually triggers the dream agent
- Step-counter approach can't work (Ante 0.preview.16 has no per-interaction hooks)
- Raw/ folder is empty — nothing to process
- No time-budgeting, no allocation strategy, no confidence scoring

## Design Goals

| Goal | Priority | Why |
|------|----------|-----|
| **Idle-based scheduling** | P0 | Only viable trigger mechanism on Ante |
| **Time budget allocation** | P0 | Prevent runaway token consumption |
| **Dynamic intake/refinement ratio** | P1 | Adapt to wiki maturity state |
| **Deliberative refinement confidence** | P1 | Know what you know, know what you don't |
| **Metadata/YAML schema** | P1 | Cross-referencing, provenance, staleness |
| **Intake log system** | P1 | Track processed vs pending across restarts |
| **Model tokens/sec calibration** | P2 | Fair allocation across different models |

## Architecture

### Dual-Agent Pattern (Letta-inspired)

Following Letta's proven sleep-time architecture:

```
┌─────────────────────────────┐     ┌─────────────────────────────┐
│     PRIMARY AGENT           │     │      DREAM AGENT            │
│  (user-facing, fast model)  │     │  (background, thorough)     │
│                             │     │                             │
│  Tools: conversation,       │     │  Tools: memory blocks,      │
│         search, tool exec   │     │         wiki edit, lint     │
│                             │     │                             │
│  Memory: read-only (from    │────►│  Memory: read-write (edits  │
│          dream agent)       │     │          primary agent's    │
│                             │     │          memory blocks)     │
└─────────────────────────────┘     └─────────────────────────────┘
         │                                    │
         │         ┌──────────────────┐        │
         │         │  Memory Blocks   │        │
         └────────►│  (shared state)  │◄───────┘
                   │                  │
                   │  - persona       │
                   │  - human         │
                   │  - wiki index    │
                   │  - skill index   │
                   └──────────────────┘
```

Key insight from Letta's research: separate the agents so memory management doesn't
compete with conversation. The dream agent can use a slower/thorough model since
latency doesn't matter. The primary agent stays fast.

### Trigger Mechanism: Systemd Idle Timer (Ante-compatible)

Ante has no hook system yet. The only viable trigger is OS-level idle detection:

```
┌──────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ systemd      │───►│  idle-check.sh    │───►│  dream_agent.py │
│ --idle timer │    │  (checks: no pi   │    │  (runs with     │
│              │    │   process in 5min)│    │   time budget)  │
└──────────────┘    └──────────────────┘    └─────────────────┘
```

The timer fires every 30 minutes. The idle-check guards against running while
the user is active. The dream agent itself enforces a percentage-based time budget.

Systemd user timer:

```ini
# ~/.config/systemd/user/karpathy-dream.timer
[Unit]
Description=Karpathy Wiki Dream Agent Timer

[Timer]
OnBootSec=5min
OnUnitInactiveSec=30min
Persistent=true

[Install]
WantedBy=default.target
```

```ini
# ~/.config/systemd/user/karpathy-dream.service
[Unit]
Description=Karpathy Wiki Dream Agent
After=network.target

[Service]
Type=oneshot
ExecStart=%h/code/karpathy-wiki/dream/scheduler.py --cycle
Environment=AI_WIKI=%h/code/karpathy-wiki/wiki
```

Fallback: if systemd isn't available, use a simple cron with a lockfile:

```cron
*/30 * * * * ~/code/skills-USER/karpathy-wiki/dream/scheduler.py --cron
```

## Time Budget System

### Percentage-Based Budget

The core concept: the dream agent runs with **a fixed percentage of wall-clock time**
since last run, not a fixed number of iterations or tokens.

```
budget_seconds = (now - last_run_time) * BUDGET_PERCENTAGE

Example: BUDGET_PERCENTAGE = 0.25 (25%)
  - Idle for 1 hour  →  15 minutes of dreaming
  - Idle for 6 hours →  90 minutes of dreaming
  - Idle for 24 hours → 6 hours of dreaming (capped)
```

The budget caps at a configurable maximum to prevent runaway:

```
max_budget_seconds = 7200  # 2 hours absolute max per cycle
```

### Why Percentage-Based

Letta's paper found that sleep-time compute produces a **Pareto improvement**:
more sleep-time compute → better accuracy, with diminishing returns. The percentage
approach is self-balancing:

- **Heavy use (little idle time)**: Small budget, dream agent catches up on essentials
- **Light use (lots of idle time)**: Large budget, deep refinement cycles
- **No use (vacation)**: Max budget, full re-processing and lint sweep

This avoids the step-counter problem (can't rely on Ante hooks) AND the fixed-interval
problem (wasteful if user is active, insufficient if user is away).

### Dynamic Intake vs Refinement Ratio

The budget is split between two phases:

```
intake_budget = total_budget * INTAKE_RATIO
refinement_budget = total_budget * (1 - INTAKE_RATIO)
```

The **wiki refinement state** determines the ratio:

```python
def calc_refinement_state(wiki):
    """Score 0.0-1.0: how well-refined is the wiki?"""
    raw_count = len(list_raw_files(wiki))
    page_count = len(list_wiki_pages(wiki))
    orphan_count = count_orphan_pages(wiki)
    stale_count = count_stale_pages(wiki, max_age_days=30)
    broken_links = count_broken_links(wiki)
    
    if page_count == 0:
        return 0.0
    
    # Factors: source-vs-page coverage, health, freshness
    coverage = min(1.0, page_count / max(1, raw_count))
    health = 1.0 - (orphan_count + broken_links) / max(1, page_count)
    freshness = 1.0 - stale_count / max(1, page_count)
    
    return 0.5 * coverage + 0.3 * health + 0.2 * freshness

def calc_ratio(refinement_state):
    """Map refinement state to intake/refinement split.
    
    Very raw wiki (0.0): 80% intake, 20% refinement — get basic coverage
    Mid wiki (0.5):      50/50 split
    Mature wiki (0.9+):  30% intake, 70% refinement — polish what you have
    """
    # Linear interpolation
    intake_ratio = 0.80 - (0.50 * refinement_state)
    # At 0.0 → 0.80, at 1.0 → 0.30
    return max(0.10, min(0.90, intake_ratio))
```

The 94% example from the summary maps to:
- refinement_state = 0.94
- intake_ratio = 0.80 - (0.50 × 0.94) = 0.33
- Split: 33% intake / 67% refinement ✓

### Model Tokens/Second Allocation

Different models have different throughput. A tokens/second conversion ensures
fair allocation regardless of which model the dream agent uses:

```python
MODEL_SPEEDS = {
    "deepseek/deepseek-chat":    120,   # tokens/sec (measured)
    "deepseek/deepseek-r1":       40,   # tokens/sec (measured)
    "anthropic/claude-sonnet-4":  80,   # tokens/sec (estimated)
    "openai/gpt-4o-mini":        200,   # tokens/sec (estimated)
    "google/gemini-2-flash":     150,   # tokens/sec (estimated)
}

def allocate_tasks(budget_seconds, model, pending_tasks):
    """Allocate tasks based on time budget and model speed.
    
    Each task has estimated token cost. The model's tokens/sec determines
    how many tasks can fit in the budget.
    """
    model_speed = MODEL_SPEEDS.get(model, 100)  # default 100 tok/s
    max_tokens = int(budget_seconds * model_speed)
    
    # Sort tasks by priority (intake first, then refinement)
    # Greedily allocate until budget exhausted
    allocated = []
    total_cost = 0
    for task in pending_tasks:
        task_cost = estimate_task_cost(task)  # tokens needed
        if total_cost + task_cost <= max_tokens:
            allocated.append(task)
            total_cost += task_cost
        else:
            break
    
    return allocated, total_cost, max_tokens
```

## Deliberative Refinement Confidence Scoring

### Why Refinement, Not Just Scoring

The dream agent currently does simple pattern matching (keyword → category).
This produces high recall but low precision. **Deliberative refinement** means:

1. The agent thinks about whether its own output is correct
2. It scores each claim with confidence
3. Low-confidence claims get flagged, not silently added
4. Contradictory claims from different sources are noted

### Implementation: Two-Stage Pipeline

```
Raw content
    │
    ▼
Stage 1: EXTRACT ───► Raw observations with source citations
    │                   (fast model, high recall)
    │
    ▼
Stage 2: REFINE ─────► Scored, cross-referenced wiki pages
                        (slower model, high precision)
```

**Stage 1 (Extract)**: Uses the fast model to extract candidate observations
from raw sources. This is the current keyword-matching replacement — the model
actually reads and understands the content.

**Stage 2 (Refine)**: Uses a slower/judge model (or council) to:

```python
def refine_observation(observation, existing_pages):
    """Score a candidate observation and decide: add, merge, flag, reject."""
    
    # 1. Self-consistency check
    #    Does the observation contradict itself?
    
    # 2. Cross-reference check
    #    Does it match, contradict, or extend existing wiki pages?
    
    # 3. Source freshness check
    #    Is the source recent? Is it reputable?
    
    # 4. Confidence score
    confidence = calculate_confidence(
        self_consistency=0.9,
        source_freshness=0.7,
        cross_ref_match=0.8,
        evidence_count=3,
    )
    # → 0.85 (high confidence, add to wiki)
    
    # Decision matrix:
    # confidence > 0.8:  ADD to wiki (high confidence)
    # confidence 0.5-0.8: FLAG for user review
    # confidence < 0.5:  REJECT (not enough evidence)
    # confidence > 0.6 AND contradicts existing: NOTE BOTH POSITIONS
    
    return decision
```

### Adversarial Council for Edge Cases

Following the proven `convene_council` pattern from pi-agent-suite,
use two-model deliberation for the hard cases:

- Split confidence (e.g., `refine()` returns 0.55)
- Contradictory sources (Source A says X, Source B says not-X)
- Wiki already has high-confidence claim that conflicts

The council format:

```json
{
  "claim": "Python 3.12 supports f-string debugging",
  "sources": ["raw/python-312-release.md"],
  "existing_pages": ["concepts/python-features.md <- says 'not yet available'"],
  "council_verdict": {
    "judge_a": {"confidence": 0.9, "verdict": "true", "reason": "PEP 701 merged"},
    "judge_b": {"confidence": 0.95, "verdict": "true", "reason": "Confirmed in 3.12.0"},
    "consensus": "true",
    "action": "update_page_and_flag_contradiction"
  }
}
```

## Metadata & YAML Frontmatter Schema

Every wiki page and every raw source gets YAML frontmatter. This is the
cross-referencing backbone.

### Raw Source Frontmatter

```yaml
---
title: "Python 3.12 Release Notes"
source_type: session | file | url | paste
source_path: "raw/2024-10-02-python-312.md"
created: 2024-10-02T14:30:00Z
ingested: 2024-10-02T14:35:00Z
content_hash: "a1b2c3d4e5f6..."    # sha256 of content
size_tokens: 2847
confidence: 0.92                   # deliberative refinement score
extracted_facts: 12                # count of observations from this source
status: processed | pending | failed | needs_review
tags: [python, release-notes, 3.12]
entities: [CPython, PEP-701, PEP-698]
concepts: [f-string-debugging, exception-groups]
relationships:
  - type: updates
    target: "concepts/python-debugging.md"
    confidence: 0.95
  - type: supersedes
    target: "raw/2023-10-01-python-311.md"
    confidence: 0.90
---
```

### Wiki Page Frontmatter

```yaml
---
title: "F-String Debugging"
created: 2024-10-02
updated: 2024-10-02
tags: [python, debugging, syntax]
sources:
  - "raw/2024-10-02-python-312.md"    # provenance
  - "raw/2023-11-15-pep-701.md"
status: stable | draft | stale | needs_review
confidence: 0.95                     # aggregated from sources
version: 3                            # increment on meaningful edits
page_type: concept | entity | query
wikilinks:
  - "concepts/string-interpolation.md"
  - "concepts/debugging-techniques.md"
stale_after: 2025-04-02               # auto-flag if 6 months without update
---
```

### Cross-Reference Integrity

The metadata enables three critical cross-reference operations:

1. **Provenance queries**: "Which raw sources support this claim?"
2. **Impact analysis**: "If I update source X, which wiki pages change?"
3. **Staleness detection**: "Which pages haven't been updated in 6 months?"

## Intake Log

The intake log replaces the current ad-hoc processing. It's a JSONL file at
`wiki/.meta/intake_log.jsonl` — append-only, one JSON object per line.

### Log Entry Schema

```jsonl
{"type": "source_added",    "timestamp": "...", "path": "raw/foo.md", "size": 1234, "hash": "..."}
{"type": "source_processed","timestamp": "...", "path": "raw/foo.md", "status": "ok", "pages_created": 3, "confidence": 0.88, "duration_s": 12.5}
{"type": "page_created",    "timestamp": "...", "path": "pages/concepts/foo.md", "source": "raw/foo.md", "confidence": 0.88}
{"type": "page_updated",    "timestamp": "...", "path": "pages/concepts/bar.md", "source": "raw/foo.md", "change": "added f-string debugging note"}
{"type": "skill_created",   "timestamp": "...", "path": "auto-code-review/SKILL.md", "pattern": "code-review", "count": 4}
{"type": "contradiction",   "timestamp": "...", "paths": ["pages/concepts/x.md", "pages/concepts/y.md"], "claim": "..."}
{"type": "lint_issue",      "timestamp": "...", "issue": "broken_link", "path": "pages/concepts/foo.md", "target": "[[missing-page]]"}
{"type": "cycle_summary",   "timestamp": "...", "duration_s": 300, "budget_s": 900, "intake_pct": 0.4, "refinement_pct": 0.6, "sources_processed": 5, "pages_updated": 12, "skills_created": 1, "issues_found": 3}
```

### Status Tracking

The intake log feeds a status summary:

```
STATUS:  12 sources in raw/       → 8 processed, 3 pending, 1 failed
         47 pages in wiki/        → 42 stable, 3 draft, 2 stale
         5 skills auto-created    → code-review, debugging, testing, deployment, api-dev
         6 lint issues            → 3 broken links, 2 orphan pages, 1 contradiction
```

This is computed by scanning raw/ for files and checking the intake log for
their processing status.

## Integration with Ante

Since Ante 0.preview.16 has no hook system, the dream agent needs to be fully
self-contained. Here's how it connects:

1. **systemd timer** (preferred): Runs scheduler.py --cycle every 30 min idle
2. **cron fallback**: Same script, runs every 30 min, checks idle condition internally
3. **Manual**: `python3 dream/scheduler.py --cycle` anytime
4. **Daemon**: `python3 dream/scheduler.py --daemon` for continuous operation

The scheduler:
1. Checks if pi/ante process is running → skip if active
2. Checks time since last cycle → compute budget from elapsed × percentage
3. Runs dream agent with that budget
4. Updates intake log, state file, cron.log

## Implementation Plan

### Phase 1: Core Infrastructure (Do this first)

| Task | File | Effort |
|------|------|--------|
| Rewrite scheduler.py with systemd timer support | `dream/scheduler.py` | 2h |
| Add deliberation pipeline (not just keyword matching) | `dream/dream_agent.py` | 3h |
| Add YAML frontmatter schema + validation | `dream/dream_agent.py` | 1h |
| Build intake log system | `dream/dream_agent.py` | 1h |

### Phase 2: Time Budget + Dynamic Ratio

| Task | File | Effort |
|------|------|--------|
| Implement percentage-based budget calculation | `dream/dream_agent.py` | 1h |
| Build wiki refinement state metric | `dream/dream_agent.py` | 1h |
| Implement dynamic intake/refinement ratio | `dream/dream_agent.py` | 0.5h |
| Add model tokens/sec allocation | `dream/dream_agent.py` | 1h |

### Phase 3: Deliberative Refinement

| Task | File | Effort |
|------|------|--------|
| Build two-stage extract-refine pipeline | `dream/dream_agent.py` | 3h |
| Add confidence scoring with decision matrix | `dream/dream_agent.py` | 1h |
| Wire council call for edge cases | `dream/dream_agent.py` | 1h |
| Add contradiction detection + dual-position storage | `dream/dream_agent.py` | 1h |

### Phase 4: Polish

| Task | File | Effort |
|------|------|--------|
| systemd .timer + .service unit files | `dream/karpathy-dream.*` | 0.5h |
| Self-test suite | `tests/` | 2h |
| Staleness detection + auto-refresh scheduling | `dream/dream_agent.py` | 1h |
| Performance benchmark (measure actual t/s for models) | `dream/benchmark.py` | 1h |

## Comparison to Existing Systems

| Feature | Letta Sleep-Time | Hermes GEPA | Hindsight | This Design |
|---------|-----------------|-------------|-----------|-------------|
| Dual-agent architecture | ✅ | ❌ | ❌ | ✅ |
| Percentage-based budget | ❌ (fixed step-count) | ❌ | ❌ | ✅ |
| Dynamic intake/refinement | ❌ | ❌ | ✅ (observation consolidation) | ✅ |
| Confidence scoring | ❌ | ❌ | ✅ (evidence tracking) | ✅ (refinement) |
| Council deliberation | ❌ | ❌ | ❌ | ✅ |
| Skill auto-creation | ❌ | ✅ (GEPA reads traces) | ❌ | ✅ (pattern detection) |
| Multi-strategy retrieval | ❌ | ❌ | ✅ (TEMPR) | ❌ (v1 scope) |
| OS idle detection | ❌ (in-process triggers) | ❌ | ❌ | ✅ (systemd/cron) |
| Intake log | ❌ | ❌ | ❌ | ✅ |

## Key Design Decisions

### DD1: Systemd timer over in-process hooks
- **Context**: Ante has no hook system; Pi had step-counter that was never wired
- **Options**: (a) systemd idle timer, (b) cron, (c) daemon process, (d) Ante hooks (not built yet)
- **Decision**: systemd --idle timer with cron fallback
- **Rationale**: OS-level idle detection is the ONLY reliable way to know the user
  isn't actively using the agent. In-process triggers would compete for context
  budget and can't detect "user walked away."

### DD2: Percentage budget over fixed iterations
- **Context**: Letta uses fixed N-steps (default 5) between sleep-time triggers
- **Options**: (a) fixed N steps, (b) fixed interval, (c) percentage-of-idle-time
- **Decision**: Percentage-of-idle-time with absolute max cap
- **Rationale**: Self-balancing across usage patterns. Heavy use → small budget.
  Vacation → max budget. No configuration needed per usage pattern.
- **Letta context**: Their paper shows sleep-time compute has diminishing returns
  (~5 parallel generations works better than 10 for some tasks). Our percentage
  approach naturally limits over-allocation.

### DD3: Two-stage pipeline over single-pass
- **Context**: Current dream agent does everything in one pass (keyword matching)
- **Options**: (a) single-pass LLM, (b) extract-then-refine with two models
- **Decision**: Extract (fast, cheap) → Refine (thorough, council for edge cases)
- **Rationale**: The extract stage is high-recall, low-precision. The refine stage
  filters and scores. This mirrors the classic RAG pattern (retrieve → rerank)
  and is empirically validated by Hindsight's observation consolidation pipeline.

### DD4: Deliberative refinement (internal) over external judge
- **Context**: Previous decision was to use `convene_council` for all judgment
- **Options**: (a) external council for everything, (b) internal refinement with
  council only for edge cases
- **Decision**: Internal refinement for standard cases, council for edge cases
  (confidence < 0.6 or contradictions)
- **Rationale**: Council calls cost 2× tokens per decision. For routine ingestion,
  a single-model refinement pass is sufficient. The council is reserved for the
  hard cases where disagreement signals genuine uncertainty.

## Open Questions

1. **How often should the refinement state be recalculated?** Every dream cycle
   is probably fine (it's cheap — just counts and timestamps), but the staleness
   check actually needs to read file contents.

2. **Should the budget cap scale with idle time or be absolute?** Absolute cap
   at 2 hours prevents one long weekend from consuming 10GB of API tokens.
   But a per-model cap might make more sense (DeepSeek is cheap, Claude is not).

3. **What's the right tokens/second baseline for our DeepSeek V4 Flash?** Need to
   run `dream/benchmark.py` once with a realistic workload. The 120 tok/s in the
   table is an educated guess.

4. **Contradiction resolution policy**: When two sources contradict and both have
   confidence > 0.7, should we (a) store both positions neutrally, (b) flag for
   user, (c) use recency as tiebreaker, or (d) decide via council?

5. **Should the dream agent use the same model as the primary agent, or a
   different one?** Letta recommends a stronger model for sleep-time since latency
   doesn't matter. But stronger models cost more. DeepSeek V4 Flash is our only
   free model — do we use it for both roles?

## Files That Need Changes

| File | Current | Target |
|------|---------|--------|
| `dream/dream_agent.py` | Keyword matching, no budget, no confidence | Two-stage pipeline, % budget, refinement scoring |
| `dream/scheduler.py` | Step-counter, daemon mode | systemd timer + cron + idle-check |
| `wiki/AGENTS_WIKI.md` | Old schema spec | Updated with new frontmatter + intake log |
| `skill/SKILL.md` | Old architecture paths | Updated with new paths + redesign refs |

## Migration Path

1. Current system is dead (nothing runs). No harm in replacing entirely.
2. Install systemd timer + update dream agent in one PR.
3. Old `raw/` files (none exist) need no migration.
4. Old `wiki/` pages (index.md, log.md only) need frontmatter added — run
   a one-time migration script that reads each page, adds frontmatter, writes back.
5. Ready for Phase 2 immediately after Phase 1 is deployed.

## References

- **Letta Sleep-Time Compute Paper**: https://arxiv.org/abs/2504.13171
- **Letta Sleep-Time Agents**: https://docs.letta.com/guides/agents/architectures/sleeptime/
- **Hermes GEPA Self-Evolution**: https://github.com/NousResearch/hermes-agent-self-evolution
- **Hindsight Memory System**: https://hindsight.vectorize.io/
- **pi-agent-suite (convene_council)**: https://npmjs.com/package/pi-agent-suite
