# Critic Patterns

## Table of contents

- Separate critic (AI Search pattern)
- Hostile persona
- Rejection loop
- Reflexion memory
- Bias controls

## Separate critic (AI Search pattern)

Builder builds v1. A different agent examines the work from multiple angles, scores 0–10 with a ranked fix list. Threshold stops the loop (8 in the demo; 8.5 for the game build); the round cap (3, or 4) ships the final round regardless. The demo's key line: without the critic the model stops at the mediocre first result. Use when quality matters more than speed; cost is roughly one extra builder-sized call per round.

## Hostile persona

Same model, separate turn, adversarial role: "as a skeptical CTO list the 3 fatal flaws, then rewrite fixing only those." Persona shift forces re-evaluation that polite self-review never reaches. Two to three iterations maximum before returns flatten. Cheap and effective for drafts.

## Rejection loop

Define bad first: list the cliches, buzzwords, and generic moves that are banned, then draft, flag violations, rewrite. Negative constraints are mechanically checkable, which makes them stick across rounds where positive guidance ("be insightful") evaporates.

## Reflexion memory

Keep an episodic lesson log across trials: each failure writes one line ("failed because X"), injected into the next round's brief. Stops repeated errors in long or repeated tasks (code repair, reasoning benchmarks). One line per lesson; prune lines that stop firing.

## Bias controls

For anything scored: reasoning before score, strict output shape, low temperature on the judge (0–0.2), pairwise A/B with order swapped when comparing variants, and a different model family for the judge when the decision is expensive. These neutralize position, verbosity, and self-preference bias per current LLM-as-judge practice.
