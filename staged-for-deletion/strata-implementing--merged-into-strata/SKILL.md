---
name: strata-implementing
description: 'Use when specifications are authored and ready to build: running the
  full spec-driven pipeline end-to-end, generating constitution/spec/plan/tasks
  automatically, or executing a STRATA project folder through to implementation.
  Consumes intent/spec/plan authored by strata-authoring, or a requirements.md plus
  design.md pair. Triggers: "run speckit", "strata implement", "execute the specs",
  "build from spec", "full speckit pipeline", "autonomous run", "sdd run", "spec-driven
  development pipeline", "take it through to tasks", "and build it". Do NOT use to
  author or revise specifications; strata-authoring owns that.'
license: MIT
metadata:
  author: pi
  version: '2.0'
  pairs-with: strata-authoring
  supersedes: [speckit-autonomous-run]
tags:
- planning
- automation
grade: B
source: custom
---

# STRATA Implementing

> Full spec-driven pipeline, from authored specifications to implementation in one
> autonomous sequence.

This is the execution half of STRATA. `strata-authoring` produces the
specifications; this skill builds them. It does not author or revise specs: if
the inputs are thin, stop and hand back rather than inventing requirements.

## Inputs

Either of:

1. **A STRATA project folder** — the Living Documents dossier at
   `~/LIVING_DOCUMENTS/projects/<project-id>/`, containing `intent`, `spec`,
   `plan`, `plays`, `substrate`, and a seeded ledger. Read the `start-here`
   standing page and the ledger tail **first**; they state where the project is
   and what the next safe action is.
2. **A `requirements.md` plus `design.md` pair** in a `specs/` directory.

Record progress back to the project folder as you go. The ledger is append-only
and updated on every decision and outcome, not at milestones. A build whose
decisions were never written down leaves the next session to reconstruct them
by archaeology, which is the failure STRATA exists to prevent.

## Prerequisites

- `specify` CLI installed (`uv tool install specify-cli --from git+https://github.com/github/spec-kit.git`)
- Project initialized: `specify init --here --integration pi --force`
- Two input files exist at `specs/requirements.md` and `specs/design.md`

## Workflow Overview

```
[specs/requirements.md]  ─┐
                          ├──→ /speckit.constitution ─→ .specify/memory/constitution.md
[specs/design.md]        ─┘         │
                                    ▼
                          /speckit.specify ─→ specs/NNN-feature/spec.md
                                    │
                                    ▼
                          /speckit.plan ─→ specs/NNN-feature/plan.md
                                    │
                                    ▼
                          /speckit.tasks ─→ specs/NNN-feature/tasks.md
                                    │
                                    ▼
                          Edit AGENTS.md / CLAUDE.md → wire constitution INLINE
                                    │
                                    ▼
                          RELOAD or restart the agent (loads the constitution)
                                    │
                                    ▼
                          Verify constitution is in context, then /speckit.implement
```

## Input Files Location

| File | Required Path | Purpose |
|------|-------------|---------|
| `specs/requirements.md` | Requirements & user stories (what/why) |
| `specs/design.md` | Architecture & tech stack decisions (how) |
| `specs/` | Root directory for all spec artifacts |

The `specs/` directory is the canonical location for all spec-driven development artifacts. If `specs/` doesn't exist yet, create it.

If the inputs already live in a numbered feature directory (for example `specs/003-name/requirements.md`), generate the speckit artifacts INTO that same directory instead of letting `/speckit.specify` mint a new number. Align the git branch to that directory (`git checkout -b 003-name`) so `check-prerequisites.sh` resolves the feature; otherwise the commands fragment the work across `003` and a new `004`.

## Execution Sequence

### Step 0: Validate Prerequisites

```bash
# Check specify CLI is available
which specify >/dev/null 2>&1 || uv tool install specify-cli --from git+https://github.com/github/spec-kit.git

# Check input files exist
test -f specs/requirements.md || { echo "Missing: specs/requirements.md"; exit 1; }
test -f specs/design.md || { echo "Missing: specs/design.md"; exit 1; }

# Check project is initialized
test -f .specify/memory/constitution.md || specify init --here --integration pi --force
```

### Step 1: Generate Constitution

Read the constitution template at `.specify/memory/constitution.md`, then fill it with project-specific values using:

```
/speckit.constitution <constitution prompt derived from specs/requirements.md and specs/design.md>
```

The constitution prompt MUST include:
- Project name (from `specs/requirements.md` or directory name)
- The core principles the requirements/design imply. **Do NOT assume a fixed count.** The
  template ships five placeholders, but a real constitution may need fewer or more. Add or remove
  `### Principle` headings as the project requires. Whatever count you land on, that exact set is
  the authoritative list every downstream step must match.
- The additional sections (constraints, workflow, governance)
- Version + ratification date

**If a complete, ratified constitution already exists** (no `[ALL_CAPS_PLACEHOLDER]` tokens remain), do NOT regenerate it. Regenerating clobbers ratified governance. Verify completeness and keep it.

**Template placeholder mapping:**

| Placeholder | Source |
|-------------|--------|
| `[PROJECT_NAME]` | Project name from requirements or CWD basename |
| `[PRINCIPLE_1_NAME]` through `[PRINCIPLE_5_NAME]` | Derived from design.md constraints |
| `[PRINCIPLE_1_DESCRIPTION]` through `[PRINCIPLE_5_DESCRIPTION]` | Derived from design.md decisions |
| `[SECTION_2_NAME]` | "Technical Constraints" |
| `[SECTION_2_CONTENT]` | Tech stack, platform, dependencies from design.md |
| `[SECTION_3_NAME]` | "Development Workflow" |
| `[SECTION_3_CONTENT]` | Quality gates, review process from requirements |
| `[GOVERNANCE_RULES]` | Standard governance text |
| `[CONSTITUTION_VERSION]` | "1.0.0" |
| `[RATIFICATION_DATE]` | Today's date |
| `[LAST_AMENDED_DATE]` | Today's date |

After filling, verify no `[ALL_CAPS_PLACEHOLDER]` tokens remain.

### Step 2: Generate Specification

```
/speckit.specify <content of specs/requirements.md>
```

Creates `specs/NNN-feature-name/spec.md` with prioritized user stories (P1, P2, P3...), functional requirements, acceptance criteria, and edge cases. If the feature directory already exists (see Input Files note), generate `spec.md` into it rather than creating a new number.

### Step 3: Generate Plan

```
/speckit.plan <content of specs/design.md>
```

Creates `specs/NNN-feature-name/plan.md` plus research.md, data-model.md, contracts/, quickstart.md. The plan contains a **Constitution Check gate**. That gate is only meaningful if the constitution is actually in the agent's context (see Step 5 and the Reload note). Read `.specify/memory/constitution.md` while filling the gate; do not rubber-stamp it.

### Step 4: Generate Tasks

```
/speckit.tasks
```

Creates `specs/NNN-feature-name/tasks.md` (ordered by user story, `[P]` parallel markers, file paths).

### Step 5: Wire AGENTS.md / CLAUDE.md to the Constitution

This step is the one that historically corrupted the gate. The failure mode: the agent typed the
principle names **from memory** and pulled in rules from the global `~/.claude/CLAUDE.md` (e.g.
"no hardcoded model names") that are NOT constitution principles, while silently dropping real
ones. The corrupted list then filled the plan gate and passed a circular "name the principles"
check. **Never type the principle names from memory. Extract them mechanically from the file.**

**5a. Extract the authoritative principle headings from the file you just generated:**

```bash
grep -nE '^### (Principle |[IVX]+\.|[0-9]+\.)' .specify/memory/constitution.md
# Fallback if headings are not numbered:
grep -nE '^### ' .specify/memory/constitution.md
N=$(grep -cE '^### ' .specify/memory/constitution.md)   # authoritative principle count
```

The strings this prints are the ONLY acceptable principle names. Copy them verbatim.

**5b. Inline into the project `CLAUDE.md` (or `AGENTS.md` if it exists). Prefer the FULL text so
it survives context compaction; fall back to exact headings + a hard re-read trigger only if the
full text would push the file over the 300-line Progressive-Disclosure limit:**

```bash
# Decide: does inlining the full constitution keep CLAUDE.md under 300 lines?
LINES_NOW=$(wc -l < CLAUDE.md); CONST_LINES=$(wc -l < .specify/memory/constitution.md)
# If (LINES_NOW + CONST_LINES) <= 300  -> inline the FULL constitution body.
# Else -> inline the exact ### headings from 5a + the MANDATORY re-read trigger below.
```

Full-text form (preferred):
```markdown
## Constitution (full text, inlined for compaction survival)

<paste the entire body of .specify/memory/constitution.md here, verbatim>
```

Headings + trigger form (only if full text breaks the 300-line limit):
```markdown
## Constitution

Authoritative principles (copied verbatim from `.specify/memory/constitution.md`, count = N):
<paste the exact ### headings from 5a — no additions, no paraphrase>

Engineering constraints / workflow: see the file.

**MANDATORY (survives compaction):** Before running any `/speckit.*` command, filling or editing a
`plan.md` Constitution Check, or marking any task complete, you MUST Read
`.specify/memory/constitution.md` in full. The names above are for drift detection only; the file
body is the source of truth.
```

**Critical correctness notes:**
- The names in CLAUDE.md MUST be an exact set match with the 5a output: same count, same strings,
  nothing added, nothing dropped. If you cannot reconcile them, STOP and re-read the file.
- This wiring feeds the **Constitution Check gate** in `/speckit.plan` and the gating in
  `/speckit.implement`. A bare file pointer can be skipped if the agent never opens the file.
- If `CLAUDE.md` is wrapped in tool-managed markers (e.g. RTK `<!-- rtk-instructions -->`), append
  the constitution section OUTSIDE those markers so auto-regeneration does not erase it.
- Touch only the project-local `CLAUDE.md`/`AGENTS.md`. Do not edit the global
  `~/.claude/CLAUDE.md`, a sibling `.claude/CLAUDE.md`, or unrelated agent CLAUDE.md files.
- **The RUNNING agent does not see this edit until its context is reloaded.** Mid-session edits do
  not retroactively load. This is a common cause of constitution gates passing incorrectly.

### Step 5.5: Gate-validity rule (applies to plan.md and tasks.md)

A `plan.md` Constitution Check is VALID only if it enumerates **every** `### ` principle heading
from `constitution.md` (count = N from 5a), each marked PASS / FAIL / N/A with a justification. A
gate is INVALID — and blocks `/speckit.implement` — if it:
- enumerates fewer than N principles, or
- lists items that are NOT headings in `constitution.md` (e.g. "reuse over duplication", "no
  hardcoded model names" when those are not constitution headings).

When generating or reviewing `tasks.md`, confirm that tasks touching destructive operations
(teardown, force-resets, atomic swaps, alias/file installation) and configuration surfaces are
covered by the principles their gate claims to honor. If the gate never evaluated the relevant
principle, the tasks cannot honor it — fix the gate first.

### Step 6: Reload, Verify, then Implement

The pipeline is now scaffolded, but the constitution wiring from Step 5 is not yet in the running agent's context. Do NOT run `/speckit.implement` in the same session that wrote the wiring.

1. **Reload or restart the agent** so the updated `CLAUDE.md`/`AGENTS.md` (and thus the constitution) is loaded. See Reload Semantics below.
2. **Verify by FILE CROSS-CHECK, not recitation.** Asking the agent to "name the principles" is
   circular: after reload it reads the names from CLAUDE.md and recites them, which proves only
   that recitation matches CLAUDE.md — not that CLAUDE.md matches the constitution. That circular
   check is what let a corrupted list pass historically. Instead, diff the two sources:

   ```bash
   diff <(grep -E '^### ' .specify/memory/constitution.md | sed 's/^### //') \
        <(grep -E '^- |^[0-9]+\. ' CLAUDE.md | grep -if <(grep -E '^### ' .specify/memory/constitution.md | sed 's/^### //'))
   ```

   The principle set in CLAUDE.md must be an exact match (count and strings) with the `### `
   headings in the constitution. Then confirm `plan.md`'s Constitution Check enumerates all N of
   them (the Step 5.5 gate-validity rule). If either fails, the gate is invalid — fix it before
   implementing, do not proceed on a recited-but-unverified list.
3. **Run** `/speckit.implement` to begin executing the tasks.

You cannot pipe `/speckit.implement` across the reload in a single turn, because the reload resets context. The reliable sequence is: finish the skill, send `/reload` (or restart), then send `/speckit.implement` as the next message once the reload completes.

## Reload Semantics and the Constitution Gate

- CLAUDE.md files from every applicable location (global `~/.claude/CLAUDE.md`, project-root `CLAUDE.md`, sibling `.claude/CLAUDE.md`, parent directories) are **combined** into context at session start. They are **additive**, not one superseding another. Adding a constitution section to the project `CLAUDE.md` augments the loaded context; it erases nothing.
- A `/reload` or a full restart re-reads all of these fresh and re-combines them. A full restart is the reliable equivalent if `/reload` is unavailable in your harness.
- Because the load happens at session start, any edit made during a session is invisible to that same session until reload. The Constitution Check gate evaluated by a session that never loaded the constitution is not a real gate. Always reload between Step 5 and `/speckit.implement`.
- For maximum safety, inline the principle names in `CLAUDE.md` (Step 5) so the gate has the principles even without opening the constitution file.

## AGENTS.md Integration Pattern

```markdown
## Speckit Workflow Automation

This project uses `speckit-autonomous-run` for spec-driven development.
When you have `specs/requirements.md` and `specs/design.md` ready, this skill
will autonomously execute the full pipeline.

Workflow:
1. Place `requirements.md` (what/why) and `design.md` (how) in `specs/`
2. Invoke this skill → constitution → spec → plan → tasks → wire constitution
3. Reload the agent, verify the constitution is loaded
4. Run `/speckit.implement` to execute
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `specify: command not found` | Install: `uv tool install specify-cli --from git+https://github.com/github/spec-kit.git` |
| `.specify/memory/constitution.md` missing | Run: `specify init --here --integration pi --force` |
| Constitution still has `[PLACEHOLDER]` tokens | Run `/speckit.constitution` with explicit values |
| Constitution gate passed but feels rubber-stamped | Cross-check, do not recite. Diff the `### ` principle headings in `.specify/memory/constitution.md` against the names wired into `CLAUDE.md` (Step 6) and against the gate's enumerated list in `plan.md`. A gate that lists fewer than N principles, or items that are not constitution headings (e.g. "no hardcoded model names"), is INVALID — rewrite it to enumerate all N, then re-run the gated step. |
| CLAUDE.md principle list disagrees with constitution.md | The names were typed from memory, not extracted from the file (the original failure). Re-run Step 5a `grep -E '^### '` and copy the headings verbatim; never paraphrase from the global `~/.claude/CLAUDE.md`. |
| `/speckit.specify` created a new `NNN` dir instead of using the existing one | Align the git branch to the existing feature dir and generate artifacts into it; see the Input Files note. |
| `check-prerequisites.sh` errors "Not on a feature branch" | Checkout a branch named like `003-feature-name`, or export `SPECIFY_FEATURE=003-feature-name`. |
| Plan references "NEEDS CLARIFICATION" | Run `/speckit.clarify` or fill placeholders manually |
| Tasks out of date after spec change | Run `/speckit.tasks` again to regenerate |
| `/speckit.implement` blocks on checklists | Run `/speckit.checklist <domain>` then complete items |

## References

- [github/spec-kit](https://github.com/github/spec-kit): Official Spec Kit repository
- Constitution template: `.specify/templates/constitution-template.md`
- Spec template: `.specify/templates/spec-template.md`
- Plan template: `.specify/templates/plan-template.md`
- Tasks template: `.specify/templates/tasks-template.md`
