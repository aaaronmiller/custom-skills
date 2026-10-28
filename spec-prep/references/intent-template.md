---
date: 2026-05-18 10:00:00 PDT
ver: 1.0.0
author: ice-ninja
model: claude-opus-4-7
tags: [spec-prep, intent, template, human-authored, constraints]
---

# Intent Template (`intent.md`)

Authoritative owner: the user; an agent may draft with provenance. Layer: Intent. Maintain this asset separately from requirements and design. Goal changes start here; behavior, architecture and workflow corrections start at their owning layer and reconcile affected dependents. Preserve explicitly required technologies with their source and justified layer exception; do not promote agent proposals into constraints.

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
[Consumer/product outcomes inform epics; engineering workflow outcomes inform governance or reusable plays. List both when present. Both need observable acceptance in requirements/spec; engineering intent is not permission to execute a commit, deployment or other consequential action.]

## 3. Constraints
[Hard constraints only. The deployment target lives here because it is a constraint, not an architecture. Budget, latency ceiling, regulatory regime, offline requirement, data residency, team stack the system must respect.]

## 4. Scale and quality expectations
[The numbers architecture is derived from. Concurrent users at peak. Recovery time objective after a zone failure. Throughput. Durability. These expectations inform design; derive linked measurable acceptance clauses in requirements/spec as well.]

## 5. Success conditions
[What "this worked" means, observably, at the level of user outcome, not implementation.]

## 6. Failure conditions
[The branches the system must handle when things go wrong. If the requested item is unavailable, does the system recommend alternatives or fail silently. That branch is intent. Name every one that matters.]

## 7. Personas
[Each primary user type, their goal, their frustration, their context, their technical sophistication.]

## 8. User stories
[One story per meaningful capability, grouped into epics. Form: As a <persona>, I want <capability> so that <outcome>. Each story carries Given/When/Then acceptance in user-observable terms and lists the SPEC-IDs that verify it. Stories are intent: they say what a person needs, never how the system does it.]

## 9. Scope boundaries
| In scope | Out of scope | Rationale |
|----------|-------------|-----------|
| ... | ... | ... |

## 10. Prior art
| Solution | Strength | Weakness | Gap this fills |
|----------|----------|----------|----------------|
| ... | ... | ... | ... |
[Patterns adopted and patterns deliberately avoided, with reasoning. Keep the user-facing comparison here and link implementation research in research.md or plan.md. Naming products here is expected; the validator exempts any section titled "Prior art" from the separation check.]

## 11. Assumptions and dependencies
[Assumptions about users and environment. External dependencies as capabilities, not products.]

## 12. Open intent questions
[Preserve all material unresolved needs. Use the installed native template's clarification-marker convention; move overflow into a linked issue list rather than losing source needs. Block only actions dependent on an unavailable decision.]
```

## Rules

Record explicit deployment constraints in section 3 and distinguish them from architecture proposals. Derive observable platform and non-functional acceptance in requirements/spec, with mechanisms in design/plan. Preserve failure outcomes and public acceptance. Do not erase user-named technology constraints to satisfy a token heuristic: cite their source and allowed exception. Goal changes begin in intent; corrections in behavior, architecture or workflow enter their owning layer and propagate to affected dependents. Preserve source prompts once and include or link the material source-disposition map.
