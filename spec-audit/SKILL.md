---
name: spec-audit
description: |-
  Audits spec-driven artifacts by reconstructing intent from a downstream artifact and comparing it to its upstream source; divergence is the signal. Use for spec drift checks, decomposition audits, requirements/design reviews, backtranslation, cold review, and "does the code match the spec".
  Triggers: "audit the spec", "spec drift", "backtranslation", "does the code match the spec", "cold review", "decomposition audit", "audit requirements", "drift check".
license: MIT
metadata:
  version: "1.0.0"
  lineage: "spec-workflow AUDIT gate (backtranslation-spec-auditor 2.2.0) split out; spec-prep covers CREATE and IMPLEMENT"
tags:
- spec-driven
- audit
---

# Spec Audit

Reconstruct intent from a downstream artifact, compare it to its upstream source of truth, classify the divergence. One report out.

Full protocol: `references/gate-audit-source.md`.

Supporting files:

- `references/method.md` — backtranslation grounding, epistemics, contamination rules.
- `references/cold-pass.md` — blind external-review protocol (only on request or genuine blind-validation need).
- `references/drift-taxonomy.md` — 13-label classification + severity + finding format.
- `references/spec-kit-mapping.md` — per-stage checklists (pre-Spec-Kit, post-specify, post-plan, post-tasks) and the `/speckit.analyze` distinction.
- `assets/report-template.md` — one-report output shape.
- `assets/cold-questions-template.md` — external-model question package.

Two rules: preserve the blind baseline (first cold answer immutable; disclose only the smallest missing constraint on re-evaluate); do not debate every difference (bounded clarification, max two rounds without material change, then report residual).
