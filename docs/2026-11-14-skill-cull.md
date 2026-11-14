---
title: custom-skills cull and description rewrite
date: 2026-11-14
criteria: operator's standard (agents prompt-corpus line 200): "shit" = useless / one-time / non-complex / no universal utility, combined with short, single-pass, no references, bad description. Read each SKILL.md in full; compare with the S-tier skills in master-user-skills.
usage-source: Skill-tool and slash invocations across /home/cheta/.claude/projects (1.1 GB, all Claude Code transcripts)
---

# custom-skills cull, 2026-11-14

Verdicts: KEEP, MERGE (into the named skill), CUT (deleted; git history holds it).

| Skill | Uses | Verdict | Why |
|---|---|---|---|
| examine-documents | 0 | CUT | A five-step "read, cross-reference, cite" procedure any model follows from a one-line prompt; no references or tooling. |
| reply-ledger | 0 | KEEP | Documents a running Stop-hook tool with script and tests. |
| skillranker | 0 | KEEP | Operating notes for the `sr` CLI the system prompt points at. |
| spec-audit | 0 | KEEP | Backtranslation audit with five references; the post-hoc half of spec-prep. |
| research-macbook | 0 | CUT | Hermes cron job dressed as a skill; body pasted four times; one-off eBay search config. |
| imagegen | 7 | KEEP | Keyless image CLI with backends and verified quirks. |
| browser | 0 | KEEP | Engine ladder over four local CLIs with escalation rules and a bundled script. |
| bypass-paywall | 0 | KEEP | Route catalog plus URL builder and a completeness check; more than a prompt. |
| casr | 8 | KEEP | Operating manual for the private casr fork; used. |
| portfolio-lineage | 0 | KEEP | Clause comparison and archive gate with scripts and 14 tests; feeds project-archive. |
| harness-config-audit | 0 | KEEP | Binary-first config audit plus the model-assignment policy reference. Description was 993 characters. |
| notes-sweeper | 0 | KEEP | Notepad/Notepad++ recovery and library build with two scripts and a rubric. |
| black-magic | 9 | KEEP | The intent-first loop behind the BLOCKING GATE; used. Its muse tier and `cass index` advice are stale (cass indexes muse since 2026-09-18; use cass-reindex). |
| intent-organizer | 0 | KEEP | Folder declutter pipeline: 7 scripts, 3 briefs, an approval page and undo. |
| intent-refresh | 0 | KEEP | The current intent pipeline (phases 07-12) that the weekly cron and intent-find depend on. |
| intent-archaeology | 0 | CUT | Older generation of intent-refresh: same job, its own state.db and wiki. intent-refresh calls this pipeline legacy. |
| make-it-funny | 0 | KEEP | Operator-made satire generator with three format references. Absorbs is-it-funny-refinement as `references/evaluate.md`. |
| is-it-funny-refinement | 0 | MERGE into make-it-funny | The scoring half of the same job; one comedy skill, not two. |
| living-document-forge | 0 | CUT | July 2026 browser-shell generation of living documents, superseded by the living-documents system (ld CLI, dossiers, LD reader). Two skills claiming "living documents" is the confusion. |
| skill-creator | 0 | CUT | Copy of Anthropic's skill-creator with only a tags line changed; the official plugin and anthropic-skills already provide it. |
| skill-doctor | 0 | KEEP | Transcript-based skill grading with scorers, scripts and tests; different job from skill-audit (static). |
| refinement-loop | 0 | KEEP | Generate-critique-revise to a rubric threshold, five references; iterative, where deliberative-refinement is a council. |
| mechanism-forge | 0 | CUT | Project-specific to Culture Foundry (now emergence_foundry, which has its own mechanic-foundry); no general use. |
| proven-better-new | 0 | KEEP | Idea validation with mandatory prior-art research and a fixed output card. |
| session-cleanup | 0 | KEEP | Two-pass close-out with three scripts and a cross-session survey. |
| project-archive | 0 | KEEP | Archive pipeline with consumer check, recovery test and tests. |
| damage-control | 0 | CUT | Installer cookbook for a third-party hook system that is not wired into settings.json. |
| system-checkup | 0 | KEEP | Eight-phase workstation checkup with collectors, approval page and removal script. |
| capacity-watch | 0 | KEEP | Quota and model-routing system with scripts, dashboard and tests. |
| motion-lab | 0 | KEEP | Frame-exact motion rendering with a render contract and scripts. |
| deep-research | 0 | KEEP | Parameterized web research with verification passes and templates. |
| game-mechanics-design | 0 | KEEP | Coherent twelve-pillar design framework with checklists; borderline, kept for the game projects. |
| competition-analysis | 0 | KEEP | Competitor dossier procedure with evidence rules and refresh. |
| multi-transcript-synthesis | 0 | CUT | Predecessor of spec-prep's intake: transcripts to requirements and design. |
| cli-tui-styling | 0 | KEEP | Terminal styling guide with five references. |
| build-with-agent-team | 0 | CUT | Imported Agent Teams recipe; duplicated by native agent teams, oh-my-claudecode team and clawteam. |
| assignment-librarian | 0 | KEEP | Maintains LIVING_DOCUMENTS/new_assignments (45 entries) with a scan script. |
| mcp-toolkit | 0 | KEEP | MCP build and convert gates with scripts. |
| rules-file-optimizer | 0 | KEEP | Measured rules-file compression with three scripts. |
| aaron-job-search | 0 | KEEP | Personal job hunt with tracker data and hunt history. |
| agy-headless-driver | 0 | KEEP | agy delegation driver with budget script and templates. |
| cass-cli | 3 | KEEP | Session search manual; used. Its "muse is not indexed" section is stale. |
| git-audit-sync | 2 | KEEP | Repo audit and safe sync script; used. |
| weekly-report-suite | 2 | KEEP | Weekly report generator with six scripts; used. |
| yt-transcript-artifact | 0 | KEEP | Transcript to Obsidian note with extractor, validator and tests. |
| spec-prep, skill-audit | 3, 0 | KEEP | Current spec and skill tooling (spec-prep replaced strata). |
| create-viral-content, deliberative-refinement, humanize-writing, ui-ux-doctor | 0-6 | KEEP, de-duplicated | Each existed twice: a stale copy in its own repo and a newer copy here. The newer copy went into its own repo and this folder now links to it, as frontend-design-masterclass already did. |
| frontend-design-masterclass, living-documents, hallmark | 8, 0, 0 | KEEP | Links to their own repos. |
| erotic-seduction | 0 | KEEP, fixed | Operator restored it on 2026-08-24 (9f2914e), but at `erotic-seduction/erotic-seduction/`, where no harness loads it. Flattened. |
| strata | 0 | CUT | No SKILL.md (only `strata.SKILL`); the old generation of spec-prep, per the operator. |

## Also removed

- `staged-for-deletion/` (17 superseded skill versions, staged since August), `inactive/`, `dist/` (stale packaged builds), `recovered-orphans/` (old copies of graphify and gstack's connect-chrome, both installed from upstream).
- Root clutter: two `slashcommand-*.md` copies of skills, `custom-skills-files-path.md` (a tree dump). The packaging and submission guides moved to `docs/`.
- The already-deleted `macbook-analyzer-pipeline` (Hermes cron skill) is committed as deleted.

## Result

55 skill folders became 45 skills. Every description is one to three sentences; the longest custom one is 244 characters (was up to 1,013).
