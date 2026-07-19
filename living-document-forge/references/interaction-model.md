---
title: Living Document interaction model
version: 1.0.0
---

# Interaction model

## Views

### Dashboard

Answers: What is this document, what changed, what is blocked, and where should I work next?

Includes current focus, dynamic counts, health checks, pinned sections, open proposal queue, recent history, and local draft state.

### Document

Answers: What does the document currently say?

Provides stable anchors, section navigation, reading progress, focused reading mode, backlinks, local edit indicators, and contextual inspection.

### History

Answers: What happened, in what order, and who or what caused it?

Displays append-only event entries with filters by event kind, actor, source, version, and target.

### Changelog

Answers: What meaningfully changed in each released version?

Displays release summaries and categorized changes. It is shorter and more editorial than history.

### Search

Answers: Where is a concept discussed?

Searches section titles, decks, tags, and Markdown. Results show context, status, tags, and stable navigation targets.

## Section index

The left rail contains:

- primary view navigation;
- search shortcut;
- status and tag filters;
- ordered sections;
- per-section draft indicator;
- reading completion marker;
- mobile close control.

The active marker follows navigation without causing layout shift.

## Inspector

The right rail changes with context:

- dashboard: decision queue and health details;
- section: metadata, dependencies, backlinks, annotations, and edit controls;
- history: event filters;
- changelog: release navigation;
- search: query guidance and result filters.

At smaller widths it becomes a drawer.

## Quick edit

Quick edit uses a modal dialog with:

- title;
- deck;
- status;
- comma-separated tags;
- raw Markdown;
- save draft;
- discard current draft;
- keyboard shortcut legend.

Saving updates a local overlay, adds a local history event, updates the unsaved counter, and provides undo/redo. It does not silently write the canonical source file.

## Command palette

Open with `Ctrl+K` or `Cmd+K`. Commands include:

- switch view;
- jump to section;
- edit active section;
- toggle focused reading;
- undo or redo;
- change theme;
- export change request;
- open shortcuts.

Filter commands as the user types. Arrow keys move selection, Enter runs, Escape closes.

## Search

- `/` focuses global search outside text inputs.
- Search is case-insensitive.
- Results rank title matches before deck, tags, and body matches.
- Search never mutates content.
- Empty query provides indexed browsing rather than an error state.

## History and changelog

History filters must not change canonical data. Changelog entries link to target sections where IDs are available.

Local history is visibly marked as browser-only until exported or applied.

## Exports

The starter supports:

- merged document JSON;
- combined Markdown;
- change-request JSON containing only local overlays and context.

Generated filenames use document ID, version, and export type. Never include secrets or browser storage unrelated to the current document.

## Keyboard map

- `Ctrl/Cmd+K`: command palette;
- `/`: search;
- `E`: edit active section when focus is not in an input;
- `F`: focused reading;
- `Ctrl/Cmd+Z`: undo local edit;
- `Ctrl/Cmd+Shift+Z`: redo local edit;
- `Escape`: close palette, dialog, or drawer;
- `?`: shortcuts dialog.

Do not intercept shortcuts while the user is typing in a form, except Escape and standard undo/redo inside that form.

## Motion behavior

Motion has three settings:

- `system`: follows `prefers-reduced-motion`;
- `full`: enables restrained transitions unless the platform forces reduction;
- `reduced`: removes nonessential transforms and smooth scrolling.

Theme change can call `document.startViewTransition()` when supported. It must work identically without that API.
