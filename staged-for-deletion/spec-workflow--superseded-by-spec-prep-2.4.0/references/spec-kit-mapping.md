# Spec Kit Mapping Reference

## Common user workflow

The intended workflow for this skill:

1. User has an idea and discusses it with a model.
2. At the end of the conversation, the model packages the idea into:
   - `requirements.md`: what, why, users, scope, acceptance behavior
   - `design.md`: how, architecture, tradeoffs, constraints, data/contracts
3. User initializes Spec Kit.
4. User runs `/speckit.specify`, referencing or attaching `requirements.md`.
5. User runs `/speckit.plan`, referencing or attaching `design.md`.
6. User runs `/speckit.tasks`.
7. This skill audits the translation boundaries and decomposition drift.

## Artifact roles

| Artifact | Role | Audit use |
|---|---|---|
| `requirements.md` | Product intent authority | Source for product obligations |
| `design.md` | Technical intent authority | Source for design obligations |
| `spec.md` | Generated product-spec translation | Check against `requirements.md` |
| `plan.md` | Generated technical-plan translation | Check against `design.md` |
| `research.md` | Planning decisions and alternatives | Check rationale preservation |
| `data-model.md` | Entity and relationship model | Check technical/data design preservation |
| `contracts/` | Interface contracts | Check external behavior/API preservation |
| `quickstart.md` | End-to-end validation guide | Check acceptance/validation preservation |
| `tasks.md` | Implementation decomposition | Infer implied obligations, then compare upstream |

## Stage-specific audit

### Before Spec Kit

Inputs:

- `requirements.md`
- `design.md`

Audit:

- Requirements clarity
- Acceptance behavior
- Scope boundaries
- Technical rationale
- Design constraints
- Missing non-goals

Output:

- One readiness report

### After `/speckit.specify`

Inputs:

- `requirements.md`
- generated `spec.md`

Audit:

- Did product intent survive?
- Did generated spec add unsupported scope?
- Did it drop acceptance criteria or edge cases?
- Did implementation details leak into product spec?

### After `/speckit.plan`

Inputs:

- `design.md`
- generated `plan.md`
- optional `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

Audit:

- Did architecture survive?
- Did constraints survive?
- Did research preserve alternatives and rationale?
- Did data model/contracts match design?
- Does quickstart validate the intended behavior?

### After `/speckit.tasks`

Inputs:

- `tasks.md`
- all available upstream artifacts

Audit:

- Infer what the task list thinks the feature is.
- Compare inferred obligations to product and technical authorities.
- Find missing tasks, orphan tasks, sequencing risks, and test gaps.

## Relationship to `/speckit.analyze`

This skill is a semantic drift audit. It is adjacent to a consistency analyzer but not identical.

A consistency analyzer checks the artifacts side-by-side.

This skill reconstructs intent from generated/downstream artifacts first, then compares that reconstruction against source intent. That makes it better at finding subtle intent loss and task decomposition drift.

## Recommended default behavior

If all files exist, run all relevant passes and emit one report.

Do not produce separate files for each pass unless requested.
