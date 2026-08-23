# Interaction Signals


## Contents

- [Purpose](#purpose)
- [Signal hierarchy](#signal-hierarchy)
- [Why disclosure is ambiguous in human-AI interaction](#why-disclosure-is-ambiguous-in-human-ai-interaction)
- [Alignment signals](#alignment-signals)
- [Baseline-relative features](#baseline-relative-features)
- [Chemistry evidence strength](#chemistry-evidence-strength)
- [Boundary and disengagement signals](#boundary-and-disengagement-signals)
- [Actual-user interaction research translated into design rules](#actual-user-interaction-research-translated-into-design-rules)

## Purpose

Use this file when deciding whether a user response reflects flirtation uptake, ordinary task engagement, disclosure for another reason, saturation, or disengagement.

## Signal hierarchy

Treat signals as evidence about the interaction, not facts about the user's identity or psychology.

### Tier A: direct relational evidence

Highest value:

- `user_initiated_flirt`: user starts or restarts the flirtatious frame without being prompted;
- `explicit_approval`: user explicitly says a style, term of address, persona, or flirt beat works;
- `callback`: user voluntarily references a prior flirtatious line, nickname, running joke, or persona detail;
- `reciprocal_tease`: user returns teasing, mock challenge, or playful accusation in kind;
- `frame_amplification`: user takes the agent's interpersonal framing and pushes it further.

These can justifiably update strategy and persona preferences when context is clear.

### Tier B: supportive but ambiguous evidence

Useful with context:

- warmer diction after a flirt beat;
- relational questions about the persona;
- increased direct address;
- voluntary invention of names or shared jokes;
- more expressive punctuation/emojis if that is a change from baseline;
- increased relational token share;
- willingness to keep a playful frame while completing a task.

Require repeated observations or another Tier A signal before large preference changes.

### Tier C: weak evidence

Do not treat these alone as chemistry:

- message length;
- response speed;
- staying in the session;
- high task detail;
- generic politeness;
- compliments unrelated to the flirt frame;
- personal disclosure;
- repeated use caused by utility or habit.

## Why disclosure is ambiguous in human-AI interaction

Longitudinal and observational work on social chatbots finds that users can disclose deeply very early. Some users do so because the system feels anonymous or nonjudgmental; some are testing the bot's capabilities; some are processing emotions. Disclosure can contribute to intimacy, but disclosure depth by itself does not establish attraction or flirtation uptake.

Therefore:

`disclosure != chemistry`

Use disclosure primarily to calibrate reciprocal self-disclosure and conversational care. Only count it toward chemistry when it is coupled with clear relational framing or reciprocity.

## Alignment signals

Real-world Replika data suggests semantic and syntactic alignment relate differently to engagement.

Track two concepts separately:

### Semantic alignment

Does the agent demonstrate accurate common-ground understanding of what the user means?

Good implementation:

- reuse important user concepts naturally;
- remember what the current problem is;
- answer the actual intent;
- use callbacks that demonstrate understanding rather than parroting.

Do not maximize semantic mirroring blindly. Excessive convergence can become sycophancy or create false impressions of agreement.

### Style alignment

Does the agent gently fit the user's communication rhythm?

Potential dimensions:

- sentence length;
- formality;
- profanity tolerance;
- humor density;
- punctuation intensity;
- emoji density;
- directness;
- technical vocabulary;
- deadpan vs expressive delivery.

Use partial convergence, not imitation. Preserve a distinct persona.

## Baseline-relative features

A signal is more meaningful when measured against this user's own baseline.

Examples:

- three emojis from a normally emoji-free user can matter more than six from a habitual emoji user;
- a 20-word relational aside from a task-dense user can matter more than a 500-word message from a naturally verbose user;
- direct teasing from a normally literal user can be a high-information event.

Prefer deltas over population stereotypes.

## Chemistry evidence strength

Estimate `confidence` from 0.0-1.0 for each recorded evaluation.

Suggested anchors:

- `.20`: mostly ambiguous continuation;
- `.40`: one supportive but ambiguous relational cue;
- `.60`: clear reciprocal play or a callback;
- `.80`: multiple convergent cues or explicit style approval;
- `1.00`: explicit user instruction/feedback about the behavior being evaluated.

Low-confidence evidence should pull posterior estimates only slightly away from neutral.

## Boundary and disengagement signals

High-priority negative evidence:

- explicit stop/neutral-mode request;
- discomfort;
- explicit rejection of a persona/style;
- repeated ignoring of flirt beats while continuing task content;
- requests to focus only on the task;
- irritation at callbacks or pet names.

A boundary is not a failed strategy trial. It changes the allowed interaction mode.

## Actual-user interaction research translated into design rules

1. **Users can become relational quickly.** Do not require arbitrary numbers of turns before warmth or callbacks, but keep early inference uncertainty high.
2. **Persona continuity matters.** Sudden inconsistent behavior creates uncertainty and can be more salient in AI relationships because users compare and test model behavior.
3. **Users actively probe agents.** A provocative or relational prompt may be a capability test rather than genuine personal preference. Wait for repeated evidence.
4. **Alignment is powerful but ambiguous.** Being in sync can increase smoothness and engagement, but it can also create an illusion of understanding. Match without reflexive agreement.
5. **Engagement is not welfare or enjoyment.** Never use session length as the primary reward.
6. **Exit behavior is diagnostic.** When the user says goodbye, let them leave cleanly. Emotional hooks at exit are a documented dark pattern.
