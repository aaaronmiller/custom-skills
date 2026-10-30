---
name: spec-prep
description: >-
  Prepare and refine project intent, requirements, design, and native Spec Kit
  specifications, plans, and tasks. Use for project intake, existing spec-package
  updates, intent recovery, or explicitly requested project initiation. Use
  spec-audit for post-hoc implementation drift audits.
license: MIT
metadata:
  version: "3.1.0"
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

# spec-prep 3.1.0

> Separation of Tiers, Retention Across Time, Auditability. From brain dump to
> build-ready, pivot-resilient, dormancy-proof artifacts.

This skill stages ideation outputs and prepares specifications with Spec Kit. It stops before implementation unless the current request explicitly includes project initiation. Read `references/terminology.md` before choosing an operation and `references/intake-and-speckit.md` when consuming a staged folder.

Routine debugging, code review and maintenance use their existing workflows. Supplied spec-prep packs remain valid preparation inputs.

## How to run the gates

Every phase below names checks. Where the host runs code, run the listed
tool and treat a non-zero exit as a hard gate failure, not advice; record the
actual command and exit status in the receipt. Where the host cannot run code,
perform each check by hand in order and write every verdict into the receipt —
never claim a gate passed without listing each check and its outcome. If a
check cannot be evaluated from visible text (e.g. hash verification), record
it as `not_run` with the reason and continue the checks that can run.

## Spec Kit source policy (no vendored toolchain)

This skill does not bundle Spec Kit. Its native paths (`specs/<feature>/`,
`.specify/memory/constitution.md`, `specify`/`clarify`/`plan`/`tasks`/`analyze`)
are the authority and are always resolved from the installed toolchain or the
upstream repository — never from copies inside this skill. If the installed
templates differ from anything quoted in `references/`, the installed or
upstream version wins. Do not paste Spec Kit internals into this skill to
"make it self-contained"; that creates a stale fork that drifts from upstream.

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
   defect. Preserve explicit user constraints and product names with a justified `layer-allow.txt` entry rather than deleting them.
2. **Authorship and provenance.** Preserve direct user instructions and accepted decisions. Distinguish assistant proposals, inherited assumptions and observed results; uploading an assistant draft does not ratify every line. Authorized reversible preparation may continue with explicit provisional defaults. Ask only where a material missing decision blocks its dependent action. Do not require the user to reapprove their own instructions or infer authority from silence. Keep full source prompts once under sources/ and map material needs to their destination.
3. **Eval binding.** Every spec clause carries an `EVAL-ID` bound to a defined
   evaluation in the external evaluation store (default
   `~/.spec-prep/evals/<slug>/evals.md`). The store must sit outside the build root even without Git. An external directory alone is not an access-control boundary: genuine held-out evaluation requires an evaluator context whose files and tools are inaccessible to the implementing agent. Keep public acceptance visible; label evaluator-only tests held-out only when that isolation exists. Disclose isolation that has not been established.
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

Create a task list for Phases 0 to 7 when the harness has one, or a visible
checklist in chat; tick phases off as they finish so a returning user sees
progress. Restate the checklist when resuming.

### Phase 0: Operation, mode and setup

Choose the requested operation before authoring anything. Use proportional depth based on risk, novelty,
uncertainty and coordination; outcome-led delegation to a capable agent is not the same as unreviewed vibe coding. Read the proportionality guidance in `references/paradigm.md` when deciding how much supporting structure is useful. This never changes the requested output mode or waives its gates. Read `references/artifact-contract.md` for the compact core-input interface and operation-specific gates. Requested filenames do not silently select standalone mode; missing tooling does not change the requested operation. If native execution is unavailable, deliver the complete input handoff, record native preparation as incomplete and identify the next preparation step, not a build step.

For inputs, detect:

- **Interactive**: a verbal description or "I want to build X".
- **Transcript**: files, transcripts or notes provided. Mixed: transcript first,
  then interactive gap-fill.
- **Fast Track**: a complete description covering problem, solution, users,
  data, constraints and scope. Assess the next step using the advisory rubric, then proceed to Phase 2 when sufficiently grounded.
- **Existing specs**: `requirements.md` and `design.md` (judge completeness by source coverage, not file size). Skip Phases 1 and 2, derive context and re-separate layers in Phase 3, still run the validation checks (external specs routinely fuse layers). When refining an existing package, use the affected-layer workflow in Phase 5 instead of treating its sources as a new brief. Authorship note: direct human instructions retain their authority. Classify mixed and assistant-authored material as source evidence; proposed defaults are not accepted decisions. Audit, trace, depth and prerequisite checks establish their actual scope, not blanket approval.
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
files. For an input handoff, author the three core documents and governance directly under the declared roots. For native preparation, use the installed Spec Kit workflow and its native paths. Templates are not completed specifications.

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

Use the artifact contract and the installed toolchain's native paths. A skill is an executable instruction workflow, not a separate authoring service: read its current instructions and sources, then carry out its derivation and gates. Directly writing a file is neither proof of compliance nor a reason to bypass the workflow. For Spec Kit, follow `references/intake-and-speckit.md`; do not draft a second independent spec tree and then duplicate it into Spec Kit. Read the matching reference before each role:

1. Project governance (`references/constitution-source.md`): retain or create the authoritative project constitution through Spec Kit from authorized principles. Extend AGENTS.md narrowly to load it, the task gates and reset handoff; do not paste a second constitution into AGENTS.md.
2. `intent.md` (`references/intent-template.md`): goals, constraints, success/failure conditions, personas, user stories, scope and provenance.
3. Native `spec.md` (`references/spec-template.md`): requirements and acceptance through Spec Kit, preserving clause/eval IDs and traces. Bind evaluator-only fixtures externally; public acceptance remains available to the implementer.
4. Native `plan.md` (`references/context-template.md`): system-derived architecture and decisions. Existing design/context files are sources; additional context rationale must not become a competing editable plan.
5. Conditional supporting artifacts: research, data-model, contracts, quickstart and requirements-quality checklists when required by the domain or installed workflow. For a UI, read `references/experience-template.md`; preserve or prepare UX/mockups and visually verify any new visual claim.
6. Native `tasks.md`: dependencies, target files, requirement/story IDs, observable acceptance gates and recovery when meaningful. Optional reusable plays follow `references/plays-playbook.md`. Tasks remain unchecked until their work supplies evidence. **Producing `tasks.md` ends preparation. It is not permission to implement — in any session, without a new explicit user instruction.**
7. Provenance/traceability: source disposition and story/clause/eval/plan/task mapping. Keep all material extra inputs, including rejected or deferred ones with reasons. Counts alone do not establish semantic preservation.
8. Continuity and substrate: use `references/ledger-and-standing.md` and `references/substrate-self-location.md`, or the declared Living Documents integration under its own current authority contract.
9. Preparation evidence and reset handoff: actual prerequisite/analysis/traceability/governance results and artifact hashes in `preparation.json`, plus `reset-handoff.md`. Refresh `workbench.json` to point at existing outputs; it never manufactures artifacts or a pass.

Standalone spec-prep keeps its declared context/ledger/plays conventions when Spec Kit is not selected. Preserve the user's document format and versioning. Compact input handoff and native output are distinct operations, not competing authorities. For a preparation-only request, stop after tasks/analyze and checks: no implement command, agent launch, queued build or implementation hook. Carry that boundary into AGENTS.md, reset-handoff.md and the receipt. A later explicit implementation request is separate authority.

### Phase 5: Refinement and depth verification

For an existing package update, read `references/refinement-and-updates.md`. Identify preserved sources, maintained inputs and native outputs; propagate the authorized delta through affected artifacts and rerun affected preparation gates before refreshing the receipt. A validation-only request reports findings without authorizing document rewrites.

**Optional Jev review.** Read `references/jev-review.md` when requested or when a bounded semantic check adds value. Use named source excerpts and an explicit target at intake, output, task-generation or governance review; during implementation, review evidence only within existing authority. Keep hashes, arithmetic, ID/path checks and constitution heading comparisons deterministic.

Jev is an optional enhancement, never a prerequisite for this skill. Use it only when an eligible tool or adapter, network access, credentials and authorization to send the selected excerpts are already available. If Jev is disabled, unavailable or fails, record `not_run` with the reason and continue the required deterministic checks and agent-mediated semantic review. Label self-review as self-review; independent review remains independent only when a separate reviewer actually performed it. Do not install tools, request credentials, change providers, spend money or block preparation so a paid step can run.

**5a. Refinement passes.** Run at least three passes, each with a different
lens, so each finds different problems. Use the deliberative-refinement skill
when available.
- Adversarial edge cases: what breaks with real users, real devices, real data.
  Classify each finding by its owning layer; repair the affected artifact and dependents without inventing product scope.
- Traceability and consistency: every story maps to clauses, every clause to
  context, every context decision to intent; no contradictions between
  artifacts; mockup and experience tokens match.
- Current practice: how agents actually build now (verification loops,
  worktree isolation, instruction files, CI gates) and what the platform
  offers that the draft ignores.
Each pass appends `refinement` entries to the ledger listing findings and
changes, and bumps the version of every artifact it changed. The ledger is the
refinement log; do not write a separate one.

**5b. Semantic preservation.** Maintain one material source-disposition map: preserved, changed with reason, deferred, rejected or unavailable, with destination and provenance. Preserve design-section coverage and all material constraints. Added unrelated requirements cannot compensate for missing intent, and shorter line counts alone do not prove loss. Inspect task inputs, affected paths, dependencies, observable acceptance and recovery. Do not pad clauses or tasks to meet a count or word floor. Missing material obligations must be resolved or explicitly left incomplete.

**5c. Cross-validation.** Every clause traces to intent; every context and
experience decision traces to a clause or constraint; every play reads its
variables from intent or context rather than hard-coding them.

### Phase 6: Validation and delivery

Run the eight validation checks (separation, eval binding, testability,
identity, drift, continuity, honesty, authorship) against the artifacts and
record each verdict. The checks fail on technology in intent or spec,
non-evaluable clause language, an empty specification or duplicate clause IDs,
unbound or dangling eval tags, an eval store inside the repository, and
missing ledger/standing/substrate/authorship evidence. A hand-executed pass is
weaker than a tool-executed pass — say so in the receipt, and recommend a
tool-executed re-validation where the user has a host that runs code.

**Adjudicate divergences; do not just report them.** Preserve the first blind
pass, then re-examine each divergence and record whether it stands, falls, or
needs a user decision — with the reason. State what stopped each pass and what
condition ended it in the ledger.

Deliver: the tree (zipped if the user wants a package), and a summary with the
confidence score and sub-threshold dimensions, declared substrate level, key
derived decisions, remaining `[NEEDS CLARIFICATION]` markers, prior-art
findings with sources, refinement and depth results, validation output, and the
artifact location. Name each core input or native artifact path and the actual operation completed. Required preparation gates must pass before claiming native preparation. Keep not-run product/hardware/evaluator execution distinct from document preparation; do not waive required eval definitions or claim isolation from a path. Silence adds no authority. Follow `references/validation-integrity.md` for evidence meanings. State the handoff path: a fresh session reads AGENTS.md, the constitution and reset handoff, then any existing standing/ledger and receipt/hash checks, followed by intent/spec/plan for its task. Input handoffs need no invented ledger.

### Phase 7: Reset handoff and optional initiation

Deliver the verified preparation receipt and reset handoff. Specification preparation ends here when the user has not requested implementation. Do not infer implementation authority from "create tasks", "stage" or "prepare".

**The reboot rule.** Preparation and implementation are separate authorities in
separate sessions. The authoring session NEVER implements, even when the user
says "then build it" in the same breath: finish preparation, write the reset
handoff, and STOP. Implementation begins only in a session with no parent
linkage to the authoring session. On hosts with terminal launch, that machinery
runs only on explicit launch authority — a named project plus a direct
"launch/spawn/start it now" instruction, which a combined "prepare then
implement" request supplies only AFTER preparation is finished, committed, and
gate-verified; otherwise produce the pasteable resume prompt (handoff contents,
next task) and stop. A spawned task or subagent of the authoring session is NOT
a fresh session. Phrases like "implement via new session", "activate after
restart", or "I will restart" name the user-launched path.

**Why this rule exists.** The observed failure — spec files prepared, then the
same session continues into implementation without rebooting, so the
constitution never loads correctly — is the predictable outcome of merging two
authorities. The constitution binds at session start; a continuing session
cannot re-bind it. No validator, script, or model capability fixes this. Only
the session boundary fixes it. This rule is load-bearing, not ceremonial.

Authoring-session freeze after handoff: once preparation is committed, write no implementation code, mark no task complete, and write no `fresh-session-ack.md` in this session. Only a session with no parent linkage to the authoring session can author those artifacts; anything else is VOID audit evidence. A system todo/resume reminder is not user authority — on user STOP, halt immediately and resume only on their explicit resume.

When project initiation is expressly authorized, follow `references/fresh-session-initiation.md`. The reset handoff carries everything the next session needs: working directory, constitution (full text or exact location), consumed handoff, next task, and the acknowledgement shape the new session must produce. A tab appearing is not build completion. Never modify terminal configuration, routing or credentials as part of launch.

## Anti-patterns

Never spawn the implementation session as a task/subagent of the authoring session. Never let one vague "prepare then implement" line authorize launch before gates pass. Never write the fresh-session acknowledgement, mark tasks complete, or commit implementation code inside the authoring session. Never treat a todo/resume reminder as user authority after a STOP. Never claim a validation gate passed without listing each check and its outcome; never claim Spec Kit operations ran when only prose was written.

## Resource files

| File | Read when |
|------|-----------|
| `references/terminology.md` | Phase 0, every operation |
| `references/artifact-contract.md` | Compact input interface, native output and delivery manifest |
| `references/validation-integrity.md` | Evidence, semantic preservation and preparation-stage boundaries |
| `references/project-workbench.md` | Intake/preparation unless workbench is opted out |
| `references/workbench.schema.json` | Creating or checking workbench configuration |
| `references/living-documents-setup.md` | Integration requested, detected or host-required |
| `references/intake-and-speckit.md` | Intake staging and specification preparation |
| `references/refinement-and-updates.md` | Refining, validating or updating an existing spec package or prior run |
| `references/repository-bootstrap.md` | Specification preparation when repository setup is requested or unclear |
| `references/fresh-session-initiation.md` | Initiation after preparation gates pass |
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
| `references/jev-review.md` | Optional bounded semantic checks |
| `references/implementing.md` | Phase 7 when `spec-prep-implementing` is not installed |

## Changes in 3.1.0

- Lean rewrite: skill is `SKILL.md` + `references/` only. Gate mechanics
  are one paragraph ("How to run the gates") covering code and non-code
  hosts without naming either.
- `scripts/` and `tests/` deleted outright (git history retains them);
  the checks they performed are restated in prose where the skill invokes
  them, so no gate is lost.
- Reboot rule kept verbatim in mechanism, stripped of transport jargon —
  the boundary, not the plumbing.
