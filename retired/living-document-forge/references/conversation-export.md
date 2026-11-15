---
title: Conversation export contract
version: 1.2.0
---

# Conversation export contract

Use this reference when a human invokes the skill for a long conversation or asks the model to materialize current findings as a living document.

## Goal

Create or update a complete living-document folder. The output should feel like a polished document about the user's topic, not an essay about the living-document format.

The living-document architecture should appear in:

- root `RAISON_DETRE.md`;
- `MODEL_START_HERE.md` and `READER_START_HERE.html`;
- manifest compatibility metadata;
- history, changelog, annotations, proposals, and worklog records;
- the browser shell and styling.

The topic findings should appear in:

- `public/content/index.json`;
- `public/content/sections/*.md`;
- `public/data/annotations.json`;
- optional `resources/`.
- `modelReplies` for questions the model can ask without blocking unrelated work.

## Content mapping

Map conversation material as follows:

| Conversation material | Living-document destination |
|---|---|
| central conclusion | `meta.thesis` and first section |
| major findings | Markdown section files |
| evidence, links, screenshots, attachments | annotations or resources targeting section IDs |
| unresolved questions | proposals or an "open questions" section |
| model question for the human | `modelReplies` |
| explicit user decisions | history events and proposal decisions |
| rejected alternatives | rejected proposals or a "rejected directions" section |
| next actions | proposals plus dashboard focus |
| model uncertainty | annotations, limitations section, or worklog warnings |
| implementation instructions | sections, proposals, or change requests depending on authority |

## Section rules

- Use 3-8 sections for most 5-30 turn conversations.
- Use stable kebab-case IDs independent of the visible title.
- Name files with ordered kebab-case paths, such as `01-problem.md`.
- Keep each section focused on one retrieval question.
- Put long reasoning in Markdown, not JSON.
- Avoid placeholder sections.
- Preserve concrete examples from the conversation when they carry the user's intent.
- Do not create a dashboard section; the dashboard is generated from manifest data.

## Manifest minimum

The manifest must include:

- `meta.documentId`, `title`, `subtitle`, `version`, `updated`, `status`, `thesis`, `audience`, `compatibility`;
- `navigation.defaultView` and `navigation.sectionOrder`;
- `dashboard.focus`, `dashboard.health`, `dashboard.metricDefinitions`, `dashboard.pinnedSectionIds`;
- `sections` metadata with `id`, `index`, `eyebrow`, `title`, `dek`, `source`, `tags`, `status`, `editable`, `owner`, `updated`, `estimatedMinutes`, `dependencies`, and `backlinks`;
- `proposals`, even if empty;
- `releases`, `history`, `visual`, and `worklogs`.
- `modelReplies` and `resources`, even if empty.

## Default release and worklog

A newly exported document should include one release:

- version: `1.0.0`;
- title: "Initial living document export";
- summary: one sentence about what the conversation produced.

It should include one worklog:

- id: `W-001`;
- actor: the model or agent name if known;
- summary: what was converted;
- changed: files or concepts created;
- validations: JSON parse, structural validation, or `skipped` with reason;
- warnings: uncertainty, missing sources, or unverified claims.

## Annotation rules

Use annotations for review state, not generic commentary. Good annotations include:

- "This claim came from the user's original explanation and should not be softened."
- "Evidence link needed before public release."
- "This open question blocks implementation."
- "This point may belong in a sibling wiki page once settled."

## Output when filesystem writes are unavailable

If the agent cannot write files, output:

1. the folder name;
2. a file tree;
3. each required file in a fenced code block with its path as a heading;
4. a final validation note listing which checks were performed or could not run.

Do not output a partial sketch. A living document export is complete only when the user could create the files and open the shell.
