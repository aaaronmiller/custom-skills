# Spec archaeology

Resolving which version of which document was actually used, when a project
has a dozen versions of its requirements file and more added afterwards.

## The five document eras

Era selects the parser. Each shape encodes intent differently and one
extractor tuned for a single era will quietly under-read the others.

| Era | Format | Extraction | Confidence |
|---|---|---|---|
| 1 | Loose short markdown | Intent prose. Every sentence is a candidate. Low precision, accept it. | Low |
| 2 | PRD files | Section-aware; headings are scope boundaries | Medium |
| 3 | `requirements.md` plus `plans.md` | Two-document join: what/why versus how | Medium-high |
| 4 | Era 3 plus paths and user stories | User stories map to acceptance criteria; paths give a free evidence join | High |
| 5 | Living document | **No archaeology needed.** Ingest the structured ledgers directly. | Very high |

Era 5 is the newest material and the cheapest to process. Since sessions are
processed newest-first, it is also the first thing you will hit, which makes
it the right reference standard for judging how well eras 1 to 4 reconstruct.

## Finding the invocations

Match a prefix pattern, not an enumerated list. Command names changed across
releases and older forms are in your logs.

```sql
SELECT e.slash_command, e.slash_args, e.ts, s.source_path
  FROM event e JOIN session s ON s.id=e.session_id
 WHERE e.project_id = ?
   AND (e.slash_command LIKE 'specify%' OR e.slash_command LIKE 'speckit%')
 ORDER BY e.ts;
```

Also search bare filename mentions, because an attachment often appears as a
path in a turn rather than as a command argument:

```sql
SELECT id, ts, substr(text,1,200) FROM event
 WHERE project_id=? AND is_human=1
   AND (text LIKE '%requirements.md%' OR text LIKE '%design.md%'
        OR text LIKE '%prd%' OR text LIKE '%plans.md%')
 ORDER BY ts;
```

## Resolving the version

1. Find the invocation timestamp.
2. For tracked files, take the commit on that path whose timestamp immediately
   precedes it. That fixes the exact blob.
3. For untracked files, fall back to mtime, editor backups, and any copy of
   the content that appears inline in the session itself. That last source is
   often decisive: if the agent read the file, its content is in the log.
4. Content-hash every candidate version in the repo and its history, so
   "which version" becomes a hash lookup rather than a judgement call.

## The canonical document is a merge, not a selection

Frequently no single file is correct: v3 was attached at spec time, v5 added a
section that got built anyway, v7 was written afterwards and informed nothing.
Build three layers, each keeping provenance:

- **Base** the version resolved as attached, with the evidence that fixed it.
- **Overlay** every later change that demonstrably shaped the build, whether
  from a document version or a session instruction, annotated with its source.
- **Residue** everything in other versions that shaped nothing, retained and
  marked, because "we wrote this and never used it" is a finding.

## Sorting ideas for a project that has not started

Four buckets, not three. `unresolved` is the one that matters: forcing a
genuinely undecided idea into good or bad manufactures a decision you never
made, and something will later act on it.

`incorporated` in the final version or in the code · `discarded` present early,
absent later, or explicitly cut · `deferred` explicitly postponed ·
`unresolved` contradictory treatment across versions with no evidence of a decision.
