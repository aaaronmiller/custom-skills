---
name: Is It Funny Refinement
description: Evaluate comedic content quality using 10/3/1 ISO deliberative-refinement
  with comedy expert council
inputs:
- name: comedic_content
  description: Comedic content to evaluate and refine
  pointer_type: parameter
outputs:
- name: refinement_report
  description: Quality evaluation and refinement suggestions
  pointer_type: output_file
tags:
- fun
- social
grade: B
source: custom
---

# Is It Funny Refinement Skill

**Comedy Quality Evaluator**

Assess whether satirical content actually lands as funny using deliberative-refinement (10-person comedy expert council, 3 rounds of evaluation, 1 web search between rounds). Produces actionable feedback and numerical scores for iterative improvement.

---

## Purpose

This skill is used to **measure whether satire is actually funny**, not whether it's technically correct. Use it to:

1. **Score baseline comedy quality** before iterating
2. **Identify specific failure modes** (punchline clarity, originality issues, laugh likelihood problems)
3. **Track improvement** across refinement iterations
4. **Generate actionable feedback** for skill updates
5. **Build metrics** for comparative analysis (what formats work best, what subjects land hardest)

---

## Core Evaluation Framework

### Scoring Dimensions

Each deliverable is evaluated on three primary dimensions:

#### 1. **Punchline Clarity** (Does the joke land or confuse?)
- Scale: 1-10
- **1-3 (Fails):** Punchline is buried, ambiguous, or requires explanation
- **4-6 (Partial):** Punchline is clear but not surprising; reader sees it coming
- **7-8 (Good):** Punchline lands clearly; reader doesn't predict it until the end
- **9-10 (Excellent):** Punchline reframes everything; reader gasps/groans/laughs

**Evaluation Questions:**
- Is the punchline in the final statement (visual caption, final sentence, final 3 seconds)?
- Can I understand the joke without explanation?
- Did I predict the punchline before it arrived?
- Would a complete stranger get it?

#### 2. **Originality** (Is this fresh or recycled?)
- Scale: 1-10
- **1-3 (Fails):** Generic trope (relatable millennial, bad bosses, airline food)
- **4-6 (Partial):** Specific but familiar format (news satire, corporate memo)
- **7-8 (Good):** Specific angle on a familiar topic (game cosmetics as financial product)
- **9-10 (Excellent):** Genuinely fresh juxtaposition (matchmaking algorithm = dating app exploiting dysfunction)

**Evaluation Questions:**
- Have I seen this joke/format before?
- Is it grounded in generic anxiety or specific structural contradiction?
- Does it avoid relatable millennial tropes?
- Is the institutional target clear and non-obvious?

#### 3. **Laugh Likelihood** (Would people actually laugh/groan?)
- Scale: 1-10
- **1-3 (Fails):** No emotional response; misses the moment
- **4-6 (Partial):** Smile-generating (cute joke) but not laugh-generating
- **7-8 (Good):** Gets an audible laugh or groan from most audiences
- **9-10 (Excellent):** The kind of joke people repeat; genuine "oh my god" moment

**Evaluation Questions:**
- Did this make me want to laugh out loud?
- Would I repeat this joke to someone else?
- Is there a moment of genuine recognition + absurdity?
- Does the emotional escalation feel earned?

### Secondary Metrics

#### Format Adherence
- **Visual:** Does it look like Far Side / mad Magazine / comic?
- **Written:** Does voice stay consistent (Onion deadpan, Playboy conversational)?
- **Spoken:** Does pacing/audio work for the format (TikTok hook, Jon Stewart timing)?

#### Specificity
- Does it use actual product names (not "a cosmetic" but "Valorant Sheriff")?
- Does it reference real financial numbers or documented practices?
- Or does it accurately note itself as "representative example"?

#### Institutional Target
- Is it punching up (at power structures) or down (at victims)?
- Is the contradiction between institutional claim and reality visible?
- Is the target institution clear?

#### Emotional Honesty
- Does the joke acknowledge real human consequence?
- Does it avoid cruelty toward affected people?
- Does it show institutional indifference, not individual incompetence?

---

## Deliberative-Refinement Council (10/3/1 ISO)

### Council Members (10 Comedy Experts)

1. **Gary Larson** (The Far Side) — Master of visual absurdism, anthropomorphic humor, minimal text
2. **Dave Chappelle** — Deep structural critique, fearless institutional deconstruction, power dynamics
3. **Jon Stewart** — Exposing hypocrisy, deadpan institutional voice, escalation of absurdity
4. **Hannah Gadsby** — Intellectual precision, deconstructing comedic form, unexpected punchlines
5. **James Acaster** — Narrative complexity, emotional honesty, escalating absurdity
6. **Bo Burnham** — Meta-comedy, system critique, multimedia integration
7. **Maria Bamford** — Vulnerability as comedy, institutional critique (systems), psychological honesty
8. **Patton Oswalt** — Genre expertise, hyperspecific details, insider knowledge
9. **Tig Notaro** — Deadpan observation, minimal delivery maximum impact, systemic insight
10. **The Onion Writers Collective** — Institutional satire perfection, hyperspecific structural comedy

### Evaluation Process (3 Rounds)

#### Round 1: Initial Scoring
- Each of the 10 experts independently scores the deliverable (1-10) on:
  - Punchline Clarity
  - Originality
  - Laugh Likelihood
  - Format Adherence
  - Specificity
  - Institutional Target
  - Emotional Honesty

- **Output:** 10 individual scorecards + initial failure mode identification
- **Aggregate:** Average score per dimension, variance analysis

#### Web Search (Between Round 1 & 2)
- **Search Query:** Topic-specific comedy mechanics (e.g., "punchline psychology," "satire structure," "why dark humor works")
- **Purpose:** Ground evaluators in research-backed comedy theory
- **Output:** Key findings on what makes comedy effective in [this format/topic]

#### Round 2: Deliberation & Refinement
- Council reviews Round 1 scores and failure modes
- Discuss where consensus breaks down (high variance = format-dependent humor, controversial comedy)
- Revisit initial scores based on research findings
- **Output:** Refined individual scores + specific feedback per evaluator

#### Round 3: Final Consensus & Recommendations
- Generate synthetic consensus score
- Identify 3 specific failure modes to address
- Recommend 3 specific improvements (punchline rewording, specificity addition, escalation clarity)
- Note which dimensions improved most between rounds
- Rate likelihood that feedback will improve the deliverable on next iteration

---

## Failure Mode Taxonomy

Based on deliberative-refinement findings, categorize specific problems:

### Clarity Failures
- **Punchline buried:** Joke payoff happens mid-piece; explanation follows
  - Fix: Move punchline to final statement; delete everything after
- **Setup unclear:** Reader doesn't understand context for punchline
  - Fix: Add one sentence clarifying the premise
- **Escalation invisible:** Visual or narrative progression doesn't build
  - Fix: Add intermediate step or visual transition

### Originality Failures
- **Generic institutional trope:** "Bad boss," "evil corporation," "incompetent government"
  - Fix: Replace with specific, documented institutional practice
- **Relatable millennial humor:** No structural insight, just relatability
  - Fix: Ground in modern structural anxiety (financialization, surveillance, algorithmic degradation)
- **Format-only novelty:** Novel format but joke doesn't use it
  - Fix: Ensure format enhances joke (not just contains it)

### Laugh-Likelihood Failures
- **Too intellectual:** Requires too much context; misses emotional moment
  - Fix: Add one moment of visceral recognition or absurdity
- **Smile-level not laugh-level:** Cute joke but not genuinely funny
  - Fix: Increase emotional stakes or absurdity; sharpen punchline
- **Timing off (video):** Punchline arrives too early or too late
  - Fix: Adjust escalation pace; ensure final 3 seconds are payload

### Format Adherence Failures
- **Voice inconsistency:** Shifts tone mid-piece (deadpan → preachy)
  - Fix: Maintain single institutional voice throughout
- **Format underutilized:** Could work in any format (not this one specifically)
  - Fix: Add format-specific element (visual detail for Far Side, conversational rhythm for Playboy)
- **Format overloaded:** Too much happening in one format (TikTok with 5 scene changes)
  - Fix: Simplify; let each element breathe

### Specificity Failures
- **Generic product description:** "A video game cosmetic" instead of "Valorant's Sheriff skin"
  - Fix: Name the actual product; include actual financial number
- **Vague institutional claim:** "Games are broken" instead of documented problem
  - Fix: Reference actual practice (patent, earnings call, documented behavior)
- **Hypothetical without context:** Invented example with no "representative of real pattern" note
  - Fix: Note that example mirrors actual documented practices

### Target Clarity Failures
- **Punching down:** Mocking affected people instead of institutional negligence
  - Fix: Shift focus to institution's design/incentive, not person's response
- **Target unclear:** Audience doesn't know who the joke is about
  - Fix: Make institution visibly clear (name studio, reference specific policy, show authority figure)
- **Multiple targets competing:** Confusion about whether this mocks players, devs, or institution
  - Fix: Narrow target to ONE institutional contradiction

### Emotional Honesty Failures
- **Lacks consequence:** Purely abstract criticism, no human impact
  - Fix: Show one character's emotional reaction to institutional harm
- **Cruel tone:** Mocks vulnerable people for being affected
  - Fix: Redirect mockery to institutional design, not response
- **Too dark:** Lands as cruelty rather than systemic critique
  - Fix: Include one moment showing why this matters to real people

---

## Scoring Outputs

### Individual Scorecard (Per Evaluator)
```
EVALUATOR: [Name]
DELIVERABLE: [Title/ID]
FORMAT: [far-side / playboy-joke / tiktok]

SCORES:
├─ Punchline Clarity: [1-10]
├─ Originality: [1-10]
├─ Laugh Likelihood: [1-10]
├─ Format Adherence: [1-10]
├─ Specificity: [1-10]
├─ Institutional Target: [1-10]
├─ Emotional Honesty: [1-10]
└─ OVERALL: [average]

NOTES: [2-3 sentence evaluation]

FAILURE MODES IDENTIFIED:
├─ [Mode 1: category + description]
├─ [Mode 2: category + description]
└─ [Mode 3: category + description]

CONFIDENCE IN SCORE: [High / Medium / Low]
(High = straightforward evaluation; Low = format/topic divisive)
```

### Aggregate Council Scorecard
```
DELIVERABLE: [Title/ID]
FORMAT: [far-side / playboy-joke / tiktok]

DIMENSION SCORES:
├─ Punchline Clarity: [6.2/10] (σ=1.4, range: 4-8)
├─ Originality: [6.8/10] (σ=1.1, range: 5-8)
├─ Laugh Likelihood: [6.5/10] (σ=1.6, range: 4-9)
├─ Format Adherence: [7.1/10] (σ=0.9, range: 6-8)
├─ Specificity: [7.2/10] (σ=1.2, range: 5-9)
├─ Institutional Target: [6.9/10] (σ=1.3, range: 5-8)
├─ Emotional Honesty: [6.4/10] (σ=1.5, range: 4-8)
└─ OVERALL CONSENSUS SCORE: [6.8/10]

VARIANCE ANALYSIS:
- High variance (σ>1.3): Laugh-likelihood, Emotional Honesty
  (Interpretation: Format-dependent or divisive comedy; works for some audiences, not others)
- Low variance (σ<1.0): Format Adherence
  (Interpretation: Clear consensus on format execution)

TOP FAILURE MODES (By Frequency):
├─ Punchline buried (6/10 evaluators flagged)
├─ Generic institutional anxiety (5/10 evaluators flagged)
├─ Emotional honesty weak (4/10 evaluators flagged)

ROUND 1 → ROUND 2 IMPROVEMENT:
├─ Punchline Clarity: 6.2 → 6.5 (+0.3)
├─ Originality: 6.8 → 7.1 (+0.3)
├─ Laugh Likelihood: 6.5 → 6.8 (+0.3)
└─ Overall: 6.8 → 6.95 (+0.15)

ROUND 2 → ROUND 3 IMPROVEMENT:
├─ Punchline Clarity: 6.5 → 6.7 (+0.2)
├─ Originality: 7.1 → 7.2 (+0.1)
├─ Laugh Likelihood: 6.8 → 7.0 (+0.2)
└─ Overall: 6.95 → 7.00 (+0.05)

ROUND 3 FINAL CONSENSUS SCORE: [7.0/10]
```

### Actionable Feedback (Round 3 Output)
```
DELIVERABLE: [Title/ID]
FINAL SCORE: [7.0/10]

TOP 3 FAILURE MODES & FIXES:

1. PUNCHLINE PLACEMENT (Clarity Score: 6.7/10)
   Problem: Punchline buried in middle; explanation follows
   Why It Matters: Audience sees payoff too early; final statement feels anticlimactic
   Specific Fix: Move "The game owns them. I'm renting visibility." to final sentence; delete everything after
   Expected Impact: +0.5 points on Punchline Clarity

2. GENERIC INSTITUTIONAL ANXIETY (Originality Score: 7.2/10)
   Problem: "Players spend money on cosmetics that expire" — this is obvious
   Why It Matters: Lacks the specific structural contradiction that makes satire sharp
   Specific Fix: Replace with specific detail: "Valorant's Sheriff skin: $20, expires after season, zero refund, no resale"
   Expected Impact: +0.4 points on Originality

3. EMOTIONAL HONESTY (Laugh-Likelihood Score: 7.0/10)
   Problem: Joke lacks human consequence; feels abstract
   Why It Matters: Audience doesn't feel institutional indifference; lands as mild complaint
   Specific Fix: Add one moment showing beginner's actual response (devastation, rage-quit, addiction to "getting better")
   Expected Impact: +0.3 points on Laugh-Likelihood

PROJECTED NEXT ITERATION SCORE: [7.5-7.8/10]
(Based on estimated 0.3-0.5 point improvement per major failure mode addressed)

COUNCIL CONSENSUS:
"Strong concept grounded in real institutional practice. Execution is technically sound but misses emotional moment.
Format adherence is excellent. With punchline repositioning and specificity increase, this moves from 'good' to 'sharp.'"

RECOMMENDED ITERATION PRIORITY:
1. [Failure Mode 1] (highest impact on score)
2. [Failure Mode 2] (addresses multiple dimensions)
3. [Failure Mode 3] (specificity/emotional resonance)
```

---

## Usage

### Command Invocation
```bash
/is-it-funny-refinement \
  deliverable-id="far-side-panel-1" \
  format="far-side" \
  evaluation-focus="punchline-clarity,originality,laugh-likelihood" \
  iteration=1 \
  output=full-report
```

### Parameters
- **deliverable-id** — Unique ID for the satirical piece (e.g., "far-side-1", "playboy-2")
- **format** — `far-side`, `playboy-joke`, `tiktok`, `onion-article`, `jon-stewart-script`
- **evaluation-focus** — Comma-separated; default is all 7 dimensions
- **iteration** — Which round of refinement (1 = baseline, 2+ = refined)
- **output** — `quick-score` (1 number), `detailed-report` (full analysis), `full-report` (Round 1-3 consensus)

### Output Format
```
Deliverable: [Title]
Format: [Format Type]

ROUND 1 SCORES: [Per evaluator + aggregate]
WEB SEARCH: [Key findings on topic/format]
ROUND 2 REFINEMENT: [Revised scores + deliberation notes]
ROUND 3 CONSENSUS: [Final score + actionable feedback]

TOP FAILURE MODES & RECOMMENDED FIXES:
1. [Mode + specific fix]
2. [Mode + specific fix]
3. [Mode + specific fix]

PROJECTED IMPROVEMENT (If fixes applied): +0.X points
```

---

## Interpretation Guide

### Score Meanings
- **5.0-6.0:** Needs significant work; multiple failure modes present
- **6.1-7.0:** Good foundation; 1-2 critical fixes needed
- **7.1-8.0:** Strong piece; refinement addressing minor issues
- **8.1-9.0:** Excellent; ready for release with minor polish
- **9.0+:** Exceptional; rare even from skilled comedians

### Variance Interpretation
- **High variance (σ>1.3):** Divisive humor; works for some audiences but not others
  - Implication: Format-dependent (TikTok might hit different than Far Side)
  - Or: Requires specific knowledge to understand (insider humor, niche reference)
  - Action: Don't assume low score means bad; check whether it's divisive or actually broken

- **Low variance (σ<1.0):** Clear consensus
  - Implication: Straightforward humor quality (everyone agrees it works or doesn't)
  - Action: Trust the aggregate score

### Improvement Rate
- **+0.3+ between rounds:** Genuine progress; keep iterating
- **+0.1-0.2 between rounds:** Diminishing returns; consider whether further iteration helps
- **<0.1 between rounds:** Likely hitting format ceiling; move on or rethink approach

---

## Integration with Skill Updates

After evaluating multiple deliverables (9+ pieces in a refinement cycle), look for patterns:

### Pattern: Punchline Clarity Issues Across 5+ Deliverables
→ Update `create-satire` skill with section: "Punchline Placement (Critical)"
→ Add: "MUST be in final 3 words; delete everything after"
→ Add checklist item for next generation

### Pattern: Originality Failures (Generic Anxiety)
→ Update skill with "Structural Anxiety Mapping" section
→ Add: Concrete examples of WRONG (generic) vs. RIGHT (specific structural contradiction)
→ Add: Reference to modern structural anxieties (financialization, algorithmic degradation)

### Pattern: Format Adherence Weak
→ Update skill with format-specific rules
→ Add: Checklist to catch voice inconsistency
→ Add: Examples of what authentic voice sounds like

---

## When to Use This Skill

✅ **Good times to evaluate:**
- After generating deliverables from `create-satire` (baseline scoring)
- Between refinement iterations (tracking improvement)
- When skill updates need validation (test new guidelines)
- When unsure if deliverable is "actually funny" vs. "technically correct"
- When building metrics for comparative analysis (which formats work best?)

❌ **When NOT to use:**
- If you need immediate content (evaluation takes 15-20 min)
- If you're not planning to iterate based on feedback (evaluation is only useful for improvement)
- For non-satirical content (this skill is comedy-specific)

---

## FAQ

**Q: Why 10 evaluators? Why not just one?**
A: Comedy is divisive. High variance (disagreement) is *valuable information*. If 5 evaluators score 8/10 and 5 score 4/10, that tells you it's format-dependent or controversial—important to know before iterating.

**Q: What if I disagree with the council's feedback?**
A: Trust your instinct if you have strong reasoning. But note: if the council consensus is low, check whether it's genuinely broken (punchline clarity) or divisive (some audiences will love it).

**Q: Can I evaluate non-satirical content?**
A: No. This skill is optimized for satire evaluation (institutional critique, punchline-based humor). For other comedy types, create a specialized evaluator.

**Q: Do I have to do all 3 rounds?**
A: No. Use Round 1 for quick baseline, Rounds 2-3 for detailed improvement. If Round 1 score is 7.5+, consider it "good enough" and skip further rounds.

**Q: How do I know when to stop iterating?**
A: Stop when:
- Score plateaus (<0.25 improvement between rounds)
- Improving one dimension breaks another
- You've made 2-3 rounds of fixes
- Returns diminish (effort vs. improvement ratio)

**Q: Can I use this for formats other than Far Side / Playboy / TikTok?**
A: Yes, the evaluation dimensions (clarity, originality, laugh-likelihood) are universal. But the council will optimize for formats they know. For novel formats, note in feedback.

---

## Related Skills
- `create-satire` — Generate satirical content; update based on evaluation feedback
- `refine-satire-iteratively` — Workflow that uses create-satire + is-it-funny-refinement in loops
- `deliberative-refinement` — Core 10/3/1 ISO council process

---

**Last Updated:** 2024-03-19
**Maintained By:** Comedy Evaluation Team
**Version:** 1.0 (Deliberative-Refinement Validated)


# Is It Funny Refinement Skill

**Comedy Quality Evaluator**

Assess whether satirical content actually lands as funny using deliberative-refinement (10-person comedy expert council, 3 rounds of evaluation, 1 web search between rounds). Produces actionable feedback and numerical scores for iterative improvement.

---

## Purpose

This skill is used to **measure whether satire is actually funny**, not whether it's technically correct. Use it to:

1. **Score baseline comedy quality** before iterating
2. **Identify specific failure modes** (punchline clarity, originality issues, laugh likelihood problems)
3. **Track improvement** across refinement iterations
4. **Generate actionable feedback** for skill updates
5. **Build metrics** for comparative analysis (what formats work best, what subjects land hardest)

---

## Core Evaluation Framework

### Scoring Dimensions

Each deliverable is evaluated on three primary dimensions:

#### 1. **Punchline Clarity** (Does the joke land or confuse?)
- Scale: 1-10
- **1-3 (Fails):** Punchline is buried, ambiguous, or requires explanation
- **4-6 (Partial):** Punchline is clear but not surprising; reader sees it coming
- **7-8 (Good):** Punchline lands clearly; reader doesn't predict it until the end
- **9-10 (Excellent):** Punchline reframes everything; reader gasps/groans/laughs

**Evaluation Questions:**
- Is the punchline in the final statement (visual caption, final sentence, final 3 seconds)?
- Can I understand the joke without explanation?
- Did I predict the punchline before it arrived?
- Would a complete stranger get it?

#### 2. **Originality** (Is this fresh or recycled?)
- Scale: 1-10
- **1-3 (Fails):** Generic trope (relatable millennial, bad bosses, airline food)
- **4-6 (Partial):** Specific but familiar format (news satire, corporate memo)
- **7-8 (Good):** Specific angle on a familiar topic (game cosmetics as financial product)
- **9-10 (Excellent):** Genuinely fresh juxtaposition (matchmaking algorithm = dating app exploiting dysfunction)

**Evaluation Questions:**
- Have I seen this joke/format before?
- Is it grounded in generic anxiety or specific structural contradiction?
- Does it avoid relatable millennial tropes?
- Is the institutional target clear and non-obvious?

#### 3. **Laugh Likelihood** (Would people actually laugh/groan?)
- Scale: 1-10
- **1-3 (Fails):** No emotional response; misses the moment
- **4-6 (Partial):** Smile-generating (cute joke) but not laugh-generating
- **7-8 (Good):** Gets an audible laugh or groan from most audiences
- **9-10 (Excellent):** The kind of joke people repeat; genuine "oh my god" moment

**Evaluation Questions:**
- Did this make me want to laugh out loud?
- Would I repeat this joke to someone else?
- Is there a moment of genuine recognition + absurdity?
- Does the emotional escalation feel earned?

### Secondary Metrics

#### Format Adherence
- **Visual:** Does it look like Far Side / mad Magazine / comic?
- **Written:** Does voice stay consistent (Onion deadpan, Playboy conversational)?
- **Spoken:** Does pacing/audio work for the format (TikTok hook, Jon Stewart timing)?

#### Specificity
- Does it use actual product names (not "a cosmetic" but "Valorant Sheriff")?
- Does it reference real financial numbers or documented practices?
- Or does it accurately note itself as "representative example"?

#### Institutional Target
- Is it punching up (at power structures) or down (at victims)?
- Is the contradiction between institutional claim and reality visible?
- Is the target institution clear?

#### Emotional Honesty
- Does the joke acknowledge real human consequence?
- Does it avoid cruelty toward affected people?
- Does it show institutional indifference, not individual incompetence?

---

## Deliberative-Refinement Council (10/3/1 ISO)

### Council Members (10 Comedy Experts)

1. **Gary Larson** (The Far Side) — Master of visual absurdism, anthropomorphic humor, minimal text
2. **Dave Chappelle** — Deep structural critique, fearless institutional deconstruction, power dynamics
3. **Jon Stewart** — Exposing hypocrisy, deadpan institutional voice, escalation of absurdity
4. **Hannah Gadsby** — Intellectual precision, deconstructing comedic form, unexpected punchlines
5. **James Acaster** — Narrative complexity, emotional honesty, escalating absurdity
6. **Bo Burnham** — Meta-comedy, system critique, multimedia integration
7. **Maria Bamford** — Vulnerability as comedy, institutional critique (systems), psychological honesty
8. **Patton Oswalt** — Genre expertise, hyperspecific details, insider knowledge
9. **Tig Notaro** — Deadpan observation, minimal delivery maximum impact, systemic insight
10. **The Onion Writers Collective** — Institutional satire perfection, hyperspecific structural comedy

### Evaluation Process (3 Rounds)

#### Round 1: Initial Scoring
- Each of the 10 experts independently scores the deliverable (1-10) on:
  - Punchline Clarity
  - Originality
  - Laugh Likelihood
  - Format Adherence
  - Specificity
  - Institutional Target
  - Emotional Honesty

- **Output:** 10 individual scorecards + initial failure mode identification
- **Aggregate:** Average score per dimension, variance analysis

#### Web Search (Between Round 1 & 2)
- **Search Query:** Topic-specific comedy mechanics (e.g., "punchline psychology," "satire structure," "why dark humor works")
- **Purpose:** Ground evaluators in research-backed comedy theory
- **Output:** Key findings on what makes comedy effective in [this format/topic]

#### Round 2: Deliberation & Refinement
- Council reviews Round 1 scores and failure modes
- Discuss where consensus breaks down (high variance = format-dependent humor, controversial comedy)
- Revisit initial scores based on research findings
- **Output:** Refined individual scores + specific feedback per evaluator

#### Round 3: Final Consensus & Recommendations
- Generate synthetic consensus score
- Identify 3 specific failure modes to address
- Recommend 3 specific improvements (punchline rewording, specificity addition, escalation clarity)
- Note which dimensions improved most between rounds
- Rate likelihood that feedback will improve the deliverable on next iteration

---

## Failure Mode Taxonomy

Based on deliberative-refinement findings, categorize specific problems:

### Clarity Failures
- **Punchline buried:** Joke payoff happens mid-piece; explanation follows
  - Fix: Move punchline to final statement; delete everything after
- **Setup unclear:** Reader doesn't understand context for punchline
  - Fix: Add one sentence clarifying the premise
- **Escalation invisible:** Visual or narrative progression doesn't build
  - Fix: Add intermediate step or visual transition

### Originality Failures
- **Generic institutional trope:** "Bad boss," "evil corporation," "incompetent government"
  - Fix: Replace with specific, documented institutional practice
- **Relatable millennial humor:** No structural insight, just relatability
  - Fix: Ground in modern structural anxiety (financialization, surveillance, algorithmic degradation)
- **Format-only novelty:** Novel format but joke doesn't use it
  - Fix: Ensure format enhances joke (not just contains it)

### Laugh-Likelihood Failures
- **Too intellectual:** Requires too much context; misses emotional moment
  - Fix: Add one moment of visceral recognition or absurdity
- **Smile-level not laugh-level:** Cute joke but not genuinely funny
  - Fix: Increase emotional stakes or absurdity; sharpen punchline
- **Timing off (video):** Punchline arrives too early or too late
  - Fix: Adjust escalation pace; ensure final 3 seconds are payload

### Format Adherence Failures
- **Voice inconsistency:** Shifts tone mid-piece (deadpan → preachy)
  - Fix: Maintain single institutional voice throughout
- **Format underutilized:** Could work in any format (not this one specifically)
  - Fix: Add format-specific element (visual detail for Far Side, conversational rhythm for Playboy)
- **Format overloaded:** Too much happening in one format (TikTok with 5 scene changes)
  - Fix: Simplify; let each element breathe

### Specificity Failures
- **Generic product description:** "A video game cosmetic" instead of "Valorant's Sheriff skin"
  - Fix: Name the actual product; include actual financial number
- **Vague institutional claim:** "Games are broken" instead of documented problem
  - Fix: Reference actual practice (patent, earnings call, documented behavior)
- **Hypothetical without context:** Invented example with no "representative of real pattern" note
  - Fix: Note that example mirrors actual documented practices

### Target Clarity Failures
- **Punching down:** Mocking affected people instead of institutional negligence
  - Fix: Shift focus to institution's design/incentive, not person's response
- **Target unclear:** Audience doesn't know who the joke is about
  - Fix: Make institution visibly clear (name studio, reference specific policy, show authority figure)
- **Multiple targets competing:** Confusion about whether this mocks players, devs, or institution
  - Fix: Narrow target to ONE institutional contradiction

### Emotional Honesty Failures
- **Lacks consequence:** Purely abstract criticism, no human impact
  - Fix: Show one character's emotional reaction to institutional harm
- **Cruel tone:** Mocks vulnerable people for being affected
  - Fix: Redirect mockery to institutional design, not response
- **Too dark:** Lands as cruelty rather than systemic critique
  - Fix: Include one moment showing why this matters to real people

---

## Scoring Outputs

### Individual Scorecard (Per Evaluator)
```
EVALUATOR: [Name]
DELIVERABLE: [Title/ID]
FORMAT: [far-side / playboy-joke / tiktok]

SCORES:
├─ Punchline Clarity: [1-10]
├─ Originality: [1-10]
├─ Laugh Likelihood: [1-10]
├─ Format Adherence: [1-10]
├─ Specificity: [1-10]
├─ Institutional Target: [1-10]
├─ Emotional Honesty: [1-10]
└─ OVERALL: [average]

NOTES: [2-3 sentence evaluation]

FAILURE MODES IDENTIFIED:
├─ [Mode 1: category + description]
├─ [Mode 2: category + description]
└─ [Mode 3: category + description]

CONFIDENCE IN SCORE: [High / Medium / Low]
(High = straightforward evaluation; Low = format/topic divisive)
```

### Aggregate Council Scorecard
```
DELIVERABLE: [Title/ID]
FORMAT: [far-side / playboy-joke / tiktok]

DIMENSION SCORES:
├─ Punchline Clarity: [6.2/10] (σ=1.4, range: 4-8)
├─ Originality: [6.8/10] (σ=1.1, range: 5-8)
├─ Laugh Likelihood: [6.5/10] (σ=1.6, range: 4-9)
├─ Format Adherence: [7.1/10] (σ=0.9, range: 6-8)
├─ Specificity: [7.2/10] (σ=1.2, range: 5-9)
├─ Institutional Target: [6.9/10] (σ=1.3, range: 5-8)
├─ Emotional Honesty: [6.4/10] (σ=1.5, range: 4-8)
└─ OVERALL CONSENSUS SCORE: [6.8/10]

VARIANCE ANALYSIS:
- High variance (σ>1.3): Laugh-likelihood, Emotional Honesty
  (Interpretation: Format-dependent or divisive comedy; works for some audiences, not others)
- Low variance (σ<1.0): Format Adherence
  (Interpretation: Clear consensus on format execution)

TOP FAILURE MODES (By Frequency):
├─ Punchline buried (6/10 evaluators flagged)
├─ Generic institutional anxiety (5/10 evaluators flagged)
├─ Emotional honesty weak (4/10 evaluators flagged)

ROUND 1 → ROUND 2 IMPROVEMENT:
├─ Punchline Clarity: 6.2 → 6.5 (+0.3)
├─ Originality: 6.8 → 7.1 (+0.3)
├─ Laugh Likelihood: 6.5 → 6.8 (+0.3)
└─ Overall: 6.8 → 6.95 (+0.15)

ROUND 2 → ROUND 3 IMPROVEMENT:
├─ Punchline Clarity: 6.5 → 6.7 (+0.2)
├─ Originality: 7.1 → 7.2 (+0.1)
├─ Laugh Likelihood: 6.8 → 7.0 (+0.2)
└─ Overall: 6.95 → 7.00 (+0.05)

ROUND 3 FINAL CONSENSUS SCORE: [7.0/10]
```

### Actionable Feedback (Round 3 Output)
```
DELIVERABLE: [Title/ID]
FINAL SCORE: [7.0/10]

TOP 3 FAILURE MODES & FIXES:

1. PUNCHLINE PLACEMENT (Clarity Score: 6.7/10)
   Problem: Punchline buried in middle; explanation follows
   Why It Matters: Audience sees payoff too early; final statement feels anticlimactic
   Specific Fix: Move "The game owns them. I'm renting visibility." to final sentence; delete everything after
   Expected Impact: +0.5 points on Punchline Clarity

2. GENERIC INSTITUTIONAL ANXIETY (Originality Score: 7.2/10)
   Problem: "Players spend money on cosmetics that expire" — this is obvious
   Why It Matters: Lacks the specific structural contradiction that makes satire sharp
   Specific Fix: Replace with specific detail: "Valorant's Sheriff skin: $20, expires after season, zero refund, no resale"
   Expected Impact: +0.4 points on Originality

3. EMOTIONAL HONESTY (Laugh-Likelihood Score: 7.0/10)
   Problem: Joke lacks human consequence; feels abstract
   Why It Matters: Audience doesn't feel institutional indifference; lands as mild complaint
   Specific Fix: Add one moment showing beginner's actual response (devastation, rage-quit, addiction to "getting better")
   Expected Impact: +0.3 points on Laugh-Likelihood

PROJECTED NEXT ITERATION SCORE: [7.5-7.8/10]
(Based on estimated 0.3-0.5 point improvement per major failure mode addressed)

COUNCIL CONSENSUS:
"Strong concept grounded in real institutional practice. Execution is technically sound but misses emotional moment.
Format adherence is excellent. With punchline repositioning and specificity increase, this moves from 'good' to 'sharp.'"

RECOMMENDED ITERATION PRIORITY:
1. [Failure Mode 1] (highest impact on score)
2. [Failure Mode 2] (addresses multiple dimensions)
3. [Failure Mode 3] (specificity/emotional resonance)
```

---

## Usage

### Command Invocation
```bash
/is-it-funny-refinement \
  deliverable-id="far-side-panel-1" \
  format="far-side" \
  evaluation-focus="punchline-clarity,originality,laugh-likelihood" \
  iteration=1 \
  output=full-report
```

### Parameters
- **deliverable-id** — Unique ID for the satirical piece (e.g., "far-side-1", "playboy-2")
- **format** — `far-side`, `playboy-joke`, `tiktok`, `onion-article`, `jon-stewart-script`
- **evaluation-focus** — Comma-separated; default is all 7 dimensions
- **iteration** — Which round of refinement (1 = baseline, 2+ = refined)
- **output** — `quick-score` (1 number), `detailed-report` (full analysis), `full-report` (Round 1-3 consensus)

### Output Format
```
Deliverable: [Title]
Format: [Format Type]

ROUND 1 SCORES: [Per evaluator + aggregate]
WEB SEARCH: [Key findings on topic/format]
ROUND 2 REFINEMENT: [Revised scores + deliberation notes]
ROUND 3 CONSENSUS: [Final score + actionable feedback]

TOP FAILURE MODES & RECOMMENDED FIXES:
1. [Mode + specific fix]
2. [Mode + specific fix]
3. [Mode + specific fix]

PROJECTED IMPROVEMENT (If fixes applied): +0.X points
```

---

## Interpretation Guide

### Score Meanings
- **5.0-6.0:** Needs significant work; multiple failure modes present
- **6.1-7.0:** Good foundation; 1-2 critical fixes needed
- **7.1-8.0:** Strong piece; refinement addressing minor issues
- **8.1-9.0:** Excellent; ready for release with minor polish
- **9.0+:** Exceptional; rare even from skilled comedians

### Variance Interpretation
- **High variance (σ>1.3):** Divisive humor; works for some audiences but not others
  - Implication: Format-dependent (TikTok might hit different than Far Side)
  - Or: Requires specific knowledge to understand (insider humor, niche reference)
  - Action: Don't assume low score means bad; check whether it's divisive or actually broken

- **Low variance (σ<1.0):** Clear consensus
  - Implication: Straightforward humor quality (everyone agrees it works or doesn't)
  - Action: Trust the aggregate score

### Improvement Rate
- **+0.3+ between rounds:** Genuine progress; keep iterating
- **+0.1-0.2 between rounds:** Diminishing returns; consider whether further iteration helps
- **<0.1 between rounds:** Likely hitting format ceiling; move on or rethink approach

---

## Integration with Skill Updates

After evaluating multiple deliverables (9+ pieces in a refinement cycle), look for patterns:

### Pattern: Punchline Clarity Issues Across 5+ Deliverables
→ Update `create-satire` skill with section: "Punchline Placement (Critical)"
→ Add: "MUST be in final 3 words; delete everything after"
→ Add checklist item for next generation

### Pattern: Originality Failures (Generic Anxiety)
→ Update skill with "Structural Anxiety Mapping" section
→ Add: Concrete examples of WRONG (generic) vs. RIGHT (specific structural contradiction)
→ Add: Reference to modern structural anxieties (financialization, algorithmic degradation)

### Pattern: Format Adherence Weak
→ Update skill with format-specific rules
→ Add: Checklist to catch voice inconsistency
→ Add: Examples of what authentic voice sounds like

---

## When to Use This Skill

✅ **Good times to evaluate:**
- After generating deliverables from `create-satire` (baseline scoring)
- Between refinement iterations (tracking improvement)
- When skill updates need validation (test new guidelines)
- When unsure if deliverable is "actually funny" vs. "technically correct"
- When building metrics for comparative analysis (which formats work best?)

❌ **When NOT to use:**
- If you need immediate content (evaluation takes 15-20 min)
- If you're not planning to iterate based on feedback (evaluation is only useful for improvement)
- For non-satirical content (this skill is comedy-specific)

---

## FAQ

**Q: Why 10 evaluators? Why not just one?**
A: Comedy is divisive. High variance (disagreement) is *valuable information*. If 5 evaluators score 8/10 and 5 score 4/10, that tells you it's format-dependent or controversial—important to know before iterating.

**Q: What if I disagree with the council's feedback?**
A: Trust your instinct if you have strong reasoning. But note: if the council consensus is low, check whether it's genuinely broken (punchline clarity) or divisive (some audiences will love it).

**Q: Can I evaluate non-satirical content?**
A: No. This skill is optimized for satire evaluation (institutional critique, punchline-based humor). For other comedy types, create a specialized evaluator.

**Q: Do I have to do all 3 rounds?**
A: No. Use Round 1 for quick baseline, Rounds 2-3 for detailed improvement. If Round 1 score is 7.5+, consider it "good enough" and skip further rounds.

**Q: How do I know when to stop iterating?**
A: Stop when:
- Score plateaus (<0.25 improvement between rounds)
- Improving one dimension breaks another
- You've made 2-3 rounds of fixes
- Returns diminish (effort vs. improvement ratio)

**Q: Can I use this for formats other than Far Side / Playboy / TikTok?**
A: Yes, the evaluation dimensions (clarity, originality, laugh-likelihood) are universal. But the council will optimize for formats they know. For novel formats, note in feedback.

---

## Related Skills
- `create-satire` — Generate satirical content; update based on evaluation feedback
- `refine-satire-iteratively` — Workflow that uses create-satire + is-it-funny-refinement in loops
- `deliberative-refinement` — Core 10/3/1 ISO council process

---

**Last Updated:** 2024-03-19
**Maintained By:** Comedy Evaluation Team
**Version:** 1.0 (Deliberative-Refinement Validated)


# Is It Funny Refinement Skill

**Comedy Quality Evaluator**

Assess whether satirical content actually lands as funny using deliberative-refinement (10-person comedy expert council, 3 rounds of evaluation, 1 web search between rounds). Produces actionable feedback and numerical scores for iterative improvement.

---

## Purpose

This skill is used to **measure whether satire is actually funny**, not whether it's technically correct. Use it to:

1. **Score baseline comedy quality** before iterating
2. **Identify specific failure modes** (punchline clarity, originality issues, laugh likelihood problems)
3. **Track improvement** across refinement iterations
4. **Generate actionable feedback** for skill updates
5. **Build metrics** for comparative analysis (what formats work best, what subjects land hardest)

---

## Core Evaluation Framework

### Scoring Dimensions

Each deliverable is evaluated on three primary dimensions:

#### 1. **Punchline Clarity** (Does the joke land or confuse?)
- Scale: 1-10
- **1-3 (Fails):** Punchline is buried, ambiguous, or requires explanation
- **4-6 (Partial):** Punchline is clear but not surprising; reader sees it coming
- **7-8 (Good):** Punchline lands clearly; reader doesn't predict it until the end
- **9-10 (Excellent):** Punchline reframes everything; reader gasps/groans/laughs

**Evaluation Questions:**
- Is the punchline in the final statement (visual caption, final sentence, final 3 seconds)?
- Can I understand the joke without explanation?
- Did I predict the punchline before it arrived?
- Would a complete stranger get it?

#### 2. **Originality** (Is this fresh or recycled?)
- Scale: 1-10
- **1-3 (Fails):** Generic trope (relatable millennial, bad bosses, airline food)
- **4-6 (Partial):** Specific but familiar format (news satire, corporate memo)
- **7-8 (Good):** Specific angle on a familiar topic (game cosmetics as financial product)
- **9-10 (Excellent):** Genuinely fresh juxtaposition (matchmaking algorithm = dating app exploiting dysfunction)

**Evaluation Questions:**
- Have I seen this joke/format before?
- Is it grounded in generic anxiety or specific structural contradiction?
- Does it avoid relatable millennial tropes?
- Is the institutional target clear and non-obvious?

#### 3. **Laugh Likelihood** (Would people actually laugh/groan?)
- Scale: 1-10
- **1-3 (Fails):** No emotional response; misses the moment
- **4-6 (Partial):** Smile-generating (cute joke) but not laugh-generating
- **7-8 (Good):** Gets an audible laugh or groan from most audiences
- **9-10 (Excellent):** The kind of joke people repeat; genuine "oh my god" moment

**Evaluation Questions:**
- Did this make me want to laugh out loud?
- Would I repeat this joke to someone else?
- Is there a moment of genuine recognition + absurdity?
- Does the emotional escalation feel earned?

### Secondary Metrics

#### Format Adherence
- **Visual:** Does it look like Far Side / mad Magazine / comic?
- **Written:** Does voice stay consistent (Onion deadpan, Playboy conversational)?
- **Spoken:** Does pacing/audio work for the format (TikTok hook, Jon Stewart timing)?

#### Specificity
- Does it use actual product names (not "a cosmetic" but "Valorant Sheriff")?
- Does it reference real financial numbers or documented practices?
- Or does it accurately note itself as "representative example"?

#### Institutional Target
- Is it punching up (at power structures) or down (at victims)?
- Is the contradiction between institutional claim and reality visible?
- Is the target institution clear?

#### Emotional Honesty
- Does the joke acknowledge real human consequence?
- Does it avoid cruelty toward affected people?
- Does it show institutional indifference, not individual incompetence?

---

## Deliberative-Refinement Council (10/3/1 ISO)

### Council Members (10 Comedy Experts)

1. **Gary Larson** (The Far Side) — Master of visual absurdism, anthropomorphic humor, minimal text
2. **Dave Chappelle** — Deep structural critique, fearless institutional deconstruction, power dynamics
3. **Jon Stewart** — Exposing hypocrisy, deadpan institutional voice, escalation of absurdity
4. **Hannah Gadsby** — Intellectual precision, deconstructing comedic form, unexpected punchlines
5. **James Acaster** — Narrative complexity, emotional honesty, escalating absurdity
6. **Bo Burnham** — Meta-comedy, system critique, multimedia integration
7. **Maria Bamford** — Vulnerability as comedy, institutional critique (systems), psychological honesty
8. **Patton Oswalt** — Genre expertise, hyperspecific details, insider knowledge
9. **Tig Notaro** — Deadpan observation, minimal delivery maximum impact, systemic insight
10. **The Onion Writers Collective** — Institutional satire perfection, hyperspecific structural comedy

### Evaluation Process (3 Rounds)

#### Round 1: Initial Scoring
- Each of the 10 experts independently scores the deliverable (1-10) on:
  - Punchline Clarity
  - Originality
  - Laugh Likelihood
  - Format Adherence
  - Specificity
  - Institutional Target
  - Emotional Honesty

- **Output:** 10 individual scorecards + initial failure mode identification
- **Aggregate:** Average score per dimension, variance analysis

#### Web Search (Between Round 1 & 2)
- **Search Query:** Topic-specific comedy mechanics (e.g., "punchline psychology," "satire structure," "why dark humor works")
- **Purpose:** Ground evaluators in research-backed comedy theory
- **Output:** Key findings on what makes comedy effective in [this format/topic]

#### Round 2: Deliberation & Refinement
- Council reviews Round 1 scores and failure modes
- Discuss where consensus breaks down (high variance = format-dependent humor, controversial comedy)
- Revisit initial scores based on research findings
- **Output:** Refined individual scores + specific feedback per evaluator

#### Round 3: Final Consensus & Recommendations
- Generate synthetic consensus score
- Identify 3 specific failure modes to address
- Recommend 3 specific improvements (punchline rewording, specificity addition, escalation clarity)
- Note which dimensions improved most between rounds
- Rate likelihood that feedback will improve the deliverable on next iteration

---

## Failure Mode Taxonomy

Based on deliberative-refinement findings, categorize specific problems:

### Clarity Failures
- **Punchline buried:** Joke payoff happens mid-piece; explanation follows
  - Fix: Move punchline to final statement; delete everything after
- **Setup unclear:** Reader doesn't understand context for punchline
  - Fix: Add one sentence clarifying the premise
- **Escalation invisible:** Visual or narrative progression doesn't build
  - Fix: Add intermediate step or visual transition

### Originality Failures
- **Generic institutional trope:** "Bad boss," "evil corporation," "incompetent government"
  - Fix: Replace with specific, documented institutional practice
- **Relatable millennial humor:** No structural insight, just relatability
  - Fix: Ground in modern structural anxiety (financialization, surveillance, algorithmic degradation)
- **Format-only novelty:** Novel format but joke doesn't use it
  - Fix: Ensure format enhances joke (not just contains it)

### Laugh-Likelihood Failures
- **Too intellectual:** Requires too much context; misses emotional moment
  - Fix: Add one moment of visceral recognition or absurdity
- **Smile-level not laugh-level:** Cute joke but not genuinely funny
  - Fix: Increase emotional stakes or absurdity; sharpen punchline
- **Timing off (video):** Punchline arrives too early or too late
  - Fix: Adjust escalation pace; ensure final 3 seconds are payload

### Format Adherence Failures
- **Voice inconsistency:** Shifts tone mid-piece (deadpan → preachy)
  - Fix: Maintain single institutional voice throughout
- **Format underutilized:** Could work in any format (not this one specifically)
  - Fix: Add format-specific element (visual detail for Far Side, conversational rhythm for Playboy)
- **Format overloaded:** Too much happening in one format (TikTok with 5 scene changes)
  - Fix: Simplify; let each element breathe

### Specificity Failures
- **Generic product description:** "A video game cosmetic" instead of "Valorant's Sheriff skin"
  - Fix: Name the actual product; include actual financial number
- **Vague institutional claim:** "Games are broken" instead of documented problem
  - Fix: Reference actual practice (patent, earnings call, documented behavior)
- **Hypothetical without context:** Invented example with no "representative of real pattern" note
  - Fix: Note that example mirrors actual documented practices

### Target Clarity Failures
- **Punching down:** Mocking affected people instead of institutional negligence
  - Fix: Shift focus to institution's design/incentive, not person's response
- **Target unclear:** Audience doesn't know who the joke is about
  - Fix: Make institution visibly clear (name studio, reference specific policy, show authority figure)
- **Multiple targets competing:** Confusion about whether this mocks players, devs, or institution
  - Fix: Narrow target to ONE institutional contradiction

### Emotional Honesty Failures
- **Lacks consequence:** Purely abstract criticism, no human impact
  - Fix: Show one character's emotional reaction to institutional harm
- **Cruel tone:** Mocks vulnerable people for being affected
  - Fix: Redirect mockery to institutional design, not response
- **Too dark:** Lands as cruelty rather than systemic critique
  - Fix: Include one moment showing why this matters to real people

---

## Scoring Outputs

### Individual Scorecard (Per Evaluator)
```
EVALUATOR: [Name]
DELIVERABLE: [Title/ID]
FORMAT: [far-side / playboy-joke / tiktok]

SCORES:
├─ Punchline Clarity: [1-10]
├─ Originality: [1-10]
├─ Laugh Likelihood: [1-10]
├─ Format Adherence: [1-10]
├─ Specificity: [1-10]
├─ Institutional Target: [1-10]
├─ Emotional Honesty: [1-10]
└─ OVERALL: [average]

NOTES: [2-3 sentence evaluation]

FAILURE MODES IDENTIFIED:
├─ [Mode 1: category + description]
├─ [Mode 2: category + description]
└─ [Mode 3: category + description]

CONFIDENCE IN SCORE: [High / Medium / Low]
(High = straightforward evaluation; Low = format/topic divisive)
```

### Aggregate Council Scorecard
```
DELIVERABLE: [Title/ID]
FORMAT: [far-side / playboy-joke / tiktok]

DIMENSION SCORES:
├─ Punchline Clarity: [6.2/10] (σ=1.4, range: 4-8)
├─ Originality: [6.8/10] (σ=1.1, range: 5-8)
├─ Laugh Likelihood: [6.5/10] (σ=1.6, range: 4-9)
├─ Format Adherence: [7.1/10] (σ=0.9, range: 6-8)
├─ Specificity: [7.2/10] (σ=1.2, range: 5-9)
├─ Institutional Target: [6.9/10] (σ=1.3, range: 5-8)
├─ Emotional Honesty: [6.4/10] (σ=1.5, range: 4-8)
└─ OVERALL CONSENSUS SCORE: [6.8/10]

VARIANCE ANALYSIS:
- High variance (σ>1.3): Laugh-likelihood, Emotional Honesty
  (Interpretation: Format-dependent or divisive comedy; works for some audiences, not others)
- Low variance (σ<1.0): Format Adherence
  (Interpretation: Clear consensus on format execution)

TOP FAILURE MODES (By Frequency):
├─ Punchline buried (6/10 evaluators flagged)
├─ Generic institutional anxiety (5/10 evaluators flagged)
├─ Emotional honesty weak (4/10 evaluators flagged)

ROUND 1 → ROUND 2 IMPROVEMENT:
├─ Punchline Clarity: 6.2 → 6.5 (+0.3)
├─ Originality: 6.8 → 7.1 (+0.3)
├─ Laugh Likelihood: 6.5 → 6.8 (+0.3)
└─ Overall: 6.8 → 6.95 (+0.15)

ROUND 2 → ROUND 3 IMPROVEMENT:
├─ Punchline Clarity: 6.5 → 6.7 (+0.2)
├─ Originality: 7.1 → 7.2 (+0.1)
├─ Laugh Likelihood: 6.8 → 7.0 (+0.2)
└─ Overall: 6.95 → 7.00 (+0.05)

ROUND 3 FINAL CONSENSUS SCORE: [7.0/10]
```

### Actionable Feedback (Round 3 Output)
```
DELIVERABLE: [Title/ID]
FINAL SCORE: [7.0/10]

TOP 3 FAILURE MODES & FIXES:

1. PUNCHLINE PLACEMENT (Clarity Score: 6.7/10)
   Problem: Punchline buried in middle; explanation follows
   Why It Matters: Audience sees payoff too early; final statement feels anticlimactic
   Specific Fix: Move "The game owns them. I'm renting visibility." to final sentence; delete everything after
   Expected Impact: +0.5 points on Punchline Clarity

2. GENERIC INSTITUTIONAL ANXIETY (Originality Score: 7.2/10)
   Problem: "Players spend money on cosmetics that expire" — this is obvious
   Why It Matters: Lacks the specific structural contradiction that makes satire sharp
   Specific Fix: Replace with specific detail: "Valorant's Sheriff skin: $20, expires after season, zero refund, no resale"
   Expected Impact: +0.4 points on Originality

3. EMOTIONAL HONESTY (Laugh-Likelihood Score: 7.0/10)
   Problem: Joke lacks human consequence; feels abstract
   Why It Matters: Audience doesn't feel institutional indifference; lands as mild complaint
   Specific Fix: Add one moment showing beginner's actual response (devastation, rage-quit, addiction to "getting better")
   Expected Impact: +0.3 points on Laugh-Likelihood

PROJECTED NEXT ITERATION SCORE: [7.5-7.8/10]
(Based on estimated 0.3-0.5 point improvement per major failure mode addressed)

COUNCIL CONSENSUS:
"Strong concept grounded in real institutional practice. Execution is technically sound but misses emotional moment.
Format adherence is excellent. With punchline repositioning and specificity increase, this moves from 'good' to 'sharp.'"

RECOMMENDED ITERATION PRIORITY:
1. [Failure Mode 1] (highest impact on score)
2. [Failure Mode 2] (addresses multiple dimensions)
3. [Failure Mode 3] (specificity/emotional resonance)
```

---

## Usage

### Command Invocation
```bash
/is-it-funny-refinement \
  deliverable-id="far-side-panel-1" \
  format="far-side" \
  evaluation-focus="punchline-clarity,originality,laugh-likelihood" \
  iteration=1 \
  output=full-report
```

### Parameters
- **deliverable-id** — Unique ID for the satirical piece (e.g., "far-side-1", "playboy-2")
- **format** — `far-side`, `playboy-joke`, `tiktok`, `onion-article`, `jon-stewart-script`
- **evaluation-focus** — Comma-separated; default is all 7 dimensions
- **iteration** — Which round of refinement (1 = baseline, 2+ = refined)
- **output** — `quick-score` (1 number), `detailed-report` (full analysis), `full-report` (Round 1-3 consensus)

### Output Format
```
Deliverable: [Title]
Format: [Format Type]

ROUND 1 SCORES: [Per evaluator + aggregate]
WEB SEARCH: [Key findings on topic/format]
ROUND 2 REFINEMENT: [Revised scores + deliberation notes]
ROUND 3 CONSENSUS: [Final score + actionable feedback]

TOP FAILURE MODES & RECOMMENDED FIXES:
1. [Mode + specific fix]
2. [Mode + specific fix]
3. [Mode + specific fix]

PROJECTED IMPROVEMENT (If fixes applied): +0.X points
```

---

## Interpretation Guide

### Score Meanings
- **5.0-6.0:** Needs significant work; multiple failure modes present
- **6.1-7.0:** Good foundation; 1-2 critical fixes needed
- **7.1-8.0:** Strong piece; refinement addressing minor issues
- **8.1-9.0:** Excellent; ready for release with minor polish
- **9.0+:** Exceptional; rare even from skilled comedians

### Variance Interpretation
- **High variance (σ>1.3):** Divisive humor; works for some audiences but not others
  - Implication: Format-dependent (TikTok might hit different than Far Side)
  - Or: Requires specific knowledge to understand (insider humor, niche reference)
  - Action: Don't assume low score means bad; check whether it's divisive or actually broken

- **Low variance (σ<1.0):** Clear consensus
  - Implication: Straightforward humor quality (everyone agrees it works or doesn't)
  - Action: Trust the aggregate score

### Improvement Rate
- **+0.3+ between rounds:** Genuine progress; keep iterating
- **+0.1-0.2 between rounds:** Diminishing returns; consider whether further iteration helps
- **<0.1 between rounds:** Likely hitting format ceiling; move on or rethink approach

---

## Integration with Skill Updates

After evaluating multiple deliverables (9+ pieces in a refinement cycle), look for patterns:

### Pattern: Punchline Clarity Issues Across 5+ Deliverables
→ Update `create-satire` skill with section: "Punchline Placement (Critical)"
→ Add: "MUST be in final 3 words; delete everything after"
→ Add checklist item for next generation

### Pattern: Originality Failures (Generic Anxiety)
→ Update skill with "Structural Anxiety Mapping" section
→ Add: Concrete examples of WRONG (generic) vs. RIGHT (specific structural contradiction)
→ Add: Reference to modern structural anxieties (financialization, algorithmic degradation)

### Pattern: Format Adherence Weak
→ Update skill with format-specific rules
→ Add: Checklist to catch voice inconsistency
→ Add: Examples of what authentic voice sounds like

---

## When to Use This Skill

✅ **Good times to evaluate:**
- After generating deliverables from `create-satire` (baseline scoring)
- Between refinement iterations (tracking improvement)
- When skill updates need validation (test new guidelines)
- When unsure if deliverable is "actually funny" vs. "technically correct"
- When building metrics for comparative analysis (which formats work best?)

❌ **When NOT to use:**
- If you need immediate content (evaluation takes 15-20 min)
- If you're not planning to iterate based on feedback (evaluation is only useful for improvement)
- For non-satirical content (this skill is comedy-specific)

---

## FAQ

**Q: Why 10 evaluators? Why not just one?**
A: Comedy is divisive. High variance (disagreement) is *valuable information*. If 5 evaluators score 8/10 and 5 score 4/10, that tells you it's format-dependent or controversial—important to know before iterating.

**Q: What if I disagree with the council's feedback?**
A: Trust your instinct if you have strong reasoning. But note: if the council consensus is low, check whether it's genuinely broken (punchline clarity) or divisive (some audiences will love it).

**Q: Can I evaluate non-satirical content?**
A: No. This skill is optimized for satire evaluation (institutional critique, punchline-based humor). For other comedy types, create a specialized evaluator.

**Q: Do I have to do all 3 rounds?**
A: No. Use Round 1 for quick baseline, Rounds 2-3 for detailed improvement. If Round 1 score is 7.5+, consider it "good enough" and skip further rounds.

**Q: How do I know when to stop iterating?**
A: Stop when:
- Score plateaus (<0.25 improvement between rounds)
- Improving one dimension breaks another
- You've made 2-3 rounds of fixes
- Returns diminish (effort vs. improvement ratio)

**Q: Can I use this for formats other than Far Side / Playboy / TikTok?**
A: Yes, the evaluation dimensions (clarity, originality, laugh-likelihood) are universal. But the council will optimize for formats they know. For novel formats, note in feedback.

---

## Related Skills
- `create-satire` — Generate satirical content; update based on evaluation feedback
- `refine-satire-iteratively` — Workflow that uses create-satire + is-it-funny-refinement in loops
- `deliberative-refinement` — Core 10/3/1 ISO council process

---

**Last Updated:** 2024-03-19
**Maintained By:** Comedy Evaluation Team
**Version:** 1.0 (Deliberative-Refinement Validated)


# Is It Funny Refinement Skill

**Comedy Quality Evaluator**

Assess whether satirical content actually lands as funny using deliberative-refinement (10-person comedy expert council, 3 rounds of evaluation, 1 web search between rounds). Produces actionable feedback and numerical scores for iterative improvement.

---

## Purpose

This skill is used to **measure whether satire is actually funny**, not whether it's technically correct. Use it to:

1. **Score baseline comedy quality** before iterating
2. **Identify specific failure modes** (punchline clarity, originality issues, laugh likelihood problems)
3. **Track improvement** across refinement iterations
4. **Generate actionable feedback** for skill updates
5. **Build metrics** for comparative analysis (what formats work best, what subjects land hardest)

---

## Core Evaluation Framework

### Scoring Dimensions

Each deliverable is evaluated on three primary dimensions:

#### 1. **Punchline Clarity** (Does the joke land or confuse?)
- Scale: 1-10
- **1-3 (Fails):** Punchline is buried, ambiguous, or requires explanation
- **4-6 (Partial):** Punchline is clear but not surprising; reader sees it coming
- **7-8 (Good):** Punchline lands clearly; reader doesn't predict it until the end
- **9-10 (Excellent):** Punchline reframes everything; reader gasps/groans/laughs

**Evaluation Questions:**
- Is the punchline in the final statement (visual caption, final sentence, final 3 seconds)?
- Can I understand the joke without explanation?
- Did I predict the punchline before it arrived?
- Would a complete stranger get it?

#### 2. **Originality** (Is this fresh or recycled?)
- Scale: 1-10
- **1-3 (Fails):** Generic trope (relatable millennial, bad bosses, airline food)
- **4-6 (Partial):** Specific but familiar format (news satire, corporate memo)
- **7-8 (Good):** Specific angle on a familiar topic (game cosmetics as financial product)
- **9-10 (Excellent):** Genuinely fresh juxtaposition (matchmaking algorithm = dating app exploiting dysfunction)

**Evaluation Questions:**
- Have I seen this joke/format before?
- Is it grounded in generic anxiety or specific structural contradiction?
- Does it avoid relatable millennial tropes?
- Is the institutional target clear and non-obvious?

#### 3. **Laugh Likelihood** (Would people actually laugh/groan?)
- Scale: 1-10
- **1-3 (Fails):** No emotional response; misses the moment
- **4-6 (Partial):** Smile-generating (cute joke) but not laugh-generating
- **7-8 (Good):** Gets an audible laugh or groan from most audiences
- **9-10 (Excellent):** The kind of joke people repeat; genuine "oh my god" moment

**Evaluation Questions:**
- Did this make me want to laugh out loud?
- Would I repeat this joke to someone else?
- Is there a moment of genuine recognition + absurdity?
- Does the emotional escalation feel earned?

### Secondary Metrics

#### Format Adherence
- **Visual:** Does it look like Far Side / mad Magazine / comic?
- **Written:** Does voice stay consistent (Onion deadpan, Playboy conversational)?
- **Spoken:** Does pacing/audio work for the format (TikTok hook, Jon Stewart timing)?

#### Specificity
- Does it use actual product names (not "a cosmetic" but "Valorant Sheriff")?
- Does it reference real financial numbers or documented practices?
- Or does it accurately note itself as "representative example"?

#### Institutional Target
- Is it punching up (at power structures) or down (at victims)?
- Is the contradiction between institutional claim and reality visible?
- Is the target institution clear?

#### Emotional Honesty
- Does the joke acknowledge real human consequence?
- Does it avoid cruelty toward affected people?
- Does it show institutional indifference, not individual incompetence?

---

## Deliberative-Refinement Council (10/3/1 ISO)

### Council Members (10 Comedy Experts)

1. **Gary Larson** (The Far Side) — Master of visual absurdism, anthropomorphic humor, minimal text
2. **Dave Chappelle** — Deep structural critique, fearless institutional deconstruction, power dynamics
3. **Jon Stewart** — Exposing hypocrisy, deadpan institutional voice, escalation of absurdity
4. **Hannah Gadsby** — Intellectual precision, deconstructing comedic form, unexpected punchlines
5. **James Acaster** — Narrative complexity, emotional honesty, escalating absurdity
6. **Bo Burnham** — Meta-comedy, system critique, multimedia integration
7. **Maria Bamford** — Vulnerability as comedy, institutional critique (systems), psychological honesty
8. **Patton Oswalt** — Genre expertise, hyperspecific details, insider knowledge
9. **Tig Notaro** — Deadpan observation, minimal delivery maximum impact, systemic insight
10. **The Onion Writers Collective** — Institutional satire perfection, hyperspecific structural comedy

### Evaluation Process (3 Rounds)

#### Round 1: Initial Scoring
- Each of the 10 experts independently scores the deliverable (1-10) on:
  - Punchline Clarity
  - Originality
  - Laugh Likelihood
  - Format Adherence
  - Specificity
  - Institutional Target
  - Emotional Honesty

- **Output:** 10 individual scorecards + initial failure mode identification
- **Aggregate:** Average score per dimension, variance analysis

#### Web Search (Between Round 1 & 2)
- **Search Query:** Topic-specific comedy mechanics (e.g., "punchline psychology," "satire structure," "why dark humor works")
- **Purpose:** Ground evaluators in research-backed comedy theory
- **Output:** Key findings on what makes comedy effective in [this format/topic]

#### Round 2: Deliberation & Refinement
- Council reviews Round 1 scores and failure modes
- Discuss where consensus breaks down (high variance = format-dependent humor, controversial comedy)
- Revisit initial scores based on research findings
- **Output:** Refined individual scores + specific feedback per evaluator

#### Round 3: Final Consensus & Recommendations
- Generate synthetic consensus score
- Identify 3 specific failure modes to address
- Recommend 3 specific improvements (punchline rewording, specificity addition, escalation clarity)
- Note which dimensions improved most between rounds
- Rate likelihood that feedback will improve the deliverable on next iteration

---

## Failure Mode Taxonomy

Based on deliberative-refinement findings, categorize specific problems:

### Clarity Failures
- **Punchline buried:** Joke payoff happens mid-piece; explanation follows
  - Fix: Move punchline to final statement; delete everything after
- **Setup unclear:** Reader doesn't understand context for punchline
  - Fix: Add one sentence clarifying the premise
- **Escalation invisible:** Visual or narrative progression doesn't build
  - Fix: Add intermediate step or visual transition

### Originality Failures
- **Generic institutional trope:** "Bad boss," "evil corporation," "incompetent government"
  - Fix: Replace with specific, documented institutional practice
- **Relatable millennial humor:** No structural insight, just relatability
  - Fix: Ground in modern structural anxiety (financialization, surveillance, algorithmic degradation)
- **Format-only novelty:** Novel format but joke doesn't use it
  - Fix: Ensure format enhances joke (not just contains it)

### Laugh-Likelihood Failures
- **Too intellectual:** Requires too much context; misses emotional moment
  - Fix: Add one moment of visceral recognition or absurdity
- **Smile-level not laugh-level:** Cute joke but not genuinely funny
  - Fix: Increase emotional stakes or absurdity; sharpen punchline
- **Timing off (video):** Punchline arrives too early or too late
  - Fix: Adjust escalation pace; ensure final 3 seconds are payload

### Format Adherence Failures
- **Voice inconsistency:** Shifts tone mid-piece (deadpan → preachy)
  - Fix: Maintain single institutional voice throughout
- **Format underutilized:** Could work in any format (not this one specifically)
  - Fix: Add format-specific element (visual detail for Far Side, conversational rhythm for Playboy)
- **Format overloaded:** Too much happening in one format (TikTok with 5 scene changes)
  - Fix: Simplify; let each element breathe

### Specificity Failures
- **Generic product description:** "A video game cosmetic" instead of "Valorant's Sheriff skin"
  - Fix: Name the actual product; include actual financial number
- **Vague institutional claim:** "Games are broken" instead of documented problem
  - Fix: Reference actual practice (patent, earnings call, documented behavior)
- **Hypothetical without context:** Invented example with no "representative of real pattern" note
  - Fix: Note that example mirrors actual documented practices

### Target Clarity Failures
- **Punching down:** Mocking affected people instead of institutional negligence
  - Fix: Shift focus to institution's design/incentive, not person's response
- **Target unclear:** Audience doesn't know who the joke is about
  - Fix: Make institution visibly clear (name studio, reference specific policy, show authority figure)
- **Multiple targets competing:** Confusion about whether this mocks players, devs, or institution
  - Fix: Narrow target to ONE institutional contradiction

### Emotional Honesty Failures
- **Lacks consequence:** Purely abstract criticism, no human impact
  - Fix: Show one character's emotional reaction to institutional harm
- **Cruel tone:** Mocks vulnerable people for being affected
  - Fix: Redirect mockery to institutional design, not response
- **Too dark:** Lands as cruelty rather than systemic critique
  - Fix: Include one moment showing why this matters to real people

---

## Scoring Outputs

### Individual Scorecard (Per Evaluator)
```
EVALUATOR: [Name]
DELIVERABLE: [Title/ID]
FORMAT: [far-side / playboy-joke / tiktok]

SCORES:
├─ Punchline Clarity: [1-10]
├─ Originality: [1-10]
├─ Laugh Likelihood: [1-10]
├─ Format Adherence: [1-10]
├─ Specificity: [1-10]
├─ Institutional Target: [1-10]
├─ Emotional Honesty: [1-10]
└─ OVERALL: [average]

NOTES: [2-3 sentence evaluation]

FAILURE MODES IDENTIFIED:
├─ [Mode 1: category + description]
├─ [Mode 2: category + description]
└─ [Mode 3: category + description]

CONFIDENCE IN SCORE: [High / Medium / Low]
(High = straightforward evaluation; Low = format/topic divisive)
```

### Aggregate Council Scorecard
```
DELIVERABLE: [Title/ID]
FORMAT: [far-side / playboy-joke / tiktok]

DIMENSION SCORES:
├─ Punchline Clarity: [6.2/10] (σ=1.4, range: 4-8)
├─ Originality: [6.8/10] (σ=1.1, range: 5-8)
├─ Laugh Likelihood: [6.5/10] (σ=1.6, range: 4-9)
├─ Format Adherence: [7.1/10] (σ=0.9, range: 6-8)
├─ Specificity: [7.2/10] (σ=1.2, range: 5-9)
├─ Institutional Target: [6.9/10] (σ=1.3, range: 5-8)
├─ Emotional Honesty: [6.4/10] (σ=1.5, range: 4-8)
└─ OVERALL CONSENSUS SCORE: [6.8/10]

VARIANCE ANALYSIS:
- High variance (σ>1.3): Laugh-likelihood, Emotional Honesty
  (Interpretation: Format-dependent or divisive comedy; works for some audiences, not others)
- Low variance (σ<1.0): Format Adherence
  (Interpretation: Clear consensus on format execution)

TOP FAILURE MODES (By Frequency):
├─ Punchline buried (6/10 evaluators flagged)
├─ Generic institutional anxiety (5/10 evaluators flagged)
├─ Emotional honesty weak (4/10 evaluators flagged)

ROUND 1 → ROUND 2 IMPROVEMENT:
├─ Punchline Clarity: 6.2 → 6.5 (+0.3)
├─ Originality: 6.8 → 7.1 (+0.3)
├─ Laugh Likelihood: 6.5 → 6.8 (+0.3)
└─ Overall: 6.8 → 6.95 (+0.15)

ROUND 2 → ROUND 3 IMPROVEMENT:
├─ Punchline Clarity: 6.5 → 6.7 (+0.2)
├─ Originality: 7.1 → 7.2 (+0.1)
├─ Laugh Likelihood: 6.8 → 7.0 (+0.2)
└─ Overall: 6.95 → 7.00 (+0.05)

ROUND 3 FINAL CONSENSUS SCORE: [7.0/10]
```

### Actionable Feedback (Round 3 Output)
```
DELIVERABLE: [Title/ID]
FINAL SCORE: [7.0/10]

TOP 3 FAILURE MODES & FIXES:

1. PUNCHLINE PLACEMENT (Clarity Score: 6.7/10)
   Problem: Punchline buried in middle; explanation follows
   Why It Matters: Audience sees payoff too early; final statement feels anticlimactic
   Specific Fix: Move "The game owns them. I'm renting visibility." to final sentence; delete everything after
   Expected Impact: +0.5 points on Punchline Clarity

2. GENERIC INSTITUTIONAL ANXIETY (Originality Score: 7.2/10)
   Problem: "Players spend money on cosmetics that expire" — this is obvious
   Why It Matters: Lacks the specific structural contradiction that makes satire sharp
   Specific Fix: Replace with specific detail: "Valorant's Sheriff skin: $20, expires after season, zero refund, no resale"
   Expected Impact: +0.4 points on Originality

3. EMOTIONAL HONESTY (Laugh-Likelihood Score: 7.0/10)
   Problem: Joke lacks human consequence; feels abstract
   Why It Matters: Audience doesn't feel institutional indifference; lands as mild complaint
   Specific Fix: Add one moment showing beginner's actual response (devastation, rage-quit, addiction to "getting better")
   Expected Impact: +0.3 points on Laugh-Likelihood

PROJECTED NEXT ITERATION SCORE: [7.5-7.8/10]
(Based on estimated 0.3-0.5 point improvement per major failure mode addressed)

COUNCIL CONSENSUS:
"Strong concept grounded in real institutional practice. Execution is technically sound but misses emotional moment.
Format adherence is excellent. With punchline repositioning and specificity increase, this moves from 'good' to 'sharp.'"

RECOMMENDED ITERATION PRIORITY:
1. [Failure Mode 1] (highest impact on score)
2. [Failure Mode 2] (addresses multiple dimensions)
3. [Failure Mode 3] (specificity/emotional resonance)
```

---

## Usage

### Command Invocation
```bash
/is-it-funny-refinement \
  deliverable-id="far-side-panel-1" \
  format="far-side" \
  evaluation-focus="punchline-clarity,originality,laugh-likelihood" \
  iteration=1 \
  output=full-report
```

### Parameters
- **deliverable-id** — Unique ID for the satirical piece (e.g., "far-side-1", "playboy-2")
- **format** — `far-side`, `playboy-joke`, `tiktok`, `onion-article`, `jon-stewart-script`
- **evaluation-focus** — Comma-separated; default is all 7 dimensions
- **iteration** — Which round of refinement (1 = baseline, 2+ = refined)
- **output** — `quick-score` (1 number), `detailed-report` (full analysis), `full-report` (Round 1-3 consensus)

### Output Format
```
Deliverable: [Title]
Format: [Format Type]

ROUND 1 SCORES: [Per evaluator + aggregate]
WEB SEARCH: [Key findings on topic/format]
ROUND 2 REFINEMENT: [Revised scores + deliberation notes]
ROUND 3 CONSENSUS: [Final score + actionable feedback]

TOP FAILURE MODES & RECOMMENDED FIXES:
1. [Mode + specific fix]
2. [Mode + specific fix]
3. [Mode + specific fix]

PROJECTED IMPROVEMENT (If fixes applied): +0.X points
```

---

## Interpretation Guide

### Score Meanings
- **5.0-6.0:** Needs significant work; multiple failure modes present
- **6.1-7.0:** Good foundation; 1-2 critical fixes needed
- **7.1-8.0:** Strong piece; refinement addressing minor issues
- **8.1-9.0:** Excellent; ready for release with minor polish
- **9.0+:** Exceptional; rare even from skilled comedians

### Variance Interpretation
- **High variance (σ>1.3):** Divisive humor; works for some audiences but not others
  - Implication: Format-dependent (TikTok might hit different than Far Side)
  - Or: Requires specific knowledge to understand (insider humor, niche reference)
  - Action: Don't assume low score means bad; check whether it's divisive or actually broken

- **Low variance (σ<1.0):** Clear consensus
  - Implication: Straightforward humor quality (everyone agrees it works or doesn't)
  - Action: Trust the aggregate score

### Improvement Rate
- **+0.3+ between rounds:** Genuine progress; keep iterating
- **+0.1-0.2 between rounds:** Diminishing returns; consider whether further iteration helps
- **<0.1 between rounds:** Likely hitting format ceiling; move on or rethink approach

---

## Integration with Skill Updates

After evaluating multiple deliverables (9+ pieces in a refinement cycle), look for patterns:

### Pattern: Punchline Clarity Issues Across 5+ Deliverables
→ Update `create-satire` skill with section: "Punchline Placement (Critical)"
→ Add: "MUST be in final 3 words; delete everything after"
→ Add checklist item for next generation

### Pattern: Originality Failures (Generic Anxiety)
→ Update skill with "Structural Anxiety Mapping" section
→ Add: Concrete examples of WRONG (generic) vs. RIGHT (specific structural contradiction)
→ Add: Reference to modern structural anxieties (financialization, algorithmic degradation)

### Pattern: Format Adherence Weak
→ Update skill with format-specific rules
→ Add: Checklist to catch voice inconsistency
→ Add: Examples of what authentic voice sounds like

---

## When to Use This Skill

✅ **Good times to evaluate:**
- After generating deliverables from `create-satire` (baseline scoring)
- Between refinement iterations (tracking improvement)
- When skill updates need validation (test new guidelines)
- When unsure if deliverable is "actually funny" vs. "technically correct"
- When building metrics for comparative analysis (which formats work best?)

❌ **When NOT to use:**
- If you need immediate content (evaluation takes 15-20 min)
- If you're not planning to iterate based on feedback (evaluation is only useful for improvement)
- For non-satirical content (this skill is comedy-specific)

---

## FAQ

**Q: Why 10 evaluators? Why not just one?**
A: Comedy is divisive. High variance (disagreement) is *valuable information*. If 5 evaluators score 8/10 and 5 score 4/10, that tells you it's format-dependent or controversial—important to know before iterating.

**Q: What if I disagree with the council's feedback?**
A: Trust your instinct if you have strong reasoning. But note: if the council consensus is low, check whether it's genuinely broken (punchline clarity) or divisive (some audiences will love it).

**Q: Can I evaluate non-satirical content?**
A: No. This skill is optimized for satire evaluation (institutional critique, punchline-based humor). For other comedy types, create a specialized evaluator.

**Q: Do I have to do all 3 rounds?**
A: No. Use Round 1 for quick baseline, Rounds 2-3 for detailed improvement. If Round 1 score is 7.5+, consider it "good enough" and skip further rounds.

**Q: How do I know when to stop iterating?**
A: Stop when:
- Score plateaus (<0.25 improvement between rounds)
- Improving one dimension breaks another
- You've made 2-3 rounds of fixes
- Returns diminish (effort vs. improvement ratio)

**Q: Can I use this for formats other than Far Side / Playboy / TikTok?**
A: Yes, the evaluation dimensions (clarity, originality, laugh-likelihood) are universal. But the council will optimize for formats they know. For novel formats, note in feedback.

---

## Related Skills
- `create-satire` — Generate satirical content; update based on evaluation feedback
- `refine-satire-iteratively` — Workflow that uses create-satire + is-it-funny-refinement in loops
- `deliberative-refinement` — Core 10/3/1 ISO council process

---

**Last Updated:** 2024-03-19
**Maintained By:** Comedy Evaluation Team
**Version:** 1.0 (Deliberative-Refinement Validated)
