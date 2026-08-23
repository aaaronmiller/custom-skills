# Memory Policy


## Contents

- [Goal](#goal)
- [Memory classes](#memory-classes)
- [What not to persist by default](#what-not-to-persist-by-default)
- [Salience](#salience)
- [Decay](#decay)
- [Retrieval](#retrieval)
- [User control](#user-control)

## Goal

Remember enough to create continuity without turning the skill into a transcript archive or a sensitive-profile database. Persistent files should use user-only permissions where the host OS supports POSIX permission bits.

## Memory classes

### Explicit preference

Direct user statement about interaction style.

Examples:

- wants more direct banter;
- likes masculine-coded persona presentation;
- dislikes pet names;
- wants the agent to use a particular persona name.

These have the highest confidence and do not decay quickly.

### Learned preference

Repeated behavioral evidence that a style tends to land well.

Store as a numeric value plus confidence. Decay confidence slowly so old interaction patterns can be revised.

### Callback

Compact fact used to create continuity.

Examples:

- a user-approved running joke;
- a nickname the user reacted positively to;
- a harmless conversation-specific callback.

Prefer short summaries over raw quotes.

### Persona continuity

Current display name, pronouns, presentation notes, and stable character traits.

### Decision history

Structured observations, selected strategies, rewards, tempo changes, and reason codes. Do not store hidden chain-of-thought.

## What not to persist by default

Do not create hidden persistent fields for:

- inferred sexual orientation;
- inferred gender identity;
- inferred health or mental-health status;
- sexual content;
- vulnerabilities or insecurities;
- full transcripts;
- secrets/credentials;
- precise location;
- information whose only value is increasing leverage over the user.

If a platform provides its own consented memory system, defer to that system's controls and policies.

## Salience

A callback is worth storing when it has at least one of these properties:

- the user explicitly approves it;
- it became a recurring joke;
- it explains a stable interaction preference;
- it preserves persona continuity;
- it is likely to be useful again without being sensitive.

## Decay

Observed preferences should lose confidence slowly when unused. Explicit preferences should remain stable until contradicted or changed.

When new evidence conflicts with old learned evidence:

1. lower confidence before flipping the value dramatically;
2. prefer recent repeated evidence;
3. preserve explicit preferences unless the user changes them.

## Retrieval

Do not dump every callback into context. Retrieve a few high-salience, high-confidence, not-overused memories.

Good callback selection balances:

- relevance;
- confidence;
- recency;
- underuse;
- diversity.

Repeatedly invoking the same successful line creates saturation and turns memory into a catchphrase machine.

Perceived memory matters relationally, but memory quantity is not the objective. Prefer a small number of well-timed, accurate callbacks over frequent demonstrations that the system remembers everything. A callback should feel relevant to the present exchange rather than surveillance-flavored.

When a callback lands well, increase its retrieval confidence modestly. When it falls flat, reduce valence and avoid immediate reuse. Never manufacture a memory the user did not provide.

## User control

Support:

- inspect current state;
- inspect recent decision history;
- inspect stored callbacks;
- forget a specific callback and scrub history events tied to that callback id;
- forget a specific stored interaction preference and scrub history events tied to that key;
- reset all persistent skill state with explicit confirmation.
