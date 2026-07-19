---
id: source-architecture
title: Canonical content stays outside the shell
updated: 2026-07-09
---

## Three layers, three responsibilities

The reference architecture keeps canonical material in files that remain useful without the interface:

1. `content/index.json` carries identity, ordering, relationships, releases, history, and display metadata.
2. `content/sections/*.md` carries the actual argument in small, diff-friendly modules.
3. `data/annotations.json` carries comments and evidence that target the document without silently becoming part of it.

The HTML shell contains landmarks and loading code, not the document’s substantive prose. This makes the content easier to diff, migrate, search, quote, and hand to an agent.

## Stable identity beats file position

A section ID survives title changes and reordering. Navigation order is therefore a list of IDs rather than an inference from filenames. Dependencies and backlinks use the same IDs.

This separation prevents a cosmetic rename from breaking every annotation or proposal. When identity truly must change, the project performs a migration and records the redirect rather than quietly inventing a new object.

## The manifest is not a prose landfill

The manifest should not absorb paragraphs merely because JSON is convenient to fetch. It stores compact structure and relationships. Markdown remains the preferred home for long-form reasoning because it is readable in a text editor, friendly to version control, and straightforward for models to patch surgically.

The browser may export a merged representation for transport, but that generated file is not allowed to erase the source split.

## Wiki sibling, not wiki replacement

An LLM wiki should stay optimized for settled knowledge and retrieval. It wants compact pages, indexes, summaries, and stable definitions. A living document wants active review state: objections, proposals, local drafts, experiments, changelogs, and worklogs.

Those jobs reinforce each other when they remain separate. A wiki can link to a living document when a topic is under active design or debate. A living document can link back to wiki pages for definitions that are no longer contested. Collapsing them into one artifact either bloats retrieval or erases refinement history.
