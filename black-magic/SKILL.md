---
name: black-magic
description: Use when organizing any project folder under ~/code or ~/code2, working a punchlist, or about to report something as blocked. Runs the intent-first loop - organize the folder, make the intent record current, then answer questions from the record instead of escalating. Searches the whole cross-project pool, never one dossier.
---

# black magic

The loop that turns "I am blocked on X" into "X was answered on 2026-07-14, in
a different project."

Scoped to this machine: project folders under `~/code` and `~/code2`, dossiers
under `~/LIVING_DOCUMENTS/projects`, intents in
`~/.intent-archaeology/archaeology.db`. **207 project folders, 95 of them git
repositories, as of 2026-08-20.** It works on any of them, not only the ones
with a dossier.

## Resource readiness gate — run this FIRST

Before the loop, verify every resource the loop reads. Any gap becomes task #1:
fix it, then run the loop with the corrected intent. A loop run against a
missing resource answers nothing and manufactures false blockers.

Checklist (all must pass before step 1 of the loop):

1. `intent-find` on PATH (`which intent-find`).
2. The target project has a record: `intent-find --resolve <project>` — if it
   reports no recorded intent anywhere, build the corpus FIRST (step 2 below)
   before working the punchlist.
3. Dossier sections complete: `prompt-corpus`,
   `intent-archaeology-findings`, `intent-archaeology-source-adjudication`.
   `ld-audit` reports a missing section as a `SECTION` finding and exits
   non-zero. Fix the section before looping. (Confirmed 2026-08-20:
   quartermaster was missing `intent-archaeology-findings` while the other
   two existed.)
4. CASS index is not stale: `cass status --json`. A stale index means the
   Tier-2 intent source below is incomplete. On a named need
   (checkpoint/database mismatch, pending sessions, partial coverage,
   quarantine), run `cass index` first. If `cass index` refuses with
   "unhealthy canonical archive" (exit 5), the archive has interrupted
   operation artifacts. Recovery, verified 2026-08-21:
   `cass doctor check --json` → clear stale `raw-mirror/v1/tmp/capture.*`
   dirs (partial `.tmp` blobs, inspect mtimes first) → `cass doctor --fix`
   (it reclaims stale repair locks itself) → `cass index`. Known residual
   defect: the lexical checkpoint fingerprint can lag the DB
   (`content-v1:<n>` mismatch) so status reports stale even after a
   successful run — cross-check with `cass doctor check` (which reports
   search ready) before treating the stale flag as real. Known constraint
   (2026-08-22): cass's indexer hard-requires a 4GB memory reserve
   (`host_available_memory_bytes_*_below_reserve_4294967296` in the stall
   diagnostics) — on this 7.8GB box it only runs when the interactive stack
   is idle, so schedule index runs for idle windows and do not retry them
   under load.
5. Muse coverage: `cass onboarding --json`. If `muse` is NOT listed as a
   provider, the Tier-3 muse supplement below is REQUIRED, not optional.
6. `ld-audit` on PATH. If missing:
   `ln -sf /home/cheta/code/living-documents/skill/scripts/ld-audit /home/cheta/.local/bin/ld-audit`

If any item fails, that item is task #1. Do the fix, then run the loop.

## Intent sourcing — three tiers, in order

Search all three before declaring anything unanswered.

- **Tier 1 — the six-month intent scan.** The archaeology database
  (`~/.intent-archaeology/archaeology.db`) and the archaeology pages under
  `~/LIVING_DOCUMENTS/projects/*/intent-archaeology-*.md`, produced by the
  intent-archaeology scan. This is the baseline; it is not current by itself.
- **Tier 2 — CASS updates since the scan.** `cass search` / `cass view` over
  claude, codex, gemini, hermes, opencode, antigravity, pi_agent, qwen,
  openclaw sessions (cass 0.6.24 as of 2026-08-20). If `cass status` reports
  stale, refresh before searching.
- **Tier 3 — muse, direct session audit.** Muse is NOT integrated into CASS
  as of 2026-08-20 (confirmed: `cass onboarding` lists no muse provider;
  `cass upgrade --force` fetched no newer build). When that integration lands,
  run `cass upgrade` + `cass index`, re-confirm, and demote this tier. Until
  then, audit muse sessions directly:
  - `muse export --session <uuid|path> --out <file>` — one self-contained JSON
    per session (timestamps, messages, reasoning, tool calls, approvals,
    model ids).
  - Or read the raw logs:
    `~/.local/share/muse/sessions/YYYY/MM/DD/<uuid>/session.jsonl` plus
    `subagent/` trees (8,784 session files present as of 2026-08-20).
  - Mine user prompts from those exports exactly as the prompt-corpus builder
    does, and fold the result into the dossier corpus.

## Why it works

Instructions get given once, on one project. Months later a different project
hits the same question and treats it as new. The answer already exists; nobody
looks outside the dossier they are standing in.

Measured on the first run, 2026-08-20:

| project | items reading as blocked | already answered | genuinely blocked |
| --- | ---: | ---: | ---: |
| quartermaster | 10 | **8** | 2 |
| model-scan | 9 | **6** | 3 |

Fourteen of nineteen. The model-scan nine had been blocking a whole revision
since 2026-08-16.

## Start here, every time

    intent-find --resolve <project>

Resolves a folder name to its repository under `~/code` or `~/code2`, its
dossier, its archaeology ids, its intent count, and which of the three
archaeology pages exist. It tells you in one line whether this project has a
record to consult or whether you must build one first.

If it reports **no recorded intent anywhere**, do step 2 before step 3. Working
a punchlist against an empty record is how a project accumulates false
blockers.

## The loop

Run it **per project**. Do not batch across projects; organizing one project is
what surfaces the questions the record then answers.

### 1. Organize the folder

Archive dead build artefacts into `archive/`. **Never delete.** Date every
operation so an unintended change can be found later.

Add `archive/` to `.gitignore` if the moves would otherwise read as mass
deletion. On the Living Documents corpus, 86 moves showed as 86 deletions plus
86 untracked additions and blocked committing anything at all until the path
was ignored and untracked with `git rm --cached`.

Typical dead artefacts here: `__pycache__`, `.pytest_cache`, `.ruff_cache`,
dated `*.bak-YYYYMMDD` files, duplicated version directories in `v1`/`v2`/`v3`
style, scratch directories named after the prompt that created them, and
`node_modules` committed by mistake.

### 2. Make the intent record current

This is the priority, not step 3. An out-of-date intent page answers nothing.

Every dossier carries the full section: `prompt-corpus`,
`intent-archaeology-findings`, `intent-archaeology-source-adjudication`. A
half-built section is worse than none: a corpus with no adjudication is
evidence nobody ruled on, and an adjudication with no corpus is a ruling with
no source. `ld-audit` reports this as a `SECTION` finding and exits non-zero.

For a project the archaeology database never ingested, build the corpus from
what is on disk: the repository's own prompt aggregations, `session.jsonl`
files, muse session data under `~/.local/share/muse/sessions`, and commit
messages. **Do not skip a project because the database is empty.** Seven
dossiers had zero intents and no corpus on 2026-08-20, and that is precisely
where blockers accumulate.

Regenerating a corpus: `python3 ~/code/build-prompt-corpus.py`. It refuses to
overwrite a page it did not itself generate, so a hand-built corpus is safe.

### 3. Work the punchlist, and ask the record before asking the human

Every time a question or blocker surfaces:

    intent-find <terms>              search everything, all projects
    intent-find --all <a> <b>        require all terms
    intent-find --project <name>     scope to one project
    intent-find --stats              coverage of the whole pool

It searches the archaeology database, every `prompt-corpus*.md` page, and every
archaeology, punchlist and blocking-questions page.

**Search the whole pool. Never a single dossier.** The cross-project hit is the
common case. A question about task fixtures in `model-scan` was partly answered
by a retrospective in `agentic-operating-system`, a project nobody would have
thought to open.

### 4. Escalate only what the record genuinely cannot answer

State what you searched and what you found nothing for. A blocker reported
without a search is not a blocker, it is an unread file.

**Never report a blocker without proposing the best solution you can see.** If
the record has no answer, propose the one you would pick and why, so the
decision is a yes or no rather than an open question.

**Present every escalated item in plain language, never as an id or code
alone.** A "blocked on B2" or "safety 0.40" means nothing to the human being
asked to authorize it. Name the thing: which project, which artifact, what the
blocker is, what the proposal is, and what exactly the human must say yes or no
to. If the answer already exists in live config or a record the loop reads
(example: an active loadout already encodes which skills are vetted), say so
and do not ask.

## The four shapes of "already answered"

Name which one applies.

- **Answered.** An intent or prompt states the decision. Quote it.
- **Superseded.** A later decision replaced the question. Name both.
- **Rejected as automatic.** Declined as a standing action, not blocked. Common
  for push, merge, publish, delete.
- **Incorporated.** Already done and living somewhere. Name the file.

The fourth is the one most often mistaken for a blocker.

## Failure modes seen in practice

- **Trusting a delegated agent's inventory without checking.** One recommended
  deleting two template trees as byte-identical duplicates. Per-file md5 showed
  three files differed, and they were the design files, so the trees were
  genuine variants. Acting on it would have destroyed two designs. **Verify any
  load-bearing claim before acting on it.**
- **The stale-alias trap.** A corpus generator aliased one project's prompts
  into another's dossier and would have overwritten a hand-built corpus. Any
  generator that writes a page must refuse to overwrite one it did not write.
- **Frontmatter dates lie.** `updated:` records the file write, not the
  evidence window. A corpus can say 2026-08-01 and end at 2026-06-28. Check the
  content range against the repository's last commit.
- **Relative timestamps in `find`.** `bfs` rejects `-newermt "-90 minutes"` and
  the failure is easy to miss. Use an absolute timestamp. (`bfs` is not
  installed on this machine as of 2026-08-20; use `find` with an absolute
  timestamp when it is absent.)

## Revision log

Append whenever a run teaches something. This skill improves during use.

- **2026-08-20, first run.** Established the loop across six projects. Hit rate
  14 of 19. Built `intent-find`. Learned: the archaeology database is
  incomplete so disk evidence must be searched too; seven dossiers had zero
  intents and no corpus; delegated inventories need their load-bearing claims
  verified before action; `--resolve` added so the loop can start on any of the
  207 folders rather than only ones with a dossier.
- **2026-08-20, second run.** Added the resource readiness gate (any missing
  resource becomes task #1 before the loop runs) and the three-tier intent
  sourcing (six-month scan → CASS → muse CLI direct audit). Confirmed muse is
  NOT in CASS (cass 0.6.24; `cass upgrade --force` fetched nothing newer);
  the muse tier documents `muse export --session` and raw `session.jsonl`
  reading. Wired `ld-audit` onto PATH (was present in
  `living-documents/skill/scripts/` but unreachable). Added the plain-language
  escalation rule after a run that asked the human to authorize codes instead
  of decisions, and failed to notice the vetted-skill answer already encoded
  in the active loadout (`baseline-223`).

- **2026-08-21.** Added the blocking gate to the global rules: no blocker
  reaches the operator until `intent-find` has been run across all projects and
  the four dispositions applied. Also recorded the steering protocol, after the
  model tier definition was rewritten four times in one session, once per
  steering message. Steering is refinement; buffer it and apply once at a work
  boundary, rather than servicing each interjection on arrival.
