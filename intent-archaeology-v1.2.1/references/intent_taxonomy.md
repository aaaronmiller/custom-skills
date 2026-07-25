# Intent Taxonomy (closed vocabulary)

> **When to read:** before Phase 6 (intent distillation), or when the
> `intents.type` column needs explanation.

## The closed vocabulary

Every distilled intent is labeled with exactly one type from this
closed set. Closed means closed — adding a new type requires a
deliberate schema migration, not a runtime decision. Open vocabularies
drift; closed vocabularies accumulate comparable frequency counts
across tranches.

| Type | Definition | Example |
|------|------------|---------|
| `question` | Asks for information or explanation | "why is the auth middleware double-fetching the user?" |
| `command` | Directs the agent to do something | "add a /health endpoint to the api" |
| `correction` | Reverses or fixes a prior agent action | "no, use Postgres not MySQL — revert that" |
| `scope-cut` | Removes a feature or requirement from scope | "drop the admin dashboard for v1, we'll do it later" |
| `scope-add` | Adds a feature or requirement to scope | "actually we need audit logging too" |
| `spec-reference` | Points at a spec/PRD/requirements file | "use the requirements.md I attached, specifically the user stories section" |
| `bug-report` | Reports unexpected behavior | "the login flow crashes on Safari 17" |
| `constraint` | States a non-negotiable rule | "never log PII, even at debug level" |
| `preference` | States a negotiable preference | "I prefer the typed variant but it's not required" |
| `noise` | Off-topic, side-task, or no extractable intent | "brb getting coffee" / "test test test" / pasted log with no instruction |

## Why these ten and not more

The taxonomy was designed by looking at what changes the audit. A
`question` rarely changes scope; a `scope-cut` always does. A
`correction` is the highest-signal intent type — it's the user
explicitly saying the agent got something wrong, and frequency of
corrections per project is a leading indicator of `drifted` in Phase 7.

`noise` is in the set deliberately. Phase 6 must return a verdict for
every submitted turn ID — including an explicit `noise` verdict for
turns that yielded nothing. A missing ID is an error, not an empty
result. See SKILL.md rule on per-turn coverage.

## Multi-intent turns

A single user turn can carry multiple intents. Phase 6 emits one row
per intent, all sharing the same `prompt_id`. The wiki renders these as
a bulleted list under the turn.

## How type frequency is used

Cross-tranche, type frequency is the early-warning system:

- Rising `correction` rate → agent is drifting, not learning
- Rising `scope-cut` rate → project is converging on a smaller true scope
- Rising `constraint` rate → constitution is being discovered in real-time
- `noise` rate > 15% → extraction is too permissive, tighten the filter

The cross-cutting wiki page `corrections_by_era.md` answers whether
the standing instructions are actually being read: if `correction`
frequency for the same constraint rises over time, the constraint is
being ignored.

## What NOT to do

- Don't add ad-hoc types like `meeting-note` or `chitchat` mid-tranche.
  File a schema migration issue instead.
- Don't collapse `scope-cut` and `scope-add` into a single `scope-change`
  type. They have opposite audit implications.
- Don't relabel old tranches when the taxonomy changes. The
  `taxonomy_version` column on `intents` records which version was in
  effect; cross-tranche comparisons join on it.
