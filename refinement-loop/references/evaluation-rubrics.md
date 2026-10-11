# Evaluation Rubrics

## Table of contents

- Score-first design
- Dimension design
- Evidence rule
- Threshold calibration

## Score-first design

One overall 0–10 score plus 3–6 named dimensions. Each dimension gets a one-line description of what passing looks like, not a paragraph. Granular dimensions beat a single holistic score: they tell the reviser where to spend the next round. The AI Search pattern (0–10, stop at 8) works because the threshold is public before generation starts — set it in the brief, never after seeing v0.

## Dimension design

Name dimensions after failure shapes, not virtues. "No uncited claims" beats "accuracy". "Each section actionable in isolation" beats "clarity". Derive dimensions from the artifact's purpose: a plan is scored on executability, a prompt on independence (runs without the author present), a design on tradeoffs named. Cap at six; beyond that critics spread attention thin and scores go noisy.

## Evidence rule

The critic must quote the offending span before scoring the dimension down. No quote, no deduction. This separates rubric bugs from work bugs: if the critic cannot find a span for a low score, the rubric is wrong, not the work. G-Eval style reasoning-first output (`reasoning`, then `score`, strict shape) makes this auditable and lets later rounds diff what actually improved.

## Threshold calibration

Defaults transfer badly. Calibrate on 3–5 samples of known quality (one clearly passing, one clearly failing, rest mixed) and set the stop threshold where the critic's scores split them. For automated gates, hold out 10–20 human-labeled examples and re-check the threshold whenever the rubric changes. Until calibrated, treat the first loop as calibration, not production.
