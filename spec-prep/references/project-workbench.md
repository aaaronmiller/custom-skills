---
title: Optional default project workbench
version: "2.3.0"
tags: [spec-prep, workbench, intake, configuration]
---

# Optional default project workbench

Use this reference during intake staging or specification preparation unless the user opts out. It adds the workbench integration that 2.2 lacked; it does not replace the intake or preparation contracts.

## Default and boundaries

Workbench mode is `auto` by default: create or update a lightweight `workbench.json` in the intake folder, reuse a compatible existing workbench, and register it with an already available renderer when supported. `on` explicitly requests that integration. `off` omits workbench generation; it does not delete an existing workbench. Do not install a renderer, start a service, launch a terminal or initiate implementation merely to create this file.

`project-intake.json` owns project identity, ideation sources, read order, findings and intake lifecycle. `workbench.json` points to it and records presentation/configuration choices, actual artifact locations and optional integration preferences. The renderer derives displayed state from the intake, prepared artifact files and preparation receipt. Never mirror editable requirements, task statuses or a second lifecycle field into the workbench.

The default artifact set is intent, native specification, native plan, gated tasks, project constitution, agent instructions, traceability/provenance and reset handoff with preparation evidence. Requirements/design files supplied by ideation remain preserved inputs. Do not generate requirements.md beside spec.md, or design.md beside plan.md, with duplicate independently editable content. Context rationale, UX, data models, contracts, research, quality checklists and playbooks are additional roles when they add value or the selected toolchain requires them.

## Generate and check

After establishing a valid intake manifest, run the bundled helper:

```bash
python3 scripts/spec-prep-workbench.py write <intake-folder> --mode auto --living-documents auto
python3 scripts/spec-prep-workbench.py check <intake-folder>
```

When the real build root has been resolved, repeat `write` with `--build-root <actual-build-root>`. The helper lists existing recognized artifacts as source or operational pointers. It never creates a pretend spec, changes task state or generates a successful preparation receipt. It preserves custom configuration and existing valid artifact mappings. An invalid existing workbench requires repair rather than silent overwrite.

The schema is `references/workbench.schema.json`. It uses schemaVersion 1, kind `spec-prep-workbench`, intake `project-intake.json`, a mode, optional buildRoot, an artifacts array and a Living Documents mode. Artifact entries declare role, scope (`intake` or `build`), path and use (`source` or `operational`). Intake paths are relative and remain inside their intake folder. Build pointers require an explicitly resolved buildRoot. Never add secrets, raw eval contents or credentials.

## Additional files

Discover additional visible files dynamically. Preserve transcripts, screenshots, diagrams, mockups, research, prototype code, spreadsheets, PDFs and unknown formats as source evidence. Role inference from a filename is advisory, not authority. Classify each material source as incorporated, deferred, rejected, superseded, duplicate or unresolved during preparation, with its provenance and reason. Unsupported extraction is visible in findings; do not lose the original or treat unread content as examined.

Exclude version-control internals, dependency caches, machine secrets and external symlink traversal from automatic discovery. Archives are inert until the explicit safe staging extraction operation. Held-out evaluation payloads remain external and only a handling pointer appears in the workbench.

Workbench configuration is independent of a renderer. The assignment catalog is one adapter: it reads the manifest and presents artifact pointers alongside its live folder inventory. A source pointer in an existing spec pack is not proof that the project has completed native Spec Kit preparation.

## Optional integration

Keep Living Documents mode in the workbench as `auto`, `on` or `off`. Read `living-documents-setup.md` only when requested, detected or required by the host instructions. That file defines setup, authority and continuity behavior. An absent optional integration never blocks independent spec preparation. Current scoped instructions can make an integration mandatory; the portable default does not override them.
