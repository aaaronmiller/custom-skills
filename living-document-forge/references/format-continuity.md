---
title: Format continuity and legacy upgrade policy
version: 1.2.1
---

# Format continuity

Living documents are expected to improve over time. The format may add fields, split files, change validation rules, or replace interface conventions. That is acceptable only if legacy documents remain discoverable, migratable, and auditable.

## Core policy

Every format change must choose one of two compatibility strategies:

1. **Support legacy schemas.** The current skill can read older documents and operate with documented feature limits.
2. **Patch legacy documents forward.** The project provides a migration that updates older documents into the current format.

Do not silently strand legacy documents. If a document cannot be migrated safely, mark it `blocked` in the registry with the reason and required human decision.

## Central registry

Maintain a central index of living documents whenever more than one document exists in a workspace or organization.

Recommended location:

```text
living-documents-index.json
```

The registry records:

- document ID;
- title;
- root path or URL;
- current content version;
- format version;
- skill range;
- status;
- owner;
- last validation result;
- last migration applied;
- tags;
- notes.

The registry is not the source of truth for document content. It is the routing layer that lets a future agent find every document that may need validation or migration.

## Format versioning

Use semantic format versions:

- **Patch:** validator wording, documentation, or non-structural clarifications.
- **Minor:** additive fields with safe defaults, such as `modelReplies` and `resources`.
- **Major:** breaking schema, path, identity, or rendering changes.

Examples:

- `2.0.0` to `2.1.0`: additive; add missing arrays and start files.
- `2.x` to `3.0.0`: breaking; requires explicit migration script, backup, validation, and registry update.

## Migration requirements

A migration must define:

- source format range;
- target format;
- files read;
- files written;
- backup strategy;
- exact transformations;
- fields added with defaults;
- fields removed or renamed;
- relationship checks;
- validation commands;
- rollback or recovery path;
- registry update.

Breaking migrations should be implemented as scripts, not prose-only instructions, once the format is used by multiple real documents.

## Batch upgrade workflow

When the format changes:

1. Read `living-documents-index.json`.
2. For each registered document, inspect `public/content/index.json`.
3. Compare `meta.compatibility.formatVersion` with the target format.
4. Select the migration path.
5. Back up or commit the current document state.
6. Apply the migration.
7. Run validation.
8. Append a migration history event and worklog.
9. Update the central registry entry.
10. Report succeeded, skipped, blocked, and failed documents.

If no central registry exists, create one before the next broad migration.

## Legacy support windows

The skill should usually support at least one previous minor format for reading and migration. It may refuse destructive edits against unsupported major versions until migration is complete.

Recommended behavior:

- current minor: operate normally;
- previous minor: migrate or operate with warnings;
- older same major: migrate before editing;
- older major: require explicit migration path;
- newer major: warn and avoid destructive changes.

## Living-document project organization

The Living Document Forge itself should be managed as a living document when the ecosystem grows beyond a single package. That project document should track:

- proposed schema changes;
- migration decisions;
- registry policy;
- interface improvements;
- validation gaps;
- release notes;
- legacy support status.

The format evolves through proposals, migrations, validation, and worklogs, not informal edits scattered across examples.
