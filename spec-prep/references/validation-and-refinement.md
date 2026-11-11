---
title: Validation and refinement
version: "4.0.0"
tags: [spec-prep]
---

# Validation and refinement

## Contents

- [Evidence and source preservation](#evidence-and-source-preservation)
- [Refining an existing specification package](#refining-an-existing-specification-package)
- [Optional Jev semantic review](#optional-jev-semantic-review)

## Evidence and source preservation

*Formerly `#evidence-and-source-preservation`, version 2.5.1.*

Read when reviewing sources, interpreting validation or writing a receipt. Artifact roles and operations belong to references/artifact-contract.md#canonical-artifact-contract; the preparation procedure belongs to references/intake-and-speckit.md#intake-staging-and-spec-kit-preparation. This reference owns evidence meanings, not a second workflow.

Keep source instructions, accepted decisions, assistant proposals, defaults and measured facts distinct. Preserve exact supplied prompts/attachments once with source IDs and locators. Map material needs to owning requirements/design/intent sections and record preserved, changed with reason, deferred, rejected or unavailable. A mixed draft does not ratify every proposal. Existing explicit user authority persists; silence creates none.

Artifact existence, mechanical consistency, semantic preservation/feasibility and runtime validation are separate claims. Hashes identify bytes. ID checks establish references. Counts can flag a possible omission, not prove that the same needs survived. Public acceptance remains readable by implementers. Keep required EVAL bindings and external definition conventions; do not waive a required evaluator profile to obtain a pass. A path outside the build tree does not prove access isolation. Test definitions, independent execution and product results have separate evidence.

Record each required gate's status (passed, failed, incomplete or not_run), input identities, actual command or named agent workflow, observation time, evidence path and material limitation. Agent workflows are instructions the agent executes; a fake shell transcript is never required. An equivalent semantic review must document the same rubric/findings/resolutions and its actual reviewer. ID counting is not analyze; self-review is not independent review. Optional Jev advice is never a required gate or authoring authority.

Native preparation is complete only when constitution, prerequisites, semantic analysis, source preservation/traceability and applicable document/delivery checks pass. Product tests, target-device benchmarks and isolated evaluator execution remain tasks at their appropriate implementation stage. Do not require future runtime measurements merely to prepare documents; do not hide a known feasibility contradiction by declaring all hardware evidence future work. Missing required evaluation definitions remain an incomplete preparation check, not fabricated fixtures.

Correct the owning layer and affected dependents, then hash the final artifacts. Refresh standing for material resumable changes. Do not rehash stale contracts merely to make a receipt pass. Preserve existing instructions and govern actual task gates with the project constitution. Reset recovery and preparation-only stopping are part of delivery, not implementation authority.

Use one concise source map and one preparation receipt, linking necessary evidence instead of copying it into many reports. An incomplete lifecycle honestly describes unfinished work; it does not satisfy a requested native-preparation deliverable. Complete independent work and name the next unfinished preparation operation.

## Refining an existing specification package

*Formerly `#refining-an-existing-specification-package`, version 2.5.1.*

Read when updating a prior spec-prep run, incorporating steering into a prepared package, or validating whether its inputs and outputs still agree. This reference replaces the earlier universal two-copy synchronization recipe. It specializes the existing change-propagation rule; artifact roles remain defined in `references/artifact-contract.md#canonical-artifact-contract` and evidence meanings in `#evidence-and-source-preservation`.

### Resolve authority before changing documents

Inspect the requested package, scoped instructions, workbench, preparation receipt and current continuity. Distinguish:

- Preserved evidence: original prompts, attachments, earlier drafts and immutable input snapshots. Keep original bytes and provenance. Record later steering as a new source or amendment rather than rewriting history.
- Maintained inputs: the requirements/design/intent documents the project explicitly uses to generate or revise native outputs. Keep these current when the authorized delta affects them, so a later preparation run preserves the change.
- Operational outputs: the project's native specification, plan, tasks, contracts and supporting artifacts. These govern implementation within the recorded authorization.

Map the actual paths and their dependencies. A package need not contain a separate input trio; do not create duplicate requirements/spec or design/plan authorities just to satisfy this procedure. Where both exist, record how maintained inputs feed outputs and which document owns each decision. Preserve IDs and naming conventions. Historical drafts are evidence, not regeneration sources that can override newer accepted decisions.

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

Keep existing clause, task and evaluation identifiers stable. Bind every required functional and quality clause according to the project's evaluation convention. Distinguish public acceptance from evaluator-only definitions: an implementing agent must not open or rewrite protected evaluations. Arrange evaluator-owned updates when required, or mark that dependent gate incomplete. An external path alone does not establish isolation.

Review source preservation, cross-document consistency and feasibility, not merely identifier counts. A clean hash cannot establish that conflicting contracts are coherent. Record material decisions and outcomes in the existing ledger and refresh standing; do not mark unexecuted implementation tasks complete.

### Validate and refresh the receipt

Resolve the skill root, intake root, build root, feature root and external evaluation location separately. Run helpers from the loaded skill, not from an assumed scripts directory in the product. The workbench helper requires a subcommand. With these paths already resolved, the following are command forms for the relevant mechanical checks:

```bash
Validate the intake manifest, write and check the workbench pointers, then run the full validation checks (trace) and the intent/spec audit against the eval store.
```

Select applicable commands for the existing layout; do not fabricate an intake manifest for a package that lacks one. Evaluation binding checks must respect evaluator access restrictions. Count/depth checks are coarse diagnostics, never semantic preservation evidence.

For native preparation, also rerun affected constitution checks, the installed Spec Kit prerequisite checker and semantic analyze using the installed integration or an explicitly equivalent review with named rubric, findings, resolutions and reviewer. Inspect task dependencies and clause coverage. Record each required gate's real command or workflow, input identity, observation time, evidence and limitation. Retained evidence is valid only when its input scope remains unchanged; otherwise mark it stale until rerun. Self-review is not independent review.

After final content and continuity updates, hash the final consumed artifacts and update the existing receipt in its supported format. Preserve legacy receipt identity rather than claiming a new native run. Link fresh evidence; do not relabel old review output with a current observation time. Reread the receipt and verify every hash, path, gate status and implementation boundary. Where `delivery.json` exists or the operation requires a new delivery, validate its package root with `spec-prep-delivery.py`; the skill directory itself is not a product delivery package.

If an archive is part of the requested delivery, create a new versioned bundle without overwriting an uninspected prior artifact. Exclude caches and accidental nested archives; preserve required source assets. Validate a safely extracted copy at a different path, including pointers, applicable gates and receipt hashes. Keep evaluator material out of implementer deliveries. A release or push requires its own actual authority.

Complete the requested operation only when maintained inputs, affected outputs and evidence agree. Otherwise record the exact unfinished gate and next preparation action while preserving independent completed work. Refer to the existing handoff rather than adding a second workflow authority.

## Optional Jev semantic review

*Formerly `#optional-jev-semantic-review`, version 2.5.1.*

Read when Jev review is requested or a bounded semantic check could improve preparation. This reference owns the Jev procedure; no earlier reference covered it. It does not add a mandatory service or approval gate. The agent still executes the selected Spec Kit workflows and records their actual results.

### Availability and fallback

Jev is optional in every deployment. Use it only when the user has not disabled it and an eligible adapter/tool, network access, credentials and authority for the selected external send already exist. Hosted Claude Code or OpenAI agents may lack any of these; inspect available capabilities without assuming access or inspecting secret values. Do not provision Jev as part of ordinary preparation.

When disabled, unavailable or unsuccessful, record the Jev review as `not_run` with a short reason. Preserve any attempted provider call's actual failure in its adapter receipt; `not_run` means no usable Jev semantic verdict was obtained, not that no attempt occurred. Continue deterministic validation and the required agent-mediated semantic review against the same sources and rubric. Attribute the review to the actual reviewer, and label self-review accurately. A separately required independent review is not satisfied by self-review, and a required gate never becomes optional because Jev is absent. Do not retry unavailable access repeatedly, switch providers, request new credentials or incur spend solely to obtain optional advice. If the user separately requests configuring Jev, treat that as its own scoped task.

Jev evaluates supplied state with typed questions. It does not write specifications or replacement prose. Keep exact comparisons and arithmetic in code; the vendor documents limitations with numeric precision, dates, indirection and irrelevant context. Use it for an atomic evidence judgment with an explicit abstention option, then review the cited excerpt yourself. Confidence is a routing signal, not proof of correctness. A stronger model or the human resolves a substantive ambiguity without inventing product scope.

### Where it helps

| Stage | Useful semantic question, with a named excerpt | Deterministic work stays outside Jev |
|---|---|---|
| Intake, before specify/plan | Does this acceptance condition express an observable outcome? Does this design excerpt support this stated constraint? | Intake hashes, files, JSON/schema, read order |
| Generated output | Does this one requirement preserve this source obligation? Is a documented constraint contradicted by this decision? | ID existence, source hashes, clause/eval tags, artifact paths |
| Task generation | Does this task's proposed acceptance exercise the linked requirement? Is a recovery procedure adequate for this named failure? | Task format, dependency cycles, missing paths/gates |
| Governance | Does this plan decision conflict with this quoted principle? | Exact constitution heading set, instruction-file references, receipt checks |
| Implementation, when already authorized | Does this captured acceptance evidence support this one claim? | Actual tests, checksums, numerical boundaries, authorization, checked task state |

Avoid a full-document “approve everything” question, repeated calls on every edit, or use as a constitution/permission oracle. Use the smallest excerpt that can decide each question. Jev checks within one request are independent; a question cannot rely on another answer. When prerequisites or tools fail, record that failure and use the normal deterministic/reviewer workflow. Never label another model's reasoning a Jev verdict.

### Keep the target explicit

For a skill change, `--target skill --root /absolute/path/to/the/skill` must point to the folder containing SKILL.md. Application specs are examples, not the edit target. For project preparation, use `--target project` and the actual build root. A recommendation never edits either root. Review any proposed upstream semantic change against intent, then regenerate the affected plan/tasks/contracts, rerun gates and refresh the preparation receipt after the final writes. Operational ledgers with two path aliases must agree; do not refresh hashes in order to hide drift.

### Typed provider adapter

Build the review request from an explicit packet, perform no discovery, and default to an offline preview. Sources must be UTF-8 files resolving inside the chosen root. The packet chooses excerpts by line range; the receipt fingerprints the complete source files. Requests/responses are capped at 64 KiB and rejected rather than silently truncated. Do not include secrets, private URLs, evaluator-only fixtures or unnecessary project data. Preview the exact request before any approved external send.

Packet example (for a skill with at least two lines in SKILL.md):

```json
{
  "schemaVersion": 1,
  "sources": [
    {"id": "boundary", "path": "SKILL.md", "startLine": 1, "endLine": 2}
  ],
  "checks": [
    {"id": "observable", "criterion": "The described result is an observable deliverable.", "sourceIds": ["boundary"]}
  ]
}
```

Use actual relevant line ranges and criteria for the review; the example demonstrates the packet shape only. Given a reviewed packet at `/tmp/spec-prep-review.json`, this previews the installed canonical skill without a network request:

```bash
Build the request from an explicit packet (target, stage, packet path, request output path); preview the exact request before any approved external send.
```

A separate invocation with `--allow-network` authorizes one request to OpenCode's typed System One API. The adapter reads an existing OPENCODE_API_KEY or OPENCODE_ZEN_API_KEY, then literal OPENCODE_API_KEY/OPENCODE_ZEN_API_KEY assignments in the existing `~/.cuddle-bucket`, then the `opencode.key` entry from the existing OpenCode auth store. The credential file is parsed as data and never executed. It never logs keys, repairs auth, changes provider configuration, follows redirects, retries, or switches to a paid model. The request uses `state` and `questions`, not chat `messages`, and identifies its client truthfully as `spec-prep/2.5.1`. Python’s default urllib user agent was rejected with Cloudflare error 1010 during verification; a truthful application user agent and the documented curl request both succeeded. Error receipts distinguish that edge rejection from expired credentials without logging provider messages or keys. It pins the requested free ID `jev-1.13-free`; confirm availability before depending on it. OpenCode's current endpoint is `https://opencode.ai/inference/systemone/v1/systemone`. A generic `opencode run` chat session is not the typed decision contract. If the requested CLI path is unavailable, disclose that and use this same-provider API adapter only within the authorized scope.

The adapter returns `supported`, `needs_review` or `abstain` per question, validates IDs/types/distributions/confidence, and records requested/resolved model plus request/source fingerprints. Low confidence, abstention, stale source, malformed response and transport/auth failures cannot become a pass. Status `advisory` means only that the selected semantic checks returned supported advice; `gateEffect` is always `none`, and a reviewer still adjudicates it. `--response` validates recorded/synthetic data offline and explicitly does not establish provider execution. Existing output paths are never overwritten.

No live quality claim is justified by offline transport tests. Record actual provider results separately from semantic review, and retain the original blind response before giving additional context. Use the existing divergence-resolution procedure rather than an unbounded model loop. Jev changes no launch authority, task checkbox or required deterministic gate.

### Sources and local verification

Checked 2026-10-21: [TypeSafe System One API](https://docs.typesafe.ai/api/system-one), [Choice response contract](https://docs.typesafe.ai/primitives/choice), [documented Jev limitations](https://docs.typesafe.ai/model-jaggedness/jev-1.13), [OpenCode model endpoints](https://opencode.ai/v2/docs/console/models/). These establish wire format and model availability declarations; local credential/endpoint success must still be measured.

Run the adapter and validator regressions with:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s spec-prep/tests -v
```
