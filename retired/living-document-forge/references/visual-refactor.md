---
title: Visual refactor protocol
version: 1.0.0
---

# Visual refactor protocol

A visual refactor must improve orientation, state visibility, reading endurance, editing confidence, or conceptual persuasion.

## Before changing styles

Record:

- communication goal;
- primary user and reading context;
- product type;
- selected visual direction;
- current failures;
- expected responsive behavior;
- motion and accessibility constraints.

## Hierarchy

- Canonical document content is primary.
- Section identity and local draft state remain visible.
- Dashboard metrics support action but do not dominate reading.
- Annotations, proposals, and edit controls are reachable without becoming permanent clutter.
- History and changelog remain distinct.
- Agent handoff is consequential and reviewable.

## Default direction

Use Obsidian Editorial Workbench unless the user chooses another explicit direction. Read `interface-design-system.md`.

## Motion

Motion may confirm, orient, or provide restrained delight. It may not delay editing, move large reading surfaces unexpectedly, or continue indefinitely.

Respect explicit reduction and `prefers-reduced-motion`. Theme transitions and dialog settles must have immediate fallbacks.

## Responsive behavior

- Wide: three-pane workbench.
- Medium: persistent section rail, inspector drawer.
- Narrow: both rails become drawers; main reading canvas remains full width.
- Dialogs fit the viewport.
- Source Markdown remains editable on small screens.
- No horizontal page scrolling at 320 CSS px or 200% zoom.

## Refactor report

Report:

- chosen design direction and rejected alternatives;
- affected files and components;
- theme changes;
- motion changes and reduced-motion behavior;
- responsive checks;
- accessibility checks;
- assets added or removed;
- anything not tested in an actual browser.
