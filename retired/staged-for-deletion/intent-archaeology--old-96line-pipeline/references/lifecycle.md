# Lifecycle routing

Different project states need different outputs. Treating them uniformly
produces a gap list for a project that has not started and a build plan for
one that is finished.

## Derive, then confirm

Lifecycle state is itself an audit finding, so derive it from signals, propose
it, and have the human confirm. Misrouting sends a whole project down the
wrong pipeline.

Signals: days since last commit; days since last session; `tasks.md` checkbox
ratio; test presence and pass state; whether the entry point runs; whether the
README claims completion; count of TODO and FIXME; whether any spec exists.

| State | Signature | Output artifact |
|---|---|---|
| `not-started` | Spec docs exist, little source, few sessions | Canonical spec plus the four idea buckets |
| `in-progress` | Recent sessions, partial tests, unchecked tasks | Canonical PRD plus updates, plus the gap list |
| `complete` | No recent sessions, tests pass, tasks checked | Canonical PRD plus a verification report and `last_verified` |
| `revision` | Complete, then new sessions or spec versions appear | **Change-level spec** for the next change only |
| `archive-candidate` | Long dormant, no tests, superseded by a sibling, or abandoned in the logs | Archive recommendation with evidence, nothing else |

`archive-candidate` exists because an audit that cannot recommend killing a
project is a completion engine wearing an audit costume. Expect a meaningful
fraction of the older root to land here.

For `revision` projects do not generate a whole-system reverse-engineered
spec. A derived spec becomes a misalignment source, and new work built against
it raises regression risk. Write a change-level spec bounded to the next
change: current behaviour, target behaviour, invariants, scope boundaries.

Record actual behaviour including bugs, marked as bugs. A bug documented as a
feature is recoverable; a bug silently rewritten into intent is not.

## Status vocabulary

Deliberately more granular than done and not-done.

`implemented_verified` code plus a test or runtime check ·
`implemented_unverified` code, no test · `partial` some acceptance conditions ·
`missing` no evidence · `drifted` built differently from the stated intent ·
`superseded` replaced by a later intent · `abandoned` explicitly cut ·
`unverifiable` intent too vague to check.

`drifted` and `unverifiable` are why this audit is worth running. Every naive
tool produces done and not-done. A project with 40 percent unverifiable
intents does not have a completion problem, it has a specification problem,
and the remedy is different.

**Never report a single completion percentage.** Report the vector. A scalar
hides `drifted`, `superseded` and `abandoned`, which are the three categories
you built this to find.
