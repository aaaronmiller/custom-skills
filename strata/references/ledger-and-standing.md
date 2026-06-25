---
date: 2026-05-18 10:00:00 PDT
ver: 1.0.0
author: ice-ninja
model: claude-opus-4-7
tags: [strata, ledger, continuity, memory, standing, anti-dreamstate]
---

# Continuity: Ledger and Standing (`ledger/`)

Author: the system, append-only. Layer: Continuity. This is the artifact nobody else ships as load-bearing structure, and it is the reason a STRATA project comes back from dormancy in ninety seconds instead of two days. Kiro's living specs, Augment's worktrees, and spec-kit's resumable state are all partial versions of this idea bolted to the side of a spec pipeline. Here it is the spine.

## Two files

`ledger/ledger.md` is an append-only record. Never edited, never reordered, never pruned. Every entry is one decision and, when known, its outcome. The ledger is how drift becomes loud instead of silent: nothing changes without an entry, so a diverged project shows its divergence in the log rather than hiding it in the code.

`ledger/standing.md` is a single overwritten file that answers one question in plain language: where is this system standing right now, and how did it get here. It is the first thing a revived session reads. It is not a status badge; it is sentences a human or an agent can act on without archaeology.

## Ledger entry format

```markdown
## [SEQ] [phase.step] [decision | outcome | pivot | refinement]
- What: [the decision or observation, one or two sentences]
- Why: [the intent input, spec clause, or council finding that drove it]
- Effect: [what changed in which artifact; on a pivot, the context.md delta]
- Outcome: [observed result if known, or "pending"]
```

Sequence numbers are monotonic and never reused. Phase.step uses STRATA phase notation, never dates.

## Standing format

```markdown
---
date: {{DATE}} {{TIME}} {{TZ}}
ver: {{VERSION}}
author: {{AUTHOR}} (system-owned)
model: {{MODEL}}
tags: [{{TAGS}}]
---

# Standing

## Where this is
[Plain sentences. What the project is, what phase it is in, what was last completed.]

## Last decisions that matter
[The three to five ledger entries a resuming worker must know, summarized, with SEQ references.]

## Not yet decided
[Open questions and deferred decisions, each pointing at the intent or spec section that will resolve them.]

## Next
[The immediate next action and which play or phase carries it.]

## Substrate note
[Current declared level and any pre-locked decision that a resuming worker should know is pre-locked, not live.]
```

## The revive protocol

A dormant project is resumed by reading `standing.md` and the tail of `ledger.md` before touching code, ever. `scripts/strata-revive.sh` prints exactly this reconstruction. Reading diffs to reconstruct intent is the failure STRATA exists to abolish; if a worker is reading diffs to figure out why, the ledger failed and that failure is itself a ledger entry.

## The backward feed

The outcomes recorded here are the empirical memory that `context.md` derives from on the next project. A decision whose recorded outcome was bad is a decision the next Context Crafting pass weights against. This is how architecture selection stops being intuition and becomes repeatable engineering across projects. The accumulated ledger across projects is the knowledge base the paradigm calls the differentiator. It is not bought. It is accrued.

## Rules

Append-only, monotonic, never pruned. Every decision, pivot, and refinement emits an entry, every time, not at milestones. `standing.md` is overwritten on every entry so it is never stale. The revive protocol reads standing and the ledger tail before code. A project with no ledger or no `standing.md` fails validation; continuity is not optional.
