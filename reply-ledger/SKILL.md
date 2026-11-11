---
name: reply-ledger
description: Keep every reply the operator saw in a Claude Code session as structured, navigable HTML in Living Documents, captured by a Stop hook with no model calls. Use when asked to find, reread, review or link past session replies, to backfill a session's replies, or to check that reply capture is working.
metadata:
  version: "1.0.0"
  tags: "living-documents, sessions, replies, hooks, html, observability"
---

# reply-ledger

Every reply in a session carries pacing, decisions and review context that the operator wants to reread later as a document, not as terminal scrollback. This skill captures them programmatically.

## What it writes

```
/home/cheta/LIVING_DOCUMENTS/replies/index.html            every captured session, newest first
/home/cheta/LIVING_DOCUMENTS/replies/<session-id>.html     one session: turn list, filter box, prompts, replies
/home/cheta/LIVING_DOCUMENTS/replies/<session-id>.jsonl    the source records (prompt, reply, summary, event)
/home/cheta/LIVING_DOCUMENTS/replies/.state/               byte offsets, locks, errors.log
```

Each turn shows the operator's prompt (collapsed), background events such as finished jobs, interim replies (dashed) and the final reply of the turn. Compaction summaries appear as collapsed context blocks. Thinking, tool calls, tool output and subagent transcripts are left out.

## How it runs

Registered as a Stop hook in `/home/cheta/.claude/settings.json`:

```
python3 -I /home/cheta/code/custom-skills/reply-ledger/scripts/reply_ledger.py --hook
```

The hook reads the hook JSON, detaches a worker and returns at once, so it never delays the session. The worker reads only the transcript bytes added since its last run, never parses a half-written last line, and holds a per-session lock. Errors go to `.state/errors.log`; the hook always exits 0.

## Commands

```
python3 -I scripts/reply_ledger.py --transcript <path.jsonl> --session <id> --cwd <dir>   backfill one session
python3 -I scripts/reply_ledger.py --render-all                                           rebuild every page and the index
python3 -I -m pytest -q tests                                                             tests
```

Markdown is rendered with markdown-it-py with raw HTML disabled, so any HTML inside a reply is shown as text.

## Limits

- Claude Code only. Codex, omp and other harness sessions are not captured by this hook; cass holds them.
- A page is regenerated whole on each capture: a session of about 370 turns renders in about 2 seconds, in the background.
- The first capture of a very long transcript reads it once in full (a 97 MB transcript took about 10 seconds).
