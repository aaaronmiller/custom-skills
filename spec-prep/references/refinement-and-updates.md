---
title: Refining an existing specification package
version: "2.5.1"
tags: [spec-prep, refinement, updates, validation, speckit]
---

# Refining an existing specification package

Read when updating a prior spec-prep run, incorporating steering into a prepared package, or validating whether its inputs and outputs still agree. This reference replaces the earlier universal two-copy synchronization recipe. It specializes the existing change-propagation rule; artifact roles remain defined in `artifact-contract.md` and evidence meanings in `validation-integrity.md`.

## Resolve authority before changing documents

Inspect the requested package, scoped instructions, workbench, preparation receipt and current continuity. Distinguish:

- Preserved evidence: original prompts, attachments, earlier drafts and immutable input snapshots. Keep original bytes and provenance. Record later steering as a new source or amendment rather than rewriting history.
- Maintained inputs: the requirements/design/intent documents the project explicitly uses to generate or revise native outputs. Keep these current when the authorized delta affects them, so a later preparation run preserves the change.
- Operational outputs: the project's native specification, plan, tasks, contracts and supporting artifacts. These govern implementation within the recorded authorization.

Map the actual paths and their dependencies. A package need not contain a separate input trio; do not create duplicate requirements/spec or design/plan authorities just to satisfy this procedure. Where both exist, record how maintained inputs feed outputs and which document owns each decision. Preserve IDs and naming conventions. Historical drafts are evidence, not regeneration sources that can override newer accepted decisions.

A validation-only request produces findings and evidence. A refinement request authorizes the relevant document changes within its scope. Neither grants implementation, publication or launch authority.

## Resolve the delta at its owning layer

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

## Apply and review the affected region

Checkpoint relevant files before broad or architectural edits and retain unrelated working changes. Preserve newly supplied briefs with provenance. For private local reference material, retain only the authorized relevant content or a sufficient locator and fingerprint; do not indiscriminately copy a vault or credentials into a distributable package.

Update maintained inputs and their corresponding native outputs together where both exist. Re-derive a changed dependency region as a unit when tasks are added, combined or reordered. Check downstream consumers: contracts and schemas, public acceptance, task gates, recovery, source dispositions, instruction adapters and reset handoff. Amend the constitution only for an actual governance change.

Keep existing clause, task and evaluation identifiers stable. Bind every required functional and quality clause according to the project's evaluation convention. Distinguish public acceptance from evaluator-only definitions: an implementing agent must not open or rewrite protected evaluations. Arrange evaluator-owned updates when required, or mark that dependent gate incomplete. An external path alone does not establish isolation.

Review source preservation, cross-document consistency and feasibility, not merely identifier counts. A clean hash cannot establish that conflicting contracts are coherent. Record material decisions and outcomes in the existing ledger and refresh standing; do not mark unexecuted implementation tasks complete.

## Validate and refresh the receipt

Resolve the skill root, intake root, build root, feature root and external evaluation location separately. Run helpers from the loaded skill, not from an assumed scripts directory in the product. The workbench helper requires a subcommand. With these paths already resolved, the following are command forms for the relevant mechanical checks:

```bash
python3 "$skill_root/scripts/spec-prep-intake.py" "$intake_root"
python3 "$skill_root/scripts/spec-prep-workbench.py" write "$intake_root" --build-root "$build_root"
python3 "$skill_root/scripts/spec-prep-workbench.py" check "$intake_root"
python3 "$skill_root/scripts/spec-prep-validate.py" "$feature_root" --build-root "$build_root" --evals "$eval_store" --trace
python3 "$skill_root/scripts/spec-prep-validate.py" --audit "$feature_root/intent.md" "$feature_root/spec.md"
```

Select applicable commands for the existing layout; do not fabricate an intake manifest for a package that lacks one. Evaluation binding checks must respect evaluator access restrictions. Count/depth checks are coarse diagnostics, never semantic preservation evidence.

For native preparation, also rerun affected constitution checks, the installed Spec Kit prerequisite checker and semantic analyze using the installed integration or an explicitly equivalent review with named rubric, findings, resolutions and reviewer. Inspect task dependencies and clause coverage. Record each required gate's real command or workflow, input identity, observation time, evidence and limitation. Retained evidence is valid only when its input scope remains unchanged; otherwise mark it stale until rerun. Self-review is not independent review.

After final content and continuity updates, hash the final consumed artifacts and update the existing receipt in its supported format. Preserve legacy receipt identity rather than claiming a new native run. Link fresh evidence; do not relabel old review output with a current observation time. Reread the receipt and verify every hash, path, gate status and implementation boundary. Where `delivery.json` exists or the operation requires a new delivery, validate its package root with `spec-prep-delivery.py`; the skill directory itself is not a product delivery package.

If an archive is part of the requested delivery, create a new versioned bundle without overwriting an uninspected prior artifact. Exclude caches and accidental nested archives; preserve required source assets. Validate a safely extracted copy at a different path, including pointers, applicable gates and receipt hashes. Keep evaluator material out of implementer deliveries. A release or push requires its own actual authority.

Complete the requested operation only when maintained inputs, affected outputs and evidence agree. Otherwise record the exact unfinished gate and next preparation action while preserving independent completed work. Refer to the existing handoff rather than adding a second workflow authority.
