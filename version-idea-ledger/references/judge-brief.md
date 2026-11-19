# Judge brief: confirm or reject each removal candidate

Copy this into the judge's prompt and fill the `<...>` fields. The judge must be a different
agent from the classifier, ideally a different model. The judge deletes nothing. The operator
approves the final list.

## Inputs

- Candidates: `<dossier>/ledgers/removal-candidates.jsonl`. Every row passed
  `screen_removals.py`, so each one carries a `survivor`: where its exact bytes still exist
  (`loose` path, `zip-member` path and member, `git-blob` with `tree_path` `<commit>:<path>`,
  `members` for an archive, or `ephemeral`).
- Context: `<dossier>/ledgers/` (`idea-ledger.jsonl`, `file-ledger.jsonl`, `canonical.json`,
  `rules.json`) and the skill's `SKILL.md`. Rows the screen held are in the file ledger with a
  `held` list. They are not your input, but read them to see which patterns the screen already
  caught.

## For every row

1. Re-hash the file. If it no longer matches `sha256`, the verdict is `stale`.
2. Re-check the survivor. For a loose survivor, re-hash it. For a member, read it from the
   archive and hash it. For a git blob, run `git -C <path> cat-file -e <tree_path>` and hash
   the output of `git show <tree_path>`. Then confirm the survivor is not itself in this
   candidate list. If any of these checks fails, the verdict is `reject`.
3. Decide whether removing the file loses anything the survivor does not keep. Look for
   package layout that matters, a path that something still names (scripts, docs, crontab,
   skills), or a reason to keep this location rather than the survivor's.
4. The verdict is exactly one of: `confirm`, `reject` (with the disposition you would give
   instead: keep or archive), or `stale`. `judge_reason` is one sentence with the evidence.
5. Be adversarial and reject when unsure. Never confirm operator instructions, transcripts,
   credential handling, or the only copy of any data. The screen holds these, so finding one
   here is a screen defect: name it in the summary.

## Outputs, in the judge's own working folder

- `verdicts.jsonl`: one row per input row, in the same order and count, with `verdict` and
  `judge_reason` filled in.
- `summary.md` with:
  - the count per verdict;
  - the reject list with reasons;
  - **"Where the screen failed"**: the patterns the screen should have caught, which feed the
    skill's next refinement;
  - the total bytes that confirmation would free.

Read only outside your folder. Never print a secret; if a file holds one, say "contains a
credential" without quoting it.
