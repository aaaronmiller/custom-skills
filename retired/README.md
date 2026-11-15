---
id: retired-custom-skills
title: Retired custom skills, restored for review
type: index
updated: 2026-11-14
---

# Retired custom skills

Every custom skill ever removed from this repo, restored from git history for the operator to review. The operator asked for this on 2026-11-14: "all the custom skills removed should be put in a folder for user review later - obtain them from earlier commits if necessary." These are user-made skills, so each probably had a reason to exist. Nothing here is deployed: skillshare deploys from its own source folder, and no harness scans this repo.

Each entry is the last version before its deletion, at its original path. `.manifest.tsv` has the raw restore record. Rebuild with `git archive <commit>^ -- <path>`.

Not restored, because a current version is still live: create-viral-content, deliberative-refinement, humanize-writing, frontend-design-masterclass and ui-ux-doctor (now symlinks to master-user-skills), spec-prep and erotic-seduction (nested copies flattened in place). Two nested folders come inside their parents: `karpathy-wiki/karpathy-wiki/skill` and the `mine` skill inside `userprompt-mine-skill`.

Five cut skills also sit untracked at the repo top level, re-created on disk at 03:24 to 03:27 on 2026-11-14, minutes after the cull commit: build-with-agent-team, damage-control, examine-documents, multi-transcript-synthesis and skill-creator. Their origin is unknown, and they were left untouched.

## Skill folders (36)

| Path in retired/ | Removed in | Why it was removed |
|---|---|---|
| `build-with-agent-team` | 5a603bb 2026-11-14 | CUT: Imported Agent Teams recipe; duplicated by native agent teams, oh-my-claudecode team and clawteam. |
| `damage-control` | 5a603bb 2026-11-14 | CUT: Installer cookbook for a third-party hook system that is not wired into settings.json. |
| `examine-documents` | 5a603bb 2026-11-14 | CUT: A five-step "read, cross-reference, cite" procedure any model follows from a one-line prompt; no references or tooling. |
| `intent-archaeology` | 5a603bb 2026-11-14 | CUT: Older generation of intent-refresh: same job, its own state.db and wiki. intent-refresh calls this pipeline legacy. |
| `is-it-funny-refinement` | 5a603bb 2026-11-14 | MERGE into make-it-funny: The scoring half of the same job; one comedy skill, not two. |
| `living-document-forge` | 5a603bb 2026-11-14 | CUT: July 2026 browser-shell generation of living documents, superseded by the living-documents system (ld CLI, dossiers, LD reader). Two skills claiming "living documents" is the confusion. |
| `macbook-analyzer-pipeline` | 5a603bb 2026-11-14 | Hermes cron skill, already deleted from disk; the cull committed the deletion. |
| `mechanism-forge` | 5a603bb 2026-11-14 | CUT: Project-specific to Culture Foundry (now emergence_foundry, which has its own mechanic-foundry); no general use. |
| `multi-transcript-synthesis` | 5a603bb 2026-11-14 | CUT: Predecessor of spec-prep's intake: transcripts to requirements and design. |
| `recovered-orphans/graphify` | 5a603bb 2026-11-14 | Old copy of graphify; installed from upstream. |
| `recovered-orphans/gstack-connect-chrome` | 5a603bb 2026-11-14 | Old copy of gstack connect-chrome; gstack is installed from upstream. |
| `research-macbook` | 5a603bb 2026-11-14 | CUT: Hermes cron job dressed as a skill; body pasted four times; one-off eBay search config. |
| `skill-creator` | 5a603bb 2026-11-14 | CUT: Copy of Anthropic's skill-creator with only a tags line changed; the official plugin and anthropic-skills already provide it. |
| `staged-for-deletion/backtranslation-spec-auditor--v2.1.0-superseded-by-v2.2.0` | 5a603bb 2026-11-14 | Staged for deletion earlier, with the reason in its folder name: v2.1.0 superseded by v2.2.0 |
| `staged-for-deletion/backtranslation-spec-auditor-v2.2.0--merged-into-spec-workflow` | 5a603bb 2026-11-14 | Staged for deletion earlier, with the reason in its folder name: merged into spec workflow |
| `staged-for-deletion/create_new_spec_design_project--merged-into-spec-workflow` | 5a603bb 2026-11-14 | Staged for deletion earlier, with the reason in its folder name: merged into spec workflow |
| `staged-for-deletion/deprecated-spec-prep--100pct-trigger-dupe-of-spec-prep-authoring` | 5a603bb 2026-11-14 | Staged for deletion earlier, with the reason in its folder name: 100pct trigger dupe of spec prep authoring |
| `staged-for-deletion/intent-archaeology--old-96line-pipeline` | 5a603bb 2026-11-14 | Staged for deletion earlier, with the reason in its folder name: old 96line pipeline |
| `staged-for-deletion/living-documents--stale-vault-copy-2026-08-14` | 5a603bb 2026-11-14 | Staged for deletion earlier, with the reason in its folder name: stale vault copy 2026 08 14 |
| `staged-for-deletion/mcp-builder--merged-into-mcp-toolkit` | 5a603bb 2026-11-14 | Staged for deletion earlier, with the reason in its folder name: merged into mcp toolkit |
| `staged-for-deletion/mcp-conversion--merged-into-mcp-toolkit` | 5a603bb 2026-11-14 | Staged for deletion earlier, with the reason in its folder name: merged into mcp toolkit |
| `staged-for-deletion/skill-audit-skill--now-sourced-from-quartermaster` | 5a603bb 2026-11-14 | Staged for deletion earlier, with the reason in its folder name: now sourced from quartermaster |
| `staged-for-deletion/spec-prep-implementing--merged-into-spec-prep` | 5a603bb 2026-11-14 | Staged for deletion earlier, with the reason in its folder name: merged into spec prep |
| `staged-for-deletion/spec-workflow--superseded-by-spec-prep-2.4.0` | 5a603bb 2026-11-14 | Staged for deletion earlier, with the reason in its folder name: superseded by spec prep 2.4.0 |
| `staged-for-deletion/speckit-autonomous-run--merged-into-spec-workflow` | 5a603bb 2026-11-14 | Staged for deletion earlier, with the reason in its folder name: merged into spec workflow |
| `staged-for-deletion/userprompt-mine-skill--payload-folded-into-intent-archaeology` | 5a603bb 2026-11-14 | Staged for deletion earlier, with the reason in its folder name: payload folded into intent archaeology |
| `staged-for-deletion/youtube-transcript-extraction--merged-into-yt-transcript-artifact` | 5a603bb 2026-11-14 | Staged for deletion earlier, with the reason in its folder name: merged into yt transcript artifact |
| `staged-for-deletion/yt-transcript-obsidian-artifact--merged-into-yt-transcript-artifact` | 5a603bb 2026-11-14 | Staged for deletion earlier, with the reason in its folder name: merged into yt transcript artifact |
| `git-audit-sync/living-document-forge` | 272fcb6 2026-11-10 | Stray nested copy of living-document-forge inside git-audit-sync. |
| `intent-archaeology-v1.2.1` | 1fa3155 2026-08-22 | Commit message: "consolidate colliding skills: 39 active -> 30" |
| `generate-images-with-gemini` | 9774c14 2026-07-19 | Commit message: "chore: publish current custom skills checkpoint" |
| `spec-audit-skill` | 9774c14 2026-07-19 | Commit message: "chore: publish current custom skills checkpoint" |
| `satirical-media-generator` | a1e7457 2026-06-21 | Commit message: "chore: pending skill updates" |
| `karpathy-wiki` | d92b8d2 2026-06-20 | Commit message: "Consolidate spec-audit skills, remove karpathy stub, fix dangling refs" |
| `spec-audit-skill-v2` | d92b8d2 2026-06-20 | Commit message: "Consolidate spec-audit skills, remove karpathy stub, fix dangling refs" |
| `spec-audit-skill-v3` | d92b8d2 2026-06-20 | Commit message: "Consolidate spec-audit skills, remove karpathy stub, fix dangling refs" |

## Packaged skills (38)

Zipped `.skill` and `.SKILL` bundles from `dist/`, `inactive/`, `web_skill_files/` and two skill folders. Unzip one to read it.

| Path in retired/ | Removed in | Why it was removed |
|---|---|---|
| `dist/deep-research.skill` | 5a603bb 2026-11-14 | KEEP: Parameterized web research with verification passes and templates. |
| `dist/humanize-writing.skill` | 5a603bb 2026-11-14 | Stale packaged build, cleared with `inactive/` and `dist/` in the cull. |
| `dist/is-it-funny-refinement.skill` | 5a603bb 2026-11-14 | MERGE into make-it-funny: The scoring half of the same job; one comedy skill, not two. |
| `dist/make-it-funny.skill` | 5a603bb 2026-11-14 | KEEP: Operator-made satire generator with three format references. Absorbs is-it-funny-refinement as `references/evaluate.md`. |
| `dist/spec-prep-2.4.0.skill` | 5a603bb 2026-11-14 | Stale packaged build, cleared with `inactive/` and `dist/` in the cull. |
| `inactive/SKILL files/auditing-ui-ux.skill` | 5a603bb 2026-11-14 | Stale packaged build, cleared with `inactive/` and `dist/` in the cull. |
| `inactive/SKILL files/backtranslation-spec-auditor-v2.2.0.skill` | 5a603bb 2026-11-14 | Stale packaged build, cleared with `inactive/` and `dist/` in the cull. |
| `inactive/SKILL files/backtranslation-spec-auditor.skill` | 5a603bb 2026-11-14 | Stale packaged build, cleared with `inactive/` and `dist/` in the cull. |
| `inactive/SKILL files/cli-tui-styling.skill` | 5a603bb 2026-11-14 | KEEP: Terminal styling guide with five references. |
| `inactive/SKILL files/create-new-project.skill` | 5a603bb 2026-11-14 | Stale packaged build, cleared with `inactive/` and `dist/` in the cull. |
| `inactive/SKILL files/create-viral-content.skill` | 5a603bb 2026-11-14 | Stale packaged build, cleared with `inactive/` and `dist/` in the cull. |
| `inactive/SKILL files/deep-research.skill` | 5a603bb 2026-11-14 | KEEP: Parameterized web research with verification passes and templates. |
| `inactive/SKILL files/deliberative-refinement.skill` | 5a603bb 2026-11-14 | Stale packaged build, cleared with `inactive/` and `dist/` in the cull. |
| `inactive/SKILL files/examine-documents.skill` | 5a603bb 2026-11-14 | CUT: A five-step "read, cross-reference, cite" procedure any model follows from a one-line prompt; no references or tooling. |
| `inactive/SKILL files/frontend-design-masterclass.skill` | 5a603bb 2026-11-14 | Stale packaged build, cleared with `inactive/` and `dist/` in the cull. |
| `inactive/SKILL files/game-mechanics-design.skill` | 5a603bb 2026-11-14 | KEEP: Coherent twelve-pillar design framework with checklists; borderline, kept for the game projects. |
| `inactive/SKILL files/generate-images-with-gemini.skill` | 5a603bb 2026-11-14 | Stale packaged build, cleared with `inactive/` and `dist/` in the cull. |
| `inactive/SKILL files/humanize-writing.skill` | 5a603bb 2026-11-14 | Stale packaged build, cleared with `inactive/` and `dist/` in the cull. |
| `inactive/SKILL files/intent-archaeology.skill` | 5a603bb 2026-11-14 | CUT: Older generation of intent-refresh: same job, its own state.db and wiki. intent-refresh calls this pipeline legacy. |
| `inactive/SKILL files/is-it-funny-refinement.skill` | 5a603bb 2026-11-14 | MERGE into make-it-funny: The scoring half of the same job; one comedy skill, not two. |
| `inactive/SKILL files/make-it-funny.skill` | 5a603bb 2026-11-14 | KEEP: Operator-made satire generator with three format references. Absorbs is-it-funny-refinement as `references/evaluate.md`. |
| `inactive/SKILL files/mcp-builder.skill` | 5a603bb 2026-11-14 | Stale packaged build, cleared with `inactive/` and `dist/` in the cull. |
| `inactive/SKILL files/mcp-conversion.skill` | 5a603bb 2026-11-14 | Stale packaged build, cleared with `inactive/` and `dist/` in the cull. |
| `inactive/SKILL files/multi-transcript-synthesis.skill` | 5a603bb 2026-11-14 | CUT: Predecessor of spec-prep's intake: transcripts to requirements and design. |
| `inactive/SKILL files/satirical-media-generator.skill` | 5a603bb 2026-11-14 | Stale packaged build, cleared with `inactive/` and `dist/` in the cull. |
| `inactive/SKILL files/skill-audit.skill` | 5a603bb 2026-11-14 | Stale packaged build, cleared with `inactive/` and `dist/` in the cull. |
| `inactive/SKILL files/spec-prep.skill` | 5a603bb 2026-11-14 | Stale packaged build, cleared with `inactive/` and `dist/` in the cull. |
| `inactive/SKILL files/speckit-autonomous-run.skill` | 5a603bb 2026-11-14 | Stale packaged build, cleared with `inactive/` and `dist/` in the cull. |
| `inactive/SKILL files/weekly-report-suite.skill` | 5a603bb 2026-11-14 | KEEP: Weekly report generator with six scripts; used. |
| `inactive/SKILL files/youtube-transcript-extraction.skill` | 5a603bb 2026-11-14 | Stale packaged build, cleared with `inactive/` and `dist/` in the cull. |
| `inactive/frontend-design-masterclass.SKILL` | 5a603bb 2026-11-14 | Stale packaged build, cleared with `inactive/` and `dist/` in the cull. |
| `inactive/living-document-forge.skill` | 5a603bb 2026-11-14 | CUT: July 2026 browser-shell generation of living documents, superseded by the living-documents system (ld CLI, dossiers, LD reader). Two skills claiming "living documents" is the confusion. |
| `strata/strata.SKILL` | 5a603bb 2026-11-14 | CUT: No SKILL.md (only `strata.SKILL`); the old generation of spec-prep, per the operator. |
| `spec-prep/spec-prep.SKILL` | 272fcb6 2026-11-10 | Commit message: "spec-prep consolidation (iteration 1) + corpus junk cleanup" |
| `deliberative-refinement/deliberative-refinement.skill` | 706e6b9 2026-10-30 | Commit message: "Remove stale deliberative-refinement.skill 7z (skillshare distributes live files)" |
| `web_skill_files/spec-audit-skill.skill` | 9774c14 2026-07-19 | Commit message: "chore: publish current custom skills checkpoint" |
| `web_skill_files/spec-audit-skill-v2.skill` | b39875b 2026-06-21 | Commit message: "chore: auto-sync local skill changes" |
| `web_skill_files/spec-audit-skill-v3.skill` | b39875b 2026-06-21 | Commit message: "chore: auto-sync local skill changes" |
