# Changelog

## 1.2.0 (2026-11-19)

This release refines the skill using its first real run, the model-scan family with ARDF
folded in. A separate judge rejected 140 of 517 removal candidates. The debate behind these
changes is in `references/rule-debate-2026-11-19.md`.

- New `scripts/screen_removals.py`. It runs after inventory and merge, and holds a proposed
  removal candidate as `archive` with reasons in five cases:
  - H1: the file is stale since inventory.
  - H2: it is the source of an idea row.
  - H3: it is in a protected class. That covers operator words, transcripts, handoffs,
    restart prompts and credential handling, archive members included, and `protect` globs
    in `rules.json`. A protected file is held even when a byte copy exists.
  - H4: its bytes survive nowhere outside the whole removal set. A survivor can be a loose
    file, a member of a surviving archive, or a blob in the tree of a named git revision.
  - H5: it is an archive with a member found nowhere else.
- Survivors are re-hashed live. Among identical candidates one is kept, in keeper order.
  Only fixed ephemeral file types pass without a survivor, and no rule can waive this.
- A passing row carries `survivor` and `screened_sha256`. `inventory.py` clears the screen
  fields on every run. `render.py` and `check_ledgers.py` refuse a candidate without a current
  stamp, and `check_ledgers.py` refuses a candidate that is an idea source.
- `render.py` adds the survivor column and a "Held by the removal screen" section. It keeps
  a judge's verdict only while both the bytes and the survivor are unchanged.
- New `references/judge-brief.md` (the judge prompt, now with survivor re-checks and a
  "Where the screen failed" section). New `references/rule-debate-2026-11-19.md`.
- 17 new tests, one or more per screen rule. Suite: 29 tests.
- Checked against the first run's data: the screen holds 130 of the judge's 140 rejections.
  The other 10 keep their bytes through an identical sibling or the fold commit. 11 of 377
  confirmations are held: 9 are the other half of those sibling pairs, and 2 are extra caution.

## 1.1.0 (2026-11-19)

- Canonical-first copies (`--prefer`), `copy` rules, quote checks inside ZIP members.

## 1.0.0 (2026-11-19)

- Idea ledger, file ledger, canonical decision, incorporation list, checker and renderer.
