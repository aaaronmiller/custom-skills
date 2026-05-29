# Verification Strategies

## Table of Contents
1. Verification Levels
2. Claim Extraction
3. Source Quality Hierarchy
4. Contradiction Handling
5. Confidence Scoring
6. Reporting Format

## 1. Verification Levels

### V=0: Trust Mode
No explicit verification. Appropriate only for:
- Skim profiles where speed matters more than certainty
- Well-established facts from authoritative sources
- Topics with low consequence for errors

Even at V=0, note when a single claim comes from only one source.

### V=1: Spot-Check Mode
- Extract the top ~30% of claims by importance
- For each selected claim, search for one independent corroborating source
- If corroboration found: mark as "supported"
- If contradicted: escalate to V=2 treatment for that specific claim
- If no independent source found: mark as "single-source, unverified"

### V=2: Systematic Verification
- Extract ~60% of substantive claims
- For each, find two independent sources
- Cross-reference specific data points (numbers, dates, names)
- Apply the "two of three" rule: if 2/3 sources agree, adopt that position. If all three disagree, report the disagreement explicitly.
- Verify recency: are sources from the same time period? Outdated sources on fast-moving topics should be flagged.

### V=3: Triangulation Mode
- Extract ALL substantive claims
- For each, require three independent sources
- Sources must come from different categories (e.g., not three blog posts, but one academic paper + one news source + one primary document)
- Apply contradiction detection: actively search for counter-evidence
- For numerical claims: verify across primary data sources, not just reports of data
- Record the full provenance chain for each claim

## 2. Claim Extraction

A "claim" is any statement that could be true or false. Extract claims that are:

**Always verify**:
- Numerical/statistical claims ("X% of companies use Y")
- Causal claims ("X caused Y")
- Superlative claims ("X is the best/first/only")
- Attribution claims ("Person X said Y")
- Existence claims ("X exists" or "X doesn't exist")

**Verify when V >= 2**:
- Descriptive claims ("X works by doing Y")
- Comparative claims ("X is better than Y at Z")
- Timeline claims ("X happened before Y")

**Skip verification for**:
- Definitions from authoritative sources
- Claims the agent can verify from training knowledge
- Tautologies and logical necessities

## 3. Source Quality Hierarchy

When selecting verification sources, prefer higher-quality sources:

```
Tier 1 (Highest Authority):
  - Peer-reviewed academic papers
  - Official government publications
  - Primary documents (financial filings, court records)
  - Specification documents (RFCs, W3C specs)

Tier 2 (High Authority):
  - Official company documentation
  - Major news outlets with editorial standards
  - Expert commentary with credentials cited
  - Technical documentation from maintainers

Tier 3 (Moderate Authority):
  - Industry analysis from recognized firms
  - Well-sourced blog posts from domain experts
  - Conference presentations and talks
  - Community-curated resources (awesome lists, wikis)

Tier 4 (Low Authority, Still Useful):
  - Forum discussions (Reddit, HN, Stack Overflow)
  - Personal blogs without sourcing
  - Social media posts
  - Marketing materials

Tier 5 (Use With Caution):
  - Anonymous sources
  - Content farms / SEO-optimized thin content
  - Undated material
  - Sources with clear commercial bias
```

**Rule**: At V >= 2, at least one verification source must be Tier 1 or Tier 2.

## 4. Contradiction Handling

When sources disagree:

### Step 1: Classify the contradiction
- **Factual**: Sources state different numbers/dates/names -> The most recent, most authoritative source wins. Report the discrepancy.
- **Interpretive**: Sources agree on facts but disagree on meaning -> Present both interpretations with their reasoning.
- **Methodological**: Sources used different methods, got different results -> Report both methods and results. Note which is more rigorous.
- **Temporal**: Sources from different time periods reflect change over time -> Present as evolution, not contradiction.

### Step 2: Report transparently
Never silently pick one side. Always:
1. State the claim as presented by Source A
2. State the counter-claim from Source B
3. Provide your assessment of which is more credible and why
4. Let the reader decide

### Step 3: Adjust confidence
Contradicted claims get a lower confidence score regardless of source quality.

## 5. Confidence Scoring

Assign confidence to each major finding:

| Level | Symbol | Meaning |
|-------|--------|---------|
| **High** | ■■■ | 3+ independent sources agree, at least one Tier 1-2 |
| **Medium** | ■■□ | 2 sources agree, or 1 Tier 1 source uncontradicted |
| **Low** | ■□□ | Single source, or sources of Tier 3+ only |
| **Disputed** | ⚡ | Sources actively contradict each other |
| **Unverified** | ? | Claim exists in research but was not independently checked |

Include confidence indicators inline with findings in the report.

## 6. Reporting Format

In the final report, verification results appear in two places:

**Inline**: After each major claim, append the confidence symbol.
```
The market for AI implementation specialists grew 34% YoY in 2025 ■■■
[Source: BLS data, LinkedIn Workforce Report, Indeed Hiring Trends]
```

**Summary section**: A dedicated "Verification Summary" section listing:
- Total claims extracted
- Claims verified at each confidence level
- Key contradictions discovered
- Claims that could not be independently verified
- Recommended areas for further investigation
