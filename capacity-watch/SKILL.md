---
name: capacity-watch
version: 1.0.0
description: Read the remaining quota of every paid and free model pool, grade the free and contributor models we can reach, project each pool to its reset, schedule the open masterplan work on AI-era estimates, and refine the method itself twice a day. Use when asked how much quota is left, where the next agent should run, which free models are good enough, when the masterplan lands, or whether an estimate is realistic.
tags: [quota, capacity, scheduling, estimation, free-models, masterplan, cron]
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

Live page: https://claude.ai/artifact/PMkHYC6L33VxiVfeQSJEqi (a Dashboard-type artifact; the Overdrive Night Ledger links to it). Data comes from `scripts/dashboard-data.py`, which writes five CSVs to `~/.local/state/capacity-watch/dashboard/`: quota_history, projections, usage_daily, forecast_hours and lane_trial. They hold counts and percentages only. The page source is `dashboard/index.html` in this skill.

Refresh (any Claude session with the Artifact tools, after `assess` and a ledger `ingest`):
1. `python3 -I scripts/dashboard-data.py`
2. Upload each changed CSV to the artifact as an asset (Artifact publish with `url`, `asset: true`, one CSV per call).
3. For each dataset, ArtifactData `update` of `datasets/<id>` with the new `source.url`, `updated: {at, by}` and `edit`, pinned with `if_version`.
4. Hourly quota targets: write `~/.local/state/capacity-watch/hour-<date>/scores.json` (hour_start, pool, window, baseline_pct, target_delta, actual_delta, note) before step 1.

The 4-hourly cron agent cannot reach the Artifact tools, so the cron refreshes the CSVs and a coordinator session uploads them. Datasets are marked stale after 6 hours.
