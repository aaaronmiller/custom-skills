---
name: make-it-funny
description: Generate high-quality satirical and comedic content in visual, written,
  and spoken formats with institutional critique focus
inputs:
- name: topic
  description: Topic or institution to satirize
  pointer_type: parameter
outputs:
- name: satirical_content
  description: Generated satirical and comedic content
  pointer_type: output_file
tags:
- fun
- social
- writing
grade: A
source: custom
---

# Make It Funny

**Master Satirist and Comedic Media Generator**

Create clever, current, and relevant satirical content across visual (image prompts), written (articles/jokes), and spoken (scripts) formats. Specializes in Far Side-style panels, Playboy-style jokes, TikTok video concepts, Onion articles, and Jon Stewart-style scripts.

---

## Core Comedic Philosophy

### ✓ What Works (Do This)
1. **Authentic satire targeting power structures** — Punch up at institutions, hypocrisy, and systems
2. **Hyper-specific modern structural anxieties** — Financialization, algorithmic degradation, surveillance, gig economy, climate denial, normalized greed
3. **Punchline at the VERY END** — Last 3 words hit hardest
4. **Institutional voice consistency** — Maintain format (deadpan news, cynical memo, casual TikTok) throughout
5. **Dual-perspective structure** — Show tension between what institution claims and what actually happens
6. **Real human consequence** — Ground joke in actual emotional stakes, not abstract criticism
7. **Specific details, NOT generic** — Use actual products, real financial numbers, documented practices

### ✗ What Fails (Don't Do This)
1. **Generic, relatable millennial tropes** — "Moving between screens," "avocado toast," "bad bosses," "airline food"
2. **Performative outrage without target clarity** — Anger at everything, critique of nothing
3. **Punchline buried in setup** — Joke dies if reader sees the payoff before the end
4. **Vague comparisons** — "This is like..." without the comparison landing
5. **Over-explaining the joke** — Never add "Here's why that's funny..." after the payoff
6. **Format inconsistency** — Don't break character; don't switch tone mid-piece
7. **Punching down** — Don't mock vulnerable communities; mock the institutions that exploit them

---

## Format Specifications

### Far Side Panel (Visual Satire)

**Core Structure:**
- Single illustration with short caption
- Anthropomorphic or surreal visual premise
- Punchline is the **visual juxtaposition**, not the caption
- Caption amplifies absurdity, doesn't explain it

**What Works:**
- Minimize figure count (1-3 characters max)
- Heavy use of architectural/environmental detail
- Deadpan caption tone
- Visual details that suggest backstory
- Punchline in caption's FINAL PHRASE

**What Fails:**
- Too many elements competing for attention
- Caption that explains the visual
- Smile-generating setup without laugh-generating punchline
- Generic office/household settings

**Example Framework:**
```
[Visual: Surgeon in OR, hand on scalpel, 47M patient charts on wall monitor scrolling in real-time]
Caption: "[Character] had finally accepted that he would never know the consequences of his decisions until after [action] was over."
```

**Checklist:**
- [ ] Visual is immediately striking
- [ ] Can understand 80% of joke from image alone
- [ ] Caption's final phrase is the payoff
- [ ] No explanation required beyond caption
- [ ] Specific detail in visual (not generic "hospital")

---

### Playboy Joke (Written Satire)

**Core Structure:**
- Setup (2-4 sentences): Establish character, situation, assumption
- Reversal/Subversion (1-2 sentences): Expose the contradiction
- Punchline (1 sentence): Final twist that reframes everything

**What Works:**
- Conversational tone (as if being told at a bar)
- Setup feels reasonable until reversal
- Punchline reframes earlier statements
- Sexual/innuendo tension optional but can heighten impact
- Specific detail in setup (product name, price, timeline)

**What Fails:**
- Setup too long (reader guesses punchline early)
- Punchline is obvious joke format ("Why? Because...")
- Crude without wit
- Setup and punchline disconnected
- Generic characters ("guy" without personality)

**Example Framework:**
```
Setup: "Guy at bar leans toward attractive person. 'I'm actually an investor,' he says."
Reversal: "Yeah, I've put $4,000 into seasonal cosmetics last year."
Punchline: "'Own is generous. The game owns them. I'm just renting the visibility.'"
```

**Checklist:**
- [ ] Setup uses conversational voice
- [ ] Specific detail: actual price, actual product, actual timeline
- [ ] Reversal exposes institutional contradiction (claim vs. reality)
- [ ] Punchline is final statement (nothing after)
- [ ] Laugh comes from structural hypocrisy, not shock

---

### TikTok Video (Spoken Satire)

**Core Structure:**
- Hook (0-3 sec): Grab attention with specific, surprising statement
- Escalation (3-15 sec): Show context, add dimension, build to reveal
- Punchline (final 5 sec): Text overlay, visual reveal, or TTS mic drop
- Audio design: Undercut expectations with music/sound

**What Works:**
- Hook is NOT a question ("Did you know...?" is weak)
- Hook is a STATEMENT or ACTION that makes viewer stop scrolling
- Each 5-sec segment adds new information (not repetition)
- Text overlays add data that audio doesn't explain
- Final 3 seconds are devastating, not ambiguous
- Sound design emphasizes absurdity (dramatic music on ridiculous claim, sad trombone on loss)

**What Fails:**
- Hook too vague ("This is crazy...")
- Too much talking, not enough visual escalation
- Text overlays that repeat what audio says
- Ending is unclear (does the character win or lose?)
- Generic background/setup

**Example Framework:**
```
Hook [0-3]: Developer reading patch notes solemnly: "Cooldown reduction: 0.5 seconds."
Escalation [3-10]: Rapid game footage of absolute chaos, then metrics dashboard.
Reveal [10-15]: "Tested with: 12 players. Deployed to: 47 million."
Punchline [final 5]: Developer's dead-inside face. TTS: "This is fine. This is completely fine."
```

**Checklist:**
- [ ] Hook is NOT a question
- [ ] Hook is a specific, surprising statement or action
- [ ] Escalation adds new dimension every 5 seconds
- [ ] Text overlays provide DATA (not narrative)
- [ ] Final segment is devastating or absurd
- [ ] Audio design amplifies, doesn't explain
- [ ] Punchline is in final 3 seconds

---

## Structural Anxiety Mapping (Modern Context)

Map jokes to specific, documented institutional problems, NOT generic complaints:

### Financialization of Everything
**Documented Problem:** Games use cosmetics as depreciating asset model (buy for $20, asset expires in 90 days, zero refund policy)
**Satire Angle:** Treat cosmetics as financial product (investment, ROI, asset class, mortgage-broker tone)
**Example:** "Battle Pass: A Smart Investment" (infomercial format showing actual financial language applied to disposable cosmetics)

### Algorithmic Degradation
**Documented Problem:** Matchmaking algorithms intentionally create skill mismatches to maximize engagement (documented in Activision patents)
**Satire Angle:** Expose that "fairness" is subordinate to "engagement metrics"
**Example:** Developer staring at metrics showing +47% engagement, while beginner gets destroyed by pro player

### Normalized Greed
**Documented Problem:** Cosmetics rebranded with euphemistic language ("seasonal exclusive" instead of "temporary license") when transparency causes player backlash
**Satire Angle:** Expose language manipulation and A/B testing of euphemisms
**Example:** Memo showing studio A/B tested language ("cosmetics expire" scored 11% lower than "seasonal cosmetics are now legacy content")

### Systems Gambling with User Outcomes
**Documented Problem:** Live-service balance patches are deployed without full predictability; devs ship changes knowing they can't model 50M+ player interactions
**Satire Angle:** Expose that patch notes are corporate spin for "we guessed and the system broke"
**Example:** Surgeon performing operation on 50M simultaneous patients, none of whom can be consulted

### Predatory Engagement Design
**Documented Problem:** Young players maxed credit cards on cosmetics; cosmetics serve as status anxiety + FOMO mechanism
**Satire Angle:** Show that FOMO is intentional design, not accident
**Example:** Real estate agent selling house that expires after 90 days, calling it "seasonal exclusive property"

---

## Punchline Placement (Critical)

**Rule:** Punchline MUST be in the final 3 words (visual) or final sentence (written/spoken). Nothing comes after the laugh.

### Visual Satire
```
WRONG: "Dr. Chen had finally accepted that he would never know the consequences of his decisions. This made him think carefully before each surgery."
RIGHT: "Dr. Chen had finally accepted that he would never know the consequences of his decisions until after surgery was over."
```

### Written Satire
```
WRONG: "Guy says he's invested in cosmetics. She laughs. Then she realizes he's serious."
RIGHT: "'Own is generous,' he says. 'The game owns them. I'm just renting the visibility.'"
```

### Spoken Satire
```
WRONG: [Developer reads patch notes, game breaks, metrics show success, then text says "This is fine"]
RIGHT: [Developer's face, dead inside, TTS final statement: "This is fine." [End video]]
```

**Checklist Before Output:**
- [ ] Last sentence/phrase is the punchline
- [ ] Nothing comedic after the final punchline
- [ ] Reader/viewer can't predict payoff before reaching it
- [ ] Punchline reframes everything that came before

---

## Specificity Requirement (No Generics)

Every deliverable MUST include:

### Actual Product/Feature Name (Not Generic Description)
```
WRONG: "A video game cosmetic costs $20 and expires."
RIGHT: "Valorant's Sheriff skin costs $20 and disappears at season end."
```

### Real Financial Numbers (Or Note as "Representative")
```
WRONG: "Players spend a lot of money on cosmetics."
RIGHT: "Players reported spending $4,000 on battle passes over 3 years; cosmetics expired after each season."
```

### Institutional Documentation (Patents, Quotes, Data)
```
WRONG: "Matchmaking might be designed to exploit players."
RIGHT: "Activision patent (US 10,293,275) for engagement-optimized matchmaking explicitly deprioritizes fairness for engagement metrics."
```

### If Inventing Example, Note It As Representative
```
"A hypothetical example that mirrors actual patterns: Cooldown reduction of 0.5s in controlled lab test caused 47% engagement spike in live environment with 47M players."
```

**Checklist:**
- [ ] Product/feature has actual name (not "cosmetic" but "Operator skin")
- [ ] Financial numbers are real or noted as representative
- [ ] Claims reference documented practices (patents, earnings calls, published studies)
- [ ] Generics ("game," "player," "studio") are replaced with specific proper nouns where possible

---

## Dual-Perspective Structure (Reveals Contradiction)

Structure satire to show tension between institutional claim and institutional practice:

### Claim vs. Reality Juxtaposition
```
Split Screen / Side-by-side:
- Left: What marketing says ("Fair and Balanced")
- Right: What system actually optimizes for (engagement metrics)
```

### Authority Voice vs. Consequences
```
Developer (confident, reading patch notes): "Minor cooldown adjustment for improved gameplay experience."
[Cut to]: Game footage showing complete chaos
[Cut to]: Player's devastated face
```

### Different Institutional Perspectives on Same Event
```
Studio: "This cosmetic is seasonal exclusive, creating urgency and value."
Player: "I paid $20 for something that expires in 90 days."
Investor: "Cosmetics are recurring revenue model: high margin, high repeat purchase."
```

**Checklist:**
- [ ] Piece shows institutional claim somewhere
- [ ] Piece shows institutional reality somewhere else
- [ ] Contradiction is visible without explanation
- [ ] Reader can draw their own conclusion

---

## Emotional Honesty (Ground in Real Stakes)

Include at least ONE moment showing genuine human consequence:

### What To Show
- A pro player's career affected by broken patch
- A disabled player priced out by accessibility negligence
- A beginner's learned helplessness from matchmaking
- A developer's panic at unintended consequences
- A young player's credit card debt from cosmetics

### How To Show It
- One character's face showing real emotion (panic, heartbreak, resignation)
- One quote showing vulnerability or desperation
- One data point showing scale of harm (millions affected, thousands of dollars lost)
- One moment where the joke acknowledges actual suffering

### What NOT To Do
- Don't become cruel; the joke is about institutions, not the person harmed
- Don't mock vulnerability; use it to show institutional indifference
- Don't add moral lecture; let the contradiction speak
- Don't make the victim the target; make the system the target

**Example:**
```
Video shows beginner getting demolished in matchmaking.
Caption: "[Beginner player name], 15 hours played, 3-hour session, matchmade against pro with 2000+ hours."
The joke isn't "beginner sucks"; it's "system intentionally did this."
Audio: Developer's voice: "Engagement metrics are up. The new player will return tomorrow."
```

**Checklist:**
- [ ] Piece includes human consequence, not just abstract criticism
- [ ] Emotion is shown, not explained
- [ ] Target is institutional design, not the person affected
- [ ] Vulnerability reveals system's indifference

---

## Format-Specific Rules

### Far Side Panels
1. **One visual premise, one punchline**
2. **Caption is final statement** (no follow-up)
3. **Specific detail in image** (not generic "office")
4. **Absurdity should feel possible** (not physically impossible)

### Playboy Jokes
1. **Conversational voice** (bar story, not formal prose)
2. **Setup invites assumption**
3. **Reversal in penultimate statement**
4. **Punchline reframes** everything before it
5. **No "and then" after punchline**

### TikTok Videos
1. **Hook is statement, not question** (0-3 sec)
2. **Each 5-sec segment adds new info**
3. **Text overlays = data, not narrative**
4. **Escalation is visible** (visual or metric)
5. **Punchline is final 3 seconds** (mic drop, dead-inside face, ridiculous revelation)

---

## Deliberative Refinement Checklist (Before Output)

Run through this before finalizing any deliverable:

```
[ ] CLARITY
    [ ] Is the punchline in the final sentence/phrase?
    [ ] Can the joke be understood without explanation?
    [ ] Is the setup clear enough to land the reversal?

[ ] ORIGINALITY
    [ ] Does this avoid generic tropes (relatable millennial, bad bosses, etc.)?
    [ ] Is this grounded in specific structural anxiety, not vague complaint?
    [ ] Have I seen this joke/premise before?

[ ] SPECIFICITY
    [ ] Does it name actual products/features (not "a game")?
    [ ] Does it use real financial numbers or note them as representative?
    [ ] Does it reference documented practices (patents, quotes, data)?

[ ] FORMAT ADHERENCE
    [ ] Does the format feel authentic (Far Side is Far Side, TikTok sounds like TikTok)?
    [ ] Does voice consistency hold throughout?
    [ ] Does format enhance the joke, not confuse it?

[ ] INSTITUTIONAL TARGET
    [ ] Am I punching up (at power structures)?
    [ ] Have I shown institutional contradiction?
    [ ] Is the target clear?

[ ] EMOTIONAL HONESTY
    [ ] Does the joke acknowledge real human consequence?
    [ ] Is the target institutional negligence, not individual victims?
    [ ] Does it avoid cruelty?

[ ] ESCALATION (for video/written)
    [ ] Does each segment add new information?
    [ ] Does intensity/absurdity increase?
    [ ] Does final reveal feel inevitable in hindsight?

[ ] PUNCHLINE POWER
    [ ] Does the final statement make me want to laugh/groan?
    [ ] Does it reframe what came before?
    [ ] Would a stranger get it without explanation?
```

---

## Example: Complete Satirical Piece

### Far Side Panel
```
[VISUAL: Surgeon in operating room, hand trembling on scalpel. Wall monitor behind shows cascading 47,000,000 patient charts in real-time, incomprehensible scroll. Nurse handing fresh scalpel. Surgeon's face: resigned, certain of failure.]

CAPTION: "Dr. Chen had finally accepted that he would never know the consequences of his decisions until after surgery was over."
```

**Why This Works:**
- ✓ Visual immediately strikes (scale is overwhelming)
- ✓ Specific detail (47M charts, Dr. Chen's name)
- ✓ Punchline in final phrase ("until after surgery was over")
- ✓ Maps to real problem (live-service game balance at scale)
- ✓ Shows human consequence (surgeon's resignation)
- ✓ Dual perspective (institutional claim: "precision surgery" vs. reality: "gambling with 50M outcomes")

---

## Anti-Patterns (What Not To Do)

### Anti-Pattern 1: Punchline Buried
```
WRONG: "Game was broken by patch. So everyone was angry. The studio said it was intentional. But really it was just incompetence."
RIGHT: "The studio blamed player feedback. In reality, the algorithm was optimizing for engagement, not fun. The broken game kept people coming back."
```

### Anti-Pattern 2: Generic Anxiety
```
WRONG: "Video games are hard and nobody plays them because they're too expensive."
RIGHT: "Elden Ring costs $60 base + $40 DLC + $200 coaching because matchmaking is broken + accessibility features cost extra if they exist at all."
```

### Anti-Pattern 3: Over-Explaining
```
WRONG: "[Joke]. This is funny because it shows how institutions are hypocritical."
RIGHT: "[Joke.] [End. No explanation.]"
```

### Anti-Pattern 4: Punching Down
```
WRONG: "[Disabled players who need accessibility features]"
RIGHT: "[Studios that negligently design without accessibility, then price accessibility as external coaching]"
```

### Anti-Pattern 5: Format Inconsistency
```
WRONG: [Playboy joke that suddenly becomes preachy news-voice in final line]
RIGHT: [Playboy joke that stays conversational bar-story tone throughout]
```

### Anti-Pattern 6: Generic Product Names
```
WRONG: "A video game cosmetic..."
RIGHT: "Valorant's Reaver Operator skin costs $2,175 if you unlock all variants..."
```

### Anti-Pattern 7: Unclear Escalation (Video)
```
WRONG: [Shot of developer] [Shot of game] [Shot of confusion] [End]
RIGHT: [Developer confident] → [Game breaks] → [Metrics show success anyway] → [Developer's face: dead inside]
```

---

## Usage

### Command Invocation
```bash
/create-satire \
  formats="far-side,playboy-joke,tiktok" \
  subject="game-design-failures" \
  quantity=3 \
  output=raw-deliverables \
  iteration=1 \
  refinement-context="avoid-punchline-burial,target-structural-anxiety"
```

### Parameters
- **formats** — Comma-separated: `far-side`, `playboy-joke`, `tiktok`, `onion-article`, `jon-stewart-script`
- **subject** — Topic focus: `game-design-failures`, `surveillance-capitalism`, `startup-fraud`, etc.
- **quantity** — Number of deliverables per format (default: 3)
- **iteration** — Which refinement iteration (1 = first draft, 2+ = refined based on feedback)
- **refinement-context** — Specific failure modes to avoid (from deliberative-refinement feedback)
- **output** — `raw-deliverables` (content only) or `with-feedback` (include eval notes)

### Output Format
```
<final_output>
[DELIVERABLE TYPE]: [TITLE]

[Raw content - no explanation, no preamble]
</final_output>
```

---

## Related Skills
- `is-it-funny-refinement` — Evaluate comedy quality using deliberative-refinement
- `deliberative-refinement` — 10/3/1 ISO council validation
- `refine-satire-iteratively` — Workflow for continuous skill improvement

---

**Last Updated:** 2024-03-19
**Maintained By:** Satire Skill Development Team
**Version:** 2.1 (Post-Deliberative-Refinement Validation)


