---
name: spec-audit-skill-v2
description: |
  **DEPRECATED — Use spec-audit-skill-v3 instead.** (problems + our solutions), generate self-contained questions that describe ONLY the problem domain (no implementation details revealed), submit questions ALONE to an S-tier model, compare the model's first-principles answers against the spec — the divergence IS the audit signal.

  Use when: user says "spec audit", "backtranslation audit", "compare our design against first principles", "blind spec review", "gauge our design against first principles", "test if our implementation is optimal", "external perspective on our design", "ideal spec from questions only", "path 2 spec audit", "backtranslate our design". Also triggers on "divergence analysis", "first-principles audit", "solution vs intuition comparison".

  v2 improvement over v1: Questions NEVER reveal implementation details. S-tier model answers from first principles only. Divergence between answers and spec IS the audit finding.
---

# Spec Audit Skill v2 — Backtranslation-Driven Audit

> Don't ask the oracle what you should change. Ask it what the ideal looks like. Compare.

This skill encodes the corrected backtranslation methodology. The core insight: **questions that reveal your implementation contaminate the answer.** The S-tier model will just agree with your choices. The real signal comes from asking the model what it thinks the ideal solution is — describing only the problem — and then comparing that against what you actually built.

## The Flow

```
[Phase 1: Document] → spec-as-designed.md (problem + our solution, paired)
                            ↓
[Phase 2: Backtranslate] → self-contained questions (problem domain ONLY)
                            ↓
       User submits questions → S-tier model (NO spec given to model)
                            ↓
       User returns model answers → external-answers.md
                            ↓
[Phase 3: Compare] → divergence report (answers vs spec-as-designed.md)
                            ↓
[Phase 4: Council] → deliberative refinement on divergences
                            ↓
              ideal-spec.md + task-list.md
```

## Core Principle: Questions Must Never Reveal the Answer

A backtranslation question is **contaminated** if the S-tier model can deduce what you built from the question itself.

| ❌ Contaminated (v1 style) | ✅ Clean (v2 style) |
|---|---|
| "Our confidence scoring uses a 35/25/25/15 weight split for self-consistency/freshness/cross-refs/evidence. Should these weights change?" | "What factors should determine whether an auto-compiled knowledge entry is trustworthy enough to include without human review? How should those factors be weighted relative to each other?" |
| "Should our auto-skill creation threshold of 3 occurrences be adaptive?" | "At what point should a system that observes repeated work patterns automatically capture those patterns as reusable procedures? What factors should influence that threshold?" |
| "Is our three-tier architecture (ClawMem → Wiki → MemVid) optimal or should we collapse to two tiers?" | "For a system that needs both sub-millisecond session memory retrieval and long-term compressed archival, what tier architecture is appropriate? Describe the optimal storage hierarchy." |

The test: if you can read the question and infer something about what was built, it's contaminated. Rework it until the question describes the problem space, not the solution space.

---

## Phase 1: Write `spec-as-designed.md`

This is **not** a feature inventory. It's a design document that pairs each problem with the solution you chose. Structured as:

```markdown
# Project Name — Spec as Designed v1.0

## Overview
What problem does this project solve? Who is it for?

## Design Decisions

### D-001: Short Design Name
- **Problem:** The concrete problem this decision addresses
- **Our Solution:** What we built to address it
- **Why This Solution:** The rationale, tradeoffs accepted, alternatives considered
- **Constraints:** What bounded the decision (hardware, time, dependencies, platform)
- **Quality Signal:** How well does the solution fit the problem? (1-10)

### D-002: ...
```

Each design decision is a (problem, solution) pair. This structure is essential because:

1. The **problem** feeds the backtranslation question (the question describes the problem, not the solution)
2. The **solution** is what we compare the S-tier model's answer against
3. The **constraints** are critical — if the model proposes something our constraints don't allow, that's not a divergence worth acting on

Include every meaningful design decision from the project. If you skip a decision, the S-tier model's answer for that problem won't be comparable.

---

## Phase 2: Backtranslate → Self-Contained Questions

For each design decision in `spec-as-designed.md`:

1. Read the **Problem** field
2. Write a question that asks about the ideal solution to that problem — **without** revealing your own solution
3. The question must be answerable from first principles — the S-tier model needs no knowledge of your project

### Question writing rules

- **Never reference implementation specifics.** No thresholds, weights, exact architectures, file paths, or technology names unless they're intrinsic to understanding the problem domain.
- **Describe the problem domain, not your solution.** Instead of "our three-tier architecture..." say "a system that needs both sub-millisecond retrieval and long-term archival..."
- **Ask for reasoning, not just answers.** "What would you do and why?" produces more useful signal than "Which is better, X or Y?"
- **One question per design decision** minimum. Some decisions may need multiple questions to cover different aspects.
- **Add cross-cutting questions** for architectural gestalt — things that emerge from multiple decisions interacting.
- **Target 15–30 questions.** Enough to cover every significant design decision, not so many the model rushes.

### Output format

Two files:

`questions-v2.json` — structured:
```json
{
  "project": "Project Name",
  "spec_version": "2.0",
  "date": "YYYY-MM-DD",
  "methodology": "backtranslation-v2 — questions reveal NO implementation details",
  "instructions": "Answer each question from first principles. Do not reference any project-specific implementation. Your answers will be compared against an actual implementation to find divergences.",
  "total_questions": 20,
  "categories": ["architecture", "confidence-scoring", "idle-compute", "multi-agent", ...],
  "questions": [
    {
      "id": "Q-001",
      "category": "architecture",
      "maps_to": "D-001",
      "problem_context": "A system that needs...",
      "question": "What would you design and why?"
    }
  ]
}
```

`questions-v2.md` — human-readable for pasting into the S-tier model's interface:
```markdown
# Spec Audit — <Project Name> — Questions

Answer each question from first principles. Do not reference any project-specific implementation. Your answers will be compared against an actual implementation to find divergences.

---

## Architecture

**Q-001:** ...
```

---

## Phase 3: Compare → Divergence Report

When the user returns `external-answers.md` (the S-tier model's answers):

1. **Map each answer** to its corresponding design decision in `spec-as-designed.md`
2. **Classify the divergence**:

| Classification | Meaning | Action |
|---|---|---|
| **CONFIRMED** | Model's answer matches our solution | No action — we're on solid ground |
| **DIVERGENT — BETTER** | Model proposes a clearly superior approach | Consider implementing; add to task list |
| **DIVERGENT — EQUIVALENT** | Different approach, similar outcomes | Document but no priority change |
| **DIVERGENT — UNFEASIBLE** | Model's suggestion violates known constraints | Document the constraint gap; no action |
| **DIVERGENT — AMBIGUOUS** | Unclear which is better | Flag for council deliberation |

3. **Produce `divergence-report.md`** with one row per answer:

```markdown
| Q-ID | Decision | Our Solution | Model's Answer | Classification | Rationale |
|------|----------|-------------|----------------|---------------|-----------|
```

---

## Phase 4: Council Deliberation

For each divergence classified as **AMBIGUOUS** or where the model's answer deserves serious scrutiny:

1. Use **Parallel Groups** (Internal/As-Built vs External/Ideal perspective)
2. Profile based on number of contested items
3. The council's output:
   - For each AMBIGUOUS item: recommendation (keep, change, or investigate further)
   - Updated `ideal-spec.md` incorporating accepted changes
   - `task-list.md` with implementation tasks for changes

---

## Pitfalls

- **The cardinal sin is revealing your implementation in questions.** Re-read each question and ask: "Could someone answer this without knowing what I built?" If no, rewrite.
- **Don't skip constraints in spec-as-designed.md.** The model's answer might be technically superior but infeasible. The constraints field is what lets you classify divergences correctly.
- **One decision per question.** If a design decision involves multiple independent choices, split them. A question that asks "what should X and Y look like?" can't be cleanly mapped.
- **The problem description in the question is the spec's problem field, rephrased.** Don't add extra context that wasn't in the spec — that would bias the answer.
- **If the model asks clarifying questions** (unlikely with S-tier models for well-written questions), note them. It may indicate your problem description is incomplete.
