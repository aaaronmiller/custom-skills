---
title: Intake checklists
version: "4.0.0"
tags: [spec-prep]
---

# Intake checklists

## Contents

- [Confidence Gate](#confidence-gate)
- [Discovery Questions (Interactive mode)](#discovery-questions-interactive-mode)
- [Prior Art Research Checklist](#prior-art-research-checklist)

## Confidence Gate

*Formerly `#confidence-gate`, version 1.0.0.*

Use the dimensions to identify missing information. A weighted score is advisory, not an empirical probability or an approval gate. Sufficient information for the next authorized action controls progress; no score changes the output mode.

| Dimension | Weight | 0 to 25% | 50% | 75% | 100% |
|-----------|--------|----------|-----|-----|------|
| Problem clarity | 12% | Vague pain | Stated, root cause unclear | Root cause with evidence | Quantified before and after |
| Solution definition | 12% | "Something like X" | Concept described | Workflow walkthrough possible | End-to-end journey articulable |
| User personas | 8% | "People who" | One persona | 2 to 3 distinct | Goals, frustrations, context |
| Success criteria | 10% | "It should work" | Qualitative | Measurable | Testable with targets |
| Data model | 12% | No entities | Some named | Entities and relationships | Access patterns and lifecycle |
| Scope boundaries | 8% | Open-ended | Some exclusions | In and out list | Boundary rationale documented |
| Technical constraints | 10% | None | Platform mentioned | Platform, perf, integration | Full constraint matrix |
| Business context | 10% | None | OSS vs commercial decided | Distribution and monetization | Competitive position |
| Layer-separation integrity | 10% | Intent, spec, implementation fully fused in what the user said | Two of three separable | All three separable with effort | User already speaks in distinct layers |
| Continuity readiness | 8% | Nothing to seed a ledger | Some decisions implied | Kickoff decisions extractable | First standing.md writable now |

Ask only about material missing inputs that block their dependent action; continue independent reversible preparation. State the understood scope and provisional defaults without redundant confirmation. Respect native clarification marker limits, keeping other unresolved source needs in the assumption/source map rather than dropping them.

The two spec-prep-specific dimensions matter most. Layer-separation integrity below 50% means the user is speaking in fused layers and the artifacts will inherit the fusion unless intake separates it first. Continuity readiness below 50% means the project cannot seed a ledger and will be born without the spine.

## Discovery Questions (Interactive mode)

*Formerly `#discovery-questions-interactive-mode`, version 1.0.0.*

Do not ask all of these at once. Proceed by category, 2 to 4 questions per round, reassessing the Confidence Gate after each. Use the structured-question tool when available so the user taps rather than types. As answers arrive, tag each one as intent, spec, or implementation; the separation begins in the interview, not in the artifacts.

### Problem space
What problem does this solve and who has it. What happens today without it. What do people use now and why is it insufficient.

### Solution vision
What does success look like for the user, as an outcome not a task. Walk the primary workflow start to finish. What is explicitly out of scope for the first version.

### Users and adoption
Who are the one to three primary user types. What is their technical sophistication. How do they discover and adopt this. What makes them choose this over the alternative.

### Data and state
What must be stored. What are the relationships between entities. What is the data lifecycle. What are the privacy and retention requirements.

### Technical constraints
Target platforms. Offline requirement. Performance expectations as numbers. Integration requirements. Deployment target (capture this as an intent constraint, never as an architecture).

### UX and interaction
What interaction pattern fits. What design language fits the audience. Accessibility requirements. How errors surface. Responsive, PWA, offline-first needs. Internationalization needs.

### Business and distribution
Open source, commercial, or internal. Monetization if any. Competitive landscape. Regulatory and compliance requirements.

### spec-prep-specific probes (always ask before exiting intake)
Which decisions does the user want fixed up front versus left for the system to resolve. This populates `substrate.md`. What is the single sentence outcome. If it does not fit in one sentence, intake is not done. What are the failure branches when things go wrong. These become intent failure conditions, not spec test cases.

### Done criteria per category
Problem space: articulate the problem to a stranger in 2 sentences. Solution vision: walk the primary workflow step by step. Users: name each persona and explain why they care. Data: sketch the entity relationships. Technical: list hard constraints vs preferences. UX: describe the first 30 seconds of interaction and the primary navigation model. Business: explain who pays (or why free) and how users find it.

## Prior Art Research Checklist

*Formerly `#prior-art-research-checklist`, version 1.1.0.*

Mandatory in Phase 2 and enforced by the prior-art gate in SKILL.md, which applies in every intake mode, including existing specs and referenced use. The minimum is a floor, not a ceiling. Always survey how others approached the problem and extract reusable patterns and documented pitfalls. Findings land in `intent.md` section 10 (Prior art). A prior-art record supplied with the intake (for example `sources/prior-art.md`) is preserved as evidence and summarized in section 10, not rewritten or discarded. The survey should happen early, before design work goes deep: its verdict can turn a build into a fork.

### Step 1: Local workspace scan (always first)

Check for existing agent configs and related projects that already solve or partially solve the problem: `.claude/`, `.cursor/`, `.agents/`, `skills/`, `.skillshare/`, `.kiro/`, `.windsurf/`, `.openclaw/`, `~/.config/hermes/`, `.specify/`, `openspec/`, and any existing `spec-prep/` tree (an existing tree means this skill does not apply).

### Step 2: Skill registries (minimum 2 searches)

`skills.sh`, `agentskills.io`, `npx antigravity-awesome-skills`, `mcpmarket.com/tools/skills`.

### Step 3: Code search (minimum 3 searches)

Direct problem description, alternative framing, technology-specific framing. For each relevant result extract repository, stars, last commit, license, how they solved the core problem, strengths, weaknesses, and reusable architectural patterns.

### Step 4: Web research (minimum 2 searches)

Current state of the art with the current year, and a comparison or "best of" framing. Also check package registries for sub-problem libraries and practitioner forums for real-world failure reports. Ground every claim in a current search; do not assume training knowledge is current.

### Step 5: Competitive analysis (if commercial)

Three to five closest competitors, feature parity, differentiation, pricing, IP concerns.

### Synthesis

Record a verdict for the closest candidates: build new, fork, extend, or use as is. If an existing tool fully solves the problem, stop, surface it with a comparison, and ask the user explicitly whether to proceed and what gap this fills. Do not proceed until confirmed. If it partially solves, document coverage and gaps, adopt its strengths into the design, and define the unique value. If nothing exists, document that the search was thorough and consider why no one has built it.

### Output

Comparison table, patterns adopted, and patterns avoided go into `intent.md` section 10. Process notes go nowhere. If a known project is later found to have been missed, append a ledger entry recording what was missed, when it surfaced, and why it matters, then update `intent.md`.
