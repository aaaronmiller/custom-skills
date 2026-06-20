# Inference Guide: Resolving R(W,D,S,V,F) from Ambiguous Requests

## Table of Contents
1. Decision Tree
2. Signal Detection
3. Keyword Mapping
4. Complexity Scoring
5. Override Rules
6. Examples

## 1. Decision Tree

```
START
├─ User provides explicit parameters? -> Use them directly
├─ User names a profile? -> Use that profile
├─ User provides no guidance? -> Score complexity:
│   ├─ Score 1-3:  Survey     R(3,1,2,0,1)
│   ├─ Score 4-6:  Standard R(6,2,4,1,1)
│   ├─ Score 7-9:  Thorough R(10,3,6,2,2)
│   └─ Score 10+:  Exhaustive R(15,4,10,3,3)
└─ Ambiguous? -> Default to Standard, ask user to confirm
```

## 2. Signal Detection

### Signals that INCREASE scope

| Signal | W bump | D bump | S bump | V bump | F bump |
|--------|--------|--------|--------|--------|--------|
| "comprehensive" or "exhaustive" | +4 | +1 | +3 | +1 | +1 |
| "all perspectives" or "every angle" | +6 | 0 | +2 | 0 | 0 |
| "deep dive" or "go deep" | +2 | +2 | +2 | 0 | 0 |
| "I need to be sure" or "critical decision" | +2 | +1 | +2 | +2 | +1 |
| "academic" or "peer-reviewed" | +2 | +1 | +4 | +2 | +1 |
| "compare X options" where X > 3 | +X | +1 | +2 | +1 | 0 |
| Mentions specific page count or word count | Scale proportionally | | | | |
| "due diligence" | +4 | +2 | +4 | +2 | +2 |
| "survey the landscape" | +6 | +1 | +2 | 0 | 0 |

### Signals that DECREASE scope

| Signal | Effect |
|--------|--------|
| "quick" or "brief" or "overview" | Cap at Survey |
| "just the basics" | Cap at Survey |
| "don't go overboard" | Cap at Standard |
| "time-sensitive" or "urgent" | Reduce D and S by 1 each |
| "I just need to know X" (single specific fact) | NOT a research task. Answer directly. |

## 3. Keyword Mapping

### Domain-specific parameter adjustments

**Technical/Engineering topics**: Increase S by +2 (more sources needed for accuracy). Ensure GitHub grounding is prioritized.

**Medical/Legal/Financial topics**: Set V >= 2 (high verification). Set F >= 2 (high fidelity). These domains have high consequence for errors.

**Emerging/Rapidly-changing topics** (AI, crypto, startups): Increase D by +1 (high discovery potential). Prioritize recency in source selection.

**Historical/Established topics**: Decrease D by -1 (less recursive discovery expected). Increase S by +1 (more established sources to draw from).

**Contested/Political topics**: Set V >= 2. Ensure W includes at least one sub-question per major perspective.

## 4. Complexity Scoring

Score the query on these dimensions (1 point each):

1. **Multi-domain**: Query spans 2+ distinct knowledge domains
2. **Temporal range**: Query involves historical context AND current state
3. **Multiple entities**: 3+ companies/products/concepts to compare
4. **Contested**: Known disagreement exists among experts
5. **Technical depth**: Requires understanding of specialized terminology
6. **Quantitative**: Needs specific numbers, statistics, or measurements
7. **Forward-looking**: Involves prediction or forecasting
8. **Multi-stakeholder**: Different stakeholders have different interests
9. **Implementation-oriented**: User needs actionable, not just informational output
10. **Novel/Emerging**: Topic has limited established literature

Sum the applicable points. Map to profiles as shown in the decision tree.

## 5. Override Rules

These always apply regardless of scoring:

- If user says "research" + any topic -> minimum Standard profile
- If user says "deep research" -> minimum Thorough profile
- If user is clearly in a hurry -> cap at Standard, note the limitation
- If topic involves health, safety, or legal risk -> minimum V=2
- If user has provided prior research context -> reduce W (they've already decomposed), increase D (go deeper on what they have)
- If user specifies output length (e.g., "2000 words") -> scale F proportionally: <1000 words = F=1, 1000-3000 = F=2, 3000+ = F=3

## 6. Examples

### Example 1: "What are the best project management tools for a team of 20?"
- Complexity score: 3 (multiple entities, implementation-oriented, multi-stakeholder)
- Profile: **Survey** (bounded comparison, clear answer space)
- R(3,1,2,0,1) -> W=3 angles [features, pricing, team-size fit]

### Example 2: "Research the current state of quantum computing for drug discovery"
- Complexity score: 7 (multi-domain, technical depth, quantitative, forward-looking, novel)
- Profile: **Thorough**
- R(10,3,6,2,2) -> 10 angles covering hardware, algorithms, pharma applications, clinical trials, companies, funding, limitations, competing approaches, regulatory, timeline

### Example 3: "I'm deciding whether to migrate our infrastructure from AWS to GCP. Do a deep dive."
- Complexity score: 9 (multi-domain, multiple entities, technical, quantitative, implementation, multi-stakeholder, contested, plus "deep dive" keyword)
- Profile: **Exhaustive** (due to "deep dive" override + high complexity)
- R(15,4,10,3,3) -> Full investigation

### Example 4: "Quick overview of what's happening with AI agents"
- "Quick" + "overview" -> **Survey** override
- R(3,1,2,0,1) -> 3 angles, surface-level scan

### Example 5: "Research the market for AI Implementation Specialists in Seattle"
- Complexity score: 6 (multi-stakeholder, quantitative, implementation, temporal, multiple entities, forward-looking)
- Profile: **Standard** heading toward Thorough
- R(8,2,5,1,2) -> Hybrid: more width than Standard, extra fidelity pass for actionable output
