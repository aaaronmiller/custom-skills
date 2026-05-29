---
name: speckit-autonomous-run
description: |
  Use when: initiating a new feature or project build, running the full Spec-Driven Development workflow, need to generate constitution/spec/plan/tasks automatically, have requirements.md and design.md ready and want to execute the speckit pipeline end-to-end. Triggers: "run speckit", "speckit autonomous", "init speckit project", "build from spec", "execution plan for speckit", "full speckit pipeline", "automated speckit", "speckit run", "specify workflow", "sdd run", "spec-driven development pipeline", "autonomous speckit execution".
license: MIT
metadata:
  author: pi
  version: "1.0"
---

# Speckit Autonomous Run

> **Full Spec-Driven Development pipeline — from requirements to tasks in one autonomous sequence.**
> Requires `requirements.md` and `design.md` in the project's `specs/` directory.

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
                          Edit AGENTS.md → point AGENTS.md instructions to
                          .specify/memory/constitution.md
                                    │
                                    ▼
                          Wait for user `/reload` + `/speckit.implement`
```

## Input Files Location

| File | Required Path | Purpose |
|------|-------------|---------|
| `specs/requirements.md` | Requirements & user stories (what/why) |
| `specs/design.md` | Architecture & tech stack decisions (how) |
| `specs/` | Root directory for all spec artifacts |

The `specs/` directory is the canonical location for all spec-driven development artifacts. If `specs/` doesn't exist yet, create it.

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

Read the constitution template at `.specify/memory/constitution.md`, then fill it with project-specific values using the format:

```
/speckit.constitution <constitution prompt derived from specs/requirements.md and specs/design.md>
```

The constitution prompt MUST include:
- Project name (from `specs/requirements.md` or directory name)
- 5 core principles extracted from requirements and design
- 3 additional sections (constraints, workflow, governance)
- Version + ratification date

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

Run the `/speckit.specify` command with the content of `specs/requirements.md` as the argument:

```
/speckit.specify <content of specs/requirements.md>
```

This creates `specs/NNN-feature-name/spec.md` with:
- Prioritized user stories (P1, P2, P3...)
- Functional requirements
- Acceptance criteria
- Edge cases

### Step 3: Generate Plan

Run the `/speckit.plan` command with the content of `specs/design.md` as the argument:

```
/speckit.plan <content of specs/design.md>
```

This creates `specs/NNN-feature-name/plan.md` with:
- Tech stack decisions
- Architecture overview
- Data model
- Implementation phases
- Research notes

### Step 4: Generate Tasks

Run `/speckit.tasks` with no additional arguments — it reads from the plan:

```
/speckit.tasks
```

This creates `specs/NNN-feature-name/tasks.md` with:
- Ordered task list by user story
- Dependency management
- Parallel execution markers `[P]`
- File path specifications

### Step 5: Wire AGENTS.md to Constitution

Edit the project's `AGENTS.md` (or `CLAUDE.md`) to add a reference to the constitution:

```markdown
## Constitution

This project follows a governing constitution at `.specify/memory/constitution.md`.
The constitution establishes non-negotiable principles that MUST be followed
during all development phases. Before implementing, read the constitution.
```

This ensures subsequent `/speckit.*` commands and any agent working on the project
references the constitution.

### Step 6: Handoff for Reload + Implement

The speckit pipeline is now fully scaffolded. The next steps require a user action:

1. **User runs `/reload`** (or equivalent) to refresh the agent context
2. **User runs `/speckit.implement`** to begin executing the tasks

## AGENTS.md Integration Pattern

Add to your project's `AGENTS.md` (or `CLAUDE.md`):

```markdown
## Speckit Workflow Automation

This project uses `speckit-autonomous-run` for spec-driven development.
When you have `specs/requirements.md` and `specs/design.md` ready, this skill
will autonomously execute the full pipeline.

Workflow:
1. Place `requirements.md` (what/why) and `design.md` (how) in `specs/`
2. Invoke this skill → auto-generates constitution → spec → plan → tasks
3. Review the generated artifacts
4. Run `/speckit.implement` to execute
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `specify: command not found` | Install: `uv tool install specify-cli --from git+https://github.com/github/spec-kit.git` |
| `.specify/memory/constitution.md` missing | Run: `specify init --here --integration pi --force` |
| Constitution still has `[PLACEHOLDER]` tokens | Run `/speckit.constitution` with explicit values |
| Plan references "NEEDS CLARIFICATION" | Run `/speckit.clarify` or fill placeholders manually |
| Tasks out of date after spec change | Run `/speckit.tasks` again to regenerate |
| `/speckit.implement` blocks on checklists | Run `/speckit.checklist <domain>` then complete items |

## References

- [github/spec-kit](https://github.com/github/spec-kit) — Official Spec Kit repository
- Constitution template: `.specify/templates/constitution-template.md`
- Spec template: `.specify/templates/spec-template.md`
- Plan template: `.specify/templates/plan-template.md`
- Tasks template: `.specify/templates/tasks-template.md`
