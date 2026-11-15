---
title: Eight-perspective adversarial review
status: resolved
---

# Adversarial design review

## Thesis

A living document should become a dark-first, themeable research workbench with dashboard, history, changelog, quick editing, section indexing, search, and tactile microinteractions while preserving external, diff-friendly content.

## Round 1: independent positions

1. **Information architect:** supported the thesis but required strict separation between navigation, canonical content, and activity metadata.
2. **Editorial systems designer:** attacked dashboard dominance and warned that excessive widgets would turn reading into administration.
3. **Interaction designer:** supported quick edit and command palette, but required undo, visible local-draft state, and safe export rather than invisible source mutation.
4. **Accessibility specialist:** rejected motion and dark-mode defaults unless motion reduction, high contrast, keyboard operation, focus management, and a complete light theme were first-class.
5. **Frontend performance engineer:** attacked framework-heavy starter dependencies and argued for a portable reference shell with no required build chain.
6. **Data-governance engineer:** required append-only history, immutable worklogs, stable IDs, schemas, compatibility metadata, and explicit migration.
7. **Agent-workflow engineer:** required change-request exports, provenance, bounded targets, and clear distinctions among human edits, agent suggestions, and canonical state.
8. **Visual design critic:** supported a dark research aesthetic but rejected purple gradients, universal glassmorphism, decorative gauges, and card saturation.

## Round 2: direct criticism

- The editorial designer and performance engineer defeated the initial idea of a bento-heavy Svelte dashboard as the canonical starter. It offered visual novelty but increased dependency, migration, and content-obscuration costs.
- The interaction designer defeated direct browser writes as a default. Local overlays plus export are safer and work without a backend.
- The accessibility specialist forced theme and motion controls into the base contract rather than leaving them as polish.
- The data-governance engineer strengthened the distinction among history, changelog, and worklog after other perspectives initially treated them as one timeline.
- The visual critic accepted bounded dashboard instruments but rejected putting every section in a rounded card.

## Round 3: revised thesis

The strongest surviving design is a three-layer editorial workbench:

- a portable, dependency-free reference application;
- external Markdown and structured JSON as canonical source;
- dashboard functions separated from focused reading;
- local quick edits with undo, history, and export;
- dark-first semantic themes plus paper and high contrast;
- restrained, optional microinteractions;
- schemas, migrations, and agent handoff contracts.

## Verdict

**REVISED, THEN SURVIVES.**

The original feature thesis survives, but only after abandoning framework dependence, dashboard sprawl, direct source mutation, and decorative motion.
