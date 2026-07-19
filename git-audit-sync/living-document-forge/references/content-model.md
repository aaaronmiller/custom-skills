# Living canvas content model

## Purpose

`public/content.json` is the conceptual source of truth. The HTML shell renders it, local edits overlay it in the browser, and agent revisions write accepted changes back into it. Keep the file human-readable, diff-friendly, and stable across versions.

## Top-level shape

- `meta`: document identity, version, status, thesis, and operator instructions.
- `sections`: ordered concept modules.
- `proposals`: addressable potential changes with decision state.
- `visualRefactor`: explicit visual communication intent.
- `worklogs`: immutable revision appendices.

## Meta

Required fields:

- `documentId`: stable kebab-case identity.
- `title`: display title.
- `subtitle`: concise purpose statement.
- `version`: monotonic semantic or project-specific version.
- `updated`: ISO date.
- `status`: exploration, prototype, review, or other clear state.
- `thesis`: one-paragraph central proposition.

Do not change `documentId` during routine edits. A title change does not require an identity change.

## Sections

Each section contains:

- `id`: unique kebab-case anchor.
- `eyebrow`: compact index and category label.
- `title`: argument-level heading.
- `dek`: concise explanation of the section’s job.
- `markdown`: editable body content.
- `tags`: retrieval and focus filters.
- `media`: optional figures.
- `status`: normally `active`; may be `draft`, `deprecated`, or `archived` if the UI supports it.
- `editable`: whether the local editor exposes the section.

Place a concept in the narrowest existing section that can carry it without becoming incoherent. Add a section when the idea has its own durable decision surface, needs independent annotation, or is likely to evolve separately.

Section order should reflect the reader’s reasoning path, not the chronology of notes. Preserve stable IDs when reordering.

### Media entries

A media item uses:

- `src`: project-relative public path.
- `alt`: description of informational content.
- `caption`: why the image matters to the argument.

Do not use captions as decoration. If an image has no conceptual function, omit it.

## Proposals

A proposal contains:

- `id`: stable ID such as `X-04` or `Y-02`.
- `appendix`: human-readable proposal group.
- `title`: one actionable change.
- `summary`: rationale and intended effect.
- `impact`: low, medium, or high.
- `effort`: low, medium, or high.
- `decision`: approve, defer, or reject.
- `tags`: affected systems.

Proposal IDs are permanent references. Never renumber old proposals when adding new ones. Begin a new alphabetic appendix or continue the existing sequence according to the current project convention.

Decision semantics:

- `approve`: implement during the next authorized revision.
- `defer`: retain without implementation.
- `reject`: do not implement; treat the proposal as a negative constraint until explicitly reconsidered.

## Visual refactor

Fields may include:

- `palette`
- `surface`
- `density`
- `ornament`
- `motion`
- `heroAsset`
- `notes`
- `candidateAssets`

This object is included in change requests. It should describe the intended information hierarchy and interaction language, not only colors.

## Worklogs

Worklogs are append-only. An entry includes:

- `id`
- `version`
- `date`
- `agent`
- `summary`
- `changed`
- `suggested`

Extended entries may add applied proposal IDs, constraints, validations, and warnings. Preserve prior entries exactly unless correcting a proven factual or structural error, in which case add a correction entry rather than erasing history.

## Annotations

Annotations live in `data/annotations.json` rather than the content file. They are not automatically merged into prose. Each annotation has:

- `id`
- `targetId`
- `kind`
- `text`
- `tags`
- `files`
- `author`
- `createdAt`

The target can be a section ID, `document`, `proposal-appendix`, `visual-refactor`, or another stable interface target.

## Change discipline

When applying a revision:

1. Preserve top-level key order where practical.
2. Keep JSON indentation at two spaces.
3. Avoid escaping normal Unicode unnecessarily.
4. Do not store executable JavaScript in content fields.
5. Do not store secrets, raw OAuth tokens, or API keys.
6. Keep content paths relative to `public/` when rendered by the client.
7. Validate unique section and proposal IDs.
8. Ensure every media asset exists.
