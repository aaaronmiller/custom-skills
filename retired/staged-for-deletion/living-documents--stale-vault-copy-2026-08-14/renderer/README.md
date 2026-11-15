---
title: Living Documents shared renderer
status: canonical
---

# Living Documents shared renderer

This directory is the one operational presentation layer for every project
Living Document.

- `public/` contains the application shell, styles, behavior, and installable
  metadata.
- Canonical project Markdown lives under
  `/home/cheta/LIVING_DOCUMENTS/projects/<project>/`.
- The `living-documents` skill generates disposable renderer projections under
  `/home/cheta/.cache/living-documents/runtime/projects/<project>/`.
- `serve.mjs` resolves each generated `current.json` pointer from that runtime
  cache.
- Project folders own Markdown truth. Generated manifests and annotation
  bootstrap files are projections, not authorities.

Routes:

- `/` renders the Portfolio from canonical `~/LIVING_DOCUMENTS/INDEX.md` and
  current generated project manifests.
- `/projects/<project>/` renders that project using the same application code.
- `/api/portfolio` exposes the read-only derived portfolio payload.
- `/api/operations` exposes read-only current queue, decision, and ledger
  summaries derived from canonical Markdown and explicit ledger records.
- `/api/portfolio-export` downloads a versioned loopback-local operations
  export. It includes local paths, compact summaries, session IDs, and Git
  metadata for recovery; it excludes raw transcript/prompt bodies and
  credentials. Do not publish it without a separate reviewed redaction profile.
- Shell assets always come from `renderer/public/`.
- `content/` and `data/` come from the generated projection of the selected
  Markdown project.

Run:

```bash
npm start
```

The default address is `http://127.0.0.1:4173`.

Run `ld sync --all` before launching after direct Markdown edits. The enabled
projection watcher uses `ld sync --all --no-index-write` after detected source
changes, rebuilding only the generated runtime cache. It never edits canonical
Markdown or rewrites the portfolio index.
