---
title: Removal-rule debate after the first run (model-scan and ARDF fold)
date: 2026-11-19
skill-version: 1.2.0
method: deliberative-refinement, Structured Review council, V(8,3,1)
---

# Removal-rule debate, 2026-11-19

The first real run (model-scan family, ARDF folded into `model-scan/frontier`) proposed 517
removal candidates. A separate judge rejected 140 of them. This page records why the rules
failed, the debate over the fix, and how the fix performed against the judge's verdicts.

Evidence, all left unmodified:

- `/home/cheta/LIVING_DOCUMENTS/projects/model-scan/ledgers/` (file, idea and removal ledgers, `rules.json`)
- `/home/cheta/code/musebot/.omp-runs/removal-judge-2026-11-19/` (`prompt.md`, `verdicts.jsonl`, `summary.md`)
- `/home/cheta/LIVING_DOCUMENTS/projects/masterplan/liaison-run-2026-11-19-model-scan.md` (packets L3, L4, L7)

## What failed

Rejections by proposing rule (confirm / reject): `AA-repo-root` 4/41, `AA-staging` 40/26,
`AR-repo-docs` 61/14, `AA-zip` 0/10, `AA-data-csv` 8/10, `AA-html-dash` 9/9, `AA-data-json` 23/6,
`AA-canonical-leftovers` 9/5, `AA-copy` 163/4, `AA-data-log` 0/4. The globs were folder-wide
("superseded snapshot") and trusted three false assumptions:

1. **A copy is a survivor.** 182 of the 266 `same_as` counterparts were candidates themselves.
2. **Generated output and superseded data carry no evidence.** The older ARDF and Priors
   comparison differs in 91 of its 100 rows from the folded one. Two pricing extracts each had
   four rows the other lacks. Dated ledgers, dashboard payloads and run logs had no copy.
3. **A release ZIP repeats its extract.** The v4, v5 and organised v7.3 ZIPs held 18, 19 and 21
   members found nowhere else.

There were two more failures. Operator prompts, transcripts and credential instructions were
proposed because a byte copy existed. And a "byte copy" rule (`AR-copy-of-frontier`) covered
`verify_dashboard.py`, whose counterpart changed after inventory when the fold added
Playwright handling.

## Council

Eight seats sat for three rounds, with one probe between rounds. Each probe ran the draft
screen against the real ledgers and the judge's verdicts. The probes used a scratch copy and
never touched the evidence.

| Seat | Brief |
|---|---|
| Preservationist | A false deletion cannot be undone; prefer a false hold |
| Operator economy | The operator approves the list; holds that cost nothing but disk still cost review time |
| Judge's advocate | Reproduce what the judge checked, so the judge reads content instead of hashes |
| Determinism engineer | Every rule mechanical, repeatable, testable; no reliance on reason text |
| Evidence auditor | Idea-ledger citations and dated evidence must keep resolving |
| Security | Credential handling and secrets never move through a deletion path |
| Archivist | Package layout and grouping are evidence too |
| Advocatus diaboli | Added in round 2 because round 1 agreed at once on the survivor check |

## Round 1: what the classifier must check

All eight seats agreed at once on **whole-set survival**: a byte copy counts only if it is
outside the removal set. The unanimous result triggered the adversarial seat.

The other proposals from round 1:

- Evidence auditor: hold the **source of any idea row**, of any category, not only `unknown`.
- Security: hold **protected classes** even when a copy exists. These are operator words
  (prompt, transcript, pasted text, handoff, restart or meta prompt, intent, instructions)
  and credential handling.
- Archivist: an archive survives only if **every member** survives elsewhere.
- Determinism engineer: **re-hash** the candidate and its survivor at screen time, so a
  "same name" never stands in for "same bytes".

Probe 1 (draft screen, git history from any ref counted as a survivor) held 117 of the 140
rejections. It also held 11 of the 377 confirmations. 23 rejections still passed, 11 of them
through blobs that were only reachable somewhere in git history.

## Round 2: the adversarial round

**Advocatus diaboli on git history.** "A blob reachable from some ref is recoverable, so it is
a survivor." The reply: recoverable only by someone who already knows the blob id. The judge
accepted only blobs in the fold commit, and rejected 11 that were deeper in history.
Resolution: a git blob counts only in the tree of a **named revision** (`--git-root ROOT@REV`,
default HEAD). The stamp records the resolved commit id, so a moving HEAD cannot change it.
Probe 2 with HEAD only held 131 of 140. With the fold commit named, 5 more confirmations passed,
matching the judge's 5 git-blob confirmations.

**Operator economy on the credential scan.** "`secret` and `password` will hold half of any
codebase." Probe evidence: among 327 text candidates, the credential pattern hit 12 rejections
and 0 confirmations. The cost is asymmetric. A wrong hold leaves a file archived, which is
cheap to undo. A wrong deletion of credential instructions cannot be undone. Kept as is.
A second pattern for operator voice in body text ("the user asked...") hit 24 rejections but
also 13 confirmations. It was dropped as too noisy, and name-based protection carries that
class instead.

**Advocatus diaboli on idea sources.** "Holding every cited file freezes archives forever."
Resolution: the hold has a release path. Re-point the idea row's `source` to a surviving copy
with `ideas_tool.py set`. The quote check then verifies the citation at its new source.
Probe: 43 of 43 cited candidates were rejections, with 0 confirmations.

**Archivist on archives versus loose copies.** "Keep the release ZIP; it carries layout."
The judge confirmed 243 loose files because their bytes survive as ZIP members. Resolution:
in keeper order, archives come before loose extracts. An archive is also protected when any
of its members is protected; both copies of the from-scratch and refined ZIPs were rejected
for holding operator prompt aggregation.

**Determinism engineer against a rule-level waiver.** "If a rule can say `survivor: not
required`, folder-wide globs will say it again." Resolution: there is no waiver in
`rules.json`. Only a fixed list of ephemeral types passes without a survivor: `.pid`, `.lock`,
`.tmp`, `.swp`, `.pyc`, `.DS_Store`, `Thumbs.db`. Coverage data, logs, backups and
generated HTML are not on the list; the judge rejected `.coverage` and all four logs.
`rules.json` may add `protect` globs but never remove a protection.

## Round 3: where the screen runs and what stays human

- **Placement.** The screen needs the idea ledger, which does not exist at inventory time
  (step 3). So it is a separate step, `screen_removals.py`, run after merge (step 7).
  `inventory.py` clears every screen field on each run. `render.py` and `check_ledgers.py`
  refuse a removal candidate without a stamp for its current bytes. Folding the screen into
  inventory was rejected for the ordering reason.
- **Held rows become `archive`**, keep `rule_disposition: removal-candidate`, and list
  every reason, not just the first. The judge recommended archive for 139 of its 140
  rejections.
- **The judge and the operator gates stay.** The screen checks bytes, citations and names.
  The judge still reads content: variant value, layout, "this differs by 16 lines". The
  operator still approves the exact list. Nothing in the skill deletes. The judge brief is
  now a reference (`judge-brief.md`) rather than an ad hoc prompt.
- **Rejected proposals:**
  - Lint rule reasons that say "copy" when the rule lacks `copy: true`. Redundant, because
    survival is now checked against bytes and the reason text is ignored.
  - Count history-only git blobs. Rejected in round 2.
  - Let a rule waive H4. Rejected in round 2.
  - Scan body text for operator voice. Too noisy.

Convergence came in round 3: no seat changed position, and probe 3 matched probe 2.

## Result against the judge (probe 3, final screen)

Command run on a scratch copy of the ledgers:

```
screen_removals.py --ledgers <copy> --git-root /home/cheta/code/model-scan \
  --git-root /home/cheta/code/model-scan@db0efd5 --prefer /home/cheta/code/model-scan
```

| | Judge confirmed (377) | Judge rejected (140) |
|---|---:|---:|
| Screen passed | 366 | 10 |
| Screen held | 11 | 130 |

Holds by code: H2 cited 43, H3 protected 44, H4 unique 63, H5 exclusive archive 2.
A row can carry several codes.

The 10 rejections that passed:

- **9** are pairs of byte-identical files where the judge kept one copy and the screen kept the
  other (three scraped CSVs; six files of the consolidated-from-cwd snapshot). The bytes are
  kept either way. These 9 pairs also account for 9 of the 11 held confirmations.
- **1** is `ardf/ardf/tests/verify_dashboard.py`. The judge rejected it because its declared
  counterpart changed. Its exact bytes survive in the fold commit's tree (`db0efd5:frontier/tests/verify_dashboard.py`),
  which the screen names in the survivor stamp.

The other 2 held confirmations are the cost of caution. One is a timestamp file
(`.remember/tmp/last-save-ts`) that is not on the ephemeral list. The other is a ZIP whose
member `scrape_benchmarks.py` mentions credentials.

Net result: after the screen, no byte sequence the judge chose to keep would have been
proposed for deletion. The judge would have reviewed 376 rows instead of 517.

## Open questions for the next run

- Keeper order is canonical root first, then archives, then shallow paths. The judge
  sometimes preferred the deeper copy. Neither choice loses bytes, so this was left as is.
- The protected-name pattern is English and tuned to this operator's file names. Extend it
  through `protect` globs in `rules.json` rather than widening the pattern without evidence.
