# Frontmatter Schema (closed vocabulary)

> **When to read:** before Phase 8 (wiki emission), or when adding a
> new metadata field to the wiki pages.

## The closed-vocabulary tag rule

Every markdown file the wiki emits has YAML frontmatter. The tag values
are drawn from closed vocabularies. Tags are how cross-cutting pages
aggregate per-project pages; an open vocabulary breaks aggregation
silently.

## Per-project page frontmatter

```yaml
---
project: my-app                          # matches projects.name
lifecycle: in-progress                   # from references/lifecycle_states.md
era: 3                                   # from references/era_typology.md
status_vector:                           # from references/metric_vector.md
  completed: 0.62
  in_progress: 0.18
  drifted: 0.08
  superseded: 0.04
  abandoned: 0.04
  not_begun: 0.04
last_audited: 2025-07-23
scope_hash: a1b2c3d4...                  # tranche scope, for reproducibility
taxonomy_version: "1.0"                  # from references/intent_taxonomy.md
canonical_prd_path: ~/code/my-app/requirements.md
spec_lineage:
  - path: ~/code/my-app/prd-v1.md
    role: original
    superseded_by: ~/code/my-app/prd-v3.md
  - path: ~/code/my-app/prd-v3.md
    role: at-spec-time
    attached_at: 2025-03-15T10:30:00Z
  - path: ~/code/my-app/requirements.md
    role: canonical
related_projects:
  - api-server
  - shared-lib
tags:
  - auth                                 # from closed vocabulary below
  - api
  - experimental
---
```

## Closed tag vocabulary

Tags are scoped to this list. Adding a tag requires updating this file
and bumping `taxonomy_version`.

**Domain tags:**
`auth`, `api`, `ui`, `data`, `infra`, `ml`, `cli`, `docs`, `tests`,
`build`, `deploy`, `observability`, `security`, `perf`, `refactor`

**Maturity tags:**
`experimental`, `prototype`, `alpha`, `beta`, `stable`, `maintenance`,
`deprecated`, `abandoned`

**Activity tags:**
`active`, `idle`, `dormant`, `revival` (recent activity after long idle)

**Structural tags:**
`monorepo`, `subproject`, `meta-project`, `single-file`, `library`,
`service`, `batch`, `tool`

## Cross-cutting page frontmatter

```yaml
---
page_type: standing_constraints           # or repeated_corrections, abandoned, corrections_by_era
generated_from_scope_hash: a1b2c3d4...
generated_at: 2025-07-23T14:22:00Z
source_tranches: [tranche_001, tranche_002]
row_count: 47
---
```

## The "generated block" rule

Generated blocks inside markdown are fenced:

```
<!-- BEGIN GENERATED: status_vector -->
... machine-generated content ...
<!-- END GENERATED: status_vector -->
```

`scripts/lint_wiki.py` fails the build if a human edit appears inside a
fence. This is the single rule that stops the wiki from becoming the
markdown graveyard everyone running the Karpathy pattern reports
hitting.

## What humans can edit

- Prose around generated blocks
- The `notes` section at the bottom of each page
- The `related_projects` list (humans know relationships the audit misses)
- Tag additions (within the closed vocabulary)
- `lifecycle` confirmation (`proposed` → confirmed state)

## What humans cannot edit

- Anything inside a `BEGIN GENERATED` / `END GENERATED` fence
- The `status_vector` field (it's derived)
- The `scope_hash` field (it's a record of what was processed)
- The `canonical_prd_path` after Phase 3 has confirmed it (file a
  dispute in the wiki's `notes` section instead; Phase 3 will re-run
  with the dispute as a hint)
