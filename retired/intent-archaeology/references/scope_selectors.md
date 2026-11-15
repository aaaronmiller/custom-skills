# Scope Selectors

> **Version:** 1.2.1 (updated for cass v0.6.22 compatibility)
> **When to read:** before any non-default Phase 5+ run, or whenever the user
> asks for a narrower / wider / different cut of the corpus than the default
> "all prompts from the last 30 days, all projects, all agents".

This is the canonical spec for the composable scope system. The skill's
Phase 5+ scripts accept these flags via `scripts/lib/scope.py`; the
ScopeSpec dataclass compiles them into `cass` CLI invocations.

## Design

Scope is **composable**: every dimension is independent and optional, and
any combination is valid. The default is `--since 30d` across all projects
in the SQLite `projects` table and all agents cass knows about.

Every run's scope is persisted in the `tranches` table. Re-running with a
different scope does not clobber earlier results — each `(scope_hash,
tranche_id)` pair is its own row. This is what lets you do "all prompts
from last week" today, "all prompts from this project ever" tomorrow, and
"only Cursor corrections from Q1" the day after, without losing prior work.

## The seven dimensions

### 1. Time — relative (`--since`)

`--since Nd` (e.g. `--since 7d`, `--since 30d`, `--since 365d`)

Default: `30d`.

Maps to cass (enumeration — Phase C):
- `cass search "" --days N --robot-format sessions` (sessions per workspace)

Maps to cass (search — Phase F):
- `cass search "<query>" --days N --json --fields full --limit <N>`
### 2. Time — absolute (`--from`, `--to`)

`--from 2025-01-01 --to 2025-06-30` (ISO dates, either or both may be omitted).

Default: none.

Maps to cass: post-filter on the timestamps from `cass search "" --robot-format sessions`. cass itself does not accept

### 3. Time — today (`--today`)

Boolean flag. Mutually exclusive with `--since` and `--from/--to`.

Maps to cass: `cass search "" --today --robot-format sessions`.

### 4. Projects (`--projects` or `--project-dir`)

`--projects foo,bar,baz` — short names, resolved against the `projects`
table (matching either `name` or `path`).

`--project-dir ~/code/foo` — absolute or `~`-expanded path, matched
against `projects.path`.

Default: all projects in the DB. (Phase 5 emits a warning if the DB is
empty and falls back to scanning `~/code` and `~/code2` if those exist.)

Maps to cass: one `cass search "" --workspace /abs/path --robot-format sessions --days N`
per project, results unioned. cass takes a single `--workspace` per
invocation; the skill handles fan-out.

### 5. Agents (`--agent`)

`--agent claude` or `--agent claude,cursor,gemini` (comma-separated).

Open vocabulary: passes agent names through to cass, which validates at
runtime. cass v0.6.22 supports 22 connectors; unknown agents produce a
warning, not an error.

Default: all agents.

Maps to cass: `cass search "" --agent <name> --workspace <path> --robot-format sessions`
(one invocation per agent, results unioned). The `--agent` flag works with
`cass search` for enumeration.

### 6. Prompt type (`--type`)

`--type correction` or `--type correction,scope-cut,abandonment`.

Closed vocabulary (mirrors `references/intent_taxonomy.md`):
`question`, `command`, `correction`, `scope-cut`, `scope-add`,
`spec-reference`, `bug-report`, `constraint`, `preference`, `noise`.

Default: all types.

Maps to cass: **post-distillation filter only**. cass indexes message
text, not intent labels. The skill applies this filter on the `intents`
table after Phase 6 has labeled rows. Using `--type` on `05_extract_prompts.py`
is a no-op with a warning; using it on `06_distill_intent.py` and later
filters correctly.

### 7. Content regex (`--matches`)

`--matches "jwt|auth|token"` — Python `re` syntax, applied case-insensitive
to the prompt text.

Default: none.

Maps to cass:
- Phase C (exhaustive): post-filter on the extracted prompt text after
  `cass export`. Slower but exhaustive.
- Phase F (cited evidence): `cass search "<regex>" --json` directly.
  Faster, but recall depends on cass's BM25+vector fusion — only use for
  Phase F.

### 8. Single session (`--session`)

`--session /path/to/session.jsonl` — absolute path to a single session file.

Default: none.

When set, all other scope dimensions are ignored with a warning (the
session is the scope). Maps to cass:
- `cass export /path --format json` (always)
- `cass export /path --include-tools` (when `--include-tools` is also set)

### 9. Result cap (`--limit`)

`--limit 500` — integer. Stops enumeration after N prompts have been
extracted (Phase C) or returns top-N results (Phase F).

Default: none (unbounded).

Maps to cass:
- Phase C: stop iterating sessions after the cumulative prompt count
  reaches N.
- Phase F: `cass search ... --limit N --json`.

### 10. Ordering (`--ordering`)

`--ordering newest-first` (default) or `--ordering oldest-first`.

Newest-first is strongly recommended (see SKILL.md rule #8). Oldest-first
is supported for re-pass scenarios where you want to backfill from the
beginning of time up to a fixed cutoff.

Maps to cass: cass search results from `--robot-format sessions` are
already newest-first by default. Oldest-first requires a reverse sort
in Python before per-session export.

| User says | Compiled scope |
|-----------|----------------|
| "all my prompts from the last week" | `--since 7d` |
| "what did I do on my-app today" | `--projects my-app --today` |
| "every Cursor prompt since January about auth" | `--agent cursor --from 2025-01-01 --matches "auth\|jwt\|login"` |
| "all the corrections I issued last month" | `--type correction --since 30d` (applied at distillation) |
| "this one session in full" | `--session /path/to/session.jsonl --include-tools` |
| "everything on foo and bar from Q1" | `--projects foo,bar --from 2025-01-01 --to 2025-03-31` |

## Compilation rules

`scripts/lib/scope.py` resolves the scope to a list of cass invocations
following these rules, in order:

1. If `--session` is set, emit one `cass export` command (plus
   `--include-tools` if set) and stop. All other dimensions ignored.
2. Compute the time filter: `--today` > `--from/--to` > `--since Nd` >
   default `--since 30d`.
3. Compute the project list: explicit `--projects` or `--project-dir` >
   all rows in `projects` table.
4. For each project, emit `cass search "" --workspace <abs_path>
   --robot-format sessions --days <N>` (or `--today`). Union the session lists.
5. Apply `--agent` post-filter on the session list (cass search's enumeration
   already supports `--agent` per invocation, but unioning across agents
   requires per-agent calls; post-filter is the simpler path).
6. Sort by `--ordering` (cass search returns newest-first; oldest-first
   requires Python reverse sort).
7. Apply `--limit` to truncate the session list (Phase C) — but emit a
   warning that truncation may break completeness guarantees.
8. For each remaining session, emit `cass export <path> --format json`
   (and `cass export <path> --include-tools` if `--include-tools` set).
9. Apply `--matches` regex post-filter on extracted prompt text (Phase C)
   OR emit `cass search "<regex>" --limit N --json` (Phase F).
10. Apply `--type` post-filter on the `intents` table (Phase 6+ only).

The compiled scope is JSON-serialized and SHA-256 hashed; the hash is the
`scope_hash` primary key in the `tranches` table.

## Defaults are explicit

Never run with an implicit scope. If the user invokes Phase 5 with no
scope flags, the script emits a log line: "Using default scope:
--since 30d, all projects, all agents". This makes the scope visible in
logs and in the eventual status vector report.
