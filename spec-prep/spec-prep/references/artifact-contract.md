---
title: Canonical artifact contract
version: "2.3.0"
tags: [spec-prep, artifacts, speckit, governance]
---

# Canonical artifact contract

Read when deciding what to produce from ideation. This consolidates the artifact naming/mapping guidance previously spread across the core table and compatibility reference. Do not add a file merely to reproduce another file's contents.

| Role | Default location | Purpose |
| --- | --- | --- |
| Intake | project-intake.json | Preserved source inventory, identity, read order and format findings |
| Workbench | workbench.json, unless opted out | Configuration and artifact pointers; derived display rather than another specification |
| Intent | intent.md in the declared spec area | Why, goals, scope, constraints, success/failure conditions and human intent |
| Specification | specs/<feature>/spec.md | What, requirements, user stories, observable acceptance and eval bindings |
| Plan | specs/<feature>/plan.md | How, derived architecture and implementation decisions |
| Tasks | specs/<feature>/tasks.md | Dependency-ordered work, owned paths, acceptance gates and recovery |
| Constitution | .specify/memory/constitution.md | Project principles and mandatory gates |
| Session instructions | AGENTS.md in the actual build root | Required read order, constitution reference, task gates and initiation boundary |
| Provenance and traceability | Intake/source disposition map plus traceability.md when useful | Source → intent/story → clause/eval → plan/task → evidence; no silently dropped material |
| Preparation evidence | preparation.json | Actual gate results and hashes of the consumed artifact versions |
| Fresh-session handoff | reset-handoff.md | Build root, current authority, validated inputs, unresolved items and next authorized task |
| Continuity | Declared spec-prep ledger/standing or linked Living Documents context | Decisions, outcomes and resumable state under one declared authority |

Existing requirements.md and design.md are accepted inputs or existing naming conventions. For native Spec Kit preparation, their roles resolve to spec.md and plan.md. Context.md is retained only as a source, an alternate standalone plan or additional derivation rationale. Do not create a competing plan.

Create conditional supporting artifacts when the domain or installed template requires them: research.md, data-model.md, contracts/, quickstart.md, requirements-quality checklists, experience.md, mockups/screenshots, reusable plays, substrate self-location and evaluator-only held-out fixtures. Preserve already supplied supporting files regardless of whether they match one of these names. Mark unknown or unreadable content explicitly.

AGENTS.md should reference the authoritative constitution and contain the session's enforceable read order and gate procedure. Do not paste a second independently editable constitution into it. Preserve existing instructions; add the project-specific gates narrowly. CLAUDE.md may import AGENTS.md when that is the repository convention; other integrations use their own installed instruction loaders.

Task acceptance gates are procedures that must be executed, not just checkbox text. Verify the installed prerequisite checker and artifact analysis before issuing a preparation pass. Custom requirements-quality checklist marks are reviewer decisions, distinct from implementation completion. A later fresh harness verifies receipt hashes again so artifact changes invalidate stale preparation evidence.

Spec Kit references checked 2026-10-14: https://github.github.com/spec-kit/reference/agentic-sdd.html. Tests for implementation tasks are added when requested or needed for their acceptance, rather than mirrored automatically for every reversible change.
