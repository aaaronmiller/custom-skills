# Evaluation Protocol

> **When to read:** before publishing any benchmark claim, or when
> Phase 7's `drifted` threshold needs calibration.

## Why eval matters

The single largest gap between this skill and a field contribution is
that TLR reports precision/recall/F1 against shared datasets, and this
skill has no numbers yet. Closing that gap is the cheapest path to
S-tier.

## The labeled set

Build a labeled set for one project, end to end:

1. Pick one project (era 3 or 4 — era 5 is too easy, era 1 is too
   hard).
2. Hand-label every intent in the session corpus with:
   - Type (from `references/intent_taxonomy.md`)
   - Supersession links (if superseded)
   - Status ground truth (`completed`, `in_progress`, `drifted`,
     `superseded`, `abandoned`, `not_begun`)
3. Record the labels in `labeled_intents` table (separate from the
   machine-produced `intents` table).
4. This is the gold standard. `[GAP-14]`

## Metrics

For intent extraction (Phase 6):
- **Turn-level recall:** by construction 100% (cass `is_human` filter
  cannot miss what matches). Not interesting.
- **Intent-level recall:** intents found / intents in gold standard.
  This is the real extraction metric.
- **Intent-level precision:** correct intents / intents produced.
- **Per-turn coverage:** every submitted ID comes back with a verdict,
  including `noise`. Missing ID is an error.

For supersession detection (Phase 6, the hard part):
- **Supersession-detection rate:** correct supersession links / gold
  supersession links. This is where extraction stays accurate long
  after cross-item reasoning starts slipping — measure this, not
  extraction rate, to set batch size.

For three-way join (Phase 7):
- **Status vector accuracy:** per-component precision/recall against
  gold standard.
- **`drifted` detection F1:** the hardest component. Threshold
  calibration lives here.

For meta-learning (Phase 9):
- **Held-out score:** metric vector accuracy on a held-out tranche.
- **No-regression check:** no component of the metric vector may
  regress when accepting an edit.

## The calibration procedure

1. Run Phase 6 on the labeled project with batch size N.
2. Measure intent-level recall and supersession-detection rate.
3. Increase N until supersession-detection rate drops by 5% from its
   peak.
4. That N is the batch size for production runs.
5. Re-run calibration every 3 tranches or when the underlying model
   changes.

This follows the ATLAS methodological point: measure the degradation
curve on the actual corpus rather than trusting any published number
including those in `references/prior_art.md`.

## What to publish

When the user decides to publish (this is a research decision, not a
tool decision):

1. The labeled set (if privacy permits — `[GAP-11]`).
2. The metric definitions (this file).
3. The metric values on the labeled set.
4. The batch-size calibration curve.
5. Comparison to one baseline (LiSSA or UserTrace, applied to the
   same corpus if possible — `[GAP-08]`).

That's a paper. The thesis is in `references/research_position.md`.

## What NOT to publish

- A single accuracy percentage. Use the per-component vector.
- "Should work" claims. Only "did work, here are the numbers."
- Comparisons to systems that don't share a corpus. `[GAP-12]`
- Inferred numbers for any `[GAP-NN]`. State the gap, leave it absent.
