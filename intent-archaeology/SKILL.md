---
name: intent-archaeology
description: Reconstruct user intent for coding projects by triangulating three sources — agent session logs (via `cass`), spec-kit artifacts (PRD / requirements.md / design.md / living documents), and the current repo state — then emit a Karpathy-style wiki plus a per-project status vector. Composable scope (time, projects, agents, prompt type, content regex, session, cap); default is all prompts from the last 30 days. Use whenever the user wants to audit what a project was supposed to be vs. what it became, recover the original plan from conflicting PRD versions, mine every prompt they typed across coding agents (Claude Code, Codex, Cursor, Gemini CLI, Aider, ChatGPT), build a wiki from their own prompts, feed gaps to an idle-time agent loop, or perform any "what did I ask for" / "is this done" / "what got abandoned" analysis on a folder of projects. Also trigger on mentions of cass, spec-kit, /specify.plan, living documents, constitution files, brownfield spec recovery, or requirements traceability. SQLite-backed.
license: Apache-2.0
metadata:
  author: ice-ninja
  requires: "Python 3.11+, git. Optional but strongly recommended: cass CLI (github.com/Dicklesworthstone/coding_agent_session_search), jq."
  reads: "~/code and ~/code2 by default, plus agent session logs. Session logs may contain pasted credentials."
  writes: "~/.intent-archaeology and the wiki output directory only. Never writes to your repos."
  version: "1.2.1"
  architecture_doc_version: "v2.2.0"
  spec_compliance: agentskills.io-v1
---

# Intent Archaeology

## What this skill does

You have a folder of coding projects (typically `~/code` and `~/code2`). Across months of work, each project accumulated:

- **A dozen PRD / requirements.md / design.md versions**, half of them written after the fact
- **Hundreds of agent session logs** spread across Claude Code, Codex, Cursor, Gemini CLI, and a dozen other harnesses
- **A repo that may or may not match** what any of those documents said it should be

This skill reconstructs the *intent* of each project by triangulating three sources, then publishes the result as a wiki a human can read and a status vector a sleep-time agent can act on.

The three sources are:

1. **Session intent** — the prompts you actually typed, extracted from the `cass` index, deduplicated by supersession (not by string match), frequency-ranked
2. **Spec lineage** — the canonical PRD/requirements.md/design.md that was live at build time, recovered via era-aware archaeology (not just "the latest one")
3. **Repo reality** — what the code actually does today

The join of those three is the audit. None of the three is authoritative on its own.

## Why it's a skill, not a script

State must live in **SQLite**, not in the skill and not in a conversation. This runs over weeks in tranches on a machine with a crash history. A skill holding run state in context can't survive a crash; a skill **driving scripts whose state is a DB** resumes from anywhere. The skill is the orchestrator and the procedural memory; the scripts are the deterministic core; the SQLite file is the recoverable truth.

## The anchor (immutable)

Every section of this skill and every script it drives must map to one of the nine steps below. The lint script (`scripts/lint_wiki.py`) fails the build if it finds a section that doesn't map. This is the "question zero" defense against drift — a self-improving system needs a fixed point that isn't part of what it improves.

| Step | Phase script | What it produces |
|------|--------------|------------------|
| 0. Identify projects | `01_discover_projects.py` | `projects` table rows |
| 1. Project descriptions | `01_discover_projects.py` (same pass) | `description`, `era` columns |
| 2. Era classification | `02_classify_era.py` | `era` ∈ {1..5} |
| 3. Spec archaeology | `03_spec_archaeology.py` | `canonical_prd_path`, `spec_lineage` |
| 4. Lifecycle state | `04_derive_lifecycle.py` | `lifecycle` ∈ {not-started, in-progress, completed, under-revision, archive-candidate} |
| 5. Prompt extraction | `05_extract_prompts.py` | `prompts` table (newest-first) |
| 6a. Batch emission | `06_distill_intent.py` | batch JSON files for classification |
| 6b. Verdict merge | `06b_merge_verdicts.py` | `intents` table, `superseded_by` links |
| 7. Three-way join | `07_three_way_join.py` | `status_vector` per project |
| 8. Wiki emission | `08_emit_wiki.py` + `09_status_vector.py` | Karpathy-style wiki + status vectors |
| 9. Post-completion audit | `10_post_completion_audit.py` | Retrospective findings (progressive disclosure) |

Steps 0–8 are the build. Step 9 is the meta-learning loop and is **only loaded at completion** — see "Progressive disclosure" below.

## Scope selectors (adjustable, composable)

Every Phase 5+ run is scoped. Scope is composable: any combination of the dimensions below is valid. The default scope is **all prompts from the last 30 days, across all known projects, across all agents** — but you typically narrow it.

Read `references/scope_selectors.md` before the first non-default run. It contains the full spec, the closed vocabulary for `--type`, and the exact mapping from each scope dimension to one or more `cass` CLI flags.

| Dimension | Flag | Default | Maps to cass |
|-----------|------|---------|--------------|
| Time — relative | `--since 7d` | `30d` | `--days N` or `--since Nd` on `cass search` |
| Time — absolute | `--from 2025-01-01 --to 2025-06-30` | (none) | post-filter on `cass search` timestamps |
| Time — today | `--today` | false | `cass search "" --today --robot-format sessions` |
| Projects | `--projects foo,bar` or `--project-dir ~/code/foo` | all in DB | `cass search "" --workspace /abs/path --robot-format sessions` per project |
| Agents | `--agent claude,cursor` | all | `cass search ... --agent <name> --robot-format sessions` (one invocation per agent, results unioned) |
| Prompt type | `--type correction,scope-cut` | all | post-filter on the distilled `intents.type` column (see `references/intent_taxonomy.md`) |
| Content regex | `--matches "jwt|auth"` | (none) | `cass search "<regex>" --json` (Phase F) or post-filter on extracted prompt text (Phase C) |
| Single session | `--session /path/to/session.jsonl` | (none) | `cass export /path --format json` directly, no enumeration |
| Result cap | `--limit 500` | (none) | `cass search ... --limit N --json` (Phase F) or stop enumeration after N prompts (Phase C) |
| Ordering | `--ordering newest-first` | `newest-first` | cass search results are processed in-line; per-session ordering in extract_prompts_from_session |

**Mix-and-match examples** (all valid):

```bash
# Default: all prompts from the last 30 days across all projects and agents
python scripts/05_extract_prompts.py --db ~/.intent-archaeology/state.db

# All prompts from a single project going back 90 days
python scripts/05_extract_prompts.py \
  --db ~/.intent-archaeology/state.db \
  --projects my-app \
  --since 90d

# Every prompt on two projects since January, Claude Code only
python scripts/05_extract_prompts.py \
  --db ~/.intent-archaeology/state.db \
  --projects my-app,api-server \
  --since 2025-01-01 \
  --agent claude

# Only corrections issued in Cursor in the last week (post-distillation filter)
python scripts/06_distill_intent.py \
  --db ~/.intent-archaeology/state.db \
  --type correction \
  --agent cursor \
  --since 7d

# Every prompt containing "auth" or "jwt" across all agents (Phase F-style)
python scripts/05_extract_prompts.py \
  --db ~/.intent-archaeology/state.db \
  --matches "auth|jwt|token" \
  --since 180d

# One specific session, full export including tool calls
python scripts/05_extract_prompts.py \
  --db ~/.intent-archaeology/state.db \
  --session ~/.claude/projects/abc-123.jsonl \
  --include-tools
```

The scope is recorded in the `tranches` table on every run, so a later re-pass with a different scope doesn't clobber earlier results — each (scope, tranche_id) pair is its own row.

### How cass is actually invoked

The skill never tries to re-implement what cass already does. It shells out to the `cass` CLI and parses JSON. The exact commands are documented in `references/scope_selectors.md` and embedded in `scripts/lib/scope.py`. The five commands you'll see most often:

```bash
# 1. Enumerate sessions for a project (Phase C enumeration)
cass search "" --workspace /abs/path/to/project --robot-format sessions --days 30

# 2. Export a single session to JSON (path is positional)
cass export /path/to/session.jsonl --format json

# 3. Include tool calls in the export (separate flag, also positional path)
cass export /path/to/session.jsonl --include-tools

# 4. View a specific line with context (path positional, -n is line number)
cass view /path/to/session.jsonl -n 42 -C 10 --json

# 5. Expand context around a line (path positional, --line not -n)
cass expand /path/to/session.jsonl --line 42 -C 3 --json
```

For Phase F (cited evidence against a specific question), use `cass search`:

```bash
# Cited evidence bundle. --fields full returns everything; --fields minimal returns paths only.
cass search "how did we handle jwt refresh" --fields full --json --limit 20
cass search "bug fix login" --agent claude --days 30 --json
```

If your cass build supports `cass pack` (deterministic cited bundles with `freshness.stale_evidence_count` and `privacy_redactions_applied` as structured fields), use it for Phase F. If not, `cass search ... --fields full --json` plus a small Python wrapper that adds the freshness and redaction accounting is the fallback.

## How to run it

### First run (bootstrap)

```bash
# 1. Initialize the SQLite state DB. Idempotent.
python scripts/init_db.py --db ~/.intent-archaeology/state.db

# 2. Discover projects and write descriptions.
python scripts/01_discover_projects.py \
  --db ~/.intent-archaeology/state.db \
  --code-dirs ~/code ~/code2 \
  --github-token "$GITHUB_TOKEN"  # optional, for GitHub descriptions

# 3. Classify the document era of each project (1..5).
python scripts/02_classify_era.py --db ~/.intent-archaeology/state.db

# 4. Find the canonical PRD via cass search for "specify.spec" and "requirements.md".
python scripts/03_spec_archaeology.py --db ~/.intent-archaeology/state.db

# 5. Derive and confirm the lifecycle state per project.
python scripts/04_derive_lifecycle.py --db ~/.intent-archaeology/state.db

# 6. Extract every human prompt, newest-first, scoped to last 30 days across all projects.
#    (Adjust scope here — see "Scope selectors" above for the full flag set.)
python scripts/05_extract_prompts.py \
  --db ~/.intent-archaeology/state.db \
  --ordering newest-first \
  --since 30d

# 7a. Emit classification batches. This script does NOT call a model.
python scripts/06_distill_intent.py \
  --db ~/.intent-archaeology/state.db \
  --out ~/.intent-archaeology/batches \
  --items 60 --all

# 7b. You classify each batch. Read references/intent_taxonomy.md first.
#     Every id must come back with a verdict, including "noise" verdicts.
#     Write verdicts as JSON into ~/.intent-archaeology/verdicts/

# 7c. Merge the verdicts. Deterministic, no model. Enforces ID accounting
#     and rejects any intent whose verbatim span is not in its source prompt.
python scripts/06b_merge_verdicts.py \
  --db ~/.intent-archaeology/state.db \
  --verdicts ~/.intent-archaeology/verdicts \
  --batches ~/.intent-archaeology/batches

# 8. Three-way join → status vector.
python scripts/07_three_way_join.py --db ~/.intent-archaeology/state.db

# 9. Emit the wiki + status vectors.
python scripts/08_emit_wiki.py \
  --db ~/.intent-archaeology/state.db \
  --out ~/intent-wiki/
python scripts/09_status_vector.py --db ~/.intent-archaeology/state.db
```

### Resuming after a crash

Every script is idempotent and reads its starting point from SQLite. Re-run the same command. The `tranches` table records what's been processed; the `intents` table records what's been distilled; nothing is recomputed unless you pass `--force`.

### After the build completes

Only when steps 0–8 are done for a tranche:

```bash
python scripts/10_post_completion_audit.py \
  --db ~/.intent-archaeology/state.db \
  --tranche <tranche-id>
```

This loads `references/retrospective.md` — which is deliberately not loaded earlier, because loading it earlier biases the run toward producing findings that make the retrospective look good. This is the progressive-disclosure mechanism the user asked for.

## Critical rules (the ones that will quietly wreck the run if violated)

These are explained in depth in `references/architecture.md`. They are listed here so they sit in the always-loaded context.

1. **State in SQLite, not in context.** Crash recovery, multi-tranche resumption, and proposer/verifier separation all depend on this. The skill never holds run state.

2. **Don't extract only user prompts.** Ingest everything once via `cass export`; project the human prompts as a view. The tool calls, file paths, and errors are the evidence layer the audit needs, and you can't get them back after filtering at ingest.

3. **cass selects, raw JSONL extracts.** `cass` normalizes 20+ harness formats and flattens away fields like `isSidechain`, `gitBranch`, `parentUuid`, and `toolUseResult`. Use `cass view /path/to/session.jsonl -n N --json` (path is positional), `cass expand /path/to/session.jsonl --line N -C 3 --json` (note `--line`, not `-n`), and `cass export /path/to/session.jsonl --format json` plus `cass export /path/to/session.jsonl --include-tools` to round-trip back to the raw JSONL on `source_path:line_number`. One enrichment pass materializes a derived table with a foreign key back to cass. Not duplication — the audit fields cass doesn't carry. See `references/cass_fidelity.md` and `references/scope_selectors.md` for the full CLI reference.

4. **Don't split by token count.** Split on session boundary, then topic segment. Splitting a big session in half kills exactly the cross-boundary dedup and supersession detection you're after.

5. **Don't dedupe repeated instructions, count them.** Frequency is your importance signal *and* your compliance-failure signal. Five occurrences of the same constraint is a constitution rule, not a duplicate. The frequency-ranked cross-cutting page (`standing-constraints.md`) is a constitution discovered rather than authored.

6. **The proposer of a status must not be the verifier.** Phase 6b (merge) and Phase 7 (three-way join) run as separate processes, and neither calls a model: 6a emits, you classify, 6b merges deterministically. Everything else in the design is plumbing around that. See `references/failure_modes.md` #1.

7. **Phase C enumerates, Phase F searches.** For exhaustive sweeps (Phase 5), enumerate every session for a project (`cass search "" --workspace /path --robot-format sessions --days N` then `cass export /path --format json` per session), filter, process all of it. Never use `cass search "<topic>"` to pull a project's relevant prompts for Phase C — recall moves into BM25+vector fusion and a turn phrased in unqueried vocabulary silently never appears. `cass search` is fine for Phase F (cited evidence against a question) as long as you use a content-bearing query, not the empty-string session enumeration form. If your cass build supports `cass pack`, use that for deterministic cited bundles in Phase F; otherwise fall back to `cass search "..." --fields full --json`.

8. **Newest-first ordering.** Makes the merge monotonic (every conflicting item arriving is older, so it can only be marked superseded). Makes the run safely truncatable (newest-first at 60% is a correct audit with a known cutoff; oldest-first at 60% asserts things are current when the unprocessed 40% contains the instructions that superseded them).

9. **Status vector, not scalar.** Never report a single completion percentage. A scalar hides `drifted`, `superseded`, and `abandoned`, which are the three categories you built this to find. The status vector is defined in `references/metric_vector.md`.

10. **Markdown canonical for human judgment, SQLite canonical for derived facts, never both for the same field.** Generated blocks in markdown get fenced; `lint_wiki.py` fails the build if a human edits inside a fence. This is the single rule that stops the wiki from becoming the markdown graveyard everyone running the Karpathy pattern reports hitting.

11. **Retrospective loads only at completion.** `references/retrospective.md` is the progressive-disclosure resource. Loading it earlier biases the run.

## Progressive disclosure map

This skill has three disclosure tiers, matching the Anthropic Agent Skills standard:

**Tier 1 — always loaded (this SKILL.md frontmatter):** ~150 tokens. Just enough for Claude to know when to trigger the skill.

**Tier 2 — loaded when triggered (this SKILL.md body):** ~5000 tokens. The anchor, the run commands, the critical rules, the file map.

**Tier 3 — loaded as needed (the `references/` and `scripts/`):** effectively unbounded. Read each reference only when the corresponding problem is on the table.

| Reference | When to read it |
|-----------|-----------------|
| `references/architecture.md` | Before any non-trivial modification, or when a step's exit criteria are unclear |
| `references/cass_fidelity.md` | Before Phase 5 (prompt extraction), to understand which cass fields survive normalization |
| `references/scope_selectors.md` | Before any non-default scope run; the full composable-scope spec, closed vocabularies, and exact cass CLI mappings |
| `references/era_typology.md` | Before Phase 2 (era classification), to apply the 5-era parser selector |
| `references/lifecycle_states.md` | Before Phase 4 (lifecycle derivation), to route per-state output |
| `references/intent_taxonomy.md` | Before Phase 6 (intent distillation), to label intents with the closed vocabulary |
| `references/frontmatter_schema.md` | Before Phase 8 (wiki emission), to apply the closed-vocabulary tag rule |
| `references/metric_vector.md` | Before Phase 7 (three-way join), to compute the status vector correctly |
| `references/failure_modes.md` | When something goes wrong; ranked, so read top-down |
| `references/corpus_sources.md` | When Phase 5 feels incomplete; the 13 sources you're forgetting |
| `references/prior_art.md` | When deciding whether to build vs. reuse; cass / spec-kit / stackshift / spec-gen / UserTrace / Trace2Skill / ALIGNXPLORE / LiSSA / Beads |
| `references/living_document_v3.md` | When a project is era 5; the living document is machine-readable, skip archaeology |
| `references/research_position.md` | When the user asks "is this S-tier" or "what's the research framing" |
| `references/retrospective.md` | **Only** at completion, via `10_post_completion_audit.py` |

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

## What to do when the user invokes this skill

1. **Read the user's request and locate it on the anchor.** Is this a full run (steps 0–9), a single-project audit, a re-pass of an earlier tranche, a scope-narrowed extraction ("just my Cursor prompts from last week"), or just a wiki refresh? The anchor tells you which scripts to invoke.

2. **Confirm the scope.** Default is `--since 30d` across all known projects and all agents. If the user said anything time-bounded ("recently", "this week", "since January"), project-bounded ("my app", "the api-server"), agent-bounded ("in Cursor", "Claude Code only"), type-bounded ("corrections", "scope cuts"), or content-bounded ("about auth"), translate that to scope flags using the table in "Scope selectors" above. Read `references/scope_selectors.md` for the closed vocabularies and exact cass mappings. When in doubt, state the scope back to the user before running.

3. **Confirm the code directories.** Default to `~/code` and `~/code2`, but ask if not specified. Subfolder projects are real — don't drop non-git directories. (Note: if scope is `--session /path/...` only, code directories aren't needed.)

4. **Confirm the state DB path.** Default `~/.intent-archaeology/state.db`. Create the parent directory if missing.

5. **Run the relevant scripts in order.** Each script prints its exit criteria. Don't proceed to the next phase until the prior phase's exit criteria are met — this is what makes the build machine-checkable. Pass the scope flags through — every Phase 5+ script accepts them via `scripts/lib/scope.py`.

6. **At completion only**, run `10_post_completion_audit.py`. This is the meta-learning loop. It will:
   - Read `references/retrospective.md`
   - Compare the tranche's observations to the retrospective's question list
   - Propose prompt-level edits to the skill (never merge-logic edits — those require three consecutive tranches of no prompt-level gain)
   - Write proposed edits as files in git so every edit is a readable diff
   - Accept an edit only if it improves the held-out score **without regressing any component of the metric vector**

7. **Report results to the user** as a status vector, not a percentage. Use the templates in `assets/templates/`. The wiki is for the human; the status vector is for the sleep-time agent; the SQLite is for both. Always state the scope that produced the results — "this audit covers Claude Code and Cursor prompts on my-app and api-server from 2025-01-01 to 2025-06-30" — so the user knows what's in and what's out.

## What NOT to do

- **Don't run `cass search "<topic>"` for Phase 5 (exhaustive enumeration).** Phase 5 enumerates via `cass search "" --workspace ... --robot-format sessions --days N` then `cass export /path --format json` per session. `cass search "<topic>"` (with a content query) and `cass pack` belong in Phase F (cited evidence against a specific question) only. The reason: `cass search` recall for content queries moves into BM25+vector fusion, and a turn phrased in vocabulary that wasn't queried silently never appears — disqualifying for an audit whose deliverable is completeness. The empty-string session enumeration form is safe for Phase 5 because it returns all sessions without any recall gap.
- **Don't forget the positional path.** `cass view -n 42 --json` will fail. Path is positional: `cass view /path/to/session.jsonl -n 42 --json`. Same for `cass expand` (which uses `--line`, not `-n`) and `cass export`.
- **Don't conflate `--include-tools` with `--format json`.** They're separate flags. `cass export /path --format json` exports the conversation as JSON. `cass export /path --include-tools` adds tool-call entries to the export. To get both, run both (or check your cass version — newer builds may accept them together).
- **Don't split a long session in half to fit a context window.** Filter to human prompts first (typically 2–5% of raw corpus), then split on session boundary. The token backstop (~20–30% of window) is for pathological turns only.
- **Don't trust a single source.** A spec that says "feature X is implemented" + a session log that says "we cut feature X" + a repo with no X = `abandoned`, not `completed`. The status vector exists to make this visible.
- **Don't run the retrospective mid-tranche.** Bias is the failure mode.
- **Don't accept meta-learning edits that improve a single metric at the cost of another.** The ICLR 2026 reward-hacking finding (73.8% / 46.8% of optimizations showed proxy gains with no held-out real-task gain) is the cautionary tale. See `references/failure_modes.md` #4.
- **Don't infer content for the research paper / S-tier analysis.** State gaps directly with `[GAP-NN]` markers and leave them absent with a note for later correction. See `references/research_position.md`.

## Compatibility notes

- **cass** is required for Phase 5+. Install from `github.com/Dicklesworthstone/coding_agent_session_search`. The skill degrades gracefully: if `cass` is not installed, Phase 5 emits an empty `prompts` table and the wiki shows "no session corpus available — install cass to enable intent recovery."
- **spec-kit** is not required, but if present, `03_spec_archaeology.py` will look for `tasks.md`, `constitution.md`, `plan.md` as additional spec lineage sources.
- **Beads** is not required, but if present, the skill writes its status vector as beads so the sleep-time agent's task queue picks them up.
- **Python 3.11+** for `tomllib` and modern typing. Python 3.10 will work with `tomli` backport.

## Versioning

This is `intent-archaeology` v1.2.1, mapping to architecture doc v2.2.0.

v1.2.1 fixes three bugs:
1. **`cass timeline --workspace` replaced with `cass search "" --robot-format sessions`** across all scripts and docs. cass v0.6.22 does not support `timeline --workspace`; `cass search "" --robot-format sessions` is the correct enumeration path.
2. **`SUPPORTED_AGENTS` validation relaxed** from hard `ValueError` to advisory warning. cass v0.6.22 supports 22 agent connectors; the script should not reject unknown agent names.
3. **Git history resolution added to spec archaeology** (`03_spec_archaeology.py`). Before falling back to filename-convention heuristics, the script now checks `git log --all --diff-filter=A` to find which file version existed at the first coding session's timestamp.
4. **SKILL.md docs updated** — all `cass timeline` references replaced, version consistency fixed, scope table mappings fixed.

v1.2.0 added the composable scope selector system and corrected cass CLI syntax to match the canonical command reference. The versioning follows the transcript's convention: major bump when the spine (the 9-step anchor) changes, minor bump for new sections or capabilities, patch bump for fixes.
