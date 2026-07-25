# Living Document v3.1 Format

> **When to read:** when a project is era 5, or when generating a
> living document for a `not-started` project.

## Why era 5 needs no archaeology

The living document format (v3.1+) already carries structured ledgers
and an append-only worklog, so its intent is machine-readable rather
than reconstructed. Phase 3 (spec archaeology) skips era 5 projects
and reads the living document directly.

Era 5 is ~2-3% of the user's docs and the newest — which pairs exactly
with newest-first ordering. The first tranche is the cheapest,
highest-fidelity material available, which makes it the right
calibration reference for measuring how well eras 1–4 reconstruct.

## The v3.1 format

A living document is a single markdown file with YAML frontmatter and
structured sections. The key innovation over v2: temporal-irrelevant
modification is allowed. The user and the model can work on whatever
they need without disrupting the other. If an item is blocked, the
model moves to the next unblocked item via the dependency graph. The
user answers questions as they are able, keeping the model active and
unrestricted.

### Frontmatter

```yaml
---
project: my-app
version: "3.1"
created: 2025-01-15
last_modified: 2025-07-23
lifecycle: in-progress
status_vector: {...}                  # machine-maintained
dependencies:                         # cross-project
  - api-server
  - shared-lib
---
```

### Sections

1. **Purpose** — one paragraph, human-authored, rarely changes.
2. **Goals** — bulleted, human-authored, version-controlled in the
   worklog when changed.
3. **Non-Goals** — bulleted, human-authored. This is where abandoned
   scope lives, explicitly.
4. **Open Questions** — bulleted. The model can add questions; the
   user answers when able. Temporal-irrelevant: the model doesn't
   block on answers, it works on what it can.
5. **Decisions** — typed ledger. Each entry has `decision`, `rationale`,
   `decided_by` (user|model), `decided_at`, `supersedes` (optional).
6. **Worklog** — append-only, timestamped. Each entry has `timestamp`,
   `actor` (user|model), `action`, `artifact` (file/commit/PR).
7. **Constitution** — bulleted constraints. Machine-discoverable via
   frequency analysis; human-confirmable.
8. **Backlog** — typed ledger. Each entry has `item`, `status`
   (not-started|in-progress|blocked|done|abandoned), `blocked_by`
   (optional), `depends_on` (optional).

## How the skill reads era 5

Phase 3 (spec archaeology) for an era 5 project:

1. Locate the living document (usually `LIVING.md` or `<project>.md`
   with v3.x frontmatter).
2. Parse the frontmatter, sections 1-3, 5, 7, 8.
3. Skip archaeology — the document is the canon.
4. Record `canonical_prd_path` as the living document path.
5. Record `spec_lineage` as `[{role: "living-document", path:
   <path>, version: <frontmatter.version>}]`.

Phase 7 (three-way join) for an era 5 project:

- The join is two-way (spec + repo), not three-way, because the
  living document is authoritative.
- `drifted` is still possible (the document says X, the repo does Y).
- `superseded` is rare (the document is append-only, but decisions
  can supersede earlier decisions).
- `abandoned` is read directly from the Non-Goals section and the
  Backlog with `status: abandoned`.

## How the skill writes era 5

For `not-started` projects, Phase 3 generates a living document by
analyzing existing (era 1-4) versions and sorting ideas into:

- **Discarded** — bad ideas, explicitly cut
- **Incorporated** — good ideas, in the new Goals section
- **Deferred** — future plans, in the Backlog with `status: not-started`
- **Unresolved** — ideas appearing across versions with contradictory
  treatment and no evidence of a decision. These go to the Open
  Questions section as proposals, NOT to Goals or Non-Goals. Forcing
  them into good/bad manufactures a decision that was never made, and
  the sleep-time agent will act on it.

This four-bucket sort (the fourth `unresolved` bucket was proposed
change #3 from the transcript) is the era 5 generation procedure.

## What changed from v2

v2 living documents required the user and model to coordinate on a
single plan. If the model was blocked on a question, it stopped. v3
introduces temporal-irrelevant modification: the model moves to the
next unblocked item, the user answers questions asynchronously, and
neither blocks the other. This is why v3 documents have an Open
Questions section separate from Goals/Non-Goals — questions don't
block work, they accumulate.

The worklog being append-only is what makes era 5 machine-readable:
every change is recorded with timestamp and actor, so the audit can
reconstruct the document's evolution without archaeology.
