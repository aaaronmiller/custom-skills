---
name: spec-workflow
description: |-
  Spec-driven development end to end, in three gates. CREATE turns an idea, brain dump, or transcript into a constitution, spec, plan, and tasks. IMPLEMENT executes authored specs through the speckit pipeline to working code. AUDIT backtranslates a downstream artifact and compares the reconstruction to its upstream source, using divergence as the signal. Use for Spec Kit, OpenSpec, and Kiro-style workflows.
  Triggers: "spec this out", "write a PRD", "feature spec", "spec-driven", "speckit", "openspec", "kiro", "requirements.md", "design.md", "run speckit", "build from spec", "execute the specs", "sdd run", "spec drift", "audit the spec", "backtranslation", "does the code match the spec", "cold review".
license: MIT
metadata:
  version: "1.0.0"
  supersedes: "create_new_spec_design_project-skill, speckit-autonomous-run, backtranslation-spec-auditor 2.2.0"
tags:
- spec-driven
- planning
- audit
- coding
---

# Spec Workflow

Three gates over one artifact set. Pick the gate by where the work already is.

| gate | you have | you want |
| --- | --- | --- |
| **CREATE** | an idea, brain dump, or transcript | constitution, spec, plan, tasks |
| **IMPLEMENT** | authored specs | working code |
| **AUDIT** | code or specs that may have drifted | a divergence report |

These were three separate skills. They shared trigger phrases almost
completely - `deprecated/strata` and the old create skill overlapped on 78% of
their quoted triggers, and both claimed "ALWAYS invoke when the user wants to
start a new project" - so which one loaded was arbitrary. One skill with three
gates removes the coin flip.

**This is the classic, non-intent-weaving path.** The [strata](../strata)
skill covers the same three gates while threading recovered intent through
them. Keep both installed to compare them on the same project; reach strata by
naming it or by asking for an intent-driven workflow.

## Gate: CREATE

Turns unstructured input into build-ready specifications.

Full protocol: `references/gate-create-source.md`.

Templates, used in this order:
- `references/constitution.md` - project principles that later gates enforce
- `references/requirements-template.md`
- `references/design-template.md`
- `references/data-architecture-guide.md` - when the feature is data-shaped
- `references/research-checklist.md` - prior art before committing to a design

Do not skip the constitution. Both the implement and audit gates check against
it, and a project without one gives the audit gate nothing to measure drift
from.

## Gate: IMPLEMENT

Executes authored specs through to code.

Full protocol: `references/gate-implement-source.md`.

Prerequisites, checked before starting:
- specs exist and are complete, or a `requirements.md` plus `design.md` pair does
- the `specify` CLI is available
- the project is initialized

The pipeline generates constitution, spec, plan, and tasks, then works the task
list. It is autonomous by design; the constitution is what keeps it bounded.

**Note on templates.** This gate references `templates/constitution-template.md`
and siblings. Those are emitted by the `specify` CLI at run time and are not
shipped here - a skill that carried its own copies would drift from whatever
version of the tool is installed.

## Gate: AUDIT

Reconstructs intent from a downstream artifact, then compares that
reconstruction to its upstream source of truth. Divergence is the audit signal.

Full protocol: `references/gate-audit-source.md`.

- `references/drift-taxonomy.md` - how to classify a divergence once found
- `references/method.md` - the backtranslation procedure
- `references/spec-kit-mapping.md` - which artifact is upstream of which
- `references/cold-pass.md` - blind external review protocol
- `assets/cold-questions-template.md` - the question package format
- `assets/report-template.md` - the output shape

Two rules carried from v2.2.0 that are easy to get wrong:

**Preserve the blind baseline.** When a cold answer diverges, keep its first
answer immutable. Disclose only the smallest missing constraint and
re-evaluate. This separates source ambiguity from real design disagreement
without destroying the blind signal.

**Do not debate every difference.** Use bounded clarification only for material
divergences. Reveal one constraint at a time, without naming or defending the
source design. Stop when the divergence resolves, when no undisclosed material
constraint remains, or after two clarification rounds produce no material
change. Report how many divergences were clarification-resolved against how
many are residual.

## Choosing between this and strata

Run the same project through both and compare the artifacts. They implement the
same three gates over the same template set; strata adds intent recovery ahead
of the create gate and threads it through implement and audit. If the intent
layer does not change what gets built, this skill is the cheaper path.
