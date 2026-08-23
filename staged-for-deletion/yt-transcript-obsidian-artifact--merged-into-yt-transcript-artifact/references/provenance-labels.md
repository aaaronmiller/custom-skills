# Provenance Labels

Use provenance labels to prevent contamination between transcript facts, reusable constructed templates, and the model's own reasoning.

## Labels

### `[VERBATIM]`

Use only for exact language from the transcript:
- Direct quotes.
- Commands.
- Code.
- Formulas.
- Prompts.
- Recipes.
- URLs.
- Exact rule names or named principles.
- Exact numerical claims.

Do not "clean up" a `[VERBATIM]` quote except for obvious transcript artifacts when necessary. If cleaned, call it `[DESCRIBED]`.

### `[DESCRIBED]`

Use for a speaker-described process or idea that is paraphrased:
- "The speaker recommends..."
- "The process described is..."
- "The example shows..."

### `[CONSTRUCTED]`

Use for reusable templates, checklists, examples, or explanations synthesized from transcript ideas:
- A generalized prompt template.
- A release checklist derived from advice.
- A table format created by the agent.
- An example scenario not in the transcript.

Always make clear that constructed material is not transcript fact.

### `[INFERRED]`

Use for implementation paths or mechanisms extrapolated from transcript evidence plus general domain knowledge.

Required pattern:

```text
# [INFERRED] Conceptual pattern for {{described_capability}}
# Rationale: {{why this follows from transcript evidence but is not confirmed}}
{{pattern}}
```

Avoid strong inferences for safety-critical, legal, medical, financial, or current-fact claims. State what requires verification.

## Common mistakes

- Labeling a paraphrase as `[VERBATIM]`.
- Turning a speaker's vague suggestion into a concrete command without `[CONSTRUCTED]`.
- Treating an inferred implementation as if it appeared in the transcript.
- Omitting provenance labels from examples.
- Marking transcript-inspired templates as `[DESCRIBED]` instead of `[CONSTRUCTED]`.
