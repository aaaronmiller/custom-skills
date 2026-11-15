# Question Quality Rubric — Reference Guide

**Purpose:** Graded rubric for evaluating backtranslated question quality during
Phase 2. Load this when you're uncertain whether a question is contaminated or
well-formed.

---

## The Five Tests

### Test 1: Contamination Test
**Question:** "Could someone who reads ONLY this question infer our specific
implementation choices?"

| Score | Meaning | Action |
|---|---|---|
| Pass | No implementation details can be inferred | Proceed |
| Fail | Implementation is partially or fully revealed | Rewrite the question |

**Common contamination patterns:**
- Naming specific technologies you used ("our SQLite-based memory layer")
- Including specific numerical values from your implementation ("35/25/25/15 weights")
- Framing as evaluation ("should our X change?" / "is our Y optimal?")
- Using internal terminology that maps to specific design decisions

**Repair pattern:** Replace implementation-specific language with problem-space
language. "Our SQLite-based memory layer" → "A memory layer that needs
sub-millisecond retrieval for recent context."

**Examples (contaminated vs clean):**

| Contaminated (reveals implementation) | Clean (problem space only) |
|---|---|
| "Our confidence scoring uses a 35/25/25/15 weight split for self-consistency/freshness/cross-refs/evidence. Should these weights change?" | "What factors should determine whether an auto-compiled knowledge entry is trustworthy enough to include without human review? How should those factors be weighted relative to each other?" |
| "Should our auto-skill creation threshold of 3 occurrences be adaptive?" | "At what point should a system that observes repeated work patterns automatically capture those patterns as reusable procedures? What factors should influence that threshold?" |
| "Is our three-tier architecture (ClawMem → Wiki → MemVid) optimal or should we collapse to two tiers?" | "For a system that needs both sub-millisecond session memory retrieval and long-term compressed archival, what tier architecture is appropriate? Describe the optimal storage hierarchy." |

### Test 2: Specificity Test
**Question:** "Is the question specific enough that a competent designer would
give a focused answer, or would it produce a broad survey?"

| Score | Meaning | Action |
|---|---|---|
| Too vague | Will produce a broad survey answer | Narrow the question with more context |
| Appropriately specific | Will produce a focused, comparable answer | Proceed |
| Too specific | Has become a disguised implementation question | Broaden slightly |

**Repair pattern for "too vague":** Add domain constraints from the D-XXX's
Problem field. "How should a system handle memory?" → "How should a system
needing sub-millisecond session retrieval AND long-term archival handle memory
tiering and promotion?"

### Test 3: Answerability Test
**Question:** "Can a competent system designer answer this question from first
principles, without any knowledge of our project?"

| Score | Meaning | Action |
|---|---|---|
| Answerable | A designer can reason about the problem domain | Proceed |
| Unanswerable | Requires project-specific knowledge to answer | Add domain context |

**Repair pattern:** Add a context clause that provides the necessary framing
without revealing the solution. "How should confidence scoring work?" → "In a
system that auto-compiles knowledge entries from multiple sources with varying
reliability, how should confidence scoring work?"

### Test 4: Reconstruction Alignment Test
**Question:** "If a strong model answers this correctly from first principles,
would its answer be substantially the same as our spec clause?"

| Score | Meaning | Action |
|---|---|---|
| Aligned | The spec clause would be a natural answer | Proceed |
| Misaligned | The question would produce a different answer than our clause | Question captures the wrong problem, or spec clause needs refinement |

**Repair pattern:** Re-read the D-XXX Problem field. The question should be
derived from the Problem, not from the Solution. If the Problem is imprecise,
refine the Problem field first.

### Test 5: Obviousness Calibration Test
**Question:** "Given this question, how likely is it that a competent designer
would produce our exact spec clause as the answer?"

| Rating | Implication | Action |
|---|---|---|
| 1-2 (unlikely) | Our solution is non-obvious | Divergence is expected; rate Expected Obviousness accordingly |
| 3 (possible) | Our solution is one of several plausible answers | Divergence reveals alternatives; moderate audit value |
| 4-5 (likely) | Our solution should be the default | Divergence is unexpected; question may be bad |

---

## Worked Example

**Spec clause (D-012):** "The system uses a weighted confidence score combining
source reliability (35%), corroboration count (25%), recency (25%), and
authoritative-source bonus (15%) to determine whether an auto-compiled entry
should be included without human review."

**Draft question:** "How should confidence scoring work for an auto-compilation system?"

**Evaluation:**
- Test 1 (Contamination): PASS — no implementation revealed
- Test 2 (Specificity): FAIL — too vague, will produce a broad survey
- Test 3 (Answerability): PARTIAL — answerable but unfocused
- Test 4 (Reconstruction): FAIL — a broad question won't produce our specific
  weighting scheme as the answer
- Test 5 (Obviousness): N/A — question is too vague to calibrate

**Revised question:** "In a system that auto-compiles knowledge entries from
multiple sources with varying reliability, what factors should determine whether
an entry is trustworthy enough to include without human review, and how should
those factors be weighted relative to each other?"

**Re-evaluation:**
- Test 1: PASS
- Test 2: PASS — specific enough for a focused answer about factors and weights
- Test 3: PASS — answerable from first principles
- Test 4: PASS — a natural answer would enumerate factors and propose weights
- Test 5: 2 — unlikely a designer would independently produce our exact 35/25/25/15
  split, but they might produce a similar multi-factor weighted scheme

---

*Expand with project-specific examples as you encounter contamination patterns.*
