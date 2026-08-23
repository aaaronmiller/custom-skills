# Metric Vector (status vector)

> **When to read:** before Phase 7 (three-way join), or when reporting
> results. Never report a single completion percentage.

## The status vector

Every project gets a status vector, not a scalar. The components sum to
1.0 across a project's intent items.

| Component | Definition |
|-----------|------------|
| `completed` | Intent is in the spec, in the repo, and matches |
| `in_progress` | Intent is in the spec, partially in the repo, recent activity |
| `drifted` | Intent is in the spec, in the repo, but built differently |
| `superseded` | Intent was in an older spec version, replaced by a newer one |
| `abandoned` | Intent was in the spec, not in the repo, with evidence of intentional cut |
| `not_begun` | Intent is in the spec, not in the repo, no evidence of cut |

## Why a vector, not a scalar

A scalar hides `drifted`, `superseded`, and `abandoned` — which are the
three categories you built this to find. A scalar will send your
sleep-time agent to rebuild things you deliberately cut.

Concrete example: project X is "80% complete". Sounds great. The vector
reveals: 80% completed, 5% drifted (built differently, will cause
regressions), 10% abandoned (intentionally cut, do not resurrect), 5%
not begun. The scalar said "ship it"; the vector says "fix the drift,
don't touch the abandoned, plan the not-begun".

## How the join computes the vector

For each intent item (Phase 6 output), Phase 7 asks three questions:

1. Is the intent in the canonical spec? (Yes/No/In older version)
2. Is the intent in the repo? (Yes/No/Partial)
3. Is there evidence of intentional cut? (Yes/No)

| In spec? | In repo? | Cut? | Status |
|----------|----------|------|--------|
| Yes | Yes | No | `completed` (verify match — if no match, `drifted`) |
| Yes | Partial | No | `in_progress` |
| Yes | No | No | `not_begun` |
| Yes | No | Yes | `abandoned` |
| Older version | (any) | (any) | `superseded` |
| Yes | Yes, differently | No | `drifted` |

The "built differently" check is the hardest. Phase 7 uses a
similarity score (LLM-judged, with the spec text and the relevant code
diff as input). Below the threshold, it's `drifted`. The threshold is
calibrated against a held-out set — see `references/eval_protocol.md`.

## Anti-metrics (what NOT to report)

These are explicitly forbidden in the status vector report:

- **Single completion percentage.** Loses the three categories that
  matter.
- **Lines of code per intent.** Rewards verbose implementations.
- **Time spent per intent.** Penalizes careful work.
- **Agent turn count per intent.** Penalizes necessary iteration.

The ICLR 2026 reward-hacking finding (73.8% / 46.8% of optimizations
showed proxy gains with no held-out real-task gain) is the cautionary
tale. Anti-metrics exist because they will be gamed if reported.

## What the sleep-time agent consumes

The sleep-time agent reads the status vector and uses it to prioritize
work:

- `not_begun` intents on `in-progress` projects → highest priority
- `drifted` intents → high priority (regression risk)
- `in_progress` intents on `in-progress` projects → medium priority
- `completed` → skip
- `abandoned` → NEVER touch (cross-reference `abandoned.md`)
- `superseded` → skip (older version, already replaced)

The vector is written to SQLite (`status_vectors` table) and optionally
to beads if installed (so the sleep-time agent's task queue picks them
up automatically).
