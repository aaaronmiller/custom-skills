# Supported harnesses

This file is the single source of truth for harness support in `skill-doctor`. Reference it instead of repeating harness lists in `SKILL.md`.

## Sources the collector parses

Any harness may run skill-doctor (see SKILL.md Step 0). This table lists the session sources `collect_sessions.py` parses, not the harnesses allowed to run the skill.

| Source | Collector ID | Local conversation source |
| --- | --- | --- |
| Warp | `warp` | Read-only Warp conversation databases |
| Claude Code | `claude` | Project-history JSONL |
| Codex | `codex` | Rollout JSONL |
| Pi | `pi` | Pi agent JSONL (`~/.pi/agent/sessions`) |
| Grok Build | `grok` | Grok Build chat_history JSONL (`~/.grok/sessions`) |
| ZCode | `zcode` | ZCode model-io rollout (`~/.zcode/cli/rollout`) |
| Hermes | `hermes` | Hermes Agent state.db (SQLite: `sessions` + `messages`) |

## Extra passes for other sources

Run each pass into its own subdirectory of `REPORT_DIR` so inventories do not overwrite each other, then score every pass's transcripts and sum the stats.

- **oh-my-pi (omp).** omp writes the Pi v3 session format (`session` and `message` records, plus a leading `title` record) under `~/.omp/agent/sessions`. Run the collector a second time with `--harness pi --pi-home ~/.omp/agent --out "$REPORT_DIR/omp"`. Label these sessions `omp` in the report. Status: format matched by inspection on 2026-11-08; not yet confirmed by a run. If the pass samples 0 sessions while omp sessions exist in the window, report omp as found but not parsed.
- **Any source that cass indexes** (gemini, opencode, antigravity, kiro and others). When `casr` and `cass` are installed: list recent sessions with `casr list --json --limit N --provider <slug>`, then export each with `cass export <path> --format markdown -o "$REPORT_DIR/cass/transcripts/<slug>-<id>.md"`. Gemini and opencode exports worked on 2026-11-08. These exports may carry messages without tool calls; score efficiency as `insufficient_evidence` when no tool calls appear.
- **Not covered:** muse sessions stored in its session-index database (`cass export` of a muse path failed on 2026-11-08). Report them as found but not parsed.

## Collector source selection

- `--harness auto` scans every locally available supported source and is the default.
- `--harness all` also requests every supported source.
- `--harness <collector-id>` restricts collection to one source from the table.
- A report containing one source uses its collector ID in `inventory.json`; a report containing multiple sources uses `mixed`.

Harness-specific source overrides:

- `--claude-home PATH` — nonstandard Claude Code configuration directory.
- `--codex-home PATH` — nonstandard Codex home.
- `--warp-db PATH` — explicit Warp database; repeatable.
- `--warp-data-dir PATH` — nonstandard Warp channel-data directory.
- `--pi-home PATH` — nonstandard Pi agent home (default `~/.pi/agent`).
- `--grok-home PATH` — nonstandard Grok Build home (default `~/.grok`).
- `--zcode-home PATH` — nonstandard ZCode home (default `~/.zcode`).
- `--hermes-home PATH` — Hermes Agent home containing `state.db` (default discovery checks `HERMES_HOME`, `~/.hermes`, then `~`).

## Skill locations

Project skills are discovered from:

- `.agents/skills`
- `.claude/skills`
- `.codex/skills`

Global skills are discovered from the corresponding directories under the user's home and configured harness homes when `--include-global-skills` is set: `~/.claude/skills`, `~/.agents/skills`, `~/.codex/skills`, Pi's skill directory under its agent home (default `~/.pi/agent/skills`), Grok Build's `~/.grok/skills`, and ZCode's `~/.zcode/skills`.
