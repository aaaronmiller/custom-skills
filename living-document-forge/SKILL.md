---
name: living-document-forge
description: >-
  Create, redesign, maintain, validate, and package browser-native living
  documents: addressable review surfaces for asynchronous human-agent
  collaboration, with external Markdown sections, annotations, proposals,
  history, changelog, themes, microinteractions, immutable worklogs, and
  controlled agent handoffs. Use for evolving concepts, research dossiers,
  specifications, prompt laboratories, or any document that must remain
  editable, auditable, navigable, and reviewable at human speed.
license: MIT
---

# Living Document Forge

Before operating on any living document, read `RAISON_DETRE.md` if present, then `references/raison-detre.md`. That file is the concept contract. The skill is the executable method.

A living document is a browser-native, addressable review surface for asynchronous human-agent collaboration. It exists because chat is the wrong protocol for sustained conceptual work: agents produce faster than humans can review, terminal output is a poor reading surface, and linear chat history cannot preserve precise annotations, media, proposals, worklogs, and decision state around a large evolving idea.

Do not reduce this to "an interactive document." The document is the coordination protocol.

The skill supports five jobs:

1. scaffold a new living document;
2. revise an existing document without flattening its structure;
3. redesign the interface while preserving content identity and accessibility;
4. package an auditable handoff for humans or coding agents.
5. route work to the current universal or project monthly document through `ld`.

Most common use: a human invokes the skill at the beginning of a substantial exchange and then has a 5-30 turn conversation with the model. The living document should become the working surface for that exchange, not only a final export after the fact. If the human later says, "output your findings in a living document," produce or update the folder-shaped document from the conversation state.

The bundled reference application is dependency-free and intentionally portable. It demonstrates the complete interaction contract while remaining easy to migrate into SvelteKit, Hono, or another host stack. The canonical working artifact is a folder, optionally named with a `.livingdoc/` suffix. Archives are for distribution, not daily editing.

## Operating principles

- Treat external Markdown and structured JSON as the source of truth. HTML is a shell, not a content warehouse.
- Put the reason-for-being first. Every generated document must include `RAISON_DETRE.md` at its root and the browser shell must expose the same concept in metadata or comments.
- Preserve the sibling boundary with LLM wikis: wikis optimize settled knowledge and retrieval; living documents optimize active refinement, review, proposals, sleep-state iteration, changelog, and worklogs.
- Preserve stable IDs for documents, sections, proposals, annotations, releases, history events, and worklogs.
- Preserve format continuity. When schemas improve, either support legacy documents explicitly or migrate them through documented patches.
- Maintain a central living-documents registry when multiple documents exist in a workspace so future migrations can find every legacy document.
- Keep direct human edits distinct from model-authored suggestions.
- Never delete a section, proposal, annotation, or worklog without explicit authorization and inbound-reference checks.
- Use append-only worklogs and event history. Correct history with a new entry rather than rewriting the old one.
- Measure interface quality by orientation, editing confidence, retrievability, and decision clarity, not decorative density.
- Default to dark mode, but ship complete light, monochrome, system, and high-contrast options.
- Motion must provide feedback, orientation, or restrained delight. It must never delay editing or override reduced-motion preferences.
- Validate data, links, assets, keyboard behavior, responsive layout, themes, motion settings, and exports before completion.

## First decision: operation type

Classify the request before touching files:

| Operation | Typical request | Primary action |
|---|---|---|
| Living conversation | “Use this skill while we work through X” | Maintain the document as the asynchronous collaboration surface during the exchange. |
| Conversation export | “Output your findings in a living document” | Convert the current conversation state into a complete living-document folder using Markdown sections and manifest data. |
| Scaffold | “Create a living document” | Run the scaffold workflow and choose blank or reference content. |
| Content revision | “Add these ideas / apply changes 2, 4, 7” | Edit Markdown and structured records surgically. |
| Information architecture | “Reorganize sections / add dashboard” | Update manifest, navigation, backlinks, and views. |
| Visual refactor | “Make it dark / redesign the canvas” | Apply the design-system and interaction references. |
| Workflow extension | “Add quick edit / history / agent handoff” | Extend UI state and schemas without mixing it into prose. |
| Migration | “Update an older living document” | Read compatibility metadata and run the migration path. |
| Registry maintenance | “Index all living documents / prepare for upgrades” | Create or update `living-documents-index.json` and validate migration readiness. |
| Monthly routing | “Use/follow the current living document” | Run `ld ensure`; let it select universal or project scope, create the month when absent, and preserve rollover continuity. |
| Packaging | “Return a skill or project archive” | Validate, assemble, and produce a deterministic archive. |

## Required project contract

A conforming project contains:

```text
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
MODEL_START_HERE.md
READER_START_HERE.html
serve.mjs
package.json
```

Larger projects may split scripts, components, schemas, media, experiments, or API routes, but the canonical content must remain inspectable without running the UI.

Workspaces containing multiple living documents should also keep:

```text
living-documents-index.json
```

Use `templates/registry/living-documents-index.template.json` as the starting point.

## Scaffold workflow

For routine work, prefer the bundled `ld` entrypoint. It gives agents one idempotent command and prevents improvised paths:

```bash
ld ensure                         # auto: project in a Git tree, otherwise universal
ld ensure --scope universal
ld ensure --scope project --project /path/to/repo
ld status --scope auto
```

The universal series lives under `/home/cheta/code/living-documents/universal/`. A project series lives under `<project>/.living-documents/`. Each month is a separate `.livingdoc/` folder; `current.json` is the pointer. Rollover creates the new month, records the previous document, updates the central registry atomically, and never mutates the previous document. Read `references/ld-command.md` before changing this routing policy.

For a custom one-off location, use the lower-level scaffold script.

Use `scripts/scaffold-living-document.mjs` rather than reconstructing the starter from memory.

```bash
node scripts/scaffold-living-document.mjs --template blank --target ~/code/living-documents/<kebab-topic> --title "<Document title>" --document-id <kebab-id>
```

Available profiles:

- `blank`: neutral structure with finished interface copy and no topic-specific claims;
- `reference`: populated demonstration of the living-document architecture.

When a model needs to plan the output before writing files, fill `templates/content-input/content-plan.template.json`, then materialize it into `public/content/index.json`, `public/content/sections/*.md`, `public/data/annotations.json`, and `resources/`.

After scaffolding:

1. read `RAISON_DETRE.md`;
2. verify the document's central temporal problem and intended audience;
3. replace the title, thesis, audience, and first section content;
4. preserve schema and stable IDs unless the project truly needs a migration;
5. run `node scripts/validate-living-document.mjs <project-root>`;
6. launch with `npm run dev` or `node serve.mjs`;
7. verify all five themes, both motion modes, keyboard navigation, exports, and narrow layouts.

## Living conversation workflow

Use this path when the skill is invoked before or during an active conversation.

1. Create or update the living-document folder early enough that the document can carry the conversation state.
2. Put settled or current findings into Markdown sections.
3. Put model questions, answer options, blocked choices, and requested human decisions into `modelReplies`.
4. Put human comments, objections, answers, and highlighted text notes into annotations.
5. Continue working on unblocked sections while waiting for human answers.
6. Stop only when all remaining useful work is blocked by unresolved human input, missing evidence, or explicit user pause.
7. Append worklogs after model-authored revisions so the human can review sleep-state progress later.

This workflow is the point of the format. Human and model do not need to move in lockstep. The document lets each side progress at its own pace while sharing stable targets.

Read `references/conversation-lifecycle.md` for the full usage story.

## Conversation-to-living-document export workflow

Use this path when the skill is attached at the end of a long exchange and the user wants the findings as a living document.

1. Identify the conversation's actual topic, thesis, audience, important findings, open questions, decisions, examples, and evidence.
2. Keep the indexed content about the user's topic. Do not fill sections with explanations of the Living Document Forge itself unless the user's topic is living documents.
3. Create or emit this structure:

```text
<topic>.livingdoc/
  RAISON_DETRE.md
  public/
    index.html
    app.js
    styles.css
    manifest.webmanifest
    content/
      index.json
      sections/
        01-<section>.md
        02-<section>.md
    data/
      annotations.json
  worklogs/
  resources/
  package.json
  serve.mjs
  validate.mjs
```

4. Put substantive findings in `public/content/sections/*.md`.
5. Put section metadata, order, proposals, history, releases, visual settings, and worklog summaries in `public/content/index.json`.
6. Put review comments, objections, citations, or evidence notes in `public/data/annotations.json`.
7. Keep `RAISON_DETRE.md` as the architectural preface for agents and humans, but do not duplicate it into every section.
8. If the environment cannot write folders, output a complete file tree with each file in fenced blocks and clear paths.
9. Validate JSON mentally if tooling is unavailable; validate with scripts when files are written.

Read `references/conversation-export.md` for the content mapping contract.

## Revision workflow

1. Read the current request and all attached change payloads.
2. Read `RAISON_DETRE.md`, `public/content/index.json`, targeted Markdown files, annotations, history, releases, and worklogs.
3. Classify each requested change by scope, authority, reversibility, and evidence need.
4. Resolve conflicts using this precedence:
   1. current explicit user instruction;
   2. approved or rejected proposal state;
   3. direct human edits and decision annotations;
   4. attached evidence;
   5. document invariants;
   6. model suggestion.
5. Edit the narrowest possible files. Do not rewrite unrelated prose for uniformity.
6. Update `updated` fields and backlinks when relationships change.
7. Append history and worklog entries.
8. Add decision-ready proposals after model-authored revisions when meaningful alternatives remain.
9. Validate and report changed files, user-visible behavior, migrations, and unresolved risks.

## Canonical content model

Read `references/content-model.md` before changing the schema. The short form:

- `meta`: identity, thesis, audience, version, compatibility;
- `navigation`: view defaults, section order, filters;
- `dashboard`: focus statement, health indicators, metric definitions;
- `sections`: stable metadata pointing to external Markdown files;
- `proposals`: individually decidable changes;
- `releases`: human-readable changelog entries;
- `history`: append-only event timeline;
- `visual`: default theme, allowed themes, motion preference;
- `worklogs`: immutable agent revision appendices;
- `modelReplies`: model-authored questions, answer options, and clarification requests;
- `resources`: arbitrary attachments, media, links, and evidence files;
- `annotations.json`: target-specific comments and evidence pointers.

Never store executable JavaScript, credentials, or untrusted HTML in content fields.

Before changing the format, read `references/format-continuity.md`. A format change is not complete until legacy support, migration, registry updates, and validation gates are documented.

## Interface architecture

The default interface has three layers:

1. **Orientation layer**: persistent title, search, view switcher, section index, status, and progress.
2. **Document layer**: dashboard, focused reader, history, changelog, and search results.
3. **Action layer**: quick edit, annotations, proposal decisions, exports, theme/motion controls, and agent handoff.

Do not wrap every paragraph in a card. Use borders, typographic hierarchy, full-width bands, and whitespace for ordinary content. Reserve cards for repeated dashboard metrics, proposals, annotations, or interactive objects that need an affordance.

Read `references/interface-design-system.md` and `references/interaction-model.md` before changing the starter UI.

The reference design follows the local `frontend-design-masterclass` constraints where they fit this product type: editorial broadsheet reading, data-dense governance views, semantic theme tokens, strong visible focus, no decorative pill clutter, no card sickness, restrained microanimations, and dark/light themes that are independently designed rather than inverted.

## Required capabilities in the reference starting point

A newly scaffolded document must provide:

- dark-first theme with `system`, `obsidian`, `graphite`, `paper`, and `high-contrast` choices;
- persistent theme and motion preferences;
- dashboard with dynamic document metrics and current focus;
- document reader with stable anchors and reading progress;
- section index with status, tag filtering, active-section tracking, and mobile drawer behavior;
- full-text search across section metadata and Markdown;
- history timeline and release changelog as separate concepts;
- quick-edit dialog for title, deck, status, tags, and Markdown;
- local drafts with visible unsaved state;
- undo and redo for local edits;
- command palette and keyboard shortcuts;
- annotations and proposal decision queue;
- focused reading mode;
- JSON, Markdown, and change-request exports;
- responsive two-drawer mobile layout;
- visible focus styles, skip link, semantic landmarks, and reduced-motion support;
- no credentials, remote execution, or hidden network calls.

The first visible example should communicate the reason for the architecture: humans should review agent work in a browser-native surface at their own pace, not race terminal or chat scrollback.

## History versus changelog

Do not merge these:

- **History** is the event ledger: edits, decisions, imports, migrations, exports, and agent runs.
- **Changelog** is the reader-facing release narrative: what changed in a named version and why it matters.
- **Worklogs** are immutable agent appendices: what an agent changed, validated, suggested, and could not verify.

The UI may cross-link them, but each serves a different retrieval question.

## Quick-edit rules

Quick edit is an overlay, not silent canonical mutation.

- Browser edits persist as a local overlay.
- The interface must label local drafts clearly.
- Exporting a change request is the safe bridge back to source files.
- A server-backed implementation may write canonical files only through an authenticated, validated route with version checks.
- Preserve original Markdown until an explicit save or exported patch is applied.
- Keep undo/redo within the current session and record committed local changes in local history.

## Theme and motion rules

- `obsidian` is the default dark theme.
- Light mode is independently designed, not a color inversion.
- Use semantic CSS custom properties; components never hard-code theme colors.
- Apply `color-scheme` so native controls match the selected surface.
- Theme changes may use the View Transition API when available, but must degrade to an immediate token swap.
- Expose `system`, `full`, and `reduced` motion choices.
- Respect `prefers-reduced-motion`; explicit reduced motion wins over decorative transitions.
- Use motion tokens. Most feedback should complete in 100–250 ms.
- Avoid parallax, continuous floating, large zooms, or motion that alters reading position.

## Visual-refactor workflow

When the request changes appearance:

1. State the communication goal.
2. Identify the product type and reading context.
3. Choose an aesthetic direction from the design reference rather than mixing unrelated trends.
4. Define palette, typography, density, surface hierarchy, control language, and motion tokens.
5. Test the content at narrow, medium, and wide widths.
6. Test all themes and reduced motion.
7. Report affected components and any semantic changes.

The bundled direction is **Obsidian Editorial Workbench**: a dark research instrument with serif editorial headings, restrained teal and amber accents, rule-based separation, minimal rounding, and tactile controls. It rejects neon-AI spectacle, gratuitous glass, excessive cards, and ornamental machinery.

## Agent handoff

A handoff payload should include:

- document identity and version;
- targeted section or global scope;
- direct edits;
- annotations and attached resources;
- model replies and unresolved clarification queues;
- approved, deferred, and rejected proposals;
- immutable constraints;
- requested output shape;
- compatibility range;
- validation commands;
- expected changed files.

Read `references/agent-bridge.md` and `references/change-request-contract.md` before invoking an external coding agent.

## Validation sequence

Run all applicable checks:

```bash
node scripts/validate-skill.mjs
node scripts/validate-living-document.mjs examples/reference-living-document
node --check examples/reference-living-document/public/app.js
node --check examples/reference-living-document/serve.mjs
python3 tests/test-ld.py
```

Then inspect manually:

- start page and every view;
- keyboard-only navigation;
- command palette;
- search and filters;
- quick edit, undo, redo, and export;
- theme persistence;
- motion reduction;
- mobile drawers and dialogs;
- missing assets and broken anchors;
- console errors;
- history, changelog, proposals, annotations, and worklog visibility.

## Progressive disclosure map

Load only what the operation needs:

| Need | Reference |
|---|---|
| Why the architecture exists | `references/raison-detre.md` |
| Data fields and invariants | `references/content-model.md` |
| Format evolution and legacy migrations | `references/format-continuity.md` |
| Layout, themes, typography, color | `references/interface-design-system.md` |
| Dashboard, search, editing, history, motion | `references/interaction-model.md` |
| Convert a long conversation into document files | `references/conversation-export.md` |
| Run an ongoing human-model document conversation | `references/conversation-lifecycle.md` |
| Fill section titles and content paths before generation | `templates/content-input/content-plan.template.json`, `schemas/content-plan.schema.json` |
| Apply revisions safely | `references/revision-playbook.md` |
| Evaluate editorial quality and prevent conceptual drift | `references/editorial-rubric.md` |
| Classify claims, resolve contradictions, and structure deliberation | `references/concept-deliberation.md` |
| Visual refactor | `references/visual-refactor.md` |
| Agent request/response contracts | `references/agent-bridge.md`, `references/change-request-contract.md` |
| Migration from 0.3.x | `references/migration-paths.md` |
| Central registry template | `templates/registry/living-documents-index.template.json`, `schemas/living-documents-index.schema.json` |
| Universal/project routing and month rollover | `references/ld-command.md`, `bin/ld` |
| Deploy the functional follow clause | `references/system-prompt-clause.md` |
| Evidence and attachments | `references/resource-provenance.md` |
| Adversarial design verdict | `references/adversarial-review.md` |
| Design input provenance | `references/design-provenance.md` |
| Customize the starter | `references/starter-guide.md` |

## Completion report

Return:

- artifact path;
- version;
- changed architecture and visible features;
- validations run and their results;
- migrations or compatibility changes;
- known limitations or unverified browser behavior;
- concise instructions to scaffold and launch.

Never claim a browser interaction was tested when only static validation was performed.
