---
date: 2026-05-18 10:00:00 PDT
ver: 1.0.0
author: ice-ninja
model: claude-opus-4-7
tags: [spec-prep, spec, template, eval-binding, contract]
---

# Spec Template (`spec.md`)

Layer: Specification. Preserve the source authority of each requirement: direct user instruction, accepted decision or explicit proposal/inference. Authorized preparation can derive provisional observable clauses without creating implementation authority. Keep mechanisms in plan and retain genuine source-constrained platform/interface acceptance with cited layer exceptions. Write evaluable clauses and preserve native user scenarios; intent remains the source for goals/stories, not a reason to delete native template content.

## The single litmus

Every clause must be convertible into an evaluation that returns pass or fail. If an obligation is not yet evaluable, classify it as intent, a proposal or an unresolved requirement and preserve its source/disposition. Do not silently delete a material need. A specification may include explanatory context, but its contract clauses need observable acceptance.

## Eval binding

Every clause carries an `EVAL-ID` linked to a defined evaluation. Retain the external evaluation-definition store expected by the validator (default `~/.spec-prep/evals/<slug>/evals.md`); this storage convention does not establish held-out isolation. Public acceptance criteria and development tests remain available to the implementer. Use evaluator-only tests when appropriate and claim held-out evaluation only with actual file/tool access separation. An unbound clause fails validation; a bound identifier alone does not prove a useful test.

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
[Given / When / Then, each scenario bound to one or more EVAL-IDs. Cover happy path, the failure conditions named in intent section 6, and the boundaries named in intent section 9, and every user story in intent section 8.]

## 3. Eval index
| EVAL-ID | Asserts | Bound clause | Stored at |
|---------|---------|--------------|-----------|
| EVAL-001 | ... | SPEC-001 | evals/ (outside build tree) |
```

## Rules

Keep derived mechanisms in design/plan. Preserve explicit source-mandated platform/interface constraints with provenance and justified layer exceptions. Every clause has a SPEC-ID and an EVAL-ID and traces to intent. Cover material failure conditions and measurable quality obligations; keep their originating expectations in intent. Distinguish public acceptance from evaluator-only fixtures. Reclassify architecture proposals into the owning layer without erasing user authority.
