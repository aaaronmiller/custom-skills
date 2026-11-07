---
title: Ledger phase 0 run, 2026-11-07
date: 2026-11-07
plan: /home/cheta/LIVING_DOCUMENTS/projects/masterplan/model-economics-plan-2026-11-07.md
phase: 0
gate: rows from at least 3 harnesses (pass); token sums reconcile with provider window deltas within 10% (fail for Codex, unverified for opencode-go and claude)
---

# Ledger phase 0 run, 2026-11-07

Run on SPECTRE-16 at about 08:09 PT on 2026-11-07. Ledger: `/home/cheta/.local/state/capacity-watch/ledger.sqlite` (13 MB, 35,954 rows after the backfill).

## Result

- **Rows from at least 3 harnesses: pass.** Four harnesses wrote rows: omp 29,203, claude 5,449, codex 1,153, direct-api 149. opencode wrote none (see below).
- **Re-ingest is idempotent.** A second identical `ingest --since 2026-10-24` inserted 0 rows in every adapter. A third run after a code change inserted only calls made in the minutes between runs (2 claude, 2 direct-api).
- **Reconcile within 10%: fail for Codex.** The 5-hour window instances over 7 days range from 2,244 to 32,575 uncached tokens per window percent, so no single tokens-per-percent figure predicts the window within 10%. The opencode-go and claude pools have only two probe readings each in `readings.jsonl`, so they cannot be reconciled yet.

## What each adapter found

| Adapter | Source | Files read | Records | Rows | Notes |
|---|---|---|---|---|---|
| claude | `~/.claude/projects/*/*.jsonl` plus `*/*/subagents/**/*.jsonl` | 281 of 391 (110 older than the cutoff) | 11,267 usage records | 5,449 | Streaming fragments share `message.id` and are merged (largest counter wins), not added. 145 subagent transcripts sit below the session directory and were added to the glob; the brief's one-level glob missed them. Proxied models are recorded as served: muse-spark-1.3-contributor, thinkingmachines/inkling:free (route free). Native Anthropic rows keep route `unknown` because the log carries no billing evidence. |
| codex | `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl` | 26 of 184 | 1,153 calls | 1,153 | Per-call usage from `token_count.info.last_token_usage`; 17 repeated events (same cumulative total) skipped; 80 snapshot-only events (no usage) skipped. Every row stores its `rate_limits` snapshot (primary, secondary, plan_type, limit_id). Rollouts also carry `token_usage_record` events with a `response_id`; they duplicate the same usage and are not read. |
| omp | `~/.omp/agent/sessions/*/*.jsonl` | 7 of 160 | 29,203 assistant messages | 29,203 | Exact field names, from real files: `message.usage.{input, output, cacheRead, cacheWrite, reasoningTokens, cost.total}`, `message.{provider, model, responseId, duration, stopReason, errorStatus}`. 2,687 rows carry HTTP 429 in `errorStatus` and are now recorded as outcome `429` rather than `error`. Cost is OMP's catalog estimate, not a bill. |
| opencode | `~/.local/share/opencode/opencode.db` (read-only) | 1 | 0 | **0** | Schema matches (`message.data` JSON with `tokens.{input, output, reasoning, cache.read, cache.write}`, `cost`, `modelID`, `providerID`). Zero rows because the newest message is from 2026-08-20T20:35Z, before the 2026-10-24 cutoff. OpenCode has not been used as an interactive harness since then; Go calls now arrive through omp and the direct log. |
| direct-api | `~/.local/state/capacity-watch/calls-direct.jsonl` | 1 | 149 | 149 | `usage.opencode` carries billing_source, list_cost, allowance and tokens. Models with zero allowance (crouton-alpha-free, beam-free, iceman-contributor-free) route as free; the rest of the `go` billing rows route as subscription. |

## The 2026-11-07 Codex anchor

Measured by the operator: three Codex high-effort jobs, 07:42 to 08:05 PT (15:42 to 16:05 UTC), used about 446k tokens and moved Codex from 0 to 100% of its 5-hour window and from 37% to 54% of its week.

The ledger holds those calls: 52 calls in 3 sessions between 15:42:47Z and 15:49:12Z, all gpt-6-astra.

| Measure | Tokens |
|---|---|
| uncached input plus output (plus cache writes, which were 0) | **446,393** |
| cache reads | 5,247,616 |
| all buckets | 5,694,009 |

The operator's 446k is exactly the uncached measure, so reconcile reports that measure as its headline ratio and also reports the all-bucket ratio. Because the anchor and the ledger read the same token logs, this check tests the percent side only; it is not an independent token count.

Anchor ratios: 5-hour 446,000 / 100 = 4,460 tokens per point; weekly 446,000 / 17 = 26,235 tokens per point. The ledger's own instance for that window (baseline call excluded, last observation 99% at 15:48:50Z) gives 417,234 / 99 = **4,214**, 5.5% under the anchor. The 7-day pooled ratios miss the anchor by +21.5% (5-hour) and -29.3% (weekly).

Two defects in the earlier reconcile were found on this window and fixed:

1. **Stale snapshots.** Three concurrent sessions write rate-limit snapshots out of order (for example 88%, then 40%, then 94%). The old code moved its baseline down on every decrease and counted the same percent again, so one 0 to 99 window could sum to well over 100 points. Within one fixed Codex window, usage can only rise, so a lower value is now ignored without moving the baseline (11 skipped in the 5-hour series, 6 in the weekly).
2. **Reset jitter.** The first snapshot of the window reported a reset 7 seconds earlier than the rest, which split one window into two and dropped its first points. Resets within 15 minutes of each other are now one window instance.

## Why the Codex gate fails, and what phase 3 needs

Per 5-hour instance, uncached tokens per point (from the reconcile output below):

| Instance start (UTC) | Points | Uncached tokens per point | Models |
|---|---|---|---|
| 2026-11-01 00:25 | 5 | 3,947 | gpt-6.1-sol |
| 2026-11-01 06:35 | 26 | 4,533 | gpt-6.1-sol |
| 2026-11-02 05:35 | 16 | 10,048 | gpt-6.1-sol, gpt-6.1-terra |
| 2026-11-02 21:45 | 6 | 32,575 | gpt-6.1-sol, gpt-6.1-terra |
| 2026-11-02 21:53 | 7 | 5,265 | gpt-6.1-sol |
| 2026-11-03 21:48 | 89 | 2,244 | gpt-6.1-sol |
| 2026-11-04 10:49 | 31 | 15,866 | gpt-6.1-sol, gpt-6.1-terra |
| 2026-11-05 05:38 | 97 | 5,981 | gpt-6-astra, gpt-6.1-terra |
| 2026-11-07 11:30 | 89 | 3,368 | gpt-6-astra |
| 2026-11-07 15:42 | 99 | 4,214 | gpt-6-astra |

Inferred, not verified: the instances that include gpt-6.1-terra spend far more tokens per point, so the quota likely weights models differently. An ad hoc least-squares fit on these ten instances with one weight per token kind (uncached input, cache reads, output) still misses by up to 7x on single instances, so token kind alone does not explain it. The low ratio on 2026-11-03 (89 points from about 200k tokens) could also mean Codex usage from somewhere this host does not log (another machine or Codex cloud tasks). Phase 3 needs per-model quota weights, and the reconcile should be rerun once there are several single-model windows per model. Effort level is in `turn_context.effort` and is not yet stored.

## Commands and raw output

```
python3 -I -m pytest -q tests        # 29 passed
python3 -I scripts/ledger.py ingest --since 2026-10-24
python3 -I scripts/ledger.py report --days 14 --by model
python3 -I scripts/ledger.py reconcile --pool codex --days 7
python3 -I scripts/ledger.py reconcile --pool codex --days 7 --expect primary:300=4460 --expect secondary:10080=26235
python3 -I scripts/ledger.py reconcile --pool opencode-go --days 7
python3 -I scripts/ledger.py reconcile --pool claude --days 7
```

### ingest --since 2026-10-24 (first run)

```json
{
  "adapters": {
    "claude": {
      "accepted_records": 11267,
      "candidate_rows": 11267,
      "files_before_since": 110,
      "files_found": 391,
      "files_read": 281,
      "inserted_rows": 5449
    },
    "codex": {
      "accepted_records": 1153,
      "candidate_rows": 1153,
      "files_before_since": 158,
      "files_found": 184,
      "files_read": 26,
      "inserted_rows": 1153,
      "repeated_usage_events": 17,
      "snapshot_only_events": 80
    },
    "direct-api": {
      "accepted_records": 149,
      "candidate_rows": 149,
      "files_found": 1,
      "files_read": 1,
      "inserted_rows": 149
    },
    "omp": {
      "accepted_records": 29203,
      "candidate_rows": 29203,
      "files_before_since": 153,
      "files_found": 160,
      "files_read": 7,
      "inserted_rows": 29203
    },
    "opencode": {
      "files_found": 1,
      "files_read": 1,
      "inserted_rows": 0,
      "zero_rows_reason": "no eligible assistant usage in the requested time range; see counters"
    }
  },
  "host": "SPECTRE-16",
  "rows_by_harness": {
    "claude": 5449,
    "codex": 1153,
    "direct-api": 149,
    "omp": 29203
  },
  "since": "2026-10-24T00:00:00.000000Z",
  "total_rows": 35954
}
```

### ingest, second and third runs (inserted rows per adapter, opencode detail)

```json
{
  "second_run_inserted": {
    "claude": 0,
    "codex": 0,
    "direct-api": 0,
    "omp": 0,
    "opencode": 0
  },
  "third_run_inserted": {
    "claude": 2,
    "codex": 0,
    "direct-api": 2,
    "omp": 0,
    "opencode": 0
  },
  "third_run_opencode": {
    "files_found": 1,
    "files_read": 1,
    "inserted_rows": 0,
    "newest_source_ts": "2026-08-20T20:35:12.297000Z",
    "zero_rows_reason": "newest source record (2026-08-20T20:35:12.297000Z) predates --since"
  }
}
```

### report --days 14 --by model

Token buckets are disjoint: `tokens_total` is input plus output plus cache read plus cache write; reasoning is inside output and also shown alone. Cost and allowance are null where the source has none. Rows with zero tokens are failed or stalled calls.

```json
{
  "by": "model",
  "rows": [
    {
      "allowance_known_calls": 0,
      "allowance_usd": null,
      "calls": 9,
      "cost_known_calls": 0,
      "list_cost_usd": null,
      "model": "<synthetic>",
      "tokens_cache_read": 0,
      "tokens_cache_write": 0,
      "tokens_in": 0,
      "tokens_out": 0,
      "tokens_reasoning": 0,
      "tokens_total": 0,
      "usage_known_calls": 9
    },
    {
      "allowance_known_calls": 19,
      "allowance_usd": 0.0,
      "calls": 19,
      "cost_known_calls": 19,
      "list_cost_usd": 0.0,
      "model": "beam-free",
      "tokens_cache_read": 48576,
      "tokens_cache_write": 0,
      "tokens_in": 133067,
      "tokens_out": 214951,
      "tokens_reasoning": 167184,
      "tokens_total": 396594,
      "usage_known_calls": 19
    },
    {
      "allowance_known_calls": 0,
      "allowance_usd": null,
      "calls": 54,
      "cost_known_calls": 0,
      "list_cost_usd": null,
      "model": "claude-fable-5-1",
      "tokens_cache_read": 7828705,
      "tokens_cache_write": 1028828,
      "tokens_in": 1613,
      "tokens_out": 224325,
      "tokens_reasoning": 0,
      "tokens_total": 9083471,
      "usage_known_calls": 54
    },
    {
      "allowance_known_calls": 0,
      "allowance_usd": null,
      "calls": 59,
      "cost_known_calls": 0,
      "list_cost_usd": null,
      "model": "claude-haiku-5-5",
      "tokens_cache_read": 5755715,
      "tokens_cache_write": 492749,
      "tokens_in": 118,
      "tokens_out": 120440,
      "tokens_reasoning": 0,
      "tokens_total": 6369022,
      "usage_known_calls": 59
    },
    {
      "allowance_known_calls": 0,
      "allowance_usd": null,
      "calls": 4418,
      "cost_known_calls": 0,
      "list_cost_usd": null,
      "model": "claude-opus-5-5",
      "tokens_cache_read": 1025628760,
      "tokens_cache_write": 25269774,
      "tokens_in": 8864,
      "tokens_out": 5216140,
      "tokens_reasoning": 0,
      "tokens_total": 1056123538,
      "usage_known_calls": 4418
    },
    {
      "allowance_known_calls": 0,
      "allowance_usd": null,
      "calls": 574,
      "cost_known_calls": 0,
      "list_cost_usd": null,
      "model": "claude-sonnet-5-5",
      "tokens_cache_read": 65264439,
      "tokens_cache_write": 3386265,
      "tokens_in": 1151,
      "tokens_out": 588157,
      "tokens_reasoning": 0,
      "tokens_total": 69240012,
      "usage_known_calls": 574
    },
    {
      "allowance_known_calls": 49,
      "allowance_usd": 0.0,
      "calls": 49,
      "cost_known_calls": 49,
      "list_cost_usd": 0.0,
      "model": "crouton-alpha-free",
      "tokens_cache_read": 0,
      "tokens_cache_write": 0,
      "tokens_in": 444207,
      "tokens_out": 80634,
      "tokens_reasoning": 0,
      "tokens_total": 524841,
      "usage_known_calls": 49
    },
    {
      "allowance_known_calls": 17,
      "allowance_usd": 0.06884565,
      "calls": 19,
      "cost_known_calls": 17,
      "list_cost_usd": 0.11474275,
      "model": "deepseek-v4.1-flash",
      "tokens_cache_read": 9984,
      "tokens_cache_write": 0,
      "tokens_in": 156264,
      "tokens_out": 152122,
      "tokens_reasoning": 128576,
      "tokens_total": 318370,
      "usage_known_calls": 17
    },
    {
      "allowance_known_calls": 0,
      "allowance_usd": null,
      "calls": 2608,
      "cost_known_calls": 2608,
      "list_cost_usd": 0.0,
      "model": "deepseek-v4.1-flash-free",
      "tokens_cache_read": 0,
      "tokens_cache_write": 0,
      "tokens_in": 0,
      "tokens_out": 0,
      "tokens_reasoning": 0,
      "tokens_total": 0,
      "usage_known_calls": 2608
    },
    {
      "allowance_known_calls": 18,
      "allowance_usd": 1.1190714,
      "calls": 18,
      "cost_known_calls": 18,
      "list_cost_usd": 0.5595357,
      "model": "gemini-4-argon",
      "tokens_cache_read": 7737,
      "tokens_cache_write": 0,
      "tokens_in": 151756,
      "tokens_out": 25525,
      "tokens_reasoning": 0,
      "tokens_total": 185018,
      "usage_known_calls": 18
    },
    {
      "allowance_known_calls": 0,
      "allowance_usd": null,
      "calls": 119,
      "cost_known_calls": 0,
      "list_cost_usd": null,
      "model": "gpt-6-astra",
      "tokens_cache_read": 13349504,
      "tokens_cache_write": 0,
      "tokens_in": 893011,
      "tokens_out": 67620,
      "tokens_reasoning": 9894,
      "tokens_total": 14310135,
      "usage_known_calls": 119
    },
    {
      "allowance_known_calls": 0,
      "allowance_usd": null,
      "calls": 7,
      "cost_known_calls": 0,
      "list_cost_usd": null,
      "model": "gpt-6-luna",
      "tokens_cache_read": 615808,
      "tokens_cache_write": 0,
      "tokens_in": 100007,
      "tokens_out": 1059,
      "tokens_reasoning": 190,
      "tokens_total": 716874,
      "usage_known_calls": 7
    },
    {
      "allowance_known_calls": 0,
      "allowance_usd": null,
      "calls": 806,
      "cost_known_calls": 0,
      "list_cost_usd": null,
      "model": "gpt-6.1-sol",
      "tokens_cache_read": 163310208,
      "tokens_cache_write": 0,
      "tokens_in": 5511556,
      "tokens_out": 691826,
      "tokens_reasoning": 281459,
      "tokens_total": 169513590,
      "usage_known_calls": 806
    },
    {
      "allowance_known_calls": 0,
      "allowance_usd": null,
      "calls": 221,
      "cost_known_calls": 0,
      "list_cost_usd": null,
      "model": "gpt-6.1-terra",
      "tokens_cache_read": 54112128,
      "tokens_cache_write": 0,
      "tokens_in": 1010652,
      "tokens_out": 96766,
      "tokens_reasoning": 25619,
      "tokens_total": 55219546,
      "usage_known_calls": 221
    },
    {
      "allowance_known_calls": 0,
      "allowance_usd": null,
      "calls": 3,
      "cost_known_calls": 3,
      "list_cost_usd": 0.0,
      "model": "groq/compound-mini",
      "tokens_cache_read": 0,
      "tokens_cache_write": 0,
      "tokens_in": 0,
      "tokens_out": 0,
      "tokens_reasoning": 0,
      "tokens_total": 0,
      "usage_known_calls": 3
    },
    {
      "allowance_known_calls": 19,
      "allowance_usd": 0.0,
      "calls": 19,
      "cost_known_calls": 19,
      "list_cost_usd": 0.0,
      "model": "iceman-contributor-free",
      "tokens_cache_read": 40964,
      "tokens_cache_write": 0,
      "tokens_in": 135941,
      "tokens_out": 72216,
      "tokens_reasoning": 21157,
      "tokens_total": 249121,
      "usage_known_calls": 19
    },
    {
      "allowance_known_calls": 0,
      "allowance_usd": null,
      "calls": 565,
      "cost_known_calls": 565,
      "list_cost_usd": 0.0,
      "model": "inclusionai/ling-3.0-flash-fin:free",
      "tokens_cache_read": 0,
      "tokens_cache_write": 0,
      "tokens_in": 0,
      "tokens_out": 0,
      "tokens_reasoning": 0,
      "tokens_total": 0,
      "usage_known_calls": 565
    },
    {
      "allowance_known_calls": 0,
      "allowance_usd": null,
      "calls": 3,
      "cost_known_calls": 3,
      "list_cost_usd": 0.0,
      "model": "mimo-v2.6-flash-free",
      "tokens_cache_read": 0,
      "tokens_cache_write": 0,
      "tokens_in": 0,
      "tokens_out": 0,
      "tokens_reasoning": 0,
      "tokens_total": 0,
      "usage_known_calls": 3
    },
    {
      "allowance_known_calls": 27,
      "allowance_usd": 0.0902801,
      "calls": 23103,
      "cost_known_calls": 22856,
      "list_cost_usd": 25.440439094000002,
      "model": "muse-spark-1.3-contributor",
      "tokens_cache_read": 11119681497,
      "tokens_cache_write": 0,
      "tokens_in": 22636125,
      "tokens_out": 4687318,
      "tokens_reasoning": 1107678,
      "tokens_total": 11147004940,
      "usage_known_calls": 23103
    },
    {
      "allowance_known_calls": 0,
      "allowance_usd": null,
      "calls": 172,
      "cost_known_calls": 172,
      "list_cost_usd": 0.0,
      "model": "qwen/qwen3.8-27b:free",
      "tokens_cache_read": 0,
      "tokens_cache_write": 0,
      "tokens_in": 0,
      "tokens_out": 0,
      "tokens_reasoning": 0,
      "tokens_total": 0,
      "usage_known_calls": 172
    },
    {
      "allowance_known_calls": 0,
      "allowance_usd": null,
      "calls": 828,
      "cost_known_calls": 828,
      "list_cost_usd": 0.0,
      "model": "stealth/space-bunny-alpha",
      "tokens_cache_read": 0,
      "tokens_cache_write": 0,
      "tokens_in": 0,
      "tokens_out": 0,
      "tokens_reasoning": 0,
      "tokens_total": 0,
      "usage_known_calls": 828
    },
    {
      "allowance_known_calls": 0,
      "allowance_usd": null,
      "calls": 352,
      "cost_known_calls": 309,
      "list_cost_usd": 0.0,
      "model": "thinkingmachines/inkling:free",
      "tokens_cache_read": 50002048,
      "tokens_cache_write": 0,
      "tokens_in": 3413098,
      "tokens_out": 54810,
      "tokens_reasoning": 25575,
      "tokens_total": 53469956,
      "usage_known_calls": 352
    },
    {
      "allowance_known_calls": 0,
      "allowance_usd": null,
      "calls": 1853,
      "cost_known_calls": 1853,
      "list_cost_usd": 0.0,
      "model": "z-ai/glm-5.2",
      "tokens_cache_read": 0,
      "tokens_cache_write": 0,
      "tokens_in": 0,
      "tokens_out": 0,
      "tokens_reasoning": 0,
      "tokens_total": 0,
      "usage_known_calls": 1853
    }
  ],
  "since": "2026-10-24T16:09:12.101542Z"
}
```

### reconcile --pool codex --days 7

```json
{
  "candidate_calls": 455,
  "candidate_tokens_all": 94997187,
  "candidate_tokens_uncached": 3467331,
  "gate_within_10_percent": "fail",
  "limits": "Local calls only; account-wide quota may include other hosts or cloud tasks. Provider percents are integers, so small deltas are rounding noise. Stale (out-of-order) Codex snapshots and resets are excluded. Claude billing is inferred from native Anthropic model ids.",
  "pool": "codex",
  "since": "2026-10-31T16:09:12.206812Z",
  "status": "measured",
  "windows": [
    {
      "all_tokens_per_percent": 197168.135,
      "decreases_skipped": 11,
      "gate": {
        "basis": "agreement of 10 window instances with the pooled ratio",
        "max_relative_deviation": 5.0126,
        "verdict": "fail"
      },
      "instances": [
        {
          "first": "2026-11-01T00:25:32.430000Z",
          "last": "2026-11-01T00:27:31.957000Z",
          "percent_delta": 5.0,
          "resets_at": "2026-11-01T05:25:16.000000Z",
          "tokens_all": 1171478,
          "tokens_uncached": 19734,
          "uncached_tokens_per_percent": 3946.8
        },
        {
          "first": "2026-11-01T06:35:22.550000Z",
          "last": "2026-11-01T07:21:32.549000Z",
          "percent_delta": 26.0,
          "resets_at": "2026-11-01T11:35:13.000000Z",
          "tokens_all": 8144346,
          "tokens_uncached": 117850,
          "uncached_tokens_per_percent": 4532.692
        },
        {
          "first": "2026-11-02T05:35:43.973000Z",
          "last": "2026-11-02T06:20:54.612000Z",
          "percent_delta": 16.0,
          "resets_at": "2026-11-02T10:35:37.000000Z",
          "tokens_all": 5239165,
          "tokens_uncached": 160765,
          "uncached_tokens_per_percent": 10047.812
        },
        {
          "first": "2026-11-02T21:45:16.306000Z",
          "last": "2026-11-02T21:50:59.336000Z",
          "percent_delta": 6.0,
          "resets_at": "2026-11-02T21:52:12.000000Z",
          "tokens_all": 2383612,
          "tokens_uncached": 195452,
          "uncached_tokens_per_percent": 32575.333
        },
        {
          "first": "2026-11-02T21:53:25.041000Z",
          "last": "2026-11-02T22:02:48.491000Z",
          "percent_delta": 7.0,
          "resets_at": "2026-11-03T02:52:15.000000Z",
          "tokens_all": 2250102,
          "tokens_uncached": 36854,
          "uncached_tokens_per_percent": 5264.857
        },
        {
          "first": "2026-11-03T21:48:31.356000Z",
          "last": "2026-11-03T21:56:53.932000Z",
          "percent_delta": 89.0,
          "resets_at": "2026-11-04T02:48:21.000000Z",
          "tokens_all": 4620922,
          "tokens_uncached": 199674,
          "uncached_tokens_per_percent": 2243.528
        },
        {
          "first": "2026-11-04T10:49:00.059000Z",
          "last": "2026-11-04T11:03:49.867000Z",
          "percent_delta": 31.0,
          "resets_at": "2026-11-04T11:13:23.000000Z",
          "tokens_all": 23771841,
          "tokens_uncached": 491841,
          "uncached_tokens_per_percent": 15865.839
        },
        {
          "first": "2026-11-05T05:38:33.352000Z",
          "last": "2026-11-05T06:39:40.559000Z",
          "percent_delta": 97.0,
          "resets_at": "2026-11-05T10:38:20.000000Z",
          "tokens_all": 33693234,
          "tokens_uncached": 580146,
          "uncached_tokens_per_percent": 5980.887
        },
        {
          "first": "2026-11-07T11:30:39.697000Z",
          "last": "2026-11-07T11:43:18.433000Z",
          "percent_delta": 89.0,
          "resets_at": "2026-11-07T15:37:05.000000Z",
          "tokens_all": 4925777,
          "tokens_uncached": 299729,
          "uncached_tokens_per_percent": 3367.742
        },
        {
          "first": "2026-11-07T15:42:47.969000Z",
          "last": "2026-11-07T15:48:50.948000Z",
          "percent_delta": 99.0,
          "resets_at": "2026-11-07T20:42:38.000000Z",
          "tokens_all": 5482706,
          "tokens_uncached": 417234,
          "uncached_tokens_per_percent": 4214.485
        }
      ],
      "no_token_samples": 0,
      "observations": 454,
      "percent_delta": 465.0,
      "samples": 245,
      "saturated_samples": 0,
      "tokens_all": 91683183,
      "tokens_uncached": 2519279,
      "uncached_tokens_per_percent": 5417.804,
      "window": "primary",
      "window_minutes": 300
    },
    {
      "all_tokens_per_percent": 596095.462,
      "decreases_skipped": 6,
      "gate": {
        "basis": "agreement of 3 window instances with the pooled ratio",
        "max_relative_deviation": 0.9151,
        "verdict": "fail"
      },
      "instances": [
        {
          "first": "2026-11-01T00:25:32.430000Z",
          "last": "2026-11-01T07:21:32.549000Z",
          "percent_delta": 6.0,
          "resets_at": "2026-11-04T06:42:40.000000Z",
          "tokens_all": 9467747,
          "tokens_uncached": 138467,
          "uncached_tokens_per_percent": 23077.833
        },
        {
          "first": "2026-11-02T05:35:43.973000Z",
          "last": "2026-11-03T21:56:53.932000Z",
          "percent_delta": 99.0,
          "resets_at": "2026-11-09T05:35:37.000000Z",
          "tokens_all": 16285726,
          "tokens_uncached": 909726,
          "uncached_tokens_per_percent": 9189.152
        },
        {
          "first": "2026-11-04T10:49:00.059000Z",
          "last": "2026-11-07T15:48:47.823000Z",
          "percent_delta": 53.0,
          "resets_at": "2026-11-11T10:48:46.000000Z",
          "tokens_all": 68429610,
          "tokens_uncached": 1882922,
          "uncached_tokens_per_percent": 35526.83
        }
      ],
      "no_token_samples": 0,
      "observations": 455,
      "percent_delta": 158.0,
      "samples": 75,
      "saturated_samples": 0,
      "tokens_all": 94183083,
      "tokens_uncached": 2931115,
      "uncached_tokens_per_percent": 18551.361,
      "window": "secondary",
      "window_minutes": 10080
    }
  ]
}
```

### reconcile --pool codex --days 7 with the anchor as --expect (gate blocks only; instances are identical to the run above)

```json
{
  "gate_within_10_percent": "fail",
  "windows": [
    {
      "window": "primary",
      "uncached_tokens_per_percent": 5417.804,
      "gate": {
        "basis": "expected uncached tokens per percent",
        "expected": 4460.0,
        "relative_error": 0.2148,
        "verdict": "fail"
      }
    },
    {
      "window": "secondary",
      "uncached_tokens_per_percent": 18551.361,
      "gate": {
        "basis": "expected uncached tokens per percent",
        "expected": 26235.0,
        "relative_error": -0.2929,
        "verdict": "fail"
      }
    }
  ]
}
```

### reconcile --pool opencode-go --days 7 (instances omitted)

Two probe readings per pool exist, so each window has at most one sample.

```json
{
  "candidate_calls": 21293,
  "candidate_tokens_all": 10718459081,
  "candidate_tokens_uncached": 17849589,
  "gate_within_10_percent": "unverified",
  "limits": "Local calls only; account-wide quota may include other hosts or cloud tasks. Provider percents are integers, so small deltas are rounding noise. Stale (out-of-order) Codex snapshots and resets are excluded. Claude billing is inferred from native Anthropic model ids.",
  "pool": "opencode-go",
  "since": "2026-10-31T16:09:12.850645Z",
  "status": "measured",
  "windows": [
    {
      "all_tokens_per_percent": 147681.0,
      "decreases_skipped": 0,
      "gate": {
        "reason": "fewer than 2 window instances with at least 5 percent movement, and no --expect value",
        "verdict": "unverified"
      },
      "no_token_samples": 0,
      "observations": 2,
      "percent_delta": 7.0,
      "samples": 1,
      "saturated_samples": 0,
      "tokens_all": 1033767,
      "tokens_uncached": 1016046,
      "uncached_tokens_per_percent": 145149.429,
      "window": "monthly",
      "window_minutes": null
    },
    {
      "all_tokens_per_percent": null,
      "decreases_skipped": 0,
      "gate": {
        "reason": "fewer than 2 window instances with at least 5 percent movement, and no --expect value",
        "verdict": "unverified"
      },
      "no_token_samples": 0,
      "observations": 2,
      "percent_delta": 0.0,
      "samples": 0,
      "saturated_samples": 0,
      "tokens_all": 0,
      "tokens_uncached": 0,
      "uncached_tokens_per_percent": null,
      "window": "rolling",
      "window_minutes": null
    },
    {
      "all_tokens_per_percent": 68917.8,
      "decreases_skipped": 0,
      "gate": {
        "reason": "fewer than 2 window instances with at least 5 percent movement, and no --expect value",
        "verdict": "unverified"
      },
      "no_token_samples": 0,
      "observations": 2,
      "percent_delta": 15.0,
      "samples": 1,
      "saturated_samples": 0,
      "tokens_all": 1033767,
      "tokens_uncached": 1016046,
      "uncached_tokens_per_percent": 67736.4,
      "window": "weekly",
      "window_minutes": null
    }
  ]
}
```

### reconcile --pool claude --days 7 (instances omitted)

Two probe readings per pool exist, so each window has at most one sample.

```json
{
  "candidate_calls": 5020,
  "candidate_tokens_all": 1127985814,
  "candidate_tokens_uncached": 35680838,
  "gate_within_10_percent": "unverified",
  "limits": "Local calls only; account-wide quota may include other hosts or cloud tasks. Provider percents are integers, so small deltas are rounding noise. Stale (out-of-order) Codex snapshots and resets are excluded. Claude billing is inferred from native Anthropic model ids.",
  "pool": "claude",
  "since": "2026-10-31T16:09:13.151373Z",
  "status": "measured",
  "windows": [
    {
      "all_tokens_per_percent": 15721040.6,
      "decreases_skipped": 0,
      "gate": {
        "reason": "fewer than 2 window instances with at least 5 percent movement, and no --expect value",
        "verdict": "unverified"
      },
      "no_token_samples": 0,
      "observations": 2,
      "percent_delta": 5.0,
      "samples": 1,
      "saturated_samples": 0,
      "tokens_all": 78605203,
      "tokens_uncached": 2188678,
      "uncached_tokens_per_percent": 437735.6,
      "window": "seven_day",
      "window_minutes": null
    }
  ]
}
```
