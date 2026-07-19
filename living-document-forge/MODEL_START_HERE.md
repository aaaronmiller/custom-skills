# MODEL START HERE

You are reading the Living Document Forge skill package.

Read in this order:

1. `RAISON_DETRE.md`
2. `SKILL.md`
3. `references/conversation-lifecycle.md`
4. `references/content-model.md`
5. `references/format-continuity.md`
6. `references/conversation-export.md`

For normal use, do not edit the HTML, CSS, or JavaScript. Copy the template app, then write the user's content into:

- `public/content/index.json`
- `public/content/sections/*.md`
- `public/data/annotations.json`
- `resources/`

Run `node scripts/scaffold-living-document.mjs` when you can write files. If you cannot write files, output the complete folder tree and file contents.

If a workspace contains multiple living documents, create or update `living-documents-index.json` from `templates/registry/living-documents-index.template.json` before broad migrations. Never strand legacy documents without either a supported schema path or a migration patch.
