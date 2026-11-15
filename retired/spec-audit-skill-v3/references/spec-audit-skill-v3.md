---
name: spec-audit-skill-v3
version: 3.0
description: |
  True backtranslation-driven spec audit, aligned with the LLM SFT training data generation technique.
  
  The process: write spec-as-designed.md (problem→solution pairs). Backtranslate each clause into
  a question whose CORRECT ANSWER IS that clause — the S-tier model is answering cold, with no spec.
  Its answers, read in sequence, should reconstruct the spec. Divergence between the model's
  reconstruction and your actual spec IS the audit signal. Council deliberates on divergences.
  ideal-spec.md + task-list.md are the final output.

  v3 vs v2: v2 still framed questions as "probe what an ideal looks like from first principles."
  v3 corrects this: questions are LITERAL BACKTRANSLATIONS of spec clauses. The question's
  correct answer IS the spec clause. The S-tier model's job is reconstruction, not ideation.
  Divergence = the model reconstructed something different = audit finding.
  
  Also adds: constraint tagging, confidence scoring, coverage check, bounded iteration rule,
  and dual-path support. Resources for specific sub-tasks are listed below and loaded only
  when needed (progressive disclosure).

  Use when: "spec audit", "backtranslation audit", "blind spec review", "ideal spec from questions",
  "compare design against first principles", "path 2 spec audit", "divergence analysis",
  "test if our implementation is optimal", "external perspective on our design".
---

# Spec Audit Skill v3 — True Backtranslation Audit

> The question is the lock. The spec clause is the key. The model must cut a key that fits, without seeing yours.

---

## Critical Distinction: v2 vs v3

**v2 framing (wrong):** "Write questions that ask the S-tier model what the ideal solution looks like from first principles."

**v3 framing (correct):** "Backtranslate each spec clause into a question whose CORRECT ANSWER IS that clause. The S-tier model's answers, in sequence, should reconstruct the spec. They never will perfectly — and that gap IS the audit."

This is the same technique used to generate SFT training question/answer pairs for LLM training:
- You have target text: `"The system uses a three-tier memory architecture: A (hot), B (warm), C (cold)."`
- You generate a question whose answer IS that text: `"For a system needing sub-millisecond session retrieval and long-term archival, describe the appropriate storage tier architecture."`
- A model that independently arrives at a three-tier A/B/C design confirms your approach.
- A model that proposes two tiers — or different tier characteristics — is a divergence worth investigating.

The question carries **domain context** (enough to frame the problem) but **never reveals the solution**.

---

## The Dual-Path Model

This skill supports two audit paths. Both can run concurrently and their outputs combined.

| Path | What gets submitted | Model context | Signal type |
|---|---|---|---|
| **Path 1** | spec-as-built.md + original questions TOGETHER | Full context — model sees your spec | "Does a strong model agree with our approach when it has full context?" |
| **Path 2** | Questions ONLY — no spec | Cold — model answers from first principles | "Does a strong model independently reconstruct our design, or derive something better?" |

**Path 2 is the primary audit path.** Path 1 is a secondary validation check. Run both; use both outputs in the council phase.

---

## The Full Flow

```
PREP
└── [Phase 0: Dual Path Decision]
      ├── Path 1: gather existing spec + questions → submit both to S-tier model
      └── Path 2: continue to Phase 1 below

PHASE 1: DOCUMENT
└── Write spec-as-designed.md
      └── Format: problem → our solution (structured for backtranslation extraction)
            ↓

PHASE 2: BACKTRANSLATE
└── For each clause/decision in spec-as-designed.md:
      └── Write a question whose correct answer IS that clause
            └── Carry domain context; never reveal the solution
      └── Run coverage check — every clause maps to at least one question
      └── Tag constraint metadata onto each question
            ↓

PHASE 3: SUBMIT
└── User submits questions-v3.md to S-tier model (NO spec attached)
      └── Instruct model: answer each question from first principles,
          include confidence score 1-10 per answer
            ↓

PHASE 4: COMPARE
└── Map model answers → spec clauses
      └── Classify each: CONFIRMED / DIVERGENT-BETTER / DIVERGENT-EQUIVALENT /
                         DIVERGENT-INFEASIBLE / DIVERGENT-AMBIGUOUS
      └── High-confidence DIVERGENT = strongest audit signal
            ↓

PHASE 5: COUNCIL
└── Deliberative refinement on AMBIGUOUS and DIVERGENT-BETTER items
      └── See resource: references/council-formations.md for formation selection
            ↓

PHASE 6: OUTPUT
└── ideal-spec.md + task-list.md
```

---

## Phase 0: Dual Path Setup

Before starting Phase 1, determine if Path 1 files already exist.

- If `spec-as-built.md` and `questions.md` (or similar v1 files) exist → those become **Path 1**. Submit them together to the S-tier model now, in parallel with Path 2 work. No modifications.
- If no prior files exist → Path 1 is skipped; run Path 2 only.
- Document which paths are active at the top of your session notes.

---

## Phase 1: Write `spec-as-designed.md`

**This document is written knowing it will feed backtranslation.** Every clause must be expressed clearly enough that a question can be constructed from it, and the question's answer reconstructs the clause.

### Structure

```markdown
# [Project Name] — Spec as Designed v[N]
Generated: [DATE]
Purpose: Foundation document for backtranslation audit. Each decision is structured
         as (problem → our solution) so questions can be extracted without revealing answers.

## Overview
One paragraph: what problem does this project solve, who is it for, what is the key constraint set.

## Design Decisions

### D-001: [Short Decision Name]
- **Problem:** The concrete problem this decision addresses. Be precise — the question
  will be derived from this field. Vague problems produce vague questions.
- **Our Solution:** What we built. Be specific — this is what the model's answer
  will be compared against.
- **Rationale:** Why this solution over alternatives. What tradeoffs were accepted.
- **Constraints:** Hard limits that bounded this decision (hardware, platform, latency,
  budget, team, dependencies). CRITICAL — used to classify INFEASIBLE divergences.
- **Coverage Tags:** [architecture | confidence | memory | scheduling | agents | ...]
  (used for coverage check in Phase 2)
- **Self-Quality Signal:** 1-10 — how confident are you this solution is optimal?
  Low scores = priority audit targets.

### D-002: ...
```

### Writing Rules

- **Write the Problem field as if explaining the challenge to a peer who has no knowledge of your project.** The question will be derived from this — it must stand alone.
- **Write the Solution field with enough specificity to be verifiable.** "We used a three-tier memory architecture" is better than "we have memory layers."
- **Every significant design decision gets its own entry.** If you skip one, that area has no audit coverage.
- **The Constraints field is not optional.** It's what separates "the model found a better approach" from "the model doesn't know about our M-series Mac limitation."

---

## Phase 2: Backtranslate → Questions

For each D-XXX entry in `spec-as-designed.md`:

1. Read the **Problem** field.
2. Write a question that asks for the ideal solution to that problem — the question's **correct answer** is your solution clause.
3. The question must be answerable without any knowledge of your project.
4. Tag it with the D-ID it maps to, the constraint tags, and any hard constraints that bound the answer.

### The Backtranslation Test

After writing each question, ask: *"Could I read this question and reconstruct what was built?"*

- If yes → contaminated. Rework.
- If no → clean.

Secondary test: *"If a strong model answers this correctly from first principles, would its answer be substantially the same as our spec clause?"*

- If yes → well-formed question.
- If no → the question is not capturing the right problem, or the spec clause needs refinement.

### Contamination Examples

| ❌ Contaminated | ✅ Clean |
|---|---|
| "Our confidence scoring uses a 35/25/25/15 weight split. Should these weights change?" | "What factors should determine whether an auto-compiled knowledge entry is trustworthy enough to include without human review? How should those factors be weighted relative to each other?" |
| "We use 3 occurrences as the threshold for auto-skill creation. Should this be adaptive?" | "At what point should a system observing repeated work patterns automatically capture those patterns as reusable procedures? What factors should influence that threshold, and should it be static or adaptive?" |
| "Is our three-tier ClawMem → Wiki → MemVid architecture optimal?" | "For a system requiring both sub-millisecond session memory retrieval and long-term compressed archival with minimal active compute, describe the ideal storage tier architecture and the criteria for promotion between tiers." |

### Context Clauses

Some questions need framing context to be answerable. This context describes the **problem space**, not the solution. Include it explicitly.

Example: A question about a sub-feature of the ante agent needs the framing "when extending an agentic coding assistant's core capabilities beyond its baseline feature set..." — this is domain context, not implementation reveal. The framing is **part of the question**.

### Constraint Tagging

Each question gets a `constraints` field listing the hard limits that apply. This prevents misclassification during the comparison phase.

```markdown
**Q-007**
Maps to: D-007
Constraint tags: [local-only, m-series-mac, no-cloud-dependency]
Question: For a system that needs to...
```

If the model's answer requires cloud infrastructure and the constraint is `local-only`, that divergence is classified as **INFEASIBLE** — not a real finding.

### Coverage Check

After generating all questions:

1. List all D-XXX IDs from `spec-as-designed.md`
2. Verify each D-XXX maps to at least one question
3. Any uncovered D-XXX = audit blind spot — either write a question for it or explicitly mark it as out-of-scope

Document the coverage map in the question file.

### Output Format

Two outputs:

**`questions-v3.md`** — submitted to the S-tier model:

```markdown
# Spec Audit — [Project Name] — Questions v3
Date: [DATE]
Methodology: backtranslation-v3

Instructions to answering model:
Answer each question from first principles. Do not reference any project-specific
implementation. For each answer, include a confidence score (1-10) reflecting how
confident you are that your answer represents the optimal approach. Your answers will
be compared against an actual implementation to identify divergences worth investigating.

---

## [Category]

**Q-001** [Maps to: D-001] [Constraints: none]
[Context if needed: ...]
[Question]

**Q-002** ...
```

**`questions-v3.json`** — structured record for Phase 4 mapping:

```json
{
  "project": "Project Name",
  "spec_version": "3.0",
  "date": "YYYY-MM-DD",
  "methodology": "backtranslation-v3",
  "questions": [
    {
      "id": "Q-001",
      "maps_to": "D-001",
      "category": "architecture",
      "constraints": ["local-only"],
      "context": "...",
      "question": "..."
    }
  ]
}
```

---

## Phase 3: Submit to S-tier Model

**Submit `questions-v3.md` ONLY.** Do not attach `spec-as-designed.md`.

Instructions block to prepend:

```
Answer each question from first principles. Do not reference any project-specific
implementation you may be aware of. Your goal is to describe what you believe the
optimal solution is for each problem as stated. 

For each answer, include:
- Your answer (as detailed as the question requires)
- Confidence: [1-10] — how confident are you this is the optimal approach?

Your answers will be compared against an actual implementation to identify
meaningful divergences.
```

Save the model's full response as `external-answers.md`.

---

## Phase 4: Compare → Divergence Report

Map each answer in `external-answers.md` to its corresponding D-XXX entry in `spec-as-designed.md`.

### Divergence Classifications

| Classification | Meaning | Confidence weight | Action |
|---|---|---|---|
| **CONFIRMED** | Model's answer matches our solution | Any | No action — confirmed optimal |
| **DIVERGENT — BETTER** | Model proposes a clearly superior approach | High confidence = strong signal | Priority candidate for implementation |
| **DIVERGENT — EQUIVALENT** | Different approach, similar outcomes | Any | Document, no priority change |
| **DIVERGENT — INFEASIBLE** | Model's answer violates a tagged constraint | Any | Document constraint gap only; no implementation action |
| **DIVERGENT — AMBIGUOUS** | Unclear which is better | Any | Flag for council deliberation |

**Confidence amplification rule:** A high-confidence (8-10) DIVERGENT answer from the S-tier model is a strong signal. A low-confidence (1-4) DIVERGENT is weaker and may reflect the question being ambiguous or the problem domain being genuinely uncertain.

### Divergence Report Format

```markdown
# Divergence Report — [Project Name]
Date: [DATE]
Path: [1 / 2 / both]

| Q-ID | D-ID | Our Solution (summary) | Model's Answer (summary) | Confidence | Classification | Notes |
|------|------|----------------------|--------------------------|------------|----------------|-------|
| Q-001 | D-001 | ... | ... | 9 | DIVERGENT-BETTER | Model suggests X which addresses Y gap |
```

Produce `divergence-report.md`.

---

## Phase 5: Council Deliberation

For **AMBIGUOUS** and **DIVERGENT-BETTER** items:

> See `references/council-formations.md` for available council formations and selection criteria.
> The council formation choice is context-dependent. Use the resource to determine which
> formation (or sequence of formations) is appropriate for the current divergence set.

The council output per item:
- Recommendation: keep our solution / adopt model's answer / merge both / investigate further
- Rationale: why
- Any constraints or unknowns that would change the recommendation

---

## Phase 6: Output Files

**`ideal-spec.md`** — the spec updated with accepted council recommendations. Format mirrors `spec-as-designed.md` but includes:
- Which decisions were CONFIRMED (unchanged)
- Which decisions were UPDATED (what changed and why)
- Which decisions are PENDING (investigation needed)

**`task-list.md`** — implementation tasks derived from UPDATED decisions:

```markdown
# Task List — [Project Name] — Post-Audit
Generated from: ideal-spec.md v[N]

## Priority 1 — DIVERGENT-BETTER (accepted)
- [ ] T-001: [task] — implements D-XXX update — estimated scope: [S/M/L]

## Priority 2 — DIVERGENT-AMBIGUOUS (resolved to change)
- [ ] T-002: ...

## Deferred
- [ ] T-003: [task flagged for future investigation] — reason: [...]
```

---

## Bounded Iteration Rule

If a question-answer pair is being revised iteratively (e.g., via a clarification round with the S-tier model), apply this rule:

- **Round 1:** Initial answer received.
- **Round 2:** If the answer was ambiguous or incomplete, send one clarification. Note: if clarification produces convergence → the question was ambiguous, not the model's understanding. Revise the question for future use.
- **Round 3 maximum:** If after two rounds the answers remain divergent and the divergence can't be classified, the question itself or the spec clause is structurally broken. Mark as `DEFERRED` and revise offline.

**Do not iterate indefinitely.** Three rounds max. If the process can't converge in three turns, the question needs architectural revision, not more back-and-forth.

---

## Pitfalls

- **Cardinal sin: revealing your implementation in questions.** Read each question after writing it and ask: "Can I infer what was built from this?" If yes, rewrite.
- **Skipping the Constraints field.** The model may propose something better that you can't implement. Without constraints tagged, you'll misclassify it as DIVERGENT-BETTER and waste engineering time.
- **Coverage gaps.** Every spec clause needs a question. Use the coverage check.
- **Conflating Path 1 and Path 2 signals.** Path 1 (model sees spec + questions) confirms coherence. Path 2 (model is cold) finds genuine architectural divergence. They measure different things. Don't average them — present separately.
- **Treating low-confidence divergences as strong signals.** Weight confidence appropriately. A model that says "I'm not sure, but maybe X" is a weak finding; a model that confidently proposes a different architecture is a strong one.
- **One design decision per question.** If a decision involves multiple independent choices, split into multiple questions. A bundled question can't be cleanly mapped.

---

## Resources

These sub-documents are loaded only when needed. They are NOT read automatically — reference them at the specific phase where they apply.

### `references/council-formations.md`
**When to load:** Phase 5 (Council Deliberation), when selecting a council formation for deliberative refinement.
**What it covers:** Available council formation types (parallel groups, adversarial, Socratic, etc.), selection criteria by use case, multi-formation sequences for complex divergence sets.
**Location:** `[skill-root]/references/council-formations.md`

### `references/question-quality-rubric.md`
**When to load:** Phase 2 (Backtranslation), if you're uncertain whether a question is contaminated or well-formed.
**What it covers:** Graded rubric for question quality (contamination test, specificity test, answerability test, reconstruction test), worked examples for each test, repair patterns for common contamination types.
**Location:** `[skill-root]/references/question-quality-rubric.md`

### `references/divergence-classification-guide.md`
**When to load:** Phase 4 (Compare), when a divergence is unclear and needs a structured classification decision.
**What it covers:** Decision tree for AMBIGUOUS vs BETTER vs EQUIVALENT, how to apply constraint tags to filter INFEASIBLE, confidence weighting rules, examples of each classification type.
**Location:** `[skill-root]/references/divergence-classification-guide.md`

### `references/spec-writing-patterns.md`
**When to load:** Phase 1 (Document), when the project being audited is complex or unfamiliar, or when the first draft of spec-as-designed.md needs quality review.
**What it covers:** Patterns for writing Problem fields that feed clean backtranslation, common spec-writing mistakes (too vague, too implementation-specific, missing constraints), worked examples from different project types (agentic systems, APIs, data pipelines, UI frameworks).
**Location:** `[skill-root]/references/spec-writing-patterns.md`

### `references/dual-path-merge-guide.md`
**When to load:** After both Path 1 and Path 2 results are returned, before Phase 5 council.
**What it covers:** How to merge Path 1 and Path 2 findings into a unified divergence picture, weighting Path 2 (cold reconstruction) heavier for architectural decisions vs Path 1 (full context) for implementation coherence checks, format for combined divergence report.
**Location:** `[skill-root]/references/dual-path-merge-guide.md`

---

## Quick Reference Checklist

```
PHASE 0
[ ] Determine if Path 1 files exist → submit them to S-tier model in parallel if so

PHASE 1: spec-as-designed.md
[ ] Every decision has: Problem / Our Solution / Rationale / Constraints / Coverage Tags
[ ] Problem fields are written for a reader with NO project knowledge
[ ] Constraints field is complete — no decision missing its constraint set

PHASE 2: questions
[ ] Every question passes the contamination test
[ ] Every D-XXX maps to at least one question (coverage check)
[ ] Constraint tags copied to question metadata
[ ] Questions ask for reasoning, not just answers
[ ] Context clauses describe problem domain only

PHASE 3: submit
[ ] questions-v3.md submitted WITHOUT spec-as-designed.md
[ ] Confidence scoring instructions included in the prompt to the model
[ ] Model output saved as external-answers.md

PHASE 4: compare
[ ] Every answer mapped to a D-ID
[ ] Confidence scores recorded
[ ] INFEASIBLE divergences filtered via constraint tags before classification
[ ] divergence-report.md produced

PHASE 5: council
[ ] council-formations.md consulted (references/council-formations.md)
[ ] Dual-path merge completed if both paths ran (references/dual-path-merge-guide.md)
[ ] Each AMBIGUOUS and DIVERGENT-BETTER item has a council recommendation

PHASE 6: output
[ ] ideal-spec.md produced (mirrors spec-as-designed.md structure)
[ ] task-list.md produced (prioritized by classification)
```
