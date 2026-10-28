---
date: 2026-05-18 10:00:00 PDT
ver: 1.0.0
author: ice-ninja
model: claude-opus-4-7
tags: [spec-prep, substrate, self-location, honesty, maturity]
---

# Substrate Self-Location (`substrate.md`)

Author: the human. This file turns the closing question of the autopsy, are you being honest with yourself, into a required field. You declare which substrate level the project actually operates at and which decisions are pre-locked at preparation time versus resolved live at implementation time. You do not get to claim a level you have not earned.

## Source taxonomies and legacy compatibility

Ahuja's **Substrate Stack** in the supplied article has five numbered levels:

1. Vibe: model and coding interface, without the proposed persistent intent/contract substrate.
2. Spec-driven: structured specification tooling.
3. Intent-driven: separated layers, the four crafts, plays and an empirical knowledge base.
4. Autonomous: shared guardrails and reasoning across plays. The author explicitly describes this as not yet lived.
5. Dark Factory: live resolution within a largely autonomous methodology. The author explicitly treats the implementation as unresolved.

These are Ahuja's proposed substrate categories, not a benchmark or a capability certification. His article locates his own implementation around 2.5-2.75, not fully at 3. It credits Dan Shapiro for the Dark Factory term and autonomy-model influence; it does not make the two taxonomies numerically interchangeable.

**Existing STRATA labels S0-S5 are retained as legacy file/validator syntax.** They describe the local operating arrangement, not an exact Shapiro scale or a renumbering of Ahuja's five levels:

- S0: human implementation with autocomplete.
- S1: discrete agent tasks with human review.
- S2: agent changes with line-by-line human review.
- S3: human direction and verification with agent development.
- S4: specification/outcome-oriented human oversight rather than routine line review.
- S5: claimed autonomous production with separately evaluated outcomes, requiring evidence beyond this declaration.

Name the framework beside the label, and describe actual human review, agent permissions, protected evaluation and decision timing. Using this skill does not establish any maturity level. Do not silently reinterpret old declarations under a new taxonomy; record any revised interpretation with its source and evidence.

## What you must declare

```markdown
---
date: {{DATE}} {{TIME}} {{TZ}}
ver: 1.0.0
author: {{AUTHOR}}
model: {{MODEL}}
tags: [{{TAGS}}]
---

# Substrate Self-Location

## Declared level
[Legacy STRATA label S0 through S5 for compatibility, followed by the actual operating arrangement and evidence. If also discussing Ahuja's Levels 1-5, label that framework separately; do not imply numeric equivalence.]

## Pre-locked decisions
[Decisions fixed at preparation time, their source authority, and why they are fixed. Distinguish required user constraints from provisional agent choices. Do not infer a maturity rank from timing alone.]

## Live-resolved decisions
[What is genuinely resolved at implementation time, not pre-locked.]

## Empirical memory state
[Full, partial, or empty project ledger; distinguish applicable observed outcomes, current research and unsupported intuition. Record access and relevance limits.]

## Known reach
[What this project claims it can do that it has not yet proven. Stated as reach, not as fact.]
```

## Why this is required, not optional

The declaration makes pre-locking, missing evidence and unproven autonomy visible. The validator checks the presence of a legacy level label, not whether the claimed capabilities exist. Validate material capabilities separately; neither a label nor this file enforces evaluator isolation or certifies autonomy.
