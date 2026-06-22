---
name: multi-transcript-synthesis
description: |
  Collate and synthesize multiple AI conversation transcripts, specs, and notes into clean requirements and design documents. Use when: the user has multiple files from different AI sessions about the same project idea, needs to "audit these files", "clean up these transcripts", "figure out what I actually need", "collate ideas from multiple conversations", "find the best version", "merge these specs", "create requirements from conversations", "synthesize these docs", "extract the good ideas", "make sense of this mess", "consolidate these transcripts", "build a requirements doc from these notes", "compare these approaches", "which model was right", "merge these ideas", "what's the consensus across these", "I got different answers from different models", "prioritize these features from my notes", "make a spec from these conversations", "I talked to GPT/Claude/Gemini about this". AUTOMATIC ACTIVATION: Any request involving 3+ markdown files that appear to be AI conversation logs, project specs, or ideation documents about the same topic. NOT for: summarizing a single meeting transcript, editing one document, simple Q&A, or single-file analysis tasks. Minimum 2 source files required.
version: 0.3.0
inputs:
  - name: transcript_files
    description: AI conversation transcripts, specs, and notes to synthesize
    pointer_type: file_path
outputs:
  - name: requirements_doc
    description: Consolidated requirements and design document
    pointer_type: output_file
tags:
- writing
- planning
- ai/llm
- automation
grade: A
source: custom
---

> ⚠️ **BEFORE STARTING:** Read all files in `references/` — they contain the scratchpad template, synthesis matrix, retrospective checklist, and starter code guide required for proper execution.

# Multi-Transcript Synthesis Engine

> Turn a pile of AI conversations into actionable project documents.

A practitioner has an idea. They discuss it with one agent. Then they hand the transcript to 2–5 other agents for independent opinions. Now they have 3–6 files of mixed quality containing overlapping, contradictory, and complementary ideas. This skill extracts the signal from the noise and produces clean requirements and design documents.

## When to Activate

- User has multiple files (transcripts, specs, notes, paste dumps) about one project
- User asks to "audit", "collate", "synthesize", "consolidate", or "find the best version"
- User drops a folder and says "clean this up" or "figure out what I need"
- User mentions having talked to multiple agents about the same idea
- User says "I got different answers" or "which model was right"

## Minimum & Edge Cases

| Scenario | Action |
|----------|--------|
| **1 file** | Do NOT activate Multi-Transcript Synthesis. Use doc-coauthoring or standard analysis. |
| **2 files** | Activate with simplified synthesis matrix (2 columns). |
| **3+ files** | Full process. |
| **All files off-track** | State this to the user. Extract fragments rather than choosing a "best version." Build from fragments + research. |
| **Contradictory intent evolution** | The LATEST user intent overrides the earliest, UNLESS the user explicitly says to return to their original vision. |
| **Non-markdown files (code, JSON, YAML)** | Treat as supporting evidence, not primary sources. Don't extract "intent" from code. |
| **Mixed quality** | Common. The shortest file may be the best. Evaluate alignment with user intent, not volume. |

## Core Process: Five Phases

```
Phase 1: Inventory & Triage     ─── What do we have? What does the user already have working?
Phase 2: Intent Extraction       ─── What does the USER actually want?
Phase 3: Idea Harvest            ─── What are the best ideas across all sources?
Phase 4: Ground Truth Research   ─── What already exists? Don't reinvent.
Phase 5: Synthesis & Output      ─── Produce clean deliverables.
```

### Phase 1: Inventory & Triage

**Quick Scan (before deep reads):** Before committing to full file reads, do a fast triage:
- Compare file sizes — files within 10% size of each other are likely duplicates
- Read first and last 20 lines of each file — check for identical openings/closings
- Grep for unique structural markers (project names, section headers)
- If two files have >90% content overlap, discard the duplicate immediately and note it

This prevents wasting time deep-reading 3 versions of the same content.

Read every unique file. For each, record in the scratchpad (see [references/scratchpad-template.md](references/scratchpad-template.md)):

1. **File name and type** — transcript, spec, notes, code, paste dump
2. **Source agent** — which model/tool generated it (GPT, Claude, Gemini, etc.)
3. **Verdict** — Best version / Useful partial / Duplicate / Outdated / Off-track
4. **Unique?** — YES (unique content) / PARTIAL (some unique content) / DISCARD (duplicate)
5. **Key contributions** — 1–3 bullet points of what THIS file uniquely adds
6. **Red flags** — Where the model went off-track from user intent
7. **Existing infrastructure** — Check the user's workspace BEFORE deep-diving files. Run `ls`, `find`, `cat README.md` on the project directory. Any working system (scripts, configs, READMEs, existing tools) is a HARD CONSTRAINT on the design. This is the #1 failure mode: designing a system that replaces something the user already has working.

**Critical rules:**
- Do NOT assume the most detailed or longest document is the best. Evaluate alignment with user intent, not volume.
- Do NOT over-weight the last file you read (recency bias).
- Check the user's workspace for existing infrastructure BEFORE forming opinions about architecture.

**Check-in:** After completing Phase 1, send a brief status message: "I've read all [N] files. [1-sentence triage summary]. [Note any duplicates discarded]. Proceeding to extract your core intent."

**Detecting off-track models:** Compare each model's output against the user's ORIGINAL problem statement (usually in the first transcript). A model is off-track when it:
- Narrows scope below what the user asked for
- Introduced tangents the user didn't request
- Ignored stated constraints
- Solved a different problem than the one described

### Phase 2: Intent Extraction

The user's ACTUAL intent is often buried across multiple conversations. Extract it by:

1. **Find the origin statement** — The first time the user described what they want. This is the purest signal.
2. **Track intent evolution** — How did the user's vision change across conversations? Did they expand scope? Narrow it? Change priorities?
3. **Identify constraints** — Stated requirements that never changed across conversations (tech stack, privacy, platforms)
4. **Separate user intent from model suggestions** — Models often propose features the user never asked for. Track which ideas came from the user vs. from models.
5. **Check for the "switchboard" pattern** — Does the user already have working infrastructure? If so, the project should EXTEND it, not replace it.

**Output:** A 1-paragraph "User Intent Statement" that captures what the user actually wants, stripped of model-introduced tangents.

### Phase 3: Idea Harvest

Use the Synthesis Matrix (see [references/synthesis-matrix.md](references/synthesis-matrix.md)):

For each file, extract:
- **Unique good ideas** — concepts that appear in only this file and are genuinely valuable
- **Reinforced ideas** — concepts that appear across 2+ files (high confidence)
- **Contradictions** — where two files disagree on approach

For contradictions, evaluate which approach better serves the user's extracted intent.

**Code snippets:** Preserve valuable schemas, pseudocode, and algorithms per the [references/starter-code-guide.md](references/starter-code-guide.md). Even if the build agent rewrites everything, starter material anchors thinking and encodes implicit decisions.

**Check-in (if contradictions found):** "I found [N] contradictions between sources. Here's a quick summary: [list]. Want me to resolve these based on your latest intent, or do you have a preference?"

### Phase 4: Ground Truth Research

**Never skip this phase.** Search for existing solutions before writing requirements.

**Research Protocol (7 categories):**

1. **Workspace scan** — Reference Phase 1 findings. If you found existing infrastructure (scripts, tools, configs), this constrains the design.
2. **Competitor search** — Tools that do exactly what the user wants. Search: `"[problem domain]" CLI tool github npm 2026`
3. **Adjacent search** — Tools that solve part of the problem. What existing packages could be stitched in?
4. **Pattern search** — How is this class of problem normally solved? Industry standards, established architectures.
5. **Stack search** — Packages for the user's specific tech stack (Bun, Svelte, Hono, etc.)
6. **Integration target verification** — If the project integrates with external systems (APIs, agents, services), verify the current API surface of each target. Don't rely on what transcripts claim — check actual docs/READMEs. Flag unverified integration assumptions clearly.
7. **Code snippet verification** — For any code snippets preserved in starter-code (import paths, API calls, provider constructors), verify against actual package documentation (PyPI, npm, GitHub README). Mark unverified snippets with ⚠️.

**Output:** Gap analysis table — what exists (DON'T rebuild) vs. what needs building.

### Phase 5: Synthesis & Output

Produce these deliverables. If artifacts are available, use them. If not, write files to the project directory.

#### Required Outputs

1. **Scratchpad** — Per-file audit notes, synthesis matrix, research findings, gap analysis. Working document using the [references/scratchpad-template.md](references/scratchpad-template.md).

2. **Requirements Document** — Clean SRS. Must include these sections:
   - Problem statement (what's broken / missing)
   - What already works (existing infrastructure — DO NOT propose replacing it)
   - User stories organized by priority
   - Functional requirements (split: already-satisfied vs. needs-building)
   - Non-functional requirements
   - Hardware/resource constraints (if applicable — VRAM budgets, CPU targets, memory limits)
   - Constraints, risks, success criteria

3. **Design Document** — Technical SDD. Must include these sections:
   - Architecture (extends existing systems, doesn't replace them)
   - Component design with interfaces
   - Data models (TypeScript types or equivalent)
   - Integration points with existing infrastructure
   - Implementation phases
   - Technology stack with rationale

#### Optional Outputs

4. **Starter Code Reference** — Preserved code snippets per [references/starter-code-guide.md](references/starter-code-guide.md).

5. **Open Questions** — 5–10 questions for the user. Ask AFTER presenting deliverables — users give better answers with context.

## Anti-Patterns

- ❌ **Premature questions** — Don't ask the user 10 questions before reading the files. Read everything first, form a thesis, THEN ask.
- ❌ **Longest = best** — The most detailed doc is often the most off-track. Evaluate alignment with intent.
- ❌ **Model loyalty / authority bias** — Don't favor ideas because they came from a "better" model. GPT-4's bad idea is still bad.
- ❌ **Recency bias** — Don't over-weight the last file you read. The first file often has the purest user intent.
- ❌ **Confirmation bias** — Don't look for evidence supporting your emerging thesis. Actively seek contradictions.
- ❌ **Tabula rasa design** — Don't propose building from scratch when the user has working infrastructure.
- ❌ **Feature creep absorption** — Don't include every feature every model suggested. Separate user-requested from model-suggested.
- ❌ **Skipping research** — Always search for existing tools. The user wants to "stitch existing tools, not rebuild."
- ❌ **Ignoring code snippets** — Pseudocode and schemas from transcripts have value as starter material.
- ❌ **Dismissing narrow docs** — Even a narrow or seemingly off-track document may contain core features the user values.

## Cross-Skill Integration

- After producing deliverables, if the user wants to refine them interactively, hand off to the **doc-coauthoring** skill for iterative section-by-section polish.
- For high-stakes decisions within the synthesis (contested ideas, architecture choices), invoke the **deliberative-refinement** skill for structured evaluation.

## Iteration Protocol

After completing a synthesis cycle, perform a retrospective (see [references/retrospective.md](references/retrospective.md)):

1. What went well? What was missed?
2. Score each phase 1–5
3. Identify specific SKILL.md changes to make
4. Apply changes before the next cycle

This skill improves through use. Each retrospective should produce concrete edits.

## Resources

- [references/scratchpad-template.md](references/scratchpad-template.md) — Structured working document template
- [references/synthesis-matrix.md](references/synthesis-matrix.md) — Cross-file idea comparison methodology
- [references/retrospective.md](references/retrospective.md) — Post-cycle improvement checklist with scoring
- [references/starter-code-guide.md](references/starter-code-guide.md) — Guidelines for preserving useful code from transcripts
## 📎 Resources

📎 `~/code/agents/skills/multi-transcript-synthesis/references/retrospective.md`
📎 `~/code/agents/skills/multi-transcript-synthesis/references/scratchpad-template.md`
📎 `~/code/agents/skills/multi-transcript-synthesis/references/starter-code-guide.md`
📎 `~/code/agents/skills/multi-transcript-synthesis/references/synthesis-matrix.md`

---
name: multi-transcript-synthesis
description: "Collate and synthesize multiple AI conversation transcripts, specs, and notes into clean requirements and design documents. Use when: auditing files, cleaning up transcripts, figuring out what to build, collating ideas from multiple conversations."
  Collate and synthesize multiple AI conversation transcripts, specs, and notes into clean requirements and design documents. Use when: the user has multiple files from different AI sessions about the same project idea, needs to "audit these files", "clean up these transcripts", "figure out what I actually need", "collate ideas from multiple conversations", "find the best version", "merge these specs", "create requirements from conversations", "synthesize these docs", "extract the good ideas", "make sense of this mess", "consolidate these transcripts", "build a requirements doc from these notes", "compare these approaches", "which model was right", "merge these ideas", "what's the consensus across these", "I got different answers from different models", "prioritize these features from my notes", "make a spec from these conversations", "I talked to GPT/Claude/Gemini about this". AUTOMATIC ACTIVATION: Any request involving 3+ markdown files that appear to be AI conversation logs, project specs, or ideation documents about the same topic. NOT for: summarizing a single meeting transcript, editing one document, simple Q&A, or single-file analysis tasks. Minimum 2 source files required.
version: 0.3.0
inputs:
  - name: transcript_files
    description: AI conversation transcripts, specs, and notes to synthesize
    pointer_type: file_path
outputs:
  - name: requirements_doc
    description: Consolidated requirements and design document
    pointer_type: output_file
---

> ⚠️ **BEFORE STARTING:** Read all files in `references/` — they contain the scratchpad template, synthesis matrix, retrospective checklist, and starter code guide required for proper execution.

