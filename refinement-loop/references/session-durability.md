# Session Durability (`S:durable`)

## Table of contents

- Scratchpad
- Gated phases
- Constitution
- When to downgrade

## Scratchpad

Long loops lose state to compaction and drift. Keep one append-only scratchpad the loop owns: current version pointer, last verdict with scores, ranked fix list with done flags, open questions, and decisions taken with reasons. Append; never rewrite history. The critic reads the scratchpad before each verdict so standards cannot silently slide between rounds.

## Gated phases

Split the work into phases where each phase ends in a scored gate: brief → plan → draft → verify → ship, or per-department in pipeline work. A phase's output must pass its gate (threshold set up front) before the next phase spends budget on top of it. Failed gate means revise within the phase, not proceed-and-fix-later. This is what makes department pipelines composable: every handoff arrives already judged.

## Constitution

Five or fewer standing rules, enforced every round, referenced by number ("C3: no placeholders"). Typical set: evidence-before-score, cap-is-sacred, brief-beats-taste, invalidate-on-new-data, rollback-on-regression. When a new instruction conflicts with the constitution, the constitution wins and the conflict is surfaced, not silently absorbed. This is the mechanism that keeps hundred-turn sessions coherent.

## When to downgrade

Durability costs tokens every round. Drop to `scratchpad` when the loop fits in one context window with room to spare, and to `none` for three rounds or fewer on a single artifact. Upgrade mid-loop the first time a verdict contradicts an earlier one from forgotten context.
