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

## Careful-Touch Rules (2026-11)

The description decides whether the skill loads at all. Edit it by hand, one
skill at a time, never in bulk and never with a low-capability model. Every
rewrite passes the trigger-loss gate before it ships:

```bash
python3 scripts/audit_mechanical.py <skills-root> --baseline HEAD
```

### The core rule: cut prose pleonasm, keep trigger pleonasm

A pleonasm is a redundant expression: "in order to", "join together",
"end result", "this skill should be used when". Redundancy has two kinds in a
description, and they are treated in opposite ways.

| Kind | Example | Treatment |
|---|---|---|
| Prose pleonasm | "This skill is designed to help you in order to create..." | Cut first. It costs characters and carries no matching signal. |
| Trigger pleonasm | "go viral", "make this viral", "shareable", "spread" | Keep. Each synonym catches a different phrasing; the redundancy is the recall. |

Only after all prose pleonasm is gone may a trigger be merged, and then only
when two phrases are the same words in another order or differ by an
inflection the model already generalizes ("audit skill" / "audit skills").

### Hard and soft limits (checked 2026-11-10)

| Limit | Value | Source | Audit level |
|---|---|---|---|
| Maximum length | 1024 chars | Anthropic quick_validate.py, agentskills.io, Codex | ERROR |
| Codex budget shortening | over 500 chars is shortened first when the skill list exceeds 2% of context (8,000 chars default) | openai/codex skills loader | WARN |
| Claude Code listing | description plus `when_to_use` truncated at 1,536 chars; rarely used skills dropped first under the 1% budget | Claude Code skills docs | covered by 1024 |
| claude.ai help center | 200 chars | Anthropic help center, enforcement unverified | not enforced |
| Characters | no `<` or `>` | quick_validate.py, claude.ai | ERROR |
| Format | one physical line; double-quoted with triggers in single quotes | gemini-cli validate_skill.cjs | WARN |

Codex also reads an optional `metadata.short-description` for compact
listings. Add one (under 100 chars) when the full description runs long.

### Order of content

1. **Key use case first, in third person:** "Audits skill ecosystems for...",
   not "I can help" or "You can use". Truncation cuts from the end, so the
   first sentence must stand alone.
2. **"Use when ..."** situations, most frequent first.
3. **"Triggers:"** quoted phrases (single quotes inside the double-quoted
   value), the user's own words rather than the skill's vocabulary.
4. Content-type lists and edge cases last.

### Trim order when over a limit

1. Prose pleonasm and boilerplate ("This skill", "designed to", "in order to").
2. Version strings, URLs, author names (they belong in metadata or the body).
3. Restated words: a noun already in the name, a "Use when" item that repeats
   a trigger verbatim.
4. Content-type lists, longest first.
5. Never: quoted triggers, the first sentence's use case, an "AUTOMATIC
   ACTIVATION" instruction the skill depends on.

If a description cannot fit without step 5, the skill is doing too much:
split it, or move the overflow into `when_to_use` (Claude Code only) and
record why.

### Rewrite checklist

- [ ] Prose pleonasm removed; trigger synonyms intact.
- [ ] First sentence states the use case in third person.
- [ ] Every quoted trigger from the baseline still present (`--baseline` reports none lost).
- [ ] At most 1024 chars; under 500 or front-loaded so a Codex cut keeps the use case.
- [ ] One physical line, double-quoted, no inner `"`, no `<` or `>`.
- [ ] Read the old and new versions side by side once, aloud, before shipping.
