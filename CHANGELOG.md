# Changelog

## [spec-prep 2.4.0 + spec-audit 1.0.0] — 2026-10-16

### Changed
- Superseded `spec-workflow` by spec-prep 2.4.0 (per-file comparison at `/tmp/spec-workflow-compare.md`: 1 COVERED, 5 PARTIAL, 7 UNIQUE, 1 SUPERSEDED). CREATE/IMPLEMENT absorbed — Mode C, depth-preservation directives, 80-word density heuristic, per-category done-criteria merged into spec-prep. Retired `spec-workflow/` to `staged-for-deletion/spec-workflow--superseded-by-spec-prep-2.4.0/`.
- Split AUDIT gate to new standalone `spec-audit` 1.0.0 skill (backtranslation, cold-pass, drift taxonomy, stage checklists, report templates — no spec-prep equivalent existed). spec-prep triggers consolidated; audit triggers route to spec-audit.

## [spec-prep 2.3.3] — 2026-10-16

### Changed
- Tiered ratification (user directive: author-supplied specs are pre-ratified, review wastes author time). `spec-prep/SKILL.md` Authorship rule, Existing-specs and Recovery entries, and Phase 6 delivery now state: human-authored packs need no review gate — the gate battery (audit, trace, depth, prerequisites) IS the review; delivery names paths with MAY-review/never-REQUIRED wording and silence-is-consent. Mandatory ratification survives only for system-drafted or system-inferred material. `references/spec-template.md` authorship tiered likewise. Distributable archives rebuilt (36 files, no nesting).

## [spec-prep 2.3.2] — 2026-10-16

### Fixed
- Initiation-transport violation (Helix 2026-10-16 post-mortem): prior session read "prepare then implement via new session" as authority to spawn a task/subagent in-tree as the "fresh" session, executing T001 and committing ack/code without user restart. `spec-prep/SKILL.md` Phase 7 now forbids in-process task/subagent spawn as initiation transport, adds a launch-authority test (named project + direct launch instruction) and an authoring-session freeze after handoff; `references/fresh-session-initiation.md` marks subagent-authored implementation artifacts VOID and validates acks only from parentless session IDs; `references/terminology.md` states a spawned subagent is never a fresh harness. User STOP overrides todo/resume reminders. Distributable archives (`spec-prep.skill`, `spec-prep/spec-prep.SKILL`) rebuilt from canonical sources with no nested archives (33 files).

## [Unreleased]

### Added
- `system-checkup` — SPECTRE-16-specific periodic system checkup (Windows Update/servicing, memory and telemetry, Process Lasso Pro rules, crashes, Bluetooth input, storage reclaim with a dry-run removal script, npm→pnpm/bun hygiene, software currency, living-document folder cleanup, dark HTML report). Grunt work runs on headless omp workers (opencode-go/muse-spark-1.3-contributor). Windows Claude Code uses a deployed copy; `scripts/deploy-windows.sh` keeps it in sync.
- `third-party-skills.json` manifest at `~/code/agents/third-party-skills.json` — manifest-driven integration for external skill repos (taste-skill, ponytail, drawio-skill, SkillSpector, skill-audit).
- `scripts/sync-third-party.py` at `~/code/agents/scripts/` — sync engine that clones/pulls third-party repos and selectively symlinks skills, commands, hooks, and agents.
- Integrated `--third-party` flag into `sync.sh` — runs automatically during `--fix` and previews during `--dry-run`.

### Fixed
- Mermaid diagram syntax in `external_skills_integration_plan.md` — replaced problematic `subgraph` labels with colons/slashes.

### Removed
- `spec-audit-skill-v2` and `spec-audit-skill` (v1) — superseded by the v3 backtranslation methodology; unique council-plan template migrated forward.
- `spec-audit-skill-v3/references/spec-audit-skill-v3.md` — dead embedded copy of an older SKILL body (never loaded).
- `karpathy-wiki` — not a skill; the full project lives in `~/code/wiki-memory`. Removed orphaned stub + dead `/home/cheta/...` symlink.

### Changed
- Renamed `spec-audit-skill-v3` -> `spec-audit-skill` (de-versioned name + H1; methodology v3.1 markers retained).
- `skill-audit-skill`: illustrative reference example repointed from phantom `references/patterns.md` to real `references/scoring-rubric.md`.
- `skill-creator`: removed fragile cross-skill reference into `skill-audit-skill` (now self-contained).
- `spec-audit-skill`: removed 3 dangling pointers to never-authored `built-vs-designed-guide.md`; migrated council-plan template into `council-formations.md`.


### Fixed
- Standardized skill support documentation directories from `resources/` to `references/`.
- Removed repeated concatenated `SKILL.md` bodies across imported skills.
- Added missing `mcp-conversion` reference docs and helper scripts promised by its `SKILL.md`.
- Synced frontend-design-masterclass from master-user-skills, removed duplicated skill body, and restored the referenced `references/` support-file layout.
