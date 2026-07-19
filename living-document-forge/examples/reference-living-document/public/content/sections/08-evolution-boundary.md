---
id: evolution-boundary
title: The portable starter is a floor, not a ceiling
updated: 2026-07-09
---

## What belongs in extensions

The dependency-free starter proves the information architecture and interaction contract. Projects can extend it with:

- authenticated canonical saves;
- version-control commits;
- collaborative presence;
- paragraph-level anchors;
- semantic search and relationship graphs;
- model-assisted proposal generation;
- resource previews and attachment ingestion;
- automated evaluation or policy checks.

These features should arrive through explicit adapters and migrations. They should not be hidden inside the starter as remote calls, undeclared storage, or credentials exposed to the browser.

## Preserve the portable core

Even after a project moves to SvelteKit and Hono, the manifest and Markdown should remain inspectable. A server outage must not make the document unintelligible. An agent should be able to open the repository, read the reason for existence, locate a section, and understand the revision protocol without launching the interface.

The working artifact should remain a folder. A `.livingdoc/` directory can behave like a document package by convention, while still staying searchable, diffable, and editable on every platform. Zip archives and `.skill` files are release formats. They should not become the day-to-day source of truth.

## The next design question

The most consequential unresolved choice is canonical persistence for collaborative deployments. File commits provide excellent diffs, object storage provides simple immutable versions, and a database supports queries and concurrency. The correct answer depends on whether the document is primarily a repository artifact, a published knowledge product, or a multi-user application.

That question belongs in a proposal and experiment, not in an accidental implementation detail.
