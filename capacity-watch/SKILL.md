---
name: capacity-watch
description: Read the remaining quota of every paid and free model pool, grade the free and contributor models we can reach, project each pool to its reset, schedule the open masterplan work on AI-era estimates, and refine the method itself twice a day. Use when asked how much quota is left, where the next agent should run, which free models are good enough, when the masterplan lands, or whether an estimate is realistic.
metadata:
  version: "1.0.0"
  tags: "quota, capacity, scheduling, estimation, free-models, masterplan, cron"
---

# capacity-watch

Answers four questions with evidence, every 4 hours:

1. How much is left in each pool, and will it run out or go to waste before it resets?
2. Which free, contributor and stealth models can do capable work today?
3. Does the queued work fit the headroom, and when does each item land?
4. Are the estimates realistic for agents, or pre-AI timelines in disguise?

Twice a day a judgment agent reviews the method itself and refits its priors.

## Pools and how each is read

All four paid pools are read from the provider's own usage endpoint with `quota-probe.py --active` (verified 2026-11-06). Each token goes only to its issuer and is never refreshed by the probe.

| Pool | Plan | Reading | Windows |
|---|---|---|---|
| claude | Anthropic subscription | GET api.anthropic.com/api/oauth/usage | five_hour (when open), seven_day |
| codex | ChatGPT Plus | GET chatgpt.com/backend-api/wham/usage | 5-hour, weekly |
| agy | Google AI Pro (Antigravity) | POST cloudcode-pa v1internal:fetchAvailableModels (internal) | per model, with reset time |
| opencode-go | OpenCode Go | GET opencode.ai/zen/go/v1/usage (undocumented) | rolling 5-hour, weekly, monthly |
| openrouter | key, free tier | GET openrouter.ai/api/v1/key | 1,000 free requests a day |
| opencode-zen, kilo | free | local request and error counts only | concurrency, not a window |

Known limits, 2026-11-06:
- **agy:** the internal endpoint answered a manual test and then refused the probe (403). The probe falls back to agy's logs: activity counts and quota errors. The operator decides whether the probe may present itself as the agy client (see the method page).
- **opencode-go:** the key in OpenCode's auth store has expired (401 `api_key_expired`). The probe uses `OPENCODE_GO_API_KEY` from the environment, which is current.
- **Free lanes** stall silently instead of returning 429. Concurrency is capped at 3, and the throughput figures live in calibration.json.

## Files

- `scripts/quota-probe.py`: readings, one JSON line per pool. `--active` for the endpoints, `--record FILE` to keep history. Extended from masterplan research/mesh-results/quota-router/quota-probe.py (2026-11-05, passive only).
- `scripts/free-catalog.py --out DIR`: every zero-cost and contributor model across OpenCode Zen, OpenCode Go, OpenRouter, Kilo and the providers Kilo lists, graded against the quality floor (the lowest ARDF score among the approved free lanes). Tiers: capable, unscored (trial first), below-floor (never for Living Documents or intent work). It also marks data-sharing tiers, which are wanted, and routes with no credential on this machine.
- `scripts/assess.py`: projects each pool to its reset (pace 1.0x is even burn), compares queued demand with headroom using calibration priors, and schedules the workload on two tracks. It writes `~/LIVING_DOCUMENTS/projects/masterplan/capacity-status.md`.
- `calibration.default.json`: the first priors and the measured anchors A1 to A5. The live copy is `~/.local/state/capacity-watch/calibration.json`, owned by the meta-review.
- `references/estimation-rules.md`: how every estimate is built and checked. Agent-hours only, four named reasons for long waits, and the ten-times rule.
- `references/meta-review.md`: the twice-daily review of the method.

## Ledger

`scripts/ledger.py` keeps one row per model call in `~/.local/state/capacity-watch/ledger.sqlite` (override with `CAPACITY_LEDGER`). It reads the logs harnesses already write, never calls an API, opens every source read-only and stores no prompt text.

- `ingest [--since ISO] [--host NAME]`: idempotent backfill keyed on (harness, session_id, message_id). Adapters: Claude Code JSONL (including subagent transcripts), Codex rollouts (with the rate-limit snapshot per row), omp sessions, opencode.db, and `calls-direct.jsonl`. Each adapter reports its counters and, when it finds nothing, why.
- `report [--days N] [--by provider|model|harness|day]`: calls, disjoint token buckets, list cost and allowance. Missing costs stay null.
- `reconcile --pool codex|opencode-go|claude [--days N] [--expect WINDOW=N]`: tokens per window-percent from Codex snapshots or `readings.jsonl`, per window instance, both uncached (input plus output plus cache writes) and all-bucket. The 10% gate passes against `--expect`, or when at least two instances of 5 points or more agree with the pooled ratio.

Phase 0 result, 2026-11-07: rows from four harnesses; the Codex gate fails because tokens per point vary about 15x across windows, most likely by model. Details and raw output: `references/ledger-phase0-2026-11-07.md`. Tests: `python3 -I -m pytest -q tests`.

## Phase 3

`python3 -I scripts/weights.py` fits Codex quota weights by model and window, one shared Claude weight per window, and Go allowance weights. It writes `~/.local/state/capacity-watch/weights.json` with sample counts, fit errors and identifiability. Go limits come from `references/opencode-go-limits.json`. Inputs are local and read-only; no model calls occur.

`python3 -I scripts/which_model.py <task-class> --json` ranks catalog and active subscription routes using success probability, quota scarcity and time. Add `--private` to require non-sharing Anthropic or OpenAI endpoints. Quality and observed 429 rates are hard filters. Bulk JSON validity comes from completed Go lane trials; other task success probabilities start from explicitly labeled ARDF Beta priors. Scores use fractions of the binding quota window, and all windows must have headroom. Results describe the latest assessment, not live availability, and do not dispatch work.

Run `python3 -I -m pytest -q tests` for offline synthetic checks. The Phase 3 receipt, complete command outputs, units, prior assumptions and remaining fit limitations are in `references/phase3-2026-11-07.md`. Model fitting does not by itself pass the failed Phase 0 reconciliation gate. No installation or cron integration is included.

## The workload block

The masterplan dossier's `timeline.md` holds one fenced block opened with ```` ```json capacity-workload ````. Each task row has `id`, `title`, `status`, `remaining_agent_hours`, `lanes`, `pools` (shares of the task's agent-hours, keyed by pool name), `basis`, and optionally `wall_hours`, `after`, `not_before`, `blocked_on`, `observation` (a soak window that occupies no work track), `decomposed`, `actual_agent_hours` and `actual_wall_hours`. Coordinator sessions edit it; the cron jobs only read it.

## Cadence (guardian cron, `capacity-watch.sh`)

- **Hourly at :05**, `probe`: active readings appended to `readings.jsonl`. The free catalog refreshes once a day at the 00:05 run.
- **Every 4 hours at :15** (00:15, 04:15, 08:15, 12:15, 16:15, 20:15 Pacific), `assess`: a fresh probe, the status page, then a Sonnet judgment agent writes a routing and slippage report to `~/.local/state/capacity-watch/reports/`. Four hours divides the day and the week, and the hourly probe catches 5-hour resets as they come.
- **07:40 and 19:40**, `meta`: an Opus agent reviews the method (`references/meta-review.md`), may refit `calibration.json`, and proposes any other change as an exact edit. The wrapper then commits `capacity-status.md` to Living Documents.

## Rules

- Readings never contain a credential. Run `grep -ciE 'sk-ant|bearer|access_token|ya29' readings.jsonl`; it must print 0.
- Data-sharing models get redacted text only, never credentials or private exports.
- No low-tier models. The catalog's floor is the gate, and unscored models are trialed before use.
- The cron agents read and report. Only the meta-review writes, and only `calibration.json` plus its own report.

## Quota Ledger dashboard (MP-14)

Live page: https://claude.ai/artifact/PMkHYC6L33VxiVfeQSJEqi (a Dashboard-type artifact; the Overdrive Night Ledger links to it). Data comes from `scripts/dashboard-data.py`, which writes six CSVs to `~/.local/state/capacity-watch/dashboard/`: quota_history, projections, usage_daily, forecast_hours, lane_trial and tasks. Task excerpts are redacted; the other datasets hold counts and percentages. The page source is `dashboard/index.html` in this skill.

Refresh (any Claude session with the Artifact tools, after `assess` and a ledger `ingest`):
1. `python3 -I scripts/dashboard-data.py`
2. Upload each changed CSV to the artifact as an asset (Artifact publish with `url`, `asset: true`, one CSV per call).
3. For each dataset, ArtifactData `update` of `datasets/<id>` with the new `source.url`, `updated: {at, by}` and `edit`, pinned with `if_version`.
4. Hourly quota targets: write `~/.local/state/capacity-watch/hour-<date>/scores.json` (hour_start, pool, window, baseline_pct, target_delta, actual_delta, note) before step 1.

The 4-hourly cron agent cannot reach the Artifact tools, so the cron refreshes the CSVs and a coordinator session uploads them. Datasets are marked stale after 6 hours.

## Task ledger

`scripts/task-ledger.py` reads the local `tasks/remote-*.json` summaries, mesh telemetry snapshots, Workflow journals and their adjacent agent transcripts, dispatch `c*.md` briefs and `c*.log` console logs, and Codex calls in `ledger.sqlite`. It matches task IDs against the masterplan task list. It makes no network or model calls.

It writes `~/.local/state/capacity-watch/dashboard/tasks.csv` and one full redacted run page per task plus `index.md` under `/home/cheta/LIVING_DOCUMENTS/projects/masterplan/runs/`. Unchanged pages are not rewritten. The dashboard's Tasks completed section filters and sorts all outcomes and expands each task with metrics, excerpts and its copyable run-page path. Missing evidence stays unknown. Costs are list-price equivalents; subscription rows do not imply an extra charge. Codex console token totals are separate from output tokens. Finished sessions with no exit or result record are marked unknown, because call records do not establish task completion.

To refresh source snapshots, run `scripts/job-summary-remote.py` on each worker over its configured mesh SSH route, saving stdout locally to `~/.local/state/capacity-watch/tasks/remote-<host>.json`. Then run `python3 -I scripts/dashboard-data.py`. That command writes all six datasets, including tasks.csv. Upload/register the tasks dataset with the Dashboard Artifact through the existing coordinator refresh procedure when publication is authorized. Local refresh does not publish the artifact.

Every CSV must be below 256,000 bytes. An oversized task export fails before writing run pages or replacing tasks.csv rather than silently dropping tasks. Full briefs and available result text remain in Living Documents. The remote summary collector limits result text to 4,000 characters and output names to 60; the dashboard shows the first 20 output names. Workflow completion means all launched agents returned, not independent acceptance of their work. Timing derived from telemetry observation or log modification is marked approximate in the run page.

## Bundled resources

Load or run these when the step they name comes up.

- `scripts/lane-trial.py`: Trial unscored free lanes with `scripts/lane-trial.py` before using them for Living Documents or intent work.
