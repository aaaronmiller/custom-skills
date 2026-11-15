# RAISON D'ETRE: Why Living Documents Exist

This is the first file to read. It states the concept, the operating contract, and the boundary between a living document, a wiki, a chat transcript, and an agent workspace.

## The founding idea

A living document is a browser-native, addressable review surface for asynchronous human-agent collaboration.

It exists because chat is a poor protocol for long-running agent work. Agents can produce thousands of words in seconds. Humans read, compare, annotate, and decide much more slowly. In chat, the human races the next model reply, loses position in the scroll, cannot attach a comment to a durable paragraph, cannot bind a screenshot or video to one proposition, and cannot reliably distinguish what changed across several agent runs.

The problem is not that chat lacks enough buttons. The problem is that chat is linear, ephemeral, synchronous, mostly text-only, and organized around turns. A living document is spatial, persistent, asynchronous, multimedia, and organized around addressable claims, sections, decisions, and history.

The document is therefore not just the output. It is the collaboration protocol.

## What makes it living

A living document preserves the active state around an idea, not only the current prose:

- stable section IDs so humans and agents can point at the same target without racing the scroll;
- annotations attached to sections, paragraphs, media, or proposals;
- proposals that can be approved, rejected, or deferred one by one;
- immutable worklogs that record what an agent changed, validated, skipped, and recommends next;
- changelogs that summarize reader-facing releases separately from granular history;
- media and evidence bound to the exact claim they support;
- visual-refactor objects that make interface intent explicit rather than hiding it in chat;
- structured change requests so an agent edits through a contract, not a vague prompt;
- compatibility metadata so future agents know which document format they are touching.

"Living" does not mean constantly rewritten. It means unresolved state is visible, reviewable, and durable.

## Browser first, terminal second

Models often return blocks of text in places optimized for command output, not human comprehension. Dense terminal scrollback is the wrong surface for reviewing a concept, design, spec, or research argument.

A living document should be read in a browser or similarly rich surface because it needs:

- persistent navigation while the reader moves through history;
- stable anchors and backlinks;
- side-by-side context;
- annotation at human speed;
- visible approval state;
- attached images, videos, audio, and source files;
- search, filters, history, and changelog views;
- local drafts that do not masquerade as committed source.

The terminal remains useful for validation, packaging, tests, and agent execution. It should not be the primary reading surface for large conceptual output.

## Relationship to LLM wikis

Karpathy-style LLM wikis and living documents are siblings, not replacements for each other.

An LLM wiki optimizes for retrieval of settled knowledge:

- compact Markdown;
- stable definitions;
- summary and index files;
- low-friction agent lookup;
- answering "what do we know?"

A living document optimizes for refinement of unsettled work:

- open questions;
- competing proposals;
- annotations and objections;
- sleep-state agent iteration;
- changelog and worklog memory;
- answering "what are we deciding, changing, and learning?"

Turning every wiki page into a living document would usually hurt retrieval. Turning every living document into a wiki page would erase the active review state. The correct architecture is cross-reference:

- wiki pages link to living documents for active debates, design work, or evolving research;
- living documents link to wiki pages for settled definitions, background, and reusable context.

## Relationship to agent workspaces

Modern agent systems increasingly rely on instructions, tools, handoffs, structured outputs, guardrails, approval checkpoints, and traces. A living document gives those mechanisms a human-readable home.

It is not merely "agentic document processing," where agents extract or transform documents. It is a document-shaped agent workspace:

- the document stores targets, constraints, evidence, decisions, and revision history;
- the agent receives bounded change requests instead of a free-form mandate;
- the human reviews proposals and local drafts at human speed;
- the worklog makes agent activity inspectable after sleep-state or long-running refinement.

The living document is the surface where agentic work becomes legible.

## Canonical shape

The canonical working form is a plain folder, not a compressed archive:

```text
example.livingdoc/
  RAISON_DETRE.md
  public/
    index.html
    app.js
    styles.css
    content/
      index.json
      sections/
        *.md
    data/
      annotations.json
  worklogs/
  resources/
```

On macOS, a directory can be presented as a package-like object, but that behavior is not portable to Linux and Windows. Cross-platform tools should treat `.livingdoc/` as a directory with a meaningful extension.

Compression is for transport, not daily use. Zip archives are useful for sharing, installing, and preserving a release snapshot. They are worse for search, diffs, direct editing, and agent utility. Work from the folder; ship the archive when needed.

## Version contract

This file is shared by two things that must stay aligned:

1. the Living Document Forge skill, which teaches agents how to create and maintain living documents;
2. every living document created by that skill, which carries its own copy so future agents can understand it without prior chat context.

The skill declares its version in `VERSION`. A document declares compatibility in `public/content/index.json`:

```json
"compatibility": {
  "formatVersion": "2.1.0",
  "skillRange": {
    "min": "1.2.0",
    "max": "2.0.0"
  }
}
```

Compatibility rules:

```text
If the skill major version is within the document skillRange:
  proceed normally.

If the document format is older than this skill expects:
  run the documented migration path before editing content.

If the skill is older than the document requires:
  warn the human and avoid destructive changes.
```

Pure compatibility migrations update metadata and append a worklog. They do not rewrite section content, proposals, annotations, or historical records.

## The skill is the canonical home

The concept and the skill are linked because the skill is the executable understanding of the concept. The idea says sections need stable IDs; the skill validates stable IDs. The idea says worklogs are immutable; the skill requires append-only worklogs. The idea says agents should operate through structured requests; the skill defines that contract.

The concept should still be readable outside the skill. That is why this file is copied into every generated living document. The skill remains canonical; each document carries a snapshot of the concept for local autonomy.

## How to use this file

If you are a human, read through "Relationship to agent workspaces" before judging the project. The rest is the compatibility contract.

If you are an agent:

1. read this file before editing;
2. inspect `public/content/index.json`;
3. verify the compatibility block;
4. identify the requested targets by stable ID;
5. edit the narrowest files possible;
6. append history and worklog entries;
7. validate before claiming completion.

If you are creating a new living document, copy the document excerpt below to the document root as `RAISON_DETRE.md`.

---

## Document copy

# RAISON D'ETRE: This Living Document

This is a living document: a browser-native, addressable review surface for asynchronous human-agent collaboration.

It exists because chat is the wrong protocol for sustained review. Agents can generate thousands of words in seconds; humans read, compare, annotate, and decide at human speed. In chat, the human races the next reply, loses scroll position, cannot attach durable comments to precise claims, cannot bind media to propositions, and cannot inspect long-running agent work as structured history.

This document is different. It is spatial, persistent, asynchronous, multimedia, and organized around stable sections, proposals, annotations, changelogs, and immutable worklogs.

Core contract:

- stable section IDs make every claim addressable;
- annotations attach review state to exact targets;
- proposals are approved, rejected, or deferred individually;
- worklogs append what agents changed, validated, skipped, and recommend next;
- changelogs summarize meaningful releases separately from granular history;
- local drafts stay visibly local until exported or applied;
- agent handoffs use structured change-request JSON;
- the browser is the primary review surface, while the terminal is for validation and packaging.

This document is a sibling to an LLM wiki, not a replacement for one. Wikis optimize settled knowledge for retrieval. Living documents optimize unsettled work for refinement, review, and decision history. Wikis may link here for active debates; this document may link back to wiki pages for settled definitions.

The canonical working form is a folder, optionally named with a `.livingdoc` suffix. Archives are for distribution, not daily use.

## Version contract

The document declares its format and skill compatibility in `public/content/index.json`. An agent must check that block before making changes. If migration is required, it should follow the migration guide, update metadata narrowly, and append a worklog. Pure migrations must not rewrite content, proposals, annotations, or history.

Raison d'etre means reason for being. This file is the first thing a human or agent should read before operating on the document.
