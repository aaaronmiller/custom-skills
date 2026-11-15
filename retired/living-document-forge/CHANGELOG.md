---
title: Living Document Forge changelog
version: 1.3.0
---

# Changelog

## 1.3.0 - 2026-07-14

- Added the dependency-free `ld` command for idempotent monthly living-document routing.
- Added explicit universal and project scopes plus automatic Git-root detection.
- Added non-destructive month rollover with continuity metadata and current pointers.
- Added atomic central-registry updates and archive status for superseded monthly records.
- Added deterministic CLI tests covering universal, project, idempotence, and rollover behavior.
- Added a concise, executable system-prompt follow clause with trigger and failure semantics.
- Corrected the default standalone destination to `/home/cheta/code/living-documents`.

## 1.2.1 - 2026-07-09

- Added `references/format-continuity.md` to define legacy support, migration patches, and batch upgrade workflow.
- Added a central registry template at `templates/registry/living-documents-index.template.json`.
- Added `schemas/living-documents-index.schema.json`.
- Updated migration guidance to require registry updates after document migrations.
- Clarified that format evolution must either support legacy schemas or patch legacy documents forward.

## 1.2.0 - 2026-07-09

- Changed the primary lifecycle from "export after conversation" to "invoke the skill, then use the living document during the conversation."
- Added `references/conversation-lifecycle.md` for asynchronous human/model collaboration.
- Added `modelReplies` to the manifest for model questions, options, custom-answer routes, and non-blocking clarification queues.
- Added `resources` to the manifest for images, video, audio, links, documents, data files, archives, binaries, and arbitrary extensions.
- Added quote-preserving selection annotations in the reference shell.
- Added `MODEL_START_HERE.md` and `READER_START_HERE.html` at package and document roots.
- Added `templates/content-input/content-plan.template.json`, `templates/content-input/section.template.md`, and `schemas/content-plan.schema.json`.
- Bumped the document format to `2.1.0` with additive migration guidance from `2.0.0`.

## 1.1.0 - 2026-07-09

- Restored `RAISON_DETRE.md` as the first-class entry point for the skill package and every generated document.
- Re-centered the concept around browser-native, human-paced review of agent output rather than a generic dashboard application.
- Added the conversation-export workflow for materializing findings as a complete `.livingdoc/` folder.
- Added `references/conversation-export.md` to define how conversation findings map into Markdown sections, manifest records, annotations, proposals, releases, history, and worklogs.
- Clarified that Karpathy-style LLM wikis are siblings optimized for settled-knowledge retrieval, while living documents are optimized for unsettled refinement, review, sleep-state iteration, and decision history.
- Clarified that `.livingdoc/` folders are the canonical working form and archives are distribution snapshots.
- Reduced package duplication by keeping one shared app template, one reference living document, and one blank content profile.
- Applied the frontend-design-masterclass direction to the template.

## 1.0.0 - 2026-07-09

- Replaced the monolithic `public/content.json` assumption with a manifest plus external Markdown section files.
- Added a complete dependency-free reference application and a neutral blank-content profile.
- Added dashboard, section index, history, changelog, search, command palette, quick edit, local drafts, undo/redo, annotations, decision queue, exports, focused reading mode, and responsive drawers.
- Added five themes with dark-first defaults and a persistent theme selector.
- Added JSON schemas, scaffold tooling, validation, and reference-implementation tests.

## 0.3.0 - 2026-07-07

- Initial living-document maintenance and revision skill.
