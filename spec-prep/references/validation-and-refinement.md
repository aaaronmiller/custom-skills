---
title: Validation and refinement
tags: [spec-prep]
---

# Validation and refinement

## Contents

- [Evidence and source preservation](#evidence-and-source-preservation)
- [Refinement passes](#refinement-passes)
- [The nine validation checks](#the-nine-validation-checks)
- [Refining an existing specification package](#refining-an-existing-specification-package)
- [Optional Jev semantic review](#optional-jev-semantic-review)

## Evidence and source preservation

Read when reviewing sources, interpreting validation or writing a receipt. Artifact roles and operations belong to references/artifact-contract.md#canonical-artifact-contract; the preparation procedure belongs to references/intake-and-speckit.md#intake-staging-and-spec-kit-preparation. This reference owns evidence meanings, not a second workflow.

Keep source instructions, accepted decisions, assistant proposals, defaults and measured facts distinct. Preserve exact supplied prompts/attachments once with source IDs and locators. Map material needs to owning requirements/design/intent sections and record preserved, changed with reason, deferred, rejected or unavailable. A mixed draft does not ratify every proposal. Existing explicit user authority persists; silence creates none.

Artifact existence, mechanical consistency, semantic preservation/feasibility and runtime validation are separate claims. Hashes identify bytes. ID checks establish references. Counts can flag a possible omission, not prove that the same needs survived. Public acceptance remains readable by implementers. Keep required EVAL bindings and external definition conventions; do not waive a required evaluator profile to obtain a pass; isolation is governed by SKILL.md rule 3. Test definitions, independent execution and product results have separate evidence.

Record each required gate's status (passed, failed, incomplete or not_run), input identities, actual command or named agent workflow, observation time, evidence path and material limitation. Agent workflows are instructions the agent executes; a fake shell transcript is never required. An equivalent semantic review must document the same rubric/findings/resolutions and its actual reviewer. ID counting is not analyze; self-review is not independent review.

Native preparation is complete only when constitution, prerequisites, semantic analysis, source preservation/traceability and applicable document/delivery checks pass. Product tests, target-device benchmarks and isolated evaluator execution remain tasks at their appropriate implementation stage. Do not require future runtime measurements merely to prepare documents; do not hide a known feasibility contradiction by declaring all hardware evidence future work. Missing required evaluation definitions remain an incomplete preparation check, not fabricated fixtures.

Correct the owning layer and affected dependents, then hash the final artifacts. Refresh standing for material resumable changes. Do not rehash stale contracts merely to make a receipt pass. Preserve existing instructions and govern actual task gates with the project constitution. Reset recovery and preparation-only stopping are part of delivery, not implementation authority.

Use one concise source map and one preparation receipt, linking necessary evidence instead of copying it into many reports. An incomplete lifecycle honestly describes unfinished work; it does not satisfy a requested native-preparation deliverable. Complete independent work and name the next unfinished preparation operation.

## Refinement passes

SKILL.md Phase 5 runs these on every preparation, not only on package updates.

**Passes.** Run at least three passes, each with a different lens so each finds different problems; use the deliberative-refinement skill when available.

- Adversarial edge cases: what breaks with real users, real devices and real data. Classify each finding by its owning layer; repair the affected artifact and its dependents without inventing product scope.
- Traceability and consistency: every story maps to clauses, every clause to context, every context decision to intent; no contradictions between artifacts; mockup and experience tokens match.
- Current practice: how agents actually build now (verification loops, worktree isolation, instruction files, CI gates) and what the platform offers that the draft ignores.

Each pass records its findings, its changes and what stopped it, and bumps the version of every artifact it changed. In standalone and native preparation these are `refinement` entries in the ledger, which is the refinement log; do not write a separate one. An input handoff carries no ledger: record the same entries in intent.md's source-disposition section, or in a linked appendix under `appendices/` that the source-disposition map declares. This paragraph is the one rule for where refinement findings go.

**Semantic preservation.** Maintain one material source-disposition map: preserved, changed with reason, deferred, rejected or unavailable, with destination and provenance. Preserve design-section coverage and all material constraints. Added unrelated requirements cannot compensate for missing intent, and shorter line counts alone do not prove loss. Inspect task inputs, affected paths, dependencies, observable acceptance and recovery. Do not pad clauses or tasks to meet a count or word floor. Missing material obligations must be resolved or explicitly left incomplete.

**Cross-validation.** Every clause traces to intent; every context and experience decision traces to a clause or constraint; every play reads its variables from intent or context rather than hard-coding them.

## The nine validation checks

This table owns each check's pass/fail criterion. `scripts/spec-prep-validate.py` implements all nine and reports each as `passed`, `failed` or `not_run`; `tests/test_validate.py` holds a constructed fixture that makes each one fail. Where the host cannot run code, apply the "By hand" column in order and record every verdict, marking the pass hand-executed. These checks are mechanical: they establish the lexical and structural conditions they inspect, and semantic review stays a separate obligation under the evidence rules above. For Existing-specs intake, `--audit` runs separation, testability and identity on the supplied documents first.

| Check | Fails when | By hand |
|---|---|---|
| separation | A technology token (SKILL.md rule 1) appears in intent.md or the specification outside the exempt parts, or a `layer-allow.txt` entry has no justification | Build the token list from rule 1; search intent and spec for each token as a whole word, ignoring case; every hit not covered by an exemption or a justified allow entry fails |
| eval-binding | A clause has no EVAL-ID (an inline `[EVAL-...]` tag, or a traceability.md row naming the clause and an EVAL-ID); the eval store is missing or sits inside the build root (`--build-root`, else the buildRoot of the delivery.json workstream containing the artifact directory, else the Git top level, else the nearest Spec Kit project; an `inputs/` directory's parent at minimum); or a cited EVAL-ID has no definition in the store (format in `references/templates.md#eval-binding`) | Find each clause's EVAL-ID; open the store, confirm its path is outside the build root, and confirm each cited ID starts a definition line that states what it asserts |
| testability | A clause contains a non-evaluable phrase from the `NON_EVALUABLE` list in the validator (for example user-friendly, intuitive, seamless, robust, scalable, as needed, where possible, etc.) | Read each clause; such a phrase, or a clause you cannot turn into a pass/fail evaluation, fails |
| identity | The specification declares no clause at a line start, or declares one ID twice. Accepted clause prefixes: `SPEC-`, `REQ-`, `FR-`, `NFR-`, each followed by digits (drift and traceability read the same prefixes) | List the clause IDs; an empty list or a repeat fails |
| drift | A declared clause is cited by no derived document (context.md, plan.md or design.md, plus tasks.md and traceability.md); a derived document cites an undeclared clause; or a file under `data/`, `references/`, `sources/`, `fixtures/` or `appendices/` (in the artifact directory or build root) is not declared in the source-disposition map | Compare the declared and cited ID sets in both directions; list the supporting files and confirm each path, or a parent directory written with a trailing `/`, appears in the map |
| continuity | Standalone or native preparation only: the ledger or standing file is missing, holds under 40 characters of content, or flat and nested copies differ. Records `not_run` for an input handoff, or with `--continuity external` when Living Documents owns continuity | Open `ledger/ledger.md` and `ledger/standing.md`; each must record real decisions or resumable state |
| honesty | Standalone or native preparation only: substrate.md is missing, or no line under `## Declared level` starts with a level S0-S5. Records `not_run` for an input handoff | Open that section; a line must begin with S0, S1, S2, S3, S4 or S5 |
| authorship | No derived document (context.md, plan.md or design.md) exists, or no source-disposition map exists (the intent.md section whose heading contains "Source disposition", else traceability.md, else source-disposition.md), or the map records no disposition | Confirm both exist and that the map marks each source preserved, incorporated, changed, deferred, rejected, unavailable, superseded, duplicate or unresolved |
| prior-art | No done, directed or waived record exists; waived has no reason; directed while plan.md or tasks.md already exists; or done with an empty "Prior art" section and no existing record file | Apply the prior-art gate in SKILL.md to intent section 10 and any `prior-art:` status line |

## Refining an existing specification package

Read when updating a prior spec-prep run, incorporating steering into a prepared package, or validating whether its inputs and outputs still agree. It specializes the existing change-propagation rule; artifact roles remain defined in `references/artifact-contract.md#canonical-artifact-contract` and evidence meanings in `#evidence-and-source-preservation`.

### Resolve authority before changing documents

Inspect the requested package, scoped instructions, workbench, preparation receipt and current continuity. Distinguish:

- Preserved evidence: original prompts, attachments, earlier drafts and immutable input snapshots. Keep original bytes and provenance. Record later steering as a new source or amendment rather than rewriting history.
- Maintained inputs: the requirements/design/intent documents the project explicitly uses to generate or revise native outputs. Keep these current when the authorized delta affects them, so a later preparation run preserves the change.
- Operational outputs: the project's native specification, plan, tasks, contracts and supporting artifacts. These govern implementation within the recorded authorization.

Map the actual paths and their dependencies. A package need not contain a separate input trio; do not create duplicate requirements/spec or design/plan authorities just to satisfy this procedure. Where both exist, record how maintained inputs feed outputs and which document owns each decision. Preserve IDs and naming conventions. Historical drafts are evidence, not regeneration sources that can override newer accepted decisions.

When resuming an existing prepared project, follow the read order in SKILL.md Phase 7, verify the consumed artifact hashes and named gates, then inspect the actual spec, plan, tasks and constitution. Do not regenerate an intact constitution or rerun setup-plan over an existing plan just to prove readiness. A bounded artifact correction invalidates the affected evidence; recheck downstream semantic support before refreshing the receipt.

A validation-only request produces findings and evidence. A refinement request authorizes the relevant document changes within its scope. Neither grants implementation, publication or launch authority.

### Resolve the delta at its owning layer

Use direct user instructions, accepted decisions and inspected project evidence before asking for information. A project-specific license, storage choice or runtime preference is not a default for unrelated projects. Distinguish explicit choices from the agent's derived decisions; an instruction to exercise judgment authorizes that judgment without converting every resulting assumption into an explicit user statement.

Resolve routine choices using the project's goals and constraints. State material provisional assumptions and keep them revisable. When required information is unavailable or ambiguity changes the objective or target, pause only the dependent action and complete independent work. Reversibility alone does not establish correctness. Follow current user authority and the host's action-risk rules.

Classify the change before editing:

| Change | Owning artifact | Propagation |
|---|---|---|
| Goal, scope or user constraint | Maintained intent | Affected requirements, design and native outputs |
| Observable behavior or acceptance | Maintained requirements or native spec, according to the declared mapping | Corresponding input/output representation, plan, tasks, acceptance and traceability |
| Mechanism, data representation or architecture | Maintained design or native plan | Affected input/output representation, contracts, schemas, task dependencies and recovery |
| Governance or workflow defect | Constitution, instructions or skill | Only the affected project artifacts and gates; no invented product requirement |

Technical rationale stays in design/plan. Preserve explicit user technology constraints with justified layer exemptions where required; do not add exemptions solely to silence a real leak. Use the actual section headings rather than hard-coded section numbers.

### Apply and review the affected region

Checkpoint relevant files before broad or architectural edits and retain unrelated working changes. Preserve newly supplied briefs with provenance. For private local reference material, retain only the authorized relevant content or a sufficient locator and fingerprint; do not indiscriminately copy a vault or credentials into a distributable package.

Update maintained inputs and their corresponding native outputs together where both exist. Re-derive a changed dependency region as a unit when tasks are added, combined or reordered. Check downstream consumers: contracts and schemas, public acceptance, task gates, recovery, source dispositions, instruction adapters and reset handoff. Amend the constitution only for an actual governance change.

Keep existing clause, task and evaluation identifiers stable. Bind every required functional and quality clause according to the project's evaluation convention. Distinguish public acceptance from evaluator-only definitions: an implementing agent must not open or rewrite protected evaluations. Arrange evaluator-owned updates when required, or mark that dependent gate incomplete.

Review source preservation, cross-document consistency and feasibility, not merely identifier counts. A clean hash cannot establish that conflicting contracts are coherent. Record material decisions and outcomes in the existing ledger and refresh standing; do not mark unexecuted implementation tasks complete.

### Validate and refresh the receipt

Resolve the skill root, intake root, build root, feature root and external evaluation location separately. Run the scripts from the loaded skill's own `scripts/` directory, never from an assumed scripts directory in the product, using the commands in SKILL.md "How to run the gates": the nine validation checks on each affected artifact directory, and the delivery checker where a delivery manifest applies. Select the checks that apply to the existing layout; do not fabricate an intake manifest for a package that lacks one. Evaluation binding checks must respect evaluator access restrictions.

For native preparation, also rerun affected constitution checks, the installed Spec Kit prerequisite checker and semantic analyze using the installed integration or an explicitly equivalent review with named rubric, findings, resolutions and reviewer. Inspect task dependencies and clause coverage. Record each required gate's real command or workflow, input identity, observation time, evidence and limitation. Retained evidence is valid only when its input scope remains unchanged; otherwise mark it stale until rerun.

After final content and continuity updates, hash the final consumed artifacts and update the existing receipt in its supported format. Preserve legacy receipt identity rather than claiming a new native run. Link fresh evidence; do not relabel old review output with a current observation time. Reread the receipt and verify every hash, path, gate status and implementation boundary. Where `delivery.json` exists or the operation requires a new delivery, check its package root with `scripts/spec-prep-delivery.py`; the skill directory itself is not a product delivery package.

If an archive is part of the requested delivery, create a new versioned bundle without overwriting an uninspected prior artifact. Exclude caches and accidental nested archives; preserve required source assets. Validate a safely extracted copy at a different path, including pointers, applicable gates and receipt hashes. Keep evaluator material out of implementer deliveries. A release or push requires its own actual authority.

Complete the requested operation only when maintained inputs, affected outputs and evidence agree. Otherwise record the exact unfinished gate and next preparation action while preserving independent completed work. Refer to the existing handoff rather than adding a second workflow authority.

## Optional Jev semantic review

Read when Jev review is requested or a bounded semantic check could improve preparation. Jev is a typed semantic-judgment service (TypeSafe System One, https://docs.typesafe.ai/api/system-one) that answers atomic questions about supplied excerpts with `supported`, `needs_review` or `abstain`. This section owns the Jev policy. Jev is never a prerequisite, a required gate or authoring authority, and it affects no mandatory check.

### Availability and fallback

Use Jev only when the user has not disabled it and an eligible tool or adapter, network access, credentials and authority to send the selected excerpts already exist. Inspect available capabilities without assuming access or inspecting secret values. Do not install tools, request credentials, change providers, spend money or block preparation so an optional step can run. Configuring Jev is its own scoped task, only when the user asks for it.

When Jev is disabled, unavailable or unsuccessful, record its review as `not_run` with a short reason. `not_run` means no usable verdict was obtained, not that no attempt occurred, so preserve an attempted call's actual failure. Continue the deterministic checks and the required agent-mediated semantic review against the same sources and rubric. Attribute the review to its actual reviewer and label self-review as self-review; a separately required independent review is not satisfied by self-review, and a required gate never becomes optional because Jev is absent. Do not retry unavailable access repeatedly.

### How to use it

Jev evaluates supplied state with typed questions; it does not write specifications or replacement prose. Use named source excerpts and an explicit target (the folder containing SKILL.md for a skill change, the actual build root for project preparation) at intake, output, task-generation or governance review; during an already authorized implementation, review evidence only within existing authority. A recommendation never edits either target. Keep hashes, arithmetic, dates, ID and path checks and constitution heading comparisons deterministic; the vendor documents weaknesses with numeric precision, dates, indirection and irrelevant context. Ask one atomic evidence question with an explicit abstention option, then review the cited excerpt yourself. Confidence is a routing signal, not proof: low confidence, abstention, a stale source or a malformed response never becomes a pass. A more capable reviewer or the human resolves a substantive ambiguity without inventing product scope. Never send secrets, private URLs, evaluator-only fixtures or unnecessary project data, and preview the exact request before any approved external send.

### Where it helps

| Stage | Useful semantic question, with a named excerpt | Deterministic work stays outside Jev |
|---|---|---|
| Intake, before specify/plan | Does this acceptance condition express an observable outcome? Does this design excerpt support this stated constraint? | Intake hashes, files, JSON/schema, read order |
| Generated output | Does this one requirement preserve this source obligation? Is a documented constraint contradicted by this decision? | ID existence, source hashes, clause/eval tags, artifact paths |
| Task generation | Does this task's proposed acceptance exercise the linked requirement? Is a recovery procedure adequate for this named failure? | Task format, dependency cycles, missing paths/gates |
| Governance | Does this plan decision conflict with this quoted principle? | Exact constitution heading set, instruction-file references, receipt checks |
| Implementation, when already authorized | Does this captured acceptance evidence support this one claim? | Actual tests, checksums, numerical boundaries, authorization, checked task state |

Avoid a full-document "approve everything" question, repeated calls on every edit, or use as a constitution or permission oracle. Use the smallest excerpt that can decide each question. Jev checks within one request are independent; a question cannot rely on another answer. Record actual Jev results separately from the semantic review, and keep the original blind response before giving additional context. Never label another model's reasoning a Jev verdict. Jev changes no launch authority, task checkbox or required deterministic gate.
