# agy system model: what the harness does to your work

Evidence as of October 2026. Each claim is tagged with its basis. Treat anything tagged UNKNOWN as something to calibrate, not assume.

## Contents
1. Pools and windows
2. What is metered
3. Context ceilings
4. Headless invocation surface
5. Files the harness reads and writes
6. Error shapes
7. Unknowns and how to calibrate them

## 1. Pools and windows

- Usage is tracked in **separate pools**: Gemini models in one, Claude and GPT partner models in another. Each pool has its own short-window balance and weekly balance. (Basis: on-screen usage display as documented by SmartScope, 2026-10-04.)
- **Short window**: quotas refresh every five hours for Pro and Ultra subscribers. (Basis: Google blog, 2025-12-05.)
- **Weekly baseline**: premium models carry a strict weekly limit. When it is hit, the timer shows a multi-day cooldown until the current 7-day cycle resets, and the 5-hour refresh does not restore anything. (Basis: Google staff reply on the AI dev forum, 2026-06-03; SmartScope.)
- Practical reading: the 5-hour window governs bursts; the weekly baseline governs campaigns. A single heavy prompt has been reported to consume about half of both windows (anecdotal, X posts cited by SmartScope).

## 2. What is metered

- Consumption tracks **agent work**, not prompt count. Multi-step tasks (many file reads, edits, consecutive tool calls) consume more from a single instruction; simple tasks consume less. (Basis: Google blog; Antigravity docs as cited by SmartScope.)
- The precise unit is undisclosed. The working model this skill uses: work is dominated by tokens processed per turn (resident context plus new input), plus thinking and output. This matches every observed pattern: turn-heavy sessions with large residency drain fastest, and quota drops sharply during long file-ingest phases. (Basis: inference from operator logs and field reports; consistent, not proven.)
- Whether provider-side prompt caching reduces quota inside agy: UNKNOWN. Do not plan on it.

## 3. Context ceilings

- Claude models in agy: plan for **200k tokens** (operator-measured ceiling). Some third-party proxies expose 1M for Opus via an opt-in flag; do not assume agy does.
- Gemini Pro: about **1M tokens** (vendor-advertised; third-party docs confirm auto-enabled 1M for Gemini 3 Pro).
- Gemini Flash: large window; confirm with `/context` on your account.
- `/context` in interactive agy shows token use by category and manages checkpoints.
- Anthropic's long-context guidance favors placing long material above the instructions with the request at the end, and notes that a fresh window rebuilding state from files can outperform compaction for long-horizon work. The skill's template and one-unit-per-session design follow both.
- Running near the ceiling is doubly expensive: every turn re-processes a near-full window, and the harness may compact or truncate, losing detail you paid to load. Target about 60% peak residency for Claude.

Size in KB without arithmetic: 4 KB of English prose or Markdown is about 1k tokens; source code runs a little denser (about 3.3 KB per 1k tokens). 200k tokens is about 800 KB of prose. `scripts/budget.py` does the conversion.

## 4. Headless invocation surface

Second-hand (CLI guide) plus operator logs. Confirm with `agy --help` on the installed version, and record the result in `models.local.md` beside your plan.

| Flag or command | Behavior |
|---|---|
| `-p`, `--print`, `--prompt` | Run one prompt and exit |
| `--model <id>` | Select model. Observed id: `claude-opus-5-5-high` (effort encoded as a suffix). Display names such as `"Gemini 3.5 Flash"` are also accepted in some versions. |
| `--dangerously-skip-permissions` | Approve all tool calls including shell and writes |
| `--output-format text|json|stream-json` | `stream-json` emits newline-delimited events; log it for forensics |
| `--mode default|accept-edits|plan` | Edit approval mode |
| `--print-timeout <s>` | Seen in operator scripts with `0` (no harness-side print timeout). The driver passes it by default so long units are not cut off by the harness; verify with `--help` and drop it via `AGY_EXTRA_ARGS` if your version rejects it |
| `/usage` (alias `/quota`) | Interactive: remaining balance per pool and reset time |
| `/context` | Interactive: token use by category, checkpoints |
| `/model`, `/agent`, `/agents`, `/permissions` | Interactive: switch model, dispatch or monitor background subagents, set per-tool rules |

There is no `--yolo` and no `--headless`. Headless runs reuse cached credentials from an interactive sign-in on that machine and exit with `authentication required` if none exist. Since release 1.1.13, `modelProvider: "gemini"` in settings with `GEMINI_API_KEY` is an alternative for Gemini.

Always redirect stdin from `/dev/null` in scripts; a worker waiting on stdin hangs silently.

## 5. Files the harness reads and writes

- Settings: `~/.gemini/antigravity-cli/settings.json` (`agentMode`, `modelProvider`).
- Workspace skills: `.agents/skills/` (each `name.md` becomes `/name`). Workspace MCP: `.agents/mcp_config.json`.
- Context files: both `GEMINI.md` and `AGENTS.md` are read from the workspace. Anything in them is resident in every turn, so keep them short in directories where headless workers run, or launch workers from a clean working directory.
- Hooks: JSON lifecycle hooks (before tool call, after file edit, session start). Workspace hooks override global hooks.
- Session state: `~/.gemini/antigravity-cli/brain/<session-uuid>/`, including `transcript_full.jsonl`. Use it for post-mortems: it records every step, and operators have reported reading cumulative token counts per step from it (verify on your version).

## 6. Error shapes

Quota error as logged by `agy -p`:

```
AGY_ERROR: {"short_error":"RESOURCE_EXHAUSTED (code 429): Individual quota reached. ... Resets in 4h33m58s.","status":"RESOURCE_EXHAUSTED","error_code":429,"code_kind":"http","retryable":true,"error_id":"..."}
```

- `retryable` is `true` for both the short window and the weekly lock. Classify by duration: reset at or under about 5h15m is the short window; anything longer is the weekly baseline.
- The short window can hide a near-empty weekly balance. A relaunch right after the short reset can consume the weekly remainder in minutes if it re-ingests a large context.

## 7. Unknowns and how to calibrate them

| Unknown | Calibration |
|---|---|
| Quota cost of one unit | Interactive `/usage` before and after a representative unit; record per pool in `calibration.md` |
| Weekly reset anchor | Record the reset time printed by the first weekly 429 or shown by `/usage`; it is stable within a cycle |
| Model ids on this account | `/model` in interactive agy; record exact strings |
| Whether json output carries token counts | Run one tiny `--output-format json` call and inspect the keys |
| Peak residency of a unit | Inspect `transcript_full.jsonl` of the calibration session for per-step token counts |
