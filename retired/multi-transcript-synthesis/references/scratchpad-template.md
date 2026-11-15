# Scratchpad Template

Use this template when performing a Bugbear synthesis. Create it as an artifact at the start of Phase 1 and update it throughout all phases.

---

## Project: [NAME]

**Date:** [DATE]  
**Source files:** [COUNT] files  
**User intent (1 sentence):** [Filled in Phase 2]

---

## Phase 1: File Inventory

| # | File | Type | Source Agent | Verdict | Key Contributions | Red Flags |
|---|------|------|-------------|---------|-------------------|-----------|
| 1 | | | | | | |
| 2 | | | | | | |
| 3 | | | | | | |

**Verdicts:** BEST VERSION · USEFUL PARTIAL · DUPLICATE OF [#] · OUTDATED · OFF-TRACK

### Triage Summary

- **Best version(s):** [file(s)]
- **Duplicates to discard:** [files]
- **Off-track documents:** [files + why they diverged]

### Existing Infrastructure (from workspace scan)

| Component | Status | Location | Notes |
|-----------|--------|----------|-------|
| | Working / Partial / Missing | [path] | |

### Phase 1 Check-in Message
> "I've read all [N] files. [triage summary]. [duplicates discarded]. Proceeding to extract your core intent."

---

## Phase 2: Intent Extraction

### Origin Statement
> [Paste or paraphrase the user's earliest, purest description of what they want]

### Intent Evolution
1. [Conversation 1] → [What user wanted here]
2. [Conversation 2] → [How intent shifted]
3. [Conversation 3] → [Further evolution]

### Immutable Constraints
- [Tech stack, platform, privacy requirements that never changed]

### User Intent Statement
> [1-paragraph synthesis of what the user actually wants]

---

## Phase 3: Idea Harvest

### Synthesis Matrix

[See synthesis-matrix.md for the full matrix format]

**Quick summary of harvested ideas:**

| Category | Idea | Source File(s) | Confidence | Include? |
|----------|------|---------------|------------|----------|
| | | | Reinforced / Unique / Contested | ✅/❌/❓ |

### Contradictions

| Topic | Position A (File X) | Position B (File Y) | Resolution |
|-------|--------------------|---------------------|------------|
| | | | |

### Preserved Code Snippets

List any schemas, pseudocode, algorithms, or data models worth saving:

- **[Description]** from [File] — [Why it's useful]

---

## Phase 4: Ground Truth Research

### Existing Tools Found

| Tool | What it solves | What it misses | Reuse potential |
|------|---------------|----------------|-----------------|
| | | | |

### User's Existing Infrastructure

| Component | Status | Location | Notes |
|-----------|--------|----------|-------|
| | Working / Partial / Missing | | |

### Gap Analysis

**Already solved (DON'T rebuild):**
- [Component] — by [existing tool/infrastructure]

**Partially solved (EXTEND):**
- [Component] — [what exists] + [what's missing]

**Not solved (BUILD):**
- [Component] — [nothing exists, must create]

---

## Phase 5: Deliverable Tracking

- [ ] Scratchpad (this document)
- [ ] Requirements document
- [ ] Design document
- [ ] Starter code reference (if applicable)
- [ ] Open questions for user
- [ ] Retrospective

---

## Retrospective

[Filled in after deliverables are complete — see retrospective.md]
