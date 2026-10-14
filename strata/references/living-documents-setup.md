---
title: Optional Living Documents integration
version: "2.3.0"
tags: [strata, living-documents, setup, continuity]
---

# Optional Living Documents integration

Read this reference only when the user requests Living Documents, an existing dossier/configuration declares it, the `ld` command is available, or host instructions require it. This supersedes the inline Living Documents setup procedure in Strata 2.2. Host instructions remain authoritative.

## Resolve the setup choice

`auto` detects and reuses an available system or existing dossier. `on` requests integration. `off` skips optional integration without deleting anything. Do not force installation on machines without Living Documents. When requested but unavailable, state the unavailable integration and continue all independent preparation; installation requires a request targeting it.

Once present, read the installed Living Documents skill and current system contract rather than copying an old version into Strata. Resolve the exact source project, run `ld ensure` for that project, and read the returned start-here, project and what-to-do pages. Verify that the returned source-root actually matches; an ancestor match is not enough. Do not query or resume unrelated project ledger work.

For an authorized missing dossier, use the installed `ld create-project` syntax with the project ID, title and real source root. Reuse existing pages and stable IDs. Use `ld add-page` for additional pages, then edit the registered page. Preserve existing narrative and operator annotations. Read the CLI help for installed syntax; no hardcoded user paths or stale release numbers belong in this portable reference.

## Declare authority once

The workbench is presentation/configuration. The intake is source evidence and identity. Spec Kit artifacts are the operational contract in the repository. The dossier records human intent, accepted decisions, project task evidence and cross-session continuity under its own contract. Name which location owns each concept and link between scopes instead of keeping parallel editable requirements, plans or task status.

Register links to the intake, workbench, repository constitution, native spec/plan/tasks, preparation evidence and reset handoff when useful. Keep the dossier's project task register separate from Spec Kit's implementation task breakdown, with clear ownership and linked completion evidence. An implementation checkbox cannot silently satisfy a dossier gate.

## Continuity

Use the existing system's history, start-here, handoff and continuity hook for material milestones. If the chosen standalone STRATA continuity files still apply, declare their role and avoid duplicate independent decision logs. Use the installed validator/adapter for the declared canonical continuity paths; do not fabricate a ledger merely to satisfy a mechanical gate.

A fresh implementation harness reads the real build root's AGENTS.md, the canonical constitution, prepared task gates and reset handoff, then the linked dossier context when present. Verify required preparation before initiation. A renderer receipt or dossier entry is not permission to launch, publish or spend.

Store the integration preference and optional dossier locator in `workbench.json`. Only an identified existing or created dossier may supply that locator. Do not invent a path or manufacture a setup-complete label.
