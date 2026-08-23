# Skill Scoring Rubric & Comparison Methodology

Use for detailed scoring, cross-skill comparison, and marketplace gap analysis.

## 10-Category Scoring Rubric (100 points)

| # | Category | Max | 1-3 (Poor) | 4-6 (Adequate) | 7-8 (Good) | 9-10 (Excellent) |
|---|----------|-----|------------|----------------|------------|------------------|
| 1 | **Utility** | 10 | Solves rare/niche problem | Useful occasionally | Solves frequent real problem | Indispensable daily driver |
| 2 | **Completeness** | 10 | Missing steps, gaps | Covers main case | Handles edge cases too | Production-ready, all paths covered |
| 3 | **Progressive Disclosure** | 10 | Everything in one bloated file | SKILL.md has refs/ | Has refs/ + scripts/ + examples/ | Perfect 3-level loading |
| 4 | **Trigger Coverage** | 10 | No "Use when:" or triggers | Generic triggers | Specific trigger phrases | 10+ triggers with "Triggers:" section |
| 5 | **Uniqueness** | 10 | Duplicates existing skill | Same method, diff implementation | Novel approach to known problem | Unlocks capability nothing else does |
| 6 | **Cross-CLI Compat** | 10 | Claude Code only | Claude + 1-2 others | Works on 4+ CLIs | 8+ CLIs (our target list) |
| 7 | **Resource Files** | 10 | SKILL.md only | Has references/ | Has refs/ + scripts/ | Full: scripts/ + refs/ + examples/ + templates/ |
| 8 | **Maintenance** | 10 | No version/author | Has version/author | Version + author + license | Active, tracked, changelog |
| 9 | **Token Efficiency** | 10 | Body >500 lines, verbose | Moderate length | <300 lines, concise | <200 lines, highly optimized |
| 10 | **Creativity** | 10 | Copy-paste from docs | Standard approach | Clever solution | Breakthrough methodology |

## Grade Mapping

| Total | Grade | Meaning | Action |
|-------|-------|---------|--------|
| 90-100 | S-Tier | Premium. User skills level. | Keep, promote as reference. |
| 70-89 | A-Tier | Good quality. Most well-made skills. | Keep. |
| 50-69 | B-Tier | Adequate. Functional but improvable. | Keep, could improve. |
| 30-49 | C-Tier | Weak. Needs work or junk candidate. | Flag for improvement or removal. |
| 0-29 | D-Tier | Junk. | Remove or consolidate. |

## Cross-Skill Comparison Protocol

When comparing two skills that do the same thing (e.g., our version vs a
marketplace version):

### Step 1: Grade Both
Score each skill independently using the 10-category rubric. Do not compare
them directly yet — grade each against the rubric alone.

### Step 2: Identify Category Wins
For each of the 10 categories, note which skill scores higher and why.
Categories where both score the same are neutral.

### Step 3: Weight by Context
Not all categories matter equally for every comparison. For example:
- A skill for personal use: Uniqueness ≈ 0 (just needs to work)
- A skill for distribution: Uniqueness = high priority
- A skill for Claude Code only: Cross-CLI compat ≈ 0

Apply context weights on a 1-3 scale (1=low, 2=medium, 3=high importance):

```
weighted_score = category_score × importance
```

### Step 4: Determine Best

| Result | Action |
|--------|--------|
| Our skill wins decisively (10+ point gap) | Keep ours, ignore marketplace version |
| Their skill wins decisively | Adopt theirs (install via npx skills add) |
| Close match (<10 point gap) | Merge: keep our body, take their best ideas |
| Different strengths | Combine into one superseding skill |

### Step 5: Merging Protocol

When merging two skills:

1. Start with the **higher-scoring** skill as the base
2. For each category where the other skill scored higher, port those elements
3. Always preserve: trigger coverage, progressive disclosure structure, cross-CLI compat
4. Save the merged result as a new version in Skills-USER/
5. Run deliberative refinement (V(3,1,0) LITE) to validate the merge

## Marketplace Gap Analysis

When evaluating whether we're missing a skill others have:

### Step 1: Source Data

Check these marketplaces for trending skills:

| Marketplace | URL | What It Tracks |
|-------------|-----|---------------|
| skills.sh | https://skills.sh | Install counts (npx skills telemetry) |
| MCP Market | Various | GitHub stars, categories |
| ClaudSkills | https://claudskills.com | Registry of 62k+ skills |
| Agensi | https://agensi.io | Verified installs |
| TokRepo | https://tokrepo.com | Skill marketplace |
| ClawHub | https://clawhub.ai | Community market |

### Step 2: Filter by Utility

Not every high-star skill is worth adopting. Apply these filters:

**HIGH priority to adopt:**
- Solves a problem we encounter weekly
- Zero or low friction to install (single file, no API keys)
- Doesn't conflict with existing skills
- Cross-CLI compatible

**MEDIUM priority:**
- Niche but useful occasionally
- Requires some setup (API key, MCP server)
- Overlaps partially with existing skill

**LOW priority:**
- Entertainment/novelty (pokemon, game skills)
- Requires heavy dependencies
- Only works on one CLI

### Step 3: Verify via Rubric

Before adopting any external skill, score it with the rubric.
Compare against any equivalent we have. If theirs scores 10+ points
higher, adopt. If close (<10), merge.

## Real-World Example

Comparing our `deliberative-refinement` vs any marketplace alternative:

| Category | Our Score | Marketplace | Winner |
|----------|-----------|-------------|--------|
| Utility | 10 | 8 | Ours |
| Completeness | 10 | 7 | Ours |
| Progressive Disclosure | 9 | 6 | Ours |
| Trigger Coverage | 10 | 5 | Ours |
| Uniqueness | 10 | 3 | Ours (unique concept) |
| Cross-CLI Compat | 8 | 7 | Ours |
| Resources | 9 | 4 | Ours |
| Maintenance | 9 | 6 | Ours |
| Token Efficiency | 7 | 8 | Market (shorter) |
| Creativity | 10 | 5 | Ours |

**Total: Ours 92, Market 59. Keep ours.**
