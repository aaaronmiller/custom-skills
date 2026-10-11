---
name: refinement-loop
description: |
  Use when: anything should get better through repeated passes instead of one shot — improving a prompt, plan, document, design, codebase, strategy, or deliverable; evaluating work against a rubric and iterating to a score threshold; running generate-critique-revise cycles; adding a judge, critic, or evaluator role to a workflow; making long sessions cohere (scratchpad, gated phases, durable rules). Triggers: "refine this", "iterate until", "evaluate and improve", "score this", "critic loop", "self-improve", "revise until it passes", "make this better in rounds", "assessment loop", "improvement loop", "add a rubric", "judge this work", "run it again with feedback", "polish loop", "quality gate", "threshold".
license: MIT
metadata:
  author: cheta
  version: "1.0"
---

# Refinement Loop

> Stop accepting first drafts. Score them, diagnose them, revise them, repeat.

Any artifact improves through one loop: **Generate → Evaluate → Diagnose → Revise**, with a separate critic, a numeric threshold, and a hard round cap. Grounded in the Self-Refine paper (Madaan et al. 2023, ~20% average gains inference-only), LLM-as-judge practice (reasoning before score, strict output), and the field-tested critic pattern from AI Search's GPT-6 Astra demo (separate critic, 0–10 scale, stop at 8, cap 3 rounds).

## Core loop

```
v0 = GENERATE(brief)
repeat:
  verdict = CRITIC(vN)          # separate role/agent; never the author grading itself
  if verdict.score >= THRESHOLD: ship vN
  vN+1 = REVISE(vN, verdict.ranked_fix_list)
until rounds == CAP             # final round ships even under threshold
```

Three rules keep it honest. The critic must be a different role from the builder (same model self-critiquing is the weakest form; a different model family is strongest). Every verdict needs evidence quoted from the work, not vibes. And the cap is sacred: a loop without a cap is a loop without an end.

## Adjustment vector L(R, T, G, W, J, S)

Tune six dials per task instead of rewriting the process:

| Dial | Name | What it sets | Typical |
|------|------|--------------|---------|
| **R** | Rounds | `threshold/cap`, e.g. `8/3` = stop at 8, max 3 rounds | `8/3` |
| **T** | Research | Grounding probes between rounds per open gap (0 = none) | `1` |
| **G** | Inbound concepts | Seed material that must be incorporated and checked each round | none |
| **W** | Width | Variants per round: `1` = linear refine, `N` = branch N candidates, judge picks | `1` |
| **J** | Judge separateness | `self` / `role` (same model, critic persona) / `agent` (separate session) / `family` (different model) | `role` |
| **S** | State | `none` / `scratchpad` / `durable` (scratchpad + gated phases + constitution; for long sessions) | task-length decides |

Shorthand: `L(8/3, T1, W1, J:agent, S:durable)`. Defaults `L(8/3, T1, G-, W1, J:role, S:none)` suit most single-session jobs.

## Modes

- **REFINE** (input provided): score it, diagnose it, revise it. The default.
- **CREATE** (no input): generate v0 fast, then enter the loop. Expect v0 to be mediocre; say so.
- **JUDGE** (verdict only): return the scored rubric with quoted evidence, no revision.
- **HARDEN** (long session): REFINE with `S:durable` — scratchpad, gated phases, constitution. See [session-durability.md](session-durability.md).

## Choosing the critic

Match the judge to the stakes. Same-model self-critique catches surface flaws. A hostile persona in a separate turn (`role`) breaks average-first-pass bias. A separate agent session (`agent`, the AI Search pattern) adds independence. A different model family (`family`) neutralizes self-preference and is the choice for anything expensive. Details and prompt fragments: [critic-patterns.md](critic-patterns.md).

## Choosing the rubric

One 0–10 overall score plus 3–6 named dimensions, each with a one-line pass description. The critic reasons first, quotes evidence, then scores; revisions address the ranked fix list top-down. How to write rubrics that actually discriminate: [evaluation-rubrics.md](evaluation-rubrics.md).

## Model notes

Reasoning-effort models (GPT-6 Astra, Claude Fable 5.1) change loop economics: calibrate effort per role (cheap builder, strong critic), keep histories append-only, use XML boundaries and docs-first ordering. Per-model specifics: [model-notes.md](model-notes.md).

## Stop conditions

Ship when score ≥ threshold, rounds hit cap, two consecutive rounds show negligible gain (then pivot or roll back on regression), or the brief itself proves wrong (re-scope, don't iterate a bad target).

Rationing loops across a corpus and evolving the process per round: [edge-seeking iterations](references/edge-seeking.md).
