---
title: Living Document content model
format-version: 2.1.0
---

# Living Document content model

## Source-of-truth split

A version 2 living document separates content into three layers:

1. `public/content/index.json` stores identity, ordering, relationships, model replies, resources, release history, and rendering metadata.
2. `public/content/sections/*.md` stores prose in stable, diff-friendly files.
3. `public/data/annotations.json` stores target-specific comments without silently merging them into prose.

Browser drafts are overlays. They are not canonical source until exported and applied.

## Top-level manifest

`public/content/index.json` contains:

- `_meta`: machine-readable file identity and schema hint;
- `meta`: document identity and compatibility;
- `navigation`: view and section ordering;
- `dashboard`: focus and health definitions;
- `sections`: section records pointing to Markdown;
- `proposals`: decision-ready candidate changes;
- `releases`: reader-facing changelog;
- `history`: append-only event ledger;
- `visual`: theme and motion defaults;
- `worklogs`: immutable model-authored revision appendices;
- `modelReplies`: model-authored questions, answer options, and clarification requests;
- `resources`: arbitrary attachments, media, links, and evidence files.

## Meta

Required fields:

- `documentId`: permanent kebab-case identity;
- `title`: visible document title;
- `subtitle`: one-sentence purpose;
- `version`: semantic version;
- `updated`: ISO date;
- `status`: exploration, draft, review, stable, archived, or a documented extension;
- `thesis`: central proposition;
- `audience`: intended readers or operators;
- `compatibility.formatVersion`: currently `2.1.0`;
- `compatibility.skillRange.min` and `.max`.

Changing the title does not change `documentId`.

## Navigation

Fields:

- `defaultView`: dashboard, document, history, changelog, or search;
- `sectionOrder`: ordered stable section IDs;
- `quickFilters`: common tag or status filters;
- `showInspector`: default right-panel visibility;
- `showReadingProgress`: whether the progress rail is visible.

Every ID in `sectionOrder` must exist exactly once in `sections`.

## Dashboard

Dashboard content is operational, not a duplicate summary of every section.

- `focus`: the current decision or research priority;
- `health`: named checks with `good`, `attention`, or `blocked` state;
- `metricDefinitions`: optional labels and explanations for computed metrics;
- `pinnedSectionIds`: sections surfaced for immediate work;
- `decisionQueueLimit`: maximum proposals shown before linking to the full list.

Computed values such as section count or open annotations should not be duplicated in JSON.

## Sections

Required fields:

- `id`: stable kebab-case anchor;
- `index`: human-readable sequence label;
- `eyebrow`: compact category;
- `title`: argument-level heading;
- `dek`: concise section purpose;
- `source`: project-relative Markdown path beneath `public/`;
- `tags`: retrieval labels;
- `status`: draft, active, review, stable, deprecated, or archived;
- `editable`: local quick-edit permission;
- `owner`: optional responsible party;
- `updated`: ISO date;
- `estimatedMinutes`: positive integer;
- `dependencies`: section IDs this section relies upon;
- `backlinks`: section IDs that directly discuss or extend it.

Preserve IDs when renaming or reordering. Add redirects during migrations if an ID must change.

## Markdown rules

- Begin each section with YAML frontmatter containing `id`, `title`, and `updated`.
- The first visible heading is normally level two because the application supplies the page title.
- Use relative links and stable section anchors.
- Do not embed scripts, forms, or untrusted HTML.
- Keep one durable concept per file when possible.
- Record citations and provenance in the Markdown or attached resource records.

## Proposals

A proposal contains:

- `id`: permanent address such as `P-001`;
- `title`;
- `summary`;
- `impact`: low, medium, high;
- `effort`: low, medium, high;
- `decision`: proposed, approve, defer, reject, implemented;
- `targetIds`: affected section or document IDs;
- `tags`;
- `createdAt`;
- `updatedAt`.

Rejected proposals remain as negative constraints until explicitly reconsidered.

## Releases

Releases power the changelog. Each release has:

- `version`;
- `date`;
- `title`;
- `summary`;
- `changes`: categorized entries with `type`, `text`, and optional `targetIds`.

Release notes explain reader-visible meaning, not every low-level edit.

## History

History is an append-only event ledger. Each event has:

- `id`;
- `timestamp`;
- `actor`;
- `kind`: create, edit, decision, import, migration, export, agent-run, or extension;
- `summary`;
- `targetIds`;
- `version`;
- `source`: human, agent, system, import;
- optional `details`.

Never rewrite prior events to make the timeline cleaner.

## Worklogs

Worklogs are immutable model revision appendices:

- `id`;
- `version`;
- `date`;
- `agent`;
- `summary`;
- `changed`;
- `validated`;
- `suggested`;
- `warnings`.

A worklog is not a substitute for the release changelog or event history.

## Model replies

`modelReplies` captures model-authored questions, options, and clarification requests that the human can answer later. It is the back-and-forth surface for asynchronous collaboration.

Each model reply includes:

- `id`: stable address such as `MR-001`;
- `prompt`: the question or choice;
- optional `context`: why the answer matters;
- `targetIds`: affected sections, proposals, or document-level targets;
- `status`: open, answered, blocked, or resolved;
- `options`: zero or more answer options, usually including a custom-answer route;
- `createdAt` and `updatedAt`.

Use model replies when the model can continue other work while waiting. Do not stop the whole project just because one reply remains open unless every remaining task depends on it.

## Resources and media

`resources` records all non-section files and external evidence. Supported resource kinds:

- image;
- video;
- audio;
- document;
- data;
- archive;
- binary;
- link;
- other.

Each resource should include:

- `id`;
- `title`;
- `kind`;
- `path` or `url`;
- `originalName`;
- `mimeType` and extension when known;
- optional `sizeBytes` and `sha256`;
- `targetIds`;
- `description`;
- `status`: referenced, available, missing, archived, or unsafe;
- `createdAt`.

Files may have any extension. The manifest records them; the app may preview safe images, video, audio, Markdown, text, CSV, and JSON when supported. Unknown, binary, archive, script, macro, or executable files are listed rather than executed.

## Annotations

`public/data/annotations.json` contains:

- `_meta`;
- `annotations` array.

Each annotation includes:

- `id`;
- `targetId`;
- optional `quote`;
- `kind`: note, question, objection, decision, evidence;
- `text`;
- `tags`;
- `status`: open, resolved, archived;
- `author`;
- `createdAt`;
- optional `files` and `resolvedAt`.
- optional `quote` when created from selected text.

Annotations never merge themselves into section prose.

## Visual settings

`visual` includes:

- `defaultTheme`: `obsidian` by default;
- `themes`: allowed theme IDs;
- `defaultMotion`: system, full, or reduced;
- `density`: comfortable or compact;
- `designDirection`: a named visual concept.

The browser may persist user preferences separately. Do not rewrite canonical defaults merely because one user changes their local theme.

## Local overlay

The reference application stores:

- section drafts keyed by section ID;
- local history events;
- theme, motion, density, and focused-reading preferences;
- temporary undo and redo stacks.

Exports merge the overlay into a generated artifact while preserving the original manifest in memory.

## Change discipline

1. Preserve top-level key order where practical.
2. Use two-space JSON indentation.
3. Avoid unnecessary Unicode escaping.
4. Verify every source file exists.
5. Validate all relationship IDs.
6. Check duplicate IDs across every collection.
7. Search inbound links before deprecation or deletion.
8. Add optional fields in minor format revisions such as `2.1.0`.
9. Increment the major format only for breaking schema changes.
10. Add a migration when moving from monolithic content to external Markdown or when required fields change.
11. Update the central registry template and continuity policy when a format change affects discovery or migration.

## Registry relationship

A living document is self-contained, but a workspace with several living documents should maintain `living-documents-index.json`.

The registry points to each document root and manifest so future agents can:

- find legacy documents;
- compare format versions;
- run migrations in batches;
- record validation status;
- identify blocked documents needing human decisions.

The registry does not replace per-document metadata. It is an index for maintenance, migration, and continuity.
