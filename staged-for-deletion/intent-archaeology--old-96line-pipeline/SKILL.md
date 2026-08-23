---
name: intent-archaeology
description: Reconstructs what a developer actually asked for across their whole project portfolio by mining coding-agent session logs, resolving which spec document version was really used, and auditing every project against recovered intent. Use this whenever the user wants to audit their projects, find out what is finished or abandoned, figure out what they asked for on a project, reconstruct intent from past sessions, resolve which PRD or requirements version was used, sort old ideas into incorporated and discarded and deferred, build a wiki from their own prompts, or prepare a stalled project to restart. Also use for phrases like "what did I ask for", "is this project done", "audit ~/code", "which requirements file did I use", "prompt archaeology", or "portfolio audit". Works across Claude Code, Codex, Gemini, Cursor, Aider, Pi, Hermes and other harnesses via cass.
license: MIT
compatibility: Requires Python 3.10+, cass (coding-agent-session-search), git, and jq. No network access required.
metadata:
  version: "0.1.0"
  author: "Ice-ninja"
---

# Intent Archaeology

Recover what the user asked for, from the record they already have, and compare it to what exists.

Three ledgers, never merged:

- **Events** are immutable. Raw turns, normalized. Never edited.
- **Intents** are derived. Recomputable from events at any time. Machine-owned.
- **Judgments** are the user's. Statuses they confirmed, disputes, overrides. Never overwritten by a rerun.

If a rerun can destroy the user's judgment, the pipeline is wrong. Derived output lives in `derived/`, which any rebuild may delete. Human output lives in `human/`, which no script may ever write.

## Before anything else

State lives in SQLite at `~/.intent-archaeology/archaeology.db`, not in this conversation. Every script is resumable. If a run dies, rerun the same command; it will pick up where it stopped. Never hold pipeline state in context.

Run `python3 scripts/00-init.py` first. It creates the database and checks that cass, git, and jq are present.

## Phase router

Run phases in order. Each has an exit criterion that is a query, not an opinion. Do not advance on "it looks done."

| Phase | Command | Exit criterion |
|---|---|---|
| 1. Inventory | `python3 scripts/01-inventory.py` | Every directory in the roots is classified as project, container, or unclassified, and the unclassified list has been shown to the user |
| 2. Attribute | `python3 scripts/02-attribute.py` | Attribution coverage by deterministic rungs is reported, and the rung 5+ residual has been spot-checked |
| 3. Enrich | `python3 scripts/03-enrich.py` | Event count is stable across two runs and `is_human` has been computed for every event |
| 4. Batch | `python3 scripts/04-batch.py --project <slug>` | A batch file exists with every candidate turn carrying a stable ID |
| 5. Classify | You do this. See below. | Every submitted ID has a verdict, including explicit `noise` verdicts |
| 6. Merge | `python3 scripts/05-merge.py --verdicts <file>` | Merge reports zero orphan verdicts and zero unmatched IDs |
| 7. Render | `python3 scripts/06-render.py` | Wiki files written, generated fences intact |
| 8. Retrospective | Read `references/retrospective.md` | Only after a run completes. Not before. |

Run `python3 scripts/status.py` at any time to see where the pipeline is.

## Phase 5 is yours

Scripts do not call models. Phase 4 emits a batch, you classify it, phase 6 merges the result. This keeps every model call in one place, keeps merges deterministic, and makes the run work in any harness.

To classify a batch:

1. Read `references/taxonomy.md`. Load it now, not earlier.
2. Read the batch file. It is a JSON list of candidate turns, each with an `id`.
3. Emit one verdict per turn to a JSON file. **Every `id` in the batch must appear in your output.** A turn that carries no intent gets `{"id": "...", "type": "noise"}`. A missing id is an error, not an empty result.
4. Never invent an intent that has no verbatim span in the turn. Every non-noise verdict carries `verbatim` quoted from the turn text.

Verdict shape:

```json
{"id": "evt_a1b2c3", "type": "directive.feature", "statement": "add rate limiting to the auth endpoint",
 "verbatim": "we need rate limiting on /auth", "scope": "feature", "confidence": 0.9}
```

Batches are item-capped, not token-capped, and deliberately not in chronological order. Both are intentional. Do not reorder them.

## Ordering

Process newest first. `04-batch.py` does this by default and you should not override it.

Reverse-chronological order makes the merge monotonic: every conflicting intent that arrives is older than what is already stored, so it can only be marked superseded. No status already assigned is ever revised. A run stopped at 60 percent is therefore a correct audit with a known cutoff, where forward order at 60 percent asserts currency for things superseded in the unprocessed remainder.

## Invariants

Violating any of these silently corrupts the output.

- **No intent without provenance.** Every intent row requires a verbatim span and at least one event id. `05-merge.py` rejects rows lacking either.
- **Verbatim is immutable.** Normalize into `statement`. Never touch `verbatim`. A pipeline that can edit its own evidence is not an audit.
- **`is_human` is computed and stored, never inferred at query time.** Sidechain turns are agent-authored prompts to subagents, not the user. Including them corrupts the frequency counts that generate constitution rules.
- **Repetition is counted, not deduplicated.** Five occurrences of one instruction is the strongest available signal of importance and of repeated non-compliance. Collapse to one intent with `occurrences: 5`, never to one line.
- **`scope.cut` is terminal.** An explicitly abandoned item may not be transitioned back to active by any automated process.
- **Phase C enumerates. Phase F searches.** Never the reverse. Using `cass search` to select the corpus for exhaustive distillation silently drops turns whose phrasing did not match the query.

## Reference files

Load only when the phase needs them.

- `references/attribution.md` - the deterministic project ladder. Phase 2.
- `references/taxonomy.md` - intent types and classification rules. Phase 5 only.
- `references/spec-archaeology.md` - resolving which spec version was used. Phase 4 onward.
- `references/lifecycle.md` - deriving project state and routing output by state.
- `references/rendering.md` - the prompt wiki structure and the generated-fence rule.
- `references/retrospective.md` - **post-run only.** Loading it early biases the run.

## Completion report

When a run finishes, report: phases completed; attribution coverage by rung; event and intent counts; the ID accounting balance from phase 6; unclassified directories still outstanding; and what phase runs next. Never report a single completion percentage. Report the status vector.
