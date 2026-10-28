---
date: 2026-05-18 10:00:00 PDT
ver: 1.0.0
author: ice-ninja
model: claude-opus-4-7
tags: [spec-prep, ledger, continuity, memory, standing, anti-dreamstate]
---

# Continuity: Ledger and Standing (`ledger/`)

Author: the system records material evidence and decisions. Layer: Continuity. The ledger and standing snapshot make history and current resumable state explicit; their usefulness depends on accuracy and read-back against live state, not a promised recovery time or exclusive ownership of the idea.

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

Sequence numbers are monotonic and never reused. Phase.step uses spec-prep phase notation, never dates.

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

Resume by reading `standing.md` and the relevant tail of `ledger.md` before changing code, then verify against live task/artifact state. `scripts/spec-prep-revive.sh` displays this reconstruction. If the records are missing or stale, consult history and sources, record the gap and reconcile the evidence; never invent an uninterrupted history.

## The backward feed

Recorded outcomes may inform later architecture when their evidence and context are relevant and access is authorized. Separate an observation from a proposed causal lesson and from accepted reusable policy. An empty ledger supplies no empirical precedent. Ledger accumulation alone neither implements a learning engine nor establishes that an earlier architecture generalizes.

## Rules

Append-only and monotonic. Record material decisions, outcomes, pivots, refinements and task-state changes. Refresh standing.md when resumable state changes, before final receipt hashing; do not rewrite it for every prompt/tool call. Keep nested ledger/ files by default; existing flat aliases are accepted only when they do not conflict. The revive protocol reads standing and the ledger tail before code. A project with no ledger or no `standing.md` fails validation; continuity is not optional.
