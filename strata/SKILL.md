---
name: strata
description: |-
  Spec-driven development for work whose original intent has been LOST and must be recovered before anything downstream can be trusted. Derives a context and intent layer first, then runs the same author/implement/audit gates with every artifact traceable back to it. Use when the project already exists and nobody can say what it was for, when two specs disagree about it, or when traceability from intent to task matters more than speed.
  NOT for authoring a spec from material you already understand - that is spec-workflow. If the intent is known, use spec-workflow even when the input is a brain dump or transcript.
  Triggers: "strata", "recover the intent", "what was this supposed to be", "intent-driven", "weave intent", "intent layer", "traceable spec", "vibe vs spec", "spec is collapsing", "why does this project exist", "reconstruct the requirements", "the specs disagree".
license: MIT
metadata:
  version: "2.0.0"
  supersedes: "strata-authoring, strata-implementing, deprecated/strata"
tags:
- spec-driven
- intent
- planning
- coding
---


# STRATA Authoring

> Separation of Tiers, Retention Across Time, Auditability. From brain dump to
> build-ready, pivot-resilient, dormancy-proof artifacts with a permanent home.

This is the authoring half of STRATA. It produces specifications. It does not
build them; `strata-implementing` does that, and Phase 7 hands off.

## Why this exists

Vibe coding collapses because it has no contract. Spec-driven development
collapses because it has three contracts pretending to be one: intent buried
inside the spec, the testable contract diluted with prose, and architecture
pre-locked at the top before the system that should own that decision ever
reasons about it.

Two observable consequences. An upstream change such as a deployment target
moving detonates a spec-driven scaffold, because every downstream task inherited
the fused assumption. And a project that sits dormant develops amnesia, because
intent lived only in a human head and an untrusted git log.

STRATA fixes both by enforcing layer separation with a validator, and by treating
the system's memory of where it is standing as a first-class artifact.

Read `references/paradigm.md` for the conceptual model before generating
artifacts if the basis is unclear. It is the spine; this file is the procedure.

## Where artifacts live

**The project folder is the permanent home.** In Living Documents terminology,
the *project folder* is the dossier for a specific project at
`~/LIVING_DOCUMENTS/projects/<project-id>/`. Artifacts authored here are not
loose files in a working directory; they are pages in that dossier, indexed and
projected into the reader.

This is not a bolt-on. STRATA's artifacts and the Living Documents scaffold are
the same structure discovered twice:

| STRATA artifact | Living Documents page | Author |
|---|---|---|
| `intent.md` | `intent` | Human |
| `spec.md` | `spec` | Human (system may draft) |
| `context.md` | `plan` | System (derived, never hand-authored) |
| `plays/` | `plays` | System |
| `ledger/ledger.md` | `history` + `decisions` | System (append-only) |
| `ledger/standing.md` | `start-here` | System |
| `substrate.md` | `substrate` | Human |
| `constitution.md` | `constitution` | Human (never generated from scratch) |

The continuity ledger STRATA invented and the Living Documents `start-here` plus
`history` pair solve the identical problem: a revived session reconstructs from
them before touching code. Writing to both would create two sources of truth, so
the dossier is authoritative and the ledger is how it is written.

**Never create a page with a direct file write.** Use `ld add-page`, then edit
the file it creates. A direct write skips index registration, so the page is
never projected: it looks finished on disk and does not exist in the reader, with
no error anywhere. Run `ld-audit` after authoring to confirm zero orphans.

When Living Documents is unavailable, fall back to a `strata/<project-name>/`
tree and record in the delivery summary that the artifacts have no permanent
home yet.

## The six rules (enforced, not suggested)

1. **Separation.** `intent.md` is not `spec.md` is not `context.md`. A
   technology, framework, or library token in intent or spec is a defect. A spec
   clause that cannot become a pass/fail evaluation is a defect. The validator
   fails the build on either.
2. **Authorship.** The human authors intent and spec. The system authors context
   and plays. Never hand-author a technology choice into intent or spec. Never
   ask the human to choose an architecture for context.
3. **Eval binding.** Every spec clause carries an `EVAL-ID` bound to an
   evaluation stored outside the build tree. Unbound clauses fail validation.
   Evals visible to the implementing agent are treated as compromised.
4. **Pivot.** Upstream change enters at `intent.md` only. The system re-derives
   context, records the delta in the ledger, and leaves plays untouched. Never
   propagate a pivot by editing tasks.
5. **Continuity.** Every decision and its outcome is appended to the ledger and
   the standing page is updated, every time, not only at milestones. This
   prevents the **dreamstate**: a project that sits dormant, then wakes with its
   intent surviving only in a human head and an untrusted git log, so resuming it
   costs days of archaeology.
6. **Honesty.** `substrate.md` states the real substrate level and the real
   pre-lock versus live-resolve boundary. Do not record certainty the project has
   not earned.

## Confidence Gate

Before generating any artifact, intake must reach **85% confidence** across ten
dimensions. Score conservatively; one extra question round costs minutes, a
fused-layer artifact costs hours. Full rubric in `references/confidence-gate.md`.

Problem clarity (12%), Solution definition (12%), User personas (8%), Success
criteria (10%), Data model (12%), Scope boundaries (8%), Technical constraints
(10%), Business context (10%), **Layer-separation integrity (10%)** (can intent,
spec, and implementation be told apart in what the user said, or are they
fused), **Continuity readiness (8%)** (is there enough to seed the ledger and a
first standing page).

Below 85%, ask 3 to 5 targeted questions on the lowest dimensions and reassess.
Do not proceed until the threshold is met and the user confirms a one-paragraph
understanding summary.

## Execution Protocol

### Phase 0: Mode detection and setup

Detect intake mode:

- **Transcript mode** — files, transcripts, or notes provided.
- **Interactive mode** — a verbal description or "I want to build X".
- **Existing-specs mode** — the user provides detailed `requirements.md` and
  `design.md` (each 5K+, structured requirements, component descriptions, data
  model). Skip Phases 1 and 2; they are already specified and researched. Go to
  Phase 3, deriving context and re-separating layers. The Confidence Gate does
  not apply: existing documents already represent verified requirements. Still
  run the separation validator, because externally authored specs routinely fuse
  layers.
- **Mixed** — Transcript first, then Interactive gap-fill.
- **Fast Track** — a complete, well-structured description covering problem,
  solution, users, data, constraints, and scope. Score the gate once; if it
  clears 85% on the first pass, proceed directly to Phase 2.

Load references as needed. Check for existing infrastructure: the Living
Documents dossier for this project, `.specify/`, `openspec/`, `.kiro/`, or a
`strata/` tree, and any existing `constitution.md`.

If an authored STRATA tree already exists, this skill does not apply: the user
wants ongoing work, not a kickoff.

### Phase 1: Intake and extraction

*Skip in Existing-specs mode.*

**Transcript mode**: read everything. Extract problem statements, proposed
solutions, personas, success and failure conditions, constraints, scale and
quality expectations, implied data entities, integration points, and workflow
descriptions. Critically, **tag every extracted signal as intent, spec, or
implementation**, because the user will have fused them and separation starts
here. Compute the gate score.

**Interactive mode**: run structured discovery. Do not ask everything at once.
Proceed through Problem Space, Solution Vision, Users and Adoption, Data and
State, Technical Constraints, UX and Interaction, Business and Distribution,
asking 2 to 4 questions per category and reassessing after each. Use the
structured-question tool when available so the user taps rather than types.
Question bank in `references/discovery-questions.md`.

### Phase 2: Prior art research (mandatory)

*Skip in Existing-specs mode.*

Follow `references/research-checklist.md` in full: local workspace scan, then
skill registries, then a minimum of three code searches and two web searches,
then synthesis. **If an existing tool fully solves the problem, stop and surface
it before proceeding.** Findings are recorded in `intent.md` under Prior Art,
never in a separate scratch file.

Ground technology-adjacent claims in current sources. A stack decision made from
training-data recall is a guess wearing a citation.

### Phase 3: Context derivation (system-owned)

This is not a design-authoring step. The system derives architecture from
`intent.md`. Read scale and constraints out of intent, read empirical memory out
of the ledger if any prior STRATA project exists in the workspace, read the
existing stack and risk tolerance, then apply
`references/data-architecture-guide.md`.

Every decision in context cites the intent input and, where available, the ledger
entry that drove it. The accumulated ledger **is** the knowledge base, and the
knowledge base is the differentiator: it is what moves architecture selection out
of architect guesswork and into repeatable engineering. On a project with an empty ledger, state explicitly in
`substrate.md` that context derivation is operating without empirical memory and
is therefore closer to architect guesswork. Do not hide the gap.

### Phase 4: Artifact generation

Resolve the project folder first:

```bash
ld ensure                                    # confirm the corpus exists
ld create-project --project <project-id>     # if the dossier does not exist
ld add-page --project <project-id> --id <page-id> --title "<title>" \
            --type <type> --parent index     # once per new page
```

Then generate in this order, reading the matching reference immediately before
each, and editing the file `ld add-page` created:

1. `intent` using `references/intent-template.md`. Human-owned, no technology
   tokens, NFRs and scale and failure conditions included because they drive
   architecture.
2. `spec` using `references/spec-template.md`. Every clause testable, every
   clause carrying an `EVAL-ID`, zero technology tokens.
3. `plan` (context) using `references/context-template.md`. System-derived, every
   decision cited back to intent and memory.
4. `plays` using `references/plays-playbook.md`. Intent-encoded reusable
   patterns, never target-coupled. At minimum a scaffold, a commit, and a deploy
   play.
5. `start-here` and `history`/`decisions` using
   `references/ledger-and-standing.md`. Seed the ledger with kickoff decisions
   and write the first standing page.
6. `substrate` using `references/substrate-self-location.md`. Declare the honest
   level and the pre-lock boundary.
7. `constitution`: reference the user's existing constitution if present. If
   absent, do not generate one. Note its absence and say to create one through
   the project's governance tooling.

### Phase 5: Refinement and depth verification

**5a. Deliberative refinement.** Invoke the deliberative-refinement skill on the
human-authored layers. Expert Council pass on intent and spec together, checking
completeness, testability, ambiguity, fused layers, and scope creep. Structured
Review pass on context, checking that every spec clause is supported by the
architecture and that context introduces no requirement absent from intent or
spec.

**5b. Depth-verification gate.** Compare output against the original input. This
catches the specific failure where a pipeline produces well-formed artifacts that
are thinner than the source material:

- Requirement count in source versus output must match within tolerance. A drop
  is lost content, not successful summarization.
- Design section coverage must be 100%. Name any section that did not survive.
- Every play must be startable without re-reading the source documents. A play
  that is only a file path has lost its specification.
- Any content that could not be preserved is documented with the specific
  section and reason.

Where depth was lost, regenerate that artifact with explicit depth-preservation
directives. Do not accept a shallow artifact because it is well-formed.

**5c. Cross-validation.** Every spec clause traces to an intent statement. Every
context decision traces to a spec clause or an intent constraint. Every play
reads its variables from intent rather than hard-coding them. Append the
refinement decisions to the ledger.

### Phase 6: Validation and delivery

Run `scripts/strata-validate.py` against the artifacts. It fails on technology
tokens in intent or spec, unbound spec clauses, a missing or empty ledger or
standing page, and a substrate file that does not declare a level.

It also fails on non-evaluable clause language, on a spec too thin to drive
determinism, on an eval tag that resolves to no manifest outside the tree, and on
drift in either direction between spec and context.

**Arm the denylist for the domain before trusting a pass.** Drop a
`tech-tokens.txt` beside the artifacts, one token per line. The shipped list
covers common stacks and will miss domain-specific ones. A validator that passes
because it was not looking is worse than no validator.

To measure an existing SpecKit, OpenSpec, or Kiro corpus before migrating it:
`strata-validate.py --audit <files>`. It infers each file's layer from its name
and checks separation only on the human-authored ones, because the derived layer
is supposed to name technologies.

Then run `ld sync` and `ld-audit`. Zero orphans, zero ghosts, zero bad links, or
the artifacts are not actually in the reader.

**When validation reports a divergence, adjudicate it — do not just report it.**
The validator says two artifacts disagree; it cannot say which is wrong, and a
divergence left unresolved silently becomes the spec.

*Preserve the blind baseline.* Whatever the first cold reading produced stays
immutable. Do not rewrite it once you know the answer — the value of a blind
result is that it was blind, and an edited baseline can no longer disconfirm
anything.

*Disclose the smallest missing constraint, then re-evaluate.* If the divergence
looks like missing context rather than genuine disagreement, add one constraint —
the least that could account for it — and run the comparison again. Adding
everything at once tells you the artifacts agree without telling you why.

*Stop on any of three conditions*, whichever comes first: the divergence
resolves; no undisclosed material constraint remains; or two clarification
rounds pass with no material change. The third exists because an unbounded
clarification loop converges on the answer you were hoping for rather than the
one the evidence supports.

Record which condition ended it. A divergence closed by exhaustion is a
different fact from one closed by resolution, and the ledger should not blur
them.

Present the artifacts with a delivery summary: confidence score and any
sub-threshold dimensions, declared substrate level, key derived decisions and
their rationale, remaining `[NEEDS CLARIFICATION]` markers, prior-art findings,
depth-verification results, and the project folder path.

State the handoff path: a fresh session loads the standing page and ledger tail
first, then intent and spec, then proceeds, and never needs this conversation's
context.

### Phase 7: Execution handoff (REQUIRED)

This skill authors specifications. It does not build them. The next step is
`strata-implementing`, which drives the pipeline through to implementation.

**First check whether the user already authorized it.** If the original request
named that skill, said "then run it", "and build it", or "take it through to
tasks", that authorization covers this step. **Proceed directly and do not ask.**
Re-confirming work the user already requested wastes a turn and reads as not
having listened.

**Only when execution was not already requested**, ask once:

> Specs are authored in the project folder `<path>`: intent, spec, plan, plays,
> substrate, and a seeded ledger. Would you like me to continue with
> `strata-implementing` to execute them, or stop here so you can review or
> delegate the build?

Rules for the ask:

- Ask **once**. A declined offer is a decision; do not re-offer in the session.
- State what exists and where, so the choice is informed.
- Offer stopping as a real option. Delegating to a separate model and reviewing
  before building are both legitimate and common.
- If the user is not present (batch, cron, delegated run), stop after authoring
  and say so. Never assume consent for a build that was not requested.

## Anti-patterns

Never fuse layers: no technology in intent or spec, no human-authored
architecture in context. Never write a spec clause that cannot become an eval.
Never let an eval be visible to the implementing agent. Never propagate a pivot
through plays or tasks; it enters at intent only. Never skip the ledger or write
it only at milestones. Never generate a constitution from scratch. Never inflate
the Confidence Gate to skip a question round. Never claim a substrate level the
project has not earned. Never write research or exploration notes into output
files; prior art goes in intent, process notes go nowhere. Never use dates or
timestamps in plays or phases; use phase and step notation. Never ask every
discovery question in one message. **Never create a Living Documents page with a
direct file write.** Never trust a validator pass without checking that its token
list covers the domain.

## Resource files

| File | Read when |
|------|-----------|
| `references/paradigm.md` | Before generating, if the conceptual model is unclear |
| `references/intent-template.md` | Phase 4, writing intent |
| `references/spec-template.md` | Phase 4, writing spec |
| `references/context-template.md` | Phase 3 and 4, deriving context |
| `references/plays-playbook.md` | Phase 4, writing plays |
| `references/ledger-and-standing.md` | Phase 4, seeding continuity |
| `references/substrate-self-location.md` | Phase 4, writing substrate |
| `references/confidence-gate.md` | Phase 1, scoring intake |
| `references/discovery-questions.md` | Phase 1, Interactive mode |
| `references/research-checklist.md` | Phase 2, prior art |
| `references/data-architecture-guide.md` | Phase 3, context derivation |
| `references/compatibility.md` | Phase 6, toolchain handoff |
| `scripts/strata-scaffold.sh` | Create an empty tree before filling it |
| `scripts/strata-validate.py` | Phase 6, enforce the six rules |
| `scripts/strata-revive.sh` | Resume a dormant project |
