# Council Formations — Reference Guide

**Purpose:** Provides council formation selection criteria for Phase 5 deliberative
refinement on spec-audit divergences.

---

## Formation Types

### 1. Adversarial (Prosecutor/Defender)
**Best for:** SUBOPTIMAL etiology divergences where the model proposes a clearly
different approach and you need to stress-test both sides.
- Prosecutor argues for the model's approach
- Defender argues for your existing solution
- Judge evaluates

### 2. Socratic (Questioner/Responder)
**Best for:** NON-OBVIOUS-BUT-CORRECT etiology where you need to surface the
hidden constraints that make your solution correct despite not being obvious.
- Questioner probes WHY your solution works despite not being the default
- Responder articulates the constraint reasoning

### 3. Panel of Experts
**Best for:** AMBIGUOUS-QUESTION etiology where multiple valid interpretations
exist and you need diverse perspectives.
- Multiple experts each evaluate independently
- Merge perspectives to identify common ground

### 4. Red Team / Blue Team
**Best for:** DIVERGENT-BETTER where the stakes are high (major architectural change).
- Red team tries to break the model's proposed alternative
- Blue team tries to defend it
- Outcome determines adoption confidence

### 5. Sequential Refinement
**Best for:** Mixed divergence sets with different etiologies — run different
formations for different items.
- Process SUBOPTIMAL items with Adversarial
- Process NON-OBVIOUS items with Socratic
- Process AMBIGUOUS items with Panel of Experts

---

## Etiology → Formation Map

| Etiology | Recommended Formation | Rationale |
|---|---|---|
| SUBOPTIMAL | Adversarial or Red/Blue | Need to stress-test the model's proposed alternative before adopting |
| NON-OBVIOUS-BUT-CORRECT | Socratic | Need to surface hidden constraints that justify the non-obvious solution |
| AMBIGUOUS-QUESTION | Panel of Experts | Need diverse perspectives to disambiguate |
| CONSTRAINT-VIOLATION | None (auto-classified) | No council needed |

---

## Multi-Formation Sequences

For complex audit results with multiple divergence types:

1. Run Socratic on NON-OBVIOUS items first → produces constraint documentation
2. Run Adversarial on SUBOPTIMAL items → produces adoption/merge decisions
3. Run Panel of Experts on remaining AMBIGUOUS items → produces refined questions
4. Final synthesis: merge all council outputs into ideal-spec.md

---

*Expand this file with project-specific formation configurations as needed.*

---

## Documenting Your Formation: `council-plan.md` template

Once a formation is selected, record the decision so the deliberation is reproducible:

```markdown
# Council Plan — <Project Name>

## Formation
<e.g. Parallel Groups: Group A (Internal/As-Built) vs Group B (External/Ideal) → Merge Council>

## Profile
V(agents, rounds, probes) — e.g. V(8, 3, 1) = 8 agents, 3 rounds, 1 web probe per gap

## Mode
<REFINE when comparing two inputs (as-built spec + external answers), else GENERATE>

## Strategy
<BRANCHING to explore the gap between perspectives; CONVERGING to drive to one answer>

## Materials Given to Each Group
<which documents each group/agent receives>
```
