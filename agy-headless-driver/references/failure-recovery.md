# Failure recovery

## Contents
1. 429 RESOURCE_EXHAUSTED
2. Unit cut off mid-step
3. Interactive shell aliases hang the worker
4. Low disk
5. Headless auth failure
6. Worker wrote outside its roots
7. Verify step fails
8. Session ran but produced nothing
9. Post-mortem from the brain directory

## 1. 429 RESOURCE_EXHAUSTED

Parse `Resets in XhYmZs` from the error. Ignore `retryable`.

| Reset duration | Meaning | Action |
|---|---|---|
| up to about 5h15m | Worth waiting for: the short window, or a weekly lock near the end of its cycle | Sleep until reset plus 2 to 5 minutes of jitter, relaunch the same unit; its resume protocol continues from the checkpoint |
| longer, or no parseable reset | Weekly baseline for that pool | Park all units on that pool. Keep running units on the other pool. Report the unlock time (now plus reset). Do not retry. |

Before relaunching after a short reset, confirm the unit prompt has a resume protocol and that the pack, not a full preload, is the only whole-file read. A relaunch that re-ingests 190k tokens can drain the remaining weekly balance in minutes.

If the operator needs certainty about the weekly balance before a relaunch, check `/usage` interactively; that call is cheap.

## 2. Unit cut off mid-step

1. Do not hand-edit the tree blindly. Compare the tree against the previous unit's snapshot (`diff -ru`).
2. Edits that appear in the partial record with their vote and evidence: keep.
3. Edits not recorded: save the diff to `aborted-<unit>-attempt<N>.diff`, roll them back, and list them in the next attempt's pack as candidate proposals to re-probe and re-vote, never to apply unexamined.
4. Relaunch the unit; its resume protocol picks up the partial record.

## 3. Interactive shell aliases hang the worker

Symptom: the session stalls with no output after a `cp`, `mv` or `rm`. Cause: aliases such as `cp -i` waiting for a yes on a closed stdin.
Fix in the prompt's `<shell_notes>`: use `command cp -f`, `command mv -f`, `command rm -f`, or file-edit tools. Fix in the driver: launch with `< /dev/null` and a wall-clock guard so a hang ends rather than blocking the campaign.

## 4. Low disk

Snapshots and logs accumulate. Snapshot only the governed tree; compress older snapshots; rotate stream-json logs. State the free-space figure in `<shell_notes>` so the worker avoids large copies.

## 5. Headless auth failure

`authentication required` means no cached interactive credentials on this machine or user. Run `agy` interactively once and sign in. For Gemini-only workers, `modelProvider: "gemini"` plus `GEMINI_API_KEY` is an alternative on 1.1.13 and later.

## 6. Worker wrote outside its roots

Detect with a driver-side check after each unit: list files modified since launch under the forbidden roots (`find <root> -newer <launch-stamp> -type f`). If any, stop the campaign and report. Tighten `<writable_roots>` and `<forbidden>`, and consider `/permissions` rules or a hook that rejects writes outside the roots.

## 7. Verify step fails

The worker must fix the cause in the deliverable, never weaken the validator. If a unit ends without a marker because verify failed repeatedly, the driver records the unit as failed with the last verify output; the operator decides. Do not auto-retry a failing verify more than once; repeated identical failures waste a window.

## 8. Session ran but produced nothing

Check, in order: stdin redirect present; model id valid (an unknown id can fail fast with a terse error); prompt file path expanded correctly; stream-json log for an early error event; disk full.

## 9. Post-mortem from the brain directory

`~/.gemini/antigravity-cli/brain/<session-uuid>/transcript_full.jsonl` holds every step. To find where quota went:
- Locate the step where cumulative context first exceeds about 60% of the window.
- Count steps that were whole-file reads versus line-range reads.
- Find tool outputs over about 8 KB (they were candidates for `tail` or `grep`).
Feed the findings into the next pack and prompt.
