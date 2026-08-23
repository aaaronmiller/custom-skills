---
date: 2026-05-18 10:00:00 PDT
ver: 1.0.0
author: ice-ninja
model: claude-opus-4-7
tags: [strata, intent, template, human-authored, constraints]
---

# Intent Template (`intent.md`)

Author: the human. Layer: Intent. This file is the one thing changed when the world changes. Everything downstream is derived from it. It contains zero technology, framework, or library tokens. A technology token here is a defect the validator fails on.

Intent is not a tagline and not a user story. It is a full schema of what is wanted, under what constraints, with what success and failure conditions, including the scale and quality expectations that architecture is derived from.

## Template structure

```markdown
---
date: {{DATE}} {{TIME}} {{TZ}}
ver: 1.0.0
author: {{AUTHOR}}
model: {{MODEL}}
tags: [{{TAGS}}]
---

# [Project Name] Intent v1.0

## 1. Goal
[One sentence stating the outcome, not the task. "Convince mid-level managers their AI strategy has a blind spot" is an outcome. "Write a blog post" is a task. If it does not fit in one sentence, intake is not finished.]

## 2. Intent level
[Declare which kind. Consumer intent becomes an epic. Engineering intent becomes plays. A project may carry both; list each separately.]

## 3. Constraints
[Hard constraints only. The deployment target lives here because it is a constraint, not an architecture. Budget, latency ceiling, regulatory regime, offline requirement, data residency, team stack the system must respect.]

## 4. Scale and quality expectations
[The numbers architecture is derived from. Concurrent users at peak. Recovery time objective after a zone failure. Throughput. Durability. These are intent, never spec, because they drive decisions the spec never makes.]

## 5. Success conditions
[What "this worked" means, observably, at the level of user outcome, not implementation.]

## 6. Failure conditions
[The branches the system must handle when things go wrong. If the requested item is unavailable, does the system recommend alternatives or fail silently. That branch is intent. Name every one that matters.]

## 7. Personas
[Each primary user type, their goal, their frustration, their context, their technical sophistication.]

## 8. Scope boundaries
| In scope | Out of scope | Rationale |
|----------|-------------|-----------|
| ... | ... | ... |

## 9. Prior art
| Solution | Strength | Weakness | Gap this fills |
|----------|----------|----------|----------------|
| ... | ... | ... | ... |
[Patterns adopted and patterns deliberately avoided, with reasoning. This is where Phase 2 research lands. It lives nowhere else.]

## 10. Assumptions and dependencies
[Assumptions about users and environment. External dependencies as capabilities, not products.]

## 11. Open intent questions
[Maximum three `[NEEDS CLARIFICATION]` markers, only for decisions that materially change scope.]
```

## Rules

The deployment target is a constraint and goes in section 3, never in spec, never in context as if the human chose it. Non-functional requirements go in section 4 because they drive architecture. Failure branches go in section 6 because they are intent decisions, not test cases. No technology tokens anywhere. Outcomes not tasks in the goal. When the world changes, this is the only file the human edits, and the system re-derives the rest.
