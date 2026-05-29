---
date: 2026-05-19
ver: 2.0.0
tags: [dream-agent, sleep-time, deliberative-refinement, skill-creation]
---

# Dream Agent v2 — Sleep-Time Compute Specification

## Architecture

The dream agent is a Python sidecar that runs on systemd idle timer.
It talks to ClawMem via REST API and writes compiled wiki pages to disk.
It does NOT modify ClawMem's SQLite directly — all read/write goes through
ClawMem's HTTP API.

## Trigger

```
systemd --user --idle timer (30min check)
    │
    ▼
idle-check.sh → Is pi/ante process running?
    │                 │
    │ (active)        │ (idle for 5+ min)
    ▼                 ▼
  Skip              Compute budget:
                    budget = idle_seconds × BUDGET_PERCENTAGE (default 0.25)
                    cap at MAX_BUDGET (default 7200s = 2hr)
                    │
                    ▼
                  Run dream cycle with budget
```

## Dream Cycle Phases

### Phase 0: Budget Allocation

```python
refinement_state = calc_refinement_state(wiki)

# At 0.0 (raw wiki):  80% intake, 20% refinement
# At 0.5 (mid):       50/50
# At 0.94 (mature):   33% intake, 67% refinement
intake_ratio = 0.80 - (0.50 × refinement_state)
intake_budget = total_budget × intake_ratio
refine_budget = total_budget × (1 - intake_ratio)
```

### Phase 1: Extract (uses intake_budget)

Read ClawMem vault for new/updated documents since last cycle.
For each new document:

1. Fetch full content from ClawMem REST API `GET /documents/:docid`
2. Parse YAML frontmatter (already parsed by ClawMem, but re-read for wiki)
3. Categorize: decision, preference, problem, milestone, note, etc.
4. Extract key claims with source citations
5. Store in intake queue

Uses a fast/cheap model (DeepSeek V4 Flash). No cross-referencing yet.

### Phase 2: Refine (uses refine_budget)

For each extracted claim:

1. **Self-consistency check**: Does the claim contradict itself?
2. **Cross-reference check**: Does it match/contradict/extend existing wiki pages?
3. **Source freshness check**: How recent is the source?
4. **Confidence score**: Weighted combination of the above
   - confidence > 0.8: ADD to wiki
   - confidence 0.5-0.8: FLAG for user review
   - confidence < 0.5: REJECT
5. **Council escalation**: If confidence is 0.5-0.6 AND the claim contradicts
   an existing high-confidence claim → convene adversarial council

### Phase 3: Compile

For approved claims:

1. Find best existing wiki page or create new one
2. Update page with new information
3. Add/update `[[wikilinks]]` to related pages
4. Add provenance to YAML frontmatter (`sources: [clawmem://docid/...]`)
5. If page already had contradictory information: note both positions
   with dates and confidence scores

### Phase 4: Pattern Detect

Scan recent ClawMem observations for repeated task patterns.
If 3+ similar task completions detected:
1. Distill procedure from observations
2. Create SKILL.md in skills directory
3. Write reference into ClawMem vault for future retrieval

### Phase 5: Re-index

After all wiki page writes:
1. Trigger ClawMem reindex to pick up new/changed wiki pages
2. ClawMem auto-embeds new fragments on next embed timer cycle

## ClawMem REST API Integration

| Operation | Endpoint | Frequency |
|-----------|----------|-----------|
| List new docs | `GET /stats` → compare doc count | Every cycle |
| Get doc content | `GET /documents/:docid` | Per new doc |
| Search for related pages | `POST /search` | Per claim |
| Get graph edges | `GET /graph/similar/:docid` | Per claim |
| Reindex after wiki writes | `POST /reindex` | End of cycle |
| Get session history | `GET /sessions` | Pattern detection |
| Get lifecycle status | `GET /lifecycle/status` | Health check |

## Deliberative Refinement

### Confidence Scoring Formula

```python
confidence = (
    0.35 × self_consistency +
    0.25 × source_freshness +
    0.25 × cross_ref_agreement +
    0.15 × evidence_count_bonus
)
```

Where:
- `self_consistency`: Does the LLM agree with its own extraction? (0-1)
- `source_freshness`: `max(0, 1 - age_days / 365)` (0-1)
- `cross_ref_agreement`: Fraction of related wiki pages that don't contradict (0-1)
- `evidence_count_bonus`: `min(1, count / 5)` (0-1)

### Council Escalation

When confidence ∈ [0.5, 0.6] AND the claim contradicts existing wiki content:

Two-model adversarial deliberation (DeepSeek V4 Flash + secondary model):
1. Both models receive: claim, source text, existing wiki content
2. Judge A argues for accepting the claim
3. Judge B argues for rejecting it
4. Consensus output: accept, reject, or flag-for-user

## Schedule Integration with MemVid

The monthly MemVid encoding creates natural checkpoints:

```
Week 1-3: Dream agent refines actively
          (high budget, lots of idle time)
Week 4:   Freeze snapshot → run MemVid encoding
          Dream agent still runs but targets next cycle
Day 1-30: Refined memories stay in ClawMem + wiki
Day 31:   Full re-encode includes all refinements
```

This means cold storage is always 0-30 days behind live memory.
If this lag is acceptable (and per the design, it is), the integration is clean.
