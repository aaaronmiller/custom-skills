# RAISON D'ETRE: Living Document Forge

This skill exists to create browser-native, addressable review surfaces for asynchronous human-agent collaboration.

Start with `references/raison-detre.md`. It is the canonical explanation of the concept and includes the document-root copy that every generated living document must carry.

The short version:

- chat is a poor protocol for long-running conceptual work because agents produce faster than humans can review;
- a living document gives every section, proposal, annotation, change, and worklog a stable address;
- humans review and annotate at human speed;
- agents operate through bounded change requests and append-only worklogs;
- LLM wikis remain siblings optimized for retrieval of settled knowledge;
- living documents optimize active refinement, sleep-state iteration, decision history, and multimedia context;
- the canonical working artifact is a folder, optionally named `.livingdoc/`; archives are for distribution.

Read order for agents:

1. `RAISON_DETRE.md`
2. `references/raison-detre.md`
3. `SKILL.md`
4. target document `RAISON_DETRE.md`
5. target document `public/content/index.json`

Do not treat the browser shell as the document. The document is the contract plus the external Markdown and structured ledgers rendered by the shell.
