---
description: Deliberative Refinement - Use when validating drafts, making complex decisions, or stress-testing claims. Parameterized multi-agent deliberation for transforming drafts into production-ready deliverables through structured critique and evidence grounding.
---

# Deliberative Refinement

> *Stop asking AI for answers. Make it defend them.*

---

## Quick Example

**Before (Draft claim):**
> Our new architecture reduces latency by 50%.

**After V(5, 2, 1) Deliberation:**
> Our new architecture reduces P95 latency from 120ms to 58ms under 10K concurrent users, validated against production traffic logs from Nov 2024. Edge cases with cold caches show 85ms (still a 29% improvement).

---

## Quick Reference

### Profiles

| Profile | V(X, Y, S) | Use Case |
|---------|------------|----------|
| Lite | V(3, 1, 0) | Quick sanity check |
| **Standard** | **V(8, 3, 1)** | **Default** |
| Deep | V(12, 5, 2) | High-stakes |
| Exhaustive | V(15, 5, 3) | Critical decisions |

### Mode Detection

| Mode | Trigger | Process |
|------|---------|---------|
| **CREATE** | "write", "generate", "draft", no file | Generate → Lite validation → Return |
| **REFINE** | "improve", "fix", file provided | Analyze → Deliberate → Return |
| **DECIDE** | "should I", "which", "A or B" | Evaluate → Deliberate → Recommend |
| **DISCOVER** | "how should I", "what's the best way" | Explore → Deliberate → Synthesize |

### Strategy Detection

| Strategy | Trigger | Behavior |
|----------|---------|----------|
| **LINEAR** | "fix", "correct", "validate" | Cumulative improvements (default) |
| **BRANCHING** | "explore", "alternatives" | Divergent options for selection |

### Council Selection

| Input Type | Council | Why |
|------------|---------|-----|
| Code/Technical | Structured Review | Reflect-critique-refine loop |
| A vs B decision | Elimination Tournament | Forces clear winner |
| Math/Logic | Meta-Reasoning | Step verification with arbiter |
| Large scope | Parallel Groups | Split, debate, merge |
| General/Ambiguous | **Expert Council** | **Default** |

---

## Core Formula

```
V(X, Y, S) = X agents, Y rounds, S probes between rounds
Default: V(8, 3, 1) = 8 agents × 3 rounds × 1 probe per gap = 4 total probes/cycle

Execution Pattern:
[Probe] → R₁ → [Probe] → R₂ → [Probe] → R₃ → [Probe]
   ↑            ↑            ↑            ↑
   1            2            3            4  (Y+1 probes total)
```

---

## Phase -1: Target Analysis (Pre-Instantiation)

When file is provided, analyze before proceeding:

```
1. MEASURE file size

2. CLASSIFY:
   < 10KB     → SMALL    → Process inline
   10-25KB   → MEDIUM   → Create scratch file for notes
   25-50KB   → LARGE    → Recommend chunking
   50-100KB  → VERY_LARGE → Mandatory 10KB chunks
   > 100KB   → MASSIVE  → Mandatory chunks with 15% overlap

3. INFORM user of strategy
```

### Scratch File Protocol

For MEDIUM+ files, create: `.deliberate-scratch-[original-name].md`

Contents: Key claims, validation status, agent votes, web findings, draft corrections.

### Checkpoint Protocol

For multi-session work, save state to `.deliberate-checkpoint-[hash].json`:

```json
{
  "target": "filename.md",
  "config": {"profile": "Standard", "X": 8, "Y": 3, "S": 1},
  "strategy": "LINEAR",
  "passes": {"total": 20, "completed": [1,2,3], "current": 4},
  "approval_rate": 0.85
}
```

| User Says | Action |
|-----------|--------|
| "keep going" / "continue" | Resume from checkpoint |
| "start over" / "fresh" | Archive checkpoint, begin anew |
| "status" | Report state without executing |

---

## Phase 0: Intent Detection

Infer from user language (never ask for raw V() params):

| Signal | Profile | Vector |
|--------|---------|--------|
| "make better" | Standard | ISOMETRIC |
| "expand" / "more detail" | Deep | FORWARD |
| "summarize" / "shorter" | Standard | BACKWARD |
| "quick check" | Lite | ISOMETRIC |
| "bulletproof" / "investor-ready" | Exhaustive | ISOMETRIC |

**Default if ambiguous**: Standard + ISOMETRIC

---

## Phase 1: Council Selection

```
IF input is code OR technical documentation:
    → Structured Review (reflect-critique-refine loop)
    
ELSE IF input is "should I do A or B?":
    → Elimination Tournament (8→4→2→1 bracket)
    
ELSE IF input involves math OR sequential logic:
    → Meta-Reasoning (reasoners + arbiter)
    
ELSE IF scope is large OR resources constrained:
    → Parallel Groups (split, debate, merge)
    
ELSE:
    → Expert Council (all agents deliberate) ← DEFAULT
```

### Council Specifications

| Council | Structure | Size |
|---------|-----------|------|
| **Expert Council** | All agents deliberate each round | 7 (odd) |
| **Elimination Tournament** | Bracket elimination | 8 (even) |
| **Structured Review** | 3-phase loop per agent | 5 (odd) |
| **Meta-Reasoning** | Reasoners + arbiter | 5 (odd) |
| **Parallel Groups** | Split into teams, merge | 8 (even) |
| **Selective Debate** | Debate only on disagreement | Variable |

**Odd vs Even**: Odd for consensus voting (natural tiebreaker). Even for adversarial/elimination (bracket resolution).

---

## Phase 2: Decomposition

1. Break document/problem into T discrete concepts
2. **Architect Review**: Critique the breakdown. "Are we missing blind spots?"
3. Prioritize by importance/risk/uncertainty

---

## Phase 3: Deliberation

For each concept t:
1. Form council (X agents, selected type)
2. Execute: [S Probes]→R₁→[S]→R₂→...→Rᵧ→[S]
   *   *Memory*: Summarize early rounds if > R2.
   *   *Defense*: Inject Adversarial Agent if R1 is unanimous.
3. Document votes, synthesize consensus

### Probe Strategy

**LINEAR (DEPTH)** — Default:
```
Probe 1: Search for X
Probe 2: Deeper on key finding from Probe 1
Probe 3: Verify specific claim from Probe 2
```

**BRANCHING (BREADTH)** — When triangulation needed:
```
Probe 1: Source A for X
Probe 2: Source B for X (independent)
Probe 3: Source C for X (independent)
```

| Profile | S Value | Default Strategy |
|---------|---------|------------------|
| Lite | 0 | None |
| **Standard** | **1** | **LINEAR** |
| Deep | 2 | LINEAR |
| Exhaustive | 3 | BRANCHING |

---

## Phase 4: Correction Loop

If errors found during validation:
```
"This is wrong" → V(3, 1, 0) quick fix
"More errors"   → V(5, 2, 1) expanded search
"Bulletproof"   → V(10, 3, 2) full council
```

---

## Convergence & Stopping

| Signal | Action |
|--------|--------|
| Unanimous approval 2+ rounds | STOP — converged |
| <5% vote change between rounds | STOP — diminishing returns |
| All agree instantly (R1) | ADD adversarial agent (echo chamber risk) |
| Max rounds reached | STOP — time-boxed |

---

## Transformation Vectors

```
Tv = Direction of change:
  → FORWARD  : Expand, elaborate, add detail
  ← BACKWARD : Compress, summarize, distill
  ↔ ISOMETRIC: Polish without size change
```

| Vector | When to Use |
|--------|-------------|
| FORWARD | Draft too sparse |
| BACKWARD | Draft too verbose |
| ISOMETRIC | Right size, needs quality |

---

## The Breakthrough

What used to require orchestrating a dozen different models—one for generation, another for critique, a third for fact-checking—now happens through tool-interspersed reasoning. One model switches expert perspectives on demand, grounds claims between rounds, and iterates under adversarial pressure. Same quality, fraction of the complexity.

---

## Anti-Patterns

❌ Skipping Phase 0 (asking user for raw V() parameters)
❌ Single-pass reasoning on complex problems
❌ Under-grounding (S=0 on factual claims)
❌ Council collapse (all agree instantly without adversarial check)
❌ Over-validation (exhaustive for trivial changes)

---

## Execution Checklist

```
[ ] 1. Detect MODE (CREATE/REFINE/DECIDE/DISCOVER)
[ ] 2. If file provided: Check size, apply chunking if needed
[ ] 3. Infer profile from user intent
[ ] 4. Select council type based on input
[ ] 5. Confirm: "Running [mode] with [profile] profile"
[ ] 6. Execute: For each concept, run V(X, Y, S)
[ ] 7. Check convergence criteria
[ ] 8. Return refined output with summary
```

---

## Key Principle

**All variables are fluid.** The formula adapts to stakes:

- Quick draft → V(3, 1, 0)
- Normal validation → V(8, 3, 1)
- Critical decision → V(15, 5, 3)

Low-stakes = minimal validation. High-stakes = maximum intensity.

**END OF SLASH COMMAND**
