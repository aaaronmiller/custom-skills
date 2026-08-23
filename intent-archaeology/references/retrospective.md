# Retrospective (progressive disclosure)

> **⚠️ DO NOT LOAD UNTIL COMPLETION.**
> This file is loaded only by `10_post_completion_audit.py`. Loading
> it earlier biases the run toward producing findings that make the
> retrospective look good. This is the progressive-disclosure mechanism
> the user asked for.

## Question zero: does the run still serve the anchor?

Before any metric question, answer this against a file the loop cannot
modify (the SKILL.md anchor). A self-improving system needs a fixed
point that isn't part of what it improves.

If the answer is "no", stop. The drift is the finding; everything else
is downstream of it.

The signature of drift in the artifact: growth without restructuring.
62KB to 111KB across four revisions with the organizing structure
never changing. If the current run's artifact grew but the structure
didn't change, that's the drift signal.

## The question list

Run these in order. Each produces an observation appended to the
tranche's `observations` table. Observations are append-only during
the tranche with zero effect on the run. Edits to the skill are
proposed only at boundaries, accepted only if they improve the held-out
score **without regressing any component of the metric vector**.

### Q1: Did the scope produce useful coverage?

- Did the scope miss sessions you expected to find?
- Did the scope include sessions that were noise?
- Was the time range right? Too narrow? Too wide?
- Was the project list right? Missing projects? Extra projects?

If scope was wrong, propose a `scope_selectors.md` clarification, not
a code change. The scope system is correct; the documentation might
not be.

### Q2: Did Phase 6 produce complete per-turn coverage?

- Every prompt ID come back with a verdict (including `noise`)?
- Any missing IDs? (Error, not empty result.)
- Any `noise` verdicts that should have been a real type?
- Any real types that should have been `noise`?

If per-turn coverage failed, the batch size was too large OR the
prompt was unclear. Propose a prompt-level edit first. Merge-logic
edits require three consecutive tranches of no prompt-level gain.

### Q3: Did Phase 7's status vector match reality?

- Spot-check 5 projects. Does the vector feel right?
- Any `drifted` that should be `completed`? (Threshold too low.)
- Any `completed` that should be `drifted`? (Threshold too high.)
- Any `abandoned` that should be `not_begun`? (Cut evidence
  misinterpreted.)

If the threshold is wrong, propose a calibration re-run, not a code
change. The threshold is data-driven.

### Q4: Did the meta-learning loop hack its own reward?

- Did any accepted edit improve one metric component at the cost of
  another?
- Did the held-out score rise while wiki quality (as judged by
  reading it) declined?
- Did the loop propose merge-logic edits before three consecutive
  tranches of no prompt-level gain?

If yes to any, revert the edit and tighten the acceptance criterion.
The ICLR 2026 finding (73.8% / 46.8% of optimizations showed proxy
gains with no held-out real-task gain) is the cautionary tale.

### Q5: Did the proposer and verifier stay separate?

- Were Phase 6 and Phase 7 run by different processes?
- Ideally, different models?
- Any signs of inherited blind spots (status vector too clean)?

If not, the audit is suspect. Re-run with separation.

### Q6: Did the wiki avoid the markdown graveyard?

- Did `lint_wiki.py` catch any human edits inside generated fences?
- Did humans edit the wiki at all? (If not, the wiki isn't useful
  enough.)
- Did the generator overwrite any human edits? (Should be impossible
  if linting works.)

If humans aren't editing, the wiki isn't useful. Propose a
usefulness improvement, not a generation change.

### Q7: Did the scope persist correctly?

- Each tranche's scope_hash unique?
- Re-runs with the same scope_hash produce the same results?
- Re-runs with different scope_hash don't clobber each other?

If not, the scope persistence is broken. Code fix required (rare;
this is stable infrastructure).

### Q8: What did the user actually use?

- Which wiki pages did the user open (if telemetry available)?
- Which status vectors did the sleep-time agent act on?
- Which `abandoned` items did the user override?

This is the real signal. The skill serves the user; if the user isn't
using it, the skill isn't working, regardless of metric values.

## How to propose edits

For each observation that warrants a skill change:

1. Write the proposed edit as a diff against the current skill files.
2. Run the held-out eval (see `references/eval_protocol.md`) on the
   edited skill.
3. Accept only if:
   - Held-out score improves, AND
   - No component of the metric vector regresses, AND
   - The edit is prompt-level (not merge-logic) unless three
     consecutive tranches showed no prompt-level gain.
4. Write the accepted edit to `proposed_edits/<tranche_id>/<n>.diff`
   for human review.
5. Bump the skill version (patch for fix, minor for new section,
   major for spine change).

## Two timescales

- **Observe continuously, change discretely.** Observations append
  during the tranche with zero effect. Edits proposed only at
  boundaries.
- **Prompt-level first, merge-logic untouchable.** Prompt-level edits
  any tranche. Merge-logic edits only after three tranches of no
  prompt-level gain.

The two-timescale rule is what prevents the meta-learning loop from
wrecking the run. An ICLR 2026 paper documents rise-then-collapse
inside a single campaign, with the worked example being an agent that
found a 6% target-metric gain while invisibly costing 4% diversity and
1% hard-case accuracy, because it only tracked the target.

## Explicit editable surface

Every edit is a file in git. Every edit is a readable diff. The
permission boundary is enforced by the script layer, not by an
instruction in a prompt. This is what makes the loop safe to leave
running during sleep-time compute.
