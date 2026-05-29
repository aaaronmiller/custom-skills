# Refinement Patterns: Guiding Iterative Research Improvement

## Table of Contents
1. The Refinement Loop
2. Widen Operations
3. Deepen Operations
4. Saturate Operations
5. Parameter Adjustments
6. Convergence Detection
7. User Interaction Patterns

## 1. The Refinement Loop

After initial delivery, the user enters a refinement loop:

```
DELIVER REPORT
    |
    v
USER REVIEWS
    |
    ├─ "Looks good" -> FINALIZE
    ├─ "More on [topic]" -> SATURATE that branch
    ├─ "Also look at [new angle]" -> WIDEN
    ├─ "Go deeper on [branch]" -> DEEPEN that branch
    ├─ "Check [specific claim]" -> Increase V for that claim
    ├─ "Polish the report" -> Increase F
    └─ "Start over with different focus" -> Re-run Phase 0
```

Each refinement produces an addendum, never a full rewrite.

## 2. Widen Operations

**Trigger**: User wants new angles explored that weren't in original decomposition.

**Process**:
1. Accept new sub-question(s) from user
2. Validate they don't overlap with existing sub-questions
3. Run through full Phase 2 pipeline at current D and S settings
4. Verify at current V setting
5. Append findings as new section(s) in report
6. Update Executive Summary addendum
7. Check if new findings modify conclusions from original sub-questions

**Example**:
```
User: "Great research on AI agents, but you didn't cover the regulatory angle."
Action: Add sub-question "What regulations currently apply or are proposed for AI agent systems?"
       Run at D=2, S=4, V=1 (matching original Standard profile)
       Append as new section after existing findings
```

## 3. Deepen Operations

**Trigger**: User wants more recursive discovery on a specific branch.

**Process**:
1. Identify the target branch (sub-question or recursive discovery)
2. Increase D for that branch by 1-2 layers
3. Use existing findings as the starting context for deeper searches
4. New depth layers search for concepts referenced in but not explored by existing findings
5. Append discoveries under the existing branch section
6. Update cross-cutting themes if new patterns emerge

**Example**:
```
User: "The section on quantum error correction mentions 'topological codes' but doesn't explain them."
Action: Increase D on that branch. Search specifically for topological codes,
        their implementations, current limitations, and comparison to other approaches.
        Append under the existing QEC section.
```

## 4. Saturate Operations

**Trigger**: User wants more sources on a specific angle for higher confidence.

**Process**:
1. Identify the under-saturated branch
2. Increase S for that branch by 2-5 sources
3. Specifically seek sources from different tiers than already collected
4. Look for contradicting viewpoints not yet represented
5. Append additional findings, noting whether they confirm or challenge existing conclusions
6. Update confidence scores if warranted

**Example**:
```
User: "Only 2 sources on the cost comparison. Get more data."
Action: Increase S on cost comparison branch. Seek pricing data from
        vendor sites, analyst reports, user testimonials, and benchmark studies.
        Update the comparison table with new data points.
```

## 5. Parameter Adjustments

Users can modify any parameter between iterations:

| Adjustment | Syntax Examples | Effect |
|------------|----------------|--------|
| Increase V | "verify more", "I need to be sure" | Re-run Phase 3 at higher V |
| Increase F | "polish this", "more refined" | Re-run Phase 4 at higher F |
| Selective W | "also cover X" | Add specific sub-question |
| Selective D | "go deeper on section 3" | Increase D for one branch |
| Selective S | "more sources on X" | Increase S for one branch |
| Full re-scope | "actually, focus more on Y" | Re-run Phase 0 with adjusted query |

## 6. Convergence Detection

Know when to suggest stopping:

**Signals that more research will help**:
- Branches with S < 3 on important topics
- Confidence scores of ■□□ or ? on key findings
- Contradictions flagged but not resolved
- User questions that the current report can't answer

**Signals to suggest stopping**:
- Additional sources are restating what's already known (saturation plateau)
- All key findings are at ■■■ or ■■□ confidence
- No new concepts discovered in last depth layer (discovery exhaustion)
- Report adequately answers the original query and likely follow-ups

**How to communicate**: "Based on the current findings, the areas with most potential for additional value are [X, Y]. The research appears well-saturated on [Z]. Would you like to continue refining, or is this sufficient?"

## 7. User Interaction Patterns

### Pattern: The Narrower
User starts broad, then focuses after seeing initial results.
```
Turn 1: "Research AI safety" -> Standard profile, broad decomposition
Turn 2: "Focus on alignment specifically" -> Deepen alignment branch, reduce others
Turn 3: "What about RLHF limitations?" -> Deepen further on specific technique
```
Strategy: Be ready to pivot. Don't over-invest in breadth if the user's interest is narrowing.

### Pattern: The Expander
User starts narrow, then keeps asking for more angles.
```
Turn 1: "Research RLHF" -> Standard profile, focused
Turn 2: "Also cover DPO and constitutional AI" -> Widen
Turn 3: "And the debate between Anthropic and DeepMind approaches" -> Widen + Deepen
```
Strategy: Track total scope. Warn when cumulative W*D*S exceeds Thorough profile levels.

### Pattern: The Verifier
User fixates on accuracy and wants everything cross-checked.
```
Turn 1: "Research X" -> Standard profile
Turn 2: "Are you sure about that 47% figure?" -> Selective V increase
Turn 3: "Verify all the claims in section 2" -> V=3 on that section
```
Strategy: Run targeted verification passes. Don't re-research, just re-verify.

### Pattern: The Producer
User wants the report itself improved, not the research.
```
Turn 1: "Research X" -> Standard profile
Turn 2: "Make the executive summary punchier" -> F increase, writing quality
Turn 3: "Add a table comparing the top 5 options" -> Structural refinement
```
Strategy: These are synthesis/presentation requests, not research requests. Handle in Phase 4 without re-running Phases 1-3.
