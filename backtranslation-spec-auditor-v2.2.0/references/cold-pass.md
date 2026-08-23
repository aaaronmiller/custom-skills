# Optional Cold Backtranslation Pass

Use this reference only when the user asks for blind review, S-tier validation, external model audit, or strict backtranslation.

## When to use

Use a cold pass for:

- high-stakes architecture
- uncertain technical design
- major divergences where the current model may be contaminated
- comparing whether a design is first-principles obvious
- generating a separate review package for another model/session

Do not use a cold pass for routine task coverage checks unless requested.

## Files

Default generated file:

```text
cold-questions.md
```

Optional internal answer key, only if the user asks and it will not be sent to the answering model:

```text
cold-answer-key.md
```

## Generation process

1. Choose target source:
   - `requirements.md` for product intent
   - `design.md` for technical design
   - `spec.md` or `plan.md` only if upstream files do not exist
2. Extract atomic obligations internally.
3. Generate one question per obligation.
4. Include enough problem context for a competent model to answer.
5. Do not reveal the target answer.
6. Do not include exact source wording unless it is unavoidable domain context.
7. Do not include answer keys in `cold-questions.md`.

## External model instructions

Use this instruction block in `cold-questions.md`:

```text
Answer each question from first principles. You have not been given the implementation or source specification. For each answer, provide:
1. Recommended requirement/design.
2. Rationale.
3. Hard constraints assumed.
4. Confidence from 1-10.
Do not speculate about hidden project details. State assumptions explicitly.
```

## Comparison after answers return

Classify each answer as:

- `CONFIRMED`: matches the source obligation.
- `DIVERGENT-BETTER`: answer is clearly stronger and feasible.
- `DIVERGENT-EQUIVALENT`: different approach, similar outcome.
- `DIVERGENT-INFEASIBLE`: violates hard constraint.
- `DIVERGENT-AMBIGUOUS`: unclear due to question or domain uncertainty.
- `NON-OBVIOUS-BUT-CORRECT`: source design is defensible but not first-principles default.
- `SUBOPTIMAL`: source design is likely weaker.

## Bounded clarification for material divergences

The blind answer is the experimental baseline. Preserve it verbatim before any follow-up. Do not clarify `CONFIRMED` or `DIVERGENT-EQUIVALENT` answers unless a material uncertainty remains. For `DIVERGENT-INFEASIBLE`, clarify only when the violated hard constraint was absent or ambiguous in the cold question; if it was already explicit, the infeasibility is established. Clarification is for cases where a missing or ambiguous constraint could change the judgment, or where a high-impact alternative survives first-pass comparison.

For each eligible divergence:

1. Record the initial recommendation, assumptions, confidence, and comparison label as `A0`. Never overwrite it.
2. Identify the **smallest source constraint** that the cold question did not safely expose and that could plausibly explain the divergence.
3. Reveal only that constraint. Do not reveal the chosen implementation, source rationale, answer-key wording, or framing such as “our design uses X.”
4. Ask the model whether the new constraint changes its recommendation, which inference changed, and its new confidence. Record this as `A1`.
5. Repeat once only if another genuinely material, previously undisclosed constraint remains. A third round is allowed only when round 2 surfaces a new dependency that could not reasonably have been known earlier.
6. Stop immediately when the answer converges, no material undisclosed constraint remains, or two rounds produce no material recommendation change.

Use this follow-up shape:

```text
Additional constraint: <one source-supported constraint, stated neutrally>.

Re-evaluate your previous answer from first principles.
- Does this constraint change your recommendation?
- What inference, if any, changed?
- Give the revised recommendation and confidence from 1-10.
Do not infer an intended implementation from the fact that this constraint was disclosed.
```

### Trajectory labels

After clarification, add exactly one trajectory label to each eligible material divergence:

- `CLARIFICATION-RESOLVED`: the recommendation converges after a previously omitted or ambiguous constraint is disclosed. Treat this primarily as a **source/question clarity finding**; patch the source so future readers can derive the decision without privileged context.
- `RESIDUAL-DIVERGENCE`: the model still recommends a materially different approach after all legitimate constraints are known. Treat this as a **substantive design-review finding**, not an ambiguity.
- `ALTERNATIVE-STRENGTHENED`: the alternative remains feasible and becomes better supported after clarification. Escalate for explicit design comparison.

Do not invent a semantic-distance score. The useful quantitative outputs are observable counts:

```text
material_divergences = N
clarification_eligible = E
clarification_resolved = R
residual_divergences = D
alternatives_strengthened = B
clarification_resolution_rate = R / E   (when E > 0)
mean_rounds_per_eligible_divergence = total_clarification_rounds / E
```

These metrics answer two different questions that a one-shot cold pass conflates: **how much disagreement came from missing/ambiguous information, and how much survived complete constraint disclosure?** Keep them out of routine audits when no cold pass was performed.

## Contamination warning

If the same model/session saw both source artifacts and cold questions, do not label the result as blind. Call it an in-session reconstruction audit.
