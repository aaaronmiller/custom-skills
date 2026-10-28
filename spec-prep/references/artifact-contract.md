---
title: Canonical artifact contract
version: "2.5.1"
tags: [spec-prep, artifacts, speckit, governance]
---

# Canonical artifact contract

Read when deciding what to produce from ideation. This consolidates the artifact naming/mapping guidance previously spread across the core table and compatibility reference. Do not add a file merely to reproduce another file's contents.

## Compact input handoff

Each workstream has one complete requirements.md (observable behavior/acceptance), design.md (mechanisms, data, interfaces and decisions) and intent.md (goals, constraints, stories and source authority). These are the obvious entry point, not three indexes to dozens of missing chapters. Put hardware profiles, decisions and contracts in the owning core document unless a necessary appendix/format justifies separation. Keep the input-root Markdown entry surface to the named trio; linked subordinate appendices belong under appendices/, not as extra mandatory peer documents. Each workstream uses a distinct buildRoot. Existing native packs are intake sources rather than fabricated input-handoff outputs. Preserve original attachments under sources/ and map material needs once. Do not omit source depth to reduce file count or emit every conditional template.

Governance is retained alongside the core trio: `.specify/memory/constitution.md`, build-root AGENTS.md and reset-handoff.md. AGENTS.md must instruct a fresh session to read the constitution and handoff before changes. Add the selected harness's supported project-local adapter, for example CLAUDE.md containing `@AGENTS.md`, when needed. The constitution governs specifications, plan/task decisions and their gates. Verify actual selected-harness loading when claiming reset readiness; a pointer alone is not an observed fresh-session read.

An input handoff includes a concise conversion/read-order guide and source-disposition mapping (an intent appendix is sufficient). A separately requested findings document remains a package-level deliverable. Do not create native tasks, ledgers or pass receipts merely to imitate an executed pipeline. Draft governance can be authored from authorized principles when the CLI is missing, but must not be represented as an executed native workflow. Existing host coordination stays in its canonical host location.

## Native preparation

The native contract below preserves 2.4.0's functional paths. Source requirements/design/intent remain preserved input versions, separately identified from generated operational artifacts. Do not maintain two independently editable authorities after conversion. Existing native packs remain valid intake; never rewrite them simply to fit a newer serialization.

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

Specify reads requirements and intent under the constitution. Plan reads generated spec and constitution plus design and intent guidance. Tasks reads spec, plan, governance and relevant contracts. Analyze checks the resulting tree and source traceability. Inspect actual installed command spelling. For a preparation-only request, finish checks and handoff, then STOP: no implementation, launch or extension transition. Record implementation as not authorized and leave tasks unchecked. A reset does not change this authority.

Create conditional supporting artifacts when the domain or installed template requires them: research.md, data-model.md, contracts/, quickstart.md, requirements-quality checklists, experience.md, mockups/screenshots, reusable plays, substrate self-location and evaluator-only held-out fixtures. Preserve already supplied supporting files regardless of whether they match one of these names. Mark unknown or unreadable content explicitly.

AGENTS.md should reference the authoritative constitution and contain the session's enforceable read order and gate procedure. Do not paste a second independently editable constitution into it. Preserve existing instructions; add the project-specific gates narrowly. CLAUDE.md may import AGENTS.md when that is the repository convention; other integrations use their own installed instruction loaders.

Task acceptance gates are procedures that must be executed, not just checkbox text. Verify the installed prerequisite checker and artifact analysis before issuing a preparation pass. Custom requirements-quality checklist marks are reviewer decisions, distinct from implementation completion. A later fresh harness verifies receipt hashes again so artifact changes invalidate stale preparation evidence.

Spec Kit references checked 2026-10-14: https://github.github.com/spec-kit/reference/agentic-sdd.html. Tests for implementation tasks are added when requested or needed for their acceptance, rather than mirrored automatically for every reversible change.

## Delivery manifest and gate

Create one package-level delivery.json for an input handoff or native preparation. `scripts/spec-prep-delivery.py PACKAGE_ROOT` verifies this interface; it never launches anything. A missing CLI does not select standalone. If native execution is unavailable, finish the input handoff, mark native preparation incomplete in its handoff/status, and name preparation as the next action. Do not label fallback documents native-complete.

The compact input form is:

```json
{
  "schemaVersion": 1,
  "operation": "input-handoff",
  "implementationAuthorized": false,
  "workstreams": [{
    "id": "report",
    "buildRoot": "report",
    "inputRoot": "report/inputs",
    "inputs": {"requirements": "requirements.md", "design": "design.md", "intent": "intent.md"},
    "sourceMap": "intent.md#source-disposition",
    "conversionGuide": "README.md",
    "nextOperation": "specification-preparation",
    "governance": {
      "constitution": ".specify/memory/constitution.md",
      "instructions": "AGENTS.md",
      "handoff": "reset-handoff.md",
      "adapter": "CLAUDE.md"
    }
  }]
}
```

buildRoot/inputRoot are package-relative directories; input paths/sourceMap are relative to inputRoot, and conversionGuide/governance paths are relative to buildRoot. `adapter` is optional. Add one entry per workstream with a separate input trio. Each guide maps requirements/intent to specify and generated spec/constitution/design/intent to plan, then tasks/analyze and the stop boundary. Source-map fragments name a real nonempty disposition heading; semantic preservation still requires review. Conversion guides must name the generated spec and constitution in addition to the input trio and preparation stages.

For native delivery change operation to native-preparation, add per-workstream featureRoot (`specs/001-report`) and receipt (`preparation.json`), and set nextOperation to await-implementation-authorization. For new native deliveries, preserve input snapshots inside buildRoot (for example inputs/) so their receipt hashes cannot escape the build root. Native intent/spec/plan/tasks and required supporting artifacts must exist without unresolved template placeholders; tasks need identified unchecked work and observable gates; actual required gate evidence, final hashes and the stop boundary must agree. New native receipts contain `skill` with version and SHA-256 of the loaded SKILL.md, plus `implementationAuthorized: false`. The delivery checker compares that digest with its adjacent SKILL.md; inspect older-version receipts through the legacy reader instead of relabeling their identity. Hash the conversion guide, named inputs, instructions/adapters and any existing standing/ledger as consumed artifacts. See intake-and-speckit.md for receipt details. Old receipts may be inspected/normalized in memory without pretending they satisfy every new delivery field.

This mechanical delivery gate cannot establish semantic completeness, true evaluator isolation, fresh-harness loading or command execution from prose. Those claims require named evidence. The dependency-free transition reader inspects command fields in standard block-style extensions YAML and project-local Claude settings hooks, not description prose. Known preparation stages/local git commit hooks are accepted; unknown, implementation or multiline/inline hook commands require review or exclusion. Disabled block hooks are skipped. It does not execute hooks or alter configuration. Inert workflow definitions do not execute themselves: their mere presence is not a failure. Do not invoke a full workflow containing implementation as part of preparation. Record any skipped transitions and scope decisions in the normal analysis/handoff evidence; arbitrary custom scripts cannot be proven safe by token matching. Optional Jev does not affect mandatory delivery checks.

The delivery check rejects obvious template stubs and conflicting positive implementation authorization, but cannot establish semantic completeness or authenticity of workflow evidence from bytes alone. Do not treat valid:true as a replacement for required semantic analyze/source review. The raw checkout may retain historical nested source evidence; export only the canonical root files, references, scripts and tests, excluding nested skill copies, caches and earlier archives.
