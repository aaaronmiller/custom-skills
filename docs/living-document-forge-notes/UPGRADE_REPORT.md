---
title: Living Document Forge 1.2.1 upgrade report
version: 1.2.1
status: complete
---

# Upgrade report

## Executive verdict

Version 1.2 fixes the remaining lifecycle error. The skill no longer assumes the human has already finished a long conversation before invoking it. The intended flow is: invoke the skill, conduct the conversation, let the living document carry state, and export or update files as the work evolves.

The package is now organized around a simple contract: the model writes Markdown sections and structured JSON; the browser shell wraps that content with navigation, search, themes, annotations, model replies, resources, proposals, history, changelog, quick edits, and exports.

## What changed

### 1.2.1 continuity additions

- Added a central registry template for workspaces with multiple living documents.
- Added a registry schema so future agents can validate the index.
- Added a format continuity policy: support legacy schemas or provide migration patches.
- Updated migration paths to include registry updates and blocked-document handling.

### 1.2.0 lifecycle additions

- Added `references/conversation-lifecycle.md` for the ongoing human/model usage story.
- Added `modelReplies` for model-authored questions, options, and custom-answer routes.
- Added `resources` for arbitrary media, attachments, data files, links, archives, binaries, and unknown extensions.
- Added quote-preserving selection annotations to the reference shell.
- Added `MODEL_START_HERE.md` and `READER_START_HERE.html`.
- Added model-facing content templates for section titles, content paths, resources, annotations, and model replies.
- Bumped the manifest format to `2.1.0` and documented additive migration from `2.0.0`.

## Design posture

The default visual direction remains an editorial workbench:

- document-first center canvas;
- persistent section index;
- contextual inspector;
- dashboard widgets only where they answer operational questions;
- five complete themes: system, obsidian, graphite, paper, and high contrast;
- semantic theme tokens;
- local font stack with no hosted assets;
- tokenized microanimations for state feedback;
- reduced-motion support.

This intentionally avoids making the tool itself the topic. The user's findings belong in Markdown sections; the living-document machinery stays in the shell, manifest, annotations, replies, resources, and worklogs.

## Validation completed

- `node scripts/validate-skill.mjs`
- `node scripts/validate-living-document.mjs examples/reference-living-document`
- `node examples/reference-living-document/validate.mjs`
- `node --check examples/reference-living-document/public/app.js`
- `node --check templates/app/public/app.js`
- blank scaffold smoke test into a temporary `.livingdoc/` folder

## Known boundary

The static shell supports local section drafts, selection annotations, proposal decisions, model reply display, and resource listing. It does not yet provide a server-backed canonical save route or true paragraph-level persistent IDs. Those belong in a future adapter or format migration.
