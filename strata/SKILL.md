---
name: strata
description: ALWAYS invoke when the user wants to start a new project, define a feature,
  turn a brain dump or transcript into build-ready specifications, or set up a spec-driven
  or intent-driven workflow. Triggers on "new project", "new idea", "build this",
  "spec this out", "turn this into a spec", "process these transcripts", "idea to
  spec", "kickoff", "greenfield", "from scratch", "write a PRD", "feature spec", "spec-driven",
  "speckit", "openspec", "kiro", "intent-driven", "spec is collapsing", "vibe vs spec",
  or whenever transcripts or notes describing something to build are provided. Also
  triggers when preparing files for SpecKit, OpenSpec, Kiro, or any spec-driven tool.
  Supersedes plain spec-driven scaffolding by separating intent, specification, and
  implementation into distinct authored layers plus a continuity ledger so projects
  survive upstream pivots and long dormancy without rework. Do NOT use for modifying
  an already-scaffolded STRATA tree, code review, debugging, or ongoing implementation
  work.
license: MIT
metadata:
  author: ice-ninja
  version: 1.0.0
tags:
- planning
- automation
- coding
grade: A
source: custom
---

# STRATA

> Separation of Tiers, Retention Across Time, Auditability. From brain dump to build-ready, pivot-resilient, dormancy-proof artifacts in one session.

STRATA is the operational discipline that supersedes single-document spec-driven scaffolding. It transforms raw ideas, transcripts, or interactive discussion into a fixed six-artifact tree where intent, specification, and implementation are separated by author and a continuity ledger keeps the project from going into a dreamstate. Output is compatible with SpecKit, OpenSpec, Kiro, Cursor, and any agent that reads markdown.

## Why this exists

Vibe coding collapses because it has no contract. Spec-driven development collapses because it has three contracts pretending to be one: it buries intent inside the spec, pre-locks architecture at the top, and has no answer for continuity across time. STRATA fixes both by enforcing layer separation with a validator and by treating the system's memory of where it is standing as a first-class, load-bearing artifact, not a feature.

Read `references/paradigm.md` for the full conceptual model before generating artifacts if the conceptual basis is unclear. It is the spine; the rest of this file is the procedure.

## The six artifacts (plus one)

STRATA writes a `strata/{project-name}/` tree. Each artifact has exactly one author and is allowed to change without detonating the others.

| Artifact | Layer | Author | Maps to |
|----------|-------|--------|---------|
| `intent.md` | Intent | Human | SpecKit spec.md (why + constraints + NFRs), the part that drives architecture |
| `spec.md` | Specification | Human (system may draft) | SpecKit spec.md (testable what only) |
| `context.md` | Implementation | System (derived, never hand-authored) | SpecKit plan.md / OpenSpec design.md |
| `plays/` | Prompt | System | SpecKit tasks.md, but intent-encoded not target-encoded |
| `ledger/` | Continuity | System (append-only) | No SpecKit equivalent. This is the differentiator. |
| `constitution.md` | Governance | Human (never generated from scratch) | SpecKit constitution |
| `substrate.md` | Self-location | Human | No equivalent. Honest level + pre-lock declaration. |

The litmus rules, templates, and field-by-field structure for each artifact live in `references/`. Read the relevant reference before writing that artifact.

## The six rules (enforced, not suggested)

1. **Separation.** `intent.md` is not `spec.md` is not `context.md`. A technology, framework, or library token appearing in `intent.md` or `spec.md` is a defect. A `spec.md` clause that cannot be converted into a pass/fail evaluation is a defect. The validator fails the build on either.
2. **Authorship.** The human authors intent and spec. The system authors context and plays. Never hand-author a technology choice into intent or spec. Never ask the human to choose an architecture for `context.md`.
3. **Eval binding.** Every `spec.md` clause carries an `EVAL-ID` bound to an evaluation stored outside the build tree. Unbound clauses fail validation. Evals visible to the implementing agent are treated as compromised.
4. **Pivot.** Upstream change enters at `intent.md` only. The system re-derives `context.md`, records the delta in the ledger, and leaves plays untouched. Never propagate a pivot by editing tasks.
5. **Continuity.** Every decision and its outcome is appended to the ledger and `standing.md` is updated, every time, not only at milestones. A revived session reconstructs from the ledger before touching code.
6. **Honesty.** `substrate.md` states the real substrate level and the real pre-lock versus live-resolve boundary. Do not record certainty the project has not earned.

## Confidence Gate

Before generating any artifact, intake must reach **85% confidence** across ten dimensions (the original eight plus two STRATA-specific). Score conservatively. One extra question round costs minutes; a fused-layer artifact costs hours. The full rubric is in `references/confidence-gate.md`. Summary of dimensions and weights: Problem clarity (12%), Solution definition (12%), User personas (8%), Success criteria (10%), Data model (12%), Scope boundaries (8%), Technical constraints (10%), Business context (10%), **Layer-separation integrity (10%)** (can intent, spec, and implementation concerns be cleanly told apart in what the user has said, or are they fused), **Continuity readiness (8%)** (is there enough to seed the ledger and a first `standing.md`). Below 85%, ask 3 to 5 targeted questions on the lowest-scoring dimensions and reassess. Do not proceed until the threshold is met and the user confirms a one-paragraph understanding summary.

## Execution Protocol

### Phase 0: Mode detection and setup

Detect intake mode. Files or transcripts provided is Transcript mode. A verbal description or "I want to build X" is Interactive mode. Mixed is Transcript first, then Interactive gap-fill. If the user provides a complete, well-structured description covering problem, solution, users, data, constraints, and scope, run the Fast Track: score the Confidence Gate once, and if it clears 85% on the first pass proceed directly to Phase 2.

Load references as needed: `references/paradigm.md` for the model, the four artifact references for output structure, `references/research-checklist.md` for Phase 2, `references/data-architecture-guide.md` for Phase 3. Check for existing spec infrastructure (`.specify/`, `openspec/`, `.kiro/`, `strata/`) and existing `constitution.md`. If a `strata/` tree already exists, this skill does not apply; the user wants ongoing work, not a kickoff.

### Phase 1: Intake and extraction

Transcript mode: read everything, extract problem statements, proposed solutions, personas, success and failure conditions, constraints, scale and quality expectations, implied data entities, integration points, and workflow descriptions. Critically, tag every extracted signal as intent, spec, or implementation, because the user will have fused them and the separation starts here. Compute the Confidence Gate score.

Interactive mode: run a structured discovery conversation. Do not ask everything at once. Proceed through Problem Space, Solution Vision, Users and Adoption, Data and State, Technical Constraints, UX and Interaction, Business and Distribution, asking 2 to 4 questions per category and reassessing the gate after each. Use the structured-question tool when available so the user taps rather than types. The full category question bank is in `references/discovery-questions.md`.

For both modes, when confidence is below 85%, switch to targeted gap-fill on the lowest dimensions. When at or above, confirm understanding in one paragraph and proceed.

### Phase 2: Prior art research (mandatory)

Follow `references/research-checklist.md` in full. Local workspace scan first, then skill registries, then a minimum of three code searches and two web searches, then synthesis. If an existing tool fully solves the problem, stop and surface it before proceeding. Research findings are recorded in `intent.md` under Prior Art, never in a separate scratch file. Always survey how others approached the problem and extract reusable patterns and documented pitfalls.

### Phase 3: Context derivation (system-owned)

This is not a design-authoring step. The system derives the architecture from `intent.md`. Read scale and constraints out of intent, read the empirical memory out of `ledger/` if any prior STRATA project exists in the workspace, read the existing stack and risk tolerance, then apply `references/data-architecture-guide.md` to produce data, hosting, and security decisions. Every decision in `context.md` cites the intent input and, where available, the ledger entry that drove it. On a project with an empty ledger, state explicitly in `substrate.md` that Context Crafting is operating without empirical memory and is therefore closer to architect guesswork. Do not hide the gap.

### Phase 4: Artifact generation

Generate the tree in this order, reading the matching reference immediately before each:

1. `intent.md` using `references/intent-template.md`. Human-owned content, no technology tokens, NFRs and scale and failure conditions included because they drive architecture.
2. `spec.md` using `references/spec-template.md`. Every clause testable, every clause carrying an `EVAL-ID`, zero technology tokens.
3. `context.md` using `references/context-template.md`. System-derived, every decision cited back to intent and memory.
4. `plays/` using `references/plays-playbook.md`. Intent-encoded reusable patterns, never target-coupled. Include at minimum a scaffold play, a commit play, and a deploy play.
5. `ledger/ledger.md` and `ledger/standing.md` using `references/ledger-and-standing.md`. Seed the ledger with the kickoff decisions and write the first `standing.md`.
6. `substrate.md` using `references/substrate-self-location.md`. Declare the honest level and the pre-lock boundary.
7. `constitution.md`: include the user's existing constitution as a reference if present. If absent, do not generate one. Note its absence and tell the user to create one through SpecKit or OpenSpec tooling.

### Phase 5: Deliverative refinement

Invoke the deliberative-refinement skill on the human-authored layers. Run an Expert Council pass on `intent.md` and `spec.md` together checking completeness, testability, ambiguity, fused layers, and scope creep. Run a Structured Review pass on `context.md` checking that every spec clause is supported by the architecture and that nothing in context introduces a requirement absent from intent or spec. Cross-validate: every spec clause traces to an intent statement, every context decision traces to a spec clause or an intent constraint, every play reads its variables from intent rather than hard-coding them. Apply the refinements and append the refinement decisions to the ledger.

### Phase 6: Validation, delivery, handoff

Run `scripts/strata-validate.py` against the tree. It fails on technology tokens in intent or spec, on unbound spec clauses, on a missing or empty ledger or `standing.md`, and on a `substrate.md` that does not declare a level. Fix every failure before delivery. Present the tree, give a delivery summary stating the confidence score and any sub-threshold dimensions, the declared substrate level, key derived decisions and their rationale, any `[NEEDS CLARIFICATION]` markers, and the prior-art findings. Tell the user the handoff path: a fresh session loads `standing.md` and the ledger tail first, then `intent.md` and `spec.md`, then proceeds, and never needs this conversation's context. Provide next-step commands for their toolchain (SpecKit, OpenSpec, Kiro, or direct agent use); the mapping is in `references/compatibility.md`.

## Anti-patterns

Never fuse layers: no technology in intent or spec, no human-authored architecture in context. Never write a spec clause that cannot become an eval. Never let an eval be visible to the implementing agent. Never propagate a pivot through plays or tasks; it enters at intent only. Never skip the ledger or write it only at milestones. Never generate a constitution from scratch. Never inflate the Confidence Gate to skip a question round. Never claim a substrate level the project has not earned. Never write research or exploration notes into output files; prior art goes in `intent.md`, process notes go nowhere. Never use dates or timestamps in plays or phases; use phase and step notation. Never ask every discovery question in one message.

## Resource files

| File | Read when |
|------|-----------|
| `references/paradigm.md` | Before generating, if the conceptual model is unclear |
| `references/intent-template.md` | Phase 4, writing `intent.md` |
| `references/spec-template.md` | Phase 4, writing `spec.md` |
| `references/context-template.md` | Phase 3 and 4, deriving `context.md` |
| `references/plays-playbook.md` | Phase 4, writing `plays/` |
| `references/ledger-and-standing.md` | Phase 4, seeding continuity |
| `references/substrate-self-location.md` | Phase 4, writing `substrate.md` |
| `references/confidence-gate.md` | Phase 1, scoring intake |
| `references/discovery-questions.md` | Phase 1, Interactive mode |
| `references/research-checklist.md` | Phase 2, prior art |
| `references/data-architecture-guide.md` | Phase 3, context derivation |
| `references/compatibility.md` | Phase 6, toolchain handoff |
| `scripts/strata-scaffold.sh` | To create an empty tree before filling it |
| `scripts/strata-validate.py` | Phase 6, enforce the six rules |
| `scripts/strata-revive.sh` | Any time a dormant project must be resumed |


# STRATA

> Separation of Tiers, Retention Across Time, Auditability. From brain dump to build-ready, pivot-resilient, dormancy-proof artifacts in one session.

STRATA is the operational discipline that supersedes single-document spec-driven scaffolding. It transforms raw ideas, transcripts, or interactive discussion into a fixed six-artifact tree where intent, specification, and implementation are separated by author and a continuity ledger keeps the project from going into a dreamstate. Output is compatible with SpecKit, OpenSpec, Kiro, Cursor, and any agent that reads markdown.

## Why this exists

Vibe coding collapses because it has no contract. Spec-driven development collapses because it has three contracts pretending to be one: it buries intent inside the spec, pre-locks architecture at the top, and has no answer for continuity across time. STRATA fixes both by enforcing layer separation with a validator and by treating the system's memory of where it is standing as a first-class, load-bearing artifact, not a feature.

Read `references/paradigm.md` for the full conceptual model before generating artifacts if the conceptual basis is unclear. It is the spine; the rest of this file is the procedure.

## The six artifacts (plus one)

STRATA writes a `strata/{project-name}/` tree. Each artifact has exactly one author and is allowed to change without detonating the others.

| Artifact | Layer | Author | Maps to |
|----------|-------|--------|---------|
| `intent.md` | Intent | Human | SpecKit spec.md (why + constraints + NFRs), the part that drives architecture |
| `spec.md` | Specification | Human (system may draft) | SpecKit spec.md (testable what only) |
| `context.md` | Implementation | System (derived, never hand-authored) | SpecKit plan.md / OpenSpec design.md |
| `plays/` | Prompt | System | SpecKit tasks.md, but intent-encoded not target-encoded |
| `ledger/` | Continuity | System (append-only) | No SpecKit equivalent. This is the differentiator. |
| `constitution.md` | Governance | Human (never generated from scratch) | SpecKit constitution |
| `substrate.md` | Self-location | Human | No equivalent. Honest level + pre-lock declaration. |

The litmus rules, templates, and field-by-field structure for each artifact live in `references/`. Read the relevant reference before writing that artifact.

## The six rules (enforced, not suggested)

1. **Separation.** `intent.md` is not `spec.md` is not `context.md`. A technology, framework, or library token appearing in `intent.md` or `spec.md` is a defect. A `spec.md` clause that cannot be converted into a pass/fail evaluation is a defect. The validator fails the build on either.
2. **Authorship.** The human authors intent and spec. The system authors context and plays. Never hand-author a technology choice into intent or spec. Never ask the human to choose an architecture for `context.md`.
3. **Eval binding.** Every `spec.md` clause carries an `EVAL-ID` bound to an evaluation stored outside the build tree. Unbound clauses fail validation. Evals visible to the implementing agent are treated as compromised.
4. **Pivot.** Upstream change enters at `intent.md` only. The system re-derives `context.md`, records the delta in the ledger, and leaves plays untouched. Never propagate a pivot by editing tasks.
5. **Continuity.** Every decision and its outcome is appended to the ledger and `standing.md` is updated, every time, not only at milestones. A revived session reconstructs from the ledger before touching code.
6. **Honesty.** `substrate.md` states the real substrate level and the real pre-lock versus live-resolve boundary. Do not record certainty the project has not earned.

## Confidence Gate

Before generating any artifact, intake must reach **85% confidence** across ten dimensions (the original eight plus two STRATA-specific). Score conservatively. One extra question round costs minutes; a fused-layer artifact costs hours. The full rubric is in `references/confidence-gate.md`. Summary of dimensions and weights: Problem clarity (12%), Solution definition (12%), User personas (8%), Success criteria (10%), Data model (12%), Scope boundaries (8%), Technical constraints (10%), Business context (10%), **Layer-separation integrity (10%)** (can intent, spec, and implementation concerns be cleanly told apart in what the user has said, or are they fused), **Continuity readiness (8%)** (is there enough to seed the ledger and a first `standing.md`). Below 85%, ask 3 to 5 targeted questions on the lowest-scoring dimensions and reassess. Do not proceed until the threshold is met and the user confirms a one-paragraph understanding summary.

## Execution Protocol

### Phase 0: Mode detection and setup

Detect intake mode. Files or transcripts provided is Transcript mode. A verbal description or "I want to build X" is Interactive mode. Mixed is Transcript first, then Interactive gap-fill. If the user provides a complete, well-structured description covering problem, solution, users, data, constraints, and scope, run the Fast Track: score the Confidence Gate once, and if it clears 85% on the first pass proceed directly to Phase 2.

Load references as needed: `references/paradigm.md` for the model, the four artifact references for output structure, `references/research-checklist.md` for Phase 2, `references/data-architecture-guide.md` for Phase 3. Check for existing spec infrastructure (`.specify/`, `openspec/`, `.kiro/`, `strata/`) and existing `constitution.md`. If a `strata/` tree already exists, this skill does not apply; the user wants ongoing work, not a kickoff.

### Phase 1: Intake and extraction

Transcript mode: read everything, extract problem statements, proposed solutions, personas, success and failure conditions, constraints, scale and quality expectations, implied data entities, integration points, and workflow descriptions. Critically, tag every extracted signal as intent, spec, or implementation, because the user will have fused them and the separation starts here. Compute the Confidence Gate score.

Interactive mode: run a structured discovery conversation. Do not ask everything at once. Proceed through Problem Space, Solution Vision, Users and Adoption, Data and State, Technical Constraints, UX and Interaction, Business and Distribution, asking 2 to 4 questions per category and reassessing the gate after each. Use the structured-question tool when available so the user taps rather than types. The full category question bank is in `references/discovery-questions.md`.

For both modes, when confidence is below 85%, switch to targeted gap-fill on the lowest dimensions. When at or above, confirm understanding in one paragraph and proceed.

### Phase 2: Prior art research (mandatory)

Follow `references/research-checklist.md` in full. Local workspace scan first, then skill registries, then a minimum of three code searches and two web searches, then synthesis. If an existing tool fully solves the problem, stop and surface it before proceeding. Research findings are recorded in `intent.md` under Prior Art, never in a separate scratch file. Always survey how others approached the problem and extract reusable patterns and documented pitfalls.

### Phase 3: Context derivation (system-owned)

This is not a design-authoring step. The system derives the architecture from `intent.md`. Read scale and constraints out of intent, read the empirical memory out of `ledger/` if any prior STRATA project exists in the workspace, read the existing stack and risk tolerance, then apply `references/data-architecture-guide.md` to produce data, hosting, and security decisions. Every decision in `context.md` cites the intent input and, where available, the ledger entry that drove it. On a project with an empty ledger, state explicitly in `substrate.md` that Context Crafting is operating without empirical memory and is therefore closer to architect guesswork. Do not hide the gap.

### Phase 4: Artifact generation

Generate the tree in this order, reading the matching reference immediately before each:

1. `intent.md` using `references/intent-template.md`. Human-owned content, no technology tokens, NFRs and scale and failure conditions included because they drive architecture.
2. `spec.md` using `references/spec-template.md`. Every clause testable, every clause carrying an `EVAL-ID`, zero technology tokens.
3. `context.md` using `references/context-template.md`. System-derived, every decision cited back to intent and memory.
4. `plays/` using `references/plays-playbook.md`. Intent-encoded reusable patterns, never target-coupled. Include at minimum a scaffold play, a commit play, and a deploy play.
5. `ledger/ledger.md` and `ledger/standing.md` using `references/ledger-and-standing.md`. Seed the ledger with the kickoff decisions and write the first `standing.md`.
6. `substrate.md` using `references/substrate-self-location.md`. Declare the honest level and the pre-lock boundary.
7. `constitution.md`: include the user's existing constitution as a reference if present. If absent, do not generate one. Note its absence and tell the user to create one through SpecKit or OpenSpec tooling.

### Phase 5: Deliverative refinement

Invoke the deliberative-refinement skill on the human-authored layers. Run an Expert Council pass on `intent.md` and `spec.md` together checking completeness, testability, ambiguity, fused layers, and scope creep. Run a Structured Review pass on `context.md` checking that every spec clause is supported by the architecture and that nothing in context introduces a requirement absent from intent or spec. Cross-validate: every spec clause traces to an intent statement, every context decision traces to a spec clause or an intent constraint, every play reads its variables from intent rather than hard-coding them. Apply the refinements and append the refinement decisions to the ledger.

### Phase 6: Validation, delivery, handoff

Run `scripts/strata-validate.py` against the tree. It fails on technology tokens in intent or spec, on unbound spec clauses, on a missing or empty ledger or `standing.md`, and on a `substrate.md` that does not declare a level. Fix every failure before delivery. Present the tree, give a delivery summary stating the confidence score and any sub-threshold dimensions, the declared substrate level, key derived decisions and their rationale, any `[NEEDS CLARIFICATION]` markers, and the prior-art findings. Tell the user the handoff path: a fresh session loads `standing.md` and the ledger tail first, then `intent.md` and `spec.md`, then proceeds, and never needs this conversation's context. Provide next-step commands for their toolchain (SpecKit, OpenSpec, Kiro, or direct agent use); the mapping is in `references/compatibility.md`.

## Anti-patterns

Never fuse layers: no technology in intent or spec, no human-authored architecture in context. Never write a spec clause that cannot become an eval. Never let an eval be visible to the implementing agent. Never propagate a pivot through plays or tasks; it enters at intent only. Never skip the ledger or write it only at milestones. Never generate a constitution from scratch. Never inflate the Confidence Gate to skip a question round. Never claim a substrate level the project has not earned. Never write research or exploration notes into output files; prior art goes in `intent.md`, process notes go nowhere. Never use dates or timestamps in plays or phases; use phase and step notation. Never ask every discovery question in one message.

## Resource files

| File | Read when |
|------|-----------|
| `references/paradigm.md` | Before generating, if the conceptual model is unclear |
| `references/intent-template.md` | Phase 4, writing `intent.md` |
| `references/spec-template.md` | Phase 4, writing `spec.md` |
| `references/context-template.md` | Phase 3 and 4, deriving `context.md` |
| `references/plays-playbook.md` | Phase 4, writing `plays/` |
| `references/ledger-and-standing.md` | Phase 4, seeding continuity |
| `references/substrate-self-location.md` | Phase 4, writing `substrate.md` |
| `references/confidence-gate.md` | Phase 1, scoring intake |
| `references/discovery-questions.md` | Phase 1, Interactive mode |
| `references/research-checklist.md` | Phase 2, prior art |
| `references/data-architecture-guide.md` | Phase 3, context derivation |
| `references/compatibility.md` | Phase 6, toolchain handoff |
| `scripts/strata-scaffold.sh` | To create an empty tree before filling it |
| `scripts/strata-validate.py` | Phase 6, enforce the six rules |
| `scripts/strata-revive.sh` | Any time a dormant project must be resumed |


# STRATA

> Separation of Tiers, Retention Across Time, Auditability. From brain dump to build-ready, pivot-resilient, dormancy-proof artifacts in one session.

STRATA is the operational discipline that supersedes single-document spec-driven scaffolding. It transforms raw ideas, transcripts, or interactive discussion into a fixed six-artifact tree where intent, specification, and implementation are separated by author and a continuity ledger keeps the project from going into a dreamstate. Output is compatible with SpecKit, OpenSpec, Kiro, Cursor, and any agent that reads markdown.

## Why this exists

Vibe coding collapses because it has no contract. Spec-driven development collapses because it has three contracts pretending to be one: it buries intent inside the spec, pre-locks architecture at the top, and has no answer for continuity across time. STRATA fixes both by enforcing layer separation with a validator and by treating the system's memory of where it is standing as a first-class, load-bearing artifact, not a feature.

Read `references/paradigm.md` for the full conceptual model before generating artifacts if the conceptual basis is unclear. It is the spine; the rest of this file is the procedure.

## The six artifacts (plus one)

STRATA writes a `strata/{project-name}/` tree. Each artifact has exactly one author and is allowed to change without detonating the others.

| Artifact | Layer | Author | Maps to |
|----------|-------|--------|---------|
| `intent.md` | Intent | Human | SpecKit spec.md (why + constraints + NFRs), the part that drives architecture |
| `spec.md` | Specification | Human (system may draft) | SpecKit spec.md (testable what only) |
| `context.md` | Implementation | System (derived, never hand-authored) | SpecKit plan.md / OpenSpec design.md |
| `plays/` | Prompt | System | SpecKit tasks.md, but intent-encoded not target-encoded |
| `ledger/` | Continuity | System (append-only) | No SpecKit equivalent. This is the differentiator. |
| `constitution.md` | Governance | Human (never generated from scratch) | SpecKit constitution |
| `substrate.md` | Self-location | Human | No equivalent. Honest level + pre-lock declaration. |

The litmus rules, templates, and field-by-field structure for each artifact live in `references/`. Read the relevant reference before writing that artifact.

## The six rules (enforced, not suggested)

1. **Separation.** `intent.md` is not `spec.md` is not `context.md`. A technology, framework, or library token appearing in `intent.md` or `spec.md` is a defect. A `spec.md` clause that cannot be converted into a pass/fail evaluation is a defect. The validator fails the build on either.
2. **Authorship.** The human authors intent and spec. The system authors context and plays. Never hand-author a technology choice into intent or spec. Never ask the human to choose an architecture for `context.md`.
3. **Eval binding.** Every `spec.md` clause carries an `EVAL-ID` bound to an evaluation stored outside the build tree. Unbound clauses fail validation. Evals visible to the implementing agent are treated as compromised.
4. **Pivot.** Upstream change enters at `intent.md` only. The system re-derives `context.md`, records the delta in the ledger, and leaves plays untouched. Never propagate a pivot by editing tasks.
5. **Continuity.** Every decision and its outcome is appended to the ledger and `standing.md` is updated, every time, not only at milestones. A revived session reconstructs from the ledger before touching code.
6. **Honesty.** `substrate.md` states the real substrate level and the real pre-lock versus live-resolve boundary. Do not record certainty the project has not earned.

## Confidence Gate

Before generating any artifact, intake must reach **85% confidence** across ten dimensions (the original eight plus two STRATA-specific). Score conservatively. One extra question round costs minutes; a fused-layer artifact costs hours. The full rubric is in `references/confidence-gate.md`. Summary of dimensions and weights: Problem clarity (12%), Solution definition (12%), User personas (8%), Success criteria (10%), Data model (12%), Scope boundaries (8%), Technical constraints (10%), Business context (10%), **Layer-separation integrity (10%)** (can intent, spec, and implementation concerns be cleanly told apart in what the user has said, or are they fused), **Continuity readiness (8%)** (is there enough to seed the ledger and a first `standing.md`). Below 85%, ask 3 to 5 targeted questions on the lowest-scoring dimensions and reassess. Do not proceed until the threshold is met and the user confirms a one-paragraph understanding summary.

## Execution Protocol

### Phase 0: Mode detection and setup

Detect intake mode. Files or transcripts provided is Transcript mode. A verbal description or "I want to build X" is Interactive mode. Mixed is Transcript first, then Interactive gap-fill. If the user provides a complete, well-structured description covering problem, solution, users, data, constraints, and scope, run the Fast Track: score the Confidence Gate once, and if it clears 85% on the first pass proceed directly to Phase 2.

Load references as needed: `references/paradigm.md` for the model, the four artifact references for output structure, `references/research-checklist.md` for Phase 2, `references/data-architecture-guide.md` for Phase 3. Check for existing spec infrastructure (`.specify/`, `openspec/`, `.kiro/`, `strata/`) and existing `constitution.md`. If a `strata/` tree already exists, this skill does not apply; the user wants ongoing work, not a kickoff.

### Phase 1: Intake and extraction

Transcript mode: read everything, extract problem statements, proposed solutions, personas, success and failure conditions, constraints, scale and quality expectations, implied data entities, integration points, and workflow descriptions. Critically, tag every extracted signal as intent, spec, or implementation, because the user will have fused them and the separation starts here. Compute the Confidence Gate score.

Interactive mode: run a structured discovery conversation. Do not ask everything at once. Proceed through Problem Space, Solution Vision, Users and Adoption, Data and State, Technical Constraints, UX and Interaction, Business and Distribution, asking 2 to 4 questions per category and reassessing the gate after each. Use the structured-question tool when available so the user taps rather than types. The full category question bank is in `references/discovery-questions.md`.

For both modes, when confidence is below 85%, switch to targeted gap-fill on the lowest dimensions. When at or above, confirm understanding in one paragraph and proceed.

### Phase 2: Prior art research (mandatory)

Follow `references/research-checklist.md` in full. Local workspace scan first, then skill registries, then a minimum of three code searches and two web searches, then synthesis. If an existing tool fully solves the problem, stop and surface it before proceeding. Research findings are recorded in `intent.md` under Prior Art, never in a separate scratch file. Always survey how others approached the problem and extract reusable patterns and documented pitfalls.

### Phase 3: Context derivation (system-owned)

This is not a design-authoring step. The system derives the architecture from `intent.md`. Read scale and constraints out of intent, read the empirical memory out of `ledger/` if any prior STRATA project exists in the workspace, read the existing stack and risk tolerance, then apply `references/data-architecture-guide.md` to produce data, hosting, and security decisions. Every decision in `context.md` cites the intent input and, where available, the ledger entry that drove it. On a project with an empty ledger, state explicitly in `substrate.md` that Context Crafting is operating without empirical memory and is therefore closer to architect guesswork. Do not hide the gap.

### Phase 4: Artifact generation

Generate the tree in this order, reading the matching reference immediately before each:

1. `intent.md` using `references/intent-template.md`. Human-owned content, no technology tokens, NFRs and scale and failure conditions included because they drive architecture.
2. `spec.md` using `references/spec-template.md`. Every clause testable, every clause carrying an `EVAL-ID`, zero technology tokens.
3. `context.md` using `references/context-template.md`. System-derived, every decision cited back to intent and memory.
4. `plays/` using `references/plays-playbook.md`. Intent-encoded reusable patterns, never target-coupled. Include at minimum a scaffold play, a commit play, and a deploy play.
5. `ledger/ledger.md` and `ledger/standing.md` using `references/ledger-and-standing.md`. Seed the ledger with the kickoff decisions and write the first `standing.md`.
6. `substrate.md` using `references/substrate-self-location.md`. Declare the honest level and the pre-lock boundary.
7. `constitution.md`: include the user's existing constitution as a reference if present. If absent, do not generate one. Note its absence and tell the user to create one through SpecKit or OpenSpec tooling.

### Phase 5: Deliverative refinement

Invoke the deliberative-refinement skill on the human-authored layers. Run an Expert Council pass on `intent.md` and `spec.md` together checking completeness, testability, ambiguity, fused layers, and scope creep. Run a Structured Review pass on `context.md` checking that every spec clause is supported by the architecture and that nothing in context introduces a requirement absent from intent or spec. Cross-validate: every spec clause traces to an intent statement, every context decision traces to a spec clause or an intent constraint, every play reads its variables from intent rather than hard-coding them. Apply the refinements and append the refinement decisions to the ledger.

### Phase 6: Validation, delivery, handoff

Run `scripts/strata-validate.py` against the tree. It fails on technology tokens in intent or spec, on unbound spec clauses, on a missing or empty ledger or `standing.md`, and on a `substrate.md` that does not declare a level. Fix every failure before delivery. Present the tree, give a delivery summary stating the confidence score and any sub-threshold dimensions, the declared substrate level, key derived decisions and their rationale, any `[NEEDS CLARIFICATION]` markers, and the prior-art findings. Tell the user the handoff path: a fresh session loads `standing.md` and the ledger tail first, then `intent.md` and `spec.md`, then proceeds, and never needs this conversation's context. Provide next-step commands for their toolchain (SpecKit, OpenSpec, Kiro, or direct agent use); the mapping is in `references/compatibility.md`.

## Anti-patterns

Never fuse layers: no technology in intent or spec, no human-authored architecture in context. Never write a spec clause that cannot become an eval. Never let an eval be visible to the implementing agent. Never propagate a pivot through plays or tasks; it enters at intent only. Never skip the ledger or write it only at milestones. Never generate a constitution from scratch. Never inflate the Confidence Gate to skip a question round. Never claim a substrate level the project has not earned. Never write research or exploration notes into output files; prior art goes in `intent.md`, process notes go nowhere. Never use dates or timestamps in plays or phases; use phase and step notation. Never ask every discovery question in one message.

## Resource files

| File | Read when |
|------|-----------|
| `references/paradigm.md` | Before generating, if the conceptual model is unclear |
| `references/intent-template.md` | Phase 4, writing `intent.md` |
| `references/spec-template.md` | Phase 4, writing `spec.md` |
| `references/context-template.md` | Phase 3 and 4, deriving `context.md` |
| `references/plays-playbook.md` | Phase 4, writing `plays/` |
| `references/ledger-and-standing.md` | Phase 4, seeding continuity |
| `references/substrate-self-location.md` | Phase 4, writing `substrate.md` |
| `references/confidence-gate.md` | Phase 1, scoring intake |
| `references/discovery-questions.md` | Phase 1, Interactive mode |
| `references/research-checklist.md` | Phase 2, prior art |
| `references/data-architecture-guide.md` | Phase 3, context derivation |
| `references/compatibility.md` | Phase 6, toolchain handoff |
| `scripts/strata-scaffold.sh` | To create an empty tree before filling it |
| `scripts/strata-validate.py` | Phase 6, enforce the six rules |
| `scripts/strata-revive.sh` | Any time a dormant project must be resumed |


# STRATA

> Separation of Tiers, Retention Across Time, Auditability. From brain dump to build-ready, pivot-resilient, dormancy-proof artifacts in one session.

STRATA is the operational discipline that supersedes single-document spec-driven scaffolding. It transforms raw ideas, transcripts, or interactive discussion into a fixed six-artifact tree where intent, specification, and implementation are separated by author and a continuity ledger keeps the project from going into a dreamstate. Output is compatible with SpecKit, OpenSpec, Kiro, Cursor, and any agent that reads markdown.

## Why this exists

Vibe coding collapses because it has no contract. Spec-driven development collapses because it has three contracts pretending to be one: it buries intent inside the spec, pre-locks architecture at the top, and has no answer for continuity across time. STRATA fixes both by enforcing layer separation with a validator and by treating the system's memory of where it is standing as a first-class, load-bearing artifact, not a feature.

Read `references/paradigm.md` for the full conceptual model before generating artifacts if the conceptual basis is unclear. It is the spine; the rest of this file is the procedure.

## The six artifacts (plus one)

STRATA writes a `strata/{project-name}/` tree. Each artifact has exactly one author and is allowed to change without detonating the others.

| Artifact | Layer | Author | Maps to |
|----------|-------|--------|---------|
| `intent.md` | Intent | Human | SpecKit spec.md (why + constraints + NFRs), the part that drives architecture |
| `spec.md` | Specification | Human (system may draft) | SpecKit spec.md (testable what only) |
| `context.md` | Implementation | System (derived, never hand-authored) | SpecKit plan.md / OpenSpec design.md |
| `plays/` | Prompt | System | SpecKit tasks.md, but intent-encoded not target-encoded |
| `ledger/` | Continuity | System (append-only) | No SpecKit equivalent. This is the differentiator. |
| `constitution.md` | Governance | Human (never generated from scratch) | SpecKit constitution |
| `substrate.md` | Self-location | Human | No equivalent. Honest level + pre-lock declaration. |

The litmus rules, templates, and field-by-field structure for each artifact live in `references/`. Read the relevant reference before writing that artifact.

## The six rules (enforced, not suggested)

1. **Separation.** `intent.md` is not `spec.md` is not `context.md`. A technology, framework, or library token appearing in `intent.md` or `spec.md` is a defect. A `spec.md` clause that cannot be converted into a pass/fail evaluation is a defect. The validator fails the build on either.
2. **Authorship.** The human authors intent and spec. The system authors context and plays. Never hand-author a technology choice into intent or spec. Never ask the human to choose an architecture for `context.md`.
3. **Eval binding.** Every `spec.md` clause carries an `EVAL-ID` bound to an evaluation stored outside the build tree. Unbound clauses fail validation. Evals visible to the implementing agent are treated as compromised.
4. **Pivot.** Upstream change enters at `intent.md` only. The system re-derives `context.md`, records the delta in the ledger, and leaves plays untouched. Never propagate a pivot by editing tasks.
5. **Continuity.** Every decision and its outcome is appended to the ledger and `standing.md` is updated, every time, not only at milestones. A revived session reconstructs from the ledger before touching code.
6. **Honesty.** `substrate.md` states the real substrate level and the real pre-lock versus live-resolve boundary. Do not record certainty the project has not earned.

## Confidence Gate

Before generating any artifact, intake must reach **85% confidence** across ten dimensions (the original eight plus two STRATA-specific). Score conservatively. One extra question round costs minutes; a fused-layer artifact costs hours. The full rubric is in `references/confidence-gate.md`. Summary of dimensions and weights: Problem clarity (12%), Solution definition (12%), User personas (8%), Success criteria (10%), Data model (12%), Scope boundaries (8%), Technical constraints (10%), Business context (10%), **Layer-separation integrity (10%)** (can intent, spec, and implementation concerns be cleanly told apart in what the user has said, or are they fused), **Continuity readiness (8%)** (is there enough to seed the ledger and a first `standing.md`). Below 85%, ask 3 to 5 targeted questions on the lowest-scoring dimensions and reassess. Do not proceed until the threshold is met and the user confirms a one-paragraph understanding summary.

## Execution Protocol

### Phase 0: Mode detection and setup

Detect intake mode. Files or transcripts provided is Transcript mode. A verbal description or "I want to build X" is Interactive mode. Mixed is Transcript first, then Interactive gap-fill. If the user provides a complete, well-structured description covering problem, solution, users, data, constraints, and scope, run the Fast Track: score the Confidence Gate once, and if it clears 85% on the first pass proceed directly to Phase 2.

Load references as needed: `references/paradigm.md` for the model, the four artifact references for output structure, `references/research-checklist.md` for Phase 2, `references/data-architecture-guide.md` for Phase 3. Check for existing spec infrastructure (`.specify/`, `openspec/`, `.kiro/`, `strata/`) and existing `constitution.md`. If a `strata/` tree already exists, this skill does not apply; the user wants ongoing work, not a kickoff.

### Phase 1: Intake and extraction

Transcript mode: read everything, extract problem statements, proposed solutions, personas, success and failure conditions, constraints, scale and quality expectations, implied data entities, integration points, and workflow descriptions. Critically, tag every extracted signal as intent, spec, or implementation, because the user will have fused them and the separation starts here. Compute the Confidence Gate score.

Interactive mode: run a structured discovery conversation. Do not ask everything at once. Proceed through Problem Space, Solution Vision, Users and Adoption, Data and State, Technical Constraints, UX and Interaction, Business and Distribution, asking 2 to 4 questions per category and reassessing the gate after each. Use the structured-question tool when available so the user taps rather than types. The full category question bank is in `references/discovery-questions.md`.

For both modes, when confidence is below 85%, switch to targeted gap-fill on the lowest dimensions. When at or above, confirm understanding in one paragraph and proceed.

### Phase 2: Prior art research (mandatory)

Follow `references/research-checklist.md` in full. Local workspace scan first, then skill registries, then a minimum of three code searches and two web searches, then synthesis. If an existing tool fully solves the problem, stop and surface it before proceeding. Research findings are recorded in `intent.md` under Prior Art, never in a separate scratch file. Always survey how others approached the problem and extract reusable patterns and documented pitfalls.

### Phase 3: Context derivation (system-owned)

This is not a design-authoring step. The system derives the architecture from `intent.md`. Read scale and constraints out of intent, read the empirical memory out of `ledger/` if any prior STRATA project exists in the workspace, read the existing stack and risk tolerance, then apply `references/data-architecture-guide.md` to produce data, hosting, and security decisions. Every decision in `context.md` cites the intent input and, where available, the ledger entry that drove it. On a project with an empty ledger, state explicitly in `substrate.md` that Context Crafting is operating without empirical memory and is therefore closer to architect guesswork. Do not hide the gap.

### Phase 4: Artifact generation

Generate the tree in this order, reading the matching reference immediately before each:

1. `intent.md` using `references/intent-template.md`. Human-owned content, no technology tokens, NFRs and scale and failure conditions included because they drive architecture.
2. `spec.md` using `references/spec-template.md`. Every clause testable, every clause carrying an `EVAL-ID`, zero technology tokens.
3. `context.md` using `references/context-template.md`. System-derived, every decision cited back to intent and memory.
4. `plays/` using `references/plays-playbook.md`. Intent-encoded reusable patterns, never target-coupled. Include at minimum a scaffold play, a commit play, and a deploy play.
5. `ledger/ledger.md` and `ledger/standing.md` using `references/ledger-and-standing.md`. Seed the ledger with the kickoff decisions and write the first `standing.md`.
6. `substrate.md` using `references/substrate-self-location.md`. Declare the honest level and the pre-lock boundary.
7. `constitution.md`: include the user's existing constitution as a reference if present. If absent, do not generate one. Note its absence and tell the user to create one through SpecKit or OpenSpec tooling.

### Phase 5: Deliverative refinement

Invoke the deliberative-refinement skill on the human-authored layers. Run an Expert Council pass on `intent.md` and `spec.md` together checking completeness, testability, ambiguity, fused layers, and scope creep. Run a Structured Review pass on `context.md` checking that every spec clause is supported by the architecture and that nothing in context introduces a requirement absent from intent or spec. Cross-validate: every spec clause traces to an intent statement, every context decision traces to a spec clause or an intent constraint, every play reads its variables from intent rather than hard-coding them. Apply the refinements and append the refinement decisions to the ledger.

### Phase 6: Validation, delivery, handoff

Run `scripts/strata-validate.py` against the tree. It fails on technology tokens in intent or spec, on unbound spec clauses, on a missing or empty ledger or `standing.md`, and on a `substrate.md` that does not declare a level. Fix every failure before delivery. Present the tree, give a delivery summary stating the confidence score and any sub-threshold dimensions, the declared substrate level, key derived decisions and their rationale, any `[NEEDS CLARIFICATION]` markers, and the prior-art findings. Tell the user the handoff path: a fresh session loads `standing.md` and the ledger tail first, then `intent.md` and `spec.md`, then proceeds, and never needs this conversation's context. Provide next-step commands for their toolchain (SpecKit, OpenSpec, Kiro, or direct agent use); the mapping is in `references/compatibility.md`.

## Anti-patterns

Never fuse layers: no technology in intent or spec, no human-authored architecture in context. Never write a spec clause that cannot become an eval. Never let an eval be visible to the implementing agent. Never propagate a pivot through plays or tasks; it enters at intent only. Never skip the ledger or write it only at milestones. Never generate a constitution from scratch. Never inflate the Confidence Gate to skip a question round. Never claim a substrate level the project has not earned. Never write research or exploration notes into output files; prior art goes in `intent.md`, process notes go nowhere. Never use dates or timestamps in plays or phases; use phase and step notation. Never ask every discovery question in one message.

## Resource files

| File | Read when |
|------|-----------|
| `references/paradigm.md` | Before generating, if the conceptual model is unclear |
| `references/intent-template.md` | Phase 4, writing `intent.md` |
| `references/spec-template.md` | Phase 4, writing `spec.md` |
| `references/context-template.md` | Phase 3 and 4, deriving `context.md` |
| `references/plays-playbook.md` | Phase 4, writing `plays/` |
| `references/ledger-and-standing.md` | Phase 4, seeding continuity |
| `references/substrate-self-location.md` | Phase 4, writing `substrate.md` |
| `references/confidence-gate.md` | Phase 1, scoring intake |
| `references/discovery-questions.md` | Phase 1, Interactive mode |
| `references/research-checklist.md` | Phase 2, prior art |
| `references/data-architecture-guide.md` | Phase 3, context derivation |
| `references/compatibility.md` | Phase 6, toolchain handoff |
| `scripts/strata-scaffold.sh` | To create an empty tree before filling it |
| `scripts/strata-validate.py` | Phase 6, enforce the six rules |
| `scripts/strata-revive.sh` | Any time a dormant project must be resumed |
