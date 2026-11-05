---
name: intent-refresh
description: Scheduled refresh of the intent record. Brings the intent archaeology database (the one intent-find reads) and every Living Documents dossier's prompt-corpus and intent-archaeology pages up to date with agent sessions since the last run. Use when the cron job intent-refresh summons an agent, or when asked to "refresh intent archaeology", "update the intent database", "intent-find says stale", or "update the archaeology pages".
metadata:
  author: ice-ninja
  version: "1.2.0"
  created: 2026-11-05
  requires: "python3, ld, ld-audit, intent-find; this skill's pipeline/ folder"
  reads: "~/.intent-archaeology/archaeology.db, agent session files on disk, ~/code, ~/code2, ~/LIVING_DOCUMENTS"
  writes: "~/.intent-archaeology (database, batches, verdicts, derived/), ~/LIVING_DOCUMENTS/projects/*/ (prompt-corpus.md and intent-archaeology-*.md), ~/.local/state/intent-refresh/"
---

# intent-refresh

One run brings the intent record current. The black-magic loop answers questions from this record. Every week it is not refreshed, more already-answered questions come back to the operator as false blockers.

## Which pipeline, and why it lives here

`intent-find` and the black-magic loop read `/home/cheta/.intent-archaeology/archaeology.db`. That database is written by the phase scripts in `pipeline/` here (`00-init` to `06-render`).

The intent-archaeology skill's own `scripts/` folder (`01_discover_projects.py` and the rest) targets a different database, `state.db`. That file has never existed on this machine.

On 2026-08-22, commit 1fa3155 in custom-skills ("consolidate colliding skills") staged the working pipeline for deletion as `staged-for-deletion/intent-archaeology--old-96line-pipeline`. The deployed skill copy then lost its `lib/` package and stopped running. `pipeline/` is a verbatim copy of that staged folder (copied 2026-11-05) so this job keeps working. Which pipeline is canonical is an open question for the operator, recorded on the masterplan dossier. Until it is settled, this job uses `pipeline/`.

## Fixed paths

| What | Path |
|---|---|
| Database | `/home/cheta/.intent-archaeology/archaeology.db` |
| Pipeline | `/home/cheta/code/custom-skills/intent-refresh/pipeline/` (run every script by absolute path: `python3 -I /home/cheta/code/custom-skills/intent-refresh/pipeline/<script>.py`) |
| Classification rules | the docstrings of `pipeline/04-batch.py` and `pipeline/05-merge.py`, and `/home/cheta/code/custom-skills/intent-archaeology/references/intent_taxonomy.md` |
| Batches and verdicts | `/home/cheta/.intent-archaeology/batches/`, `/home/cheta/.intent-archaeology/verdicts/` |
| Prompt-corpus generator | `/home/cheta/code/build-prompt-corpus.py` |
| Dossiers | `/home/cheta/LIVING_DOCUMENTS/projects/<id>/` |
| Run state and reports | `/home/cheta/.local/state/intent-refresh/` |

## Procedure

Run the steps in order. Every phase is idempotent and resumes from the database, so after a crash the same commands continue the work.

0. **Preflight.**
   - Run `python3 -I status.py` and save its output as the "before" block of the report.
   - Check free memory (`free -m`). Under 1500 MB available, stop with the report reason "low memory". The machine has 7.8 GB, and cass can hold 3 to 4 GB.
   - The cron wrapper has already copied the database to `archaeology.db.bak-intent-refresh-<date>` and pruned older copies of its own. When you run this skill by hand, make that copy first.
   - Never run `cass index`. The cass-maintain cron job owns indexing.
1. **Inventory:** `01-inventory.py` with the default roots.
2. **Attribute new sessions:** `02-attribute.py --discovery disk`. Disk discovery avoids loading cass's memory-hungry index.
3. **Enrich:** `03-enrich.py`. It skips sessions already done.
4. **Emit batches.** For each project with human turns that have no intent verdict yet (status.py and the database tell you which), run `python3 -I /home/cheta/code/custom-skills/intent-refresh/pipeline/refresh-step.py batch <slug>`. It calls 04-batch with its default of 60 items and no output path.
5. **Classify each batch yourself.**
   - Read the two docstrings and the taxonomy first.
   - Every id in a batch must come back with a verdict, including noise.
   - Each verbatim span must be copied exactly from the source text; the merge rejects anything else.
   - Write the verdict files into the verdicts folder in the format `05-merge.py` documents.
   - Prompts can contain pasted secrets. Never copy a key, token or password into a verdict. Quote a span that excludes it.
   - Cap: 40 batches per run. Leave the rest for the next run and record the remaining count.
6. **Merge:** for each verdict file, run `python3 -I /home/cheta/code/custom-skills/intent-refresh/pipeline/refresh-step.py merge <verdict-file.json>`; the file must sit in the verdicts folder. Do not use `--allow-partial`. A missing id fails the merge on purpose: fix the verdict, never the batch.
7. **Render:** `06-render.py`. It writes only under `~/.intent-archaeology/derived/`.
8. **Prompt-corpus pages:** run `python3 /home/cheta/code/build-prompt-corpus.py`. It refuses to overwrite a page it did not generate. A refusal is correct; note the page in the report.
9. **Intent-archaeology pages.** For each dossier whose project gained new intents in this run, add a dated section to `intent-archaeology-findings.md`:
   - heading: `## Refresh <date>`;
   - one bullet per new intent with its kind, the verbatim span in quotes and the evidence date.
   - Do not rewrite existing prose. When a new intent supersedes or contradicts a recorded one, name both in the bullet. Leave the ruling to `intent-archaeology-source-adjudication.md`, which the operator owns.
   - If a dossier lacks any of the three sections (`prompt-corpus`, `intent-archaeology-findings`, `intent-archaeology-source-adjudication`), create the missing page with frontmatter and a "Not yet adjudicated" body, as the black-magic skill requires.
10. **Verify.**
    - `intent-find --stats` must no longer warn that the database is stale.
    - `ld-audit` must report no SECTION finding for the dossiers you touched.
    - `ld validate --project <id>` must be clean for each touched dossier.
    - A failed check goes into the report. Never weaken a check to pass it.
11. **Commit, do not push.** Under cron, the wrapper commits the changed `prompt-corpus.md` and `intent-archaeology-*.md` pages after you exit, with git hooks disabled. It skips the commit if any of those pages had uncommitted edits before the run. When you run this skill by hand, commit only those pages yourself. Pushing stays with the operator.
12. **Report.** Write `report-<date>.md` in the state folder with:
    - the status.py output before and after;
    - batches classified and left, intents merged, dossiers touched;
    - each failed check.

## Rules

- Under cron the agent may run only the pipeline scripts, `build-prompt-corpus.py`, `intent-find`, `ld-audit`, `ld validate`, `free -m` and `date`. Edit and Write are denied on source code, the database files and `.git` folders. If a step seems to need more than that, stop and say so in the report; never look for a way around it.

- Never run `cass index` or `cass-reindex`. Never delete outside the state folder, this job's own backups, and batch and verdict files this run created. Never edit source repositories.
- Never send prompt text to a non-Anthropic model or an external service. Session prompts can hold credentials and private data.
- Stop rather than guess when a phase fails twice with the same error, and put the error text in the report.
