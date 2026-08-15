---
name: living-documents
description: Maintain the canonical Markdown planning and context system for long-running human-agent work. Use when locating project truth, starting or resuming substantial work, consolidating competing plans, creating linked project pages, recording decisions and evidence, handling asynchronous annotations, recovering after a crash, or updating the portfolio index under ~/LIVING_DOCUMENTS.
---

# Living Documents

Living Documents are the shared operating surface between a human and agents. They exist because agents produce and revise faster than a human can review, sessions crash, harnesses change, and chat does not preserve addressable decisions or verified state.

The document is the coordination protocol, not the renderer. Markdown is canonical. Browser rendering, indexes, and annotation overlays are derived.

## Two modes in one portable package

This is both an **installation skill** and an **operating skill**. `VERSION` is
the single release authority for the portable bundle, currently `2.1.0`; the
canonical Markdown format remains `3.0.0`.

1. **Install/bootstrap mode:** packages the `ld` command, local loopback reader,
   projection watcher, service templates, and documentation required to set up a
   new machine. The bundled `renderer/` directory is part of this skill package,
   not an external prerequisite.
2. **Operating mode:** directs humans and agents to maintain canonical Markdown
   under `~/LIVING_DOCUMENTS`. The reader and projections may never become
   content authority.

Use install mode when provisioning or repairing a machine. Use operating mode
for every substantial project task after the package is installed.

## Start every substantial operation

1. Run `ld ensure` once.
2. Read the returned `start-here.md`.
3. Read `project.md`, `what-to-do.md`, and only the linked pages needed for the current task.
4. Preserve stable page IDs and existing history.
5. Before a terminal response after substantial work, run the non-mutating continuity hook and inspect its `continuation` result. Record verified changes, evidence, decisions, blockers, and the next safe action. A `review-pending` result means a human chose a loopback-local direction or submitted a rendered question packet: inspect the exact receipt, record valid intent and authorization canonically, acknowledge it with `ld-ledger ack-question --receipt-id <id>` when applicable, and run only its named gate. A `pivot-required` result means select and record a Living Documents control-plane pivot before replying; it is never permission to stop.

Do not reconstruct project intent from chat when a canonical page exists. Do not replace a direct user correction with a newer model summary.

## Mandatory cross-harness continuity contract

Use the continuity hook as a guardrail, not as an automatic writer. At session
start or before substantial work, resolve the canonical project and read its
handoff. At a meaningful milestone or before a terminal response, invoke the
hook and inspect its read-only `continuation` result. Record one compact
handoff only when intent, task status, evidence, decision, blocker, or next
safe action changed. Ordinary prompts, tool calls, and file edits do not merit
a Living Documents edit.

The hook may report missing context or a missing handoff. It must never write
Markdown autonomously. Raw transcripts remain evidence; CASS remains search;
memory remains reusable agent context.

**Self-sufficiency rule.** The Living Document must hold everything needed to
reconstruct project intent without any external store. External stores are
rebuildable caches and indexes, never authorities. If losing an external
database, index, or transcript archive would lose intent, the boundary is drawn
in the wrong place and the boundary moves, not the data.

An earlier form of this rule said the Living Document "receives only the
adjudicated state needed to resume safely". That reading licensed real loss.
Measured 2026-08-04: the prompt corpus in the Living Document held **26%** of
the recorded prompt text, with 127 prompt bodies truncated mid-instruction and
recoverable only from a 56 MB SQLite file that no Markdown page referenced.
Removing the truncation raised it to 71%. Summarising is a display decision;
discarding the source text is data loss wearing the word "adjudicated".

The distinction that actually matters is **volume versus fidelity**, not raw
versus adjudicated. The Living Document should not carry 230,947 machine events.
It must carry every human instruction in full, because that is the intent it
exists to preserve. Where a projection is lossy, the page states what was
omitted and why, so the gap is auditable rather than invisible.

When the resolver reports `review-pending`, the selected option or question
receipt is an asynchronous handoff, not self-executing authority. Verify its
target and scope, apply the user's valid direction to canonical Markdown and
the ledger, acknowledge a consumed question receipt, then run the named
acceptance gate. If no review is pending and every project record remains
blocked, create the next independent control-plane pivot rather than ending
the session.

Install lifecycle hooks at `SessionStart` and `Stop`, not on every user prompt.
The start hook injects one compact orientation clause; the stop hook permits at
most one continuation and honors `stop_hook_active` to prevent loops. The same
script emits harness-safe Claude Code and Codex JSON with `--harness-output`;
without that flag it emits the structured diagnostic record agents inspect
manually. Never point a live hook at diagnostic mode.

## Canonical locations

- Corpus and project truth: `/home/cheta/LIVING_DOCUMENTS`
- One project: `/home/cheta/LIVING_DOCUMENTS/projects/<project-id>`
- System specification: `/home/cheta/LIVING_DOCUMENTS/system`
- Bundled renderer implementation: `<skill-root>/renderer`
- Generated renderer data: `/home/cheta/.cache/living-documents`

Project folders contain Markdown reference files, not application code.

## Operating loop

Use this loop:

1. **Orient:** read the start page, current objective, standing constraints, decisions, and last verified handoff.
2. **Select:** choose one unblocked task with explicit acceptance evidence. If
   every project task is blocked, select an explicit Living Documents
   control-plane pivot instead: improve recovery, validation, the decision
   surface, or a source-backed derived view. Record the project blockers and
   pivot; never treat a full blocked project queue as permission to stop.
3. **Execute:** change only the project or pages in scope.
4. **Verify:** run the narrowest decisive gate and distinguish verified state from claims.
5. **Record:** update the relevant page, task state, evidence, decision, history, and next action.
6. **Review asynchronously:** leave questions and proposals attached to stable targets; continue unrelated work.
7. **Resume:** another harness or post-crash session begins from the durable handoff instead of replaying chat.

## Page contract

Every Markdown file starts with frontmatter:

```markdown
---
id: requirements
title: Requirements
type: requirements
order: 30
status: active
parent: index
related: ["plan", "tasks"]
updated: 2026-07-23
---
```

The required fields are `id`, `title`, `type`, `order`, `status`, and `updated`. `parent` and `related` create navigation. Page IDs are stable kebab-case identifiers and unique within the project.

Required project pages:

- `project.md`: identity, lifecycle, source roots, and project relationships;
- `start-here.md`: minimal context for a fresh session;
- `index.md`: purpose and automatically maintained page index;
- `what-to-do.md`: priority order, blockers, and next safe action;
- `requirements.md`: canonical what and why;
- `plan.md`: canonical how and dependency order;
- `tasks.md`: evidence-gated execution ledger;
- `decisions.md`: accepted, rejected, deferred, and unresolved choices;
- `history.md`: append-only milestones and handoffs;
- `resources.md`: canonical PRD, design, source, session, and evidence links.

Add one concept per additional Markdown page. Use `ld add-page` so the page appears automatically in indexes.

## Consolidating competing plans

1. Register every candidate source with path, date evidence, hash, and relationship.
2. Identify which source was actually used during construction when evidence exists.
3. Extract every material requirement, decision, constraint, task, rejection, and deferred idea.
4. Classify each as incorporated, deferred, rejected, unresolved, superseded, or duplicate, with rationale.
5. Merge into one canonical requirements/plan/tasks set without deleting predecessors.
6. Keep predecessors in the project archive until intent archaeology and implementation evidence agree with the canonical result.

Newest filename is not authority. Direct user instructions, actual construction usage, Git evidence, and internal coherence determine the result.

## Asynchronous review

- Content annotations target selected prose or a stable page ID.
- Layout annotations target the renderer presentation of a page.
- Questions that block only part of the work remain open while other tasks continue.
- A canonical question packet uses `## Questions for the user`, followed by
  `### Question N: ...`, two or more bold lettered choices such as
  `**A. Choice. Recommended.** Rationale`, and a `**Write-in:**` prompt. The
  renderer must convert this convention into one radio group plus a custom
  answer field per question.

### Question packet format is exact, and failure is silent

The renderer matches this convention literally. A packet that deviates still
renders, but as ordinary prose with **no radio buttons and no answer form**.
Nothing warns you. The human then cannot answer by clicking and must retype
everything by hand, which is the exact friction this surface exists to remove.
Do not invent your own heading, such as `## Open questions` or
`## Questions`, and do not present options as a table, a bullet list, or an
`**Answer:**` blank line.

Required, in this order:

1. Exactly `## Questions for the user`.
2. Exactly `### Question N: <question text>`.
3. Two or more options, each its own paragraph, each opening with a bold
   letter: `**A. ...**`, `**B. ...**`. Mark exactly one `Recommended.` inside
   its bold span.
4. Exactly `**Write-in:**` followed by what a custom answer should specify.

Minimal working template, copy it verbatim and replace the text:

```markdown
## Questions for the user

Answer with the question number and option letter, such as `1A, 2B`.
You may write your own answer for any question instead.

### Question 1: <the decision, stated as a question>

**A. <option>. Recommended.** <why this one, and what it costs>

**B. <option>.** <what it buys, and what it costs>

**Write-in:** <what a custom answer should name>
```

Verify before relying on it. Fetch
`/projects/<id>/content/sections/<page-id>.md` from the local reader and
confirm the exact `## Questions for the user` heading survived the projection.
A `200` on the project page alone proves nothing, because the shell returns
`200` for every route.
- Submitting a question packet creates a private loopback receipt and a
  continuity attention event. It does not edit canonical Markdown, launch
  work, spend quota, or grant authority by itself.
- The continuity resolver prioritizes pending question receipts, points the
  agent to the exact project and page, and requires canonical application plus
  explicit acknowledgement before normal queue work resumes.
- A Gateway or harness adapter may deliver the same versioned attention event
  immediately when available. The local receipt and Stop-hook path remain the
  recovery-safe baseline.
- Export page changes for an agent rather than silently merging browser state.
- Record accepted changes in Markdown and append history; browser local state is not canonical.

## Context discipline

Keep the hot context small:

- start with `start-here.md`;
- load the current task and its directly linked pages;
- use `resources.md` to reach evidence;
- keep raw transcripts and historical versions outside the hot path;
- summarize nothing as settled until its source and disposition are recorded.

## Commands

```bash
ld ensure
ld list
ld status
ld create-project --id <project-id> --title "<title>" --source-root /path/to/source
ld add-page --project <project-id> --id <page-id> --title "<title>" --type concept --parent index
ld import-legacy --project <project-id> --source /path/to/old.livingdoc --source-id <version-label>
ld sync
ld validate
ld sync --project <project-id>
ld validate --project <project-id>
ld sync --all
ld sync --all --no-index-write
ld validate --all
ld onboard --project /code/<name> --with-template [--now]  # stdlib idempotent onboarding (see Project vs skill ownership)
ld doctor --all
ld serve
ld-handoff --project <project> --work-id <id> --status active|blocked|interrupted|complete --summary "..." --next-action "..." --session <harness:id> --evidence <path-or-gate>
ld-ledger import-handoffs
ld-ledger validate
ld-ledger list
ld-ledger next [--project <project>]
ld-ledger ack-question --receipt-id <receipt-id>
```

Use `sync --no-index-write` only for the automatic projection refresher: it
rebuilds generated runtime data without changing canonical Markdown index
blocks. Ordinary explicit `sync` retains its canonical index-maintenance role.

Bare `sync`, `validate`, and `status` infer the project from the current Git
worktree, matching `ensure`. Use `--project` for an explicit project or `--all`
for the whole corpus.

`ld onboard` is stdlib-only, offline, idempotent. It never mutates corpus historic files and shares the dashboard table (`__WEEKLY__`/`telemetry`/`vault_map`) without duplicate collection. The template symlink at `<skill-root>/template -> ../../living-documents-system/template` resolves via `LIVING_DOCUMENTS_RENDERER` fallback; installer copies the directory when symlink cannot be created (Windows).

Read `/home/cheta/LIVING_DOCUMENTS/RAISON_DETRE.md` before changing the format. Read `/home/cheta/LIVING_DOCUMENTS/system/SPECIFICATION.md` for invariants and `/home/cheta/LIVING_DOCUMENTS/system/LINKING.md` before changing relationships.

The canonical worked example is the `living-documents` project itself. Do not create another example copy.

## Terminology

The vocabulary of this system is defined in one place: the `terminology` page in
the `living-documents` dossier. Read it before using a term in a new way.

The term that matters most for other skills: a **project folder** is the Living
Documents dossier for one specific project, at
`~/LIVING_DOCUMENTS/projects/<project-id>/`. It is the permanent home for that
project's planning artifacts, outliving both the working directory and the code
repository. When a skill is told to put plan files "in the project folder", that
is the location meant.

## Never write a page file directly

Create every page with `ld add-page`, then edit the file it creates. Writing a
Markdown file straight into a dossier skips index registration, so the page is
**never projected** — it looks finished on disk and does not exist in the reader,
with no error anywhere.

This is not hypothetical. On 2026-08-01 twenty completed pages were lost this
way, and one of them additionally carried a `related:` target that did not
exist, which aborted the sync for the rest of the corpus.

Audit the corpus with:

```bash
<skill-root>/scripts/ld-audit          # report; non-zero exit if anything is wrong
<skill-root>/scripts/ld-audit --fix    # re-register orphans, drop dead links, sync
```

It reports ORPHAN (on disk, unindexed, never projected), GHOST (indexed, file
missing) and BAD-LINK (`related:` naming a nonexistent page). Ghosts are never
auto-repaired, since guessing would either resurrect a deleted page or hide a
real loss. Full rationale: the `corpus-integrity-audit` page in the
`living-documents` dossier.

## Local reader and installation

`ld add-page` creates a linked, frontmatter-valid page and regenerates that
project's runtime projection. `ld create-project` creates the complete required
project page set. Use the shared local reader instead of per-project servers:

```bash
<skill-root>/scripts/install-living-documents.sh --enable-renderer
<skill-root>/scripts/install-living-documents.sh --install-hooks
<skill-root>/scripts/install-living-documents.sh --install-rules
ld serve
```

`--install-hooks` removes predecessor Living Documents handlers, preserves
unrelated hooks, creates timestamped configuration backups, and installs
five-second `SessionStart` and `Stop` command handlers for Claude Code and
Codex. Codex marks changed non-managed hooks for review; use `/hooks` after
installation to inspect and trust the new hashes.

`--install-rules` installs the bounded continuity and receipt-delivery contract
from `references/harness-rules.md` into Claude Code and Codex global rule
files. It follows symlinks, deduplicates a shared source, replaces only its
marked managed block, preserves all unrelated instructions, and creates a
timestamped backup before a change. The rules keep the protocol available
after context compression; the hooks provide current state and receipts.

The reader is available at `http://127.0.0.1:4173/`. The service is loopback
only, memory-bounded, and reads the generated projection; it never becomes
content authority. Run `ld doctor --all` after a skill sync or service change.

## Completion gate

Do not claim a Living Document update complete unless:

- Markdown remains the only project-content authority;
- page IDs, parent links, related links, and project links validate;
- indexes were regenerated;
- completed tasks link to evidence;
- decisions and rejected directions remain visible;
- history records the change and next safe action;
- the renderer can open the project;
- content and layout annotations remain separate;
- page changes can be copied for an agent;
- a fresh session can resume using `start-here.md` without the preceding chat.

## Project vs skill ownership + onboarding (comprehensive, Option A)

Project `living-documents-system` owns `template/` — single source of truth, git history in project, no skill bump. Skill `custom-skills/living-documents/template` is symlink `-> ../../living-documents-system/template` for harness distribution; installer copies directory when symlink cannot be created (Windows). Skill owns `scripts/ld`, `ld-shim`, `VERSION`, `renderer/`, and `skills/onboard.md`. Renderer resolves via `LIVING_DOCUMENTS_RENDERER` env, fallback to skill `renderer/`.

### Onboarding — one stdlib script + one LLM skill (mirrors weekly-llm-analysis)

**Script `ld onboard --project /code/<name> --with-template [--now]`** (stdlib, offline, idempotent, byte-identical): `create_project` if missing with `source-root` = code path; stats via `rglob` (`fileCount`/`mdCount`/`totalBytes`/`totalLinesMd`), `git status --porcelain` (`gitDirty`/`gitDirtyCount`), `tree` sample 50/200 (`fileIndexSample`, `fileIndexTruncated`), `prd.md` check (`prd.md`/`PRD.md`/`requirements.md`/`docs/prd.md`/`spec.md`); imports dashboard canonical `window.__WEEKLY__` weeks + `telemetry.json` + `vault_project_map.json` from `/home/cheta/code/weekly-report-dashboard` (share one table, no duplicate collection); writes `prompt-corpus.md` placeholder + `file-index.md` tree via `write_page` only; `generated_at` from newest input `mtime`, `sort_keys` idempotence; per-item `problems` isolation, provenance `verified`/`estimated`/`unavailable` on stats; never writes `FORMAT_VERSION`, never mutates historic corpus files.

**Skill `living-documents:onboard`** (`skills/onboard.md`): consumes script JSON + `cass triage --json` + `cass search` + `~/.local/share/muse/sessions/**/*.jsonl` (muse not in cass) + vault scan 10-50 md. Writes only `*.md` body in `LIVING_DOCUMENTS/projects/<id>/`: `prompt-corpus.md` (spell-fixed full prompt, 100% fidelity, no truncation), `project.md` (2-para summary + boundary), `file-index.md` (1-liner per file), `requirements.md` (user stories), `history.md` (changelog generalization, raw `session.jsonl` stays evidence), `what-to-do.md` (phases → todo + next item). Model pinning via `.env` `MODEL=opencode/deepseek-v4-flash`; resolver `.env` → `$MODEL` → `config.env` → default. Token budget 4KB/page, 32KB total. If LLM disagrees with canonical stats, canonical wins, disagreement logged to `problems`.

**Failure modes:** no API key / no network / provider down → deterministic heuristic supplement with `model: heuristic-fallback`, `data_quality: estimated`, so `ld validate` still passes; malformed LLM JSON → log to `problems`, retain prior body; missing dashboard table → `weeklyImport: false`, `provenance: unavailable`, LLM notes gap; never aborts canonical page.

**Schedule + loop:** script nightly `0 20 * * 5` like dashboard, skill headless `omp run --model opencode/deepseek-v4-flash` on change or `ld onboard --now`. Meta-improve: `scripts/audit_onboard.py --json` scores prompt completeness / file-desc coverage, `meta_improve.py` proposes deltas that raise `overall_avg`/`Actionability` without regressing `Truthfulness/Provenance`, applied only if `ld validate` stays green.

**Gates:** `ld onboard` exit 0 + JSON `stats.fileCount` + `weeklyImport` when dashboard present; `ld validate --project <id>` + `ld doctor` healthy; rerun idempotent (same bytes when source unchanged).
