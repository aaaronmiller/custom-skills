---
title: Living Document revision playbook
version: 2.0.0
---

# Revision playbook

## Read before writing

For a scoped revision, read:

1. `RAISON_DETRE.md`;
2. `public/content/index.json`;
3. targeted section Markdown;
4. annotations attached to the target or document;
5. relevant proposals and their decisions;
6. recent history, release notes, and worklogs;
7. attached evidence explicitly referenced by the request.

Do not read every resource merely because it exists. Do not skip relationship metadata merely because the prose change appears small.

## Classify incoming material

Extract and classify:

- established claim;
- hypothesis;
- implementation candidate;
- direct edit;
- objection;
- evidence;
- rejected direction;
- deferred direction;
- proposed experiment;
- interface requirement;
- destructive request.

Place each idea in the narrowest durable target. Add a section only when it has an independent reasoning path, annotation surface, or likely revision history.

## Surgical application

- Preserve unrelated wording.
- Keep section IDs when renaming or reordering.
- Update `source` only when a Markdown file moves.
- Update dependencies and backlinks when relationships change.
- Preserve rejected and deferred proposals.
- Treat browser drafts as complete local replacements for their targeted fields, not as canonical source until applied.
- Record model-authored changes in history and worklog.
- Add new proposals only when a real alternative remains.

## Proposal discipline

A useful proposal:

- expresses one change;
- names target IDs;
- explains practical effect;
- estimates impact and effort;
- can be approved, deferred, or rejected independently.

Do not propose generic “improve UX,” “add AI,” or “make it scalable” items.

## Visual revisions

Before changing UI files, read `interface-design-system.md`, `interaction-model.md`, and `visual-refactor.md`.

A visual change must identify:

- communication goal;
- selected direction;
- affected views and controls;
- theme behavior;
- motion behavior;
- narrow-layout behavior;
- accessibility consequences.

Do not rewrite canonical prose during a visual-only refactor.

## Validation sequence

1. Parse JSON.
2. Validate stable and unique IDs.
3. Verify section ordering and source paths.
4. Verify dependencies, backlinks, proposal targets, and annotation targets.
5. Run JavaScript syntax checks.
6. Run project and skill validators.
7. Serve the reference app and fetch the shell, manifest, and at least one Markdown source.
8. Inspect themes, keyboard behavior, dialogs, exports, and narrow layouts when browser tooling is available.
9. State any unperformed browser checks honestly.

## Destructive changes

Before deleting or renaming a stable target:

- verify explicit authority;
- search inbound references;
- assess historical value;
- prefer deprecation or consolidation where appropriate;
- create a redirect or migration when identity changes;
- record the action in history, release notes if reader-visible, and worklog;
- validate again.
