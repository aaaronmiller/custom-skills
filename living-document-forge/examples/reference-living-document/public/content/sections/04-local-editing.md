---
id: local-editing
title: Quick edits are visible overlays
updated: 2026-07-09
---

## Convenience without pretending

A browser can edit a section immediately, but a static browser cannot safely rewrite repository files. The reference implementation therefore treats quick edits as a local overlay.

The interface labels the draft, persists it in local storage, and keeps the canonical Markdown in memory. The operator can undo, redo, discard, export the merged document, or create a bounded change request for an agent or server-backed workflow.

This is more honest than a “Save” button that changes only an invisible browser cache while implying the project itself has been updated.

## The safe bridge back to source

A change request contains:

- the document ID and base version;
- targeted section IDs;
- changed titles, decks, tags, status, and Markdown;
- proposal decisions;
- local annotations;
- immutable constraints;
- expected output files and validation commands.

A server-backed version may apply the same payload through an authenticated route. It should use optimistic concurrency, validate the schema, append history, and reject stale base versions instead of silently overwriting another revision.

## Reversibility is part of the interface

Undo and redo are not luxuries in a living document. They are proof that the system distinguishes experiment from commitment. Local history records meaningful actions so a browser session can explain what it changed before export.
