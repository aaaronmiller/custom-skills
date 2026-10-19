# Session design: units, packs, residency and pacing

## Contents
1. The residency-times-turns model
2. Sizing a unit
3. Building a context pack
4. Read and write patterns inside a session
5. Checkpoints and resume
6. Pacing a campaign across windows
7. Parallelism across pools

## 1. The residency-times-turns model

Treat each agy session as a loop where every turn re-processes everything resident. Cost grows with both how much is loaded and how many turns run. Two consequences:

- Loading 150k tokens at the start of a session taxes every later turn, including turns that never needed that material.
- A session that runs five units back to back carries the residue of units 1 to 4 into unit 5. Fresh sessions per unit cut cost and also improve reasoning quality, because the model is not wading through stale probe output.

Quick comparison (illustrative arithmetic, same model and effort):

| Design | Start residency | Turns | Approx tokens processed |
|---|---|---|---|
| One session, five passes, full preload | 190k growing to 200k | 600 | about 115M |
| Five sessions, 30k pack each, targeted reads | 30k growing to about 90k | 120 each | about 7M each, 36M total |

The second design keeps every seat, round and probe. It just stops paying to carry what it is not using.

## 2. Sizing a unit

A unit is right-sized when all four hold:
- It needs one continuous line of reasoning (splitting it would lose coherence).
- It ends in a verifiable state (validator, tests, marker).
- Its peak residency stays near 120k tokens for Claude (about 480 KB of text loaded across the session, pack included).
- A lost session costs at most one unit of rework.

Split seams, best first: per lens or pass; per module or file group; per document section; per question in a research set. Do not split a single council round across sessions.

Rough turn budgets to plan with (not limits):

| Unit type | Typical turns | Notes |
|---|---|---|
| Deliberative pass V(10,3,1) with 4 probes and edits | 40 to 90 | Most turns are probes and edits; deliberation is written in large blocks |
| Implementation unit with tests | 60 to 150 | Sonnet excels here; quiet test output is essential |
| Pack build over a large corpus (Gemini Pro) | 20 to 60 | High residency is fine on the 1M pool |
| Mechanical sweep (Gemini Flash) | 10 to 80 | Many short commands |

## 3. Building a context pack

The pack is the only file a Claude worker reads whole. Structure:

```
# Context pack: {{campaign}} / {{unit}}
## 1. Brief (operator request, verbatim)
## 2. Protocol (the rules this unit follows, verbatim or tightly excerpted)
## 3. Current state (ledger tail, standing decisions, open items)
## 4. Prior unit outcomes (decision tables: change | vote | evidence path:line | status)
## 5. File index (path | purpose | key anchors or line ranges | size KB)
## 6. Known hazards (environment traps, forbidden paths, validator quirks)
```

Rules:
- Verbatim where the wording carries requirements (brief, protocol, adoption rules). Summarized where it only carries history (prior pass transcripts become decision tables).
- Every summary line points to a source path and line range, so the worker can verify instead of trusting.
- Target under 40k tokens. Run `python3 scripts/budget.py pack.md` and fix anything over.
- Rebuild the pack between units with a Gemini Pro unit (`assets/pack-builder-template.md`): unit N's decision table becomes a new row block in section 4.
- When a Gemini Pro session builds the pack from a big corpus, its prompt should demand path:line citations for every claim, and the Claude unit should spot-check at least the claims it acts on.

## 4. Read and write patterns inside a session

Reads:
- `grep -n 'anchor' file` to locate, then `sed -n '120,180p' file` to read.
- `wc -c` before opening anything unfamiliar; above about 40 KB, read by range only.
- Command output through `tail -n 40`, `head -n 60`, or a focused `grep`. Test runners in quiet mode.
- Do not re-read a file you wrote this session.

Writes:
- Full-quality content, written to disk as it is produced: a council round, a spec section, a module.
- Prefer targeted edits (string replacement, patch) over regenerating whole files; regeneration costs output and risks silent loss.
- Records append; do not rewrite the record each round.

## 5. Checkpoints and resume

Order at the end of every unit: verify, snapshot, ledger, done-marker. The marker is last so its existence proves the other three happened.

Resume rules a worker follows on start (the template encodes them):
1. Marker present: stop immediately.
2. Partial record present: continue from the first incomplete step. Re-verify any tree edits the record claims against the previous unit's snapshot; roll back edits that are not recorded with their vote.
3. Neither: start fresh.

Snapshots should be small: copy only the plan tree and eval files, not the whole workspace. On a tight disk, snapshot as a `tar.gz` and keep the last three.

## 6. Pacing a campaign across windows

1. Calibrate: run one representative unit, read `/usage` before and after, record the delta per pool in `calibration.md`.
2. Compute units per window = floor(short-window headroom / unit delta) and units per week = floor(weekly headroom / unit delta). Use the smaller constraint.
3. Schedule: at most units-per-window units per 5-hour window, and no more than units-per-week across the cycle. Leave one unit of weekly headroom for a rerun.
4. Order units by value: the units whose output matters most go first.
5. Re-measure after the first three units; deltas drift with corpus size and turn count.
6. If the weekly reset anchor is known, start large campaigns just after it so the full week is available.

## 7. Parallelism across pools

The Gemini and Claude pools are independent, so run them concurrently:
- While Opus runs pass N, Gemini Pro builds the pack for pass N+1 from pass N-1's record (pass N's decisions get merged when it lands).
- Gemini Flash runs validators, inventories and index extraction for upcoming units.
- An independent Gemini Pro red-team review of a finished Claude unit adds real model diversity to adversarial checking at zero Claude cost.

Within one pool, parallel sessions (or agy background subagents) draw from the same balance and multiply drain. Use them only for genuinely independent units with their own markers.
