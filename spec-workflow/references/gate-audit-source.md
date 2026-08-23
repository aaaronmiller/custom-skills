---
name: backtranslation-spec-auditor
description: Audits spec-driven development artifacts by reconstructing intent from a downstream artifact, then comparing that reconstruction to its upstream source of truth. Divergence is the audit signal. Use for Spec Kit, OpenSpec, and Kiro-style workflows, requirements.md/design.md reviews, spec.md/plan.md/tasks.md drift checks, decomposition audits, and cold backtranslation question generation.
license: MIT
compatibility: Designed for Claude Code and other Agent Skills compatible clients. No required scripts or network access.
metadata:
  version: "2.2.0"
  author: "Ice-ninja archival workflow"
---

# Backtranslation Spec Auditor

Use this skill to check whether intent survived translation across the artifacts of a spec-driven workflow: `requirements.md`, `design.md`, generated `spec.md`/`plan.md`, and `tasks.md`.

Default behavior is deliberately small: produce **one report**. Intermediate maps are internal reasoning, not files for the user to manage. Write extra files only when explicitly asked.

## The method

The whole skill is one loop applied at each translation boundary:

1. **Reconstruct.** Read the downstream artifact and infer the obligations it implies: product intent, technical intent, constraints, acceptance signals, non-goals. Do this before reading the upstream source, so the reconstruction is not just a paraphrase of the answer key.
2. **Compare.** Read the upstream authority. Match meaning, not wording.
3. **Classify.** Label each obligation with a drift type and severity (taxonomy below). This step is where the value is, not the reconstruction. A reconstruction that is never classified is just a summary.

Backtranslation means step 1: the same move as reconstructing an instruction from its output, or regenerating source code from a natural-language description of it. Both are established techniques (see `references/method.md` for the grounding).

### What the signal is and is not

Divergence between the reconstruction and the source is a **flag**, not a verdict. Treat it honestly:

- **Agreement is necessary, not sufficient.** A downstream artifact that backtranslates cleanly to its source can still be wrong if both share the same blind spot. Round-trip agreement bounds drift; it does not prove correctness.
- **In-session reconstruction is a weak signal.** If the same session already read the upstream source, the reconstruction is contaminated. Call it an *in-session reconstruction audit*, never a blind audit.
- **A cold pass is the strong signal.** True blindness requires a separate model or session that never saw the source (see Cold pass below).
- **Divergence has causes.** Before flagging drift, ask whether the downstream artifact is *worse*, *equivalent by another route*, or *better than the source*. A better alternative is a finding about the source, not the downstream.
- **Preserve the blind baseline.** When a cold answer diverges, keep its first answer immutable. If ambiguity or a missing constraint could explain the difference, disclose only the smallest missing constraint and re-evaluate. This separates source ambiguity from substantive design disagreement without destroying the original blind signal.

## Authority order

When artifacts conflict, higher wins:

1. Explicit user correction in the current request.
2. Project constitution or governing principles, if present.
3. `requirements.md`: product intent (what, why, users, scope, acceptance behavior).
4. `design.md`: technical intent (how, architecture, constraints, tradeoffs, data, contracts).
5. Generated `spec.md`: normalized product translation.
6. Generated `plan.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`: normalized technical translation.
7. `tasks.md`: implementation decomposition.

`tasks.md` is never the source of truth. It is late, lossy, and implementation-shaped, which makes it the best surface for detecting decomposition drift and the worst one for defining intent.

## Surfaces and translation boundaries

Detect what exists. Do not ask the user to pick a mode. Run the loop at every boundary present.

Common paths:

```text
requirements.md   design.md
spec.md   plan.md   research.md   data-model.md   quickstart.md   tasks.md   contracts/
specs/*/{spec,plan,research,data-model,quickstart,tasks}.md   specs/*/contracts/
.specify/memory/constitution.md   memory/constitution.md
```

If multiple Spec Kit feature directories exist, use the one the user named; otherwise use the most recently modified plausible one and state that choice in the report.

Boundaries, in order of leverage:

- **Upstream readiness** (`requirements.md`, `design.md` alone, before generation). Find ambiguity, missing acceptance signals, unstable scope, hidden constraints, absent non-goals, and design rationale gaps before generated artifacts amplify them.
- **Product translation** (`requirements.md` -> `spec.md`). Did product intent survive normalization?
- **Technical translation** (`design.md` -> `plan.md` and generated technical artifacts). Did the architecture, constraints, and rationale survive planning?
- **Decomposition drift** (`tasks.md` reconstructed, compared to all upstream). Reconstruct what the task list thinks the feature is, then compare.

If only `tasks.md` exists, run decomposition reconstruction and warn that this is a lossy audit with no upstream authority to check against.

## Drift taxonomy

Classify each obligation. Full definitions and the finding format are in `references/drift-taxonomy.md`.

`CONFIRMED` preserved · `LOST-INTENT` upstream intent absent downstream · `INVENTED-SCOPE` downstream adds unsupported behavior · `WEAKENED-CONSTRAINT` hard limit dropped or softened · `NON-GOAL-VIOLATION` excluded work implied · `ACCEPTANCE-GAP` requirement has no pass/fail signal · `DESIGN-DRIFT` plan/tasks no longer match `design.md` · `RATIONALE-GAP` choice survives, reason vanished · `TASK-GAP` obligation with no task · `ORPHAN-TASK` task with no upstream obligation · `ORDERING-RISK` sequence causes rework or invalid partial state · `IMPLEMENTATION-CONTAMINATION` product spec carries implementation detail too early · `AMBIGUOUS-SOURCE` upstream too vague to judge fairly.

Severity: `CRITICAL` (constitution, hard constraint, security/privacy boundary, core user promise) · `HIGH` (required behavior, acceptance criteria, architecture, data model, blocking dependency) · `MEDIUM` (ambiguity, rationale loss, sequencing risk, optional-scope drift) · `LOW` (naming, polish, duplication, minor trace issue).

## Output

Default: one file, `backtranslation-audit.md`, with remediation inside it. Use the structure in `assets/report-template.md`. For inline responses include: verdict, surface map, critical/high findings first, medium/low after, remediation, and a continue/pause recommendation.

Do not create separate obligation ledgers, traces, question files, or patch plans unless the user asks. Extra files allowed only on request: `cold-questions.md` (blind external pass), `trace-map.md` (large-project provenance), `corrected-*.md` (rewrites).

The user should never have to manage five intermediate files to learn whether the plan drifted. Reason internally with temporary obligation maps; hand back what drifted, why it matters, and what to change.

## Cold pass

Generate `cold-questions.md` only when the user asks for a blind external pass, strict backtranslation, or S-tier review, or when a finding genuinely needs blind validation. Each question carries enough problem context to be answerable but never reveals the chosen solution. Never ship the answer key with the questions.

When cold answers return, **do not automatically debate every difference**. Preserve the initial answer, then use bounded clarification only for material divergences that may be caused by missing or ambiguous constraints. Reveal one constraint at a time without naming or defending the source design; stop after the divergence resolves, no undisclosed material constraint remains, or two clarification rounds have produced no material change. Report how many material divergences were clarification-resolved versus residual. This turns cold review into a discriminator between specification ambiguity and genuine architectural disagreement without adding routine prompt volume. Protocol and comparison labels are in `references/cold-pass.md`; the package format is in `assets/cold-questions-template.md`.

## References

Load only when needed:

- `references/method.md`: the method in depth, contamination rules, question construction, and the literature it rests on.
- `references/spec-kit-mapping.md`: how boundaries map to Spec Kit stages, and the relationship to `/speckit.analyze`.
- `references/drift-taxonomy.md`: full classification definitions, severity rules, and finding format.
- `references/cold-pass.md`: strict external blind-question workflow.
- `assets/report-template.md`: one-report output structure.
- `assets/cold-questions-template.md`: optional external-model package.
