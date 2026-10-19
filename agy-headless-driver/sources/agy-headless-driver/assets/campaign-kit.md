# Campaign kit: manifest, calibration and model registry

Three small files that live beside a campaign's prompts. Copy the blocks below.

## units.tsv (driver manifest)

Tab-separated, one unit per line, top to bottom. Columns 6 (`verify_cmd`) and 7 (`requires`) are optional; leave a field empty to skip it. The driver skips done units, parks a pool on a weekly lock, and reports a unit as blocked (without running it) while anything in its `requires` list is not done.

Ordering rule: a unit that consumes another unit's output lists it in `requires`, so a pack is never built from a pass that did not finish. Units that do not depend on the parked pool (indexes, inventories, an independent review of an already finished unit) keep running when the other pool parks.

```
# unit_id	pool	model_id	prompt_file	done_marker	verify_cmd	requires
pack-06	gemini	{{GEMINI_PRO_ID}}	/abs/run/prompts/pack-06.md	/abs/run/markers/pack-06.done	python3 /abs/skill/scripts/budget.py /abs/run/packs/pack-06.md	
pass-06	claude	{{OPUS_ID}}	/abs/run/prompts/pass-06.md	/abs/run/markers/pass-06.done	python3 /abs/validator.py /abs/tree	pack-06
pack-07	gemini	{{GEMINI_PRO_ID}}	/abs/run/prompts/pack-07.md	/abs/run/markers/pack-07.done	python3 /abs/skill/scripts/budget.py /abs/run/packs/pack-07.md	pass-06
pass-07	claude	{{OPUS_ID}}	/abs/run/prompts/pass-07.md	/abs/run/markers/pass-07.done	python3 /abs/validator.py /abs/tree	pack-07
review-06	gemini	{{GEMINI_PRO_ID}}	/abs/run/prompts/review-06.md	/abs/run/markers/review-06.done		pass-06
```

CRLF line endings are tolerated, but keep the tabs: editors that convert tabs to spaces break the manifest.

Typical launch:

```
LOG_DIR=/abs/run/logs FORBIDDEN_ROOTS=/abs/repo:/abs/harness-config bash /abs/skill/scripts/agy-run.sh /abs/run/units.tsv
```

Exit 0 all done; 75 a pool is parked (read `logs/parked-pools.tsv` for the unlock duration); 1 a unit failed (read `logs/status.tsv`); 73 another driver already holds this LOG_DIR (overlapping cron runs are refused, so one campaign never runs twice). Re-running the same command after an unlock resumes where the campaign stopped.

## calibration.md

```
# Quota calibration: {{campaign}}
| unit | pool | model | /usage short before | after | weekly before | after | turns | peak context | notes |
|---|---|---|---|---|---|---|---|---|---|
| pass-06 | claude | {{OPUS_ID}} | 100% | 61% | 100% | 88% | 74 | 96k | pack 31k |

Derived: one pass ~ 39% of short window, ~12% of weekly.
Plan: 2 passes per 5h window, 7 passes per week max, keep 1 in reserve.
Weekly reset anchor (from /usage or first weekly 429): {{weekday time tz}}
```

Turns and peak context come from the unit's `transcript_full.jsonl` in the brain directory.

## models.local.md

```
# agy model registry on this machine (from /model and agy --help, agy version {{x.y.z}})
| pool | display name | --model id | notes |
|---|---|---|---|
| claude | Claude Opus 5.5 (high) | claude-opus-5-5-high | effort in suffix |
| claude | Claude Sonnet 5.5 | {{id}} | |
| gemini | {{Gemini Pro display name}} | {{id}} | ~1M context |
| gemini | {{Gemini Flash display name}} | {{id}} | |
Flags confirmed: -p, --model, --output-format stream-json, --dangerously-skip-permissions, --print-timeout
```
