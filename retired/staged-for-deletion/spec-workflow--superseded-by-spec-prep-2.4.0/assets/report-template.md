# Backtranslation Audit Report: [Project/Feature]

Generated: [date]

## Verdict

[One paragraph. Say whether the workflow is safe to continue, needs targeted fixes, or should pause before implementation.]

## Surface Map

| Surface | Found? | Role | Notes |
|---|---:|---|---|
| `requirements.md` | [yes/no] | Product intent authority | |
| `design.md` | [yes/no] | Technical intent authority | |
| `spec.md` | [yes/no] | Product translation | |
| `plan.md` | [yes/no] | Technical translation | |
| `research.md` | [yes/no] | Rationale/alternatives | |
| `data-model.md` | [yes/no] | Data design | |
| `contracts/` | [yes/no] | Interfaces | |
| `quickstart.md` | [yes/no] | End-to-end validation | |
| `tasks.md` | [yes/no] | Decomposition | |

## Top Findings

### F-001: [SEVERITY] [CLASSIFICATION] [Title]

Source of truth: [file/section]

Downstream artifact: [file/section]

What drifted: [specific drift]

Why it matters: [impact]

Recommended fix: [specific correction]

## Product Intent Drift

[Findings from requirements -> spec and tasks -> requirements.]

## Technical Design Drift

[Findings from design -> plan/generated technical artifacts and tasks -> design.]

## Task Decomposition Drift

[Missing tasks, orphan tasks, sequencing risks, test gaps.]

## Acceptance and Validation Gaps

[Missing acceptance criteria, missing tests, missing quickstart validation, missing contract checks.]

## Remediation Plan

1. [Critical fix]
2. [High priority fix]
3. [Medium priority fix]

## Optional Cold Pass

[Only include if useful. Say whether a blind external model pass would materially improve confidence. If yes, specify which surface to target: requirements, design, or tasks.]

[If cold answers were actually evaluated, include: material divergences, clarification-eligible divergences, clarification-resolved divergences, residual divergences, alternatives strengthened, clarification resolution rate, and mean clarification rounds. Do not emit these fields for an unperformed cold pass.]

## Continue / Pause Recommendation

[Continue to next Spec Kit stage, continue after fixes, or pause before implementation.]
