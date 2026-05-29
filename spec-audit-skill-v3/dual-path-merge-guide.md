# Dual-Path Merge Guide — Reference Guide

**Purpose:** How to merge Path 1 and Path 2 findings into a unified divergence
picture before Phase 5 council. Only load if both paths were run.

---

## Path Signal Comparison

| Dimension | Path 1 (Full Context) | Path 2 (Cold) |
|---|---|---|
| What it tests | Internal coherence of your design | Whether your design is the first-principles default |
| Model's knowledge | Sees your spec + your questions | Sees only the questions |
| Divergence meaning | The model, knowing your approach, still disagrees | The model, not knowing your approach, designs differently |
| Signal strength | Weaker for architectural audit | Stronger for architectural audit |
| Best for | Implementation coherence checks | Fundamental design validation |

**Key principle:** Path 2 carries heavier weight for architectural decisions.
Path 1 carries weight for implementation-level coherence. Do NOT average them.

---

## Merge Procedure

### Step 1: Separate the Divergence Lists

Produce two separate divergence reports:
- `divergence-report-path1.md` — from the Path 1 (full context) model
- `divergence-report-path2.md` — from the Path 2 (cold) model

### Step 2: Cross-Reference by D-ID

For each D-XXX that appears in either report:

| Path 1 Result | Path 2 Result | Combined Interpretation | Priority |
|---|---|---|---|
| CONFIRMED | CONFIRMED | Doubly confirmed — no action | None |
| CONFIRMED | DIVERGENT | Coherent but non-obvious — your design is defensible when understood but not the default | Medium — document constraints; consider whether making it more obvious is possible |
| DIVERGENT | CONFIRMED | Model agrees when it sees full context but disagrees cold — your design is good but poorly signaled | Low — consider documentation/clarity improvements |
| DIVERGENT | DIVERGENT | Model disagrees even with full context — fundamental concern | **High** — investigate whether the design has genuine issues |
| (not tested) | DIVERGENT | Only cold signal — no coherence check | Medium — treat as Path 2 standalone result |
| DIVERGENT | (not tested) | Only coherence signal — no first-principles check | Low — your design may just need better framing |

### Step 3: Produce Combined Divergence Report

```markdown
# Combined Divergence Report — [Project Name]

| D-ID | Path 1 Classification | Path 2 Classification | Combined Interpretation | Priority |
|------|----------------------|----------------------|------------------------|----------|
| D-001 | CONFIRMED | DIVERGENT-BETTER | Coherent but non-obvious | Medium |
| D-007 | DIVERGENT-EQUIVALENT | DIVERGENT-BETTER | Model disagrees even with context | High |
```

### Step 4: Feed to Council

The combined interpretation drives council formation selection:
- **High priority** items → Adversarial or Red/Blue formation
- **Medium priority** items → Socratic formation (surface constraints)
- **Low priority** items → Document only, no council needed

---

## When Paths Disagree

If Path 1 says CONFIRMED but Path 2 says DIVERGENT (most common case):

This means your design is **defensible but non-obvious**. This is NOT a problem —
it's information. Your design works well when understood, but it's not what a
skilled designer would default to. Two actions:

1. **Document** the constraints and reasoning that make your design correct despite
   not being the default. This is institutional knowledge.
2. **Consider** whether the design COULD be made more obvious without sacrificing
   its advantages. Sometimes a non-obvious design is necessary; sometimes it's
   an artifact of how you arrived at it.

If Path 1 says DIVERGENT but Path 2 says CONFIRMED (uncommon):

This means your design is **the default but not defensible**. The model arrives
at your approach from first principles but, upon seeing the full context,
identifies problems. This suggests your design has an implementation-level issue
that isn't visible from the problem statement alone. Investigate specifically.

---

*Expand with project-specific merge patterns as you encounter edge cases.*
