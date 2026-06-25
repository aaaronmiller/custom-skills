---
name: create-new-project
description: 'ALWAYS invoke when the user wants to start a new project, define a new
  feature, plan a new tool, or turn an idea into actionable specifications. Triggers
  on: "new project", "new idea", "build this", "let''s create", "I want to make",
  "project plan", "spec this out", "turn this into a spec", "process these transcripts",
  "idea to spec", "kickoff", "greenfield", "from scratch", "define requirements",
  "write a PRD", "feature spec", "spec-driven", "speckit", "openspec", "requirements
  and design", "project kickoff", "ideation to spec", or when the user provides transcripts/notes/brain
  dumps describing something they want to build. Also triggers when user mentions
  wanting to prepare files for SpecKit, OpenSpec, Cursor spec-driven workflow, Kiro,
  or any spec-driven design tool. Do NOT use for modifying existing specs, code reviews,
  debugging, or ongoing project work.

  '
license: MIT
metadata:
  author: ice-ninja
  version: 1.2.0
tags:
- planning
- writing
grade: A
source: community
---

> **BEFORE USING THIS SKILL:** Read all reference files in `references/` before starting. They contain output templates, research checklists, and data architecture guidance required for proper execution.
>
> **Claude.ai / no-filesystem fallback:** If reference files are not accessible (e.g., running in claude.ai web chat without code execution), the templates and guidance are embedded in this SKILL.md's section headers and Phase 4 descriptions at sufficient detail to produce correct output. Reference files add depth but are not blocking.

# Create New Project

> From brain dump to build-ready specs in one session.

Transforms raw ideas, transcripts, or interactive discussions into SpecKit/OpenSpec-compatible requirements and design documents that feed directly into `specify.spec`, `speckit.specify`, `opsx:propose`, or equivalent spec-driven workflows.

## Two Intake Modes

### Mode A: Transcript Processing
**Trigger:** User provides one or more transcripts, voice notes, brain dumps, or unstructured notes.

### Mode B: Interactive Discussion
**Trigger:** User describes an idea verbally or wants to explore/define it through conversation.

### Fast Track (Mode A or B shortcut)
**Trigger:** User provides a complete, well-structured project description that already covers problem, solution, users, data, constraints, and scope. Simple or well-understood projects (todo apps, CRUD tools, standard integrations) where the user clearly knows what they want.

**Fast track behavior:** Skip the iterative discovery loop. Run the Confidence Gate rubric once. If >= 85% on first pass, proceed directly to Phase 2 (research). If not, drop into Mode B for targeted gap-fill only on sub-threshold dimensions.

Both modes produce identical output written to `./docs/specs/{project-name}/`:

```
docs/specs/{project-name}/
├── requirements.md    # WHAT and WHY (SpecKit spec.md / OpenSpec specs/)
├── design.md          # HOW (SpecKit plan.md / OpenSpec design.md)
└── constitution.md    # Governance reference (copied or symlinked)
```

**Output path note:** The `./docs/specs/` path is a default. If the project already has SpecKit (`specs/`), OpenSpec (`openspec/changes/`), or Kiro (`.kiro/specs/`) directories, write output files to the existing structure instead.

## Confidence Gate

Before generating documents, the intake must reach **85% confidence** across eight dimensions. Score conservatively; one extra round of questions costs minutes, a bad spec costs hours.

| Dimension | Weight | 0-25% (Unclear) | 50% (Partial) | 75% (Solid) | 100% (Crystal) |
|-----------|--------|------------------|----------------|-------------|-----------------|
| Problem clarity | 15% | Vague pain point | Problem stated but root cause unclear | Root cause identified with evidence | Quantified impact, clear before/after |
| Solution definition | 15% | "Something like X" | Core concept described | Workflow walkthrough possible | End-to-end user journey articulable |
| User personas | 10% | "People who..." | 1 persona identified | 2-3 personas with distinct needs | Personas with goals, frustrations, context |
| Success criteria | 10% | "It should work" | Qualitative goals | Measurable outcomes defined | Testable metrics with targets |
| Data model | 15% | No entities discussed | Some entities named | Entities + relationships clear | Access patterns + lifecycle defined |
| Scope boundaries | 10% | Open-ended | Some exclusions stated | In/out scope list exists | Boundary rationale documented |
| Technical constraints | 10% | None stated | Platform mentioned | Platform + perf + integration clear | Full constraint matrix |
| Business context | 15% | None | Open source vs commercial decided | Distribution + monetization clear | Competitive position articulated |

**When confidence < 85%:** Use structured questions targeting the lowest-scoring dimensions. Ask 3-5 questions per round. Reassess after each round. Do not proceed until threshold is met.

**When confidence >= 85%:** Proceed to Phase 2. Note any dimensions below 75% as items requiring `[NEEDS CLARIFICATION]` markers in the requirements document.

## Execution Protocol

### Phase 0: Mode Detection and Setup

1. **Detect mode** from user input:
   - Files/transcripts provided -> Mode A
   - Verbal description or "I want to build X" -> Mode B
   - Mixed (some notes + wants to discuss) -> Mode A first, then Mode B gap-fill

2. **Load references:**
   - Read `references/requirements-template.md` for output format
   - Read `references/design-template.md` for output format
   - Read `references/research-checklist.md` for prior art research protocol
   - Read `references/data-architecture-guide.md` for schema/hosting decisions

3. **Check for user preferences** in memory/context:
   - Preferred stack (frameworks, languages, deployment targets)
   - Design language preferences (Material, shadcn, custom)
   - Hosting preferences (Cloudflare, Vercel, self-hosted)
   - These inform the design document but do NOT appear in the requirements document (requirements are technology-agnostic per SDD principles)

4. **Codebase exploration** (if inside an existing project):
   - Scan for existing architecture patterns, package managers, frameworks in use
   - Check for `.specify/`, `openspec/`, `.kiro/` directories (existing spec infrastructure)
   - Detect constitution.md or equivalent governance files
   - Note existing dependencies, test frameworks, deployment configs
   - Do NOT write exploration findings to files; they are context for the ideation process, not an artifact

### Phase 1: Intake and Extraction

#### Mode A: Transcript Processing

1. **Read all provided transcripts/files**
2. **Extract structured signals:**
   - Problem statements (what pain exists)
   - Proposed solutions (what the user wants to build)
   - User types / personas mentioned
   - Success criteria (how "done" is defined)
   - Constraints mentioned (budget, timeline, platform, privacy)
   - Data entities and relationships implied
   - Integration points mentioned (APIs, services, platforms)
   - UX/workflow descriptions
3. **Compute confidence score** using the Confidence Gate rubric above
4. **If confidence < 85%:** Switch to Mode B for gap-filling discussion, targeting lowest-scoring dimensions
5. **If confidence >= 85%:** Proceed to Phase 2 with extracted signals

**Tool guidance:** When available, use structured input tools (AskUserQuestion, ask_user_input) to present clarifying questions with selectable options rather than open-ended text prompts. This reduces friction and prevents misinterpretation.

#### Mode B: Interactive Discussion

Conduct a structured discovery conversation. Do NOT ask all questions at once. Proceed through these categories sequentially, asking 2-4 questions per category, adapting based on answers:

**Category 1: Problem Space**
- What problem does this solve? Who has this problem?
- What happens today without this solution?
- What existing tools/approaches do people use now, and why are they insufficient?

**Category 2: Solution Vision**
- What does success look like for the user of this tool/product?
- Walk through the primary user workflow from start to finish
- What is explicitly out of scope for v1?

**Category 3: Users and Adoption**
- Who are the 1-3 primary user types?
- What is the user's technical sophistication level?
- How will users discover and adopt this? (distribution channel)
- What would make a user choose this over alternatives?

**Category 4: Data and State**
- What data does the system need to store?
- What are the relationships between data entities?
- What is the data lifecycle (created, read, updated, deleted, archived)?
- What are the privacy/retention requirements?

**Category 5: Technical Constraints**
- Target platforms (web, mobile, desktop, CLI, embedded)?
- Offline capability requirements?
- Performance expectations (latency, throughput, scale)?
- Integration requirements (what existing systems must it connect to)?

**Category 6: UX and Interaction Model**
- What interaction pattern fits best (CRUD app, conversational, dashboard, real-time, wizard)?
- What design language aligns with the audience?
- What accessibility requirements exist?
- How does error handling surface to users?
- Does the project need responsive/adaptive layouts, PWA support, or offline-first UX?
- Are there internationalization (i18n) or localization requirements?

**Category 7: Business and Distribution**
- Is this open source, commercial, or internal?
- What is the monetization strategy (if any)?
- What is the competitive landscape?
- What regulatory/compliance requirements exist?

**Exit condition:** When the Confidence Gate rubric scores >= 85% across all dimensions. After each category round, reassess the confidence score. When threshold is met, confirm with the user: "I have enough clarity to write the spec documents. Here's what I understand: [1-paragraph summary]. Should I proceed?"

**Done criteria per category:**
- Problem Space: Can articulate the problem to a stranger in 2 sentences
- Solution Vision: Can walk through the primary workflow step by step
- Users: Can name each persona and explain why they care
- Data: Can draw an entity-relationship sketch
- Technical: Can list hard constraints vs preferences
- UX: Can describe the first 30 seconds of user interaction and the primary navigation model
- Business: Can explain who pays (or why it is free) and how users find it

### Phase 2: Prior Art Research

**This phase is mandatory.** Conduct research before writing any spec documents.

Read `references/research-checklist.md` for the full protocol. Summary:

1. **Local workspace scan:**
   - Check for existing agent configs, skills, related projects
   - Check skillshare registries, skills.sh, agentskills.io

2. **GitHub/community search** (minimum 3 searches):
   - Direct competitors or existing solutions
   - Libraries/frameworks that solve sub-problems
   - Similar architectural patterns

3. **Web search** (minimum 2 searches):
   - State of the art in the problem domain
   - Recent developments that could affect approach
   - Community discussions about the problem space

4. **Synthesis:**
   - If existing tools fully solve the problem: surface them immediately, ask user if they still want to proceed
   - If existing tools partially solve: incorporate learnings, note what this project adds beyond them
   - Document findings in the requirements file's "Prior Art" section
   - Extract useful patterns, pitfalls to avoid, and architectural lessons

### Phase 3: Data Architecture Decision

Read `references/data-architecture-guide.md` for the full decision framework.

Based on extracted entities and relationships:

1. **Classify data relationships:**
   - Flat/simple -> key-value or document store
   - Relational with joins -> SQL (PostgreSQL, SQLite)
   - Graph-like relationships -> graph DB or relational with careful schema
   - Time-series dominant -> time-series DB or partitioned tables
   - Unstructured/search-heavy -> vector store or full-text search engine

2. **Design initial schema** (entity names, key attributes, relationships)
3. **Identify access patterns** (read-heavy, write-heavy, mixed)
4. **Determine storage strategy** (local-first, cloud, hybrid)
5. **Document in design file** with rationale for each decision

### Phase 4: Document Generation

Generate two files following the templates in `references/`:

#### requirements.md (The WHAT and WHY)
Maps to: SpecKit's `spec.md`, OpenSpec's `specs/*.md`, Cursor/Kiro spec input

This document is **technology-agnostic**. It focuses on:
- Problem statement and motivation
- User scenarios and acceptance criteria
- Functional requirements (FR-001 format, using MUST/SHALL/SHOULD)
- Non-functional requirements (NFR-001 format)
- Key entities (conceptual, no implementation details)
- Success criteria (measurable metrics)
- Assumptions and dependencies
- Prior art analysis
- Identified risks
- Scope boundaries (explicit in/out)

**Quality gates (from SpecKit):**
- No implementation details (languages, frameworks, APIs)
- Focused on user value and business needs
- Requirements are testable and unambiguous
- Maximum 3 `[NEEDS CLARIFICATION]` markers allowed
- Every functional requirement has acceptance criteria

#### design.md (The HOW)
Maps to: SpecKit's `plan.md`, OpenSpec's `design.md`, Cursor/Kiro technical plan

This document IS technology-specific. It covers:
- Architecture overview (with ASCII diagram)
- Technology stack selection with rationale
- Data model (schema, relationships, access patterns)
- API/interface contracts (endpoint signatures, message formats)
- Hosting and deployment strategy
- Project structure (directory layout)
- Security considerations
- Performance targets and optimization strategy
- Implementation phases (no dates, use phase/step notation)
- Testing strategy
- Migration and upgrade paths
- References

#### constitution.md
- Include the user's existing constitution.md as a reference file if available
- If no constitution exists, note this and suggest the user create one via SpecKit/OpenSpec tooling
- Do NOT generate a new constitution from scratch; this is a governance document the user must own

### Phase 5: Deliberative Refinement

After generating both documents, invoke the **deliberative-refinement** skill on each:

1. **Requirements file:** Run V(10,3,1) using Expert Council type
   - Focus areas: completeness of requirements, testability, ambiguity detection, missing edge cases, scope creep indicators
   - Verify every FR has acceptance criteria
   - Verify no implementation details leaked into requirements
   - Check for internal contradictions

2. **Design file:** Run V(10,3,1) using Structured Review type
   - Focus areas: architectural soundness, technology fit, scalability concerns, security gaps, missing error handling, deployment feasibility
   - Verify schema supports all FRs
   - Verify hosting strategy aligns with NFRs
   - Check for over-engineering

3. **Cross-document validation:**
   - Every FR in requirements has a corresponding section in design
   - Design does not introduce requirements not present in requirements.md
   - Success criteria from requirements are achievable with proposed architecture
   - Risk mitigations in design address risks identified in requirements

4. **Apply refinements** to both documents based on council findings

### Phase 6: Delivery and Handoff

1. **Present both files** to the user

2. **Provide a delivery summary:**
   - Confidence score achieved and any sub-threshold dimensions
   - Key decisions made and rationale
   - Items marked `[NEEDS CLARIFICATION]` that require user input
   - Risks that need user acknowledgment
   - Prior art findings that influenced the design

3. **Suggest next steps** based on user's toolchain:
   - SpecKit: `specify init <project>` then `/speckit.specify` with requirements.md
   - OpenSpec: `openspec init` then `/opsx:propose` with the requirements
   - Cursor/Kiro: Load requirements.md and design.md into spec workflow
   - Manual: Files are ready for direct use by coding agents

4. **Agent team handoff** (when subagents or agent teams are available):
   - The requirements.md and design.md contain all context needed for implementation
   - A new coding session can pick up from these files without this conversation's context
   - Suggest: "Start a new session, load both files, and begin with Phase 1 of the implementation plan"
   - If agent teams are supported: each implementation phase can be parallelized across agents using the design's phase boundaries as task isolation points

5. **Iterative refinement path:**
   - User can return to any phase with new information
   - Re-running Phase 5 (deliberative refinement) after user edits catches new inconsistencies
   - The documents are living artifacts; update the version header on each revision

## Compatibility Notes

### SpecKit Alignment
- requirements.md uses FR-001/NFR-001 numbering
- Mandatory vs optional sections follow SpecKit conventions
- `[NEEDS CLARIFICATION]` markers limited to 3
- No implementation details in requirements
- Checklist validation embedded in Phase 5
- **Note:** SpecKit's `/speckit.plan` generates multiple files (research.md, data-model.md, contracts/, quickstart.md). Our design.md is a single consolidated file. When feeding into SpecKit, the agent will decompose design.md into SpecKit's multi-file structure during the plan phase. No manual splitting required.

### OpenSpec Alignment
- Requirements use SHALL/MUST language
- Design follows proposal + design.md pattern
- Data entities described as capabilities
- Testable scenarios per requirement

### Kiro/Cursor Alignment
- Both files are self-contained markdown
- No external dependencies or tool-specific syntax
- Compatible with any agent that reads markdown specs

## Anti-Patterns

- **Never** skip prior art research (Phase 2)
- **Never** include technology choices in requirements.md
- **Never** generate a constitution.md from scratch
- **Never** use dates/timestamps in implementation phases
- **Never** skip deliberative refinement (Phase 5)
- **Never** write code in either document
- **Never** leave a functional requirement without acceptance criteria
- **Never** assume the user's stack without checking preferences/context
- **Never** inflate confidence scores to skip clarification rounds
- **Never** write exploration/research findings to output files (they are process context, not artifacts)
- **Never** ask all discovery questions in a single message (sequential categories, 2-4 questions each)
- **Never** proceed past the confidence gate without explicitly confirming with the user

## Resource Files

| File | Read When |
|------|-----------|
| [references/requirements-template.md](references/requirements-template.md) | Phase 4: Structuring the requirements document |
| [references/design-template.md](references/design-template.md) | Phase 4: Structuring the design document |
| [references/research-checklist.md](references/research-checklist.md) | Phase 2: Conducting prior art research |
| [references/data-architecture-guide.md](references/data-architecture-guide.md) | Phase 3: Making data architecture decisions |


> **BEFORE USING THIS SKILL:** Read all reference files in `references/` before starting. They contain output templates, research checklists, and data architecture guidance required for proper execution.
>
> **Claude.ai / no-filesystem fallback:** If reference files are not accessible (e.g., running in claude.ai web chat without code execution), the templates and guidance are embedded in this SKILL.md's section headers and Phase 4 descriptions at sufficient detail to produce correct output. Reference files add depth but are not blocking.

