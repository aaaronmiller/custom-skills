# Prior-art check (2026-11-19)

The operator asked first whether a skill already consolidates the ideas of several project
versions into a ledger (request of 2026-11-19 07:11, verbatim in
`~/LIVING_DOCUMENTS/projects/masterplan/sources/operator-2026-11-19-model-scan-request.md`).
Every candidate was read in full or in its procedure section.

| Candidate | What it does | What it lacks for this job | Use here |
|---|---|---|---|
| `portfolio-lineage` | Extracts Markdown clauses (ID rows, SHALL/MUST, numbered rules), marks each covered, partial or unique against a successor by lexical score, and gates archiving while a unique clause has no destination | Only Markdown clauses, not ideas in prose or code; three marks, not the six categories; no file ledger; one old folder against one successor | **Called.** `extract_clauses.py` gives readers a checklist of ID'd clauses; `compare.py` gives lexical pre-marks; `gate.py` still runs before any archive move |
| `project-archive` | mine, index, move, link for one folder, with consumer scan, never-class moves and a recovery test | Leaves idea mining to "a human or agent task" (`references/method.md`); acts after classification | **Called after.** Moving an archived version is its job; this skill only marks the file |
| `intent-organizer` | Declutters Downloads-style folders: facts script, model verdicts, challenge pass, approval page with undo | Per-item intent for loose files, not ideas across versions of one project | Borrowed: facts first, then model judgement, then an adversarial check |
| `intent-refresh` | Collects operator prompts from every harness and derives intents for `intent-find` | Session prompts, not project files | Used through `intent-find` to find decisions that reject or answer an idea |
| `session-cleanup` | Closes a session: loose ends, handoffs, commit and push | Unrelated to version consolidation | Not used |
| `notes-sweeper` | Recovers Notepad tabs into dossier pages and a note library, with version merging of tabs | Notes, not project versions; no categories or file dispositions | Borrowed: preservation before interpretation; fuzzy name matching (adrf vs ardf) |
| `black-magic` | Tidy, refresh intent, answer questions from the record before calling anything blocked | A loop over a punchlist, not a ledger | Its rule applies to `unknown` rows: search `intent-find` before leaving one unknown |
| `spec-prep` | Intent, requirements and specs; its prior-art gate and source-disposition map keep rejected and deferred inputs with reasons | Builds specs forward; does not audit old versions | Borrowed: every input gets a disposition with a reason |
| `examine-documents` | Reads a local corpus into one cited synthesis | A synthesis, not a per-idea ledger; no categories | Borrowed: cite file and location per claim |
| agent `file-auditor` | Summarises and extracts ideas per file batch under a token budget | Calls `file-summarizer`, which is not installed; no categories or current-implementation check | Not used |
| agent `cluster-analyzer` | Groups audited files into lineages | Calls `similarity-cluster`, not installed | Not used; `ideas_tool.py dupes` covers duplicate candidates |
| agent `master-consolidator` | Merges each cluster into one master document | Calls `file-summarizer`, not installed; writes a merged document, which loses per-idea status | Not used |
| agent `document-organizer` | Sorts Markdown by topic and date and writes an "authoritative" version per series | Calls `document-taxon` and `document-lineage`, not installed; no current-implementation check | Not used |

## skillranker

`sr` could not rank. `/home/cheta/.local/bin/sr` pointed at
`/home/cheta/git/skillranker/target/release/sr`, which did not exist because the build writes to
the shared target dir `/home/cheta/.cargo/target-shared`; a symlink now bridges that. After it,
`sr doctor --json` saw 2 skills (181 symlinked skill folders skipped, 64 unreadable) and
`sr rank --latest --allow-network` returned `"decision": "unavailable"`, `"kind": "authentication"`,
`"Invalid credentials"`. Per the skillranker skill, credentials were not touched. No picks.

## Decision

Build a new skill that composes the existing ones. No candidate produces the two ledgers;
`portfolio-lineage` is the closest and stays the owner of clause comparison and the archive
gate, so this skill calls its scripts instead of repeating them. New here: the file ledger with
hashes and rerun skipping, the six-category idea ledger with its checker, reader slices with
quote checks (method of the 2026-11-04 lineage-archive job, `project-archive/references/method.md`),
the canonical-version record, and the incorporation list.
