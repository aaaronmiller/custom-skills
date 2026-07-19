---
title: Starter customization guide
version: 1.2.0
---

# Starter guide

## Assemble a project

```bash
node scripts/scaffold-living-document.mjs --template reference --target ./my-living-document
```

Use `blank` for a neutral project.

For the common end-of-conversation case, use the blank template as the wrapper and place the conversation findings into the content files:

```text
public/content/index.json
public/content/sections/*.md
public/data/annotations.json
```

The shell supplies dashboard, search, themes, quick edit, history, changelog, and export behavior. The model's job is to produce clean Markdown sections plus accurate manifest records.

For model-generated documents, use `templates/content-input/content-plan.template.json` first. It gives the model a small place to decide section IDs, section titles, Markdown paths, model replies, resources, and annotations before writing the full manifest.

## First files to edit

1. `RAISON_DETRE.md`
2. `public/content/index.json`
3. `public/content/sections/*.md`
4. `public/data/annotations.json`

Avoid changing `public/app.js` or `public/styles.css` until the content model and view requirements actually differ.

Keep `RAISON_DETRE.md` architectural. Do not duplicate the living-document manifesto inside the indexed topic sections unless the topic itself is living documents.

Root start files:

- `READER_START_HERE.html` opens the browser shell.
- `MODEL_START_HERE.md` tells a model which files to read and which files it may edit.

These are redundant with `RAISON_DETRE.md` on purpose. `RAISON_DETRE.md` explains why the document exists; the start files route different users into the right surface quickly.

## Rename safely

- Change `meta.title`, `meta.subtitle`, and `meta.thesis` freely.
- Change `documentId` only during initial creation.
- Keep section IDs after publication.
- Rename Markdown files only after updating the corresponding `source` field and inbound links.

## Add a section

1. Create a Markdown file with YAML frontmatter.
2. Add a section record to the manifest.
3. Add its ID to `navigation.sectionOrder`.
4. Update dependencies and backlinks.
5. Append a history event.
6. Run validation.

## Add a theme

1. Add the theme ID to `visual.themes`.
2. Define every semantic token in `styles.css`.
3. Set `color-scheme`.
4. Test native controls, code blocks, selections, status colors, dialogs, and focus rings.
5. Verify contrast and 200% zoom.

## Extend beyond static mode

When moving to SvelteKit/Hono:

- preserve the manifest and Markdown paths;
- keep browser drafts separate from canonical content;
- add authenticated API routes for writes;
- require optimistic concurrency using document version or ETag;
- validate payloads with the bundled schemas;
- append history and worklog entries server-side;
- never expose model or repository credentials to the browser.
