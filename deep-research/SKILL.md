---
name: deep-research
description: 'AUTOMATIC ACTIVATION: Use this skill whenever the user requests "deep
  research", "comprehensive analysis", "investigation", "due diligence", "technical
  audit", "prior art search", "state of the art", "landscape analysis", "competitor
  breakdown", "find everything about". Also triggers on: "research this thoroughly",
  "I need to understand", "what''s the truth about", "verify this claim", "is this
  legit".

  '
tags:
  - research
  - ai/llm
grade: A
source: community
license: MIT
metadata:
  author: ice-ninja
  version: '3.0'
tags:
- research
- academic
- ai/llm
grade: A
source: community
---

> ⚠️ **BEFORE USING THIS SKILL:** Review all files in `resources/`. These contain the 100-Dork query database, source forensics catalog, cognitive models, and synthesis protocols required for execution.

## Research Basis

This skill is powered by a comprehensive resource library (~50KB of tradecraft):
- **Query Engineering**: `advanced-query-logic.md` (100+ search operators, industry kill-chains)
- **Source Forensics**: `source-forensics.md` (SEO detection, AI-tell blacklist, trust tiers)
- **Cognitive Models**: `cognitive-models.md` (50 mental models, dialectical synthesis)
- **Research Protocols**: `research-protocols.md` (GitHub audit SOPs, Red Team checklists)
- **Statistics**: `stats-database.md` (SEO spam rates, information half-life data)
- **Output Templates**: `report-archetypes.md` (Executive Brief, Engineering Deep Dive formats)

Full statistics in `resources/stats-database.md`.

# Deep Research Skill

Turn the agent into a Senior Intelligence Analyst. This skill moves beyond "searching" to "investigating" — piercing SEO spam, triangulating claims, and synthesizing nuanced conclusions.

## Core Principle: The Dialectical Research Loop

Truth is not found; it is synthesized. You do not just "gather facts". You attack them.

1. **Thesis**: Find the mainstream claim (The Map).
2. **Antithesis**: Find the failure mode / contradictory evidence (The Territory).
3. **Synthesis**: Merit the two into a nuanced conclusion.
4. **Repeat** until the conclusion is unbreakable.

## Complexity Levels (The Algorithm)

The skill operates on a strict mathematical model of **Decomposition (X)**, **Breadth (Y)**, and **Depth (Z)**.

| Level | Name | X: Search Items | Y: Multiweb Searches | Z: Targeted Retrievals | Grounding (GitHub/Social) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | **Quick Probe** | 3 Items | 1 Search | 0 Retrievals | Optional |
| **2** | **Standard** (Default) | 6 Items | 3 Searches | 2 Retrievals | Min 10 Sources |
| **3** | **Deep Dive** | 12 Items | 6 Searches | 4 Retrievals | Min 20 Sources |
| **4** | **Omniscient** | 20+ Items | 10+ Searches | 8+ Retrievals | Max Coverage |

---

## Workflow

### Phase 1: Assessment & Decomposition

**Goal**: Define *what* to investigate and *how*.

1.  **Context Assessment**: Immediately assess any provided source files (e.g., active documents, PDFs).
2.  **Decomposition**: Break the user's request into **X** distinct, atomic search items based on the complexity level.

**Pattern: The Decomposition Template**
```
Topic: [User's Request]
├── Facet 1: [Core Definition / What is it?]
├── Facet 2: [Technical Mechanics / How does it work?]
├── Facet 3: [Comparison / How does it compare to alternatives?]
├── Facet 4: [Failure Modes / What are the known problems?]
├── Facet 5: [Adoption / Who is using it in production?]
└── Facet 6: [Future / What is the roadmap?]
```

3.  **Plan Generation**: Create a `research_plan.md` in a temp directory outlining the X items and the intended search strategies (referencing specific operators).
4.  **Plan Critique (Self-Correction)**: Pause and ask: *"Does this plan cover all angles? Are there blind spots?"*
    *   *Action*: If gaps are found, add 1-2 "Wildcard" search items to the plan to ensure robust coverage.

---

### Phase 2: Breadth (Multiweb Search)

**Consult**: `resources/advanced-query-logic.md` for query construction.
**Use Case**: Building "Impossible Strings" that pierce SEO spam.

1.  **Tool Selection**: Consult `resources/search-operators.md` AND `resources/advanced-query-logic.md`.
    *   Construct specific queries using "Dorks" (`site:`, `filetype:`) and Technical Modifiers.
    *   Use the "Kill Chains" (Crypto, SaaS, BioTech) for industry-specific pivots.
    *   **Rule**: Do NOT use generic natural language queries. Use the operators.

**Pattern: The Query Template**
```
[Core Term] "[Technical Modifier]" filetype:pdf -site:medium.com -site:linkedin.com
```
Example: `mamba architecture "latency benchmarks" filetype:pdf -site:medium.com`

2.  **Execution**: Perform **Y** multi-query web searches (`search_web`).
    *   *Rule*: Each "Multiweb Search" should target a cluster of the X items.
3.  **Grounding (Mandatory)**:
    *   **GitHub**: Specifically search GitHub for code, repositories, and prior art.
        *   *Target*: Find at least **10 sources** (Level 2). If successful, expand to 20 or 30 (Level 3/4).
    *   **Social**: Search Reddit, X (Twitter), and Hacker News for specific discussions, "prior art," and community sentiment.
    *   *Adaptive Note*: If the topic is strictly non-technical (e.g., History), shift the "GitHub" mandate to "Primary/Academic Sources" (e.g., Google Scholar, JSTOR).
4.  **Logging**: Append all findings to `scratch_findings.md`. 
    *   **MANDATORY**: Score every source using `resources/source-forensics.md` (Trust Tiers, AI-Tell Blacklist).
    *   Tag: `[Bias: Neutral/Commercial/Political]` and `[Credibility: High/Med/Low]`.
    *   *Rule*: If a source matches the "SEO Visual Catalog" patterns, DISCARD IT.
5.  **Null Result Gate**: If the Y searches yield *zero* high-quality results:
    *   **STOP**. Do not proceed to Phase 3.
    *   Refine the **X** search items or the Complexity Level and restart Phase 2.

---

### Phase 3: Depth (Targeted Retrieval)

**Consult**: `resources/research-protocols.md` for SOPs.
**Use Case**: Executing structured audits (GitHub Repo Audit, SaaS Due Diligence).

1.  **Selection**: Identify the top **Z** most promising, high-density sources from Phase 2.
2.  **Retrieval**: Use `read_url_content` (or `browser_snapshot` if highly visual/dynamic) to ingest the **full content** of these Z sources.
3.  **Credibility Check**: Apply the `source-forensics.md` "Triangulation Mandate". Verify extraordinary claims with a second source.

**Pattern: The Triangulation Check**
```
Claim: "[Source A says X is 100x faster]"
├── Verify: Search for independent benchmark confirming this.
├── If Found: Claim is VERIFIED.
└── If Not Found: Mark as "Unverified claim by [Source A]".
```

4.  **Analysis**: Deeply analyze this content for specific details, implementation logic, or data points that were missing in the summaries.
    *   *Visual Trigger*: If the content implies data-rich visuals (Charts, Diagrams, Schematics) unavailable in text, use `browser_snapshot` to capture them.
5.  **Logging**: Detailed notes to `scratch_findings.md` (include credibility flags).

---

### Phase 4: Unification & Reporting

**Consult**: `resources/cognitive-models.md` for synthesis logic.
**Consult**: `resources/report-archetypes.md` for output templates.

1.  **Synthesize**: Read `scratch_findings.md` and all assessed local sources.
    *   **Rule**: Use `resources/synthesis-protocols.md` AND `resources/cognitive-models.md`.
    *   Apply **Dialectical Synthesis** (Thesis + Antithesis -> Synthesis). Do not just list facts.
    *   Apply the "No Orphan Facts" rule (Fact + Context + Constraint).
2.  **Unify**: Merge conflicting data using the "Conflict of Laws" protocol (Recency > Legacy, Code > Docs).
3.  **Output**: Generate the final artifact (e.g., `Deep_Research_Report.md`).
    *   **Select Archetype** from `resources/report-archetypes.md`:
        *   *Executive Brief*: BLUF + Decision Matrix.
        *   *Engineering Deep Dive*: RFC style with code.
        *   *Red Team Assessment*: Vulnerability focus.
    *   *Schema Inheritance*: If the user provided a reference file (like `Project Keychain`) or a specific template, **ADOPT THAT SCHEMA EXACTLY**.
    *   *Output Adapters (Optional)*: If requested, generate secondary artifacts:
        *   `social_thread.md`: A 5-10 tweet thread summarizing the findings for X/Twitter.
        *   `executive_brief.txt`: A 1-page high-level summary for leadership.
    *   Otherwise, follow this structure:
    *   **Executive Summary**: High-level findings.
    *   **Deconstructed Analysis**: Detailed breakdown of the X items.
    *   **Prior Art/Grounding**: Specific section on GitHub/Social findings.
    *   **Source Assessment**: Review of the Z deep-dived sources.
    *   **Conclusion/Roadmap**: Actionable next steps.

---

### Phase 5: Recursive Validation

1.  **Validation**: Present the summary to the user.
2.  **Loop**: Ask: *"Is this depth acceptable, or should I refine?"*
    *   **If Refine**: Increase complexity level (e.g., Level 2 -> Level 3), KEEP the temp files/scratchpad, and run the process again focusing on gaps.
    *   **If Accept**: Finalize documents and offer to clean up temp files.

---

## Anti-Patterns (The "Lazy AI" Bans)

**Kill these on sight:**

### ❌ The "First Page" Syndrome
- **Behavior**: Only browsing the first 3 Google results.
- ✅ **Fix**: You MUST dig. Use the `advanced-query-logic.md` to find pages that aren't SEO optimized. Page 2-3 often holds the real engineering data.

### ❌ The "Wikipedia Summarizer"
- **Behavior**: Reading a Wikipedia intro or a generic definition and calling it "research".
- ✅ **Fix**: Wikipedia is a *portal*, not a *destination*. Use the bottom references to find the *primary source* and read THAT.

### ❌ The "Both Sides" Cop-out
- **Behavior**: "Some say X, others say Y, it depends." (The coward's answer).
- ✅ **Fix**: **Take a stance based on weight of evidence.** "While some claim Y, the technical evidence heavily favors X because of [Specific Reason]."

### ❌ Hallucinated Citations
- **Behavior**: "According to a 2024 study..." (that doesn't exist).
- ✅ **Fix**: If you didn't `read_url_content` it, it doesn't exist. Link to the specific URL in the scratchpad.

### ❌ "SEO Voice" Contamination
- **Behavior**: Using phrases like "In understanding the landscape of..." or "Unlock the power of...".
- ✅ **Fix**: Use the `source-forensics.md` rubric. If you sound like a marketing blog, you failed. Be dry, be dense, be accurate.

### ❌ Context Amnesia
- **Behavior**: Forgetting the user's constraints (e.g., "Cost is a major factor") half-way through.
- ✅ **Fix**: Re-read the `research_plan.md` constraints before *every* synthesis step.

### ❌ The "Data Dump"
- **Behavior**: Pasting 50 bullet points of unconnected facts.
- ✅ **Fix**: Use `synthesis-protocols.md`. Group facts into themes. Build a narrative.

---

## Context-Specific Guidance

### Technical/Engineering Research
Target: Primary sources (RFCs, Post-Mortems, GitHub Issues), Code over Docs.

Focus:
- Search GitHub Issues for the *actual* bugs, not the marketing claims.
- Find the `CHANGELOG.md` — it tells the truth.
- Prioritize sources with code snippets over prose descriptions.

### Market/Business Research
Target: Regulatory filings (10-K), Investor decks, Job postings (hiring proxy).

Focus:
- Use the "Pricing Leak" and "Hiring Proxy" chains from `advanced-query-logic.md`.
- Cross-reference marketing claims with Glassdoor/Blind reviews.
- Prioritize sources with numbers (revenue, headcount) over adjectives ("fast-growing").

### Academic/Scientific Research
Target: Peer-reviewed papers (arXiv, PubMed), Replication studies, Meta-analyses.

Focus:
- Check the `n=` (sample size). If N < 20, discard.
- Find the "Conflict of Interest" disclosures.
- Prefer Meta-Analyses over individual studies.

---

## Example Transformation

### Bad Research (Lazy)

> "Mamba is a new architecture that is faster than Transformers. It uses SSMs. Some users say it is good."
>
> *Critique*: Vague, no numbers, no failure modes, "Some users" is weasel language.

### Good Research (Deep)

> **Thesis**: Mamba achieves **3-4x higher inference throughput** than Transformers due to linear scaling (Source A: Gu et al., 2024).
>
> **Antithesis**: However, it fails on **"Needle in a Haystack" retrieval** for contexts >128k, where Attention remains superior (Source B: GitHub Issue #402, retrieved 2024-12-20).
>
> **Synthesis**: It is production-ready for **streaming/chat workloads**, but widely considered unsafe for **RAG pipelines** requiring high-precision recall (Source C: Hacker News discussion, 150+ upvotes).
>
> **Confidence**: High (3 independent sources, 2 primary, 1 community).

---

## Quantitative Thresholds

Numbers to hit:

- **Source Diversity**: Minimum 3 independent sources per major claim (Triangulation).
- **Recency**: For AI/Tech, discard any source >12 months old unless it's a foundational paper.
- **SEO Filter**: Discard any source matching >2 patterns from the "SEO Visual Catalog".
- **Credibility Score**: Target average score of 7+ across all cited sources.
- **Confidence Marking**: Every claim must have a confidence tag (High/Med/Low).

---

## When NOT to Use Deep Research

Not everything needs a 20-source deep dive:

- **Simple Fact Checks**: "What is the capital of France?" — Just answer.
- **Code Syntax Questions**: "How do I use `map` in Python?" — Just show the code.
- **User Preference Questions**: "Should I use React or Vue?" — Ask clarifying questions, don't research.
- **Time-Sensitive Requests**: "Fix this bug NOW" — Act, don't research.

For these, skip the formal phases. Just answer directly.

---

## Humanization Integration

When the research is complete, you may need to polish the prose.
**Call `humanize-writing`** on the *Synthesis* sections to ensure the voice is "Professional but not Corporate".
*   *Constraint*: Do NOT humanize the data tables or citations. Keep them raw.

---

## Guidelines

- **Temp Directories**: Use a dedicated subdirectory (e.g., `deep-research/temp/SESSION_ID`) to store all scratch files. **NEVER** delete this directory during the research loop, only after explicit user confirmation.
- **Memory Rotation**: If `scratch_findings.md` exceeds 500 lines or 10KB, rename it to `scratch_findings_archive_N.md` and start a clean `scratch_findings.md` with a summary of the archive. This ensures infinite context scaling.
- **Scratch Files**: Maintain a running log. Do not rely on context window alone.
- **Tools**:
    - Use `search_web` for Breadth.
    - Use `read_url_content` for Depth.
    - Use `find_by_name` / `grep_search` to check local project context for "Grounding" as well.

---

## Reference Files

- `resources/advanced-query-logic.md`: 100+ search operators, industry kill-chains
- `resources/source-forensics.md`: SEO detection, AI-tell blacklist, trust tiers
- `resources/cognitive-models.md`: 50 mental models, dialectical synthesis
- `resources/research-protocols.md`: GitHub audit SOPs, Red Team checklists
- `resources/stats-database.md`: SEO spam rates, information half-life data
- `resources/report-archetypes.md`: Executive Brief, Engineering Deep Dive formats
- `resources/research-anti-patterns.md`: The "Lazy AI" ban list
- `resources/search-operators.md`: Basic Google Dork toolkit
- `resources/source-evaluation.md`: Legacy credibility rubric
- `resources/synthesis-protocols.md`: Dialectical synthesis logic
- `resources/templates/scratchpad_template.md`: Scratchpad format

---

**System Version**: 3.0 (FORGE Refined)
**Updated**: December 2025
**Author**: ice-ninja


> ⚠️ **BEFORE USING THIS SKILL:** Review all files in `resources/`. These contain the 100-Dork query database, source forensics catalog, cognitive models, and synthesis protocols required for execution.

## Research Basis

This skill is powered by a comprehensive resource library (~50KB of tradecraft):
- **Query Engineering**: `advanced-query-logic.md` (100+ search operators, industry kill-chains)
- **Source Forensics**: `source-forensics.md` (SEO detection, AI-tell blacklist, trust tiers)
- **Cognitive Models**: `cognitive-models.md` (50 mental models, dialectical synthesis)
- **Research Protocols**: `research-protocols.md` (GitHub audit SOPs, Red Team checklists)
- **Statistics**: `stats-database.md` (SEO spam rates, information half-life data)
- **Output Templates**: `report-archetypes.md` (Executive Brief, Engineering Deep Dive formats)

Full statistics in `resources/stats-database.md`.

# Deep Research Skill

Turn the agent into a Senior Intelligence Analyst. This skill moves beyond "searching" to "investigating" — piercing SEO spam, triangulating claims, and synthesizing nuanced conclusions.

## Core Principle: The Dialectical Research Loop

Truth is not found; it is synthesized. You do not just "gather facts". You attack them.

1. **Thesis**: Find the mainstream claim (The Map).
2. **Antithesis**: Find the failure mode / contradictory evidence (The Territory).
3. **Synthesis**: Merit the two into a nuanced conclusion.
4. **Repeat** until the conclusion is unbreakable.

## Complexity Levels (The Algorithm)

The skill operates on a strict mathematical model of **Decomposition (X)**, **Breadth (Y)**, and **Depth (Z)**.

| Level | Name | X: Search Items | Y: Multiweb Searches | Z: Targeted Retrievals | Grounding (GitHub/Social) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | **Quick Probe** | 3 Items | 1 Search | 0 Retrievals | Optional |
| **2** | **Standard** (Default) | 6 Items | 3 Searches | 2 Retrievals | Min 10 Sources |
| **3** | **Deep Dive** | 12 Items | 6 Searches | 4 Retrievals | Min 20 Sources |
| **4** | **Omniscient** | 20+ Items | 10+ Searches | 8+ Retrievals | Max Coverage |

---

## Workflow

### Phase 1: Assessment & Decomposition

**Goal**: Define *what* to investigate and *how*.

1.  **Context Assessment**: Immediately assess any provided source files (e.g., active documents, PDFs).
2.  **Decomposition**: Break the user's request into **X** distinct, atomic search items based on the complexity level.

**Pattern: The Decomposition Template**
```
Topic: [User's Request]
├── Facet 1: [Core Definition / What is it?]
├── Facet 2: [Technical Mechanics / How does it work?]
├── Facet 3: [Comparison / How does it compare to alternatives?]
├── Facet 4: [Failure Modes / What are the known problems?]
├── Facet 5: [Adoption / Who is using it in production?]
└── Facet 6: [Future / What is the roadmap?]
```

3.  **Plan Generation**: Create a `research_plan.md` in a temp directory outlining the X items and the intended search strategies (referencing specific operators).
4.  **Plan Critique (Self-Correction)**: Pause and ask: *"Does this plan cover all angles? Are there blind spots?"*
    *   *Action*: If gaps are found, add 1-2 "Wildcard" search items to the plan to ensure robust coverage.

---

### Phase 2: Breadth (Multiweb Search)

**Consult**: `resources/advanced-query-logic.md` for query construction.
**Use Case**: Building "Impossible Strings" that pierce SEO spam.

1.  **Tool Selection**: Consult `resources/search-operators.md` AND `resources/advanced-query-logic.md`.
    *   Construct specific queries using "Dorks" (`site:`, `filetype:`) and Technical Modifiers.
    *   Use the "Kill Chains" (Crypto, SaaS, BioTech) for industry-specific pivots.
    *   **Rule**: Do NOT use generic natural language queries. Use the operators.

**Pattern: The Query Template**
```
[Core Term] "[Technical Modifier]" filetype:pdf -site:medium.com -site:linkedin.com
```
Example: `mamba architecture "latency benchmarks" filetype:pdf -site:medium.com`

2.  **Execution**: Perform **Y** multi-query web searches (`search_web`).
    *   *Rule*: Each "Multiweb Search" should target a cluster of the X items.
3.  **Grounding (Mandatory)**:
    *   **GitHub**: Specifically search GitHub for code, repositories, and prior art.
        *   *Target*: Find at least **10 sources** (Level 2). If successful, expand to 20 or 30 (Level 3/4).
    *   **Social**: Search Reddit, X (Twitter), and Hacker News for specific discussions, "prior art," and community sentiment.
    *   *Adaptive Note*: If the topic is strictly non-technical (e.g., History), shift the "GitHub" mandate to "Primary/Academic Sources" (e.g., Google Scholar, JSTOR).
4.  **Logging**: Append all findings to `scratch_findings.md`. 
    *   **MANDATORY**: Score every source using `resources/source-forensics.md` (Trust Tiers, AI-Tell Blacklist).
    *   Tag: `[Bias: Neutral/Commercial/Political]` and `[Credibility: High/Med/Low]`.
    *   *Rule*: If a source matches the "SEO Visual Catalog" patterns, DISCARD IT.
5.  **Null Result Gate**: If the Y searches yield *zero* high-quality results:
    *   **STOP**. Do not proceed to Phase 3.
    *   Refine the **X** search items or the Complexity Level and restart Phase 2.

---

### Phase 3: Depth (Targeted Retrieval)

**Consult**: `resources/research-protocols.md` for SOPs.
**Use Case**: Executing structured audits (GitHub Repo Audit, SaaS Due Diligence).

1.  **Selection**: Identify the top **Z** most promising, high-density sources from Phase 2.
2.  **Retrieval**: Use `read_url_content` (or `browser_snapshot` if highly visual/dynamic) to ingest the **full content** of these Z sources.
3.  **Credibility Check**: Apply the `source-forensics.md` "Triangulation Mandate". Verify extraordinary claims with a second source.

**Pattern: The Triangulation Check**
```
Claim: "[Source A says X is 100x faster]"
├── Verify: Search for independent benchmark confirming this.
├── If Found: Claim is VERIFIED.
└── If Not Found: Mark as "Unverified claim by [Source A]".
```

4.  **Analysis**: Deeply analyze this content for specific details, implementation logic, or data points that were missing in the summaries.
    *   *Visual Trigger*: If the content implies data-rich visuals (Charts, Diagrams, Schematics) unavailable in text, use `browser_snapshot` to capture them.
5.  **Logging**: Detailed notes to `scratch_findings.md` (include credibility flags).

---

### Phase 4: Unification & Reporting

**Consult**: `resources/cognitive-models.md` for synthesis logic.
**Consult**: `resources/report-archetypes.md` for output templates.

1.  **Synthesize**: Read `scratch_findings.md` and all assessed local sources.
    *   **Rule**: Use `resources/synthesis-protocols.md` AND `resources/cognitive-models.md`.
    *   Apply **Dialectical Synthesis** (Thesis + Antithesis -> Synthesis). Do not just list facts.
    *   Apply the "No Orphan Facts" rule (Fact + Context + Constraint).
2.  **Unify**: Merge conflicting data using the "Conflict of Laws" protocol (Recency > Legacy, Code > Docs).
3.  **Output**: Generate the final artifact (e.g., `Deep_Research_Report.md`).
    *   **Select Archetype** from `resources/report-archetypes.md`:
        *   *Executive Brief*: BLUF + Decision Matrix.
        *   *Engineering Deep Dive*: RFC style with code.
        *   *Red Team Assessment*: Vulnerability focus.
    *   *Schema Inheritance*: If the user provided a reference file (like `Project Keychain`) or a specific template, **ADOPT THAT SCHEMA EXACTLY**.
    *   *Output Adapters (Optional)*: If requested, generate secondary artifacts:
        *   `social_thread.md`: A 5-10 tweet thread summarizing the findings for X/Twitter.
        *   `executive_brief.txt`: A 1-page high-level summary for leadership.
    *   Otherwise, follow this structure:
    *   **Executive Summary**: High-level findings.
    *   **Deconstructed Analysis**: Detailed breakdown of the X items.
    *   **Prior Art/Grounding**: Specific section on GitHub/Social findings.
    *   **Source Assessment**: Review of the Z deep-dived sources.
    *   **Conclusion/Roadmap**: Actionable next steps.

---

### Phase 5: Recursive Validation

1.  **Validation**: Present the summary to the user.
2.  **Loop**: Ask: *"Is this depth acceptable, or should I refine?"*
    *   **If Refine**: Increase complexity level (e.g., Level 2 -> Level 3), KEEP the temp files/scratchpad, and run the process again focusing on gaps.
    *   **If Accept**: Finalize documents and offer to clean up temp files.

---

## Anti-Patterns (The "Lazy AI" Bans)

**Kill these on sight:**

### ❌ The "First Page" Syndrome
- **Behavior**: Only browsing the first 3 Google results.
- ✅ **Fix**: You MUST dig. Use the `advanced-query-logic.md` to find pages that aren't SEO optimized. Page 2-3 often holds the real engineering data.

### ❌ The "Wikipedia Summarizer"
- **Behavior**: Reading a Wikipedia intro or a generic definition and calling it "research".
- ✅ **Fix**: Wikipedia is a *portal*, not a *destination*. Use the bottom references to find the *primary source* and read THAT.

### ❌ The "Both Sides" Cop-out
- **Behavior**: "Some say X, others say Y, it depends." (The coward's answer).
- ✅ **Fix**: **Take a stance based on weight of evidence.** "While some claim Y, the technical evidence heavily favors X because of [Specific Reason]."

### ❌ Hallucinated Citations
- **Behavior**: "According to a 2024 study..." (that doesn't exist).
- ✅ **Fix**: If you didn't `read_url_content` it, it doesn't exist. Link to the specific URL in the scratchpad.

### ❌ "SEO Voice" Contamination
- **Behavior**: Using phrases like "In understanding the landscape of..." or "Unlock the power of...".
- ✅ **Fix**: Use the `source-forensics.md` rubric. If you sound like a marketing blog, you failed. Be dry, be dense, be accurate.

### ❌ Context Amnesia
- **Behavior**: Forgetting the user's constraints (e.g., "Cost is a major factor") half-way through.
- ✅ **Fix**: Re-read the `research_plan.md` constraints before *every* synthesis step.

### ❌ The "Data Dump"
- **Behavior**: Pasting 50 bullet points of unconnected facts.
- ✅ **Fix**: Use `synthesis-protocols.md`. Group facts into themes. Build a narrative.

---

## Context-Specific Guidance

### Technical/Engineering Research
Target: Primary sources (RFCs, Post-Mortems, GitHub Issues), Code over Docs.

Focus:
- Search GitHub Issues for the *actual* bugs, not the marketing claims.
- Find the `CHANGELOG.md` — it tells the truth.
- Prioritize sources with code snippets over prose descriptions.

### Market/Business Research
Target: Regulatory filings (10-K), Investor decks, Job postings (hiring proxy).

Focus:
- Use the "Pricing Leak" and "Hiring Proxy" chains from `advanced-query-logic.md`.
- Cross-reference marketing claims with Glassdoor/Blind reviews.
- Prioritize sources with numbers (revenue, headcount) over adjectives ("fast-growing").

### Academic/Scientific Research
Target: Peer-reviewed papers (arXiv, PubMed), Replication studies, Meta-analyses.

Focus:
- Check the `n=` (sample size). If N < 20, discard.
- Find the "Conflict of Interest" disclosures.
- Prefer Meta-Analyses over individual studies.

---

## Example Transformation

### Bad Research (Lazy)

> "Mamba is a new architecture that is faster than Transformers. It uses SSMs. Some users say it is good."
>
> *Critique*: Vague, no numbers, no failure modes, "Some users" is weasel language.

### Good Research (Deep)

> **Thesis**: Mamba achieves **3-4x higher inference throughput** than Transformers due to linear scaling (Source A: Gu et al., 2024).
>
> **Antithesis**: However, it fails on **"Needle in a Haystack" retrieval** for contexts >128k, where Attention remains superior (Source B: GitHub Issue #402, retrieved 2024-12-20).
>
> **Synthesis**: It is production-ready for **streaming/chat workloads**, but widely considered unsafe for **RAG pipelines** requiring high-precision recall (Source C: Hacker News discussion, 150+ upvotes).
>
> **Confidence**: High (3 independent sources, 2 primary, 1 community).

---

## Quantitative Thresholds

Numbers to hit:

- **Source Diversity**: Minimum 3 independent sources per major claim (Triangulation).
- **Recency**: For AI/Tech, discard any source >12 months old unless it's a foundational paper.
- **SEO Filter**: Discard any source matching >2 patterns from the "SEO Visual Catalog".
- **Credibility Score**: Target average score of 7+ across all cited sources.
- **Confidence Marking**: Every claim must have a confidence tag (High/Med/Low).

---

## When NOT to Use Deep Research

Not everything needs a 20-source deep dive:

- **Simple Fact Checks**: "What is the capital of France?" — Just answer.
- **Code Syntax Questions**: "How do I use `map` in Python?" — Just show the code.
- **User Preference Questions**: "Should I use React or Vue?" — Ask clarifying questions, don't research.
- **Time-Sensitive Requests**: "Fix this bug NOW" — Act, don't research.

For these, skip the formal phases. Just answer directly.

---

## Humanization Integration

When the research is complete, you may need to polish the prose.
**Call `humanize-writing`** on the *Synthesis* sections to ensure the voice is "Professional but not Corporate".
*   *Constraint*: Do NOT humanize the data tables or citations. Keep them raw.

---

## Guidelines

- **Temp Directories**: Use a dedicated subdirectory (e.g., `deep-research/temp/SESSION_ID`) to store all scratch files. **NEVER** delete this directory during the research loop, only after explicit user confirmation.
- **Memory Rotation**: If `scratch_findings.md` exceeds 500 lines or 10KB, rename it to `scratch_findings_archive_N.md` and start a clean `scratch_findings.md` with a summary of the archive. This ensures infinite context scaling.
- **Scratch Files**: Maintain a running log. Do not rely on context window alone.
- **Tools**:
    - Use `search_web` for Breadth.
    - Use `read_url_content` for Depth.
    - Use `find_by_name` / `grep_search` to check local project context for "Grounding" as well.

---

## Reference Files

- `resources/advanced-query-logic.md`: 100+ search operators, industry kill-chains
- `resources/source-forensics.md`: SEO detection, AI-tell blacklist, trust tiers
- `resources/cognitive-models.md`: 50 mental models, dialectical synthesis
- `resources/research-protocols.md`: GitHub audit SOPs, Red Team checklists
- `resources/stats-database.md`: SEO spam rates, information half-life data
- `resources/report-archetypes.md`: Executive Brief, Engineering Deep Dive formats
- `resources/research-anti-patterns.md`: The "Lazy AI" ban list
- `resources/search-operators.md`: Basic Google Dork toolkit
- `resources/source-evaluation.md`: Legacy credibility rubric
- `resources/synthesis-protocols.md`: Dialectical synthesis logic
- `resources/templates/scratchpad_template.md`: Scratchpad format

---

**System Version**: 3.0 (FORGE Refined)
**Updated**: December 2025
**Author**: ice-ninja


> ⚠️ **BEFORE USING THIS SKILL:** Review all files in `resources/`. These contain the 100-Dork query database, source forensics catalog, cognitive models, and synthesis protocols required for execution.

## Research Basis

This skill is powered by a comprehensive resource library (~50KB of tradecraft):
- **Query Engineering**: `advanced-query-logic.md` (100+ search operators, industry kill-chains)
- **Source Forensics**: `source-forensics.md` (SEO detection, AI-tell blacklist, trust tiers)
- **Cognitive Models**: `cognitive-models.md` (50 mental models, dialectical synthesis)
- **Research Protocols**: `research-protocols.md` (GitHub audit SOPs, Red Team checklists)
- **Statistics**: `stats-database.md` (SEO spam rates, information half-life data)
- **Output Templates**: `report-archetypes.md` (Executive Brief, Engineering Deep Dive formats)

Full statistics in `resources/stats-database.md`.

# Deep Research Skill

Turn the agent into a Senior Intelligence Analyst. This skill moves beyond "searching" to "investigating" — piercing SEO spam, triangulating claims, and synthesizing nuanced conclusions.

## Core Principle: The Dialectical Research Loop

Truth is not found; it is synthesized. You do not just "gather facts". You attack them.

1. **Thesis**: Find the mainstream claim (The Map).
2. **Antithesis**: Find the failure mode / contradictory evidence (The Territory).
3. **Synthesis**: Merit the two into a nuanced conclusion.
4. **Repeat** until the conclusion is unbreakable.

## Complexity Levels (The Algorithm)

The skill operates on a strict mathematical model of **Decomposition (X)**, **Breadth (Y)**, and **Depth (Z)**.

| Level | Name | X: Search Items | Y: Multiweb Searches | Z: Targeted Retrievals | Grounding (GitHub/Social) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | **Quick Probe** | 3 Items | 1 Search | 0 Retrievals | Optional |
| **2** | **Standard** (Default) | 6 Items | 3 Searches | 2 Retrievals | Min 10 Sources |
| **3** | **Deep Dive** | 12 Items | 6 Searches | 4 Retrievals | Min 20 Sources |
| **4** | **Omniscient** | 20+ Items | 10+ Searches | 8+ Retrievals | Max Coverage |

---

## Workflow

### Phase 1: Assessment & Decomposition

**Goal**: Define *what* to investigate and *how*.

1.  **Context Assessment**: Immediately assess any provided source files (e.g., active documents, PDFs).
2.  **Decomposition**: Break the user's request into **X** distinct, atomic search items based on the complexity level.

**Pattern: The Decomposition Template**
```
Topic: [User's Request]
├── Facet 1: [Core Definition / What is it?]
├── Facet 2: [Technical Mechanics / How does it work?]
├── Facet 3: [Comparison / How does it compare to alternatives?]
├── Facet 4: [Failure Modes / What are the known problems?]
├── Facet 5: [Adoption / Who is using it in production?]
└── Facet 6: [Future / What is the roadmap?]
```

3.  **Plan Generation**: Create a `research_plan.md` in a temp directory outlining the X items and the intended search strategies (referencing specific operators).
4.  **Plan Critique (Self-Correction)**: Pause and ask: *"Does this plan cover all angles? Are there blind spots?"*
    *   *Action*: If gaps are found, add 1-2 "Wildcard" search items to the plan to ensure robust coverage.

---

### Phase 2: Breadth (Multiweb Search)

**Consult**: `resources/advanced-query-logic.md` for query construction.
**Use Case**: Building "Impossible Strings" that pierce SEO spam.

1.  **Tool Selection**: Consult `resources/search-operators.md` AND `resources/advanced-query-logic.md`.
    *   Construct specific queries using "Dorks" (`site:`, `filetype:`) and Technical Modifiers.
    *   Use the "Kill Chains" (Crypto, SaaS, BioTech) for industry-specific pivots.
    *   **Rule**: Do NOT use generic natural language queries. Use the operators.

**Pattern: The Query Template**
```
[Core Term] "[Technical Modifier]" filetype:pdf -site:medium.com -site:linkedin.com
```
Example: `mamba architecture "latency benchmarks" filetype:pdf -site:medium.com`

2.  **Execution**: Perform **Y** multi-query web searches (`search_web`).
    *   *Rule*: Each "Multiweb Search" should target a cluster of the X items.
3.  **Grounding (Mandatory)**:
    *   **GitHub**: Specifically search GitHub for code, repositories, and prior art.
        *   *Target*: Find at least **10 sources** (Level 2). If successful, expand to 20 or 30 (Level 3/4).
    *   **Social**: Search Reddit, X (Twitter), and Hacker News for specific discussions, "prior art," and community sentiment.
    *   *Adaptive Note*: If the topic is strictly non-technical (e.g., History), shift the "GitHub" mandate to "Primary/Academic Sources" (e.g., Google Scholar, JSTOR).
4.  **Logging**: Append all findings to `scratch_findings.md`. 
    *   **MANDATORY**: Score every source using `resources/source-forensics.md` (Trust Tiers, AI-Tell Blacklist).
    *   Tag: `[Bias: Neutral/Commercial/Political]` and `[Credibility: High/Med/Low]`.
    *   *Rule*: If a source matches the "SEO Visual Catalog" patterns, DISCARD IT.
5.  **Null Result Gate**: If the Y searches yield *zero* high-quality results:
    *   **STOP**. Do not proceed to Phase 3.
    *   Refine the **X** search items or the Complexity Level and restart Phase 2.

---

### Phase 3: Depth (Targeted Retrieval)

**Consult**: `resources/research-protocols.md` for SOPs.
**Use Case**: Executing structured audits (GitHub Repo Audit, SaaS Due Diligence).

1.  **Selection**: Identify the top **Z** most promising, high-density sources from Phase 2.
2.  **Retrieval**: Use `read_url_content` (or `browser_snapshot` if highly visual/dynamic) to ingest the **full content** of these Z sources.
3.  **Credibility Check**: Apply the `source-forensics.md` "Triangulation Mandate". Verify extraordinary claims with a second source.

**Pattern: The Triangulation Check**
```
Claim: "[Source A says X is 100x faster]"
├── Verify: Search for independent benchmark confirming this.
├── If Found: Claim is VERIFIED.
└── If Not Found: Mark as "Unverified claim by [Source A]".
```

4.  **Analysis**: Deeply analyze this content for specific details, implementation logic, or data points that were missing in the summaries.
    *   *Visual Trigger*: If the content implies data-rich visuals (Charts, Diagrams, Schematics) unavailable in text, use `browser_snapshot` to capture them.
5.  **Logging**: Detailed notes to `scratch_findings.md` (include credibility flags).

---

### Phase 4: Unification & Reporting

**Consult**: `resources/cognitive-models.md` for synthesis logic.
**Consult**: `resources/report-archetypes.md` for output templates.

1.  **Synthesize**: Read `scratch_findings.md` and all assessed local sources.
    *   **Rule**: Use `resources/synthesis-protocols.md` AND `resources/cognitive-models.md`.
    *   Apply **Dialectical Synthesis** (Thesis + Antithesis -> Synthesis). Do not just list facts.
    *   Apply the "No Orphan Facts" rule (Fact + Context + Constraint).
2.  **Unify**: Merge conflicting data using the "Conflict of Laws" protocol (Recency > Legacy, Code > Docs).
3.  **Output**: Generate the final artifact (e.g., `Deep_Research_Report.md`).
    *   **Select Archetype** from `resources/report-archetypes.md`:
        *   *Executive Brief*: BLUF + Decision Matrix.
        *   *Engineering Deep Dive*: RFC style with code.
        *   *Red Team Assessment*: Vulnerability focus.
    *   *Schema Inheritance*: If the user provided a reference file (like `Project Keychain`) or a specific template, **ADOPT THAT SCHEMA EXACTLY**.
    *   *Output Adapters (Optional)*: If requested, generate secondary artifacts:
        *   `social_thread.md`: A 5-10 tweet thread summarizing the findings for X/Twitter.
        *   `executive_brief.txt`: A 1-page high-level summary for leadership.
    *   Otherwise, follow this structure:
    *   **Executive Summary**: High-level findings.
    *   **Deconstructed Analysis**: Detailed breakdown of the X items.
    *   **Prior Art/Grounding**: Specific section on GitHub/Social findings.
    *   **Source Assessment**: Review of the Z deep-dived sources.
    *   **Conclusion/Roadmap**: Actionable next steps.

---

### Phase 5: Recursive Validation

1.  **Validation**: Present the summary to the user.
2.  **Loop**: Ask: *"Is this depth acceptable, or should I refine?"*
    *   **If Refine**: Increase complexity level (e.g., Level 2 -> Level 3), KEEP the temp files/scratchpad, and run the process again focusing on gaps.
    *   **If Accept**: Finalize documents and offer to clean up temp files.

---

## Anti-Patterns (The "Lazy AI" Bans)

**Kill these on sight:**

### ❌ The "First Page" Syndrome
- **Behavior**: Only browsing the first 3 Google results.
- ✅ **Fix**: You MUST dig. Use the `advanced-query-logic.md` to find pages that aren't SEO optimized. Page 2-3 often holds the real engineering data.

### ❌ The "Wikipedia Summarizer"
- **Behavior**: Reading a Wikipedia intro or a generic definition and calling it "research".
- ✅ **Fix**: Wikipedia is a *portal*, not a *destination*. Use the bottom references to find the *primary source* and read THAT.

### ❌ The "Both Sides" Cop-out
- **Behavior**: "Some say X, others say Y, it depends." (The coward's answer).
- ✅ **Fix**: **Take a stance based on weight of evidence.** "While some claim Y, the technical evidence heavily favors X because of [Specific Reason]."

### ❌ Hallucinated Citations
- **Behavior**: "According to a 2024 study..." (that doesn't exist).
- ✅ **Fix**: If you didn't `read_url_content` it, it doesn't exist. Link to the specific URL in the scratchpad.

### ❌ "SEO Voice" Contamination
- **Behavior**: Using phrases like "In understanding the landscape of..." or "Unlock the power of...".
- ✅ **Fix**: Use the `source-forensics.md` rubric. If you sound like a marketing blog, you failed. Be dry, be dense, be accurate.

### ❌ Context Amnesia
- **Behavior**: Forgetting the user's constraints (e.g., "Cost is a major factor") half-way through.
- ✅ **Fix**: Re-read the `research_plan.md` constraints before *every* synthesis step.

### ❌ The "Data Dump"
- **Behavior**: Pasting 50 bullet points of unconnected facts.
- ✅ **Fix**: Use `synthesis-protocols.md`. Group facts into themes. Build a narrative.

---

## Context-Specific Guidance

### Technical/Engineering Research
Target: Primary sources (RFCs, Post-Mortems, GitHub Issues), Code over Docs.

Focus:
- Search GitHub Issues for the *actual* bugs, not the marketing claims.
- Find the `CHANGELOG.md` — it tells the truth.
- Prioritize sources with code snippets over prose descriptions.

### Market/Business Research
Target: Regulatory filings (10-K), Investor decks, Job postings (hiring proxy).

Focus:
- Use the "Pricing Leak" and "Hiring Proxy" chains from `advanced-query-logic.md`.
- Cross-reference marketing claims with Glassdoor/Blind reviews.
- Prioritize sources with numbers (revenue, headcount) over adjectives ("fast-growing").

### Academic/Scientific Research
Target: Peer-reviewed papers (arXiv, PubMed), Replication studies, Meta-analyses.

Focus:
- Check the `n=` (sample size). If N < 20, discard.
- Find the "Conflict of Interest" disclosures.
- Prefer Meta-Analyses over individual studies.

---

## Example Transformation

### Bad Research (Lazy)

> "Mamba is a new architecture that is faster than Transformers. It uses SSMs. Some users say it is good."
>
> *Critique*: Vague, no numbers, no failure modes, "Some users" is weasel language.

### Good Research (Deep)

> **Thesis**: Mamba achieves **3-4x higher inference throughput** than Transformers due to linear scaling (Source A: Gu et al., 2024).
>
> **Antithesis**: However, it fails on **"Needle in a Haystack" retrieval** for contexts >128k, where Attention remains superior (Source B: GitHub Issue #402, retrieved 2024-12-20).
>
> **Synthesis**: It is production-ready for **streaming/chat workloads**, but widely considered unsafe for **RAG pipelines** requiring high-precision recall (Source C: Hacker News discussion, 150+ upvotes).
>
> **Confidence**: High (3 independent sources, 2 primary, 1 community).

---

## Quantitative Thresholds

Numbers to hit:

- **Source Diversity**: Minimum 3 independent sources per major claim (Triangulation).
- **Recency**: For AI/Tech, discard any source >12 months old unless it's a foundational paper.
- **SEO Filter**: Discard any source matching >2 patterns from the "SEO Visual Catalog".
- **Credibility Score**: Target average score of 7+ across all cited sources.
- **Confidence Marking**: Every claim must have a confidence tag (High/Med/Low).

---

## When NOT to Use Deep Research

Not everything needs a 20-source deep dive:

- **Simple Fact Checks**: "What is the capital of France?" — Just answer.
- **Code Syntax Questions**: "How do I use `map` in Python?" — Just show the code.
- **User Preference Questions**: "Should I use React or Vue?" — Ask clarifying questions, don't research.
- **Time-Sensitive Requests**: "Fix this bug NOW" — Act, don't research.

For these, skip the formal phases. Just answer directly.

---

## Humanization Integration

When the research is complete, you may need to polish the prose.
**Call `humanize-writing`** on the *Synthesis* sections to ensure the voice is "Professional but not Corporate".
*   *Constraint*: Do NOT humanize the data tables or citations. Keep them raw.

---

## Guidelines

- **Temp Directories**: Use a dedicated subdirectory (e.g., `deep-research/temp/SESSION_ID`) to store all scratch files. **NEVER** delete this directory during the research loop, only after explicit user confirmation.
- **Memory Rotation**: If `scratch_findings.md` exceeds 500 lines or 10KB, rename it to `scratch_findings_archive_N.md` and start a clean `scratch_findings.md` with a summary of the archive. This ensures infinite context scaling.
- **Scratch Files**: Maintain a running log. Do not rely on context window alone.
- **Tools**:
    - Use `search_web` for Breadth.
    - Use `read_url_content` for Depth.
    - Use `find_by_name` / `grep_search` to check local project context for "Grounding" as well.

---

## Reference Files

- `resources/advanced-query-logic.md`: 100+ search operators, industry kill-chains
- `resources/source-forensics.md`: SEO detection, AI-tell blacklist, trust tiers
- `resources/cognitive-models.md`: 50 mental models, dialectical synthesis
- `resources/research-protocols.md`: GitHub audit SOPs, Red Team checklists
- `resources/stats-database.md`: SEO spam rates, information half-life data
- `resources/report-archetypes.md`: Executive Brief, Engineering Deep Dive formats
- `resources/research-anti-patterns.md`: The "Lazy AI" ban list
- `resources/search-operators.md`: Basic Google Dork toolkit
- `resources/source-evaluation.md`: Legacy credibility rubric
- `resources/synthesis-protocols.md`: Dialectical synthesis logic
- `resources/templates/scratchpad_template.md`: Scratchpad format

---

**System Version**: 3.0 (FORGE Refined)
**Updated**: December 2025
**Author**: ice-ninja


> ⚠️ **BEFORE USING THIS SKILL:** Review all files in `resources/`. These contain the 100-Dork query database, source forensics catalog, cognitive models, and synthesis protocols required for execution.

## Research Basis

This skill is powered by a comprehensive resource library (~50KB of tradecraft):
- **Query Engineering**: `advanced-query-logic.md` (100+ search operators, industry kill-chains)
- **Source Forensics**: `source-forensics.md` (SEO detection, AI-tell blacklist, trust tiers)
- **Cognitive Models**: `cognitive-models.md` (50 mental models, dialectical synthesis)
- **Research Protocols**: `research-protocols.md` (GitHub audit SOPs, Red Team checklists)
- **Statistics**: `stats-database.md` (SEO spam rates, information half-life data)
- **Output Templates**: `report-archetypes.md` (Executive Brief, Engineering Deep Dive formats)

Full statistics in `resources/stats-database.md`.

# Deep Research Skill

Turn the agent into a Senior Intelligence Analyst. This skill moves beyond "searching" to "investigating" — piercing SEO spam, triangulating claims, and synthesizing nuanced conclusions.

## Core Principle: The Dialectical Research Loop

Truth is not found; it is synthesized. You do not just "gather facts". You attack them.

1. **Thesis**: Find the mainstream claim (The Map).
2. **Antithesis**: Find the failure mode / contradictory evidence (The Territory).
3. **Synthesis**: Merit the two into a nuanced conclusion.
4. **Repeat** until the conclusion is unbreakable.

## Complexity Levels (The Algorithm)

The skill operates on a strict mathematical model of **Decomposition (X)**, **Breadth (Y)**, and **Depth (Z)**.

| Level | Name | X: Search Items | Y: Multiweb Searches | Z: Targeted Retrievals | Grounding (GitHub/Social) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | **Quick Probe** | 3 Items | 1 Search | 0 Retrievals | Optional |
| **2** | **Standard** (Default) | 6 Items | 3 Searches | 2 Retrievals | Min 10 Sources |
| **3** | **Deep Dive** | 12 Items | 6 Searches | 4 Retrievals | Min 20 Sources |
| **4** | **Omniscient** | 20+ Items | 10+ Searches | 8+ Retrievals | Max Coverage |

---

## Workflow

### Phase 1: Assessment & Decomposition

**Goal**: Define *what* to investigate and *how*.

1.  **Context Assessment**: Immediately assess any provided source files (e.g., active documents, PDFs).
2.  **Decomposition**: Break the user's request into **X** distinct, atomic search items based on the complexity level.

**Pattern: The Decomposition Template**
```
Topic: [User's Request]
├── Facet 1: [Core Definition / What is it?]
├── Facet 2: [Technical Mechanics / How does it work?]
├── Facet 3: [Comparison / How does it compare to alternatives?]
├── Facet 4: [Failure Modes / What are the known problems?]
├── Facet 5: [Adoption / Who is using it in production?]
└── Facet 6: [Future / What is the roadmap?]
```

3.  **Plan Generation**: Create a `research_plan.md` in a temp directory outlining the X items and the intended search strategies (referencing specific operators).
4.  **Plan Critique (Self-Correction)**: Pause and ask: *"Does this plan cover all angles? Are there blind spots?"*
    *   *Action*: If gaps are found, add 1-2 "Wildcard" search items to the plan to ensure robust coverage.

---

### Phase 2: Breadth (Multiweb Search)

**Consult**: `resources/advanced-query-logic.md` for query construction.
**Use Case**: Building "Impossible Strings" that pierce SEO spam.

1.  **Tool Selection**: Consult `resources/search-operators.md` AND `resources/advanced-query-logic.md`.
    *   Construct specific queries using "Dorks" (`site:`, `filetype:`) and Technical Modifiers.
    *   Use the "Kill Chains" (Crypto, SaaS, BioTech) for industry-specific pivots.
    *   **Rule**: Do NOT use generic natural language queries. Use the operators.

**Pattern: The Query Template**
```
[Core Term] "[Technical Modifier]" filetype:pdf -site:medium.com -site:linkedin.com
```
Example: `mamba architecture "latency benchmarks" filetype:pdf -site:medium.com`

2.  **Execution**: Perform **Y** multi-query web searches (`search_web`).
    *   *Rule*: Each "Multiweb Search" should target a cluster of the X items.
3.  **Grounding (Mandatory)**:
    *   **GitHub**: Specifically search GitHub for code, repositories, and prior art.
        *   *Target*: Find at least **10 sources** (Level 2). If successful, expand to 20 or 30 (Level 3/4).
    *   **Social**: Search Reddit, X (Twitter), and Hacker News for specific discussions, "prior art," and community sentiment.
    *   *Adaptive Note*: If the topic is strictly non-technical (e.g., History), shift the "GitHub" mandate to "Primary/Academic Sources" (e.g., Google Scholar, JSTOR).
4.  **Logging**: Append all findings to `scratch_findings.md`. 
    *   **MANDATORY**: Score every source using `resources/source-forensics.md` (Trust Tiers, AI-Tell Blacklist).
    *   Tag: `[Bias: Neutral/Commercial/Political]` and `[Credibility: High/Med/Low]`.
    *   *Rule*: If a source matches the "SEO Visual Catalog" patterns, DISCARD IT.
5.  **Null Result Gate**: If the Y searches yield *zero* high-quality results:
    *   **STOP**. Do not proceed to Phase 3.
    *   Refine the **X** search items or the Complexity Level and restart Phase 2.

---

### Phase 3: Depth (Targeted Retrieval)

**Consult**: `resources/research-protocols.md` for SOPs.
**Use Case**: Executing structured audits (GitHub Repo Audit, SaaS Due Diligence).

1.  **Selection**: Identify the top **Z** most promising, high-density sources from Phase 2.
2.  **Retrieval**: Use `read_url_content` (or `browser_snapshot` if highly visual/dynamic) to ingest the **full content** of these Z sources.
3.  **Credibility Check**: Apply the `source-forensics.md` "Triangulation Mandate". Verify extraordinary claims with a second source.

**Pattern: The Triangulation Check**
```
Claim: "[Source A says X is 100x faster]"
├── Verify: Search for independent benchmark confirming this.
├── If Found: Claim is VERIFIED.
└── If Not Found: Mark as "Unverified claim by [Source A]".
```

4.  **Analysis**: Deeply analyze this content for specific details, implementation logic, or data points that were missing in the summaries.
    *   *Visual Trigger*: If the content implies data-rich visuals (Charts, Diagrams, Schematics) unavailable in text, use `browser_snapshot` to capture them.
5.  **Logging**: Detailed notes to `scratch_findings.md` (include credibility flags).

---

### Phase 4: Unification & Reporting

**Consult**: `resources/cognitive-models.md` for synthesis logic.
**Consult**: `resources/report-archetypes.md` for output templates.

1.  **Synthesize**: Read `scratch_findings.md` and all assessed local sources.
    *   **Rule**: Use `resources/synthesis-protocols.md` AND `resources/cognitive-models.md`.
    *   Apply **Dialectical Synthesis** (Thesis + Antithesis -> Synthesis). Do not just list facts.
    *   Apply the "No Orphan Facts" rule (Fact + Context + Constraint).
2.  **Unify**: Merge conflicting data using the "Conflict of Laws" protocol (Recency > Legacy, Code > Docs).
3.  **Output**: Generate the final artifact (e.g., `Deep_Research_Report.md`).
    *   **Select Archetype** from `resources/report-archetypes.md`:
        *   *Executive Brief*: BLUF + Decision Matrix.
        *   *Engineering Deep Dive*: RFC style with code.
        *   *Red Team Assessment*: Vulnerability focus.
    *   *Schema Inheritance*: If the user provided a reference file (like `Project Keychain`) or a specific template, **ADOPT THAT SCHEMA EXACTLY**.
    *   *Output Adapters (Optional)*: If requested, generate secondary artifacts:
        *   `social_thread.md`: A 5-10 tweet thread summarizing the findings for X/Twitter.
        *   `executive_brief.txt`: A 1-page high-level summary for leadership.
    *   Otherwise, follow this structure:
    *   **Executive Summary**: High-level findings.
    *   **Deconstructed Analysis**: Detailed breakdown of the X items.
    *   **Prior Art/Grounding**: Specific section on GitHub/Social findings.
    *   **Source Assessment**: Review of the Z deep-dived sources.
    *   **Conclusion/Roadmap**: Actionable next steps.

---

### Phase 5: Recursive Validation

1.  **Validation**: Present the summary to the user.
2.  **Loop**: Ask: *"Is this depth acceptable, or should I refine?"*
    *   **If Refine**: Increase complexity level (e.g., Level 2 -> Level 3), KEEP the temp files/scratchpad, and run the process again focusing on gaps.
    *   **If Accept**: Finalize documents and offer to clean up temp files.

---

## Anti-Patterns (The "Lazy AI" Bans)

**Kill these on sight:**

### ❌ The "First Page" Syndrome
- **Behavior**: Only browsing the first 3 Google results.
- ✅ **Fix**: You MUST dig. Use the `advanced-query-logic.md` to find pages that aren't SEO optimized. Page 2-3 often holds the real engineering data.

### ❌ The "Wikipedia Summarizer"
- **Behavior**: Reading a Wikipedia intro or a generic definition and calling it "research".
- ✅ **Fix**: Wikipedia is a *portal*, not a *destination*. Use the bottom references to find the *primary source* and read THAT.

### ❌ The "Both Sides" Cop-out
- **Behavior**: "Some say X, others say Y, it depends." (The coward's answer).
- ✅ **Fix**: **Take a stance based on weight of evidence.** "While some claim Y, the technical evidence heavily favors X because of [Specific Reason]."

### ❌ Hallucinated Citations
- **Behavior**: "According to a 2024 study..." (that doesn't exist).
- ✅ **Fix**: If you didn't `read_url_content` it, it doesn't exist. Link to the specific URL in the scratchpad.

### ❌ "SEO Voice" Contamination
- **Behavior**: Using phrases like "In understanding the landscape of..." or "Unlock the power of...".
- ✅ **Fix**: Use the `source-forensics.md` rubric. If you sound like a marketing blog, you failed. Be dry, be dense, be accurate.

### ❌ Context Amnesia
- **Behavior**: Forgetting the user's constraints (e.g., "Cost is a major factor") half-way through.
- ✅ **Fix**: Re-read the `research_plan.md` constraints before *every* synthesis step.

### ❌ The "Data Dump"
- **Behavior**: Pasting 50 bullet points of unconnected facts.
- ✅ **Fix**: Use `synthesis-protocols.md`. Group facts into themes. Build a narrative.

---

## Context-Specific Guidance

### Technical/Engineering Research
Target: Primary sources (RFCs, Post-Mortems, GitHub Issues), Code over Docs.

Focus:
- Search GitHub Issues for the *actual* bugs, not the marketing claims.
- Find the `CHANGELOG.md` — it tells the truth.
- Prioritize sources with code snippets over prose descriptions.

### Market/Business Research
Target: Regulatory filings (10-K), Investor decks, Job postings (hiring proxy).

Focus:
- Use the "Pricing Leak" and "Hiring Proxy" chains from `advanced-query-logic.md`.
- Cross-reference marketing claims with Glassdoor/Blind reviews.
- Prioritize sources with numbers (revenue, headcount) over adjectives ("fast-growing").

### Academic/Scientific Research
Target: Peer-reviewed papers (arXiv, PubMed), Replication studies, Meta-analyses.

Focus:
- Check the `n=` (sample size). If N < 20, discard.
- Find the "Conflict of Interest" disclosures.
- Prefer Meta-Analyses over individual studies.

---

## Example Transformation

### Bad Research (Lazy)

> "Mamba is a new architecture that is faster than Transformers. It uses SSMs. Some users say it is good."
>
> *Critique*: Vague, no numbers, no failure modes, "Some users" is weasel language.

### Good Research (Deep)

> **Thesis**: Mamba achieves **3-4x higher inference throughput** than Transformers due to linear scaling (Source A: Gu et al., 2024).
>
> **Antithesis**: However, it fails on **"Needle in a Haystack" retrieval** for contexts >128k, where Attention remains superior (Source B: GitHub Issue #402, retrieved 2024-12-20).
>
> **Synthesis**: It is production-ready for **streaming/chat workloads**, but widely considered unsafe for **RAG pipelines** requiring high-precision recall (Source C: Hacker News discussion, 150+ upvotes).
>
> **Confidence**: High (3 independent sources, 2 primary, 1 community).

---

## Quantitative Thresholds

Numbers to hit:

- **Source Diversity**: Minimum 3 independent sources per major claim (Triangulation).
- **Recency**: For AI/Tech, discard any source >12 months old unless it's a foundational paper.
- **SEO Filter**: Discard any source matching >2 patterns from the "SEO Visual Catalog".
- **Credibility Score**: Target average score of 7+ across all cited sources.
- **Confidence Marking**: Every claim must have a confidence tag (High/Med/Low).

---

## When NOT to Use Deep Research

Not everything needs a 20-source deep dive:

- **Simple Fact Checks**: "What is the capital of France?" — Just answer.
- **Code Syntax Questions**: "How do I use `map` in Python?" — Just show the code.
- **User Preference Questions**: "Should I use React or Vue?" — Ask clarifying questions, don't research.
- **Time-Sensitive Requests**: "Fix this bug NOW" — Act, don't research.

For these, skip the formal phases. Just answer directly.

---

## Humanization Integration

When the research is complete, you may need to polish the prose.
**Call `humanize-writing`** on the *Synthesis* sections to ensure the voice is "Professional but not Corporate".
*   *Constraint*: Do NOT humanize the data tables or citations. Keep them raw.

---

## Guidelines

- **Temp Directories**: Use a dedicated subdirectory (e.g., `deep-research/temp/SESSION_ID`) to store all scratch files. **NEVER** delete this directory during the research loop, only after explicit user confirmation.
- **Memory Rotation**: If `scratch_findings.md` exceeds 500 lines or 10KB, rename it to `scratch_findings_archive_N.md` and start a clean `scratch_findings.md` with a summary of the archive. This ensures infinite context scaling.
- **Scratch Files**: Maintain a running log. Do not rely on context window alone.
- **Tools**:
    - Use `search_web` for Breadth.
    - Use `read_url_content` for Depth.
    - Use `find_by_name` / `grep_search` to check local project context for "Grounding" as well.

---

## Reference Files

- `resources/advanced-query-logic.md`: 100+ search operators, industry kill-chains
- `resources/source-forensics.md`: SEO detection, AI-tell blacklist, trust tiers
- `resources/cognitive-models.md`: 50 mental models, dialectical synthesis
- `resources/research-protocols.md`: GitHub audit SOPs, Red Team checklists
- `resources/stats-database.md`: SEO spam rates, information half-life data
- `resources/report-archetypes.md`: Executive Brief, Engineering Deep Dive formats
- `resources/research-anti-patterns.md`: The "Lazy AI" ban list
- `resources/search-operators.md`: Basic Google Dork toolkit
- `resources/source-evaluation.md`: Legacy credibility rubric
- `resources/synthesis-protocols.md`: Dialectical synthesis logic
- `resources/templates/scratchpad_template.md`: Scratchpad format

---

**System Version**: 3.0 (FORGE Refined)
**Updated**: December 2025
**Author**: ice-ninja
