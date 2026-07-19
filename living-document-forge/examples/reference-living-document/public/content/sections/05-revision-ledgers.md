---
id: revision-ledgers
title: History, changelog, and worklog are not synonyms
updated: 2026-07-09
---

## History answers “what happened?”

History is append-only and event-oriented. It records edits, decisions, imports, migrations, exports, and agent runs. A history entry may be small and operational because its job is traceability.

## Changelog answers “what changed for readers?”

A release changelog is selective. It groups changes into a named version and explains their practical significance. It should not list every save or temporary experiment.

## Worklog answers “what did the agent do?”

A worklog is an immutable appendix to a model-authored revision. It names changed files, validations performed, suggestions left unresolved, and warnings about what could not be verified.

These ledgers may link to one another, but merging them produces a timeline that is simultaneously too noisy for readers and too vague for auditors.

## Correction without erasure

When an old history or worklog entry is wrong, add a correction event. Do not rewrite the original record to make the project appear tidier than it was. A living document earns trust by preserving how understanding changed, including the awkward intermediate shapes.
