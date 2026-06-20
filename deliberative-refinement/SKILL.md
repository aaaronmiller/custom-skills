---
name: deliberative-refinement
description: |
  Use when: thinking through complex problems, making decisions, validating claims, exploring alternatives, uncertain how to proceed, need multiple perspectives, high-stakes choices, comparing options, weighing pros and cons, want second opinion, sanity check. Triggers: "help me decide", "which should I", "think through", "evaluate", "validate this", "is this right", "not sure", "explore alternatives", "figure out", "bulletproof", "compare", "pros and cons", "tradeoffs", "best approach", "recommend", "advise", "I can't decide", "stuck on", "confused", "code review", "architecture decision", "design review", ambiguous requests, contested decisions, strategic planning.
license: MIT
metadata:
  author: ice-ninja
  version: "1.0"
---

> ⚠️ **BEFORE USING THIS SKILL:** Review all files in the `references/` directory. These contain council specifications, profile guidance, and execution parameters required for proper skill execution.

# Deliberative Refinement

> Stop asking AI for answers. Make it defend them.

Drafts run through multiple critique rounds. Different experts attack from different angles. Web search grounds claims between passes. Only ideas that survive this pressure remain.

## When to Activate

- **Undefined problems**: "I'm not sure how to approach this"
- **Contested decisions**: "Should I do A or B?"
- **Complex reasoning**: Multi-step problems, strategic planning
- **Validation needs**: Claims requiring external evidence
- **Exploration**: "What are my options?"
- **High-stakes outputs**: Anything where being wrong is expensive

## Core Formula

```
V(X, Y, S) = X agents, Y rounds, S probes between rounds
Default: V(8, 3, 1) = 8 agents × 3 rounds × 1 web probe per gap

Execution: [Probe]→R₁→[Probe]→R₂→[Probe]→R₃→[Probe]
```

## Quick Reference

| Profile | V(X,Y,S) | Use Case |
|---------|----------|----------|
| Lite | V(3,1,0) | Quick sanity check |
| **Standard** | **V(8,3,1)** | **Default** |
| Deep | V(12,5,2) | High-stakes |
| Exhaustive | V(15,5,3) | Critical decisions |

| Mode | Trigger |
|------|---------|
| **CREATE** | No input → Generate → Lite validation |
| **REFINE** | Input provided → Deliberate → Return |
| **DECIDE** | Options presented → Evaluate → Recommend |
| **DISCOVER** | Approach unclear → Explore → Synthesize |

| Strategy | Trigger |
|----------|---------|
| **LINEAR** | "validate/correct" — cumulative improvements |
| **BRANCHING** | "explore/alternatives" — divergent options |

## Execution

### Phase 0: Intent Detection
Read the request. Pick the right profile. Don't ask for raw numbers.

### Phase 1: Council Selection
See [references/councils.md](references/councils.md):
- Code/technical → **Structured Review** (reflect-critique-refine loop)
- A vs B decision → **Elimination Tournament** (8→4→2→1)
- Math/logic → **Meta-Reasoning** (reasoners + arbiter)
- Large scope → **Parallel Groups** (split, debate, merge)
- General → **Expert Council** (full deliberation)

### Phase 1.5: The Architect (Plan Critique)
*Before* deliberation, pause. The "Architect" agent critiques the decomposition:
1.  "Does this structure miss any critical risks?"
2.  "Is the decomposition too granular or too broad?"
*Action*: Adjust Phase 2 plan if gaps are found.

### Phase 2: Decomposition
Split the problem into parts. Tackle risky pieces first.

### Phase 3: Deliberation
For each concept:
1. Form council (X agents)
7. Execute: [Probe]→R₁→[Probe]→R₂→...→Rᵧ→[Probe]
    *   **Rolling Memory**: If Round > 2, compress R1 votes into a "Previous Consensus" summary to save context.
    *   **Adversarial Injection**: If R1 result is **Unanimous**, FORCE the addition of an "Advocatus Diaboli" agent for R2 to challenge the groupthink.
8. Synthesize consensus

**Probe Strategy:**
- LINEAR: Each probe deepens previous finding
- BRANCHING: Independent sources for triangulation

### Phase 4: Synthesis
Pull validated pieces together. Ship.

## Convergence

| Signal | Action |
|--------|--------|
| Unanimous 2+ rounds | STOP — converged |
| <5% position change | STOP — diminishing returns |
| All agree R1 instantly | ADD adversarial agent (echo chamber risk) |
| Max rounds reached | STOP — time-boxed |

## Transformation Vectors

- **FORWARD →**: Expand, elaborate
- **BACKWARD ←**: Compress, distill
- **ISOMETRIC ↔**: Polish without scope change

## Anti-Patterns

> ⚠️ **CRITICAL: This skill must NEVER be executed in summarized or reduced form unless explicitly directed by the user.** A "quick approximation" of deliberative refinement defeats its entire purpose. If you cannot execute the full V(X,Y,S) cycle, inform the user rather than pretending to run a reduced version.

- ❌ **Summarized execution**: Claiming to run deliberative refinement while only skimming content
- ❌ **Approximated deliberation**: Describing what agents "would say" instead of actually deliberating
- ❌ **Bulk approval**: Approving sections without line-by-line review
- ❌ Single-pass reasoning on complex problems
- ❌ Skipping evidence grounding on factual claims
- ❌ Council collapse (all agree instantly without adversarial check)
- ❌ Over-validation (exhaustive for trivial questions)

## The Breakthrough

Six months ago you'd chain a dozen models together—one for generation, one for critique, one for fact-checking. Now? One model switches perspectives mid-conversation, grounds claims between rounds, iterates under pressure. Same quality. Way less plumbing.

## Resources

- [references/councils.md](references/councils.md) — Council type specifications
- [references/profiles.md](references/profiles.md) — Intensity parameter guidance
