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

## Contamination warning

If the same model/session saw both source artifacts and cold questions, do not label the result as blind. Call it an in-session reconstruction audit.
