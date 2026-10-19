# Case study: the spec-prep refinement lockout (October 2026)

A worked example of how a well-intended Opus campaign triggered a 162-hour lock, and how the same campaign runs under this skill.

## What was asked
Refiner 2 of 3 on a spec-prep plan: run refinement passes 6 to 10, each a V(10,3,1) council with a real probe in every gap, apply adopted changes, regenerate evals, append ledger entries, run the validator, snapshot. Model: `claude-opus-5-5-high` via `agy -p ... --dangerously-skip-permissions --print-timeout 0 < /dev/null`.

## What happened
1. The prompt ordered "Read these first, completely" across the brief, protocol, two skills with all their references, the full plan tree, five prior pass records (5k to 7k words each) and several dossiers. By the time pass 6 began, about 192k tokens were resident: the 200k window was effectively full.
2. All five passes were assigned to that one session. Every probe, round, edit and validator run re-processed a near-full window.
3. First 429 at 01:04:52 with `Resets in 4h33m58s` (short window).
4. The driver slept to 05:45:00 and relaunched the same prompt. The relaunch re-ingested the same ~192k before doing new work.
5. Second 429 at 05:47:11 with `Resets in 162h51m37s`: the weekly baseline. Two minutes of re-ingest drained what the week had left.
6. The interrupted attempt had applied four spec edits without recording them; they had to be rolled back by hand and preserved as a diff.

## What the prompt did right
Disk-persisted pass records, per-pass snapshots, explicit writable roots, grep-only access to the two largest corpus pages, alias workaround for `cp/mv/rm`, a validator gate that may not be weakened, and treating aborted edits as proposals to re-vote. Keep all of these.

## What caused the lock
- Whole-file preload of everything (residency).
- Five units in one session (turns times residency).
- Relaunch without a resume path and without classifying the 429 (weekly drain).
- No calibration of what one pass costs (no pacing).

What did NOT cause it: the depth of the council, the length of the pass records, or the effort level. Cutting those would have produced worse plans and only a small saving.

## The same campaign under this skill

1. Gemini Pro unit (Gemini pool): read the brief, protocol, skills, plan tree, five pass records and dossiers; emit `pack-pass06.md` (under 40k tokens) with verbatim protocol and adoption rule, decision tables for passes 1 to 5 with path:line evidence, a file index with anchors, and the aborted diff's four edits listed as candidates.
2. Gemini Flash unit: pre-flight (paths exist, disk headroom, validator runs green on the current tree, previous snapshot present).
3. Calibration: run pass 6 as an Opus unit with the template; read `/usage` before and after; record the delta.
4. Opus unit per pass (6, 7, 8, 9, 10), each a fresh session reading only its pack whole and probing by line range. Each ends verify, snapshot, ledger, marker. Full V(10,3,1), full records.
5. Between Opus units, a Gemini unit merges the finished pass's decision table into the next pack. These run concurrently with the next Opus pass where the dependency allows.
6. Driver classifies any 429: short window sleeps and resumes the same pass from its checkpoint; weekly parks remaining Opus passes, still lets Gemini units finish, and reports the unlock time.
7. Optional: a Gemini Pro red-team unit reviews pass 10's result against the brief.

Expected effect: the same five passes at the same depth and effort, with per-pass residency starting near 30k instead of 192k, and at most one pass of rework exposed to any quota event.
