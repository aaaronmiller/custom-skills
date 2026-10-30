---
name: cass-cli
description: >-
  Recover what was actually said, decided, or attempted in past coding-agent
  sessions. Use for prior-work lookup, intent recovery, cross-harness handoff,
  "what did I ask for", "have I solved this before", "what did the other agent
  do", session forensics after a crash, or building an evidence pack from
  history. Searches claude, codex, gemini, hermes, opencode, antigravity,
  pi-agent, qwen and openclaw histories through the local cass archive; muse
  sessions are not indexed and are read directly.

  Triggers: "cass", "search my sessions", "prior work", "did I already", "what
  did I ask", "session history", "past conversations", "intent recovery", "what
  was decided", "cross-agent handoff", "session forensics", "answer pack".
license: MIT
metadata:
  version: 1.0.0
  requires: cass CLI on PATH
tags:
  - evidence
  - sessions
  - forensics
  - meta
  - TOOL
---

# cass CLI

`cass` is the local archive and search over coding-agent histories. It answers questions
about what has already happened rather than what the code currently says, which makes it
the right tool for intent recovery and the wrong tool for reading a repository.

## Start here, always

```bash
cass triage --json
```

One call returns readiness, the recommended next command, available workflows, and the
response schemas. Run it before anything else — it is cheap, it tells you whether the
archive is usable, and it names the right follow-up for the question being asked.

If `triage` is unavailable, `cass capabilities` is the self-description fallback and
`cass health` is a sub-50ms pre-flight that exits 0 or 1.

## The normal path

```bash
cass search "<terms>" --robot          # one-off search, JSON out
cass view <path> --line <n>            # open a hit in context
cass pack "<question>"                 # deterministic answer pack for a handoff
```

**Search before enumerating.** `cass sessions --limit 5000` is not a default on this
machine — it is expensive and usually unnecessary. A targeted search or a known session
path answers most questions, and broad enumeration should follow a specific failure of the
targeted approach, not precede it.

Follow a hit with `view` or `expand` rather than re-searching with different words. The
snippet in a search result is not the evidence; the surrounding turns are.

Use `pack` when the output is going to another agent. It is deterministic, which matters
when the receiving agent will act on it.

## Muse is not indexed

`cass onboarding --json` lists which sources are covered. As of 2026-08-20 muse is **not**
among them, and `cass upgrade --force` fetched nothing newer. Muse sessions must be read
directly:

```bash
muse export --session <uuid|path> --out <file>     # self-contained JSON
# or read the raw log:
~/.local/share/muse/sessions/YYYY/MM/DD/<uuid>/session.jsonl
```

Subagent trees live under `subagent/` beside the session log. There were 8,784 muse session
files present on 2026-08-20, so this is not a small gap — a search that finds nothing in
cass has not searched muse.

Re-check `cass onboarding` before assuming the gap persists; when muse integration lands,
this section is obsolete.

## Indexing is a mutation, not a refresh

`cass index` writes to the archive. Treat it as a change requiring a reason, and record the
reason.

**A time-based "index stale" result is not sufficient justification.** Before refreshing,
require a named recovery need: pending sessions, a checkpoint/database mismatch, partial
coverage, quarantine, or an explicit request. If pending sessions are zero, the checkpoint
matches, and search coverage is complete, record the health result and stop — refreshing to
reset a freshness clock is a mutation for no gain.

Known defect: the lexical checkpoint fingerprint can lag the database (`content-v1:<n>`
mismatch), so `status` reports stale after a successful run. Cross-check with
`cass doctor check`, which reports whether search is actually ready, before believing the
stale flag.

If `cass index` refuses with "unhealthy canonical archive" (exit 5), the recovery verified
on 2026-08-21 is:

```bash
cass doctor check --json                     # inspect first
# clear stale raw-mirror/v1/tmp/capture.* dirs — check mtimes before removing
cass doctor --fix                            # reclaims stale repair locks itself
cass index
```

## What a cass hit does and does not prove

A search hit proves the text is **discoverable**. It does not prove a session was resumed,
that a decision was acted on, or that derived intent coverage is complete. State which of
those you are claiming.

For exhaustive intent attribution across projects, prefer bounded direct disk discovery
over broad cass enumeration, and check the active CASS health and resource budget first.

A topical query has a **silent recall gap**: content search runs BM25 plus vector fusion,
so a turn phrased in vocabulary you did not query simply never appears, and nothing in the
output says so. An exhaustive sweep must enumerate — `cass search "" --robot-format sessions`
— rather than trusting that a well-chosen query found everything.

Never quietly turn "all" into "recent N". If a scope cannot be honoured, say which bound
was applied.

## Related

- `intent-archaeology` — reconstructs what was asked for across a whole portfolio, using
  cass as its Tier-2 source. Reach for that when the question is "what was this project
  supposed to be" rather than "what did I say about X".
- `black-magic` — the intent-first loop that runs before reporting anything blocked. It
  calls cass as one of three tiers.
- `casr` — cross-provider session resume, for continuing a session rather than searching it.
