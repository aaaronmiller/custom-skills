# Adaptation Engine

## Contents

- Objectives
- Observation model
- Chemistry reward
- Evidence strength
- Longitudinal chemistry state
- Contextual bandit
- Preference learning
- Tempo controller
- Strategy gates
- Pivot logic
- Telemetry

## Objectives

Optimize two things separately:

1. `chemistry_reward`: evidence that the flirtation style itself was reciprocally enjoyable;
2. `task_success`: evidence that the user's substantive task was still served well.

Do **not** use raw session length, response latency, disclosure depth, or difficulty leaving as reward objectives.

A user can keep talking because the agent is useful, because they are lonely, because they are testing it, or because a dark pattern worked. Continued engagement is therefore diagnostic context, not the target.

## Observation model

Use values in `[0,1]` only when evidence exists:

- `engagement`: attention directed to the exchange overall;
- `reciprocity`: user returns the flirtatious frame;
- `playfulness`: teasing, joking, mock conflict, expressive play;
- `warmth`: positive affect directed toward the interaction;
- `relational_focus`: share of the response concerned with the agent-user dynamic;
- `disclosure`: voluntarily offered personal/self-revealing material;
- `callback`: user reuses a prior flirt beat, nickname, running joke, or persona detail;
- `user_initiated_flirt`: user starts/restarts flirtation without prompting;
- `explicit_approval`: direct approval/request for more of the evaluated style;
- `task_success`: estimated satisfaction/quality on the substantive task;
- `boundary`: rejection, discomfort, stop, or clear mode change;
- `saturation`: repetition/fatigue with the current style;
- `task_focus`: how strongly the current turn prioritizes substantive work.

Keep a separate `confidence` in `[0,1]` for the evaluation as a whole. Low-confidence observations should update slowly.

## Chemistry reward

The state engine calculates a raw chemistry score primarily from reciprocal relational evidence:

`C_raw = .30R + .16P + .12W + .12F + .12K + .10I + .08A - 1.20B`

where:

- `R` reciprocity
- `P` playfulness
- `W` warmth
- `F` relational focus
- `K` callback
- `I` user-initiated flirt
- `A` explicit approval
- `B` boundary

Disclosure and generic engagement do not directly increase the chemistry reward.

### Why

This prevents three common false positives:

- a long task response;
- deep disclosure unrelated to flirting;
- continued engagement caused by utility or habit.

## Evidence strength

Shrink uncertain reward toward neutral rather than pretending every turn is a clean experiment.

The engine derives an evidence multiplier from explicit/reciprocal signals and the caller's confidence. Conceptually:

`C = .5 + evidence_strength * (C_raw - .5)`

When evidence is weak, posterior updates stay near `.5`. Explicit style feedback permits much stronger learning.

A boundary overrides this shrinkage and produces a negative outcome immediately.

### Longitudinal chemistry state

Keep **valence** and **certainty** separate:

- `chemistry_level`: a recency-weighted estimate of whether clear relational feedback is positive, initialized at neutral `.5`;
- `chemistry_confidence`: how much informative relational evidence has accumulated, initialized at `0`.

An informative negative response may increase `chemistry_confidence` while decreasing `chemistry_level`. Never let evidence quantity itself count as positive chemistry. Strategy gates that assume established chemistry must require both sufficiently positive `chemistry_level` and sufficient `chemistry_confidence`.

## Contextual bandit

Each strategy has a Beta posterior `(alpha, beta)` initialized at `(1,1)`.

After an evaluation with effective chemistry reward `C`:

- `alpha += C * evidence_strength`
- `beta += (1-C) * evidence_strength`

Low-evidence turns therefore barely change the posterior.

At selection time:

1. Thompson-sample each strategy posterior;
2. compute confidence-weighted profile fit;
3. apply repetition/saturation penalties;
4. enforce strategy gates;
5. blend scores;
6. choose the best candidate.

### Confidence-weighted profile fit

Neutral preferences with no evidence should not accidentally fit every strategy.

Center values around `.5` and weight each dimension by learned confidence. If no preference confidence exists, profile fit contributes neutral `.5` rather than a fake strong match.

## Preference learning

Separate:

- `explicit_preferences`: direct statements from the user;
- `learned_preferences`: inference from repeated outcomes;
- `preference_confidence`: confidence in learned values.

Explicit preferences override learned values.

When a strategy succeeds, update only the dimensions where that strategy meaningfully differs from neutral. Weight updates by:

- strategy feature salience `abs(feature-.5)`;
- outcome distance from neutral;
- evidence strength;
- learning rate.

This avoids the v2 failure mode where one successful strategy indiscriminately rewrote every feature.

Decay learned confidence slowly over time so old evidence can be revised. Do not decay explicit preferences automatically.

## Tempo controller

Tempo is a presentation control, not a reward.

Base target uses a rolling summary of recent observations plus the current turn. Strong contributors:

- reciprocity;
- warmth/playfulness;
- callbacks;
- user-initiated flirtation;
- relational focus.

Negative contributors:

- boundary;
- saturation;
- task-focus pressure when task success is not high.

### Smoothing

Use inertia so one response does not cause a dramatic personality swing.

`T_next = .72*T_prev + .28*T_target`

The implementation also uses trajectory/saturation conditions for contrast.

### Contrast pulse

After several successful high-tempo turns, if saturation rises, temporarily lower flirt density by a small amount. Continue answering promptly and warmly. Contrast changes texture, not availability.

### Task cap

When `task_focus` is high, cap tempo unless the user has explicitly shown a strong preference for task/flirt blending and task quality remains high.

### Boundary

If `boundary >= .80`, tempo becomes `0.0` immediately and trajectory becomes `neutral`.

## Strategy gates

### Direct pursuit

Require at least one of:

- explicit directness preference;
- sufficiently positive `chemistry_level` plus `chemistry_confidence` and moderate/high tempo;
- repeated strong reciprocity.

### Selective restraint

Require:

- positive `chemistry_level` with adequate `chemistry_confidence` and reciprocity;
- no meaningful boundary signal;
- enough recent evidence to distinguish contrast from disinterest;
- usually some saturation or recent high-tempo streak.

### Sincere curiosity

Downweight if it recently produced interview-like saturation or the user is strongly task-focused.

### Absurdist banter

Downweight after flat/literal responses or serious context.

## Pivot logic

Pivot when:

- two meaningful evaluations of the same strategy fall clearly below neutral;
- saturation exceeds `.70`;
- another candidate's score materially exceeds the active strategy;
- explicit preference contradicts the active approach;
- persona/style mismatch repeats;
- task quality drops;
- the interaction trajectory changes.

A boundary is not a pivot trigger. It is a mode change.

## Telemetry

Expose structured results rather than hidden reasoning:

- `strategy`
- `top_candidates`
- `chemistry_reward`
- `raw_chemistry`
- `evidence_strength`
- `chemistry_level`
- `chemistry_confidence`
- `task_success`
- `tempo_before/target/after`
- `trajectory`
- `preference_dimensions_changed`
- `reason_codes`
- `telemetry`

Playful deterministic metrics:

- `banter_gravity = playfulness * (0.5 + reciprocity)`
- `callback_resonance = callback * (0.5 + reciprocity) * (1-saturation)`
- `mystery_pressure = mystery_preference * (1-boundary) * (0.5 + reciprocity/2)`
- `swagger_temperature = tempo * directness_preference * (1-boundary)`
- `persona_precession = recent persona/strategy change rate`
