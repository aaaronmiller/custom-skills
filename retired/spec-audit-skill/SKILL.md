---
name: spec-audit-skill
version: 3.1
description: "Use when: spec auditing, backtranslation audit, blind spec review. Action: Audit implementation specs against first principles..."
tags:
- planning
- ai/llm
grade: A
source: custom
---

# Spec Audit Skill — True Backtranslation Audit

> The question is the lock. The spec clause is the key. The model must cut a key
> that fits, without seeing yours. Divergence tells you your key wasn't obvious.

---

## CHANGELOG: v3 → v3.1

| # | What changed | Why |
|---|---|---|
| 1 | Phase 2 step 2: replaced "asks for the ideal solution" with "whose correct answer reconstructs the solution described in the spec clause" | "Ideal" is v2 contamination — it implies the model should invent, not reconstruct |
| 2 | Bounded iteration rule: added explicit contamination guard — clarifications may only rephrase or narrow the question, never reveal implementation | Without this guard, iteration leaks the spec and contaminates all subsequent answers |
| 3 | Added `Expected Obviousness: 1-5` field to each question | Predicts whether the S-tier model will independently arrive at the spec clause; low = high-value audit target, high = validation target |
| 4 | Added optional Phase 1b: backtranslate from spec-as-built.md separately | Produces implementation-debt vs design-debt classification (aligns-with-designed-but-not-built = implementation debt; diverges-from-both = design debt) |
| 5 | Added `Etiology` column to divergence report | Distinguishes WHY divergence occurred (non-obvious-but-correct / suboptimal / ambiguous-question / constraint-violation) — drives different council actions |
| 6 | Demoted Path 1 to optional appendix; main flow is Path 2 only | Path 1 was a salvage operation, not a designed experiment. It's useful but shouldn't get equal structural weight |
| 7 | Added stub content to all 6 reference files | Skill is now self-contained; resources can be expanded later |

---

## Critical Distinction: v2 vs v3 vs v3.1

**v2 framing (wrong):** "Write questions that ask the S-tier model what the ideal solution looks like from first principles."

**v3 framing (better but imprecise):** "Backtranslate each spec clause into a question whose correct answer IS that clause. The S-tier model's job is reconstruction."

**v3.1 framing (correct and complete):** "Backtranslate each spec clause into a question whose correct answer reconstructs the solution described in that clause. The S-tier model answers cold — its answer should naturally reconstruct your spec clause if that clause is the obvious first-principles answer. Divergence means your solution was not the default from first principles. That's the audit signal. The question's job is to make the spec clause the natural answer, not the 'ideal' answer."

This is the same technique used to generate SFT training question/answer pairs for LLMs:
- You have target text: `"The system uses a three-tier memory architecture: A (hot), B (warm), C (cold)."`
- You generate a question whose answer IS that text: `"For a system needing sub-millisecond session retrieval and long-term archival, describe the appropriate storage tier architecture."`
- A model that independently arrives at a three-tier A/B/C design confirms your approach.
- A model that proposes two tiers — or different tier characteristics — produces a divergence. That divergence means your three-tier design wasn't the first-principles default.

The question carries **domain context** (enough to frame the problem) but **never reveals the solution**.

---

## The Flow (Primary: Path 2)

```
PREP
└── [Phase 0: Check for Path 1 files]
      └── If spec-as-built.md + questions.md exist → optionally submit both
          to S-tier model in parallel (see Appendix A). NOT the main process.
            ↓

PHASE 1: DOCUMENT
└── Write spec-as-designed.md
      └── Format: problem → our solution (clause-structured for backtranslation)
            ↓

PHASE 1b: DOCUMENT (optional, if spec-as-built.md also exists)
└── Generate parallel question set from spec-as-built.md
      └── Enables built-vs-designed debt classification in Phase 4
            ↓

PHASE 2: BACKTRANSLATE
└── For each clause/decision in spec-as-designed.md:
      └── Write a question whose correct answer reconstructs the spec clause
            └── Carry domain context; never reveal the solution
      └── Rate Expected Obviousness (1-5) per question
      └── Run coverage check — every clause maps to at least one question
      └── Tag constraint metadata onto each question
            ↓

PHASE 3: SUBMIT
└── User submits questions-v3.md to S-tier model (NO spec attached)
      └── Instruct model: answer each question from first principles,
          include confidence score 1-10 per answer
            ↓

PHASE 4: COMPARE
└── Map model answers → spec clauses (using answer key)
      └── Classify each: CONFIRMED / DIVERGENT-BETTER / DIVERGENT-EQUIVALENT /
                         DIVERGENT-INFEASIBLE / DIVERGENT-AMBIGUOUS
      └── Assign Etiology: NON-OBVIOUS-BUT-CORRECT / SUBOPTIMAL /
                           AMBIGUOUS-QUESTION / CONSTRAINT-VIOLATION
      └── If Phase 1b ran: classify debt type (implementation / design)
      └── High-confidence DIVERGENT with SUBOPTIMAL etiology = strongest signal
            ↓

PHASE 5: COUNCIL
└── Deliberative refinement on AMBIGUOUS and DIVERGENT-BETTER items
      └── See resource: references/council-formations.md
      └── Etiology drives council action (see Phase 4 etiology→action map)
            ↓

PHASE 6: OUTPUT
└── ideal-spec.md + task-list.md + debt-classification.md (if Phase 1b ran)
```

---

## Phase 0: Check for Existing Files

Before starting Phase 1, check whether prior audit files exist.

- If `spec-as-built.md` and `questions.md` (v1 files) exist → optionally submit them together to the S-tier model as a **parallel validation check**. This is NOT the main process. See Appendix A.
- If `spec-as-built.md` exists WITHOUT v1 questions → use it for Phase 1b (built-vs-designed comparison).
- If no prior files exist → proceed directly to Phase 1.

Document which paths are active at the top of your session notes.

---

## Phase 1: Write `spec-as-designed.md`

**This document is written knowing it will feed backtranslation.** Every clause must be expressed clearly enough that a question can be constructed from it, and the question's answer reconstructs the clause.

### Structure

```markdown
# [Project Name] — Spec as Designed v[N]
Generated: [DATE]
Purpose: Foundation document for backtranslation audit. Each decision is structured
         as (problem → our solution) so questions can be extracted without
         revealing answers.

## Overview
One paragraph: what problem does this project solve, who is it for, what is
the key constraint set.

## Design Decisions

### D-001: [Short Decision Name]
- **Problem:** The concrete problem this decision addresses. Be precise — the
  question will be derived from this field. Vague problems produce vague questions.
- **Our Solution:** What we built. Be specific — this is what the model's answer
  will be compared against. One clause per decision.
- **Rationale:** Why this solution over alternatives. What tradeoffs were accepted.
- **Constraints:** Hard limits that bounded this decision (hardware, platform,
  latency, budget, team, dependencies). CRITICAL — used to classify INFEASIBLE
  divergences.
- **Coverage Tags:** [architecture | confidence | memory | scheduling | agents | ...]
  (used for coverage check in Phase 2)
- **Self-Quality Signal:** 1-10 — how confident are you this solution is optimal?
  Low scores = priority audit targets.

### D-002: ...
```

### Writing Rules

- **Write the Problem field as if explaining the challenge to a peer who has NO knowledge of your project.** The question will be derived from this — it must stand alone.
- **Write the Solution field with enough specificity to be verifiable.** "We used a three-tier memory architecture with hot/warm/cold tiers using SQLite, markdown, and video-codec compression respectively" is better than "we have memory layers."
- **Every significant design decision gets its own entry.** If you skip one, that area has no audit coverage.
- **The Constraints field is not optional.** It's what separates "the model found a better approach" from "the model doesn't know about our M-series Mac limitation."
- **One clause per D-XXX entry.** If a decision contains multiple independent sub-decisions (e.g., "use hooks AND support MCP servers AND separate model configs"), split into separate D-XXX entries. Atomic clauses produce atomic questions, which produce granular divergence signals.

---

## Phase 1b: Optional Built-vs-Designed Comparison

If `spec-as-built.md` exists (documenting what was actually implemented, as opposed to what was designed), generate a **parallel question set** from it.

**Why:** `spec-as-built.md` may include accidental decisions, workarounds, or legacy constraints that weren't part of the intentional design. By backtranslating from both documents separately, you can classify divergences into two categories:

| Pattern | Meaning | Debt Type |
|---|---|---|
| Model aligns with `spec-as-designed` but diverges from `spec-as-built` | You designed well but built differently | **Implementation debt** |
| Model diverges from both | Your design itself isn't the first-principles default | **Design debt** |
| Model aligns with both | Confirmed across intent and reality | No debt |

**Process:** Run Phase 2 backtranslation on `spec-as-built.md` as well, producing `questions-built-v3.md`. Submit this question set to the S-tier model separately (or in a separate session to avoid cross-contamination). Save output as `external-answers-built.md`.

**In Phase 4**, compare both answer sets against both specs. The alignment pattern produces the debt classification.

---

## Phase 2: Backtranslate → Questions

For each D-XXX entry in `spec-as-designed.md`:

1. Read the **Problem** field.
2. Write a question **whose correct answer reconstructs the solution described in the spec clause**. The question should be structured so that the spec clause is the *natural answer*, not the *ideal answer*.
3. The question must be answerable without any knowledge of your project.
4. Rate the question's **Expected Obviousness** (1-5).
5. Tag it with the D-ID it maps to, the constraint tags, and any hard constraints that bound the answer.

### Expected Obviousness Rating

After writing each question, rate:

**"How likely is it that a competent system designer, answering from first principles, would produce our spec clause as the answer to this question?"**

| Rating | Meaning | Audit Value |
|---|---|---|
| 1 — Very unlikely | Our solution is non-obvious; few designers would arrive at it independently | **Highest-value audit target** — divergence is expected and informative |
| 2 — Unlikely | Our solution requires domain-specific insight | High-value target |
| 3 — Possible | Our solution is one of several plausible approaches | Medium-value — divergence reveals alternative schools of thought |
| 4 — Likely | Most competent designers would produce something similar | Validation target — if the model DOESN'T produce our answer, the question may be bad |
| 5 — Very likely | Our solution is the obvious default | Strict validation — divergence indicates a problem with the question, not the design |

**How this interacts with Self-Quality Signal:** They measure different things.
- `Self-Quality Signal` (on D-XXX) = "Is our solution good?" (rates the solution)
- `Expected Obviousness` (on Q-XXX) = "Will the model independently arrive at our solution?" (rates the question's diagnostic value)

A solution with high quality (9/10) but low obviousness (1/5) is a **non-obvious-but-correct** design — the most interesting audit result. A solution with low quality (3/10) and low obviousness (1/5) is a **suboptimal** design — the model will likely find something better.

### The Backtranslation Test

After writing each question, apply two tests:

**Test 1 — Contamination:**
*"Could someone who reads ONLY this question infer our specific implementation choices?"*
- If yes → contaminated. Rewrite.
- If no → clean.

**Test 2 — Reconstruction alignment:**
*"If a strong model answers this correctly from first principles, would its answer be substantially the same as our spec clause?"*
- If yes → well-formed question.
- If no → the question is not capturing the right problem, or the spec clause needs refinement.

### Contamination Examples

| ❌ Contaminated | ✅ Clean |
|---|---|
| "Our confidence scoring uses a 35/25/25/15 weight split. Should these weights change?" | "What factors should determine whether an auto-compiled knowledge entry is trustworthy enough to include without human review? How should those factors be weighted relative to each other?" |
| "We use 3 occurrences as the threshold for auto-skill creation. Should this be adaptive?" | "At what point should a system observing repeated work patterns automatically capture those patterns as reusable procedures? What factors should influence that threshold, and should it be static or adaptive?" |
| "Is our three-tier ClawMem → Wiki → MemVid architecture optimal?" | "For a system requiring both sub-millisecond session memory retrieval and long-term compressed archival with minimal active compute, describe the appropriate storage tier architecture and the criteria for promotion between tiers." |

### Context Clauses

Some questions need framing context to be answerable. This context describes the **problem space**, not the solution. Include it explicitly.

Example: A question about a sub-feature of the ante agent needs the framing "when extending an agentic coding assistant's core capabilities beyond its baseline feature set..." — this is domain context, not implementation reveal. The framing is **part of the question**.

### Constraint Tagging

Each question gets a `constraints` field listing the hard limits that apply. This prevents misclassification during the comparison phase.

```markdown
**Q-007**
Maps to: D-007
Expected Obviousness: 2
Constraint tags: [local-only, m-series-mac, no-cloud-dependency]
Question: For a system that needs to...
```

If the model's answer requires cloud infrastructure and the constraint is `local-only`, that divergence is classified as **INFEASIBLE** — not a real finding.

### Coverage Check

After generating all questions:

1. List all D-XXX IDs from `spec-as-designed.md`
2. Verify each D-XXX maps to at least one question
3. Any uncovered D-XXX = audit blind spot — either write a question for it or explicitly mark it as out-of-scope
4. Document the coverage map in the question file

### Answer Key

The `questions-v3.json` file serves as the answer key. Each question maps to exactly one D-ID. This makes the comparison in Phase 4 mechanical, not subjective.

### Output Format

Two outputs:

**`questions-v3.md`** — submitted to the S-tier model:

```markdown
# Spec Audit — [Project Name] — Questions v3
Date: [DATE]
Methodology: backtranslation-v3.1

Instructions to answering model:
Answer each question from first principles. Do not reference any project-specific
implementation. Your goal is to describe the solution you believe best addresses
each problem as stated. For each answer, include a confidence score (1-10)
reflecting how confident you are that your answer represents the optimal approach.
Your answers will be compared against an actual implementation to identify
divergences worth investigating.

---

## [Category]

**Q-001** [Maps to: D-001] [Obviousness: 3] [Constraints: none]
[Context if needed: ...]
[Question]

**Q-002** ...
```

Note: The `Obviousness` rating is for internal use only — it is NOT included in the
version submitted to the S-tier model. It appears only in `questions-v3.json`.

**`questions-v3.json`** — structured answer key for Phase 4 mapping:

```json
{
  "project": "Project Name",
  "spec_version": "3.1",
  "date": "YYYY-MM-DD",
  "methodology": "backtranslation-v3.1",
  "questions": [
    {
      "id": "Q-001",
      "maps_to": "D-001",
      "category": "architecture",
      "expected_obviousness": 3,
      "constraints": ["local-only"],
      "context": "...",
      "question": "..."
    }
  ]
}
```

---

## Phase 3: Submit to S-tier Model

**Submit `questions-v3.md` ONLY.** Do not attach `spec-as-designed.md`. Do not include the Expected Obviousness ratings or the answer key.

Instructions block to prepend:

```
Answer each question from first principles. Do not reference any project-specific
implementation you may be aware of. Your goal is to describe what you believe the
best solution is for each problem as stated.

For each answer, include:
- Your answer (as detailed as the question requires)
- Confidence: [1-10] — how confident are you this is the best approach?

Your answers will be compared against an actual implementation to identify
meaningful divergences.
```

Save the model's full response as `external-answers.md`.

If Phase 1b ran: submit `questions-built-v3.md` in a separate session (to avoid
cross-contamination between the designed and built question sets). Save output as
`external-answers-built.md`.

---

## Phase 4: Compare → Divergence Report

Map each answer in `external-answers.md` to its corresponding D-XXX entry in
`spec-as-designed.md` using the answer key (`questions-v3.json`).

### Divergence Classifications

| Classification | Meaning | Confidence weight | Action |
|---|---|---|---|
| **CONFIRMED** | Model's answer matches our solution | Any | No action — confirmed as first-principles default |
| **DIVERGENT — BETTER** | Model proposes a clearly superior approach | High confidence = strong signal | Priority candidate for implementation |
| **DIVERGENT — EQUIVALENT** | Different approach, similar outcomes | Any | Document, no priority change |
| **DIVERGENT — INFEASIBLE** | Model's answer violates a tagged constraint | Any | Document constraint gap only; no implementation action |
| **DIVERGENT — AMBIGUOUS** | Unclear which is better | Any | Flag for council deliberation |

### Divergence Etiology

For each divergence, assign an etiology — the **reason** the divergence occurred:

| Etiology | Meaning | Council Action |
|---|---|---|
| **NON-OBVIOUS-BUT-CORRECT** | Our solution is correct but not the default from first principles. The model's answer is plausible but inferior given our constraints/context. | Document constraints that explain why our solution is correct despite not being obvious. No implementation change. |
| **SUBOPTIMAL** | Our solution is genuinely inferior. The model found something better. | Adopt model's approach (or merge). This is the highest-value audit finding. |
| **AMBIGUOUS-QUESTION** | The question framing allowed multiple valid interpretations. After question refinement, the model converges. | Refine the question. Re-run if needed. No implementation change unless refinement reveals a real gap. |
| **CONSTRAINT-VIOLATION** | The model's answer violates a hard constraint we tagged. | Classify as INFEASIBLE. No implementation action. Document the constraint for future reference. |

**How to determine etiology:**
1. Check constraint tags first — if the model's answer violates a constraint → CONSTRAINT-VIOLATION
2. Check Expected Obviousness — if rated 1-2 and the model's answer is plausible but different → likely NON-OBVIOUS-BUT-CORRECT
3. Check Self-Quality Signal — if rated low (1-4) and the model's answer is clearly better → SUBOPTIMAL
4. If unclear after the above → AMBIGUOUS-QUESTION (refine and re-test)

### Built-vs-Designed Debt Classification (if Phase 1b ran)

| Alignment Pattern | Debt Type | Action |
|---|---|---|
| Model aligns with `spec-as-designed`, diverges from `spec-as-built` | **Implementation debt** | Task list focuses on bringing implementation in line with design |
| Model diverges from both | **Design debt** | Task list focuses on redesigning the relevant decisions |
| Model aligns with both | **No debt** | Confirmed — no action |

### Confidence Amplification Rule

A high-confidence (8-10) DIVERGENT answer from the S-tier model is a strong signal. A low-confidence (1-4) DIVERGENT is weaker and may reflect the question being ambiguous or the problem domain being genuinely uncertain.

**Cross-reference with Expected Obviousness:** A divergence on a question rated 1 (very unlikely to produce our answer) is EXPECTED and less alarming. A divergence on a question rated 5 (very likely to produce our answer) is UNEXPECTED and suggests either the question is bad or our "obvious" solution isn't actually obvious.

### Divergence Report Format

```markdown
# Divergence Report — [Project Name]
Date: [DATE]
Path: [2 / both]

| Q-ID | D-ID | Expected Obviousness | Our Solution (summary) | Model's Answer (summary) | Model Confidence | Classification | Etiology | Notes |
|------|------|---------------------|----------------------|--------------------------|------------------|----------------|----------|-------|
| Q-001 | D-001 | 3 | Three-tier memory (hot/warm/cold) | Two-tier (active/archive) | 9 | DIVERGENT-BETTER | SUBOPTIMAL | Model argues hot/warm distinction adds complexity without proportional benefit |
| Q-002 | D-002 | 1 | Custom deliberative council | Standard chain-of-thought | 6 | DIVERGENT-EQUIVALENT | NON-OBVIOUS-BUT-CORRECT | Our approach is domain-specific; model's is generic |
```

Produce `divergence-report.md`.

If Phase 1b ran, also produce `debt-classification.md`:

```markdown
# Debt Classification — [Project Name]

| D-ID | Designed Alignment | Built Alignment | Debt Type | Notes |
|------|-------------------|-----------------|-----------|-------|
| D-001 | CONFIRMED | DIVERGENT | Implementation | Hot/warm tiers designed but not fully implemented |
| D-002 | DIVERGENT | DIVERGENT | Design | Council formation needs redesign |
```

---

## Phase 5: Council Deliberation

For **AMBIGUOUS** and **DIVERGENT-BETTER** items:

> See `references/council-formations.md` for available council formations and
> selection criteria.

**Etiology drives council action:**

| Etiology | Council Focus | Expected Outcome |
|---|---|---|
| NON-OBVIOUS-BUT-CORRECT | Validate that constraints genuinely explain the non-obvious solution | Document constraint rationale; no implementation change |
| SUBOPTIMAL | Evaluate model's proposed alternative against our full context | Adopt model's approach, merge, or keep ours with documented reason |
| AMBIGUOUS-QUESTION | Refine the question and determine if divergence is real or artifact | Refined question for re-submission; possible implementation change if real |
| CONSTRAINT-VIOLATION | No council needed — classified automatically | Discard divergence; document constraint |

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

## Priority 1 — SUBOPTIMAL (adopted model's approach)
- [ ] T-001: [task] — implements D-XXX update — estimated scope: [S/M/L]

## Priority 2 — DIVERGENT-AMBIGUOUS (resolved to change)
- [ ] T-002: ...

## Priority 3 — Implementation debt (if Phase 1b ran)
- [ ] T-003: [bring implementation in line with design] — D-XXX

## Deferred
- [ ] T-004: [task flagged for future investigation] — reason: [...]
```

**`debt-classification.md`** (if Phase 1b ran) — see Phase 4 format.

---

## Bounded Iteration Rule (with Contamination Guard)

If a question-answer pair is being revised iteratively, apply this rule:

- **Round 1:** Initial answer received.
- **Round 2:** If the answer was ambiguous or incomplete, you may send ONE
  clarification. **CRITICAL: the clarification may only rephrase or narrow the
  question. It must NEVER reference the spec, the existing implementation, or
  any solution choices.** If you cannot clarify without revealing your
  implementation, the question is structurally ambiguous — mark it DEFERRED
  and revise offline.

  Diagnostic: if clarification produces convergence → the question was ambiguous,
  not the model's understanding. Revise the question for future use.
- **Round 3 maximum:** If after two rounds the answers remain divergent and the
  divergence can't be classified, the question itself or the spec clause is
  structurally broken. Mark as `DEFERRED` and revise offline.

**Do not iterate indefinitely.** Three rounds max. If the process can't converge
in three turns, the question needs architectural revision, not more back-and-forth.

**Contamination is irreversible.** If at any point during iteration you reveal
anything about your implementation to the S-tier model, that model's answers are
contaminated for all remaining questions. If contamination occurs, discard the
model's answers for affected questions and either re-run with a fresh session or
mark those questions as COMPROMISED.

---

## Pitfalls

- **Cardinal sin: revealing your implementation in questions.** Read each question
  after writing it and ask: "Can someone who reads ONLY this question infer our
  specific implementation choices?" If yes, rewrite.
- **Second cardinal sin: revealing your implementation during iteration.** The
  bounded iteration rule exists precisely because iteration creates the temptation
  to say "but we chose X, can you elaborate?" That's contamination. Don't do it.
- **Skipping the Constraints field.** The model may propose something better that
  you can't implement. Without constraints tagged, you'll misclassify it as
  DIVERGENT-BETTER and waste engineering time.
- **Coverage gaps.** Every spec clause needs a question. Use the coverage check.
- **Conflating Path 1 and Path 2 signals.** Path 1 (model sees spec + questions)
  confirms coherence. Path 2 (model is cold) finds genuine architectural divergence.
  They measure different things. Don't average them — present separately.
- **Treating low-confidence divergences as strong signals.** Weight confidence
  appropriately. A model that says "I'm not sure, but maybe X" is a weak finding;
  a model that confidently proposes a different architecture is a strong one.
- **One design decision per question.** If a decision involves multiple independent
  choices, split into multiple questions. A bundled question can't be cleanly mapped.
- **Ignoring Expected Obviousness.** A divergence on a question rated 1 (non-obvious
  answer) is expected and less alarming. A divergence on a question rated 5 (obvious
  answer) suggests the question is bad or your "obvious" solution isn't obvious.
  Use Expected Obviousness to weight divergence signals.
- **Skipping etiology.** Classification without etiology is incomplete. A
  DIVERGENT-BETTER finding with SUBOPTIMAL etiology demands implementation action.
  The same classification with NON-OBVIOUS-BUT-CORRECT etiology demands documentation
  only. Always assign etiology.

---

## Appendix A: Path 1 (Optional Parallel Validation)

Path 1 is NOT the main audit process. It's an opportunistic validation check that
runs in parallel if you happen to have pre-existing spec + question files from a
prior (possibly incorrect) audit attempt.

**Setup:**
1. If `spec-as-built.md` and `questions.md` (v1 files) exist → submit them
   TOGETHER to the S-tier model.
2. The model sees your full spec and your questions. It reviews your approach
   with complete context.
3. Save output as `external-answers-path1.md`.

**Signal type:** "Does a strong model agree with our approach when it can see
everything?" This is a coherence check, not an audit. It tells you whether your
design is internally consistent and well-reasoned when evaluated with full context.

**How to use Path 1 results:**
- If Path 1 model agrees with your approach AND Path 2 model independently
  reconstructs your approach → doubly confirmed.
- If Path 1 model agrees but Path 2 diverges → your approach is coherent but
  not the first-principles default. This is the most common and most useful
  pattern — it means your design is defensible but non-obvious.
- If Path 1 model disagrees AND Path 2 diverges → your approach may have
  fundamental issues worth investigating.

> See resource: `references/dual-path-merge-guide.md` for detailed merge procedures.

---

## Resources

These sub-documents are loaded only when needed. They are NOT read automatically —
reference them at the specific phase where they apply.

### `references/council-formations.md`
**When to load:** Phase 5 (Council Deliberation), when selecting a council
formation for deliberative refinement.
**What it covers:** Available council formation types, selection criteria by
use case, etiology-driven formation recommendations, multi-formation sequences
for complex divergence sets.
**Location:** `[skill-root]/references/council-formations.md`

### `references/question-quality-rubric.md`
**When to load:** Phase 2 (Backtranslation), if you're uncertain whether a
question is contaminated or well-formed.
**What it covers:** Graded rubric for question quality (contamination test,
specificity test, answerability test, reconstruction test, obviousness
calibration), worked examples for each test, repair patterns for common
contamination types.
**Location:** `[skill-root]/references/question-quality-rubric.md`

### `references/divergence-classification-guide.md`
**When to load:** Phase 4 (Compare), when a divergence is unclear and needs
a structured classification decision.
**What it covers:** Decision tree for AMBIGUOUS vs BETTER vs EQUIVALENT,
etiology determination flowchart, how to apply constraint tags to filter
INFEASIBLE, confidence weighting rules, Expected Obviousness cross-reference,
examples of each classification + etiology combination.
**Location:** `[skill-root]/references/divergence-classification-guide.md`

### `references/spec-writing-patterns.md`
**When to load:** Phase 1 (Document), when the project being audited is
complex or unfamiliar, or when the first draft of spec-as-designed.md needs
quality review.
**What it covers:** Patterns for writing Problem fields that feed clean
backtranslation, common spec-writing mistakes (too vague, too
implementation-specific, missing constraints, non-atomic clauses), worked
examples from different project types.
**Location:** `[skill-root]/references/spec-writing-patterns.md`

### `references/dual-path-merge-guide.md`
**When to load:** After both Path 1 and Path 2 results are returned, before
Phase 5 council (only if Path 1 was run).
**What it covers:** How to merge Path 1 and Path 2 findings into a unified
divergence picture, weighting Path 2 (cold reconstruction) heavier for
architectural decisions vs Path 1 (full context) for implementation coherence
checks, format for combined divergence report, when Path 1 and Path 2
disagree and how to resolve.
**Location:** `[skill-root]/references/dual-path-merge-guide.md`

---

## Quick Reference Checklist

```
PHASE 0
[ ] Check for existing spec-as-built.md and questions.md
[ ] If both exist → optionally submit as Path 1 (parallel)
[ ] If spec-as-built.md exists alone → use for Phase 1b

PHASE 1: spec-as-designed.md
[ ] Every decision has: Problem / Our Solution / Rationale / Constraints /
    Coverage Tags / Self-Quality Signal
[ ] Problem fields are written for a reader with NO project knowledge
[ ] Constraints field is complete — no decision missing its constraint set
[ ] Each D-XXX is atomic — one clause per entry

PHASE 1b (optional): built-vs-designed
[ ] spec-as-built.md exists and is sufficiently different from spec-as-designed.md
[ ] Generate parallel question set from spec-as-built.md
[ ] Plan separate submission session to avoid cross-contamination

PHASE 2: questions
[ ] Every question passes the contamination test
[ ] Every D-XXX maps to at least one question (coverage check)
[ ] Each question has Expected Obviousness rating (1-5)
[ ] Constraint tags copied to question metadata
[ ] Context clauses describe problem domain only
[ ] One question per atomic design decision

PHASE 3: submit
[ ] questions-v3.md submitted WITHOUT spec-as-designed.md
[ ] Expected Obviousness ratings NOT included in submitted version
[ ] Confidence scoring instructions included in the prompt to the model
[ ] Model output saved as external-answers.md
[ ] If Phase 1b ran: questions-built-v3.md submitted in separate session

PHASE 4: compare
[ ] Every answer mapped to a D-ID via answer key
[ ] Confidence scores recorded
[ ] INFEASIBLE divergences filtered via constraint tags before classification
[ ] Etiology assigned to each divergence
[ ] Expected Obviousness cross-referenced with divergence signal
[ ] If Phase 1b ran: debt classification produced
[ ] divergence-report.md produced

PHASE 5: council
[ ] council-formations.md consulted (references/council-formations.md)
[ ] Etiology drives council action (SUBOPTIMAL → adopt; NON-OBVIOUS → document)
[ ] Dual-path merge completed if both paths ran
[ ] Each AMBIGUOUS and DIVERGENT-BETTER item has a council recommendation

PHASE 6: output
[ ] ideal-spec.md produced (mirrors spec-as-designed.md structure)
[ ] task-list.md produced (prioritized by etiology + classification)
[ ] debt-classification.md produced (if Phase 1b ran)
```


