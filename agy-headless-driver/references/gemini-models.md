# Gemini models in agy: Pro and Flash

Both draw from the Gemini pool, independent of the Claude pool. Using them never reduces Claude quota, and their work can run concurrently with Claude units. Record exact model ids from `/model` in `models.local.md` (display names like `"Gemini 3.5 Flash"` work with `--model` on some versions).

## Gemini Pro

Strengths to exploit: about 1M token context, fast long-document comprehension, broad cross-file mapping, strong multimodal input.

Best roles in a campaign:
1. **Context-pack builder.** Read the whole corpus (dossiers, transcripts, prior records) and emit the pack defined in `session-design.md`. Demand path:line citations for every summarized claim so the Claude unit can verify cheaply.
2. **Corpus mapper.** Produce a file index with anchors and line ranges for large trees, so Claude units probe precisely.
3. **Independent red team.** Review a finished Claude unit against the brief and the evidence. A different model family catches different failure modes, which makes the adversarial step genuinely adversarial.
4. **Whole-repo synthesis.** Architecture summaries, dependency maps, cross-document consistency checks where holding everything at once is the point.

Prompting notes:
- High residency is acceptable here; the pool and window are built for it. Still log stream-json and still use the driver.
- State the output schema exactly (headings, table columns, citation format). Pro follows explicit schemas closely.
- For pack building, require "verbatim" vs "summary" labels on each section so downstream units know what they can quote.

## Gemini Flash

Strengths to exploit: speed, high throughput, low latency per turn.

Best roles in a campaign:
1. **Mechanical verification.** Run validators, linters and conformance checks across many files; report failures only.
2. **Inventory and indexing.** Sizes, headings, anchors, line ranges for pack indexes.
3. **Pack pre-checks.** Confirm a freshly built pack has every schema section and that each SUMMARY row carries a `path:start-end` citation.
4. **Pre-flight checks.** Confirm paths exist, disk headroom, markers, snapshot integrity before a Claude unit launches.

Prompting notes:
- Give it deterministic, checkable instructions and a fixed output format.
- Pair each Flash unit with a script-level check of its output (row counts, path existence) in the driver's verify column.

## Weekly locks on the Gemini pool

The Gemini pool has its own 5-hour and weekly balances; premium Gemini models have shown multi-day timers too (forum reports of 5 and 6 day resets). The driver treats both pools identically: classify by reset duration, park the locked pool, continue the other.
