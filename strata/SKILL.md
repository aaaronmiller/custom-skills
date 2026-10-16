---
name: strata
description: |-
  Stages project inputs and prepares Spec Kit constitutions, specifications, plans and tasks. Use for project intake, specification preparation, intent recovery, or explicitly requested initiation of a prepared project.
license: MIT
metadata:
  version: "2.3.2"
  lineage: "create-new-project 1.x + STRATA 2.0"
tags:
- spec-driven
- intent
- planning
- coding
---

# STRATA 2.3.2

> Separation of Tiers, Retention Across Time, Auditability. From brain dump to
> build-ready, pivot-resilient, dormancy-proof artifacts.

This skill stages ideation outputs and prepares specifications with Spec Kit. It stops before implementation unless the current request explicitly includes project initiation. Read `references/terminology.md` before choosing an operation and `references/intake-and-speckit.md` when consuming a staged folder.

Routine debugging, code review and maintenance use their existing workflows. Supplied STRATA packs remain valid preparation inputs.

## Why this exists

Vibe coding collapses because it has no contract. Spec-driven development
collapses because it has three contracts pretending to be one: intent buried
inside the spec, the testable contract diluted with prose, and architecture
pre-locked before the system that should own that decision reasons about it.
An upstream change then detonates every downstream task, and a dormant project
wakes with its intent surviving only in a human head and an untrusted git log.

STRATA fixes both by enforcing layer separation with a validator and by treating
the project's memory of where it stands as a first-class artifact. Read
`references/paradigm.md` if the model is unclear.

## Where artifacts live

**Resolve the operation and the authoritative paths first.** A staged intake folder contains source evidence, not an implementation checkout. For specification preparation, use the actual project repository and Spec Kit's native `specs/<feature>/` plus `.specify/memory/constitution.md`. Existing STRATA layouts remain accepted as migration inputs; do not overwrite or reject a supplied spec pack merely because it already contains STRATA files.

Workbench mode defaults to `auto`: emit a portable `workbench.json` that points to the intake and actual artifacts, unless the user opts out. Read `references/project-workbench.md` for this operation. Keep extra source files, infer roles conservatively and record their disposition; unknown content does not disappear because it lacks a recognized name.

Living Documents is a progressive optional integration for the portable skill. Read `references/living-documents-setup.md` when requested, detected or required by current host instructions. Reuse the installed system's contract; do not force installation or duplicate its canonical content.

Read `references/artifact-contract.md` when choosing outputs. The default contract is intake/workbench, intent, native spec/plan/tasks, project constitution, scoped agent instructions, provenance/traceability, continuity, preparation evidence and reset handoff. Existing requirements/design files are accepted sources or declared conventions. Conditional artifacts include UX, research, data models, contracts, quickstart, quality checklists, plays and evaluator-only fixtures. Do not generate duplicate requirements/spec or design/plan authorities merely to fill a file list.

## The six rules (enforced, not suggested)

1. **Separation.** A technology, framework or library token in intent or spec is
   a defect. A spec clause that cannot become a pass/fail evaluation is a
   defect. Preserve explicit user constraints and product names with a justified `layer-allow.txt` entry rather than deleting them. The validator fails the build on leaked choices, and it self-arms by
   harvesting every technology the derived layer names.
2. **Authorship.** The human owns intent and spec (the system may draft; the
   human ratifies). The system owns context, experience and plays. Never ask the
   human to choose an architecture for context.
3. **Eval binding.** Every spec clause carries an `EVAL-ID` bound to a held-out
   evaluation stored outside the repository (default
   `~/.strata/evals/<slug>/evals.md`). The validator rejects stores inside the build root even without Git. An external directory alone is not an access-control boundary: genuine held-out evaluation requires an evaluator context whose files and tools are inaccessible to the implementing agent. Disclose isolation that has not been established.
4. **Pivot.** Upstream change enters at `intent.md` only. The system re-derives
   context and experience, records the delta in the ledger, and leaves plays
   untouched. Never propagate a pivot by editing tasks.
5. **Continuity.** Every decision and outcome is appended to the ledger and
   `standing.md` is overwritten, every time, not only at milestones. This
   prevents the dreamstate: a dormant project whose resumption costs days of
   archaeology.
6. **Honesty.** `substrate.md` states the real substrate level and the real
   pre-lock versus live-resolve boundary. Do not record certainty the project
   has not earned.

## Confidence Gate

Before generating, intake must reach **85% weighted confidence** across ten
dimensions (`references/confidence-gate.md`): problem clarity, solution
definition, personas, success criteria, data model, scope, technical
constraints, business context, layer-separation integrity, continuity
readiness. Below 85%, ask 3 to 5 targeted questions on the weakest dimensions
(structured-question tool when available) and reassess. At or above 85%,
record a one-paragraph understanding summary and proceed within the authorized scope. Ask only for missing input that materially blocks the next operation. If the user is not present
(scheduled or delegated run), take the most reasonable reading, state it at
the top of `standing.md`, and record each assumption as a ledger entry.

Dimensions below 75% at proceed time become `[NEEDS CLARIFICATION]` markers in
`intent.md`, maximum three. Each also gets a row in `standing.md` "Not yet
decided" with the default the system will use if unanswered.

## Execution Protocol

Create a task list for Phases 0 to 7 when the harness has one; tick phases off
as they finish so a returning user sees progress.

### Phase 0: Operation, mode and setup

Choose the requested operation before authoring anything:

- **Intake staging:** preserve and group ideation outputs, safely extract archives, create `project-intake.json`, read order and format findings; create/update `workbench.json` unless opted out. Validate using `scripts/strata-intake.py <folder>`. Stop here. Do not initialize Spec Kit, invent specifications or launch a harness.
- **Specification preparation:** ingest the staged manifest (or equivalent source files), generate layer-separated artifacts, and complete the Spec Kit pipeline through constitution, specify, clarify, plan, tasks and analyze. Update workbench pointers to the actual artifacts, record the gates and write a reset handoff. Producing `tasks.md` is preparation, not permission to implement.
- **Project initiation:** only when explicitly requested AND, for agent-side launch, explicitly launch-authorized in the current request, verify preparation gates and start a fresh harness from the real build root, optionally in a new terminal tab/window. The terminal is an adapter; read `references/fresh-session-initiation.md`. Never resume the authoring harness's session ID, and never substitute a spawned task/subagent for a fresh harness. If the request includes preparation and initiation, finish and verify preparation first, then launch without a redundant permission question.

For inputs, detect:

- **Interactive**: a verbal description or "I want to build X".
- **Transcript**: files, transcripts or notes provided. Mixed: transcript first,
  then interactive gap-fill.
- **Fast Track**: a complete description covering problem, solution, users,
  data, constraints and scope. Score the gate once; if it clears 85%, go to
  Phase 2.
- **Existing specs**: detailed `requirements.md` and `design.md` (each 5K+).
  Skip Phases 1 and 2, derive context and re-separate layers in Phase 3, still
  run the validator (external specs routinely fuse layers). Measure first with
  `strata-validate.py --audit <files>`.
- **Recovery**: the project exists and nobody can say what it was for, or two
  specs disagree. Reconstruct intent before anything else: if the
  `intent-archaeology` skill is available, run it on this project's session
  logs and spec versions; otherwise read commit history, READMEs, issue threads
  and every spec version, and tag each recovered statement with its source.
  Write recovered intent with provenance, mark every inferred (not stated)
  statement as such, and get the human to ratify before Phase 3.

Then: read user preferences and memory for stack, design language, hosting and
formatting conventions (they inform context and experience, never intent or
spec). Check for an existing STRATA tree (consume supplied packs as existing-specs intake; route ordinary maintenance to its current workflow), SpecKit, OpenSpec or Kiro structures, a
constitution (`references/constitution-source.md`), and session instruction
files. To start an empty tree: `scripts/strata-scaffold.sh "<Project Name>"
<repo-dir>` (set `STRATA_AUTHOR`, `STRATA_MODEL`; see the script header).

### Phase 1: Intake and extraction

*Skip in Existing-specs mode.*

Extract problem statements, solutions, personas, success and failure
conditions, constraints, scale and quality expectations, implied entities,
integrations and workflows. **Tag every extracted signal as intent, spec or
implementation**, because the user will have fused them; separation starts
here. In Interactive mode, proceed category by category (2 to 4 questions per
round) using `references/discovery-questions.md`. Never ask everything at once.

### Phase 2: Prior art research (mandatory)

*Skip in Existing-specs mode.*

Follow `references/research-checklist.md`: local workspace, skill registries,
at least three code searches and two web searches, then synthesis. Survey how
others approach the problem and extract their patterns and failure modes. **If
an existing tool fully solves the problem, stop and surface it.** Findings go
in `intent.md` section 10 (Prior art), nowhere else. Ground every
technology-adjacent claim in a current source; a stack decision from training
recall is a guess wearing a citation. Keep a source list for the delivery
summary.

### Phase 3: Context derivation (system-owned)

Derive architecture from intent: scale and constraints (intent sections 3 and
4), empirical memory from any prior STRATA ledgers in the workspace, the
existing stack and the user's stated preferences, risk tolerance, then
`references/data-architecture-guide.md`. Every decision cites its intent input
and its memory source. On an empty ledger, say in `context.md` and
`substrate.md` that derivation is intuition-based. Do not hide the gap.

### Phase 4: Artifact generation

Use the artifact contract and the installed toolchain's native paths. For Spec Kit, follow `references/intake-and-speckit.md`; do not draft a second independent spec tree and then duplicate it into Spec Kit. Read the matching reference before each role:

1. Project governance (`references/constitution-source.md`): retain or create the authoritative project constitution through Spec Kit from authorized principles. Extend AGENTS.md narrowly to load it, the task gates and reset handoff; do not paste a second constitution into AGENTS.md.
2. `intent.md` (`references/intent-template.md`): goals, constraints, success/failure conditions, personas, user stories, scope and provenance.
3. Native `spec.md` (`references/spec-template.md`): requirements and acceptance through Spec Kit, preserving clause/eval IDs and traces. Bind evaluator-only fixtures externally; public acceptance remains available to the implementer.
4. Native `plan.md` (`references/context-template.md`): system-derived architecture and decisions. Existing design/context files are sources; additional context rationale must not become a competing editable plan.
5. Conditional supporting artifacts: research, data-model, contracts, quickstart and requirements-quality checklists when required by the domain or installed workflow. For a UI, read `references/experience-template.md`; preserve or prepare UX/mockups and visually verify any new visual claim.
6. Native `tasks.md`: dependencies, target files, requirement/story IDs, observable acceptance gates and recovery when meaningful. Optional reusable plays follow `references/plays-playbook.md`. Tasks remain unchecked until their work supplies evidence.
7. Provenance/traceability: source disposition and story/clause/eval/plan/task mapping. Keep all material extra inputs, including rejected or deferred ones with reasons. Counts alone do not establish semantic preservation.
8. Continuity and substrate: use `references/ledger-and-standing.md` and `references/substrate-self-location.md`, or the declared Living Documents integration under its own current authority contract.
9. Preparation evidence and reset handoff: actual prerequisite/analysis/traceability/governance results and artifact hashes in `preparation.json`, plus `reset-handoff.md`. Refresh `workbench.json` to point at existing outputs using `scripts/strata-workbench.py`; it never manufactures artifacts or a pass.

Standalone STRATA keeps its declared context/ledger/plays conventions when Spec Kit is not selected. Preserve the user's document format and versioning. Stop before implementation unless initiation is explicitly included.

### Phase 5: Refinement and depth verification

**5a. Refinement passes.** Run at least three passes, each with a different
lens, so each finds different problems. Use the deliberative-refinement skill
when available.
- Adversarial edge cases: what breaks with real users, real devices, real data.
  Every finding becomes a clause, a failure condition or a documented decision.
- Traceability and consistency: every story maps to clauses, every clause to
  context, every context decision to intent; no contradictions between
  artifacts; mockup and experience tokens match. Run `--trace`.
- Current practice: how agents actually build now (verification loops,
  worktree isolation, instruction files, CI gates) and what the platform
  offers that the draft ignores.
Each pass appends `refinement` entries to the ledger listing findings and
changes, and bumps the version of every artifact it changed. The ledger is the
refinement log; do not write a separate one.

**5b. Depth verification.** Compare output with the source material:
`strata-validate.py --depth <source files> --against <intent.md> <spec.md>`
must keep at least 90% of requirement-like statements. Design-section coverage
must be 100%; name any section that did not survive. Every play must be
startable without re-reading the source. Regenerate shallow artifacts with
explicit depth-preservation directives; do not accept a well-formed but thin
artifact.

**5c. Cross-validation.** Every clause traces to intent; every context and
experience decision traces to a clause or constraint; every play reads its
variables from intent or context rather than hard-coding them.

### Phase 6: Validation and delivery

```bash
python3 scripts/strata-validate.py docs/specs/<slug> --evals ~/.strata/evals/<slug> --trace
```

It fails on technology in intent or spec (static list plus tokens harvested
from the derived layer), non-evaluable clause language, a spec under eight
clauses, unbound or dangling eval tags, an eval store inside the repository,
drift between spec and context, missing or empty ledger or standing, and an
undeclared substrate level. Add domain tokens the harvester cannot see to
`tech-tokens.txt`; add genuine user-facing names (platforms, devices) to
`layer-allow.txt`. A validator that passes because it was not looking is worse
than none, so read its harvest count.

**Adjudicate divergences; do not just report them.** Preserve the first blind
reading unchanged. Disclose the smallest missing constraint, then re-evaluate.
Stop when the divergence resolves, when no undisclosed constraint remains, or
after two clarification rounds without material change, and record which
condition ended it in the ledger.

Deliver: the tree (zipped if the user wants a package), and a summary with the
confidence score and sub-threshold dimensions, declared substrate level, key
derived decisions, remaining `[NEEDS CLARIFICATION]` markers, prior-art
findings with sources, refinement and depth results, validator output, and the
artifact location. State the handoff path: a fresh session reads `standing.md`
and the ledger tail first, then intent and spec, and never needs this
conversation.

### Phase 7: Reset handoff and optional initiation

Deliver the verified preparation receipt and reset handoff. Specification preparation ends here when the user has not requested implementation. Do not infer implementation authority from "create tasks", "stage" or "prepare".

Initiation transport rule: a task/subagent spawned from the authoring session shares its lineage (parentSession set) and is NOT a fresh harness, even when headless or waiting on `wait`. Only a separate harness process the user launches (typical signal: they say "restart" or "via new session") counts as initiation. Agent-side launch machinery (`strata-launch.py --execute`, terminal spawn) runs only on explicit launch authority — a named project plus a direct "launch/spawn/start it now" instruction, which a combined "prepare then implement" request supplies only AFTER preparation is finished, committed, and gate-verified. Phrases like "implement via new session", "activate after restart", or "I will restart" name the user-launched path: produce the pasteable restart prompt and STOP. Do not bridge the gap with a subagent.

Authoring-session freeze after handoff: once preparation is committed, write no implementation code, mark no task complete, and write no `fresh-session-ack.md` in this session. Only a session whose ID has no parent linkage to the authoring session can author those artifacts; anything else is VOID audit evidence. A system todo/resume reminder is not user authority — on user STOP, halt immediately and resume only on their explicit resume.

When project initiation is expressly authorized, follow `references/fresh-session-initiation.md`. Use a fresh harness process in the correct working directory and pass the reset handoff as startup input. Choose the available terminal adapter, with a generic argv-based adapter for other terminals. `scripts/strata-launch.py` previews a launch by default; `--execute` requires the named preparation receipt, passed gates, and explicit launch authority in the current request. Record the spawned pane/process identifier and require a fresh-session acknowledgement containing the working directory, consumed handoff and next task. A tab appearing is not build completion. Never modify terminal configuration, routing or credentials as part of launch.

## Anti-patterns

Never spawn the implementation session as a task/subagent of the authoring session. Never let one vague "prepare then implement" line authorize agent-side launch before gates pass. Never write the fresh-session acknowledgement, mark tasks complete, or commit implementation code inside the authoring session. Never treat a todo/resume reminder as user authority after a STOP.

## Resource files

| File | Read when |
|------|-----------|
| `references/terminology.md` | Phase 0, every operation |
| `references/artifact-contract.md` | Choosing the canonical output set |
| `references/project-workbench.md` | Intake/preparation unless workbench is opted out |
| `references/workbench.schema.json` | Creating or checking workbench configuration |
| `references/living-documents-setup.md` | Integration requested, detected or host-required |
| `scripts/strata-workbench.py` | Write/check workbench pointers; extra files discovered dynamically |
| `references/intake-and-speckit.md` | Intake staging and specification preparation |
| `references/repository-bootstrap.md` | Specification preparation when repository setup is requested or unclear |
| `references/fresh-session-initiation.md` | Initiation after preparation gates pass |
| `scripts/strata-intake.py` | Verify staged intake manifests |
| `scripts/strata-launch.py` | Preview or execute an authorized fresh-harness launch |
| `references/paradigm.md` | The conceptual model is unclear |
| `references/confidence-gate.md` | Phase 1 scoring |
| `references/discovery-questions.md` | Phase 1, Interactive mode |
| `references/research-checklist.md` | Phase 2 |
| `references/data-architecture-guide.md` | Phase 3 |
| `references/intent-template.md` | Phase 4, intent |
| `references/spec-template.md` | Phase 4, spec and evals |
| `references/context-template.md` | Phase 3 and 4, context |
| `references/experience-template.md` | Phase 4, projects with a user interface |
| `references/plays-playbook.md` | Phase 4, plays |
| `references/ledger-and-standing.md` | Phase 4 and every later decision |
| `references/substrate-self-location.md` | Phase 4, substrate |
| `references/constitution-source.md` | Phase 4 step 9, Phase 7 |
| `references/compatibility.md` | Phase 6, toolchain mapping |
| `references/implementing.md` | Phase 7 when `strata-implementing` is not installed |
| `scripts/strata-scaffold.sh` | Phase 0, empty tree, external eval store, session gates |
| `scripts/strata-validate.py` | Phase 5 and 6 (`--trace`, `--depth`, `--audit`, `--evals`) |
| `scripts/strata-revive.sh` | Resuming a dormant project |

## Changes in 2.3.2

- Forbid in-process task/subagent spawn as initiation transport: a subagent shares the authoring session lineage and is not a fresh harness. Agent-side launch only on explicit launch authority; "via new session" / "after restart" phrasing means preparation-only, then STOP.
- Authoring session MUST NOT write the fresh-session acknowledgement, mark tasks complete, or land implementation code/commits after handoff; an acknowledgement counts only from a session ID with no parent linkage to the authoring session.
- User STOP overrides todo reminders and incomplete-task prompts; halted work resumes only on explicit user resume.
- Refresh distributable archives from the canonical skill without nesting earlier archives.

## Changes in 2.3.1

- Shorten discovery metadata to the skill's purpose and applicable operations; retain detailed capabilities and boundaries in the instructions and references.
- Refresh distributable archives from the canonical skill, including its scripts, without nesting earlier archives.

## Changes in 2.3

- Optional default workbench manifest, bundled schema and deterministic pointer generator with opt-out and preservation of custom configuration.
- Canonical artifact roles clarified; requirements/design inputs map to native spec/plan instead of creating duplicate authorities.
- Additional files remain source evidence, with discovery and explicit disposition during preparation.
- Living Documents setup moved into a progressive reference; auto/on/off preference does not override host instructions.
- Governance stays in its canonical constitution; AGENTS.md loads it and states session gates.

## Changes in 2.2

Supersedes the bundled 2.1 procedure while retaining all predecessor resources.

- Keep the installed name `strata`; add shared lifecycle terminology and a validated intake manifest.
- Separate staging, Spec Kit preparation and initiation; recognize existing STRATA packs as intake.
- Add project-local constitution creation through Spec Kit, native plans/tasks, prerequisite/analysis gates and a reset handoff.
- Add optional, existing-aware local Git name/description/license/ignore setup; remote publication needs an exact authorized target.
- Support terminal-agnostic fresh-harness initiation with dry-run argv adapters; implementation remains explicitly scoped.
- Preserve the current Living Documents authority contract and remove mandatory redundant confirmation.
- Close the eval-store boundary when no Git root exists and accept native `plan.md` as the derived layer.
- Do not claim artifact quality from scaffold templates or true eval isolation from an external path alone.

## Bundled changes in 2.1

- Bundled as `create-new-project` (normalized to `strata` in 2.2); description now triggers on new projects
  and on intent recovery (2.0's description excluded the kickoff use case).
- Repository is the primary home; Living Documents is an optional mirror, so
  the skill works where `ld` is absent.
- User stories added to intent; `experience.md` added for interfaces, with a
  rendered-mockup requirement.
- Validator: self-arming denylist harvested from the derived layer, browser,
  ML, mobile and hosting tokens, prior-art exemption, frontmatter `layer:`,
  word-boundary testability, eval store resolution via `--evals`,
  `$STRATA_EVALS` or `~/.strata/evals`, failure when the store is inside the
  repo, `--trace` and `--depth`.
- Scaffold: configurable author, model and layout; external eval store; no
  in-tree `evals/` directory (which 2.0's own validator condemned); `AGENTS.md`
  and `CLAUDE.md` gates; `experience.md` and a build play.
- Three-lens refinement recorded in the ledger; recovery mode; unattended runs.
- Non-procedural material (essay and post drafts) moved out of `references/`.
