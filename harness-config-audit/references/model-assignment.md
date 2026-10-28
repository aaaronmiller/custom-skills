# Model assignment

Which model for which role, and what to fall back to when a quota is hit.

**Derived 2026-08-25 from `model-scan --free-mode --eval-mode free --json`**, which
live-probes every model on every configured provider and records accessibility,
latency, tokens/sec, tool support and Artificial Analysis scores. 116 models
probed, 47 reachable, **37 both reachable and tool-capable**.

Re-derive with that command rather than trusting this file after a week.
`model-scan --refresh-aa` refreshes the intelligence scores.

## Read this before picking anything

**Tool support is the first filter, not intelligence.** Ten reachable models
cannot call tools and are therefore useless as a subagent however clever they
are — `nvidia/nemotron-3-ultra-550b-a55b` (AA 38.3) is one of them. Filter on
`has_tools` first, rank second.

**Quotas are per-model, not per-account.** Measured directly: in the same second
on the same key, `z-ai/glm-5.2:free` returned 429 with
`limit_source: upstream_provider_shared_pool` while `minimax/minimax-m3:free`
returned 200. The free tier shares an upstream pool with every other OpenRouter
user, so a free model's availability has nothing to do with your usage.

The consequence is the important part: **running N different models in parallel
multiplies throughput, where running N workers on one model does not.** That is
the lever for concurrency, more than any per-worker tuning.

## The standout

**`opencode-go/deepseek-v4-flash` — AA 51.8, 68.6 tok/s, 1.0 s latency.**

Nothing else is close on the combination. It is 8.7 AA points above the current
`muse-spark` default, three times faster than most of the field, and the fastest
tool-capable model measured. Make it the general-purpose default.

## Usable models, ranked

Accessible **and** tool-capable, from the live probe:

| model | provider | AA | coding | tok/s | latency |
| --- | --- | --- | --- | --- | --- |
| `glm-5.3` | opencode-go | **59.5** | 74.8 | 15.6 | 2.1 s |
| `qwen3.8-max` | opencode-go | 58.1 | 71.8 | 14.3 | 2.0 s |
| `deepseek-v4-pro` | opencode-go | 53.2 | 68.8 | 19.8 | 1.6 s |
| `glm-5.2` | opencode-go | 52.6 | 68.8 | 26.0 | 1.2 s |
| **`deepseek-v4-flash`** | **opencode-go** | **51.8** | **69.1** | **68.6** | **1.0 s** |
| `qwen3.7-max` | opencode-go | 46.7 | 66.0 | 49.9 | 4.4 s |
| `minimax-m3` | opencode-go | 45.4 | 58.6 | 21.0 | 1.5 s |
| `minimax/minimax-m3:free` | openrouter | 45.4 | 58.6 | 11.9 | 1.2 s |
| `kimi-k2.6` | opencode-go | 45.1 | 61.8 | 18.3 | 1.8 s |
| `glm-5.1` | opencode-go | 41.0 | 55.8 | 17.0 | 1.9 s |
| `qwen3.6-plus` | opencode-go | 40.5 | 54.5 | 39.0 | 3.6 s |
| `minimax/minimax-m2.7:free` | openrouter | 38.9 | 52.6 | 9.9 | 3.2 s |
| `nemotron-3-ultra-550b:free` | openrouter | 38.3 | 49.3 | 25.4 | 0.9 s |

The operator's floor — `mimo-v2.5` at 40.1 — sits between `glm-5.1` and
`qwen3.6-plus`. Everything above that line qualifies for real work.

## Role assignment

**General subagent work.** `deepseek-v4-flash` (opencode-go). Fastest
tool-capable model measured and comfortably above the floor. Fall back to
`glm-5.2`, then `minimax-m3`.

**Verification and high-IQ judgement.** `glm-5.3` (AA 59.5) or `qwen3.8-max`
(58.1). Both on opencode-go, both tool-capable, both well clear of the field.
`stealth/ox-alpha` remains worth trying — it produced the sharpest analysis in
this audit's head-to-head passes, catching two contests the cheaper model judged
both ways — but the probe found it **rate-limited and unreachable**, so it
cannot be relied on. Try it, fall through to `glm-5.3` on 429.

**Extra hands under rate limiting.** Spread across providers rather than piling
onto one: `minimax/minimax-m3:free` (openrouter), `minimax/minimax-m2.7:free`
(openrouter), `nemotron-3-super-120b-a12b:free` (openrouter, 56 tok/s but AA
25.7 — fetch-and-summarise only), `qwen3.6-plus` (opencode-go).

**Cheap and fast, quality not critical** — title generation, classification,
triage: `nemotron-3-super-120b-a12b:free` at 56 tok/s / 0.6 s, or
`deepseek-v4-flash` if the volume is low enough not to matter.

## What is broken right now

`model-scan` found most of the incumbent stack failing:

| slot | model | status |
| --- | --- | --- |
| R2/R4/R11/R12 | `muse-spark-1.2-contributor` | **http_500** |
| R3/R6–R10 | `mimo-v2.5` | **auth_error** |
| proxy_BIG | `kilo/z-ai/glm-5.2` | **timeout** |
| proxy_MIDDLE | `opencode/deepseek-v4-flash-free` | **http_400** |

**Both models the operator nominated as defaults are down.** `muse-spark` returns
500 on every variant; `mimo-v2.5` fails auth across all six slots that use it.
model-scan proposes `glm-5.3` for delegation and `qwen3.6-plus` for compression,
which matches the ranking above.

Across all 116 probes: 18 `auth_error`, 22 `http_404`, 8 `timeout`, 4
`rate_limit`. Roughly half the configured catalogue is unreachable, which is
itself the argument for probing rather than assuming.

## Models already in use elsewhere — do not double-book

The operator runs other agents against some of these models, `glm-5.2` on
OpenRouter among them. That matters twice over.

**It contaminates the availability measurements above.** The 1-in-5 success rate
recorded for `z-ai/glm-5.2:free` is a shared upstream pool *plus* this machine's
own traffic. Some of that 429 rate is self-inflicted, so treat per-model
availability as a reading taken under existing load, not a property of the
model.

**And assigning a model that is already busy is self-contention.** Two of the
operator's own agents on one upstream pool will rate-limit each other, and the
symptom — intermittent 429s under load — looks exactly like an external quota
problem. Before assigning a model to subagent work, check whether something else
already holds it.

Practical rule: **give delegated work its own lane.** Where a model is in use by
an interactive agent, pick a different model for the subagents rather than a
larger share of the same one. The per-model quota structure means a second model
is nearly free throughput, while a second worker on the same model is not.

Currently known to be in use elsewhere:

| model | provider | used by |
| --- | --- | --- |
| `glm-5.2` | openrouter | other agents (operator, 2026-08-25) |

Add to this table as assignments are made. An entry here is a reason to route
around a model, not a reason to stop using it.

## Reasoning effort

| use case | effort |
| --- | --- |
| extraction, classification, formatting | `low` / `minimal` |
| description grading, routine review | `medium` |
| head-to-head judgement, adversarial verification | `high` / `xhigh` |
| final gate on an irreversible decision | `max` |

`deepseek-v4-flash` moves from AA 28.7 non-reasoning to 40.3 at max effort — an
11.6-point swing. Effort is not a minor dial on these models.

## Concurrency

Two independent ceilings; the tighter one binds.

- **API**: per-model, per-upstream-pool. ~2–3 concurrent agents on one model.
  Spreading across models and providers multiplies this.
- **Memory**, measured on this 7 GB host: `jcode` 275–326 MB per session, `omp`
  460–578 MB fresh (1,004 MB for an aged interactive session), `ante` 679 MB
  because it wraps Claude Code. Eleven concurrent omp workers drove available
  memory to zero and 4 GB into swap.

`cg-harness-monitor report` gives the current picture rather than an estimate.

## OAuth reuse

| credential | file | grants |
| --- | --- | --- |
| ChatGPT Plus | `~/.cli-proxy-api/codex-*-plus.json` | gpt-5.6-luna and siblings |
| Antigravity | `~/.cli-proxy-api/antigravity-*.json` | gemini-3.7-flash and opus-4.6, **two separate quotas** |
| opencode / opencode-go / openrouter / ollama-cloud | `~/.local/share/opencode/auth.json` | API keys, direct |

The OAuth credentials are reachable from other harnesses **only through the
local proxy stack** (`_proxy_stack_auto_start` in `~/.zshrc`, fronting
`127.0.0.1:8082/p/<name>`). That stack was down when this was written — every
port returned 000 — so those models were unreachable except through their own
CLI. Start it before assuming a gpt-5.6 or gemini-3.7 route exists.

**Antigravity is the largest unexploited pool**: two independent quotas on strong
models. A working route doubles the concurrency ceiling at no cost.

No muse-cli Amazon credential exists — `~/.local/bin/` holds only
`.muse-release-info.json`.

## Harness support

| harness | providers |
| --- | --- |
| `omp` | opencode-go, opencode-zen, openrouter — `--model <provider>/<id>` |
| `jcode` | 30+ including opencode-go, openrouter, zai, groq, cerebras — `-p <provider>` |
| `ante` | Claude only; wraps the Claude CLI |

**jcode's memory sidecar accepts only OpenAI or Claude models** and rejects
others with `Ignoring unsupported memory sidecar model override '...'`. Unmerged
fix at `alecuba16/jcode`, branch `feature/memory-sidecar-provider`, tracking
issue #679, adding `memory_sidecar_backend = auto|openai|claude|provider`.

## groq and cerebras — tested directly 2026-08-25

`model-scan` reported these as `http_404` and `http_402`. Direct calls show one
of those is a probe artifact and the other is real.

### groq — works, but the token budget is the real limit

`openai/gpt-oss-120b` is present on the key and **calls tools correctly**:

```
served_by: openai/gpt-oss-120b
tool_calls: YES -> calc({"expr":"17*23"})
```

`qwen/qwen3.6-27b` also serves. model-scan's 404 for both is wrong — worth
re-checking its groq probe.

The quota, from the response headers rather than documentation:

```
x-ratelimit-limit-requests:   1000      (reset 2m52s)
x-ratelimit-limit-tokens:     8000      (reset 577ms)
```

**8,000 tokens per minute is the binding constraint, not the request count.** A
single agent turn carrying a real context blows the token budget long before the
request budget. Groq is therefore usable for *short-prompt, high-frequency* work
— classification, triage, title generation, one-line judgements — and unusable
as a general subagent however fast it is (161 tok/s on gpt-oss-120b).

AA scores put it in the same bracket: `gpt-oss-120b` 24.1, `qwen3.6-27b` 31.3,
both below the `mimo-v2.5` floor of 40.1. Use for mechanical work only.

No minimax model exists on groq — the key exposes 13 models, all gpt-oss, qwen,
allam or audio.

### cerebras — not available

`gemma-4-31b` and `gpt-oss-120b` are both listed by `/v1/models`, and both
return:

```
{"message":"Payment required to access this resource. Visit your billing tab.",
 "type":"payment_required_error","code":"payment_required"}
```

The free tier is not active on this account. Nothing to configure here; it needs
resolving in the Cerebras billing tab before either model is usable. Their AA
scores (29.7 and 24.1) put them below the floor anyway, so this is a
short-prompt tier at best even once enabled.

### What this adds to concurrency

Groq is a genuine extra pool — its quota is independent of OpenRouter and
opencode-go — but only for work that fits in 8k tokens/min. Counting it as a
general-purpose worker slot will produce 429s under real load.
