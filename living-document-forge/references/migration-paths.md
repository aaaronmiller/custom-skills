---
title: Living Document migration paths
version: 2.1.0
---

# Migration paths

Before broad migration work, read `references/format-continuity.md`. If a workspace has more than one living document, locate or create `living-documents-index.json` before changing files.

## 2.0.0 manifest to 2.1.0 collaboration manifest

This is an additive migration.

1. Read `public/content/index.json`.
2. Set `meta.compatibility.formatVersion` to `2.1.0`.
3. Set `meta.compatibility.skillRange.min` to the current skill version or newer project minimum.
4. Add `"modelReplies": []` if missing.
5. Add `"resources": []` if missing.
6. Add `MODEL_START_HERE.md` and `READER_START_HERE.html` at the document root if missing.
7. Append a history event with `kind: "migration"`.
8. Append a worklog entry if the migration is agent-authored.
9. Do not rewrite section Markdown, proposals, annotations, releases, or existing history.
10. Update `living-documents-index.json` if the document is registered.

## 0.3.x monolith to 2.1.0 manifest

Older documents store prose directly in `public/content.json` under `sections[].markdown`.

Migration:

1. Copy the project before changes.
2. Create `public/content/sections/`.
3. For each section, write `sections/<index>-<id>.md` with YAML frontmatter and the former Markdown body.
4. Replace `markdown` with `source` in each section record.
5. Move the manifest to `public/content/index.json`.
6. Add `navigation`, `dashboard`, `releases`, `history`, and `visual` blocks.
7. Preserve proposals and worklogs exactly.
8. Move annotations to `public/data/annotations.json` if necessary.
9. Set `meta.compatibility.formatVersion` to `2.1.0` and update the skill range.
10. Add empty `modelReplies` and `resources` arrays unless the source document already has equivalent records.
11. Append a migration history event and worklog entry.
12. Run validation and compare rendered content against the original.
13. Update `living-documents-index.json` if the document is registered.

## Registry update after any migration

For each migrated document:

1. Update `formatVersion`.
2. Update `contentVersion` if the migration changes document content or compatibility.
3. Set `lastValidatedAt`.
4. Set `lastValidation` to passed, failed, skipped, or unvalidated.
5. Set `lastMigration` with source format, target format, timestamp, actor, and validation command.
6. Mark documents that cannot migrate as `blocked` with notes.

Do not delete the old file until the new project validates and the user authorizes cleanup.

## Skill newer than document

If the skill is beyond `skillRange.max`, read this file, perform the narrowest migration, and preserve a backup.

## Skill older than document

Warn the user. Do not make destructive changes or guess at unknown fields.
