## File map

```
intent-archaeology/
├── SKILL.md                              # this file
├── LICENSE                               # Apache-2.0
├── references/
│   ├── architecture.md                   # v2.2.0 architecture: 8 phases + retrospective
│   ├── cass_fidelity.md                  # which cass fields survive normalization
│   ├── scope_selectors.md                # composable scope spec + cass CLI mapping (v1.1)
│   ├── era_typology.md                   # 5-era document typology as parser selector
│   ├── lifecycle_states.md               # 5 lifecycle states + routing
│   ├── intent_taxonomy.md                # closed-vocabulary intent labels
│   ├── frontmatter_schema.md             # YAML frontmatter closed-vocabulary tags
│   ├── metric_vector.md                  # status vector + anti-metrics
│   ├── failure_modes.md                  # 10 ranked failure modes
│   ├── corpus_sources.md                 # 13 corpus sources
│   ├── prior_art.md                      # cass, spec-kit, stackshift, spec-gen, UserTrace, etc.
│   ├── living_document_v3.md             # era 5 living document format
│   ├── research_position.md              # S-tier analysis + research framing
│   ├── eval_protocol.md                  # benchmark / eval protocol
│   └── retrospective.md                  # PROGRESSIVE DISCLOSURE — load only at completion
├── scripts/
│   ├── init_db.py                        # SQLite schema (idempotent)
│   ├── 01_discover_projects.py           # steps 0+1: scan ~/code, README fetch
│   ├── 02_classify_era.py                # step 2: era 1..5
│   ├── 03_spec_archaeology.py            # step 3: cass search specify.spec + requirements.md
│   ├── 04_derive_lifecycle.py            # step 4: derive + confirm state
│   ├── 05_extract_prompts.py             # step 5: cass export, is_human filter, newest-first
│   ├── 06_distill_intent.py              # step 6a: emit batches. No model call.
│   ├── 06b_merge_verdicts.py             # step 6b: deterministic merge + gates
│   ├── 07_three_way_join.py              # step 7: session + spec + repo → status vector
│   ├── 08_emit_wiki.py                   # step 8: Karpathy-style wiki
│   ├── 09_status_vector.py               # step 8b: status vector per project
│   ├── 10_post_completion_audit.py       # step 9: retrospective trigger (progressive disclosure)
│   ├── cass_select.py                    # cass selects, raw JSONL extracts
│   ├── lint_wiki.py                      # 08-lint: fail build on unmapped section / human edit in fence
│   ├── meta_learning.py                  # append observations, boundary edits
│   └── lib/
│       ├── schema.sql                    # SQLite schema
│       ├── scope.py                      # ScopeSpec dataclass + cass command compiler (v1.1)
│       ├── frontmatter_vocab.yaml        # closed-vocabulary tags
│       └── metric_vector.py              # metric vector definitions (shared)
├── assets/
│   └── templates/
│       ├── master_index.md.tmpl          # wiki master index (Karpathy style)
│       ├── project_page.md.tmpl          # per-project wiki page
│       ├── standing_constraints.md.tmpl  # cross-cutting: frequency-ranked constitution
│       ├── repeated_corrections.md.tmpl  # cross-cutting: to-do for AGENTS.md
│       ├── abandoned.md.tmpl             # cross-cutting: scope-cuts + reasons
│       ├── corrections_by_era.md.tmpl    # cross-cutting: are standing instructions read?
│       ├── constitution.md.tmpl          # for living-document projects (era 5)
│       └── worklog.md.tmpl               # per-project append-only worklog
└── evals/
    └── evals.json                        # test cases for skill-creator
```

