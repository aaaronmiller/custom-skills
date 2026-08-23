# Retrospective

**Load this only when a tranche or a run has completed.** Loading it earlier
biases the run toward producing findings that make the retrospective look good.

This is not a summary. It is a fixed interrogation, and every question is
answered by a query rather than by recollection.

## Question zero, before all others

**Does the run still serve what was asked for?**

For each step of the original brief, name the artifact that satisfies it and
the query that proves the artifact exists. A step with no artifact is a gap.
An artifact serving no step is drift. If the answer here is no, none of the
metric questions below matter.

This question exists because a metric vector cannot detect that the system is
answering a different question than the one asked. A self-improving system
needs a fixed point that is not part of what it improves.

## The seven

1. **Where did the pipeline hesitate?**
   `SELECT kind, COUNT(*) FROM observation GROUP BY kind;` Look for clusters,
   not totals.
2. **Where did proposer and verifier disagree, and is there a pattern?**
   A pattern in the input spans is a taxonomy gap. A pattern in the projects
   is an attribution problem.
3. **What did the human reject?** The highest-value signal available. Group by
   intent type.
4. **Which turns produced nothing?** A high discard rate in one project usually
   means that project's intent lives somewhere the pipeline is not looking.
5. **Did ID accounting balance?**
   `SELECT id, ids_submitted, ids_returned FROM batch WHERE ids_submitted != ids_returned;`
   Any shortfall is the silent-omission failure and it is the most important
   check in this list.
6. **What did the run cost and what did it buy?** Tokens spent against intents
   accepted, per tranche. A worsening ratio means the loop is the problem.
7. **What would you change, and can you prove it?** Every proposed edit must
   name the observations that motivated it, the calibration delta it predicts,
   and the metric components it might regress. Proposals lacking all three are
   discarded unread.

## Rules for acting on this

- Observations accumulate during a tranche and change nothing until it ends.
- An edit is accepted only if it improves a held-out calibration set **without
  regressing any component of the metric vector.** Published figures put naive
  self-optimization at improving the proxy without improving the objective
  roughly half to three quarters of the time. Assume you are in that range.
- Editable surface is exactly: the classification prompt, `taxonomy.md`, the
  item cap, the confidence thresholds, and the noise filter. Everything else,
  and `05-merge.py` in particular, is read-only to this loop.
- Two timescales. Do not touch merge logic until three consecutive tranches
  show no gain from prompt-level changes.
- Every accepted edit records the prior version. If the vector degrades across
  two tranches, revert to the last known-good configuration.

Output goes to `human/retrospective-<tranche>.md`. This process never edits
anything directly.
