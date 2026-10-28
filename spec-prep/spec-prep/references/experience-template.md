---
date: 2026-10-12 11:40:00 PDT
ver: 2.1.0
author: ice-ninja
tags: [spec-prep, experience, ux, design-tokens, mockup, template]
---

# Experience Template (`experience.md`)

Author: the system. Layer: derived (declare `layer: derived` in its frontmatter). Required whenever the project has a user interface; omit it for libraries, services and CLIs with no designed surface.

Context answers how the system is built. Experience answers how it looks, reads and responds. Keeping them apart stops visual decisions from being buried in architecture and gives design-focused skills (frontend design, accessibility review, UX copy) one file to own.

## Derivation inputs

1. Personas, user stories and failure conditions from `intent.md`.
2. Accessibility and interaction clauses from `spec.md`.
3. The user's stated design preferences (theme defaults, frameworks for UI primitives belong in context, not here).
4. Any design-skill guidance available in the session. Use those skills to choose palette, type and layout, and record the choice here with one line of reasoning each.

## Template structure

```markdown
---
date: {{DATE}} {{TIME}} {{TZ}}
ver: 1.0.0
author: {{AUTHOR}} (system-derived)
model: {{MODEL}}
layer: derived
tags: [{{TAGS}}]
---

# [Project Name] Experience v1.0 (derived)

## 1. Interaction model
[Screens or states, navigation model, the first thirty seconds, loading, empty and error states. Each element cites the story or persona it serves.]

## 2. Design tokens
| Token | Dark | Light | Role |
|-------|------|-------|------|
[The mockup is the source of truth when one exists; this table mirrors it exactly.]

## 3. Components with behaviour contracts
[Only bespoke or critical components: inputs, keyboard and pointer behaviour, accessible name, role and value, feedback.]

## 4. Copy rules
[Voice, banned terms, verb consistency, error and empty-state patterns.]

## 5. Mockup
[Path to an interactive mockup and screenshots in each theme at phone and desktop widths. The mockup must be verified by actually rendering it, not by reading its source.]

## 6. Accessibility
[Target level; how each accessibility SPEC clause is met.]
```

## Rules

No requirement appears here that is not in intent or spec. Every token and component traces to a story or clause. Screenshots or it did not happen.
