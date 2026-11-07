---
title: Estimation rules for agent-built work
version: 1.0.0
updated: 2026-11-06
owner: capacity-watch meta-review (twice daily)
---

# Estimation rules for agent-built work

Operator direction, 2026-11-06 21:18 PT: AI-built work is routinely estimated with pre-AI timelines ("four to five weeks" for something a capable agent finishes in four to five hours). Every estimate in the timeline must be built from what agents actually do now, and obviously invalid timelines are rejected, not softened.

## The unit

- Estimate in **agent-hours**: one capable agent working for one wall-clock hour, including its tool and test time.
- Convert to **wall hours** with the lanes the task can really use: wall = agent-hours / lanes, but only for work that splits. A serial chain stays serial.
- Days, weeks, months and sprints are not estimate units. The assessment flags them on sight (`pre-AI units`).

## What legitimately takes long

Only these four reasons may stretch a task past its agent-hours. Name the one that applies in `blocked_on` or `not_before`:

1. **An operator action**: a decision, a `sudo` line, a login, a purchase. Estimate the operator's minutes separately and give the earliest time they are likely available.
2. **An observation window** that the acceptance test itself requires, for example a 48-hour soak or 7 days unattended. This is not work time, and agent work continues on other tasks during it.
3. **Quota or throttling**: a pool exhausted until its reset, or free lanes throttled. Use the reset time from capacity-status, not a guess.
4. **Compute or external wait**: a long build, an index, a provider's batch, a third party.

Anything else is agent time.

## How to build an estimate

1. Find the nearest anchor in `calibration.json` (`anchors`: measured wall hours for finished work) and scale by size, not by gut feel.
2. A single task estimated above **8 agent-hours** must be split into parts, each with its own acceptance test, or carry `decomposed: true` with the reason it cannot be.
3. Every task row carries `basis`: the anchor id and the scaling, or "measured" with the evidence.
4. State confidence: `measured`, `anchored` or `guess`. A guess is fine; an unlabelled guess is not.

## The sanity check (run on every estimate)

- **Pre-AI smell test.** If a human team would quote the same number, ask what the agent would actually be doing for all that time. If the answer is "waiting for itself", the estimate is wrong.
- **Ten-times rule.** If an estimate is more than ten times the nearest anchor for work of similar size, it is rejected and rebuilt.
- **Bottleneck named.** If the wall time is more than twice the agent time, one of the four reasons above must be named.

## Closing the loop

- When a task finishes, record `actual_agent_hours` and `actual_wall_hours` in its workload row before moving it to done.
- The meta-review computes the error ratio (actual / estimated) per task and per kind of work, and moves the anchors and priors toward the measurements.
- A persistent bias (estimates consistently 2x high or 2x low over three or more tasks) changes the rule or the anchor, not just the next number.
