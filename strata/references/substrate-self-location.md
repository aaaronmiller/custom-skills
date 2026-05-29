---
date: 2026-05-18 10:00:00 PDT
ver: 1.0.0
author: ice-ninja
model: claude-opus-4-7
tags: [strata, substrate, self-location, honesty, maturity]
---

# Substrate Self-Location (`substrate.md`)

Author: the human. This file turns the closing question of the autopsy, are you being honest with yourself, into a required field. You declare which substrate level the project actually operates at and which decisions are pre-locked at preparation time versus resolved live at implementation time. You do not get to claim a level you have not earned.

## The levels (lineage: Dan Shapiro, January 2026, zero-indexed)

S0, manual with spicy autocomplete. The human writes the code.
S1, the AI handles discrete well-scoped tasks under full human review.
S2, the AI handles multi-file change while the human reads every line. The field's documented majority sits here and mistakes it for the destination.
S3, the human directs and verifies, the AI develops. STRATA operationalizes this level honestly.
S4, the human is a product manager, writes specifications, evaluates outcomes, does not read the code.
S5, the dark factory. A specification enters, tested software exits, evaluated against separated scenarios the system cannot game. No human writes or reviews code.

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
[S0 through S5. One level. If you are between, say the lower one and explain the reach.]

## Pre-locked decisions
[Every decision fixed at preparation time that a true level above this one would resolve live. Be specific. This is the honesty the methodology demands.]

## Live-resolved decisions
[What is genuinely resolved at implementation time, not pre-locked.]

## Empirical memory state
[Full, partial, or empty ledger. If empty, Context Crafting is intuition-based and this is stated here and in context.md.]

## Known reach
[What this project claims it can do that it has not yet proven. Stated as reach, not as fact.]
```

## Why this is required, not optional

Two failure modes the field repeats. One, claiming a high level while pre-locking like a low one, which produces a methodology that looks autonomous and behaves brittle. Two, selling certainty about a level nobody involved has lived. STRATA blocks both by making the admission a file the validator checks for the presence of a declared level. The honest practice is to name your level of certainty and then do the work. This file is where you name it.
