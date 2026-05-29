# Divergence Classification Guide — Reference Guide

**Purpose:** Decision tree and worked examples for classifying divergences and
assigning etiology during Phase 4. Load this when a divergence is unclear.

---

## Classification Decision Tree

```
Model's answer received
│
├── Does the answer violate any tagged constraint?
│   └── YES → DIVERGENT-INFEASIBLE / CONSTRAINT-VIOLATION
│        (No council needed. Document the constraint.)
│
├── Does the answer substantially match our solution?
│   └── YES → CONFIRMED
│        (No action. Our solution is the first-principles default.)
│
├── Is the answer clearly superior to our solution?
│   ├── YES, and model is high-confidence (8-10)
│   │    → DIVERGENT-BETTER / SUBOPTIMAL
│   │     (Priority implementation candidate.)
│   │
│   ├── YES, but model is low-confidence (1-4)
│   │    → DIVERGENT-AMBIGUOUS
│   │     (Flag for council. May reflect domain uncertainty.)
│   │
│   └── UNCLEAR whether it's superior
│        → DIVERGENT-AMBIGUOUS
│         (Flag for council.)
│
├── Is the answer different but with similar outcomes?
│   └── YES → DIVERGENT-EQUIVALENT / NON-OBVIOUS-BUT-CORRECT
│        (Document. Check Self-Quality Signal — if high, our solution is
│         non-obvious but correct. If low, may be SUBOPTIMAL.)
│
└── None of the above fit clearly
     → DIVERGENT-AMBIGUOUS / AMBIGUOUS-QUESTION
      (Refine question and re-test. If model converges after refinement,
       the question was the problem, not the design.)
```

---

## Etiology Determination Flowchart

```
Divergence identified
│
├── Check constraint tags → violation? → CONSTRAINT-VIOLATION
│
├── Check Expected Obviousness
│   ├── Rated 1-2 (non-obvious answer expected)
│   │   ├── Model's answer is plausible but contextually inferior
│   │   │    → NON-OBVIOUS-BUT-CORRECT
│   │   └── Model's answer is genuinely better even accounting for context
│   │        → SUBOPTIMAL
│   │
│   └── Rated 4-5 (obvious answer expected)
│       ├── Model produced a different answer
│       │    → AMBIGUOUS-QUESTION (our "obvious" answer isn't obvious —
│       │     question may be bad)
│       └── Model produced our answer → CONFIRMED (no divergence)
│
├── Check Self-Quality Signal
│   ├── Low (1-4): our solution may be suboptimal → SUBOPTIMAL likely
│   └── High (8-10): our solution is probably correct → NON-OBVIOUS-BUT-CORRECT likely
│
└── Still unclear → AMBIGUOUS-QUESTION
     (Refine question. Re-run. If divergence persists after refinement,
      reassess etiology with new data.)
```

---

## Worked Examples

### Example 1: Three-Tier Memory Architecture

**D-001:** Three-tier memory (ClawMem hot/warm SQLite, Wiki permanent markdown,
MemVid V2 cold archival)
**Expected Obviousness:** 3 (possible — multi-tier is common but three is non-standard)
**Model's answer:** Two-tier (active hot store + cold archive). Argues hot/warm
distinction adds complexity without proportional benefit.
**Model confidence:** 9

**Classification:** DIVERGENT-BETTER
**Etiology determination:**
- No constraint violation (both approaches run locally)
- Expected Obviousness 3 — divergence is not unexpected
- Model is high-confidence (9)
- The model makes a specific, well-reasoned argument (complexity without benefit)
- Self-Quality Signal on D-001 was 7 (we're fairly confident)

→ **Etiology: SUBOPTIMAL** (tentative — council should validate whether the
hot/warm distinction provides sufficient benefit to justify the complexity)

### Example 2: Confidence Scoring Weights

**D-007:** Weighted confidence: 35% source reliability, 25% corroboration, 25%
recency, 15% authoritative bonus
**Expected Obviousness:** 1 (very unlikely a designer independently produces
these exact weights)
**Model's answer:** Multi-factor confidence scoring with source reliability as
primary factor, but suggests corroboration and recency should be equal-weighted
with no separate authoritative bonus (absorbed into source reliability).
**Model confidence:** 6

**Classification:** DIVERGENT-EQUIVALENT
**Etiology determination:**
- No constraint violation
- Expected Obviousness 1 — our exact weights are non-obvious, divergence expected
- Model is medium-confidence (6)
- The model's approach is structurally similar (multi-factor, reliability-primary)
  but differs in detail
- Self-Quality Signal on D-007 was 5 (we're uncertain about our weights)

→ **Etiology: NON-OBVIOUS-BUT-CORRECT** for the overall structure (multi-factor
weighted scoring), but the specific weight values may be SUBOPTIMAL. Council
should evaluate whether the authoritative bonus provides independent signal.

### Example 3: Cloud-Based Storage

**D-003:** Local-only memory system (no cloud dependency)
**Expected Obviousness:** 4 (local-first is fairly standard for dev tools)
**Model's answer:** Cloud-backed memory with local caching for performance,
enabling cross-device sync and team knowledge sharing.
**Model confidence:** 8

**Classification:** DIVERGENT-INFEASIBLE
**Etiology determination:**
- Constraint tags on Q-003: [local-only, m-series-mac, no-cloud-dependency]
- Model's answer requires cloud infrastructure
- Constraint is violated

→ **Etiology: CONSTRAINT-VIOLATION** (no council needed. Document the constraint
for future reference if requirements change.)

---

*Expand with project-specific examples as you encounter edge cases.*
