---
name: living-documents:onboard
description: LLM supplement for ld onboard — fills prompt, summaries, file descriptions, stories, changelog from script JSON + sessions. Stdlib script owns canonical. Mirrors weekly-llm-analysis delineation.
---

# living-documents:onboard

LLM wrapper around stdlib `ld onboard`. See `living-documents-system/specs/onboarding.md` and `weekly-llm-analysis` for contract.

## Delineation (NON-NEGOTIABLE)

**Scripting (deterministic, stdlib only, no network, byte-identical):** `ld onboard --project /code/foo --with-template` — one canonical stats table, per-item `problems` isolation, `generated_at` from newest input mtime via `sort_keys`, provenance `verified`/`estimated`/`unavailable`. Writes only canonical pages (`prompt-corpus.md` placeholder + `file-index.md` tree) via `write_page`. Never invents a file or rewrites `FORMAT_VERSION`.

Never let an LLM rewrite canonical stats, invent a file, or fill a missing metric. If LLM disagrees with `stats` (fileCount, totalBytes, gitDirty), canonical wins and disagreement is logged as `problem`.

**LLM (supplement only, post-onboard, optional):** reads script JSON + `cass triage` + `~/.local/share/muse/sessions/**/*.jsonl` (muse not in cass) + vault scan (10-50 md sample) and writes only `*.md` body in `LIVING_DOCUMENTS/projects/<id>/`, never `FORMAT_VERSION` keys.

## Input

- `ld onboard --project /code/foo --with-template` JSON (`stats`, `fileIndexSample`, `prdFound`, `weeklyImport`)
- `cass triage --json` + `cass search` (all harnesses)
- `~/.local/share/muse/sessions/**/*.jsonl` (muse sessions NOT in cass)
- Vault scan (md files, 10-50 sample)
- `specs/onboarding.md` + template partials for context

## Output

Writes only `*.md` body in `LIVING_DOCUMENTS/projects/<id>/`, never `FORMAT_VERSION` keys:

- `prompt-corpus.md` — spell-fixed full user prompt text (100% fidelity, no truncation; saying “adjudicated” does not license loss)
- `project.md` — 2-para summary + boundary
- `file-index.md` — 1-liner per file from tree (capped)
- `requirements.md` — user stories extract
- `history.md` — changelog generalization (raw `session.jsonl` stays raw evidence)
- `what-to-do.md` — phases → todo, next item, carry age

Integration: script `problems` array surfaces in JSON; LLM keeps prior supplement if new JSON malformed.

## Model pinning

`.env` in `living-documents-system` pins default `MODEL=opencode/deepseek-v4-flash` (maps `opencode-zen: deepseek-v4-flash-07031`). Resolver reads `.env` → `$MODEL` → `config.env` → default. Same value used by `schedule.py` and headless run.

## Failure modes (mirrors weekly-llm-analysis)

- No API key / no network / provider down: writes deterministic heuristic supplement (extractive summary of prompt corpus + file tree heuristic) with `model: heuristic-fallback` and `data_quality: estimated`, so `ld validate` still passes.
- Malformed LLM JSON: logged to `problems`, prior body retained, never aborts canonical page.
- Token budget: supplement capped at 4 KB per page, 32 KB total, to keep corpus small.
- Missing dashboard table: onboard marks `weeklyImport: false` with `provenance: unavailable`; LLM notes gap instead of inventing.

## Meta-improve loop (like `audit_viz` → `meta_improve`)

```bash
python3 scripts/audit_onboard.py --json   # scores prompt completeness %, file-desc coverage, story extract
python3 scripts/meta_improve.py --audit /tmp/audit_onboard.json --out /tmp/meta_proposals.json
python3 scripts/meta_improve.py --apply /tmp/meta_proposals.json --check  # only if ld validate still passes + audit non-regressing
```

Raise `overall_avg` and `Actionability` without regressing `Truthfulness/Provenance`. Headless OMP:

```bash
omp run --model opencode/deepseek-v4-flash "read specs/onboarding.md and fill md body from onboard JSON + sessions"
ld validate --project foo
```

Schedule: script nightly `0 20 * * 5` like dashboard, skill headless on change or `ld onboard --now`.
