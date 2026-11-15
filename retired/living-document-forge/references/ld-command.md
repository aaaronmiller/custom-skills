---
title: ld command routing and rollover contract
version: 1.3.0
---

# `ld` command

`ld` is the deterministic entrypoint for finding or creating the living document an agent should follow. It prevents each agent from inventing a path, forgetting the registry, or overwriting last month's state.

## Commands

```bash
ld ensure
ld ensure --scope universal
ld ensure --scope project --project /path/to/repository
ld status
```

`ld` with no subcommand is equivalent to `ld ensure`. Every successful command emits JSON suitable for agent parsing.

Linux already uses `/usr/bin/ld` for the GNU linker. Installation therefore uses the bundled `bin/ld-shim`: only the explicit living-document surface above (or living-document flags such as `--scope`) routes to Forge; linker commands such as `ld --version`, `ld -o`, and compiler-driven linker calls pass through to `/usr/bin/ld`. Do not install the Python command directly over the linker name.

## Scope selection

- `--scope universal`: use the central universal series.
- `--scope project`: use the specified project or nearest Git root.
- `--scope auto` (default): choose project scope when `--project`, `LD_PROJECT_ROOT`, or a Git root is present; otherwise choose universal scope.

A non-Git folder explicitly passed with `--project` is a valid project root. Automatic routing never creates a new project folder.

## Paths

Default central home:

```text
/home/cheta/code/living-documents
```

Universal series:

```text
<home>/universal/
  current.json
  YYYY-MM.livingdoc/
```

Project series:

```text
<project>/.living-documents/
  current.json
  YYYY-MM.livingdoc/
```

Central registry:

```text
<home>/living-documents-index.json
```

Use `LD_HOME` only for a deliberate alternate registry/home, especially isolated tests. Do not silently substitute dash/underscore siblings.

## Month rollover

The month defaults to the local current `YYYY-MM`; tests and controlled operations may use `--month` or `LD_NOW`.

When the current pointer refers to an earlier month, `ld ensure`:

1. leaves the prior document untouched;
2. scaffolds the new monthly document;
3. adds `meta.continuity` pointing to the prior document;
4. appends rollover history and worklog entries in the new document;
5. marks the old registry record archived;
6. adds the new active record;
7. atomically replaces `current.json`.

It does not copy all old prose forward. An agent should carry forward only still-active decisions, blockers, evidence, and next actions after reading the previous document.

## Idempotence and safety

- Re-running `ld ensure` in the same scope and month returns `existing`.
- Every non-dry run executes the bundled living-document validator before updating the registry or current pointer.
- A non-empty target that lacks the living-document manifest is rejected.
- Registry and pointer writes use atomic replacement.
- Previous monthly documents are never mutated by rollover.
- The command does not execute attachments or make network calls.
- `--dry-run` resolves the intended target without creating or updating files.

## Environment overrides

| Variable | Purpose |
|---|---|
| `LD_HOME` | Alternate central home and registry |
| `LD_PROJECT_ROOT` | Explicit project root for auto routing |
| `LD_NOW` | Deterministic `YYYY-MM` for tests |
| `LD_TIMESTAMP` | Deterministic ISO timestamp for tests |
| `LD_SKILL_ROOT` | Alternate skill package containing templates |

## Agent use

At the start of substantial work, run `ld ensure` once. Read the returned `manifest` and the document's `MODEL_START_HERE.md`. Update the living document only when work creates durable intent, decisions, evidence, blockers, or recovery state. Do not turn every trivial command into document churn.
