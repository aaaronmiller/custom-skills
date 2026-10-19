---
name: agy-headless-driver
description: Plan, prompt, launch and supervise headless Antigravity CLI (agy -p) sessions so Claude Opus, Claude Sonnet, Gemini Pro and Gemini Flash deliver maximum-quality work inside Google's 5-hour and weekly quota windows and the 200k Claude context ceiling. Use this skill whenever you are about to delegate work to agy, write a prompt for an agy headless run, build or fix a driver script that calls agy, split a long task (multi-pass refinement, deliberative councils, spec work, large refactors, research synthesis) across agy sessions, recover from an agy RESOURCE_EXHAUSTED / 429 error, or decide which agy model pool should carry which part of a job, even if the user only says "run this in Antigravity", "hand it to agy" or "use the Google quota".
license: MIT
metadata:
  author: ice-ninja
  version: "1.3.0"
---

# agy headless driver

You are the orchestrator. agy is a worker you launch with `agy -p`. Your job is to get exceptional output from it at full reasoning effort without tripping Google's quota locks. The operator chose the model, the effort level and the amount of iteration for a reason; keep all three. What you control is how the work is packaged.

## The one idea that governs everything

agy meters agent work, not prompts. In an agent loop the biggest piece of work is the model re-processing its resident context on every turn. So the cost of a session is roughly:

```
session cost  ~=  sum over turns of (resident context at that turn)  +  thinking  +  output
```

A session that reads 190k tokens up front and then makes 150 tool calls processes on the order of 28M token-equivalents before it writes anything clever. The identical deliberation run from a 30k context pack in a fresh session per unit processes a small fraction of that, with the same model, the same effort and the same number of rounds.

Therefore: **spend quota on thinking and writing, not on re-reading.** Shrink residency and session length; never shrink effort, iteration or depth.

This also matches Anthropic's own guidance for long-horizon work: make incremental progress, keep state in files, and let a fresh context window rebuild state from disk rather than dragging a bloated one forward.

## Hard facts about the harness

Read `references/agy-system-model.md` for evidence and unknowns. The short version:

| Fact | Consequence |
|---|---|
| Two windows per pool: a 5-hour rolling window and a strict weekly baseline for premium models | A 429 whose reset is over about 5 hours is the weekly lock. Sleeping does not help. |
| Gemini models and Claude/GPT models draw from separate pools | Gemini work never costs Claude quota. Route accordingly. |
| Claude context in agy: plan for 200k | Keep peak residency near 60% (about 120k tokens, about 480 KB of text). |
| Gemini Pro context: about 1M | Gemini Pro is the corpus reader and pack builder. |
| 429 bodies say `retryable: true` even for weekly locks | Classify by the `Resets in` duration, never by the flag. |
| Headless flags: `-p`, `--model`, `--dangerously-skip-permissions`, `--output-format text/json/stream-json`, `--mode` | Always `< /dev/null`, always log stream-json, always run under the driver. |

Rule of thumb for sizing without arithmetic: **4 KB of English text is about 1k tokens.** 200k window is about 800 KB. Run `scripts/budget.py <files>` instead of guessing.

## Workflow

Follow these phases in order. Each exists because skipping it caused a real lockout (see `references/case-study-spec-prep-lockout.md`).

### Phase 1: Decompose into units of judgment

A unit is the largest piece of work that needs one continuous mind: one refinement pass, one council deliberation, one feature implementation, one review. Not a whole five-pass campaign.

- One unit per agy session. Fresh context per unit; continuity lives on disk.
- A unit must end in a verifiable state: validator green, files written, marker created.
- If a unit cannot finish below the residency target, split it at a natural seam (per lens, per module, per section), not at an arbitrary token count.

Details and sizing tables: `references/session-design.md`.

### Phase 2: Build the context pack

Before any Claude session, produce a context pack: one file the worker reads whole, containing exactly what it needs to start reasoning, plus a map of where everything else lives.

- Target size: under 40k tokens (about 160 KB). Check with `scripts/budget.py`.
- Contents: the brief verbatim, the governing protocol, the current state summary (ledger tail, standing decisions), prior-unit outcomes as decision tables (not full transcripts), and a file index with one line per file and its key line ranges.
- Build every pack with a Gemini Pro unit using `assets/pack-builder-template.md`: separate pool, about 1M window, strong at long-document distillation. It labels requirements VERBATIM, history SUMMARY, and cites `path:start-end` for every summary row, so the Claude unit verifies any claim it acts on with one line-range read. Between units, the next pack build absorbs the finished unit's decision table.
- Never paste prior pass records whole into a pack. Summarize decisions, keep pointers.

### Phase 3: Write the prompt from the template

Use `assets/prompt-template.md` (a fully filled real example is `assets/example-spec-prep-pass06.md`). It is an XML sandwich: an operating contract up front, the inputs and procedure in the middle, and a completion contract at the end that restates the constraints a long session tends to forget. Fill every tag; delete none. Keep the operator's requirements verbatim inside `<operator_requirements>`.

Key elements the template enforces:

- **Read discipline**: read the pack whole once; read everything else by `grep -n` or line range; never re-read a file you just wrote.
- **Write discipline**: write deliberation records in full, one write per round or section, appending to disk as you go so an interruption loses at most one round.
- **Checkpoint protocol**: the unit's last steps are validate, snapshot, ledger, done-marker, in that order.
- **Resume protocol**: on start, check for done-markers and partial records; continue from the first incomplete step instead of restarting.
- **Environment block**: aliases, writable roots, forbidden paths, disk limits.
- **Depth guard**: an explicit instruction not to stop early for budget reasons; the record on disk plus resume carries the work.

### Phase 4: Launch through the driver

Run every unit through `scripts/agy-run.sh` (or a driver with the same behavior). It:

1. Skips units whose done-marker exists.
2. Launches `agy -p` with `< /dev/null`, `--output-format stream-json`, `--print-timeout 0`, the chosen model id, and a generous wall-clock guard. It refuses prompts over 120 KB (Linux argv limit), so reference the pack by path.
3. On a 429 (an `AGY_ERROR` line near the end of the log, and no done-marker), parses `Resets in`. A reset of up to 5h15m is worth waiting for (usually the short window, occasionally a weekly lock near the end of its cycle), so it sleeps until reset plus jitter and relaunches the same unit, which resumes from its checkpoint. Anything longer, or unparseable, is the weekly lock: it parks every unit in that pool, keeps running units in the other pool, and exits 75 with a status report.
4. After each unit, runs the unit's verify command and refuses to mark done unless it passes.
5. Holds back any unit whose `requires` list is not done (a pack is never built from an unfinished pass), and holds a lock so overlapping launches cannot run one campaign twice.

Never relaunch a heavy unit right after a short-window reset without the resume protocol in its prompt. That exact move converted a 4.5-hour wait into a 162-hour lock.

### Phase 5: Pace the weekly budget

The weekly cap, not the 5-hour window, is the binding constraint for Opus campaigns.

- Before a multi-unit Claude campaign, run one representative unit as a calibration unit. Read `/usage` in an interactive `agy` before and after and record the delta per pool in `calibration.md` next to the plan (schema in `assets/campaign-kit.md`).
- Plan the campaign as units per window and units per week from that measured delta. Spread units across 5-hour windows so no single window drains the weekly balance.
- Put the highest-value judgment units first so a surprise lock still leaves the best work done.

More in `references/session-design.md` (pacing section).

### Phase 6: Verify and hand back

After the campaign, check outputs against the source: run validators, diff snapshots between units, spot-check that adopted changes cite real probes. Report per unit: status, verify result, notable decisions, quota events.

## Model profiles

Pick the model the operator asked for. These profiles say how to get the most from each, not when to substitute one for another. Full detail: `references/claude-models.md`, `references/gemini-models.md`.

**Claude Opus (e.g. `claude-opus-5-5-high`)**: the deepest judgment in the harness and the most quota-weighted. Give it the hardest reasoning with the leanest residency: context pack, one unit per session, full council and full probe schedule, records written to disk round by round. Let thinking run; trim reading.

**Claude Sonnet**: strong agentic executor with long tool-call stamina. Ideal for implementation units with many edits and test runs. Same residency rules; its sessions tend to be turn-heavy, so line-range reads and quiet commands (`--quiet`, `| tail -n 40`, `2>&1 | grep -E 'FAIL|ERROR'`) matter even more.

**Gemini Pro**: 1M window on a separate pool. Best use: whole-corpus reading, context-pack building, cross-file mapping, and an independent red-team seat whose different training gives genuine model diversity to an adversarial review.

**Gemini Flash**: fast, high-throughput, separate pool. Best use: mechanical work where judgment is not the product: running validators across many files, format conformance sweeps, inventorying a tree, extracting line-range indexes for a pack.

A campaign that uses all four puts every model on the work it is best at and lets the two pools run in parallel.

## Deliberative councils inside agy

V(X,Y,S) councils (for example V(10,3,1)) run well in agy when each pass is its own unit. Keep every seat, every round and every probe. Write each round to the pass record as it completes. The probe between rounds is a real command, file read or search; its output goes into the record as a trimmed excerpt with the command that produced it. See `references/deliberation-in-agy.md`.

## When something goes wrong

Read `references/failure-recovery.md`. Covers: weekly vs short-window 429, a unit cut off mid-pass, interactive `cp/mv/rm` aliases that hang headless shells, low disk, auth expiry in headless mode, a worker that wanders outside its writable root, and a validator that fails after edits.

## Files in this skill

| Path | Read when |
|---|---|
| `assets/prompt-template.md` | Writing any agy prompt (always) |
| `assets/pack-builder-template.md` | Writing the Gemini Pro pack-building unit |
| `assets/campaign-kit.md` | Writing `units.tsv`, `calibration.md`, `models.local.md` |
| `assets/example-spec-prep-pass06.md` | You want a fully filled, real-world prompt to model yours on |
| `references/agy-system-model.md` | You need evidence for a quota claim or hit an unknown |
| `references/session-design.md` | Sizing units, building packs, pacing a campaign |
| `references/claude-models.md` | Running Opus or Sonnet units |
| `references/gemini-models.md` | Running Gemini Pro or Flash units |
| `references/deliberation-in-agy.md` | Running council-style passes |
| `references/failure-recovery.md` | Any error, lockout or interrupted unit |
| `references/case-study-spec-prep-lockout.md` | You want the worked example of what not to do |
| `scripts/agy-run.sh` | Launching units (always) |
| `scripts/budget.py` | Sizing a pack or a read list |
