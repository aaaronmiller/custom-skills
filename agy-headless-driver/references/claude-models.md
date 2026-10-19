# Claude models in agy: Opus and Sonnet

Both draw from the partner pool (shared with GPT models). Both see a 200k ceiling in agy. Model ids vary by account and version: record the exact strings from `/model` in `models.local.md` (observed: `claude-opus-5-5-high`, where the suffix encodes effort).

## Opus

Strengths to exploit: long-horizon judgment, adversarial self-critique, synthesis across many constraints, holding a ten-seat council with distinct voices, noticing what earlier passes missed.

Getting exceptional output:
- Give it the problem, not the corpus. A tight pack plus probe access beats a preloaded archive: less residency means more of each turn goes to reasoning about what matters.
- Use the operator's effort setting. Deep thinking is where Opus quota pays for itself.
- Ask for an explicit plan-of-attack written to disk at the start of the unit (which probes, which files, which order). It anchors a long session and gives resume a foothold.
- For councils: name every seat with a one-line mandate in the pack so seats stay distinct across rounds without re-explaining; force an adversarial seat if round 1 is unanimous.
- Probes must be real and cited. Opus will reason confidently from memory if allowed; the operating contract forbids it.
- Let it challenge prior units with evidence. Independent second opinion is usually why an operator re-runs Opus over earlier work.

Residency discipline specific to Opus:
- Prior pass records become decision tables in the pack; the full records stay on disk for spot checks.
- Large reference skills (deliberation protocols, spec templates) go into the pack as tight excerpts of the binding rules, with pointers to the full file for edge cases.

## Sonnet

Strengths to exploit: sustained agentic execution, many accurate edits, test-driven iteration, following a detailed plan precisely.

Getting exceptional output:
- Hand it a plan produced by an Opus unit (or the operator) as part of the pack. Sonnet executes a precise plan with excellent fidelity.
- Turn counts run high in implementation units, so quiet tooling matters most here: test runners in quiet mode, failures only, `tail` on build logs.
- Commit or snapshot in small verified increments inside the unit so a cut-off loses minutes, not the unit.
- Ask it to keep a running `progress.md` with one line per completed step; the resume protocol uses it.

## Choosing between them

Follow the operator's choice. If the operator leaves it open, the natural split is: judgment units (design, deliberation, review, red team) on Opus; execution units (implement, migrate, refactor, apply adopted changes across many files) on Sonnet. Both run at the operator's effort level.
