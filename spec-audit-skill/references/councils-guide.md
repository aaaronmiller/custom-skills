# Council Selection Guide for Spec Audit

This reference explains how to match council formations from the deliberative-refinement skill to the specific challenge of comparing an as-built spec against external (S-tier model) answers.

## The Core Tension

A spec audit pits two perspectives against each other:

| Perspective | Knows | Doesn't Know |
|-------------|------|--------------|
| **Internal (As-Built)** | Full codebase, real constraints, history of decisions, resource limits | Ideal solutions, best practices outside the project's context, alternative architectures |
| **External (S-Tier)** | Broad knowledge of patterns, alternatives, best practices | The project's real constraints, why specific tradeoffs were made, code-level reality |

The council formation must create a productive tension between these two.

## Recommended Formations

### Default: Parallel Groups (8 agents)

Split into two groups of 4 — one arguing from the as-built perspective, one from the external answers. Then a merge council of all 8 synthesizes.

**Why:** The two groups can independently build coherent arguments without cross-contamination. The merge phase resolves differences.

**Execution:**
```
Group A (Internal): 4 agents, 3 rounds — "Defend the as-built spec. Flag only genuine flaws."
Group B (External): 4 agents, 3 rounds — "Argue for the ideal spec from the S-tier answers. Flag only what matters."
Merge: All 8 agents, 2 rounds — "Reconcile disagreements. Produce unified ideal-spec.md."
```

### For tightly coupled projects: Expert Council (7 agents)

If features are deeply interdependent (changing one cascades), use a single council where all agents see everything.

**Why:** Parallel groups might miss cross-cutting effects in tightly coupled systems.

### For contested specific features: Elimination Tournament (8 agents)

If the council deadlocks on a specific feature ("keep or replace"), run a focused tournament on just that feature.

**Why:** Forces a binary decision when consensus is elusive. Run after the main council, not instead of it.

### Profile selection

| Project Complexity | Profile | Rationale |
|-------------------|---------|-----------|
| Small (<5 features, single-file) | Lite V(3,1,0) | Quick sanity check |
| Medium (5-15 features, few files) | Standard V(8,3,1) | Default |
| Large (15-40 features, multi-module) | Deep V(12,5,2) | Need thorough coverage |
| Very large (40+ features, distributed) | Exhaustive V(15,5,3) | Critical decisions across subsystems |

## Strategy: BRANCHING vs LINEAR

- **BRANCHING** — Use when the gap between as-built and ideal is large and you want to explore alternatives independently before converging. Default for spec audit.
- **LINEAR** — Use when the as-built spec is mostly correct and you just need to validate/correct specific points. Faster but less exploratory.

## Handling contradictions

When a council identifies a clear contradiction between as-built and ideal:

1. **Record both positions** with their rationales
2. **Ask: is this a real contradiction or a context-dependent tradeoff?**
3. **If real:** The ideal spec wins, but document the cost of migration
4. **If context-dependent:** The as-built spec wins, but document why the external answer doesn't apply here (specific constraints, resource limits, etc.)
