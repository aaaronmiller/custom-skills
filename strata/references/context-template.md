---
date: 2026-05-18 10:00:00 PDT
ver: 1.0.0
author: ice-ninja
model: claude-opus-4-7
tags: [strata, context, template, system-derived, architecture]
---

# Context Template (`context.md`)

Author: the system. Layer: Implementation. This file is derived, never hand-authored. A human writing a technology choice into this file by hand is the same defect as a human writing one into the spec. The validator does not block humans from editing it, but the methodology does: if you are typing the architecture, you are doing Context Crafting wrong.

## Derivation inputs, in order

1. Scale and constraints from `intent.md` sections 3 and 4.
2. Empirical memory from `ledger/` of any prior STRATA project in the workspace: what architecture was chosen under what constraints and what the recorded outcome was.
3. The existing stack the project must live in.
4. Risk tolerance from `intent.md`.

Every decision in this file cites the intent input and, where it exists, the ledger entry that drove it. A decision with no citation is guesswork wearing a citation's clothes; mark it as such.

## The empty-ledger honesty rule

On a project with no prior ledger, there is no empirical memory. Context Crafting then degrades toward architect intuition. Do not hide this. State it in this file and in `substrate.md`. The differentiator is accumulated history; on day one you have none, and pretending otherwise is the failure mode the paradigm exists to prevent.

## Template structure

```markdown
---
date: {{DATE}} {{TIME}} {{TZ}}
ver: 1.0.0
author: {{AUTHOR}} (system-derived)
model: {{MODEL}}
tags: [{{TAGS}}]
---

# [Project Name] Context v1.0 (derived)

## 1. Derivation summary
[One paragraph: which intent constraints and which ledger entries shaped this architecture. State explicitly if the ledger was empty.]

## 2. Architecture overview
[ASCII diagram. Highest-level component view.]

## 3. Decisions
**CTX-001: [decision, e.g. single-node relational store]**
- Derived from: intent section 4 (peak concurrency [n]), intent section 3 (data residency [x])
- Memory: ledger entry [id] (prior project at similar scale chose [y], outcome [z]) OR "no empirical memory, intuition-based"
- Options considered: [2 to 3]
- Trade-offs accepted: [what is given up]

## 4. Data model
[Schema with concrete types, access patterns, migration strategy. Per references/data-architecture-guide.md.]

## 5. Component specifications
[Per component: responsibility, interface, dependencies, failure surfacing.]

## 6. Hosting and deployment
[Derived from the deployment constraint in intent section 3. If that constraint changes, this section is regenerated and the delta is appended to the ledger.]

## 7. Security
[Threat model, auth, data protection, supply-chain audit strategy.]

## 8. Build phases
[Phase and step notation only, no dates. Each phase validates specific SPEC-IDs.]

## 9. Project structure
[Directory layout with the organizing principle justified.]
```

## Rules

Every decision cites its intent input. Every decision states its memory source or admits it has none. The deployment section is downstream of the intent constraint; on a pivot it is regenerated, not patched, and the delta goes to the ledger. No requirement appears here that is not present in intent or spec. Phases use phase and step notation, never dates.
