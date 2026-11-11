---
title: Continuity
version: "4.0.0"
tags: [spec-prep]
---

# Continuity

## Contents

- [Continuity: Ledger and Standing (`ledger/`)](#continuity-ledger-and-standing-ledger)
- [Substrate Self-Location (`substrate.md`)](#substrate-self-location-substratemd)
- [Optional Living Documents integration](#optional-living-documents-integration)

## Continuity: Ledger and Standing (`ledger/`)

*Formerly `#continuity-ledger-and-standing-ledger`, version 1.0.0.*

Author: the system records material evidence and decisions. Layer: Continuity. The ledger and standing snapshot make history and current resumable state explicit; their usefulness depends on accuracy and read-back against live state, not a promised recovery time or exclusive ownership of the idea.

### Two files

`ledger/ledger.md` is an append-only record. Never edited, never reordered, never pruned. Every entry is one decision and, when known, its outcome. The ledger is how drift becomes loud instead of silent: nothing changes without an entry, so a diverged project shows its divergence in the log rather than hiding it in the code.

`ledger/standing.md` is a single overwritten file that answers one question in plain language: where is this system standing right now, and how did it get here. It is the first thing a revived session reads. It is not a status badge; it is sentences a human or an agent can act on without archaeology.

### Ledger entry format

```markdown
## [SEQ] [phase.step] [decision | outcome | pivot | refinement]
- What: [the decision or observation, one or two sentences]
- Why: [the intent input, spec clause, or council finding that drove it]
- Effect: [what changed in which artifact; on a pivot, the context.md delta]
- Outcome: [observed result if known, or "pending"]
```

Sequence numbers are monotonic and never reused. Phase.step uses spec-prep phase notation, never dates.

### Standing format

```markdown
---
date: {{DATE}} {{TIME}} {{TZ}}
ver: {{VERSION}}
author: {{AUTHOR}} (system-owned)
model: {{MODEL}}
tags: [{{TAGS}}]
---

# Standing

## Where this is
[Plain sentences. What the project is, what phase it is in, what was last completed.]

## Last decisions that matter
[The three to five ledger entries a resuming worker must know, summarized, with SEQ references.]

## Not yet decided
[Open questions and deferred decisions, each pointing at the intent or spec section that will resolve them.]

## Next
[The immediate next action and which play or phase carries it.]

## Substrate note
[Current declared level and any pre-locked decision that a resuming worker should know is pre-locked, not live.]
```

### The revive protocol

Resume by reading `standing.md` and the relevant tail of `ledger.md` before changing code, then verify against live task/artifact state to reconstruct it. If the records are missing or stale, consult history and sources, record the gap and reconcile the evidence; never invent an uninterrupted history.

### The backward feed

Recorded outcomes may inform later architecture when their evidence and context are relevant and access is authorized. Separate an observation from a proposed causal lesson and from accepted reusable policy. An empty ledger supplies no empirical precedent. Ledger accumulation alone neither implements a learning engine nor establishes that an earlier architecture generalizes.

### Rules

Append-only and monotonic. Record material decisions, outcomes, pivots, refinements and task-state changes. Refresh standing.md when resumable state changes, before final receipt hashing; do not rewrite it for every prompt/tool call. Keep nested ledger/ files by default; existing flat aliases are accepted only when they do not conflict. The revive protocol reads standing and the ledger tail before code. A project with no ledger or no `standing.md` fails validation; continuity is not optional.

## Substrate Self-Location (`substrate.md`)

*Formerly `#substrate-self-location-substratemd`, version 1.0.0.*

Author: the human. This file turns the closing question of the autopsy, are you being honest with yourself, into a required field. You declare which substrate level the project actually operates at and which decisions are pre-locked at preparation time versus resolved live at implementation time. You do not get to claim a level you have not earned.

### Source taxonomies and legacy compatibility

Ahuja's **Substrate Stack** in the supplied article has five numbered levels:

1. Vibe: model and coding interface, without the proposed persistent intent/contract substrate.
2. Spec-driven: structured specification tooling.
3. Intent-driven: separated layers, the four crafts, plays and an empirical knowledge base.
4. Autonomous: shared guardrails and reasoning across plays. The author explicitly describes this as not yet lived.
5. Dark Factory: live resolution within a largely autonomous methodology. The author explicitly treats the implementation as unresolved.

These are Ahuja's proposed substrate categories, not a benchmark or a capability certification. His article locates his own implementation around 2.5-2.75, not fully at 3. It credits Dan Shapiro for the Dark Factory term and autonomy-model influence; it does not make the two taxonomies numerically interchangeable.

**Existing STRATA labels S0-S5 are retained as legacy file/validator syntax.** They describe the local operating arrangement, not an exact Shapiro scale or a renumbering of Ahuja's five levels:

- S0: human implementation with autocomplete.
- S1: discrete agent tasks with human review.
- S2: agent changes with line-by-line human review.
- S3: human direction and verification with agent development.
- S4: specification/outcome-oriented human oversight rather than routine line review.
- S5: claimed autonomous production with separately evaluated outcomes, requiring evidence beyond this declaration.

Name the framework beside the label, and describe actual human review, agent permissions, protected evaluation and decision timing. Using this skill does not establish any maturity level. Do not silently reinterpret old declarations under a new taxonomy; record any revised interpretation with its source and evidence.

### What you must declare

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
[Legacy STRATA label S0 through S5 for compatibility, followed by the actual operating arrangement and evidence. If also discussing Ahuja's Levels 1-5, label that framework separately; do not imply numeric equivalence.]

## Pre-locked decisions
[Decisions fixed at preparation time, their source authority, and why they are fixed. Distinguish required user constraints from provisional agent choices. Do not infer a maturity rank from timing alone.]

## Live-resolved decisions
[What is genuinely resolved at implementation time, not pre-locked.]

## Empirical memory state
[Full, partial, or empty project ledger; distinguish applicable observed outcomes, current research and unsupported intuition. Record access and relevance limits.]

## Known reach
[What this project claims it can do that it has not yet proven. Stated as reach, not as fact.]
```

### Why this is required, not optional

The declaration makes pre-locking, missing evidence and unproven autonomy visible. The validator checks the presence of a legacy level label, not whether the claimed capabilities exist. Validate material capabilities separately; neither a label nor this file enforces evaluator isolation or certifies autonomy.

## Optional Living Documents integration

*Formerly `#optional-living-documents-integration`, version 2.3.0.*

Read this reference only when the user requests Living Documents, an existing dossier/configuration declares it, the `ld` command is available, or host instructions require it. This supersedes the inline Living Documents setup procedure in spec-prep 2.2. Host instructions remain authoritative.

### Resolve the setup choice

`auto` detects and reuses an available system or existing dossier. `on` requests integration. `off` skips optional integration without deleting anything. Do not force installation on machines without Living Documents. When requested but unavailable, state the unavailable integration and continue all independent preparation; installation requires a request targeting it.

Once present, read the installed Living Documents skill and current system contract rather than copying an old version into spec-prep. Resolve the exact source project, run `ld ensure` for that project, and read the returned start-here, project and what-to-do pages. Verify that the returned source-root actually matches; an ancestor match is not enough. Do not query or resume unrelated project ledger work.

For an authorized missing dossier, use the installed `ld create-project` syntax with the project ID, title and real source root. Reuse existing pages and stable IDs. Use `ld add-page` for additional pages, then edit the registered page. Preserve existing narrative and operator annotations. Read the CLI help for installed syntax; no hardcoded user paths or stale release numbers belong in this portable reference.

### Declare authority once

The workbench is presentation/configuration. The intake is source evidence and identity. Spec Kit artifacts are the operational contract in the repository. The dossier records human intent, accepted decisions, project task evidence and cross-session continuity under its own contract. Name which location owns each concept and link between scopes instead of keeping parallel editable requirements, plans or task status.

Register links to the intake, workbench, repository constitution, native spec/plan/tasks, preparation evidence and reset handoff when useful. Keep the dossier's project task register separate from Spec Kit's implementation task breakdown, with clear ownership and linked completion evidence. An implementation checkbox cannot silently satisfy a dossier gate.

### Continuity

Use the existing system's history, start-here, handoff and continuity hook for material milestones. If the chosen standalone spec-prep continuity files still apply, declare their role and avoid duplicate independent decision logs. Use the installed validator/adapter for the declared canonical continuity paths; do not fabricate a ledger merely to satisfy a mechanical gate.

A fresh implementation harness reads the real build root's AGENTS.md, the canonical constitution, prepared task gates and reset handoff, then the linked dossier context when present. Verify required preparation before initiation. A renderer receipt or dossier entry is not permission to launch, publish or spend.

Store the integration preference and optional dossier locator in `workbench.json`. Only an identified existing or created dossier may supply that locator. Do not invent a path or manufacture a setup-complete label.
