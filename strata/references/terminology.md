---
title: Strata lifecycle terminology
version: "2.2.0"
tags: [strata, intake, lifecycle]
---

# Strata lifecycle terminology

| Operation | Input | Result | Stop condition |
| --- | --- | --- | --- |
| Ideation | Conversations, research, sketches and decisions | Session outputs in any supported source format | Ideas captured; no preparation claim |
| Intake staging | Ideation outputs, archives or an existing spec pack | One project folder, preserved sources, project-intake.json, read order and format findings | Inputs organized; specs and build unstarted |
| Specification preparation | Staged intake and authorized project principles | Spec Kit constitution, specification, plan, tasks, applicable supporting artifacts, analysis and preparation receipt | Contracts and task gates verified; implementation unstarted |
| Fresh-session handoff | Verified preparation and reset-handoff.md | A fresh harness consumes the handoff from the real build root | New context acknowledges exact inputs and next task |
| Project initiation | Explicit implementation authority and passed preparation gates | First implementation task starts in that fresh harness | Initiation acknowledged; implementation completion is a separate outcome |

A harness reset means a new context, not necessarily closing a terminal. A new terminal tab can host a fresh harness; reattaching the old session does not reset it. The skill is terminal agnostic. Terminal adapters only transport a validated command and working directory.

"Stage" means intake staging. "Prepare specs" and "take through tasks" mean specification preparation. "Initiate" and an explicit request to build include project initiation. Never equate these operations.

For Living Documents scope labels, use its system terminology when available. An intake folder is not a project dossier or an implementation repository. No other reference covered these operation boundaries, so this reference adds a shared vocabulary rather than duplicating one.
