# Architecture (v2.2.0)

> **When to read:** before any non-trivial modification, or when a
> step's exit criteria are unclear.

## The eight phases + retrospective

The pipeline has eight build phases (0–8) plus a retrospective (9).
Each phase has machine-checkable exit criteria. The next phase does
not start until the prior phase's exit criteria are met.

### Phase 0+1 — discover_projects

**Script:** `01_discover_projects.py`
**Inputs:** `--code-dirs ~/code ~/code2`, optional `--github-token`
**Outputs:** `projects` table rows with `name`, `path`, `description`, `era` (preliminary)
**Exit criteria:** every directory under `--code-dirs` that contains a
`.git` OR a non-trivial README OR a spec-kit `requirements.md` is a
row. Subfolder projects are included. Description is from
GitHub README (if remote), else README.md, else a brief scan.
**Edge cases:** symlinks (resolve, deduplicate); empty dirs (skip);
non-git dirs with code (include — git-root keying would silently drop
non-git projects).

### Phase 2 — classify_era

**Script:** `02_classify_era.py`
**Inputs:** `projects` table
**Outputs:** `era` ∈ {0, 1, 2, 3, 4, 5}, `era_overlap` list
**Exit criteria:** every project has an era. Era 5 projects skip
Phase 3 archaeology.
**See:** `references/era_typology.md`

### Phase 3 — spec_archaeology

**Script:** `03_spec_archaeology.py`
**Inputs:** `projects` table, cass search for `specify.spec` and `requirements.md`
**Outputs:** `canonical_prd_path`, `spec_lineage` (list of {path, role, attached_at})
**Exit criteria:** every non-era-5, non-era-0 project has a canonical
PRD path. Era 5 projects have the living document path. Era 0
projects have null (flagged for Phase 4).
**Special case:** `under-revision` projects get change-level specs,
not whole-system reconstruction (see `references/lifecycle_states.md`).

### Phase 4 — derive_lifecycle

**Script:** `04_derive_lifecycle.py`
**Inputs:** `projects` table, cass session activity, git history
**Outputs:** `derived_lifecycle`, `lifecycle_confidence`, `lifecycle_evidence`, `lifecycle` (confirmed)
**Exit criteria:** every project has a `lifecycle`. `proposed` states
are surfaced for confirmation. No Phase 7 runs on `proposed` states.
**See:** `references/lifecycle_states.md`

### Phase 5 — extract_prompts

**Script:** `05_extract_prompts.py`
**Inputs:** `projects` table, `scope` (see `references/scope_selectors.md`), `cass` CLI
**Outputs:** `prompts` table (newest-first), `prompt_audit_fields` table
**Exit criteria:** every prompt in scope is in the table. Every prompt
has audit fields (or is marked `source: "cass-only"` if raw JSONL
unavailable). Per-turn coverage is 100% by construction (cass
`is_human` filter cannot miss what matches).
**Cass commands:**
- `cass search "" --workspace <path> --robot-format sessions --days <N>` (enumerate)
- `cass export <path> --format json` (extract)
- `cass export <path> --include-tools` (with tool calls)
- `cass view <path> -n N -C 10 --json` (single line)
- `cass expand <path> --line N -C 3 --json` (context)

### Phase 6 — distill_intent

**Script:** `06_distill_intent.py`
**Inputs:** `prompts` table, scope
**Outputs:** `intents` table with `type`, `superseded_by`, `taxonomy_version`
**Exit criteria:** every `prompt_id` has at least one intent row
(including `noise` verdicts). Every supersession link is bidirectional.
Per-turn coverage: every submitted ID comes back with a verdict.
**Batch size:** calibrated on a held-out set. See
`references/eval_protocol.md`.
**See:** `references/intent_taxonomy.md`

### Phase 7 — three_way_join

**Script:** `07_three_way_join.py`
**Inputs:** `intents` table, `canonical_prd_path`, repo
**Outputs:** `status_vectors` table
**Exit criteria:** every project has a status vector. Vector
components sum to 1.0. No component is `proposed` — all are derived.
**Proposer/verifier:** Phase 6 and Phase 7 must be different
processes, ideally different models. See `references/failure_modes.md` #1.
**See:** `references/metric_vector.md`

### Phase 8 — emit_wiki + status_vector

**Scripts:** `08_emit_wiki.py`, `09_status_vector.py`
**Inputs:** all tables
**Outputs:** wiki markdown files in `--out` dir, status vector files (and optionally beads)
**Exit criteria:** `lint_wiki.py` passes. Every project has a page.
Cross-cutting pages (standing_constraints, repeated_corrections,
abandoned, corrections_by_era) are populated. Master index lists all
projects with lifecycle and status vector summary.
**See:** `references/frontmatter_schema.md`

### Phase 9 — post_completion_audit (retrospective)

**Script:** `10_post_completion_audit.py`
**Inputs:** `observations` table, `references/retrospective.md`
**Outputs:** proposed edits in `proposed_edits/<tranche_id>/`
**Exit criteria:** every question in the retrospective has an
observation. Proposed edits pass the held-out eval with no regression.
**Progressive disclosure:** this is the only phase that loads
`references/retrospective.md`. Loading earlier biases the run.
**See:** `references/retrospective.md`

## State in SQLite

All state lives in SQLite. The skill never holds run state in context.
This is what makes the pipeline crash-recoverable and tranche-resumable.

Schema is in `scripts/lib/schema.sql`. Key tables:
- `projects` — one row per discovered project
- `tranches` — one row per (scope_hash, run_id); the unit of work
- `prompts` — extracted user prompts
- `prompt_audit_fields` — fields cass flattens away (see
  `references/cass_fidelity.md`)
- `intents` — distilled intents with type and supersession links
- `status_vectors` — per-project status vectors
- `observations` — append-only observations during a tranche
- `proposed_edits` — meta-learning proposals

## Newest-first ordering

Processing is newest-first. This makes the merge monotonic (every
conflicting item arriving is older, so it can only be marked
superseded) and safely truncatable (newest-first at 60% is a correct
audit with a known cutoff; oldest-first at 60% asserts things are
current when the unprocessed 40% contains the instructions that
superseded them).

## What got missed in earlier versions (the drift diagnosis)

The worst miss in v1.x: lifecycle-state routing. The user's
progression says explicitly that done, in-progress, not-yet-started,
and under-revision each get a different output. v1.x had `status` as
a frontmatter field and never branched the pipeline on it, so all
four states got one output.

Also missing entirely: step 2 (project descriptions from README/GitHub/
scan), the five-era document typology as a parser selector, the
discarded/incorporated/deferred sort, subfolder projects (git-root
keying would have silently dropped every non-git project directory),
and `specify.spec` as a search term — v1.x wrote `speckit.specify`
from current docs without searching the older command family actually
used.

How it happened: each follow-up was a sharp local correction, each
got a focused fix, four rounds of subsection optimization while the
top-level spine drifted from the first message. Same mechanism §23
exists to prevent: proxy improvement without objective improvement,
arrived at in conversation instead of in code.

The fix: the anchor sits at the top of SKILL.md as an immutable
reference. `lint_wiki.py` fails the build on an unmapped section. Drift
becomes a build error rather than something noticed four rounds later.
