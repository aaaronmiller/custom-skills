---
name: spec-audit-skill
description: '**DEPRECATED — Use spec-audit-skill-v3 instead.** (cataloguing features
  with what & why), generate backtranslation questions for S-tier model evaluation,
  run deliberative refinement councils to compare internal vs external perspectives,
  and produce ideal-spec.md with a modification task list.


  Use when: user says "audit this project", "spec audit", "reverse engineer the spec",
  "meta-assessment", "generate ideal spec", "backtranslation questions", "compare
  as-built vs ideal", "spec review", "knowledge base audit", "architecture audit",
  "design audit", "evaluate my project''s spec", "find gaps in spec", "spec gap analysis",
  "produce ideal spec", or asks for a systematic feature inventory with external validation.
  Also triggers on phrases like "what does this project actually do", "catalog features",
  "document what we built and why", "external perspective on our design", "council-based
  spec review".


  Triggers: "spec audit", "reverse engineer spec", "spec-as-built", "ideal-spec",
  "backtranslation questions", "meta-assessment", "deliberative refinement [project]".'
tags:
- planning
grade: C
source: custom
---

# Spec Audit Skill

> Find out what you *actually* built, then find out what you *should* have built.

This skill encodes a repeatable methodology for any project — from a small library to a multi-agent system — to:

1. **Reverse-engineer** the project's feature surface into `spec-as-built.md` (describing each feature in terms of **what** it does and **why** it exists)
2. **Generate backtranslation questions** from those features — questions that probe the ideal design space
3. **Guide** the user to submit those questions to an S-tier model (Opus 4.x, GPT-4.5, Gemini 3 Pro, etc.) for external answers
4. **Orchestrate deliberative refinement councils** comparing the as-built spec vs the external answers
5. **Produce `ideal-spec.md`** and a **task list** for modifications

The user submits questions to the S-tier model on their own (to avoid API costs). You handle everything else.

---

## Process Overview

```
Project files → [Phase 1: Reverse Engineer] → spec-as-built.md
                                                 ↓
                                 [Phase 2: Backtranslate] → questions.json
                                                                ↓
                                          User submits to S-tier model (external)
                                                                ↓
                                          User returns external-answers.md
                                                                ↓
                                 [Phase 3: Council Formation] → council selection
                                                                     ↓
                                          [Phase 4: Run Councils] → internal vs external
                                                                         ↓
                                                         ideal-spec.md + task-list.md
```

---

## Phase 1: Reverse Engineer → `spec-as-built.md`

The goal is a feature catalog that answers **what** each feature does and **why** it exists — not *how* it's implemented. Implementation details only appear when they're the feature itself (e.g., "systemd idle timer" is the mechanism, but "background processing during idle cycles" is the feature).

### 1.1 Read, don't skim

Read every meaningful source file in the project. For projects larger than ~20 files, prioritize:
- Core source files (main entry points, CLI, API)
- Configuration/schema files (they encode design decisions)
- Spec/design docs (requirements, architecture, design)
- Build/setup scripts (install, CI/CD)
- Tests (they encode expected behavior)

### 1.2 Catalog each feature

For each feature, record:

```
- id: F-001
  name: Short feature name
  what: What it does — the observable behavior or capability
  why: Why it exists — the design rationale, the problem it solves, the tradeoff it makes
  where: Which files/directories implement it (for traceability, not implementation detail)
  dependencies: Other features it requires (by F-ID)
  quality_indicators:
    - Completeness: How well does it cover the obvious use cases?
    - Consistency: Does it clash with any other feature?
    - Test coverage: Are there tests? (yes/no/partial)
```

### 1.3 Structure the document

```markdown
# Project Name — Spec As Built v1.0

## Overview
One-paragraph summary of what the project does and what it's for.

## Feature Catalog

### F-001: Short Feature Name
- **What:** ...
- **Why:** ...
- **Where:** ...
- **Depends on:** ...
- **Quality:**
  - Completeness: [high/medium/low]
  - Consistency: [good/minor issues/conflicts]
  - Tests: [yes/no/partial]

### F-002: ...

## Architecture Summary
3-5 sentence description of how features compose — the system's structural gestalt.

## Observable Patterns
- What design philosophy does the project express?
- What assumptions does it make about its environment?
- What is it *not* doing that similar projects do? (deliberate omissions)
```

### 1.4 Ground rules

- **No implementation detail** as feature. "Uses YAML frontmatter" is not a feature. "Permanent provenance tracking via YAML metadata" is.
- **Be honest about quality.** Flag incomplete, inconsistent, or untested features. The audit is useless if it flatters.
- **Surface contradictions.** If two features pull in opposite directions, say so explicitly.
- **Document what's missing.** If a capability the project clearly *needs* is absent, note it as a gap.

### 1.5 Output

Write `spec-as-built.md` in the project root (or the directory where the audit is being run).

---

## Phase 2: Backtranslate → `questions.json`

From the feature catalog, generate questions that probe what an **ideal** version of the project would look like. This is backtranslation: you have the features (answers), now generate the questions that would elicit better answers.

### 2.1 Question categories

Generate questions across these dimensions:

| Category | Purpose | Example |
|----------|---------|---------|
| **Design Philosophy** | Probe foundational choices | "Should a sleep-time compute system optimize for recall or precision at the cost of latency?" |
| **Architecture** | Probe structural decisions | "Should the dream agent be a sidecar or embedded in the memory tier?" |
| **Feature Scope** | Check if a feature is solving the right problem | "Is 'automatic skill creation from patterns' a feature the system needs, or should it just compile knowledge?" |
| **Tradeoffs** | Surface implicit decisions | "What does the system lose by using REST API instead of pub/sub between dream agent and memory tier?" |
| **Gaps** | Ask about missing pieces | "How should the system handle conflicting information from two equally recent sources?" |
| **Prioritization** | Force ranking | "If you could only keep 3 features, which ones? Why?" |
| **Alternatives** | Challenge the approach | "What would this look like as a pure SQLite extension instead of a three-tier system?" |

### 2.2 Write good questions

- **Specific**, not generic. Reference actual features and architecture. Bad: "What would you change?" Good: "F-012 (auto-skill creation from patterns) triggers at 3 occurrences. Should this threshold be adaptive based on session volume?"
- **Falsifiable.** The S-tier model's answer should be something you can compare against your own reasoning.
- **10–20 questions** total. Enough to be thorough, few enough that the user can submit them in one or two passes.
- **Each question MUST reference** the specific F-ID it targets (or "GENERAL" for cross-cutting).

### 2.3 Output

Write `questions.json`:

```json
{
  "project": "Project Name",
  "spec_as_built_version": "1.0",
  "date": "YYYY-MM-DD",
  "total_questions": 15,
  "categories": ["design-philosophy", "architecture", "feature-scope", "tradeoffs", "gaps", "prioritization", "alternatives"],
  "instructions": "Read spec-as-built.md first, then answer each question. Reference the F-IDs in your answers.",
  "questions": [
    {
      "id": "Q-001",
      "category": "architecture",
      "targets": ["F-003", "F-004"],
      "question": "..."
    }
  ]
}
```

Also write `questions.md` — a human-readable version the user can paste into the S-tier model's interface:

```markdown
# Spec Audit Questions — <Project Name>

Please read `spec-as-built.md` first, then answer each question below. Reference feature IDs where relevant.

## 1. Design Philosophy

**Q-001:** ...
```

---

## Phase 3: Council Formation

After the user returns the S-tier model's answers, select the right council formation(s) for comparing internal (as-built) perspectives vs external (S-tier) answers.

See [references/councils-guide.md](references/councils-guide.md) for detailed selection criteria.

### 3.1 Default recommendation: Parallel Groups

For most projects, use **Parallel Groups** (8 agents, two groups of 4):
- **Group A (Internal):** Argues from the as-built spec's philosophy. Has read the full project codebase and understands the real constraints.
- **Group B (External):** Argues from the S-tier model's answers. Has read the answers and the ideal spec direction.
- **Merge council:** Combines outputs, resolves conflicts, produces unified recommendations.

### 3.2 When to deviate

| Scenario | Formation | Rationale |
|----------|-----------|-----------|
| Small project (<5 features) | **Expert Council** (7 agents) | No need to split — full deliberation |
| Binary "keep or replace" decision on specific feature | **Elimination Tournament** (8→4→2→1) | Forces clear yes/no on each contested feature |
| Deep technical correctness debate | **Structured Review** (reflect→critique→refine) | For implementations with correctness constraints |
| Multiple independent subsystems | **Parallel Groups** (one per subsystem) | Isolate debates per subsystem |
| User wants maximum rigor on one subsystem | **Deep profile** (12 agents, 5 rounds, 2 probes) | Per deliberative-refinement profiles |

### 3.3 Document the selection

Record in `council-plan.md`:

```markdown
# Council Plan — <Project Name>

## Formation
Parallel Groups: Group A (Internal/As-Built, 4 agents) vs Group B (External/Ideal, 4 agents) → Merge Council

## Profile
V(8, 3, 1) — 8 agents, 3 rounds, 1 web probe per gap

## Mode
REFINE (comparing two inputs: as-built spec + external answers)

## Strategy
BRANCHING (exploring the gap between two perspectives, not converging to a single answer early)

## Materials Given to Each Group
Group A: spec-as-built.md
Group B: external-answers.md
Merge Council: Both + outputs from both groups
```

---

## Phase 4: Run Councils → `ideal-spec.md` + `task-list.md`

### 4.1 Execute the deliberation

Use the deliberative-refinement skill's execution flow:
1. **Phase 0:** Confirm intent and formation
2. **Phase 1:** Select council (from Phase 3 plan)
3. **Phase 1.5:** Architect critique of the council plan
4. **Phase 2:** Decompose the comparison into sub-questions
5. **Phase 3:** Run deliberation rounds with probes between rounds
6. **Phase 4:** Synthesize

### 4.2 Output: `ideal-spec.md`

Structured as a diff between what the project currently does and what it *should* do:

```markdown
# <Project Name> — Ideal Spec v1.0

_Generated from spec audit: spec-as-built.md + council deliberation_

## Summary
What changed and why, in 3-5 sentences.

## Kept Features
Features that survived the audit unchanged.
| F-ID | Name | Rationale |
|------|------|-----------|

## Modified Features
Features that need changes, with the diff.
| F-ID | Name | Change | Rationale |

## New Features
Features the project should add.
| F-ID | Name | What | Why |

## Removed Features
Features that should be removed or replaced.
| F-ID | Name | Rationale |

## Architecture Changes
Cross-cutting architectural shifts, if any.
```

### 4.3 Output: `task-list.md`

Actionable, ordered implementation tasks:

```markdown
# Modification Task List — <Project Name>

_Priority order: P0 (blocker) → P1 (significant) → P2 (nice to have)_

## P0 — Must Do
| # | Task | Affects | Effort Estimate |
|---|------|---------|-----------------|

## P1 — Should Do
...

## P2 — Nice to Have
...
```

---

## Files this skill produces

| File | Phase | Purpose |
|------|-------|---------|
| `spec-as-built.md` | 1 | Feature catalog (what & why) |
| `questions.json` | 2 | Structured backtranslation questions |
| `questions.md` | 2 | Human-readable questions for user |
| `council-plan.md` | 3 | Council formation selection and rationale |
| `external-answers.md` | (user-provided) | S-tier model's answers to questions |
| `deliberation-log.md` | 4 | Full council deliberation record |
| `ideal-spec.md` | 4 | Target spec after audit |
| `task-list.md` | 4 | Ordered modification tasks |

---

## Pitfalls

- **Don't over-engineer the questions.** 10-20 good questions beat 50 shallow ones. Each question should take the S-tier model meaningful effort.
- **Don't skip the "why" in spec-as-built.** If you only document "what" features do, the council has no foundation for comparison. Every feature needs its design rationale.
- **The user runs the S-tier model.** Never submit to the model yourself — the user has free accounts they want to use. Prepare everything so they can copy-paste.
- **Don't merge councils prematurely.** Let each group reach independent conclusions before the merge. Early merging defeats the purpose of parallel deliberation.
- **Be specific in task estimates.** "2-4 hours" is better than "small" or "medium". Use the project's actual codebase complexity to gauge.
- **Flag uncertainty.** If you can't determine a feature's rationale from the code, say "RATIONALE UNCLEAR — possible reasons: X, Y, Z. Council should debate."
- **One feature, one row.** Don't bundle unrelated features into one entry. If they're truly coupled, note the coupling explicitly.


