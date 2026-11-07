---
title: Twice-daily meta-review of the capacity method
version: 1.0.0
updated: 2026-11-06
---

# Twice-daily meta-review

The capacity method is young. Its numbers, its equations and its process are all hypotheses. Twice a day (07:40 and 19:40 Pacific) a judgment agent reviews the method itself, not only its outputs.

## Inputs

- `~/.local/state/capacity-watch/readings.jsonl`: every quota reading.
- `~/.local/state/capacity-watch/assessments.jsonl`: every assessment summary.
- `~/.local/state/capacity-watch/calibration.json`: the live priors and anchors.
- `~/LIVING_DOCUMENTS/projects/masterplan/timeline.md`: the workload block, with any recorded actuals.
- `~/LIVING_DOCUMENTS/projects/masterplan/capacity-status.md`: the latest generated page.
- The 4-hourly assessment reports in `~/.local/state/capacity-watch/reports/`.
- This skill's `references/estimation-rules.md`.

## Questions, every run

1. **Predictions against outcomes.** For each pool, compare the projection made 4, 8 and 12 hours ago with what the readings now show. Where was the error largest, and why?
2. **Priors.** Do the readings and the agent-hours actually run fit `per_agent_hour`? Refit any prior with at least two clean observations, and record the basis.
3. **Estimates.** For tasks finished since the last review, compute actual / estimated. Name any bias and change the anchor or the rule that produced it.
4. **Pre-AI timelines.** Did any estimate on the timeline survive that a capable agent would beat by ten times or more? Rewrite it.
5. **Waste.** Did a pool reset with more than 40% unused while work was queued? Name what should have run there.
6. **The process.** Is any part of the method producing noise, being ignored, or missing a signal (for example a provider whose reading keeps failing)? Propose the change.

## What the reviewer may change

- It may edit `calibration.json` (priors, anchors, throughput) and write its own report.
- It must not edit scripts, the crontab or the skill text. Changes to those go in the report under "Proposed changes", worded as exact edits, for the coordinator session to apply.
- It records every change it made with the before and after values.
