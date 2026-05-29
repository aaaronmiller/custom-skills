# Changelog

## [Unreleased]

### Added
- `config.schema.yaml` — comprehensive configuration schema (wiki, ClawMem, MemVid, dream agent, intent router, classifier, LLM backend, rerank, MCP, all 7 agents, 4 presets)
- `setup.sh` — 8-phase multi-agent installer (wiki data dir, symlinks, ClawMem, MCP registration, skills, hooks, dream scheduler, env vars). Detects: Pi, Claude Code, Ante, KiloCode, OpenCode, Hermes, Antigravity
- `specs/requirements.md` — 6 narrative user stories, 37+ FR, 14 AC, glossary
- `specs/design.md` — 3-tier arch, 8 components, 6-phase plan, 10 risks, 4 integration points
- `specs/MASTER_SPEC.md` — aggregate entry point with cross-ref table
- Dream agent Phase 0: dynamic budget allocation (25% of idle, cap 7200s, refinement-aware ratio)
- Dream agent Phase 1: ClawMem REST API extraction with raw/ fallback
- Dream agent Phase 2: confidence scoring (4-factor weighted, council escalation stub)
- Dream agent Phase 3: wiki compilation with YAML frontmatter + wikilinks + git auto-commit
- Dream agent Phase 4: pattern detection (7 task types, threshold-3 skill creation)
- Dream agent Phase 5: ClawMem reindex POST trigger
- Dream agent Phase 6: vault improvement engine (missing metadata fix, structural lint)
- Dream agent `--quiet` and `--idle` CLI flags
- Scheduler systemd idle timer + daemon loop + launchd plist (macOS)
- Git-backed wiki with `.gitignore` (ignores .meta state files)
- SETUP.md: condensed setup guide (superseded by setup.sh as primary method)
- Multi-agent integration: skill symlinks, MCP registration, hooks, env vars for 7 agents
- `install.sh` lightweight wrapper delegating to `setup.sh`
- Wiki data moved to `~/.local/share/ai-wiki/` — globally accessible to all agents
- Cross-platform: Linux (systemd) + macOS (launchd) + WSL2 detection
- Presets: lightweight, balanced (default), high-quality, max-context

### Changed
- `dream/dream_agent.py` rewritten from 550-line cascade to 1040-line 6-phase architecture
- `dream/scheduler.py` rewritten with systemd timer + daemon + launchd + `--install` modes
- `skill/SKILL.md` updated to v3.0.0 with directive frontmatter, real paths, multi-agent support
- `wiki/AGENTS_WIKI.md` updated to v3 with confidence schema, ClawMem provenance, full frontmatter spec
- **Source of truth moved** from `/home/cheta/code/karpathy-wiki/` → `/home/cheta/code/skills-USER/karpathy-wiki/`
- `ante-spec/modules/karpathy-wiki/` is now a symlink to `skills-USER/karpathy-wiki/`
- Removed duplicate files from `ante-preview/modules/karpathy-wiki/`
- All installation logic consolidated from `install.sh` into `setup.sh`

### Fixed
- Hardcoded `/home/cheta/git/ClawMem/bin/clawmem` paths in all 8 MCP registration functions → dynamic resolution via `command -v` + `$CLAWMEM_BINARY` fallback
- AGENTS_WIKI.md source path in `setup.sh` was `../wiki/AGENTS_WIKI.md` (non-existent) → now checks multiple sources + generates default fallback
- `CANONICAL_DIR` symlink resolution: `pwd` → `pwd -P` so physical path is used
- systemd `ExecStart` had shell quotes that would produce literal-quote argv on systemd's parser
- `config.schema.yaml` and `plugin.json` had hardcoded `/home/cheta/` paths → changed to `~/`
- Cleaned up empty scaffolding dirs (`templates/`, `scripts/`, `skills/`)

### Removed
- Empty `templates/`, `scripts/`, `skills/` directories (leftover scaffolding)
- Duplicate content in `ante-preview/`
