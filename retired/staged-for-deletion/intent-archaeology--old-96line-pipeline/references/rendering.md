# Rendering rules

## Ownership is per file, not per repository

| Content | Owner | Written by |
|---|---|---|
| Events, intents, evidence, statuses | SQLite | Pipeline only. Regenerable. |
| `derived/prompt-wiki/**` | Machine | `06-render.py`. Safe to delete. |
| `human/notes/**` | Human | You. No script writes here, ever. |

Every generated file is wrapped in a fence:

```
<!-- GENERATED:intent-archaeology BEGIN. Do not edit inside this fence. -->
...
<!-- GENERATED:intent-archaeology END -->
```

If a human edits inside a fence, that is a conflict to surface rather than
something to silently discard on the next run.

## The pages that matter are the cross-cutting ones

Per-project pages are the obvious structure and the least interesting output.
The value is in views you cannot get from any single session: standing
constraints, repeated corrections, abandoned work, open questions, and
cross-project echoes.

Read `corrections.md` first. Every row is a rule you keep having to repeat,
which means it is not in your standing instructions yet.

## Verbatim rule

Normalized text is the display layer. `verbatim` is canonical and immutable.
Spelling correction and rewriting happen in `statement` only. A wiki that has
edited its own evidence is not a record, it is a story.
