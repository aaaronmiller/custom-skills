# Failure Modes (ranked)

> **When to read:** when something goes wrong. Ranked, so read top-down
> until you find the one that matches.

## #1. Proposer and verifier are the same agent

**Symptom:** the status vector looks too clean. Everything is
`completed` or `not_begun`, no `drifted` or `superseded`.

**Cause:** Phase 6 (intent distillation) and Phase 7 (three-way join)
were run by the same model in the same context. The verifier inherits
the proposer's blind spots.

**Fix:** run Phase 6 and Phase 7 as different processes, ideally
different models. The script layer enforces this via separate
invocations; the prompt layer cannot enforce it.

**Severity:** critical. Silently corrupts the audit.

## #2. cass search used for Phase C

**Symptom:** the audit misses prompts you know you typed.

**Cause:** Phase 5 used `cass search "<topic>"` instead of
`cass search "" --workspace ... --robot-format sessions --days N` plus per-session
`cass export`. Search recall for content queries depends on BM25+vector fusion; a turn
phrased in unqueried vocabulary silently never appears.

**Fix:** Phase C always enumerates. Phase F (cited evidence against a
specific question) is the only place `cass search` belongs.

**Severity:** critical. Disqualifying for an audit whose deliverable is
completeness.

## #3. Extracting only user prompts at ingest

**Symptom:** the audit can't explain why a feature was built — there's
no evidence of the tool calls, file paths, or errors that surrounded
the user's instruction.

**Cause:** the ingest pipeline filtered to `is_human`-tagged messages
before storing. The evidence layer was thrown away.

**Fix:** ingest everything once via `cass export ... --include-tools`;
project the human prompts as a view. See `references/cass_fidelity.md`.

**Severity:** high. Not recoverable without re-ingesting.

## #4. Reward hacking in the meta-learning loop

**Symptom:** the held-out score rises tranche after tranche, but the
wiki quality (as judged by reading it) doesn't improve, or actually
declines.

**Cause:** an edit to the skill improved one metric component at the
cost of another, and the aggregate score hid the regression.

**Fix:** never accept an edit that improves the held-out score **at
the cost of regressing any component of the metric vector**. The ICLR
2026 finding: 73.8% / 46.8% of optimizations showed proxy gains with
no held-out real-task gain. See `references/metric_vector.md` for the
anti-metrics list.

**Severity:** critical. Silently corrupts the self-improvement loop.

## #5. Token-based session splitting

**Symptom:** supersession detection fails. An intent that was clearly
revised later shows up as a duplicate, not a supersession.

**Cause:** a long session was split in half to fit a context window,
and the revision spanned the split.

**Fix:** split on session boundary, then topic segment, then reduce
with a stateful delta accumulator. Token budget is a backstop, not a
splitter.

**Severity:** high. Breaks the audit's core mechanism.

## #6. Scalar completion percentage reported

**Symptom:** the sleep-time agent rebuilds an abandoned feature.

**Cause:** the status vector was collapsed to a scalar, hiding the
`abandoned` component.

**Fix:** always report the full vector. See
`references/metric_vector.md`.

**Severity:** high. Causes the wrong autonomous action.

## #7. Retrospective loaded mid-tranche

**Symptom:** the tranche produces findings that suspiciously match the
retrospective's question list, but the underlying data doesn't support
them.

**Cause:** `references/retrospective.md` was loaded before Phase 9,
biasing the run toward producing findings that make the retrospective
look good.

**Fix:** the retrospective is loaded only by
`10_post_completion_audit.py`. The skill explicitly refuses to load it
earlier.

**Severity:** medium. Corrupts the meta-learning signal.

## #8. Markdown graveyard

**Symptom:** the wiki grows but stops being useful. Humans edit the
generated blocks, the generator overwrites them, humans stop editing,
the wiki rots.

**Cause:** no enforcement of the generated-block fence rule.

**Fix:** `scripts/lint_wiki.py` fails the build on any human edit
inside a `BEGIN GENERATED` / `END GENERATED` fence. See
`references/frontmatter_schema.md`.

**Severity:** medium. Slow but terminal.

## #9. Era misclassification

**Symptom:** spec archaeology produces garbage for a project that
should be era 5 but was classified as era 3.

**Cause:** Phase 2 missed a `LIVING.md` file in a subdirectory, or
the living document doesn't have v3.x frontmatter.

**Fix:** Phase 2 scans recursively and is conservative (prefers the
higher era). If you see this, check `era_overlap` in the projects
table for evidence of multi-era markers.

**Severity:** medium. Affects one project, fixable by re-running
Phase 2.

## #10. Scope drift across tranches

**Symptom:** a re-pass with a "wider" scope actually narrows the
results, or vice versa.

**Cause:** the scope was described informally ("all my recent stuff")
and interpreted differently across tranches.

**Fix:** scope is always persisted as a structured ScopeSpec, hashed
for identity. Re-runs use the same scope_hash or create a new one —
never silently merge.

**Severity:** low. Annoying, not corrupting.
