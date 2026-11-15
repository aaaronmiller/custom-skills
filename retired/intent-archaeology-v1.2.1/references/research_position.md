# Research Position

> **When to read:** when the user asks "is this S-tier" or "what's the
> research framing". Not needed for normal operation.

## The field has four names

This skill sits at the intersection of:

- **Mining Software Repositories (MSR)** — ACM/IEEE conference,
  twenty-plus years, systematic mapping studies running through 2026.
- **Requirements Traceability Link Recovery (TLR)** — a named task
  with established metrics. Technique lineage: VSM → LSI →
  Jensen-Shannon → hierarchical Bayesian → RAG+LLM (LiSSA, ICSE 2025).
  Precision/recall/F1 are standard; two decades of comparable numbers.
- **Requirements generation from repositories** — UserTrace (2025)
  does user-level requirements generation plus traceability recovery
  from project repos.
- **LLM agent trajectory analysis** — brand new, a 2026 survey
  already exists. Trace2Skill and ALIGNXPLORE are near-identical to
  mechanisms invented independently here.

## The genuine contribution

TLR spent twenty years doing information retrieval between requirement
docs and code *because intent was never recorded*. Every technique in
that lineage exists to recover a signal lost at the moment it was
produced, and the precision ceilings in that literature are a
consequence of working from lossy proxies.

The agent-log corpus doesn't have that problem — intent is there
verbatim, timestamped, in the developer's own words, with the code
change adjacent. That's a categorically better input than anything
the field has had, available only because coding agents started
writing everything down two years ago.

The three-way join is good architecture. The observation that agent
logs dissolve the central difficulty of a mature research field is
the actual contribution.

## Where it isn't S-tier, honestly

- **There are no numbers.** TLR reports precision/recall/F1 against
  shared datasets. This skill's metric vector is reasoned, not
  validated — no baseline, no labeled set yet, nothing to compare
  against. That's the single largest gap between this and a field
  contribution. `[GAP-06]`, `[GAP-14]`
- **N=1.** One corpus, one document-era history, one harness stack,
  one prompting style. The era typology in particular is
  autobiography.
- **Complexity is the wrong axis.** Asking whether this is the most
  complex alternative — it probably is, and that's the risk not the
  win. Every comparable system is narrow and shipped. This one is
  broad and unbuilt.
- **The ledger has no runtime interface.** cass-memory ships an MCP
  HTTP server and a single `cm context "<task>"` call agents make
  before starting work. This skill emits files a human reads. That
  difference decides whether it's infrastructure or a report.
- **The loop is open.** Output terminates at a wiki and a work queue
  rather than feeding back into session start. The system observes
  work without participating in it.

## What would close it, ranked

1. Publish the benchmark. The field has none for intent reconstruction
   from agent logs. A labeled set plus a metric is a contribution
   regardless of the pipeline behind it.
2. Expose the ledger over MCP. Close the loop so sessions start by
   querying recovered intent.
3. Emit skills rather than only prose rules, per Trace2Skill.
4. Test on one other person's corpus.
5. State the thesis: vibe coding says review is optional and intent
   is disposable. This is a bet that intent is durable, recoverable,
   and worth recovering. That's a counter-position, not just tooling,
   and positions get cited while tools get forked.

## Verdict

Ahead of every comparable system on architecture and currency, because
they each solve one layer and this joins three. Behind all of them on
evidence, because they shipped and reported and this hasn't run. The
gap isn't conceptual — it's that the strongest available claim today
is "should work" and the field's currency is "did work, here are the
numbers."

Cheapest path to S-tier isn't more architecture. It's Phase 4: one
project, end to end, hand-labeled, numbers published.

## The sixteen gaps (for the alpha research paper)

These are stated directly and left absent with a note for later
correction. None are filled by inference.

- `[GAP-01]` Calibration set definition
- `[GAP-02]` Source independence formal test (cheap, do first)
- `[GAP-03]` Contamination delta measurement (cheap, do first)
- `[GAP-04]` Labeled set construction protocol
- `[GAP-05]` Triangulation vs. round-trip distinction formalization
- `[GAP-06]` Corpus statistics
- `[GAP-07]` Inter-annotator agreement
- `[GAP-08]` Baseline system
- `[GAP-09]` Intent-matching function (load-bearing methodological choice)
- `[GAP-10]` Source independence (honest answer: sources are plainly not independent)
- `[GAP-11]` Privacy-preserving dataset release
- `[GAP-12]` Cross-corpus replication
- `[GAP-13]` Longitudinal stability of intent labels
- `[GAP-14]` Gold standard
- `[GAP-15]` Statistical significance testing
- `[GAP-16]` Reproducibility (model versions, prompt versions)

Recommended order: `GAP-02` and `GAP-04` first (cheap, can
invalidate the framing). Then `GAP-06` and `GAP-09` (load-bearing).
Then `GAP-14` (gold standard, enables everything else).

## Prompt to resolve omissions

```
For each [GAP-NN] marker in references/research_position.md:
1. State the gap precisely.
2. Identify whether existing literature already resolves it
   (search MSR, TLR, ICSE, ICLR, ICML 2024-2026 proceedings).
3. If resolved, cite and downgrade the contribution claim accordingly.
4. If unresolved, propose the cheapest experiment that would close it.
5. Estimate the cost (hours, labels required, compute).
6. Output as a table: gap | resolved? | citation or experiment | cost.
```
