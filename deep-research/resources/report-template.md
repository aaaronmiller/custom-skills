# Report Template

## Structure

Every Deep Research report follows this structure. Sections marked [REQUIRED] must always appear. Sections marked [CONDITIONAL] appear only when their trigger condition is met.

**Note**: The YAML frontmatter below is optional and should be adapted to your project conventions. Omit it if your workflow does not use frontmatter.

```
---
date: {{DATE}} {{TIME}} {{TZ}}
ver: {{VERSION}}
author: {{AUTHOR}}
model: {{MODEL}}
tags: {{TAGS}}
---

# {{RESEARCH TITLE}}

## Research Scope [REQUIRED]
Parameters: R(W={{W}}, D={{D}}, S={{S}}, V={{V}}, F={{F}}) [{{PROFILE}}]
Query: "{{ORIGINAL_USER_QUERY}}"
Total searches executed: {{ACTUAL_COUNT}}
Sources analyzed: {{SOURCE_COUNT}}
Duration: {{TIME_TAKEN}}

## Executive Summary [REQUIRED]
3-5 paragraphs synthesizing the key findings. No citations here.
Lead with the most important conclusion. End with the most
significant open question or uncertainty.

## Decomposition [REQUIRED]
List the W sub-questions used, with brief rationale for each.

1. **[Sub-question 1]**: [Why this angle matters]
2. **[Sub-question 2]**: [Why this angle matters]
... (W items)

## Findings [REQUIRED]

### [Sub-question 1 Title]

[Narrative synthesis of findings for this angle. Multiple paragraphs.
Each claim includes inline citation and confidence indicator.]

Key sources: [list 2-3 most important sources for this section]

### [Sub-question 2 Title]
... (repeat for each sub-question)

## Recursive Discoveries [CONDITIONAL: D > 1 and new concepts found]

Topics discovered during research that were not in the original
decomposition but proved relevant:

- **[Concept A]**: Discovered via [source]. Relevance: [explanation].
  Findings: [what was learned when this branch was explored]
- **[Concept B]**: ...

## Cross-Cutting Themes [CONDITIONAL: W > 4]

Patterns that emerged across multiple sub-questions:

1. **[Theme 1]**: Observed in sub-questions [X, Y, Z]. [Description].
2. **[Theme 2]**: ...

## Contradictions and Disputes [CONDITIONAL: V > 0]

Claims where sources disagree:

| Claim | Source A Position | Source B Position | Assessment |
|-------|-------------------|-------------------|------------|
| ... | ... | ... | ... |

## Confidence Assessment [CONDITIONAL: V > 0]

| Finding | Confidence | Supporting Sources |
|---------|------------|-------------------|
| ... | ■■■/■■□/■□□/⚡/? | [sources] |

## Source Bibliography [REQUIRED]

Organized by quality tier:

### Tier 1 (Academic/Official)
1. [Full citation with URL, date accessed, tier annotation]

### Tier 2 (Authoritative)
...

### Tier 3 (Expert/Industry)
...

### Tier 4 (Community)
...

## Limitations and Open Questions [CONDITIONAL: F >= 3]

### Coverage Gaps
- Topics not adequately covered and why
- Sources that were sought but not found

### Potential Biases
- Source set skew (geographic, temporal, ideological)
- Search query limitations

### Open Questions
- Questions that remain unanswered
- Recommended next steps for further research

## Refinement Options [REQUIRED]

Based on this research, you can refine by:

1. **Widen**: Add sub-questions on [suggested new angles]
2. **Deepen**: Increase D on [branches with high discovery potential]
3. **Saturate**: More sources on [under-covered branches]

Specify adjustments or say "looks good" to finalize.
```

## Guidelines

### Writing Style
- Lead with conclusions, follow with evidence
- Use active voice
- Cite sources inline, not just at the end
- Quantify when possible ("34% growth" not "significant growth")
- Acknowledge uncertainty explicitly rather than hedging
- Never use em dashes

### Length Calibration

| Profile | Target Report Length |
|---------|-------------------|
| Survey | 500-1000 words |
| Standard | 1500-3000 words |
| Thorough | 3000-6000 words |
| Exhaustive | 6000-12000 words |

### Citation Format

Inline citations use bracketed source references:
```
The adoption rate increased to 47% in Q3 2025 [BLS-2025, LinkedIn-WFR].
```

Full citations in bibliography include:
- Author/organization
- Title
- Publication date
- URL
- Date accessed
- Quality tier annotation

### Handling Refinement Iterations

When the user requests a refinement pass:
1. Do NOT rewrite the existing report
2. Append a new section with header: `## Refinement Pass [N]: [Description]`
3. Reference back to original sections where new findings modify earlier conclusions
4. Update the Executive Summary with a brief addendum noting what changed
5. Update the Research Scope section with new actual counts
