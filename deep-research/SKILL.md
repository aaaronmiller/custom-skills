---
name: deep-research
description: 'Multi-source investigation, synthesis, comprehensive topic exploration.
  Use for research requiring 3+ sources, competitive intel, market analysis, due diligence,
  or any structured investigation with >6 expected searches. Provides parameterized scope
  control via R(W,D,S,V,F) — Width, Depth, Saturation, Verification, Fidelity — with four
  preset profiles (Survey, Standard, Thorough, Exhaustive) plus working-state management
  (scratchpad, pointer notes, memory rotation) for long sessions.
  Do NOT use for simple factual lookups, single-source summaries, or creative writing.
  '
license: MIT
metadata:
  author: ice-ninja
  version: 4.0.0
tags:
- research
- academic
- ai/llm
grade: A
source: custom-skills
---

# Deep Research

> Parameterized multi-source investigation with quantified scope, recursive discovery,
> iterative refinement, and durable working state across long sessions.

Unified from deep-research v1.2.0 (parameter model) + v3.0 (working-state mechanics).

## Core Concept

Deep Research transforms a user query into a structured, multi-phase investigation
controlled by five tunable parameters. The agent decomposes the query, searches
iteratively, validates findings across sources, and synthesizes a grounded report —
while keeping its working state on disk so context exhaustion never loses findings.
The user can refine scope at any point.

## The Five Parameters

Research scope is governed by the vector `R(W, D, S, V, F)`:

| Param | Name | Controls | Range | Default |
|-------|------|----------|-------|---------|
| **W** | **Width** | Sub-questions in initial decomposition | 2-20 | 6 |
| **D** | **Depth** | Recursive search layers from follow-up discoveries | 1-5 | 2 |
| **S** | **Saturation** | Sources examined per branch before moving on | 2-15 | 4 |
| **V** | **Verification** | Cross-reference validators per claim | 0-3 | 1 |
| **F** | **Fidelity** | Synthesis refinement passes on final report | 1-3 | 1 |

**Expected search operations ≈ W × D × S.** Hard caps: if a user requests values
beyond the stated ranges, warn that values will be capped and explain why.

### Temporal Focus Modifier

Optional `@T` controls temporal filtering without adding a sixth parameter:
`@T=0` (default, none) · `@T=6mo` · `@T=24mo` · `@T=-10y` (historical).
Usage: `R(6,2,4,1,1) @T=12mo`.

### Parameter Descriptions

- **Width (W)**: how many angles the query splits into. "AI safety" at W=3 might
  decompose into [technical alignment, governance, societal impact].
- **Depth (D)**: when searching angle X reveals concept Y absent from the original
  decomposition, D controls whether Y gets its own branch. D=1 is flat; D=3 means
  three layers of "I found something new, let me chase it." A **novel concept** is a
  named entity, term, methodology, or causal relationship appearing in findings but
  not in the original query or existing sub-questions.
- **Saturation (S)**: sources examined per branch per depth layer before moving on.
- **Verification (V)**: cross-checking aggressiveness. V=0 trusts sources; V=1
  spot-checks ~30% of claims against one independent source; V=3 triangulates all
  substantive claims across three independent sources.
- **Fidelity (F)**: refinement passes on the final synthesis. F=1 single draft;
  F=2 adds coherence review; F=3 adds citation validation and gap analysis.

## Preset Profiles

| Profile | R(W,D,S,V,F) | Use Case | Est. Searches |
|---------|--------------|----------|---------------|
| **Survey** | R(3,1,2,0,1) | Quick orientation, scoping | ~6 |
| **Standard** | R(6,2,4,1,1) | Solid research, most questions | ~48 |
| **Thorough** | R(10,3,6,2,2) | Competitive analysis, lit reviews | ~180 |
| **Exhaustive** | R(15,4,10,3,3) | Due diligence, critical decisions | ~600 |
| **Custom** | User-specified | Full control | Computed |

## Execution Protocol

### Phase 0: Parameter Resolution

Resolve via three paths (priority order):
1. **Explicit**: user states values ("research X at W=8, D=3")
2. **Profile**: user names a profile ("do a thorough research on X")
3. **Inferred**: assess query complexity. Simple/bounded → Survey; multi-faceted →
   Standard; contested topic or professional stakes → Thorough; high-stakes
   legal/financial/safety decisions → Exhaustive.

After resolving, declare parameters in both forms:

```
Research Parameters: R(W=6, D=2, S=4, V=1, F=1) [Standard]
Translation: 6 angles, 2 layers deep, 4 sources per angle,
basic fact-checking, single synthesis pass.
Estimated scope: ~48 search operations across 6 angles
```

### Phase 0.5: Working State Setup (from v3)

Before searching, create a scratchpad directory:

```
<tmp>/deep-research-<slug>/      # /tmp or project ./research-<slug>/
  scratchpad.md     # pointer notes: concept → source:lines → 1-line note
  findings.md       # compressed extracts, one block per branch
  report.md         # the deliverable, written incrementally
```

Rules (map-reduce for the context window):
- A **pointer note** is `concept — file/URL:locator — one line`. Never paste raw
  source text; store the pointer and read back on demand.
- After each branch, compress its findings into `findings.md` (key claims +
  sources). Never accumulate raw search results in context.
- **Memory rotation**: if the scratchpad exceeds ~500 lines / 10KB, consolidate:
  merge redundant notes, promote stable findings to `findings.md`, drop dead ends
  into a one-line "rejected" list. This keeps a Thorough+ run bounded.
- On interruption or compaction, the scratchpad is the resume point: read it,
  find the first incomplete branch, continue.

### Phase 1: Query Decomposition (Width)

Split the query into W sub-questions. Each must be independently searchable,
non-overlapping where possible, ordered by expected information density (richest
first). Present the decomposition for approval before proceeding. **Non-blocking
fallback**: in headless/batch contexts, proceed and note auto-approval in the report.

### Phase 2: Iterative Search (Depth × Saturation)

```
for sub_question in decomposition:              # W iterations
    known_concepts = set()
    for depth_layer in range(D):                # D layers
        results = search(sub_question, layer)
        for source in results[:S]:              # S sources/layer
            extract = analyze(source)
            append_pointer_note(extract)        # scratchpad, not context
            new_concepts = detect_novel(extract, known_concepts)
            if new_concepts and depth_layer < D-1:
                queue_for_next_layer(new_concepts)
        known_concepts.update(extracted_concepts)
    compress_branch_to_findings()               # before next branch
```

**Search query construction**: sub-questions are not search queries. Transform each
into 1-3 short specific queries (1-6 words), broad first, narrowing on results.

**Under-saturation**: if fewer than S sources are found, note the gap in the report
rather than silently accepting incomplete coverage; try alternate formulations first.

**Progress reporting**: after each sub-question, give a findings summary and
remaining scope. Accommodate steering immediately.

### Phase 3: Verification (V passes)

- V=1: spot-check ~30% of claims against one independent source each
- V=2: verify ~60% of claims against two independent sources
- V=3: triangulate all substantive claims across three independent sources

Flag contradictions, disputed claims, and uncorroborated assertions in the report.

### Phase 4: Synthesis (F passes)

**Pass 1 (always)**: compile into a structured report (template below), inline
citations throughout.
**Pass 2 (F≥2)**: review for coherence — logical gaps, redundancy, unsupported
conclusions, missing counter-arguments. Revise.
**Pass 3 (F≥3)**: validate citations, run gap analysis, append "Limitations and
Open Questions".

## Parameter Interaction Model

- **W × D** = conceptual surface area. High W + high D = exhaustive but expensive.
- **S as density**: diminishing returns past S=8.
- **V as insurance**: most valuable when S is low.
- **F as polish**: only matters when W×D×S produced enough raw material.

**Budget-aware scaling**: limited time → raise W over D (breadth). Single-topic
deep-dive → raise D over W.

**Cost awareness**: each web_search call costs ~$0.01 on metered APIs. Approximate
search-fee costs: Survey ~$0.06, Standard ~$0.48, Thorough ~$1.80, Exhaustive ~$6.00.
Make users aware when selecting Thorough+ profiles.

## Tool Compatibility

Tool-agnostic. Backends: `web_search`, `web_fetch` (deep-read high-value sources —
important at S≥4), MCP search servers (Tavily, Brave), internal connectors.

## Grounding Requirements

Every execution MUST include:
1. **Repository search**: GitHub/GitLab for code, tools, implementations (min 3
   searches for technical topics)
2. **Community search**: Reddit, HN, Stack Overflow for practitioner views (min 2)
3. **Primary sources**: papers, official docs, company blogs (min 3)
4. **Provenance tracking**: every finding links to its source. No unattributed claims.

## Output Format

- Research parameters and scope declaration
- Executive summary
- Findings by sub-question
- Cross-cutting themes
- Contradictions and disputed claims
- Confidence assessment per finding (High/Med/Low, tied to evidence strength)
- Source bibliography with quality annotations
- Limitations and open questions

## Anti-Patterns

- **Never** present a single-pass search as deep research (Survey is scoping, say so)
- **Never** skip decomposition, even for simple queries
- **Never** report findings without source attribution
- **Never** suppress contradictory evidence
- **Never** claim higher scope than achieved, or run a lower profile than stated
- **Both Sides Cop-out**: do not end a contested section with "both sides have
  merit" — take a stance on the weight of evidence and say why the counter is weaker
- **Wikipedia is a portal, not a destination**: use it to find primary sources only
- **Recency cap**: prefer sources <12 months old unless foundational or `@T=-10y`
- **Sample-size floor**: report `n=...`; if N<20 discard the sampled claim (does not
  apply to qualitative case studies)
- **Context hoarding**: never hold raw source text across branches — compress to the
  scratchpad or you will exhaust the window mid-run
