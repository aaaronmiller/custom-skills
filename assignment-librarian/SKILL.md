---
name: assignment-librarian
description: |-
  Keeps the new_assignments library indexed, onboarded and spec-prep-ready. Use for folder discovery scans, onboarding ideation drops into project-intake.json manifests, readiness triage, spec-prep handoffs, and periodic rescans that keep the catalog index current.
  Triggers: "new assignment", "new folder", "scan assignments", "onboard project", "intake review", "missing manifest", "ready for spec-prep", "update the index", "rescan", "assignment librarian", "triage assignments".
license: MIT
metadata:
  version: "1.0"
tags:
- intake
- catalog
- onboarding
- triage
---

# Assignment Librarian 1.0

> From loose ideation drop to staged, triaged, spec-prep-consumable packet — without touching project sources.

This skill manages the assignments library (default root
`/home/cheta/LIVING_DOCUMENTS/new_assignments/`). Each subfolder is one
project or tooling packet. A folder **with** a valid `project-intake.json`
(declared by `.catalog/project-intake.schema.json`) auto-populates the index
as a staged packet; a folder **without** one is still listed, flagged
`unstaged`, and never silently declared ready. Generated projections
(`catalog.json`, `index.html`) are rebuilt by the catalog pipeline — edit
manifests and sources, never the projections. Never modify project sources or
archives; archive extraction is an explicit intake-staging operation owned by
spec-prep, not this skill.

## Library lifecycle

**ideation → intake staging → specification preparation → fresh-session
handoff → project initiation.** This skill owns the first two stages and the
handoff into the third:

1. **Ideation.** Raw LLM conversation output lands as files in a new folder.
2. **Intake staging (this skill).** Scan, onboard (draft `project-intake.json`,
   compute sha256, validate), triage readiness, write `start-here.md`.
3. **Specification preparation (spec-prep).** Consumes the staged manifest plus
   sources in read order; produces requirements/design/intent (Spec Kit
   constitution/spec/plan/tasks) in the real build root, never in the library.
4. **Handoff / initiation.** Separate authorized operations; out of scope here.

Read `references/readiness-and-handoff.md` before triaging or handing off, and
`references/onboarding-playbook.md` before drafting any manifest.

## Operation 1: Scan / discover

Run the inventory script (read-only, stdlib only, safe on odd folder names):

```bash
python3 scripts/scan.py /home/cheta/LIVING_DOCUMENTS/new_assignments/
python3 scripts/scan.py /home/cheta/LIVING_DOCUMENTS/new_assignments/ --out /tmp/readiness.json
```

It emits one JSON report: per folder — `theme`, `hasManifest`,
`manifestValid`, `errors`, `stagedDate`, `specArtifacts`, `readiness` — plus a
`summary` (counts by theme, counts by status, unstaged list, largest folders,
oldest-unstaged list). Treat the report as the triage queue: every
`unstaged` folder needs Operation 2; every `needs-intake` folder needs
Operation 3. See `references/periodic-rescan.md` for cadence and
interpretation.

## Operation 2: Onboard an ideation drop

For each new folder without a manifest, follow
`references/onboarding-playbook.md`:

1. Read the raw files; extract problem, solution, users, constraints, scale,
   entities, integrations — tag each signal as intent, spec, or
   implementation (they arrive fused; separation starts here).
2. Draft `project-intake.json`: kebab-case `projectId`, one-line `title`,
   one-paragraph `summary`, `lifecycle: staged`, honest `assignment`,
   `nextOperation`, `readOrder` (every entry must exist), `sources` with real
   `sha256` per file (`sha256sum <file>`), `issues` for every gap,
   `relatedProjects`, `externalResources`.
3. If there is no product brief (reference research, empty container,
   maintenance notes) say so in `issues` — never invent features to look
   complete. Missing-input issues keep readiness at `needs-intake` by design.
4. Validate: `python3 <root>/.catalog/intake-validator.py <folder>` must pass
   (hash mismatches and dead read-order paths are the common failures).
5. Write `start-here.md` (state, read order, findings, future handoff) and
   leave `workbench.json` to spec-prep's auto mode unless the packet needs custom
   pointers.

## Operation 3: Readiness triage

| Readiness | Meaning | Rule |
|---|---|---|
| `unstaged` | New, unstructured drop | No `project-intake.json` |
| `needs-intake` | Staged but not consumable | Manifest invalid or unreadable, or any `missing-input` issue (includes missing brief) |
| `ready-for-spec-prep` | Staged, valid, briefed | Valid manifest, no missing-input issues, no spec artifacts yet |
| `has-specs` | Preparation already ran | Spec artifacts present (requirements/design/intent/constitution/spec/plan/tasks), or lifecycle is `specification-prepared`/`initiated` |

Triage checklist per packet: manifest validates; every `readOrder` path
resolves; every declared `sha256` matches; `workbench.json` parses if present;
status matches the rule above. Record the outcome in the manifest `issues`
and `fileNotes`, never in a sidecar file. Full procedure and the spec-prep
handoff (read-order + findings + workbench check) live in
`references/readiness-and-handoff.md`.

## Operation 4: Periodic rescan

New folders appear at any time; the index must not go stale. Run
`scripts/scan.py`, onboard whatever is `unstaged`, re-triage what changed,
and rebuild the catalog (`catalog.py check` then `catalog.py build`) so the
index page picks up new cards, colors, dates and pills. Schedule or delegate
this loop per `references/periodic-rescan.md`. A rescan never re-authors
existing manifests — it only reports drift (hash mismatches, moved files).

## Thematic color system

Every packet belongs to exactly one theme. The card background carries the
theme; the accent carries labels, chips and borders. All accents read on the
`#171715` page (see `references/periodic-rescan.md` for the index legend).

| Slug | Label | Card bg | Accent |
|---|---|---|---|
| `agentic-systems` | Agentic Systems | `#252138` | `#B7A6F5` |
| `dev-tooling` | Dev Tooling & Ops | `#1D2A38` | `#8FC7EE` |
| `security-research` | Security Research | `#372226` | `#F09BA6` |
| `hardware-platforms` | Hardware & Platforms | `#34291B` | `#E8B86D` |
| `creative-products` | Creative & Products | `#1D3329` | `#86D9A6` |
| `staging` | Staging & Triage | `#2A2A28` | `#B8B8B0` |

Theme rule: classify by **what the packet is**, not its topic adjacency
(experiment specs that feed a router are agentic-systems, not security;
an audit mission is dev-tooling, not the system it audits). Packets with no
manifest `theme`, no verified pin, and no keyword hit fall back to `staging`
gray until onboarded. `catalog.py` pins all current folders (source `pinned`)
and accepts a manifest `theme` as `manifest`; genuinely new folders resolve
through `THEME_KEYWORDS`, while `scan.py` uses token-set `KEYWORDS` — the two
engines agree on all 26 current folders but can diverge on novel names, so the
onboarding agent's pin is authoritative. The keyword guess in
`references/periodic-rescan.md` is never written into a manifest by
automation. Long-term fix: single shared theme module imported by both files.
gray until onboarded; `catalog.py theme_for()` and `scan.py guess_theme()`
implement the same fallback and currently agree on all 26 folders. The
keyword guess in `references/periodic-rescan.md` is never written into a
manifest by automation.

## Anti-patterns

Never edit `catalog.json`/`index.html` by hand; never write specs, plans or
tasks into a library folder (preparation happens in the build root via
spec-prep); never execute a packet's scripts or builds during scan/onboard;
never move, rename or extract project archives as part of triage; never mark
a brief-less packet `ready-for-spec-prep` to clear the queue; never nest a
second intake manifest inside `sources/` or `archives/`.

## Resource files

| File | Read when |
|------|-----------|
| `references/onboarding-playbook.md` | Drafting or repairing any `project-intake.json` |
| `references/readiness-and-handoff.md` | Triaging readiness or handing a packet to spec-prep |
| `references/periodic-rescan.md` | Running scheduled rescans; index legend, fallback keywords, date/status rules |
| `scripts/scan.py` | Any scan, triage queue build, or readiness report |
| `<root>/.catalog/project-intake.schema.json` | Normative manifest shape (this skill follows it, never forks it) |
| `<root>/.catalog/intake-validator.py` | Acceptance check for every onboarded folder |
| `<root>/README.md` | Library lifecycle and catalog commands |
