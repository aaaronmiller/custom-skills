---
title: Artifact contract
version: "4.0.0"
tags: [spec-prep]
---

# Artifact contract

## Contents

- [Canonical artifact contract](#canonical-artifact-contract)
- [Compatibility and Handoff](#compatibility-and-handoff)
- [Optional default project workbench](#optional-default-project-workbench)
- [Optional repository bootstrap](#optional-repository-bootstrap)
- [Project constitution and task gates](#project-constitution-and-task-gates)

## Canonical artifact contract

*Formerly `#canonical-artifact-contract`, version 2.6.0.*

Read when deciding what to produce from ideation. This consolidates the artifact naming/mapping guidance previously spread across the core table and compatibility reference. Do not add a file merely to reproduce another file's contents.

### Compact input handoff

Each workstream has one complete requirements.md (observable behavior/acceptance), design.md (mechanisms, data, interfaces and decisions) and intent.md (goals, constraints, stories and source authority). These are the obvious entry point, not three indexes to dozens of missing chapters. Put hardware profiles, decisions and contracts in the owning core document unless a necessary appendix/format justifies separation. Keep the input-root Markdown entry surface to the named trio; linked subordinate appendices belong under appendices/, not as extra mandatory peer documents. Each workstream uses a distinct buildRoot. Existing native packs are intake sources rather than fabricated input-handoff outputs. Preserve original attachments under sources/ and map material needs once. Do not omit source depth to reduce file count or emit every conditional template.

Governance is retained alongside the core trio: `.specify/memory/constitution.md`, build-root AGENTS.md and reset-handoff.md. AGENTS.md must instruct a fresh session to read the constitution and handoff before changes. Add the selected harness's supported project-local adapter, for example CLAUDE.md containing `@AGENTS.md`, when needed. The constitution governs specifications, plan/task decisions and their gates. Verify actual selected-harness loading when claiming reset readiness; a pointer alone is not an observed fresh-session read.

An input handoff includes a concise conversion/read-order guide and source-disposition mapping (an intent appendix is sufficient). A separately requested findings document remains a package-level deliverable. Do not create native tasks, ledgers or pass receipts merely to imitate an executed pipeline. Draft governance can be authored from authorized principles when the CLI is missing, but must not be represented as an executed native workflow. Existing host coordination stays in its canonical host location.

### Supporting material

Every artifact list in this contract is a minimum shape, not a whitelist.
Deliverables may and often do carry material that informs the project without
being a functional requirement of it. Preserve all of it; never omit an item
because its kind is not named here.

| Role | Examples | Typical home |
| --- | --- | --- |
| analysis-input | datasets, raw snapshots, measurement tables, corpora | `data/` |
| reference | papers, vendor docs, benchmark descriptions, competitor notes | `references/` or `sources/` |
| evidence | prior-art record, interview notes, logs, screenshots | `sources/` |
| fixture | sample inputs, golden outputs, evaluator-only cases (external store) | `fixtures/` or the eval store |
| project-specific | anything else this project needs that no role above fits | any declared path |

**Exception clause.** Any other project-specific resource is permitted. The
only obligation is to declare it: one line in the source-disposition map with
path, role, and why it matters. An undeclared item is a drift finding to fix
by declaring it, never a reason to delete it. Edge cases are supported
explicitly, not denied implicitly.

The input-root entry surface stays the named trio. Supporting directories sit
beside `inputs/` (for example `data/`, `references/`, `sources/`) and are
linked from the trio, not promoted to peer entry documents.

**Data section.** When data is a significant share of pre-development work,
include `data/README.md` as the data section, linked from design.md:

1. Sources: each source, its kind (vendor, independent, aggregator, derived),
   acquisition method, retrieval date, and known gaps.
2. Raw layout: immutable raw snapshots with a manifest of hashes; derived
   stores are rebuildable from raw and need not be committed.
3. Data dictionary: each table or file, its grain, keys and fields.
4. Derivation rules: every computed value, its formula and its basis; values
   with different bases are labelled and never pooled silently.
5. Quality flags: verification status, sampling caveats, missing coverage.

Data informs requirements but is not one. Behavior over data (what must be
computed, reported or rejected) belongs in requirements.md; storage and
derivation mechanics belong in design.md and later plan or data-model.md.

### Native preparation

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

### Delivery manifest and gate

Create one package-level delivery.json for an input handoff or native preparation. Verify this interface against the artifact contract; it never launches anything. A missing CLI does not select standalone. If native execution is unavailable, finish the input handoff, mark native preparation incomplete in its handoff/status, and name preparation as the next action. Do not label fallback documents native-complete.

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
    "priorArt": {"status": "done", "record": "intent.md#prior-art"},
    "supporting": [
      {"path": "../data/README.md", "role": "analysis-input", "why": "data section"}
    ],
    "governance": {
      "constitution": ".specify/memory/constitution.md",
      "instructions": "AGENTS.md",
      "handoff": "reset-handoff.md",
      "adapter": "CLAUDE.md"
    }
  }]
}
```

`priorArt.status` is `done`, `directed` or `waived` (see the prior-art gate in SKILL.md); `record` points at the record, the directive, or the waiver reason. `supporting` lists declared supporting material with its role from the table above; it is optional and never exhaustive of what may be preserved. Both fields are additive: older manifests without them remain valid intake, and the prior-art gate then checks the source-disposition map instead.

buildRoot/inputRoot are package-relative directories; input paths/sourceMap are relative to inputRoot, and conversionGuide/governance paths are relative to buildRoot. `adapter` is optional. Add one entry per workstream with a separate input trio. Each guide maps requirements/intent to specify and generated spec/constitution/design/intent to plan, then tasks/analyze and the stop boundary. Source-map fragments name a real nonempty disposition heading; semantic preservation still requires review. Conversion guides must name the generated spec and constitution in addition to the input trio and preparation stages.

For native delivery change operation to native-preparation, add per-workstream featureRoot (`specs/001-report`) and receipt (`preparation.json`), and set nextOperation to await-implementation-authorization. For new native deliveries, preserve input snapshots inside buildRoot (for example inputs/) so their receipt hashes cannot escape the build root. Native intent/spec/plan/tasks and required supporting artifacts must exist without unresolved template placeholders; tasks need identified unchecked work and observable gates; actual required gate evidence, final hashes and the stop boundary must agree. New native receipts contain `skill` with version and SHA-256 of the loaded SKILL.md, plus `implementationAuthorized: false`. The delivery checker compares that digest with its adjacent SKILL.md; inspect older-version receipts through the legacy reader instead of relabeling their identity. Hash the conversion guide, named inputs, instructions/adapters and any existing standing/ledger as consumed artifacts. See references/intake-and-speckit.md#intake-staging-and-spec-kit-preparation for receipt details. Old receipts may be inspected/normalized in memory without pretending they satisfy every new delivery field.

This mechanical delivery gate cannot establish semantic completeness, true evaluator isolation, fresh-harness loading or command execution from prose. Those claims require named evidence. The dependency-free transition reader inspects command fields in standard block-style extensions YAML and project-local Claude settings hooks, not description prose. Known preparation stages/local git commit hooks are accepted; unknown, implementation or multiline/inline hook commands require review or exclusion. Disabled block hooks are skipped. It does not execute hooks or alter configuration. Inert workflow definitions do not execute themselves: their mere presence is not a failure. Do not invoke a full workflow containing implementation as part of preparation. Record any skipped transitions and scope decisions in the normal analysis/handoff evidence; arbitrary custom scripts cannot be proven safe by token matching. Optional Jev does not affect mandatory delivery checks.

The delivery check rejects obvious template stubs and conflicting positive implementation authorization, but cannot establish semantic completeness or authenticity of workflow evidence from bytes alone. Do not treat valid:true as a replacement for required semantic analyze/source review. The raw checkout may retain historical nested source evidence; export only the canonical root files, references, scripts and tests, excluding nested skill copies, caches and earlier archives.

## Compatibility and Handoff

*Formerly `#compatibility-and-handoff`, version 1.0.0.*

spec-prep artifacts are plain markdown and feed directly into existing spec-driven toolchains. The mapping below also shows what spec-prep adds that those tools do not have.

### SpecKit

For the current preparation pipeline and native artifact paths, read `references/intake-and-speckit.md#intake-staging-and-spec-kit-preparation`. That 2.2 reference supersedes this legacy mapping.

For new native preparation, requirements.md plus intent.md feed specify under the constitution; generated spec.md plus constitution, design.md and intent guidance feed plan. Preserve native stories and scenarios, then generate tasks and analyze. Read references/intake-and-speckit.md#intake-staging-and-spec-kit-preparation for the actual procedure. Do not feed an already-generated spec back into specify as raw intake or duplicate an operational plan. Existing legacy context/design sources remain accepted. The input trio is the compact interface; generated native artifacts and governance are separate outputs.

### OpenSpec

`intent.md` and `spec.md` map to the proposal and `specs/` capabilities, using SHALL and MUST language already present in the spec template. `context.md` maps to `design.md`. Plays map to the change tasks. The ledger and substrate files travel alongside the OpenSpec change directory.

### Kiro

Both `intent.md` and `spec.md` load as Kiro spec input. `context.md` is the technical plan. Kiro's living-specs concept is a partial overlap with the spec-prep ledger; keep the spec-prep ledger as the authoritative continuity record because it is append-only and carries the backward feed into Context Crafting, which living specs do not.

### Cursor and generic agents

All files are self-contained markdown with no tool-specific syntax. Any agent that reads markdown can consume the tree.

### Handoff protocol

A fresh session reads AGENTS.md, the constitution and reset handoff first. Read existing standing/ledger and verify receipt hashes when present, then intent and the applicable native spec/plan/task. An input handoff does not need a fabricated ledger or native pass. Preparation-only status survives reset: stop before implementation until the user explicitly authorizes it. The handoff must supply the context needed without the authoring conversation.

### Next-step commands

Spec Kit: inspect installed syntax/integration and existing tree, initialize safely only when needed, then run constitution/specify/clarify/plan/tasks/analyze with the source mapping above. Finish the reset handoff and stop before implementation for a preparation-only request.
OpenSpec: `openspec init` then `/opsx:propose` with the intent and spec.
Kiro: load `intent.md` and `context.md` into the spec workflow.
Direct: hand the tree to any markdown-reading coding agent and point it at `standing.md` first.

## Optional default project workbench

*Formerly `#optional-default-project-workbench`, version 2.3.0.*

Use this reference during intake staging or specification preparation unless the user opts out. It adds the workbench integration that 2.2 lacked; it does not replace the intake or preparation contracts.

### Default and boundaries

Workbench mode is `auto` by default: create or update a lightweight `workbench.json` in the intake folder, reuse a compatible existing workbench, and register it with an already available renderer when supported. `on` explicitly requests that integration. `off` omits workbench generation; it does not delete an existing workbench. Do not install a renderer, start a service, launch a terminal or initiate implementation merely to create this file.

`project-intake.json` owns project identity, ideation sources, read order, findings and intake lifecycle. `workbench.json` points to it and records presentation/configuration choices, actual artifact locations and optional integration preferences. The renderer derives displayed state from the intake, prepared artifact files and preparation receipt. Never mirror editable requirements, task statuses or a second lifecycle field into the workbench.

The default artifact set is intent, native specification, native plan, gated tasks, project constitution, agent instructions, traceability/provenance and reset handoff with preparation evidence. Requirements/design files supplied by ideation remain preserved inputs. Do not generate requirements.md beside spec.md, or design.md beside plan.md, with duplicate independently editable content. Context rationale, UX, data models, contracts, research, quality checklists and playbooks are additional roles when they add value or the selected toolchain requires them.

### Generate and check

After establishing a valid intake manifest, run the bundled helper:

```bash
Write the workbench pointers for the intake folder (mode auto), then check them.
```

When the real build root has been resolved, repeat `write` with `--build-root <actual-build-root>`. The helper lists existing recognized artifacts as source or operational pointers. It never creates a pretend spec, changes task state or generates a successful preparation receipt. It preserves custom configuration and existing valid artifact mappings. An invalid existing workbench requires repair rather than silent overwrite.

The schema is `references/workbench.schema.json`. It uses schemaVersion 1, kind `spec-prep-workbench`, intake `project-intake.json`, a mode, optional buildRoot, an artifacts array and a Living Documents mode. Artifact entries declare role, scope (`intake` or `build`), path and use (`source` or `operational`). Intake paths are relative and remain inside their intake folder. Build pointers require an explicitly resolved buildRoot. Never add secrets, raw eval contents or credentials.

### Additional files

Discover additional visible files dynamically. Preserve transcripts, screenshots, diagrams, mockups, research, prototype code, spreadsheets, PDFs and unknown formats as source evidence. Role inference from a filename is advisory, not authority. Classify each material source as incorporated, deferred, rejected, superseded, duplicate or unresolved during preparation, with its provenance and reason. Unsupported extraction is visible in findings; do not lose the original or treat unread content as examined.

Exclude version-control internals, dependency caches, machine secrets and external symlink traversal from automatic discovery. Archives are inert until the explicit safe staging extraction operation. Held-out evaluation payloads remain external and only a handling pointer appears in the workbench.

Workbench configuration is independent of a renderer. The assignment catalog is one adapter: it reads the manifest and presents artifact pointers alongside its live folder inventory. A source pointer in an existing spec pack is not proof that the project has completed native Spec Kit preparation.

### Optional integration

Keep Living Documents mode in the workbench as `auto`, `on` or `off`. Read `references/continuity.md#optional-living-documents-integration` only when requested, detected or required by the host instructions. That file defines setup, authority and continuity behavior. An absent optional integration never blocks independent spec preparation. Current scoped instructions can make an integration mandatory; the portable default does not override them.

## Optional repository bootstrap

*Formerly `#optional-repository-bootstrap`, version 2.2.0.*

When preparing specifications, inspect the selected build directory before creating anything. Skip each item already completed. A supplied repository is the target; never create a second repository just because it lacks one optional file.

Resolve project name, description, local build path, license, ignore rules and hosting separately. Derive the name and description from explicit intake metadata when clear. If the user requested repository setup and the directory is not in a Git repository, initialize locally with git init --initial-branch=main <build-path>. Detect parent repositories first; do not create an unintended nested repository. Preserve existing branch and remote settings. Do not commit, push or rewrite history as an incidental setup step.

For a new local repository, record its human-readable description in .git/description and its project name and purpose in README.md. Preserve an existing README and existing meaningful description; add only missing information. Local repository naming comes from the chosen directory. Do not rename a preexisting directory to match a inferred label.

If LICENSE already exists, inspect and retain it. If an explicit SPDX license choice exists, obtain the standard license text from its official source and use the authorized copyright holder and year. If ownership or license choice is ambiguous, ask a targeted question; the safe default is no licensing declaration. Do not silently choose a permissive license, or copy another project's license. A request to stage intake does not require answering license questions yet.

Generate or extend .gitignore using the derived stack and current primary templates, preserving existing rules. Cover generated outputs, dependency caches, local environment/credential files, machine state and private fixtures appropriate to this project. Do not ignore source contracts, lockfiles or spec artifacts indiscriminately. Verify representative rules with git check-ignore --no-index, and inspect git status so necessary files remain trackable.

Remote hosting is optional and separate from local initialization. If requested, resolve provider, account/organization, repository name, description, visibility and license before creation. A remote repository creation or first push is a publishing action: the current request must authorize its exact target. Ask only when that target or visibility is ambiguous. Never infer a public repository or transmit source code from local setup authority.

Record completed/skipped choices and local verification in the preparation handoff. Repository creation does not initiate implementation.

## Project constitution and task gates

*Formerly `#project-constitution-and-task-gates`, version 2.2.0.*

This 2.2 procedure supersedes the bundled 2.1 instruction to never create a constitution. The current user authorized spec-prep to create a project-local constitution through Spec Kit during specification preparation.

Resolve governance from the existing `.specify/memory/constitution.md`, a declared project constitution, or an explicitly supplied `$spec-prep_CONSTITUTION`. Preserve project-owned principles. Another project's constitution is reference material only; do not automatically inherit its technology choices or policy.

If absent, run the installed Spec Kit constitution workflow using the source's explicit principles and authorized project constraints. Resolve material ambiguities through targeted questions when they block preparation. The authoritative file is `.specify/memory/constitution.md`; other locations point to it rather than creating editable copies.

The constitution and session instructions require each task to cite its requirement/story, state its dependencies, name its acceptance gate and supply evidence before completion. Meaningful risky changes include recovery. Unresolved critical analysis findings prevent initiation. Producing specs or tasks does not authorize implementation.

Extend existing scoped AGENTS.md/CLAUDE.md/AGENT.md files narrowly and preserve operator work. Point fresh harnesses at the real build root and reset-handoff.md. Consult references/intake-and-speckit.md#intake-staging-and-spec-kit-preparation and references/handoff-and-implementation.md#terminal-agnostic-fresh-session-initiation for the named gates and receipt format.
