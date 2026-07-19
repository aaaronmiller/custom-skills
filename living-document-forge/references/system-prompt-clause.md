---
title: System-prompt follow clause
version: 1.3.0
status: candidate
---

# Living-document follow clause

## Recommended deployment text

> For substantial work, run `ld ensure` once before planning or consequential writes. Follow the returned living document: read its `MODEL_START_HERE.md` and manifest, then record durable changes to intent, decisions, evidence, blockers, gates, and next actions at milestones. `ld` routes Git-backed work to the current project month and other work to the universal month; rerun it after a month change and preserve prior documents. Skip trivial one-step requests. If `ld` fails, do not invent a substitute path: preserve the task, report the routing failure, and continue only when safe without the document.

## Why this wording

- “Substantial” prevents per-command document churn.
- “Once” prevents repeated startup calls in one task.
- The executable command makes the policy functional rather than aspirational.
- The returned paths, not model memory, determine the target.
- Milestone updates preserve durable state without turning the living document into raw logs.
- Failure behavior prevents near-duplicate folders while avoiding needless task blockage.

## Trigger default

Treat work as substantial when any condition holds:

- three or more dependent steps;
- project or system files will change;
- research or decisions should survive the session;
- work may continue across agents, sessions, or days;
- a failure would require reconstructing objective or state.

## Deliberate exclusions

Do not invoke `ld` for greetings, simple lookups, one exact read-only command, trivial formatting, or a response that creates no durable work state.

## Unresolved policy decisions

1. Whether `ld` failure should block all substantial work instead of only unsafe document-dependent work.
2. Whether project documents should remain under `<project>/.living-documents/` or be centralized under `/home/cheta/code/living-documents/projects/`.
3. Whether monthly rollover should use the machine's local timezone or a fixed operator timezone.
4. Whether agents should update at every consequential mutation or only at milestones; milestone updates are the current default.
