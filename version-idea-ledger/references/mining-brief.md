# Reader brief: mine one slice of an older version

Copy this brief into each reader's prompt, filling the four `<...>` fields. A reader is one
agent (or one person) with a fixed list of files. Readers only read and write their two output
files; they never edit, move or delete anything.

## Inputs

- Family: `<family>`. Current implementation (canonical root): `<canonical root>`.
- Canonical map: `<path to canonical-map.md>`, a one-line purpose for each module and doc of the
  current implementation. Search the canonical root yourself (`grep -rn`) before calling an idea
  absent; the map is a start, not proof.
- Your slice: `<path to slice-<name>.txt>`, one absolute path per line, with its version label.
- Id prefix: `<prefix>`. Number rows `<prefix>-001`, `<prefix>-002`, ... in reading order.

## Outputs (JSON Lines, one object per line, UTF-8)

1. `ideas-<slice>.jsonl`, one row per atomic idea (schema below).
2. `coverage-<slice>.jsonl`, one row per file in your slice:
   `{"path": "<abs>", "status": "mined" | "no-ideas", "note": "<one line>"}`.
   `no-ideas` means you read it and it holds no idea (generated output, raw data, a log of a
   past run, a byte copy of another file). Every file in the slice gets exactly one row.

## What an atomic idea is

One behaviour, rule, formula, threshold, interface, data source, output, check, or design
decision that someone could implement, test or reject on its own. Split a sentence that carries
two. Not ideas: status reports, dates and counts from a past run, progress logs, praise,
restatements of the task. Process lessons ("verify a free price against a live route before
trusting it") are ideas when they change how the tool should behave.

## Row schema

```json
{"id": "<prefix>-001", "version": "<label>", "source": "<abs path>", "loc": "L120" ,
 "quote": "<exact text copied from the file, 20 to 200 characters>",
 "idea": "<the idea in one plain sentence>",
 "category": "implemented | to-incorporate | duplicate | rejected | stretch-goal | unknown",
 "where": "<implemented: canonical path[:line], several joined by '; '>",
 "target": "<to-incorporate or stretch-goal: where it should land in the canonical root>",
 "duplicate_of": "<duplicate: id of the row it repeats>",
 "reason": "<rejected: why; stretch-goal: why not now>",
 "question": "<unknown: the evidence that would decide it>",
 "evidence": "<optional: what you checked, for example the grep you ran>"}
```

- `loc` is `L<n>` or `L<n>-L<m>` (line numbers in the file) or `§<heading>` for a whole section.
- `quote` is copied, never paraphrased or recalled; the checker looks for it near `loc` and
  refuses the row if it is missing. For a file with no usable text (an image, a binary), omit
  `quote` and set `quote_exempt` to the reason.
- Leave out the fields a category does not use.

## Choosing the category

| Category | Use when | Required field |
|---|---|---|
| implemented | the current implementation already does it; you found the code or doc | `where` |
| to-incorporate | worth having, absent from the current implementation | `target` |
| duplicate | another row (yours or an earlier slice's) already states it | `duplicate_of` |
| rejected | a later version, a decision page, a review or the evidence ruled it out, or it is worse than what exists | `reason` (cite the decision when there is one) |
| stretch-goal | worth having but out of proportion to its value now | `reason` |
| unknown | you cannot tell from the files | `question` |

Rules: an honest `unknown` beats a weak `implemented`. Check decision pages and errata before
calling something to-incorporate; many ideas were rejected on purpose. When an old version had
a feature the current one replaced with something better, the old idea is `rejected` with
`reason: superseded by <where>`. Never mark an idea implemented on a name match alone; open
the file.

## Finish

Validate before you stop: every slice file has one coverage row; every idea row parses and has
its required field. Report the two output paths, your counts per category, and anything you
could not read.
