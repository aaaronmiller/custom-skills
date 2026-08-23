---
date: 2026-05-18 10:00:00 PDT
ver: 1.0.0
author: ice-ninja
model: claude-opus-4-7
tags: [strata, spec, template, eval-binding, contract]
---

# Spec Template (`spec.md`)

Author: the human, system may draft and human ratifies. Layer: Specification. This file is the evaluable contract and nothing else. Zero technology tokens. Zero prose that can be read a dozen ways.

## The single litmus

Every clause must be convertible into an evaluation that returns pass or fail. If a clause cannot become an eval, it is intent disguised as spec or it is noise. Kick it back to `intent.md` or delete it. A spec that describes rather than verifies is not a spec.

## Eval binding

Every clause carries an `EVAL-ID`. The evaluation it points at is stored outside the build tree, in an eval set the implementing agent does not see, for the same reason a separated test exists in a dark factory: an agent that can read the test it is graded on optimizes to pass the test, not to satisfy the intent. An unbound clause fails validation.

## EARS-style phrasing

Use the Easy Approach to Requirements Syntax so each clause collapses to one testable claim with no ambiguity about trigger, scope, or response. Forms: ubiquitous ("The system SHALL ..."), event-driven ("WHEN [trigger] the system SHALL ..."), state-driven ("WHILE [state] the system SHALL ..."), unwanted ("IF [condition] THEN the system SHALL ...").

## Template structure

```markdown
---
date: {{DATE}} {{TIME}} {{TZ}}
ver: 1.0.0
author: {{AUTHOR}}
model: {{MODEL}}
tags: [{{TAGS}}]
---

# [Project Name] Specification v1.0

## 1. Contract clauses

### 1.1 [Capability group]

**SPEC-001** [EVAL-001] WHEN [trigger] AND [precondition] THE system SHALL [observable response].
- Eval: [what the separated evaluation asserts, pass/fail, no implementation reference]
- Traces to: intent section [n]

**SPEC-002** [EVAL-002] THE system SHALL [ubiquitous testable behavior].
- Eval: [assertion]
- Traces to: intent section [n]

### 1.2 [Next capability group]

## 2. Acceptance scenarios
[Given / When / Then, each scenario bound to one or more EVAL-IDs. Cover happy path, the failure conditions named in intent section 6, and the boundaries named in intent section 8.]

## 3. Eval index
| EVAL-ID | Asserts | Bound clause | Stored at |
|---------|---------|--------------|-----------|
| EVAL-001 | ... | SPEC-001 | evals/ (outside build tree) |
```

## Rules

No technology. A framework name here is a defect. Every clause has a SPEC-ID and an EVAL-ID. Every clause traces to an intent section. Every failure condition in intent section 6 has at least one clause. Evals are described by what they assert, never by how they are implemented, and they live outside the build tree. If the human starts writing architecture into a clause, stop them; that is `context.md` and they do not own it.
