---
date: 2026-05-18 10:00:00 PDT
ver: 1.0.0
author: ice-ninja
model: claude-opus-4-7
tags: [strata, plays, playbook, prompt-craft, pivot-resilience]
---

# Plays Playbook (`plays/`)

Author: the system. Layer: Prompt. Plays are reusable, intent-encoded interaction patterns that give the system determinism. They are not a one-shot task list. A task list is the thing that detonates on an upstream pivot, because every task baked in the assumption that changed. A play never bakes in the assumption. It reads the assumption from `intent.md` at execution time.

## The coupling rule

A play must never name a target it could instead read. Wrong: "deploy to Cloudflare Workers." Right: "deploy according to the deployment constraint in intent.md section 3." When the constraint changes, the play does not change, because the play never knew the constraint. It only knew where to read it. This is the entire reason plays survive pivots and tasks do not.

## The maturity-gap honesty

Plays are scaffolding across the gap between where models are now and where they will be when they resolve intent directly with no precompiled workflow. They thin as models improve. They do not vanish. State this in `substrate.md`. Anyone presenting plays as a permanent destination rather than a bridge is selling certainty they have not earned.

## Play file structure

Each play is one markdown file in `plays/`. Required sections:

```markdown
---
date: {{DATE}} {{TIME}} {{TZ}}
ver: 1.0.0
author: {{AUTHOR}} (system-owned)
model: {{MODEL}}
tags: [{{TAGS}}]
---

# Play: [name]

## Reads
[Every variable this play reads, and where. e.g. "deployment target: intent.md section 3". The play declares its inputs by location, never by value.]

## Preconditions
[State that must hold before the play runs. Halts cleanly if unmet.]

## Steps
[Ordered, deterministic. Each step references SPEC-IDs it advances.]

## Halt conditions
[When the play must stop and surface to a human rather than guess. The Klarna failure was a play with no halt condition: technically correct, intent-blind. Every play has one.]

## Ledger emission
[What this play appends to ledger/ledger.md on completion: decision made, outcome observed.]
```

## Minimum play set for any project

A scaffold play that creates the project skeleton from `context.md` section 9. A commit play that groups changes by concern and follows the constitution's commit convention, halting when a change cannot be mapped to a SPEC-ID. A deploy play that reads the deployment constraint from intent and never names a provider. Add domain plays as the project requires.

## Rules

Plays read from intent, they do not store intent. Every play has a halt condition. Every play emits to the ledger. No play names a target it could read. Plays are bridges, declared as bridges in `substrate.md`.
