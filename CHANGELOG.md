# Changelog

## [Unreleased]

### Added
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
