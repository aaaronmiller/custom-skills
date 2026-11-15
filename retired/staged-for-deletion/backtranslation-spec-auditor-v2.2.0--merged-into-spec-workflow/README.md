# Backtranslation Spec Auditor

A compact Agent Skill for auditing spec-driven development drift without drowning the user in intermediate files.

## What it does

It reconstructs the intent implied by a downstream artifact, compares that reconstruction to the upstream source of truth, and classifies the divergence. Divergence is the audit signal, not a verdict: round-trip agreement bounds drift but does not prove correctness, and an in-session reconstruction is not a blind audit. For material cold-pass disagreements, v2.2 adds bounded constraint clarification while preserving the original blind answer, so the report can separate ambiguity-driven disagreement from residual design disagreement. The method and its grounding (instruction backtranslation, round-trip correctness) are in `references/method.md`.

Default output: one report, usually `backtranslation-audit.md`.

## Best workflow

1. Discuss idea with model.
2. Ask model to produce `requirements.md` and `design.md`.
3. Run the skill before Spec Kit to audit readiness.
4. Run `/speckit.specify` with `requirements.md` attached or referenced.
5. Run the skill to compare `requirements.md` -> `spec.md`.
6. Run `/speckit.plan` with `design.md` attached or referenced.
7. Run the skill to compare `design.md` -> `plan.md` and generated technical artifacts.
8. Run `/speckit.tasks`.
9. Run the skill to audit task decomposition before implementation.

## Package layout

```text
backtranslation-spec-auditor/
├── SKILL.md
├── README.md
├── LICENSE
├── references/
│   ├── method.md
│   ├── spec-kit-mapping.md
│   ├── drift-taxonomy.md
│   └── cold-pass.md
└── assets/
    ├── report-template.md
    └── cold-questions-template.md
```

## Design choice

This version deliberately avoids emitting obligation ledgers, trace maps, and question packages by default. Those are useful internal concepts, but user-facing output should stay compact unless traceability or external cold review is explicitly requested.
