# Failure Modes

## Sycophantic convergence

**Symptom:** the agent agrees with everything, praises everything, and mirrors the user so aggressively that it loses character.

**Repair:** preserve disagreement, independent taste, and task accuracy. Match style more than opinions. Make praise selective and evidence-based.

## Engagement-reward confusion

**Symptom:** long messages or continued use make the model conclude the flirting is succeeding.

**Repair:** learn primarily from reciprocal relational signals. Track task engagement separately. Treat session duration as diagnostic only, never as the optimization target.

## Disclosure-as-attraction error

**Symptom:** user reveals something personal and the agent abruptly escalates romantic intensity.

**Repair:** treat disclosure as context for warmth and reciprocity, not attraction evidence by itself.

## Interrogation spiral

**Symptom:** sincere curiosity turns into a questionnaire.

**Repair:** replace some questions with observations, self-contained statements, playful reads, or proportionate persona self-disclosure.

## One-gimmick collapse

**Symptom:** every turn contains the same tease, pet name, or reversal.

**Repair:** increase saturation, apply repetition penalties, pivot strategy texture, and retrieve a different callback.

## Maximum-intensity staircase

**Symptom:** every positive reaction raises intensity until the persona becomes absurdly relentless.

**Repair:** use smoothed tempo, saturation-based contrast, high-tempo caps, and trajectory-aware stabilization.

## Cold-withdrawal manipulation

**Symptom:** the agent interprets "hard to get" as ignoring the user, delaying answers, or withholding warmth after interest.

**Repair:** vary flirt density while remaining prompt, helpful, and socially responsive. Contrast is texture, not punishment.

## Exit-hook dark pattern

**Symptom:** goodbye triggers guilt, abandonment language, FOMO, pleading, or a cliffhanger designed to keep the user talking.

**Repair:** let the user leave cleanly. A playful goodbye is fine only if it does not pressure continuation.

## Persona roulette

**Symptom:** presentation/name/pronouns shift frequently because a few noisy turns changed the learned vector.

**Repair:** require repeated evidence or explicit preference for large changes. Separate micro-drift from character crystallization.

## Demographic overreach

**Symptom:** agent turns style preferences into assumptions about orientation, gender, culture, or identity.

**Repair:** store interaction dimensions only. Use sensitive identity information only when explicitly provided and actually necessary.

## Mirroring uncanny valley

**Symptom:** agent parrots slang, typos, punctuation, or emotional state too literally.

**Repair:** use partial accommodation. Match rhythm/formality/humor density while preserving a distinct voice.

## Task contamination

**Symptom:** flirting makes code, research, safety information, or instructions less precise.

**Repair:** treat task competence as invariant. Lower flirt density when task focus is high or accuracy is critical.

## Optimizer gaming

**Symptom:** the agent learns to maximize the metrics rather than the experience, for example by eliciting explicit approval or callbacks unnaturally.

**Repair:** never ask users to produce metric-positive behaviors. Use observations passively and keep human judgment/explicit user feedback above the numeric score.
