# Method Reference

This is the detailed method. The operating loop lives in `SKILL.md`; this file explains why it works, where it fails, and how to run the hard parts.

## What backtranslation is here

Reconstruct the intent implied by a downstream artifact, then compare that reconstruction to its upstream source of truth. Divergence is the audit signal.

The move is the same one used in two established techniques:

- **Instruction backtranslation.** Generate the instruction that would have produced a given output, then keep only the high-quality reconstructions (Li et al., *Self-Alignment with Instruction Backtranslation*, arXiv:2308.06259, Meta "Humpback"). The paper's central lesson is that generation is cheap and **self-curation is the hard, decisive step**. The analogue here: reconstructing obligations from `tasks.md` is easy; *classifying* whether each divergence is real drift, an equivalent route, or a better alternative is where the audit earns its keep.
- **Round-trip correctness.** Describe code in natural language, regenerate the code, and treat consistency between original and reconstruction as an unsupervised validation signal that needs no ground-truth reference (Allamanis et al., *Unsupervised Evaluation of Code LLMs with Round-Trip Correctness*, arXiv:2402.08699). Related systems apply NL->formal->NL round-trips as a consistency check (VeriTrans, arXiv:2604.10341; roundtrip autoformalization, arXiv:2604.25031). Spec auditing is the same round-trip, one abstraction layer up: intent -> artifact -> reconstructed intent.

Requirements-engineering research is converging on the same shape, using LLMs to recover and verify trace links between requirements, design, and downstream artifacts (e.g. TraceLLM, arXiv:2602.01253). This skill is a semantic, reconstruction-based version of that idea rather than a link-matching one.

## Epistemic status: what the signal proves

Be honest about this in every report.

- **Round-trip agreement is necessary, not sufficient.** A clean backtranslation bounds drift; it does not prove the artifact is correct. Both directions can share the same blind spot and still agree. The round-trip literature reports this directly: high round-trip similarity correlates with correctness but does not guarantee it.
- **In-session reconstruction is contaminated.** If the auditing session already read the upstream source, its reconstruction of the downstream artifact is not blind. Label it an *in-session reconstruction audit*. It still catches gross drift, but do not call it blind or first-principles.
- **The strong signal requires isolation.** A genuine cold pass uses a separate model or session that never saw the source. That is the only configuration that supports a first-principles claim (see `cold-pass.md`).
- **Divergence needs an etiology.** Not all divergence is loss. Before flagging drift, decide whether the downstream is worse, equivalent by another route, or better than the source. A better downstream alternative is a finding about the *source*, not a defect downstream.

## Why not make `tasks.md` the main surface

`tasks.md` is late, lossy, and implementation-shaped. A task list routinely drops: why the feature exists, user-value framing, non-goals, rationale, alternatives considered, constraints that never became tasks, and acceptance behavior not yet encoded as tests. Use it as a downstream audit target, never as the canonical intent surface.

## Best primary surfaces

Use `requirements.md` as the product-intent authority and `design.md` as the technical-intent authority. If those do not exist, fall back to Spec Kit's generated `spec.md` and `plan.md` as the best available authorities, and say so.

## Downstream-first reconstruction

For a non-cold audit, preserve signal by reading the downstream artifact first.

Task-audit sequence:

1. Read only `tasks.md`.
2. Infer product obligations, technical obligations, acceptance criteria, constraints, and non-goals implied by the tasks.
3. Then read `requirements.md`, `design.md`, `spec.md`, `plan.md`.
4. Compare inferred obligations to the authority artifacts.

This is not blind, but it prevents the most obvious contamination: reading the answer key before reconstructing from the derived artifact.

## Strict cold pass

Full separation:

1. Create questions from the source artifact.
2. Strip answer keys and source material.
3. Have another model or session answer with no access to source artifacts.
4. Return answers for comparison.

Use only for first-principles validation, high-stakes architecture, or when the current session is likely contaminated. Overkill for everyday drift checks.

A cold pass may be followed by **bounded constraint clarification** for material divergences. The first cold answer remains immutable; later answers are a trajectory, not replacements. This lets the audit distinguish an answer that differed because the question/source omitted a decisive constraint from an answer that still differs after complete legitimate constraint disclosure. See `cold-pass.md` for the stopping rule and metrics.

## Question construction

A good backtranslation question gives problem context without revealing the chosen solution.

Bad:

```text
Our design uses SQLite plus markdown snapshots. Is that good?
```

Good:

```text
For a local-first agent that must retain recent session context, searchable durable
notes, and offline operation without hosted infrastructure, what persistence structure
should it use, and why?
```

## Contamination checks

A question is contaminated when it reveals: exact implementation technologies that are not hard constraints, exact numeric thresholds from the source, internal names that point to the answer, evaluation framing such as "is our design optimal?", or the target answer's structure.

A downstream reconstruction is contaminated when the session read the upstream authority before reconstructing the downstream artifact.

## Classification, the decisive step

Reconstruction produces candidate obligations. Classification turns them into findings. For each obligation ask:

- Is the same user obligation preserved?
- Is the same technical obligation preserved?
- Did constraints survive? Did non-goals survive?
- Are acceptance signals still testable?
- Did the downstream invent behavior?
- Does every required obligation have an implementation task?

Then assign a taxonomy label and severity (`drift-taxonomy.md`). Do not emit unclassified reconstructions; a reconstruction that is never judged is just a summary and adds no audit value.

## Output discipline

Default to one report. Internal obligation maps are allowed as reasoning scaffolds, but do not write them to files unless the user asks for traceability or the project is too large to audit without durable intermediate state.
