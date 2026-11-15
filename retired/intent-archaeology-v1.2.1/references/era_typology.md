# Document Era Typology (5 eras)

> **When to read:** before Phase 2 (era classification), or when a
> project's spec archaeology is producing strange results.

## The five eras

The user's project documentation evolved through five eras. Each era has
a different document shape, a different parser, and a different
archaeology procedure. Phase 2 (`02_classify_era.py`) classifies each
project into one era based on the documents present.

### Era 1 — Random markdown (early)

**Documents:** ad-hoc `.md` files, no fixed naming. Often `NOTES.md`,
`PLAN.md`, `TODO.md`, `idea.md`.

**Parser:** none structured. Phase 3 extracts intent by reading the
files in chronological order (git log) and treating each top-level
section as a candidate intent.

**Archaeology difficulty:** high. No spec-kit, no requirements, no
design — just stream-of-consciousness notes. Often the canonical version
is "whatever was committed last before the first coding session".

### Era 2 — PRD files

**Documents:** `prd.md` or `PRD.md` or `prd/<feature>.md`. Often
multiple versions (`prd-v1.md`, `prd-v2.md`, `prd-final.md`,
`prd-final-FINAL.md`).

**Parser:** section-based. PRDs typically have `## Overview`, `## Goals`,
`## Non-Goals`, `## User Stories`, `## Technical Approach`. Phase 3
extracts the non-goals section explicitly — it's where abandoned scope
lives.

**Archaeology difficulty:** medium. Multiple versions are the issue.
Phase 3 uses `cass search "prd" --workspace <path> --json` to find
sessions where a PRD was attached, then takes the version that was live
at the time of the first `/specify.plan` or first coding session.

### Era 3 — requirements.md + design.md

**Documents:** `requirements.md` (the "what" and "why"), `design.md`
(the "how"). spec-kit's `/specify.init` produces these.

**Parser:** spec-kit-aware. `requirements.md` has structured
`## Requirement:` blocks; `design.md` has `## Design Decision:` blocks.
Phase 3 uses the spec-kit parser.

**Archaeology difficulty:** low-medium. spec-kit's structure helps, but
multiple versions still exist. Phase 3 searches cass for
`/specify.plan` slash-command invocations to find which version of
`requirements.md` was attached when the plan was made.

### Era 4 — requirements.md + design.md + plans.md + path info + user stories

**Documents:** as Era 3, plus `plans.md` (or `plan.md`), explicit path
information, user stories embedded in `requirements.md`.

**Parser:** spec-kit-aware + plans.md parser. The `plans.md` file
typically has `## Plan:` blocks with dependencies and acceptance
criteria.

**Archaeology difficulty:** low. The structure is rich. Phase 3 still
does version archaeology but the documents are self-describing.

### Era 5 — Living document (v3.1+)

**Documents:** a single living document, typically `LIVING.md` or
`<project>.md`, following the v3.1 format (see
`references/living_document_v3.md`). Has structured ledgers, append-only
worklog, temporal-irrelevant modification allowed (user and model can
work on whatever they need without disrupting the other).

**Parser:** living-document parser. The document is machine-readable:
sections have typed ledgers, the worklog is append-only with timestamps.

**Archaeology difficulty:** **none.** The living document already
carries structured ledgers and an append-only worklog, so its intent is
machine-readable rather than reconstructed. Phase 3 skips archaeology
for era 5 projects and reads the living document directly.

Era 5 is ~2-3% of the user's docs and the newest — which pairs exactly
with newest-first ordering. The first tranche is the cheapest,
highest-fidelity material available, which makes it the right
calibration reference for measuring how well eras 1–4 reconstruct.

## Classification heuristics (Phase 2)

Phase 2 classifies each project by scanning for marker files. The
classifier is conservative: if multiple eras' markers are present
(common during transitions), it picks the **highest** era number and
records the others in `era_overlap` for the audit.

| Marker file(s) present | Era |
|------------------------|-----|
| `LIVING.md` or `*.living.md` with v3.x frontmatter | 5 |
| `requirements.md` + `design.md` + `plans.md` (or `plan.md`) | 4 |
| `requirements.md` + `design.md` | 3 |
| `prd*.md` or `PRD*.md` | 2 |
| any `*.md` with non-trivial content | 1 |
| (no docs) | 0 — flag for Phase 4 to consider as `not-started` |

## What era selection changes downstream

- **Phase 3 (spec archaeology):** era 5 skips archaeology; eras 1-4
  use era-specific parsers.
- **Phase 4 (lifecycle derivation):** era 0 projects are usually
  `not-started` or `archive-candidate`.
- **Phase 7 (three-way join):** era 5 projects have an authoritative
  intent source (the living document), so the join is two-way (spec +
  repo), not three-way.
- **Phase 8 (wiki emission):** era 5 projects get a "Living document —
  last updated YYYY-MM-DD" badge; other eras get "Reconstructed from
  <era> documents".
