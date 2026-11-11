---
title: Templates
version: "4.0.0"
tags: [spec-prep]
---

# Templates

## Contents

- [Intent Template (`intent.md`)](#intent-template-intentmd)
- [Spec Template (`spec.md`)](#spec-template-specmd)
- [Context Template (`context.md`)](#context-template-contextmd)
- [Experience Template (`experience.md`)](#experience-template-experiencemd)
- [Data Architecture Decision Guide](#data-architecture-decision-guide)
- [Plays Playbook (`plays/`)](#plays-playbook-plays)

## Intent Template (`intent.md`)

*Formerly `#intent-template-intentmd`, version 1.0.0.*

Authoritative owner: the user; an agent may draft with provenance. Layer: Intent. Maintain this asset separately from requirements and design. Goal changes start here; behavior, architecture and workflow corrections start at their owning layer and reconcile affected dependents. Preserve explicitly required technologies with their source and justified layer exception; do not promote agent proposals into constraints.

Intent is not a tagline and not a user story. It is a full schema of what is wanted, under what constraints, with what success and failure conditions, including the scale and quality expectations that architecture is derived from.

### Template structure

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

### Rules

Record explicit deployment constraints in section 3 and distinguish them from architecture proposals. Derive observable platform and non-functional acceptance in requirements/spec, with mechanisms in design/plan. Preserve failure outcomes and public acceptance. Do not erase user-named technology constraints to satisfy a token heuristic: cite their source and allowed exception. Goal changes begin in intent; corrections in behavior, architecture or workflow enter their owning layer and propagate to affected dependents. Preserve source prompts once and include or link the material source-disposition map.

## Spec Template (`spec.md`)

*Formerly `#spec-template-specmd`, version 1.0.0.*

Layer: Specification. Preserve the source authority of each requirement: direct user instruction, accepted decision or explicit proposal/inference. Authorized preparation can derive provisional observable clauses without creating implementation authority. Keep mechanisms in plan and retain genuine source-constrained platform/interface acceptance with cited layer exceptions. Write evaluable clauses and preserve native user scenarios; intent remains the source for goals/stories, not a reason to delete native template content.

### The single litmus

Every clause must be convertible into an evaluation that returns pass or fail. If an obligation is not yet evaluable, classify it as intent, a proposal or an unresolved requirement and preserve its source/disposition. Do not silently delete a material need. A specification may include explanatory context, but its contract clauses need observable acceptance.

### Eval binding

Every clause carries an `EVAL-ID` linked to a defined evaluation. Retain the external evaluation-definition store expected by the validator (default `~/.spec-prep/evals/<slug>/evals.md`); this storage convention does not establish held-out isolation. Public acceptance criteria and development tests remain available to the implementer. Use evaluator-only tests when appropriate and claim held-out evaluation only with actual file/tool access separation. An unbound clause fails validation; a bound identifier alone does not prove a useful test.

### EARS-style phrasing

Use the Easy Approach to Requirements Syntax so each clause collapses to one testable claim with no ambiguity about trigger, scope, or response. Forms: ubiquitous ("The system SHALL ..."), event-driven ("WHEN [trigger] the system SHALL ..."), state-driven ("WHILE [state] the system SHALL ..."), unwanted ("IF [condition] THEN the system SHALL ...").

### Template structure

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

### Rules

Keep derived mechanisms in design/plan. Preserve explicit source-mandated platform/interface constraints with provenance and justified layer exceptions. Every clause has a SPEC-ID and an EVAL-ID and traces to intent. Cover material failure conditions and measurable quality obligations; keep their originating expectations in intent. Distinguish public acceptance from evaluator-only fixtures. Reclassify architecture proposals into the owning layer without erasing user authority.

## Context Template (`context.md`)

*Formerly `#context-template-contextmd`, version 1.0.0.*

Author: the system derives mechanisms from source requirements, intent and explicit user constraints. Layer: Implementation. Record user-selected constraints as such; distinguish derived proposals and source decisions instead of pretending every choice was inferred. Native plan.md is the operational plan when Spec Kit is selected; context.md is then source/rationale, not a competing editable plan.

### Derivation inputs, in order

1. Scale and constraints from `intent.md` sections 3 and 4.
2. Empirical memory from `ledger/` of any prior spec-prep project in the workspace: what architecture was chosen under what constraints and what the recorded outcome was.
3. The existing stack the project must live in.
4. Risk tolerance from `intent.md`.

Every decision in this file cites the intent input and, where it exists, the ledger entry that drove it. A decision with no citation is guesswork wearing a citation's clothes; mark it as such.

### The empty-ledger honesty rule

An empty project ledger supplies no project-specific outcome evidence. Disclose that gap here and in `substrate.md`, while distinguishing current research, inspected-system facts and applicable prior outcomes from intuition. Cite actual evidence rather than treating an empty ledger as proof that no relevant knowledge exists.

### Template structure

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
- Memory: ledger entry [id] (prior project at similar scale chose [y], outcome [z]) OR "no project-specific outcome evidence; cite other evidence or identify intuition"
- Options considered: [2 to 3]
- Decision status and authority: [user-mandated, provisional, accepted or live-resolved; source and rationale]
- Revisit trigger: [what new evidence or constraint change invalidates this choice; affected dependents]
- Trade-offs accepted: [what is given up]

## 4. Data model
[Schema with concrete types, access patterns, migration strategy. Per #data-architecture-decision-guide.]

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

### Rules

Every decision cites its intent input. Every decision states its memory source or admits it has none. The deployment section is downstream of the intent constraint; on a pivot it is regenerated, not patched, and the delta goes to the ledger. No requirement appears here that is not present in intent or spec. Phases use phase and step notation, never dates.

## Experience Template (`experience.md`)

*Formerly `#experience-template-experiencemd`, version 2.1.0.*

Author: the system. Layer: derived (declare `layer: derived` in its frontmatter). Required whenever the project has a user interface; omit it for libraries, services and CLIs with no designed surface.

Context answers how the system is built. Experience answers how it looks, reads and responds. Keeping them apart stops visual decisions from being buried in architecture and gives design-focused skills (frontend design, accessibility review, UX copy) one file to own.

### Derivation inputs

1. Personas, user stories and failure conditions from `intent.md`.
2. Accessibility and interaction clauses from `spec.md`.
3. The user's stated design preferences (theme defaults, frameworks for UI primitives belong in context, not here).
4. Any design-skill guidance available in the session. Use those skills to choose palette, type and layout, and record the choice here with one line of reasoning each.

### Template structure

```markdown
---
date: {{DATE}} {{TIME}} {{TZ}}
ver: 1.0.0
author: {{AUTHOR}} (system-derived)
model: {{MODEL}}
layer: derived
tags: [{{TAGS}}]
---

# [Project Name] Experience v1.0 (derived)

## 1. Interaction model
[Screens or states, navigation model, the first thirty seconds, loading, empty and error states. Each element cites the story or persona it serves.]

## 2. Design tokens
| Token | Dark | Light | Role |
|-------|------|-------|------|
[The mockup is the source of truth when one exists; this table mirrors it exactly.]

## 3. Components with behaviour contracts
[Only bespoke or critical components: inputs, keyboard and pointer behaviour, accessible name, role and value, feedback.]

## 4. Copy rules
[Voice, banned terms, verb consistency, error and empty-state patterns.]

## 5. Mockup
[Path to an interactive mockup and screenshots in each theme at phone and desktop widths. The mockup must be verified by actually rendering it, not by reading its source.]

## 6. Accessibility
[Target level; how each accessibility SPEC clause is met.]
```

### Rules

No requirement appears here that is not in intent or spec. Every token and component traces to a story or clause. Screenshots or it did not happen.

## Data Architecture Decision Guide

*Formerly `#data-architecture-decision-guide`, version 1.0.0.*

Reference for Phase 3. These decisions are derived by the system into `context.md`, each cited back to an `intent.md` constraint and, where it exists, a ledger entry. They are never authored by the human.

### Storage type decision

Does the system persist data at all. If no, client-side or in-memory only; stop. If yes, is it primarily relational. If relational and over 10GB or concurrent multi-user writes, a server relational store; otherwise single-file relational. If not relational: key-value or document shaped goes to a document or key-value store depending on schema variability; graph-structured goes to a graph store or relational with recursive queries if the graph is secondary; similarity-searched goes to a vector store; time-series goes to a partitioned or time-series store; otherwise simple file storage.

### Schema principles

Relational: normalize to third normal form first, denormalize only when a recorded read pattern demands it, document every denormalization. Standard elements: sortable non-leaking id, created and updated timestamps, soft delete unless hard delete is an intent requirement. Index columns used in filtering, joining, and ordering; composite indexes put equality columns before range columns; partial indexes for filtered queries. Document stores: embed when accessed together and small and rarely updated, reference otherwise; keep nesting shallow. Key-value: namespaced keys, TTL on all ephemeral data.

### Access pattern classification

Read-heavy favors caching and materialized views. Write-heavy favors write-optimized storage and batched async writes. Append-only favors partitioned time-indexed storage. Search-heavy favors a dedicated search or vector index. Each entity's pattern is recorded as a derivation input in `context.md` section 3.

### Hosting derivation

The deployment target is an `intent.md` constraint, not a choice made here. This guide derives the data and infrastructure that satisfy that constraint. Edge and cost-sensitive and static-or-API workloads suit edge isolates with their paired edge data stores. Background jobs and long-running and SSR suit a serverless or always-on host with its paired managed stores. Full control, GPU, or strict privacy suits self-hosting. When the intent constraint changes, this entire derivation is rerun and the delta is appended to the ledger; it is never patched in place.

### Security baseline

TLS in transit always, encryption at rest when storing personal data, least-privilege credentials, input validation before storage, secrets in environment never in repo, automated backups with tested restore, audit trail for sensitive mutation. Each appears in `context.md` section 7 with the intent or spec identifier it satisfies.

## Plays Playbook (`plays/`)

*Formerly `#plays-playbook-plays`, version 1.0.0.*

Author: the system. Layer: Prompt. Plays are reusable, intent-encoded interaction patterns that make procedure and inputs explicit; they do not make model reasoning deterministic. They are not a one-shot task list. A task list is the thing that detonates on an upstream pivot, because every task baked in the assumption that changed. A play never bakes in the assumption. It reads the assumption from `intent.md` at execution time.

### The coupling rule

A play must never name a target it could instead read. Wrong: "deploy to Cloudflare Workers." Right: "deploy according to the deployment constraint in intent.md section 3." When only the constraint value changes, the play need not change because it reads that value. When the workflow or variable contract itself changes, update the play and its dependents. It only knew where to read it. This is the entire reason plays survive pivots and tasks do not.

### The maturity-gap honesty

The source describes plays as scaffolding that may thin as models become more capable; that is a proposed direction, not a guaranteed forecast. Use plays where reusable procedure, coordination or a fragile operation benefits from explicit inputs, checks and halts. Let the agent resolve ordinary mechanisms within the accepted contract instead of encoding every coding step. Preserve governance and evaluation even when detailed procedural scaffolding is unnecessary. State actual fixed and live decisions in substrate.md rather than assigning maturity from a model name.

### Play file structure

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

### Optional play examples when reusable procedures are needed

Do not generate this full set by default or run implementation/publication actions during preparation. Examples include a scaffold play that creates the project skeleton from `context.md` section 9. A commit play that groups changes by concern and follows the constitution's commit convention, halting when a change cannot be mapped to a SPEC-ID. A deploy play that reads the deployment constraint from intent and never names a provider. A build play that turns context build phases into work packages: each package names the SPEC-IDs it satisfies, its dependencies, the folder it owns, a machine-checkable definition of done, and its parallel lane, so independent packages can run as separate agents in separate worktrees. The build play reads phases from `context.md` section 8 at run time; it never copies them. Add domain plays as the project requires.

### Rules

Plays read from intent, they do not store intent. Every play has a halt condition. Every play emits to the ledger. No play names a target it could read. Plays are bridges, declared as bridges in `substrate.md`.
