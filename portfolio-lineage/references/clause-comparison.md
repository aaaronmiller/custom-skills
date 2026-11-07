# Clause-level comparison

Paths are relative to `~/work/jobs/lineage-archive/in/` unless stated.

## Why it exists

The foundation plan requires that a clause-by-clause comparison confirm
nothing unique is lost before archiving. The 2026-11-03 lineage report found
Atlas had no such pass: "Gap: clause-level comparison. Atlas compares purpose,
Git, fingerprints and spec hashes ... Add a COVERED/PARTIAL/UNIQUE pass per
requirement; this file is the manual prototype"
(`lineage-2026-11-03/routing-archive-atlas.md` line 207). The register made it
row C271 (`durable-agent-plan-2026-11-04.md` line 350, "Clause-level comparison
(covered, partial, unique) before anything is archived") and the spec made it
DA-034.

## The unit rule and the three marks

From the manual prototype, `lineage-2026-11-03/durable-agent-attempts.md`:

- line 127: "a clause is a numbered normative requirement (SPEC-n). A non-clause
  item is a decision, principle, task-level idea or asset assessed on its own.
  COVERED means Workbench states it with equal or stronger force."
- line 22: PARTIAL means the successor "states the behavior but omits a
  precision, number or edge case"; the result there was 80 distinct clauses,
  39 COVERED, 34 PARTIAL and 7 UNIQUE, plus 13 non-clause items absent.
- line 13: the method was "read-only comparison, clause by clause" against the
  successor's spec, plan, research, data model and contracts.

This skill extends "clause" to the forms plans use as well: ID rows (SPEC-001,
DA-032, C054, U14, T045, D01), table rows that start with an ID, capitalised
SHALL or MUST statements, and numbered items under requirement, decision, rule,
invariant, principle, constraint, guarantee or acceptance headings. Unnumbered
ideas in prose are not clauses; finding those is the idea sweep described in
project-archive `references/method.md`, which stays a reader's job.

## How the mechanical pass marks a clause

For each source clause, every successor clause and paragraph is scored:
0.6 x the share of the clause's content words found in the candidate, plus
0.2 x Jaccard overlap, plus 0.2 x the sequence ratio of the normalised texts.
Identical normalised text scores 1.0. Cross-reference tags such as `[EVAL-001]`
or `SPEC-012` are removed before scoring, and simple endings (-ing, -ed, -es,
-s) are stripped so "restarts" matches "restart".

| Mark | Rule |
|---|---|
| covered | score 1.0, or score at least 0.80 with every precision token present |
| partial | score at least 0.45 otherwise; `missing_precision` lists what the match lacks |
| unique | best score below 0.45 |

Precision tokens are numbers (200, 60, 0.85), `code spans`, all-capital terms
other than the EARS keywords (for example FULL, NORMAL and WAL; mixed-case words
such as SQLite are not counted), and dotted or underscored identifiers. This matches the prototype's sense of
PARTIAL: the behaviour is there, a precision is not.

## Calibration on real data (2026-11-07)

Argon's spec (`DURABLE-AGENT/Argon/durable-agent-stack-repo/specs/001-durable-agent-stack/spec.md`,
53 clauses including EVAL definitions) was compared against the Workbench spec
folders 001 and 002 as they stand in `~/work/jobs/da-integrate/out/agentic-workbench/specs/`
(130 Markdown files). For the 24 SPEC clauses the 2026-11-03 ledger marked by
hand (`durable-agent-attempts.md` lines 147 to 170):

| Hand mark | mechanical covered | mechanical partial | mechanical unique |
|---|---|---|---|
| COVERED (15) | 0 | 4 | 11 |
| PARTIAL (8) | 0 | 0 | 8 |
| UNIQUE (1) | 0 | 0 | 1 |

No clause was marked more covered than the hand ledger (no unsafe error), and
the one true unique clause was found. But 19 of the 23 clauses the hand ledger
found covered or partial came out unique: the Workbench restates them in other
words, and a lexical score cannot see that. So on real folders expect most
rows to need a reviewer's override or a destination. The thresholds were not
lowered, because a false "partial" would pass the gate and lose content. A
model-based reviewer can write `overrides.json`; the ledger keeps its reason.
The Workbench files used may differ from the 2026-11-03 baseline, which lived
on another machine.

## Reviewing

The score is lexical. It errs toward partial or unique when the successor
paraphrases, which is the safe direction: a false unique only asks a reviewer
to record a destination or an override. A false covered needs a high score with
all precision tokens present.

Review every partial and unique row and record judgements:

```json
{"spec.md#SPEC-021": {"mark": "partial", "reason": "hazard register row C242 states it", "by": "reviewer name"}}
```

The ledger keeps `mechanical_mark` beside the reviewed `mark`, with
`basis: override`, so the judgement stays auditable.

## Destinations

A destination says where the unique content now lives, so archiving loses
nothing: a file it was copied to, a register row, a task. The gate needs one for
every unique clause. Local-path destinations must exist when the gate runs.
Plan section 6 (`durable-agent-plan-2026-11-04.md` lines 756 to 770) is the
worked example: per-folder copy-out tables, and a gate that every copy-out
exists at its destination before any move.
