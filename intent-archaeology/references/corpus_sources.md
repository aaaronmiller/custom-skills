# Corpus Sources (13)

> **When to read:** when Phase 5 feels incomplete, or when the audit is
> missing context you know exists.

## The 13 sources

cass is the primary, but not the only, source of evidence. The audit
is only as complete as the union of its sources. The 13:

### Tier 1 — always ingest

1. **cass-indexed session logs** — Claude Code, Codex, Cursor, Gemini
   CLI, Aider, ChatGPT. The primary intent corpus.
2. **Raw JSONL session files** — `~/.claude/projects/*.jsonl`,
   `~/.codex/sessions/*.jsonl`, etc. The audit fields cass flattens
   away live here. See `references/cass_fidelity.md`.
3. **Git history** — commits, branches, tags. The repo reality source.
   Includes branch names (the spec-kit feature key) and commit
   messages (often reference intent).

### Tier 2 — usually available

4. **`/specify.plan` slash-command invocations** — found via `cass
   search "specify.plan" --json`. Each one tells you which
   requirements.md / design.md was attached when the plan was made.
   Critical for spec archaeology.
5. **`/specify.spec` slash-command invocations** — same idea, for the
   spec phase. The user explicitly mentioned this as a search term.
6. **`/specify.init` slash-command invocations** — marks the start of
   spec-kit usage on a project. Era transition marker.
7. **Rejected diffs** — `git diff` output that was rejected (visible
   in session logs as `toolUseResult` with rejection). High signal:
   the user explicitly said "no" to this approach.
8. **Crash markers** — sessions that ended abnormally. Often indicate
   lost work that the user re-issued later; the re-issue is the
   authoritative intent, not the original.

### Tier 3 — sometimes available

9. **GitHub PR descriptions and review comments** — when the project
   is on GitHub and the user uses PRs. Often contain explicit intent
   statements ("this PR adds X because Y").
10. **GitHub Issues** — bug reports, feature requests. The bug-report
    intent type often originates here.
11. **`AGENTS.md` / `CLAUDE.md` / `cursor.rules`** — standing
    instructions the user has already codified. The audit should
    compare these to the discovered constitution; gaps go to
    `repeated_corrections.md`.
12. **README.md and docs/** — the project's self-description. Era 1
    projects often have only this.
13. **External references** — links the user pasted into sessions
    (Stack Overflow answers, blog posts, doc URLs). The
    `spec-reference` intent type often carries these.

## What to do with each source

| Source | Phase | Use |
|--------|-------|-----|
| cass session logs | 5 | Primary intent corpus |
| Raw JSONL | 5 | Audit fields (isSidechain, gitBranch, parentUuid) |
| Git history | 7 | Repo reality; branch names = spec keys |
| /specify.plan | 3 | Spec archaeology: which requirements.md was attached |
| /specify.spec | 3 | Spec archaeology: spec phase |
| /specify.init | 2 | Era transition marker |
| Rejected diffs | 6 | High-signal "no" — constraint or scope-cut |
| Crash markers | 5 | Mark re-issued prompts as authoritative |
| GitHub PRs | 6, 7 | Intent statements; code reality |
| GitHub Issues | 6 | Bug-report intents |
| AGENTS.md etc. | 8 | Compare to discovered constitution |
| README/docs | 1, 3 | Project description; era 1 intent source |
| External refs | 6 | spec-reference intent context |

## What you're forgetting (the two at the top)

The transcript highlighted two sources that are most often forgotten:

- **Rejected diffs.** The audit usually treats the agent's output as
  the proposed intent and the user's correction as the intent. But
  the *rejected diff* is the explicit "no" — without it, the audit
  thinks the user just issued a different instruction, not that the
  agent's approach was wrong.
- **Crash markers.** Sessions that crashed mid-task often have the
  user re-issuing the prompt in a new session. Without crash markers,
  the audit treats the re-issue as a new instruction and the original
  as abandoned. With crash markers, the audit treats the re-issue as
  authoritative and the original as superseded-by-crash.

## What's unnecessary

- **Terminal scrollback.** Already captured in session logs.
- **Browser history.** Already captured as external references in
  session logs (when the user pastes URLs).
- **Email.** Out of scope for coding intent.
- **Slack/Discord.** Out of scope unless the user explicitly imports
  them. The audit assumes the session log is the canonical record.
