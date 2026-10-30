# Description Revision Guide (Corrected)

## First: Understand What Descriptions Actually Do

The `description:` field in YAML frontmatter is the SKILL ACTIVATION MECHANISM.
It is what the model uses to decide: "Should I load this skill right now?"

**Long descriptions with detailed trigger coverage = BETTER activation accuracy.**
More trigger phrases means the model is more likely to correctly identify when
the skill should fire.

## When to Expand, Not Contract

Many descriptions need MORE triggers, not fewer. If a skill has no "Use when:"
or "Triggers:" patterns, the model will struggle to activate it correctly.

### Signs a description needs MORE triggers

- Only has a name and one-liner with no trigger conditions
- Has no "Use when:" or "Triggers:" fields
- Describes WHAT it does but not WHEN to use it
- Has generic triggers that could match anything

### Expansion pattern

```
BEFORE (18): "Database optimization, query tuning, schema design."
AFTER  (42): "Use when: optimizing database performance, query tuning, schema design, or DB best practices.
Triggers: 'slow query', 'index', 'query plan', 'performance bottleneck', 'optimize SQL'."
CHANGE: Added 5 trigger phrases for better model matching. +24 tokens (worth it).
```

## When to Safely Trim

Only remove content that does NOT affect trigger coverage:

| Safe to Remove | Example | Reason |
|---------------|---------|--------|
| Version strings | "vLLM: ... version: 1.0.0" → "vLLM: ..." | Already in `version:` field |
| URLs | "Docs at https://..." | Belongs in body/references |
| Markdown artifacts | Markdown headers leaking into frontmatter | YAML parsing error |
| Redundant boilerplate | "This skill should be used when" → "Use when" | Same meaning, shorter |

| NOT Safe to Remove | Reason |
|-------------------|--------|
| "Use when:" preamble | It's the activation instruction |
| Trigger phrases | They're the matching surface |
| "Triggers:" list | Model pattern-matches against these |
| "AUTOMATIC ACTIVATION:" | Forces activation without user request |
| Content type lists | Helps match by output format |

## Before/After (CORRECT Example)

```
skill-name (path):
BEFORE (63): "ALWAYS invoke when building SvelteKit projects to verify Svelte 5 syntax compliance,
check metrics, and debug common build errors. Triggers: 'build error', 'sveltekit build', 'vercel deploy'."
AFTER  (58): "Use when building SvelteKit projects: verify Svelte 5 syntax, check metrics, debug build
errors. Triggers: 'build error', 'sveltekit build', 'vercel deploy'."
SAVINGS: 5 tokens (removed "ALWAYS", swapped "invoke when" for "when building").
Reason: Preserved all 3 trigger phrases. Only removed ALL CAPS style choice.
```

## Token Budget Reality

With 260 skills at ~47 tokens avg = ~12,330 total.
Safe trimming (no trigger removal) saves at most ~400-800 tokens.

**Under 10K is achievable. Under 5K requires architecture changes.**
Do not trim triggers to force a lower budget.
