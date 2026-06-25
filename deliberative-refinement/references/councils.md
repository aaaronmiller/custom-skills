# Council Types

## Selection Tree

```
Code/technical systems → Structured Review
Binary "A or B?" decision → Elimination Tournament
Math/logic/sequential steps → Meta-Reasoning
Large scope or constrained resources → Parallel Groups
Routine items with occasional depth → Selective Debate
General/unclear → Expert Council (DEFAULT)
```

## Specifications

| Council | Structure | Best For | Size |
|---------|-----------|----------|------|
| **Expert Council** | All agents deliberate each round | General problems, synthesis | 7 (odd) |
| **Elimination Tournament** | 8→4→2→1 bracket | Binary decisions, comparisons | 8 (even) |
| **Structured Review** | Reflect→Critique→Refine loop | Code, technical analysis | 5 (odd) |
| **Meta-Reasoning** | Reasoners + arbiter | Math, proofs, sequential logic | 5 (odd) |
| **Parallel Groups** | Split into teams, merge summaries | Large scope, budget limits | 8 (even) |
| **Selective Debate** | Debate only on disagreement | High volume, variable complexity | Variable |

## Details

### Expert Council
All X agents see the problem and deliberate together. Each round, agents state positions and respond to others. Consensus emerges through discussion.

**Use for**: Ambiguous problems, multiple valid perspectives, need synthesis not selection.

### Elimination Tournament
8 → 4 → 2 → 1 bracket. Options compete head-to-head. Forces clear winner.

**Use for**: "A or B?" decisions, comparing alternatives, need definitive choice.

### Structured Review
Three-phase loop per agent: Reflect on understanding → Critique the material → Propose refinements. Prevents knee-jerk reactions.

**Use for**: Code review, technical docs, anything requiring methodical analysis.

### Meta-Reasoning
Multiple reasoners work through problem. Meta-reasoner observes and arbitrates when they disagree. Catches logical errors.

**Use for**: Math proofs, sequential arguments, step-by-step correctness.

### Parallel Groups
Split agents into smaller teams (e.g., 8 → 2 groups of 4). Each group debates internally, then shares conclusions for synthesis.

**Use for**: Large problems, budget constraints, parallelization.

### Selective Debate
Agents give initial assessment. If they agree, skip extended deliberation. If disagreement, escalate to full debate.

**Use for**: High-volume processing where most items are routine.

## Odd vs Even

- **ODD (5, 7, 9)**: Consensus voting — natural tiebreaker
- **EVEN (4, 6, 8)**: Adversarial/elimination — bracket resolution
