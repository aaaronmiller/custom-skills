# Drift Taxonomy Reference

## Primary classifications

### CONFIRMED

The downstream artifact preserves the upstream obligation.

Action: no change.

### LOST-INTENT

A product or technical obligation exists upstream but is absent downstream.

Action: restore the missing obligation in the downstream artifact or add implementation tasks.

### INVENTED-SCOPE

The downstream artifact adds behavior, actors, integrations, data, or UX not supported upstream.

Action: remove it or explicitly promote it to requirements/design after user approval.

### WEAKENED-CONSTRAINT

The downstream artifact keeps the general idea but drops or softens a hard limit.

Action: restore the constraint and revise affected tasks/design.

### NON-GOAL-VIOLATION

The downstream artifact implies work that the upstream artifact explicitly excluded.

Action: remove downstream work unless user intentionally changes scope.

### ACCEPTANCE-GAP

A requirement exists but has no observable pass/fail signal, acceptance scenario, test implication, or quickstart validation.

Action: add acceptance criteria, scenario, quickstart validation, or test task.

### DESIGN-DRIFT

The generated plan or task decomposition no longer matches the technical design.

Action: revise plan/tasks or revise `design.md` if the new approach is intentionally better.

### RATIONALE-GAP

A design choice survives, but the reason and tradeoff disappear.

Action: document rationale in `plan.md`, `research.md`, or design notes.

### TASK-GAP

A required obligation has no implementation task.

Action: add one or more concrete tasks.

### ORPHAN-TASK

A task does not map to a requirement, design obligation, setup need, or validation need.

Action: remove, justify, or promote to requirement/design.

### ORDERING-RISK

Tasks are present but in an order that creates rework, invalid dependencies, or non-independent increments.

Action: reorder tasks or split foundational prerequisites.

### IMPLEMENTATION-CONTAMINATION

Product requirements or user-facing specs contain implementation detail too early.

Action: move implementation detail into `design.md` or `plan.md` unless it is a genuine product constraint.

### AMBIGUOUS-SOURCE

The upstream source is too vague to fairly judge downstream drift.

Action: clarify source before blaming generated artifacts.

## Severity rules

### CRITICAL

Use when the issue violates:

- project constitution
- hard security/privacy boundary
- core user promise
- legal/compliance requirement
- irreversible destructive behavior safeguard
- data integrity guarantee

### HIGH

Use when the issue affects:

- required behavior
- required user story
- acceptance criteria
- architecture
- data model
- interface contract
- performance constraint
- task coverage for required work

### MEDIUM

Use when the issue affects:

- rationale
- sequencing
- optional scope
- ambiguous assumptions
- missing traceability
- test completeness but not core behavior

### LOW

Use for:

- naming mismatches
- editorial clarity
- minor duplication
- non-blocking documentation polish

## Report phrasing pattern

Use this pattern for each finding:

```text
[F-###] [SEVERITY] [CLASSIFICATION] Title
Source of truth: <file/section>
Downstream artifact: <file/section>
What drifted: <specific change/loss/invention>
Why it matters: <impact>
Recommended fix: <specific edit or task>
```
