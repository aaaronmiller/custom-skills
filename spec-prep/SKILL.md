---
name: spec-prep
description: >-
  Prepare and refine project intent, requirements, design, and native Spec Kit
  specifications, plans, and tasks. Use for project intake, existing spec-package
  updates, intent recovery, or explicitly requested project initiation. Use
  spec-audit for post-hoc implementation drift audits.
license: MIT
metadata:
  version: "2.5.1"
  lineage: "create-new-project 1.x + STRATA (renamed spec-prep)"
  author: "ice-ninja"
  conceptual-source: "Kapil Viren Ahuja, Spec-Driven Development Isn't Broken. It will collapse. (2026-05-03)"
  conceptual-source-url: "https://medium.com/activated-thinker/spec-driven-development-isnt-broken-it-will-collapse-c00609f72496"
  methodology-source: "STRATA naming, article and initial skill: Claude assistant (Sliither), synthesized at ice-ninja's request from Ahuja, create-new-project and Spec Kit; vault copy dated 2026-05-18"
  methodology-source-link: "https://claude.ai/chat/efefe910-3b55-4129-bf10-3411bc95bab3"
  craft-allocation-source: "Kapil Viren Ahuja: human intent/spec; system context/prompt; Jones supplies craft vocabulary"
  substrate-stack-source: "Kapil Viren Ahuja: Levels 1-5; distinct from Shapiro autonomy levels and legacy STRATA S0-S5"
  attribution-reference: "references/paradigm.md"
  tags: "spec-driven, intent, planning, coding"
---

# spec-prep 2.5.1

> Separation of Tiers, Retention Across Time, Auditability. From brain dump to
> build-ready, pivot-resilient, dormancy-proof artifacts.

This skill stages ideation outputs and prepares specifications with Spec Kit. It stops before implementation unless the current request explicitly includes project initiation. Read `references/terminology.md` before choosing an operation and `references/intake-and-speckit.md` when consuming a staged folder.

Routine debugging, code review and maintenance use their existing workflows. Supplied spec-prep packs remain valid preparation inputs.

## Why this exists

Intent is a maintained asset in its own right, alongside requirements and design. Preserve why the user wants the project and its constraints independently of the observable contract and derived technical choices. This makes pivots and recovery reviewable without silently rewriting the brief.

The three-layer framing, human/system craft allocation and Substrate Stack are credited to Kapil Viren Ahuja. The user-supplied originating transcript shows that a Claude assistant, speaking as Sliither, coined STRATA and drafted its article and initial skill as a synthesis requested by ice-ninja, using the existing create-new-project skill and Spec Kit. This generated synthesis is not an independent external evaluation. STRATA is this skill's former name, not an inference engine. Read `references/paradigm.md` for source attribution, authority boundaries and the current interpretation of both articles. Its consolidation table explains which historical claims were retained or qualified.

## Where artifacts live

**Resolve the operation and the authoritative paths first.** A staged intake folder contains source evidence, not an implementation checkout. For specification preparation, use the actual project repository and Spec Kit's native `specs/<feature>/` plus `.specify/memory/constitution.md`. Existing spec-prep layouts remain accepted as migration inputs; do not overwrite or reject a supplied spec pack merely because it already contains spec-prep files.

Workbench mode defaults to `auto`: emit a portable `workbench.json` that points to the intake and actual artifacts, unless the user opts out. Read `references/project-workbench.md` for this operation. Keep extra source files, infer roles conservatively and record their disposition; unknown content does not disappear because it lacks a recognized name.

Living Documents is a progressive optional integration for the portable skill. Read `references/living-documents-setup.md` when requested, detected or required by current host instructions. Reuse the installed system's contract; do not force installation or duplicate its canonical content.

Read `references/artifact-contract.md` when choosing outputs. The default contract is intake/workbench, intent, native spec/plan/tasks, project constitution, scoped agent instructions, provenance/traceability, continuity, preparation evidence and reset handoff. Existing requirements/design files are accepted sources or declared conventions. Conditional artifacts include UX, research, data models, contracts, quickstart, quality checklists, plays and evaluator-only fixtures. Do not generate duplicate requirements/spec or design/plan authorities merely to fill a file list.

## The six rules (workflow obligations with bounded mechanical checks)

1. **Separation.** A technology, framework or library token in intent or spec is
   a defect. A spec clause that cannot become a pass/fail evaluation is a
   defect. Preserve explicit user constraints and product names with a justified `layer-allow.txt` entry rather than deleting them. The validator fails the build on leaked choices, and it self-arms by
   harvesting every technology the derived layer names.
2. **Authorship and provenance.** Preserve direct user instructions and accepted decisions. Distinguish assistant proposals, inherited assumptions and observed results; uploading an assistant draft does not ratify every line. Authorized reversible preparation may continue with explicit provisional defaults. Ask only where a material missing decision blocks its dependent action. Do not require the user to reapprove their own instructions or infer authority from silence. Keep full source prompts once under sources/ and map material needs to their destination.
3. **Eval binding.** Every spec clause carries an `EVAL-ID` bound to a defined
   evaluation in the external evaluation store (default
   `~/.spec-prep/evals/<slug>/evals.md`). The validator rejects stores inside the build root even without Git. An external directory alone is not an access-control boundary: genuine held-out evaluation requires an evaluator context whose files and tools are inaccessible to the implementing agent. Keep public acceptance visible; label evaluator-only tests held-out only when that isolation exists. Disclose isolation that has not been established.
4. **Change propagation.** Goal changes begin in intent. Behavior corrections belong in spec, architecture corrections in plan and workflow defects in the skill/governance. Reconcile affected contracts, tasks, acceptance, traceability and receipts. Update plays only when their workflow or variables change. Do not invent a product requirement to justify a tooling correction.
5. **Continuity.** Material decisions, outcomes and task-state changes are appended to the ledger;
   refresh `standing.md` when the resumable state changes. This
   prevents the dreamstate: a dormant project whose resumption costs days of
   archaeology.
6. **Honesty.** `substrate.md` states the real substrate level and the real
   pre-lock versus live-resolve boundary. Do not record certainty the project
   has not earned.

## Confidence Gate

Use `references/confidence-gate.md` to diagnose completeness. Its dimensions and optional weighted score are advisory, not probabilities or permission gates. Continue authorized reversible preparation when the next step is adequately grounded. State material assumptions and stop only the action dependent on an unavailable decision. Respect the installed native template's clarification format; do not discard other unresolved source needs to satisfy a marker limit. No confidence score changes the requested delivery mode.

## Execution Protocol

Create a task list for Phases 0 to 7 when the harness has one; tick phases off
as they finish so a returning user sees progress.

### Phase 0: Operation, mode and setup

Choose the requested operation before authoring anything. Use proportional depth based on risk, novelty, uncertainty and coordination; outcome-led delegation to a capable agent is not the same as unreviewed vibe coding. Read the proportionality guidance in `references/paradigm.md` when deciding how much supporting structure is useful. This never changes the requested output mode or waives its gates. Read `references/artifact-contract.md` for the compact core-input interface and operation-specific gates. Requested filenames do not silently select standalone mode; missing tooling does not change the requested operation. If native execution is unavailable, deliver the complete input handoff, record native preparation as incomplete and identify the next preparation step. Standalone non-Spec-Kit output requires explicit selection. When auditing or modifying this skill itself, the target is the canonical skill folder, not a project's spec/plan outputs. Resolve the real installed name/path before editing; a user saying “spec-plan” may mean spec-prep, but inspect rather than minting a second skill. Application files are examples unless independently in scope.

For preparation, select:

- **Intake staging:** preserve and group ideation outputs, safely extract archives, create `project-intake.json`, read order and format findings; create/update `workbench.json` unless opted out. Validate using `scripts/spec-prep-intake.py <folder>`. Stop here. Do not initialize Spec Kit, invent specifications or launch a harness.
- **Spec Kit input handoff:** create one complete requirements.md/design.md/intent.md trio per workstream, preserve sources, prepare or preserve governance and scoped instruction wiring, and give the exact conversion read order. Use `references/artifact-contract.md`. Do not manufacture native tasks or a native preparation pass. The next operation is specification preparation, never implementation.
- **Specification preparation:** ingest the staged manifest (or equivalent source files), generate layer-separated artifacts, and complete the Spec Kit pipeline through constitution, specify, clarify, plan, tasks and analyze. Update workbench pointers to the actual artifacts, record the gates and write a reset handoff. Producing `tasks.md` is preparation, not permission to implement.
- **Project initiation:** only when explicitly requested AND, for agent-side launch, explicitly launch-authorized in the current request, verify preparation gates and start a fresh harness from the real build root, optionally in a new terminal tab/window. The terminal is an adapter; read `references/fresh-session-initiation.md`. Never resume the authoring harness's session ID, and never substitute a spawned task/subagent for a fresh harness. If the request includes preparation and initiation, finish and verify preparation first, then launch without a redundant permission question.

For inputs, detect:

- **Interactive**: a verbal description or "I want to build X".
- **Transcript**: files, transcripts or notes provided. Mixed: transcript first,
  then interactive gap-fill.
- **Fast Track**: a complete description covering problem, solution, users,
  data, constraints and scope. Assess the next step using the advisory rubric, then proceed to Phase 2 when sufficiently grounded.
- **Existing specs**: `requirements.md` and `design.md` (judge completeness by source coverage, not file size). Skip Phases 1 and 2, derive context and re-separate layers in Phase 3, still run the validator (external specs routinely fuse layers). Measure first with `spec-prep-validate.py --audit <files>`. When refining an existing package, use the affected-layer workflow in Phase 5 instead of treating its sources as a new brief. Authorship note: direct human instructions retain their authority. Classify mixed and assistant-authored material as source evidence; proposed defaults are not accepted decisions. Audit, trace, depth and prerequisite checks establish their actual scope, not blanket approval. No redundant re-read or ratification gate is added for the user's own instructions.
- **Recovery**: the project exists and nobody can say what it was for, or two
  specs disagree. Reconstruct intent before anything else: if the
  `intent-archaeology` skill is available, run it on this project's session
  logs and spec versions; otherwise read commit history, READMEs, issue threads
  and every spec version, and tag each recovered statement with its source.
  Write recovered intent with provenance, mark every inferred (not stated) statement as such. Direct user statements retain existing authority; inferred statements remain proposals until accepted. Authorized preparation can continue with that distinction explicit, while dependent actions wait for any genuinely required decision.

Then: read user preferences and memory for stack, design language, hosting and
formatting conventions (they inform context and experience, never intent or
spec). Check for an existing spec-prep tree (consume supplied packs as existing-specs intake; route ordinary maintenance to its current workflow), SpecKit, OpenSpec or Kiro structures, a
constitution (`references/constitution-source.md`), and session instruction
files. For an input handoff, author the three core documents and governance directly under the declared roots; do not run the legacy full-tree scaffold. For native preparation, use the installed Spec Kit workflow and its native paths. Only for explicitly selected legacy standalone authoring, `scripts/spec-prep-scaffold.sh "<Project Name>" <repo-dir>` creates templates (set `SPECPREP_AUTHOR`, `SPECPREP_MODEL`; compatible `SPEC_PREP_*` aliases are accepted). Templates are not completed specifications.

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
an existing tool fully solves the problem, stop and surface it.** Keep the user-facing gap/comparison in intent section 10 (Prior art); detailed implementation research goes in research.md or plan.md with links. Ground every
technology-adjacent claim in a current source; a stack decision from training
recall is a guess wearing a citation. Keep a source list for the delivery
summary.

### Phase 3: Context derivation (system-owned)

Derive architecture from intent: scale and constraints (intent sections 3 and
4), empirical memory from any prior spec-prep ledgers in the workspace, the
existing stack and the user's stated preferences, risk tolerance, then
`references/data-architecture-guide.md`. Every decision cites its intent input
and its memory source. On an empty ledger, disclose the absence of project-specific empirical memory in `context.md` and `substrate.md`. Distinguish current research and inspected-system evidence from intuition; an empty ledger does not make all other evidence disappear. Record user-mandated, provisional, accepted and live-resolved choices distinctly. Do not hide the gap.

### Phase 4: Artifact generation

Use the artifact contract and the installed toolchain's native paths. A skill is an executable instruction workflow, not a separate authoring service: read its current instructions and sources, then carry out its derivation and gates. Setup scripts resolve paths/templates and do not certify generated content. Directly writing a file is neither proof of compliance nor a reason to bypass the workflow. For Spec Kit, follow `references/intake-and-speckit.md`; do not draft a second independent spec tree and then duplicate it into Spec Kit. Read the matching reference before each role:

1. Project governance (`references/constitution-source.md`): retain or create the authoritative project constitution through Spec Kit from authorized principles. Extend AGENTS.md narrowly to load it, the task gates and reset handoff; do not paste a second constitution into AGENTS.md.
2. `intent.md` (`references/intent-template.md`): goals, constraints, success/failure conditions, personas, user stories, scope and provenance.
3. Native `spec.md` (`references/spec-template.md`): requirements and acceptance through Spec Kit, preserving clause/eval IDs and traces. Bind evaluator-only fixtures externally; public acceptance remains available to the implementer.
4. Native `plan.md` (`references/context-template.md`): system-derived architecture and decisions. Existing design/context files are sources; additional context rationale must not become a competing editable plan.
5. Conditional supporting artifacts: research, data-model, contracts, quickstart and requirements-quality checklists when required by the domain or installed workflow. For a UI, read `references/experience-template.md`; preserve or prepare UX/mockups and visually verify any new visual claim.
6. Native `tasks.md`: dependencies, target files, requirement/story IDs, observable acceptance gates and recovery when meaningful. Optional reusable plays follow `references/plays-playbook.md`. Tasks remain unchecked until their work supplies evidence.
7. Provenance/traceability: source disposition and story/clause/eval/plan/task mapping. Keep all material extra inputs, including rejected or deferred ones with reasons. Counts alone do not establish semantic preservation.
8. Continuity and substrate: use `references/ledger-and-standing.md` and `references/substrate-self-location.md`, or the declared Living Documents integration under its own current authority contract.
9. Preparation evidence and reset handoff: actual prerequisite/analysis/traceability/governance results and artifact hashes in `preparation.json`, plus `reset-handoff.md`. Refresh `workbench.json` to point at existing outputs using `scripts/spec-prep-workbench.py`; it never manufactures artifacts or a pass.

Standalone spec-prep keeps its declared context/ledger/plays conventions when Spec Kit is not selected. Preserve the user's document format and versioning. Compact input handoff and native output are distinct operations, not competing authorities. For a preparation-only request, stop after tasks/analyze and checks: no implement command, agent launch, queued build or implementation hook. Carry that boundary into AGENTS.md, reset-handoff.md and the receipt. A later explicit implementation request is separate authority.

### Phase 5: Refinement and depth verification

For an existing package update, read `references/refinement-and-updates.md`. Identify preserved sources, maintained inputs and native outputs; propagate the authorized delta through affected artifacts and rerun affected preparation gates before refreshing the receipt. A validation-only request reports findings without authorizing document rewrites.

**Optional Jev review.** Read `references/jev-review.md` when requested or when a bounded semantic check adds value. Use named source excerpts and an explicit target at intake, output, task-generation or governance review; during implementation, review evidence only within existing authority. Keep hashes, arithmetic, ID/path checks and constitution heading comparisons deterministic. `scripts/spec-prep-jev.py` previews offline by default and supports the typed OpenCode decision API. Advice, abstention and unavailable provider results never override gates or write requirements/tasks.

Jev is an optional enhancement, never a prerequisite for this skill. Use it only when an eligible tool or adapter, network access, credentials and authorization to send the selected excerpts are already available. In any local or hosted agent environment, including Claude Code cloud and OpenAI cloud agents, assess actual capabilities rather than assuming access from the platform name. If Jev is disabled, unavailable or fails, record `not_run` with the reason and continue the required deterministic checks and agent-mediated semantic review. Label self-review as self-review; independent review remains independent only when a separate reviewer actually performed it. Do not install tools, request credentials, change providers, spend money or block preparation solely to enable Jev. Never relabel ordinary model reasoning as a Jev verdict or waive another required gate because Jev is absent.

**5a. Refinement passes.** Run at least three passes, each with a different
lens, so each finds different problems. Use the deliberative-refinement skill
when available.
- Adversarial edge cases: what breaks with real users, real devices, real data.
  Classify each finding by its owning layer; repair the affected artifact and dependents without inventing product scope.
- Traceability and consistency: every story maps to clauses, every clause to
  context, every context decision to intent; no contradictions between
  artifacts; mockup and experience tokens match. Run `--trace`.
- Current practice: how agents actually build now (verification loops,
  worktree isolation, instruction files, CI gates) and what the platform
  offers that the draft ignores.
Each pass appends `refinement` entries to the ledger listing findings and
changes, and bumps the version of every artifact it changed. The ledger is the
refinement log; do not write a separate one.

**5b. Semantic preservation.** Maintain one material source-disposition map: preserved, changed with reason, deferred, rejected or unavailable, with destination and provenance. Preserve design-section coverage and all material constraints. Run --depth as a coarse diagnostic only; added unrelated requirements cannot compensate for missing intent, and shorter line counts alone do not prove loss. Inspect task inputs, affected paths, dependencies, observable acceptance and recovery. Do not pad clauses or tasks to meet a count or word floor. Missing material obligations must be resolved or explicitly left incomplete.

**5c. Cross-validation.** Every clause traces to intent; every context and
experience decision traces to a clause or constraint; every play reads its
variables from intent or context rather than hard-coding them.

### Phase 6: Validation and delivery

```bash
python3 scripts/spec-prep-validate.py docs/specs/<slug> --evals ~/.spec-prep/evals/<slug> --trace
```

It fails on technology in intent or spec (static list plus tokens harvested
from the derived layer), non-evaluable clause language, an empty specification or duplicate clause IDs, unbound or dangling eval tags, an eval store inside the repository,
drift between spec and context, missing or empty ledger or standing, and an
undeclared substrate level. This is mechanical document validation, not proof of semantic completeness, native workflow execution or runtime feasibility. Add domain tokens the harvester cannot see to
`tech-tokens.txt`; add genuine user-facing names (platforms, devices) to
`layer-allow.txt`. A validator that passes because it was not looking is worse
than none, so read its harvest count.

Before writing the receipt, reconcile any changed upstream artifact with the affected plan/tasks/contracts and run the relevant installed analysis/prerequisite checks. Hash the final written standing/ledger and all consumed artifact versions, including aliases consistently. Record actual commands, exit status and reviewer findings; do not claim a model verdict when its endpoint failed. Confirm the selected harness can actually discover the implementation workflow and instruction wiring; a skill installed only for another disabled provider is not launch readiness.

**Adjudicate divergences; do not just report them.** Preserve the first blind
reading unchanged. Disclose the smallest missing constraint, then re-evaluate.
Stop when the divergence resolves, when no undisclosed constraint remains, or
after two clarification rounds without material change, and record which
condition ended it in the ledger.

Deliver: the tree (zipped if the user wants a package), and a summary with the
confidence score and sub-threshold dimensions, declared substrate level, key
derived decisions, remaining `[NEEDS CLARIFICATION]` markers, prior-art
findings with sources, refinement and depth results, validator output, and the
artifact location. Name each core input or native artifact path and the actual operation completed. Required preparation gates must pass before claiming native preparation. Keep not-run product/hardware/evaluator execution distinct from document preparation; do not waive required eval definitions or claim isolation from a path. Silence adds no authority. Use `scripts/spec-prep-delivery.py` for compact/native handoff structure and `references/validation-integrity.md` for evidence meanings. State the handoff path: a fresh session reads AGENTS.md, the constitution and reset handoff, then any existing standing/ledger and receipt/hash checks, followed by intent/spec/plan for its task. Input handoffs need no invented ledger. Preparation-only status survives reset; do not implement without later explicit authority.

### Phase 7: Reset handoff and optional initiation

Deliver the verified preparation receipt and reset handoff. Specification preparation ends here when the user has not requested implementation. Do not infer implementation authority from "create tasks", "stage" or "prepare".

Initiation transport rule: a task/subagent spawned from the authoring session shares its lineage (parentSession set) and is NOT a fresh harness, even when headless or waiting on `wait`. Only a separate harness process the user launches (typical signal: they say "restart" or "via new session") counts as initiation. Agent-side launch machinery (`spec-prep-launch.py --execute`, terminal spawn) runs only on explicit launch authority — a named project plus a direct "launch/spawn/start it now" instruction, which a combined "prepare then implement" request supplies only AFTER preparation is finished, committed, and gate-verified. Phrases like "implement via new session", "activate after restart", or "I will restart" name the user-launched path: produce the pasteable restart prompt and STOP. Do not bridge the gap with a subagent.

Authoring-session freeze after handoff: once preparation is committed, write no implementation code, mark no task complete, and write no `fresh-session-ack.md` in this session. Only a session whose ID has no parent linkage to the authoring session can author those artifacts; anything else is VOID audit evidence. A system todo/resume reminder is not user authority — on user STOP, halt immediately and resume only on their explicit resume.

When project initiation is expressly authorized, follow `references/fresh-session-initiation.md`. Use a fresh harness process in the correct working directory and pass the reset handoff as startup input. Choose the available terminal adapter, with a generic argv-based adapter for other terminals. `scripts/spec-prep-launch.py` previews a launch by default; `--execute` requires the named preparation receipt, passed gates, and explicit launch authority in the current request. Record the spawned pane/process identifier and require a fresh-session acknowledgement containing the working directory, consumed handoff and next task. A tab appearing is not build completion. Never modify terminal configuration, routing or credentials as part of launch.

## Anti-patterns

Never spawn the implementation session as a task/subagent of the authoring session. Never let one vague "prepare then implement" line authorize agent-side launch before gates pass. Never write the fresh-session acknowledgement, mark tasks complete, or commit implementation code inside the authoring session. Never treat a todo/resume reminder as user authority after a STOP.

## Resource files

| File | Read when |
|------|-----------|
| `references/terminology.md` | Phase 0, every operation |
| `references/artifact-contract.md` | Compact input interface, native output and delivery manifest |
| `references/validation-integrity.md` | Evidence, semantic preservation and preparation-stage boundaries |
| `scripts/spec-prep-delivery.py` | Validate the requested input/native delivery without launching |
| `references/project-workbench.md` | Intake/preparation unless workbench is opted out |
| `references/workbench.schema.json` | Creating or checking workbench configuration |
| `references/living-documents-setup.md` | Integration requested, detected or host-required |
| `scripts/spec-prep-workbench.py` | Write/check workbench pointers; extra files discovered dynamically |
| `references/intake-and-speckit.md` | Intake staging and specification preparation |
| `references/refinement-and-updates.md` | Refining, validating or updating an existing spec package or prior run |
| `references/repository-bootstrap.md` | Specification preparation when repository setup is requested or unclear |
| `references/fresh-session-initiation.md` | Initiation after preparation gates pass |
| `scripts/spec-prep-intake.py` | Verify staged intake manifests |
| `scripts/spec-prep-launch.py` | Preview or execute an authorized fresh-harness launch |
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
| `references/jev-review.md` | Optional bounded semantic checks and typed provider adapter |
| `scripts/spec-prep-jev.py` | Offline preview or explicitly authorized advisory Jev call |
| `tests/` | Verify validator and Jev adapter regressions |
| `references/implementing.md` | Phase 7 when `spec-prep-implementing` is not installed |
| `scripts/spec-prep-scaffold.sh` | Phase 0, empty tree, external eval store, session gates |
| `scripts/spec-prep-validate.py` | Phase 5 and 6 (`--trace`, `--depth`, `--audit`, `--evals`) |
| `scripts/spec-prep-revive.sh` | Resuming a dormant project |

## Changes in 2.5.1

- Preserve the 2.4.0 native preparation and constitution/reset pattern; provide one complete input trio per workstream and an operation-specific delivery gate.
- Keep selected 2.4.1 utility fixes/tests and optional Jev; retain compatible environment spellings, wrapped clauses, native story IDs and flat/nested continuity.
- Selectively adopt provenance, duplicate-ID/eval checks, evidence boundaries and portable pointers from the separately developed 2.5.0; reject its incompatible regressions.
- Keep governance active through scoped AGENTS.md/harness wiring and explicitly stop after preparation, including across reset and extension transitions.
- Preserve raw inputs and legacy receipts without creating competing specification authorities or silently migrating existing projects.

## Changes in 2.4.1

- Add optional stage-specific Jev advice through a preview-first typed OpenCode adapter; truthful client identification, safe existing-global-key loading and sanitized error diagnostics; no project edits, paid fallback or gate authority.
- Make skill-versus-application scope explicit and clarify workflow execution, final receipt hashing and actual harness discovery.
- Retain the validator identifier fix; accept flat continuity files while rejecting divergent aliases, exempt native story IDs, and inspect wrapped clause text.
- Fix scaffold shell variable names to SPECPREP_* and align the read-only revive helper with flat/nested continuity.
- Replace the obsolete implementation reference with current lifecycle pointers and use semantic task-depth checks instead of a word-count gate.

## Changes in 2.4.0

- Supersede spec-workflow: CREATE/IMPLEMENT gates absorbed (Mode C, depth-preservation, 80-word density heuristic, per-category done-criteria merged; spec-workflow retired). AUDIT gate split out to standalone spec-audit skill (backtranslation, cold-pass, drift taxonomy preserved). Trigger phrases consolidated; audit triggers routed to spec-audit.

## Changes in 2.3.3

- Historical ratification policy, superseded in 2.5.1 by source-specific authority and explicit provisional defaults; silence does not create authorization.

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

- Keep the installed name `spec-prep`; add shared lifecycle terminology and a validated intake manifest.
- Separate staging, Spec Kit preparation and initiation; recognize existing spec-prep packs as intake.
- Add project-local constitution creation through Spec Kit, native plans/tasks, prerequisite/analysis gates and a reset handoff.
- Add optional, existing-aware local Git name/description/license/ignore setup; remote publication needs an exact authorized target.
- Support terminal-agnostic fresh-harness initiation with dry-run argv adapters; implementation remains explicitly scoped.
- Preserve the current Living Documents authority contract and remove mandatory redundant confirmation.
- Close the eval-store boundary when no Git root exists and accept native `plan.md` as the derived layer.
- Do not claim artifact quality from scaffold templates or true eval isolation from an external path alone.

## Bundled changes in 2.1

- Bundled as `create-new-project` (normalized to `spec-prep` in 2.2); description now triggers on new projects
  and on intent recovery (2.0's description excluded the kickoff use case).
- Repository is the primary home; Living Documents is an optional mirror, so
  the skill works where `ld` is absent.
- User stories added to intent; `experience.md` added for interfaces, with a
  rendered-mockup requirement.
- Validator: self-arming denylist harvested from the derived layer, browser,
  ML, mobile and hosting tokens, prior-art exemption, frontmatter `layer:`,
  word-boundary testability, eval store resolution via `--evals`,
  `$spec-prep_EVALS` or `~/.spec-prep/evals`, failure when the store is inside the
  repo, `--trace` and `--depth`.
- Scaffold: configurable author, model and layout; external eval store; no
  in-tree `evals/` directory (which 2.0's own validator condemned); `AGENTS.md`
  and `CLAUDE.md` gates; `experience.md` and a build play.
- Three-lens refinement recorded in the ledger; recovery mode; unattended runs.
- Non-procedural material (essay and post drafts) moved out of `references/`.
