---
name: spec-prep
description: "Prepares and refines project intent, requirements, design, and native Spec Kit specifications, plans, and tasks, stopping before implementation. Use for project intake, existing spec-package updates, intent recovery, explicitly requested project initiation, or when another task must produce spec-prep-ready deliverables (intent, requirements and design inputs, verbatim sources, a data section, a prior-art record). Use spec-audit for post-hoc implementation drift audits. Triggers: 'spec-prep', 'make this spec-prep ready', 'prepare the specs', 'write the requirements', 'turn this into a spec', 'spec kit', 'requirements and design', 'intent document', 'project intake', 'recover the intent', 'prior art check'."
license: MIT
metadata:
  description-reviewed: "2026-11-10"
  version: "4.1.0"
  author: "ice-ninja"
  tags: "spec-driven, intent, planning, coding"
---

# spec-prep

> Separation of Tiers, Retention Across Time, Auditability. From brain dump to
> build-ready, pivot-resilient, dormancy-proof artifacts.

This skill stages ideation outputs and prepares specifications with Spec Kit. It stops before implementation unless the current request explicitly includes project initiation. Read the terminology below before choosing an operation, and `references/intake-and-speckit.md#intake-staging-and-spec-kit-preparation` when consuming a staged folder.

Routine debugging, code review and maintenance use their existing workflows. Supplied spec-prep packs remain valid preparation inputs.

## Terminology

| Operation | Input | Result | Stop condition |
| --- | --- | --- | --- |
| Ideation | Conversations, research, sketches and decisions | Session outputs in any supported source format | Ideas captured; no preparation claim |
| Intake staging | Ideation outputs, archives or an existing spec pack | One project folder, preserved sources, project-intake.json, read order and format findings | Inputs organized; specs and build unstarted |
| Specification preparation | Staged intake and authorized project principles | Spec Kit constitution, specification, plan, tasks, applicable supporting artifacts, analysis and preparation receipt | Contracts and task gates verified; implementation unstarted |
| Fresh-session handoff | Verified preparation and reset-handoff.md | A fresh harness consumes the handoff from the real build root | New context acknowledges exact inputs and next task |
| Project initiation | Explicit implementation authority and passed preparation gates | First implementation task starts in that fresh harness | Initiation acknowledged; implementation completion is a separate outcome |

"Input handoff" means a complete requirements/design/intent trio per workstream with governance, reset instructions and the conversion guide; it is not native pipeline completion. "Stage" means intake staging. "Prepare specs" and "take through tasks" mean specification preparation. "Initiate" and an explicit request to build include project initiation. Never equate these operations.

A harness reset means a new context, not necessarily a closed terminal; reattaching the old session is not a reset (Phase 7 decides what counts as fresh). Terminal adapters only transport a validated command and working directory. An intake folder is not a project dossier or an implementation repository; use Living Documents terminology for its scope labels when available.

## How to run the gates

Where the host runs code (Python 3.11 or later; PyYAML only for `.specify/extensions.yml`), run the scripts beside this file:

```bash
python3 scripts/spec-prep-validate.py ARTIFACT_DIR --operation OPERATION --build-root BUILD_ROOT --evals EVAL_STORE --json
python3 scripts/spec-prep-validate.py --audit FILE...
python3 scripts/spec-prep-delivery.py PACKAGE_ROOT
python3 -m unittest discover -s tests -v
```

The first runs the nine validation checks on one artifact directory (native: the feature root); OPERATION is `standalone`, `native-preparation` or `input-handoff`, and `--help` lists the rest, such as `--continuity external`. The second measures supplied specs for layer fusion. The third checks `delivery.json`, a native receipt and the stop boundary. The fourth, run from the skill directory, shows each check failing on a constructed fixture.

A non-zero exit is a hard gate failure. For native preparation record the command, exit status and per-check results as the receipt's `validation` gate (`references/intake-and-speckit.md#specification-preparation`, step 10). Without code execution, apply `references/validation-and-refinement.md#the-nine-validation-checks` by hand in order, record every verdict, and label the pass hand-executed (weaker: recommend tool re-validation where possible).
Never claim a gate passed without listing each check and its outcome, or claim Spec Kit operations ran when only prose was written. A check that visible text cannot settle (a hash, for example) is `not_run` with the reason; run the rest.

## Spec Kit source policy (no vendored toolchain)

This skill bundles no Spec Kit. Its native paths (`specs/<feature>/`, `.specify/memory/constitution.md`, `specify`/`clarify`/`plan`/`tasks`/`analyze`) resolve from the installed toolchain or the upstream repository, which win over anything quoted in `references/`. Never paste Spec Kit internals here to "make it self-contained"; that creates a stale fork.

spec-prep's spec and context templates serve standalone and input-handoff; native mode uses the installed Spec Kit templates for spec.md and plan.md, and only the spec-prep rules apply (clause litmus, eval binding and EARS phrasing; derivation inputs and empty-ledger disclosure).

## Why this exists

Intent is a maintained asset in its own right, alongside requirements and design. Preserve why the user wants the project and its constraints independently of the observable contract and derived technical choices, so pivots and recovery are reviewable without silently rewriting the brief.

## Two ways this skill is used

1. **Invoked.** The skill runs its phases and gates below.
2. **Referenced.** Another task is told to "prepare for spec-prep" or "make this spec-prep ready" without invoking it. The reading model uses this file and `references/artifact-contract.md#canonical-artifact-contract` as a format contract only: it shapes its deliverables as a compact input handoff (the intent, requirements and design trio, `sources/` with verbatim prompts, a source-disposition map, supporting material, a conversion guide, delivery.json) with the governance set the delivery checker requires (a constitution draft at `.specify/memory/constitution.md`, build-root AGENTS.md, reset-handoff.md, an optional CLAUDE.md adapter), and completes or schedules the prior-art gate.
   A referenced use never authors native Spec Kit outputs, never writes a receipt and never claims preparation ran. It records `operation: input-handoff` and leaves specification preparation as the next operation.

Listed artifacts are the minimum shape, not the complete set: data, references, corpora and any other project-specific resource are preserved ("Supporting material" in the artifact contract), never dropped for lacking a table entry.

## Prior-art gate

Before Phase 4 writes plan or tasks, one of these must be true and recorded in the source-disposition map:

- **done**: a prior-art record exists (intent section 10, or a supplied record under `sources/` that section 10 summarizes) with the searches run, the closest projects, and a verdict: build new, fork, extend, or use as is;
- **directed**: the user or the current task schedules the survey as the next step; preparation may continue through intent and spec, but plan and tasks wait until the record lands;
- **waived**: the user explicitly waived it, with the reason recorded.

Record it as a line `prior-art: <done|directed|waived>; <record location, directive or reason>` in the source-disposition map, or as `priorArt` in delivery.json; a nonempty intent section 10 counts as done. None of the three is a gate failure. The gate applies in every intake mode, including Existing-specs and referenced use, because supplied specs routinely omit prior art. If the record shows an existing project fully solves the problem, stop and surface it as `references/intake-checklists.md#prior-art-research-checklist` describes.

## Where artifacts live

**Resolve the operation and the authoritative paths first.** A staged intake folder holds source evidence, not an implementation checkout. Specification preparation uses the actual project repository with Spec Kit's native `specs/<feature>/` and `.specify/memory/constitution.md`. Existing spec-prep layouts remain accepted as migration inputs; never overwrite or reject a supplied spec pack because it already contains spec-prep files.

Workbench mode defaults to `auto` (`references/artifact-contract.md#optional-default-project-workbench`) unless the user opts out. Keep extra source files, infer roles conservatively and record their disposition. Living Documents is optional: read `references/continuity.md#optional-living-documents-integration` when requested, detected or required by host instructions; never force installation or duplicate its canonical content.

Choose outputs with `references/artifact-contract.md#canonical-artifact-contract`, which owns the default and conditional artifact sets. Existing requirements/design files are accepted sources or declared conventions. Do not generate duplicate requirements/spec or design/plan authorities merely to fill a file list.

## The six rules (workflow obligations with bounded mechanical checks)

1. **Separation.** A technology, framework or library token in intent or spec is a defect, and so is a spec clause that cannot become a pass/fail evaluation. Tokens are: `TECH_TOKENS` in `scripts/spec-prep-validate.py`; each line of a `tech-tokens.txt`; and each backtick identifier, CamelCase name or capitalized name with a digit that the derived layer uses (context, plan, design, research, data-model, quickstart, tasks, experience and plays files, or frontmatter `layer: derived`). Match whole words, ignoring case.
   Exempt: frontmatter, any section whose heading contains "Prior art", the H1 title's words, the platform and format names in `ALLOW_TOKENS`, and `layer-allow.txt` entries. Keep an explicit user constraint with a justified `layer-allow.txt` entry instead of deleting it: one token per line followed by `# <source and reason>`, for example `postgres  # intent section 3: user mandates the existing cluster`. Both token files sit in the checked directory or its parent; an unjustified entry fails the check.
2. **Authorship and provenance.** Preserve direct user instructions and accepted decisions; distinguish assistant proposals, inherited assumptions and observed results (an uploaded assistant draft does not ratify every line). Authorized reversible preparation continues with explicit provisional defaults. Ask only where a material missing decision blocks its dependent action; never ask the user to reapprove their own instructions or infer authority from silence. Keep full source prompts once under sources/ and map material needs to their destination.
3. **Eval binding.** Every spec clause carries an `EVAL-ID` defined in the external eval store (default `~/.spec-prep/evals/<slug>/evals.md`, `<slug>` being the project directory name; format in `references/templates.md#eval-binding`), outside the build root even without Git. An external directory is not an access-control boundary: held-out evaluation needs an evaluator context whose files and tools the implementing agent cannot reach. Keep public acceptance visible, call tests held-out only when that isolation exists, and disclose isolation not yet established.
4. **Change propagation.** Goal changes begin in intent; behavior corrections belong in spec, architecture corrections in plan, workflow defects in the skill or governance. Reconcile affected contracts, tasks, acceptance, traceability and receipts. Never invent a product requirement to justify a tooling correction.
5. **Continuity.** In standalone and native preparation, append material decisions, outcomes and task-state changes to the ledger and refresh `standing.md` when resumable state changes, so a dormant project resumes without days of archaeology. An input handoff carries no ledger.
6. **Honesty.** `substrate.md` states the real substrate level and the real pre-lock versus live-resolve boundary; the agent drafts it and the human owns the declared level. Record no certainty the project has not earned.

## Confidence Gate

Use `references/intake-checklists.md#confidence-gate` to diagnose completeness; it owns how the advisory score is used and what it can never change.

## Execution Protocol

Create a task list for Phases 0 to 7 when the harness has one, or a visible checklist in chat; tick phases off as they finish and restate the checklist when resuming.

### Phase 0: Operation, mode and setup

Choose the requested operation (Terminology) before authoring anything. **Proportionality:** select process depth by uncertainty, behavioral novelty, consequence, coordination, audit needs and expected lifetime, never by line count, model brand or context-window size; outcome-led delegation to a capable agent is not unreviewed vibe coding. A requested native Spec Kit preparation still completes its agreed stages and gates: proportionality never changes the output mode, waives a gate, or permits stopping halfway or auto-implementing.

Requested filenames do not select standalone mode, and missing tooling does not change the operation: if native execution is unavailable, deliver the complete input handoff, record native preparation as incomplete and name the next preparation step, not a build step.

The input mode (Interactive, Transcript, Fast Track, Existing specs or Recovery) decides which phases run: `references/intake-checklists.md#input-modes`.

Read user preferences and memory for stack, design language, hosting and formatting; they inform context and experience, never intent or spec. Check for an existing spec-prep tree (a supplied pack is existing-specs intake), Spec Kit, OpenSpec or Kiro structures (`references/artifact-contract.md#openspec-kiro-and-other-toolchains`), a constitution (`references/intake-and-speckit.md#constitution-and-task-gates`) and session instruction files.
An input handoff authors the three core documents and governance directly under the declared roots; native preparation uses the installed Spec Kit workflow and paths. Templates are not completed specifications.

### Phase 1: Intake and extraction

*Skip in Existing-specs mode.* Extract problem statements, solutions, personas, success and failure conditions, constraints, scale and quality expectations, implied entities, integrations and workflows. **Tag every extracted signal as intent, spec or implementation**, because the user will have fused them; separation starts here. In Interactive mode, proceed category by category with `references/intake-checklists.md#discovery-questions-interactive-mode`; never ask everything at once.

### Phase 2: Prior art research (mandatory)

*In Existing-specs mode, do not redo a survey the pack already contains; run the prior-art gate, and this phase only when it finds no record.* Follow `references/intake-checklists.md#prior-art-research-checklist` and its minimum searches. **If an existing tool fully solves the problem, stop and surface it.** Record findings in intent section 10 (`references/templates.md#intent-template-intentmd`) and keep a source list for the delivery summary.

### Phase 3: Context derivation (system-owned)

Derive architecture from intent with the derivation inputs in `references/templates.md#context-template-contextmd`, which govern native plan.md as well as standalone context.md. Every decision cites its intent input and memory source. On an empty ledger, follow `references/templates.md#the-empty-ledger-honesty-rule`; never hide the gap. Record user-mandated, provisional, accepted and live-resolved choices distinctly.

### Phase 4: Artifact generation

Use the artifact contract and the installed toolchain's native paths. For Spec Kit, follow `references/intake-and-speckit.md#intake-staging-and-spec-kit-preparation`; never draft a second independent spec tree and duplicate it into Spec Kit. Read the matching reference before each role:

1. Governance (`references/intake-and-speckit.md#constitution-and-task-gates`): retain or create the authoritative constitution through Spec Kit from authorized principles, and wire AGENTS.md to it, the task gates and the reset handoff as that section describes.
2. `intent.md` at `specs/<feature>/intent.md` (`references/templates.md#intent-template-intentmd`): goals, constraints, success/failure conditions, personas, user stories, scope and provenance.
3. Native `spec.md` through the installed template, applying the clause rules of `references/templates.md#spec-template-specmd` (standalone and input-handoff use that template whole). Preserve clause/eval IDs and traces; evaluator-only fixtures stay external, public acceptance stays visible.
4. Native `plan.md` through the installed template, with the derivation inputs of `references/templates.md#context-template-contextmd` (standalone and input-handoff use that template whole). Existing design/context files are sources, never a competing editable plan.
5. Conditional supporting artifacts (research, data-model, contracts, quickstart, requirements-quality checklists) when the domain or installed workflow requires them; supplied material and any data section follow the contract's "Supporting material" rules. For a UI, read `references/templates.md#experience-template-experiencemd` and visually verify any new visual claim.
6. Native `tasks.md`: dependencies, target files, requirement/story IDs, observable acceptance gates and recovery when meaningful; optional plays follow `references/templates.md#plays-playbook-plays`. Tasks stay unchecked until their work supplies evidence. **Producing `tasks.md` ends preparation. It is not permission to implement, in any session, without a new explicit user instruction.**
7. Provenance/traceability: source disposition, the prior-art status line, and story/clause/eval/plan/task mapping, keeping rejected or deferred inputs with reasons.
8. Continuity and substrate: `references/continuity.md#continuity-ledger-and-standing-ledger` and `references/continuity.md#substrate-self-location-substratemd`, or the declared Living Documents integration.
9. Preparation evidence and reset handoff: `preparation.json` with actual gate results and hashes, and `reset-handoff.md` (`references/intake-and-speckit.md#specification-preparation`, step 10). Refresh `workbench.json` to point at existing outputs; it never manufactures artifacts or a pass.

Standalone mode keeps its declared context/ledger/plays conventions; preserve the user's document format and versioning. For a preparation-only request, stop after tasks, analyze and checks: no implement command, agent launch, queued build or implementation hook (`references/intake-and-speckit.md#stop-gate`). Carry that boundary into AGENTS.md, reset-handoff.md and the receipt; a later explicit implementation request is separate authority.

### Phase 5: Refinement and depth verification

Run the refinement passes, semantic preservation review and cross-validation in `references/validation-and-refinement.md#refinement-passes` on every run, and for an existing package update also `references/validation-and-refinement.md#refining-an-existing-specification-package`. A validation-only request reports findings without authorizing rewrites.

**Optional Jev review:** `references/validation-and-refinement.md#optional-jev-semantic-review`, when requested or when a bounded semantic check adds value; it owns the availability, fallback and no-spend policy.

### Phase 6: Validation and delivery

Run the nine validation checks (separation, eval binding, testability, identity, drift, continuity, honesty, authorship, prior art) as "How to run the gates" describes and record each verdict; `references/validation-and-refinement.md#the-nine-validation-checks` owns each pass/fail criterion. Supporting material missing from the source-disposition map is a drift failure, never a reason to delete it.

**Adjudicate divergences; do not just report them.** Preserve the first blind pass, then record for each divergence whether it stands, falls or needs a user decision, with the reason, and record what stopped each pass where `references/validation-and-refinement.md#refinement-passes` puts refinement findings.

Deliver the tree (zipped if the user wants a package) and a summary: confidence score and sub-threshold dimensions, declared substrate level, key derived decisions, remaining `[NEEDS CLARIFICATION]` markers, prior-art findings with sources, refinement and depth results, validation output, each core input or native artifact path, and the operation actually completed.
Required preparation gates must pass before claiming native preparation; evidence meanings follow `references/validation-and-refinement.md#evidence-and-source-preservation`. State the handoff path and its read order (Phase 7).

### Phase 7: Reset handoff and optional initiation

Deliver the verified preparation receipt and reset handoff. Specification preparation ends here unless the user requested implementation; never infer implementation authority from "create tasks", "stage" or "prepare".

**The reboot rule.** Preparation and implementation are separate authorities in separate sessions. The authoring session NEVER implements, even when the user says "then build it" in the same breath: finish preparation, write the reset handoff, and STOP. Implementation begins only in a session with no parent linkage to the authoring session: one the user starts, or an explicitly authorized launcher starts, that does not inherit the authoring session's conversation, context or agent tree (`references/handoff.md#what-counts-as-a-fresh-session` lists what counts and what does not).
On hosts with terminal launch, that machinery runs only on explicit launch authority: a named project plus a direct "launch/spawn/start it now" instruction, which a combined "prepare then implement" request supplies only AFTER preparation is finished, committed and gate-verified; otherwise produce the pasteable resume prompt (handoff contents, next task) and stop.
A spawned task or subagent of the authoring session is NOT a fresh session. "Implement via new session", "activate after restart" or "I will restart" name the user-launched path. The constitution binds at session start and a continuing session cannot re-bind it; only the session boundary fixes that, so this rule is load-bearing.

**Authoring-session freeze.** Once preparation is committed, write no implementation code, mark no task complete and write no `fresh-session-ack.md` in this session; only a session with no parent linkage can author those, and anything else is VOID audit evidence. A system todo or resume reminder is not user authority: on a user STOP, halt immediately and resume only on their explicit resume.

**Fresh-session read order.** A fresh session reads AGENTS.md, the constitution and reset-handoff.md first; then any existing standing and ledger, with the receipt and hash checks; then intent, spec, plan and tasks for its task. AGENTS.md and the handoff carry this order, and the preparation-only boundary survives the reset.

When project initiation is expressly authorized, follow `references/handoff.md#fresh-session-initiation`. The reset handoff carries the working directory, the constitution's exact location, the consumed handoff, the next task and the acknowledgement shape the new session must produce. A tab appearing is not build completion. Never modify terminal configuration, routing or credentials as part of launch.

## Resource files

| File | Read when |
|------|-----------|
| `references/artifact-contract.md` | Outputs, supporting material, delivery.json, workbench, repository, other toolchains |
| `references/intake-and-speckit.md` | Intake, native preparation, constitution, stop gate |
| `references/intake-checklists.md` | Phase 0 input modes, Phases 1 and 2, the prior-art gate |
| `references/templates.md` | Phases 2 to 4: intent, spec, context, experience, plays |
| `references/continuity.md` | Ledger, standing, substrate; Living Documents when it applies |
| `references/validation-and-refinement.md` | Phases 5 and 6, evidence meanings, optional Jev |
| `references/handoff.md` | Phase 7: what counts as a fresh session; initiation when expressly authorized |
| `references/workbench.schema.json` | Writing or checking workbench.json |
| `scripts/spec-prep-validate.py`, `scripts/spec-prep-delivery.py` | Running the gates |
