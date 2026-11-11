---
title: Artifact contract
tags: [spec-prep]
---

# Artifact contract

## Contents

- [Canonical artifact contract](#canonical-artifact-contract)
- [OpenSpec, Kiro and other toolchains](#openspec-kiro-and-other-toolchains)
- [Optional default project workbench](#optional-default-project-workbench)
- [Optional repository bootstrap](#optional-repository-bootstrap)

## Canonical artifact contract

Read when deciding what to produce from ideation. Do not add a file merely to reproduce another file's contents.

### Compact input handoff

Each workstream has one complete requirements.md (observable behavior/acceptance), design.md (mechanisms, data, interfaces and decisions) and intent.md (goals, constraints, stories and source authority). These are the obvious entry point, not three indexes to dozens of missing chapters. Put hardware profiles, decisions and contracts in the owning core document unless a necessary appendix/format justifies separation. Keep the input-root Markdown entry surface to the named trio; linked subordinate appendices belong under appendices/, not as extra mandatory peer documents. The one other Markdown file allowed in the input root is a `README.md` conversion or read-order guide: it routes readers to the trio and is not a competing entry document. Each workstream uses a distinct buildRoot. Existing native packs are intake sources rather than fabricated input-handoff outputs. Preserve original attachments under sources/ and map material needs once. Do not omit source depth to reduce file count or emit every conditional template.

Governance is retained alongside the core trio: `.specify/memory/constitution.md`, build-root AGENTS.md and reset-handoff.md, wired as `references/intake-and-speckit.md#constitution-and-task-gates` describes. The constitution governs specifications, plan/task decisions and their gates. Verify actual selected-harness loading when claiming reset readiness; a pointer alone is not an observed fresh-session read.

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
explicitly, not denied implicitly. Declaring a directory (for example `data/`)
declares everything under it.

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

Source requirements/design/intent remain preserved input versions, separately identified from generated operational artifacts. Do not maintain two independently editable authorities after conversion. Existing native packs remain valid intake; never rewrite them simply to fit a newer serialization.

| Role | Default location | Purpose |
| --- | --- | --- |
| Intake | project-intake.json | Preserved source inventory, identity, read order and format findings |
| Workbench | workbench.json, unless opted out | Configuration and artifact pointers; derived display rather than another specification |
| Intent | specs/<feature>/intent.md (an input handoff keeps it in the input root) | Why, goals, scope, constraints, success/failure conditions and human intent |
| Specification | specs/<feature>/spec.md | What, requirements, user stories, observable acceptance and eval bindings |
| Plan | specs/<feature>/plan.md | How, derived architecture and implementation decisions |
| Tasks | specs/<feature>/tasks.md | Dependency-ordered work, owned paths, acceptance gates and recovery |
| Constitution | .specify/memory/constitution.md | Project principles and mandatory gates |
| Session instructions | AGENTS.md in the actual build root | Required read order, constitution reference, task gates and initiation boundary |
| Provenance and traceability | Intake/source disposition map plus traceability.md when useful | Source → intent/story → clause/eval → plan/task → evidence; no silently dropped material |
| Preparation evidence | preparation.json | Actual gate results and hashes of the consumed artifact versions |
| Fresh-session handoff | reset-handoff.md | Build root, current authority, validated inputs, unresolved items and next authorized task |
| Continuity | Declared spec-prep ledger/standing or linked Living Documents context | Decisions, outcomes and resumable state under one declared authority |

Existing requirements.md and design.md are accepted inputs or existing naming conventions. For native Spec Kit preparation, their roles resolve to spec.md and plan.md. Context.md is retained only as a source, an alternate standalone plan or additional derivation rationale. The stage order, and what each stage reads, is owned by `references/intake-and-speckit.md#specification-preparation`.

Create conditional supporting artifacts when the domain or installed template requires them: research.md, data-model.md, contracts/, quickstart.md, requirements-quality checklists, experience.md, mockups/screenshots, reusable plays, substrate self-location and evaluator-only held-out fixtures. Preserve already supplied supporting files regardless of whether they match one of these names. Mark unknown or unreadable content explicitly.

Task acceptance gates are procedures that must be executed, not just checkbox text. Verify the installed prerequisite checker and artifact analysis before issuing a preparation pass. Custom requirements-quality checklist marks are reviewer decisions, distinct from implementation completion. A later fresh harness verifies receipt hashes again so artifact changes invalidate stale preparation evidence.

Spec Kit references checked 2026-10-14: https://github.github.com/spec-kit/reference/agentic-sdd.html. Tests for implementation tasks are added when requested or needed for their acceptance, rather than mirrored automatically for every reversible change.

### Delivery manifest and gate

Create one package-level delivery.json for an input handoff or native preparation, and check it with `scripts/spec-prep-delivery.py` (commands in SKILL.md "How to run the gates"); the checker never launches anything. When native execution is unavailable, SKILL.md Phase 0 applies: finish the input handoff and mark native preparation incomplete. Do not label fallback documents native-complete.

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
    "reviewedHooks": [
      {"command": "npx prettier --write specs", "review": "formats Markdown only; launches nothing"}
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

`priorArt.status` is `done`, `directed` or `waived` (see the prior-art gate in SKILL.md); `record` points at the record, the directive, or the waiver reason. A record file is resolved relative to inputRoot, else relative to buildRoot (for example `sources/prior-art.md`), and must stay inside buildRoot. `supporting` lists declared supporting material with its role from the table above; it is optional and never exhaustive of what may be preserved. Each `supporting` path is relative to inputRoot, must resolve inside buildRoot and must appear in the source-disposition map; evaluator-only fixtures in the external store are not listed, because the implementer must not read them. Both fields are additive: older manifests without them remain valid intake, and the prior-art gate then checks the source-disposition map instead.

buildRoot/inputRoot are package-relative directories; input paths/sourceMap are relative to inputRoot, and conversionGuide/governance paths are relative to buildRoot. `adapter` is optional. Add one entry per workstream with a separate input trio. Each guide maps requirements/intent to specify and generated spec/constitution/design/intent to plan, then tasks/analyze and the stop boundary. Source-map and record fragments name a real heading, matched by its GitHub slug with any leading section number ignored, so `intent.md#prior-art` resolves the template's `## 10. Prior art` (`intent.md#10-prior-art` also does); `scripts/spec-prep-validate.py --source-map` uses the same rule. A source-map heading must be a nonempty disposition section; semantic preservation still requires review. Conversion guides must name the generated spec and constitution in addition to the input trio and preparation stages.

For native delivery change operation to native-preparation, add per-workstream featureRoot (`specs/001-report`) and receipt (`preparation.json`), and set nextOperation to await-implementation-authorization. For new native deliveries, preserve input snapshots inside buildRoot (for example inputs/) so their receipt hashes cannot escape the build root. Native intent/spec/plan/tasks and required supporting artifacts must exist without unresolved template placeholders; tasks need identified unchecked work and observable gates; actual required gate evidence, final hashes and the stop boundary must agree. New native receipts contain `skill` with version and SHA-256 of the loaded SKILL.md, plus `implementationAuthorized: false`, and the five gates of step 10 below, including `validation` with the spec-prep-validate command, `exitStatus` 0 and every check's result. The delivery checker compares that digest with the SKILL.md beside it; a receipt made under another release fails that comparison and is checked with that release's checker or re-prepared, never relabeled. The checker also reads older list-form receipts through an in-memory normalization that infers roles only from unique filenames. Hash the conversion guide, named inputs, instructions/adapters and any existing standing/ledger as consumed artifacts. See `references/intake-and-speckit.md#specification-preparation` (step 10) for receipt details.

This mechanical gate cannot establish semantic completeness, true evaluator isolation, fresh-harness loading or command execution from prose; those claims require named evidence. The checker inspects the command fields of enabled hooks in `.specify/extensions.yml` and in project-local `.claude/settings.json` and `.claude/settings.local.json`, not description prose. Known Spec Kit preparation stages and its git commit hook pass; any other command, and any prompt or agent hook, fails until it is removed, disabled or reviewed under `references/intake-and-speckit.md#stop-gate`. Record a review in the workstream's optional `reviewedHooks` list: each entry has `command` (the hook's exact command text, or a prompt or agent hook's prompt text) and `review` (a one-line note on what it does and why it cannot start implementation). A listed hook passes. A hook whose command mentions implement cannot be admitted by review; remove it or set `enabled: false`. It does not execute hooks or alter configuration.

The checker rejects obvious template stubs and conflicting positive implementation authorization. A clarification marker that states its question (`[NEEDS CLARIFICATION: <question>]`, Spec Kit's form) is a listed open item and passes in inputs and native outputs; a bare `[NEEDS CLARIFICATION]` is a stub. The delivery summary lists every remaining marker (SKILL.md Phase 6). Do not treat `valid: true` as a replacement for the required semantic analyze and source review. When exporting this skill, ship SKILL.md, references/, scripts/ and tests/, excluding nested skill copies, caches and earlier archives.

## OpenSpec, Kiro and other toolchains

spec-prep artifacts are plain Markdown. Spec Kit preparation is owned by `references/intake-and-speckit.md#intake-staging-and-spec-kit-preparation`; these mappings cover the other structures SKILL.md Phase 0 detects. Inspect the installed CLI for exact command syntax.

- **OpenSpec.** `intent.md` and `spec.md` map to the proposal and the `specs/` capabilities, using the SHALL and MUST language of the spec template; `context.md` maps to `design.md`; plays map to the change tasks; the ledger and substrate files travel beside the change directory. Next step: initialize OpenSpec, then propose the change from the intent and spec.
- **Kiro.** `intent.md` and `spec.md` load as spec input and `context.md` is the technical plan. Kiro's living specs overlap the ledger only partly; keep the spec-prep ledger as the continuity record because it is append-only.
- **Cursor and generic agents.** Every file is self-contained Markdown with no tool-specific syntax. Hand the tree to any Markdown-reading agent with the read order in SKILL.md Phase 7.

## Optional default project workbench

Use this during intake staging or specification preparation unless the user opts out. It does not replace the intake or preparation contracts.

### Default and boundaries

Workbench mode is `auto` by default: create or update a lightweight `workbench.json` in the intake folder, reuse a compatible existing workbench, and register it with an already available renderer when supported. `on` explicitly requests that integration. `off` omits workbench generation; it does not delete an existing workbench. Do not install a renderer, start a service, launch a terminal or initiate implementation merely to create this file.

`project-intake.json` owns project identity, ideation sources, read order, findings and intake lifecycle. `workbench.json` points to it and records presentation/configuration choices, actual artifact locations and optional integration preferences. The renderer derives displayed state from the intake, prepared artifact files and preparation receipt. Never mirror editable requirements, task statuses or a second lifecycle field into the workbench.

### Write and check

Once the intake manifest is valid, write `workbench.json` beside it. `references/workbench.schema.json` is the contract; follow every required key in it, including `additionalFiles` and `integrations.livingDocuments.mode`, rather than a paraphrase. List each existing recognized artifact (the roles in the native preparation table above, plus any other role that exists) with its role, scope (`intake` or `build`), path and use (`source` or `operational`). Intake paths are relative and stay inside the intake folder. Build pointers require an explicitly resolved `buildRoot`, so add them only after the real build root is resolved. Never create a pretend spec, change task state or generate a preparation receipt to fill a pointer. Preserve custom configuration and valid existing mappings; repair an invalid existing workbench rather than silently overwriting it. Never add secrets, raw eval contents or credentials.

Check the file against the schema with a JSON Schema validator the host already has, or by hand: every required key present, every enum value allowed, and every pointer path existing.

### Additional files

Discover additional visible files dynamically. Preserve transcripts, screenshots, diagrams, mockups, research, prototype code, spreadsheets, PDFs and unknown formats as source evidence. Role inference from a filename is advisory, not authority. Classify each material source as incorporated, deferred, rejected, superseded, duplicate or unresolved during preparation, with its provenance and reason. Unsupported extraction is visible in findings; do not lose the original or treat unread content as examined.

Exclude version-control internals, dependency caches, machine secrets and external symlink traversal from automatic discovery. Archives are inert until the explicit safe staging extraction operation. Held-out evaluation payloads remain external and only a handling pointer appears in the workbench.

Workbench configuration is independent of a renderer. A source pointer in an existing spec pack is not proof that the project has completed native Spec Kit preparation.

### Optional integration

Keep Living Documents mode in the workbench as `auto`, `on` or `off`. Read `references/continuity.md#optional-living-documents-integration` only when requested, detected or required by the host instructions. That file defines setup, authority and continuity behavior. An absent optional integration never blocks independent spec preparation. Current scoped instructions can make an integration mandatory; the portable default does not override them.

## Optional repository bootstrap

When preparing specifications, inspect the selected build directory before creating anything. Skip each item already completed. A supplied repository is the target; never create a second repository just because it lacks one optional file.

Resolve project name, description, local build path, license, ignore rules and hosting separately. Derive the name and description from explicit intake metadata when clear. If the user requested repository setup and the directory is not in a Git repository, initialize locally with git init --initial-branch=main <build-path>. Detect parent repositories first; do not create an unintended nested repository. Preserve existing branch and remote settings. Do not commit, push or rewrite history as an incidental setup step.

For a new local repository, record its human-readable description in .git/description and its project name and purpose in README.md. Preserve an existing README and existing meaningful description; add only missing information. Local repository naming comes from the chosen directory. Do not rename a preexisting directory to match an inferred label.

If LICENSE already exists, inspect and retain it. If an explicit SPDX license choice exists, obtain the standard license text from its official source and use the authorized copyright holder and year. If ownership or license choice is ambiguous, ask a targeted question; the safe default is no licensing declaration. Do not silently choose a permissive license, or copy another project's license. A request to stage intake does not require answering license questions yet.

Generate or extend .gitignore using the derived stack and current primary templates, preserving existing rules. Cover generated outputs, dependency caches, local environment/credential files, machine state and private fixtures appropriate to this project. Do not ignore source contracts, lockfiles or spec artifacts indiscriminately. Verify representative rules with git check-ignore --no-index, and inspect git status so necessary files remain trackable.

Remote hosting is optional and separate from local initialization. If requested, resolve provider, account/organization, repository name, description, visibility and license before creation. A remote repository creation or first push is a publishing action: the current request must authorize its exact target. Ask only when that target or visibility is ambiguous. Never infer a public repository or transmit source code from local setup authority.

Record completed/skipped choices and local verification in the preparation handoff. Repository creation does not initiate implementation.
