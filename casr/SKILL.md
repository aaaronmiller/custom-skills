---
name: casr
description: >-
  Cross Agent Session Resumer. Convert a session from one coding agent into
  another and resume it there: omp, pi-agent, ante, muse, codex, gemini, kiro
  or claude-code history into Claude Code, Codex, Gemini, Antigravity, OpenCode
  and others. Use when asked to open, resume, continue, hand off, or move a
  session across harnesses. Triggers: "casr", "open this omp session in
  claude", "resume in codex", "move session to", "cross-agent resume".
license: MIT
metadata:
  version: 1.2.0
  requires: casr CLI on PATH (local fork at /home/cheta/git/cross_agent_session_resumer)
tags:
  - sessions
  - handoff
  - meta
  - TOOL
---

# casr: Cross Agent Session Resumer

One command for every harness. You name the target; casr finds the source
from the session ID.

```bash
casr resume <target> <session-id>            # convert, then print the resume command
casr resume <target> <session-id> --dry-run  # preview, write nothing
```

Examples: `casr resume cc 01a16dcc-0848-726e-b7a1-90cc0f7ea280` (omp into
Claude Code), `casr resume cod <claude-session-id>` (Claude into Codex).

There is no `-cc` flag form and no `casr <source> ...` form. The target is the
positional alias right after `resume`.

Targets: `cc` Claude Code, `cod` Codex, `gmi` Gemini, `agy` Antigravity, `opc`
OpenCode, `cur`, `cln`, `aid`, `amp`, `gpt`. `casr providers` shows which are
installed.

## Find the session ID

```bash
casr list --provider omp --limit 10   # most recent omp sessions
casr info <session-id>                # details for one session
```

- `casr list` covers the current directory and everything below it. Run it
  from `$HOME` to see all sessions.
- `--limit` applies per provider and casr parses every file up to it. Pass
  `--provider` and keep the limit small; very high limits can take minutes.
- Use the full ID from `casr list`. Prefixes are not matched.

## After converting

```text
✓ Converted omp session to claude-code
  Written → /home/<user>/.claude/projects/-home-<user>-tmp/<new-id>.jsonl
  Resume: claude --resume <new-id>
```

Claude Code finds sessions by working directory. `cd` into the source
session's workspace (the folder encoded in the `Written` path) before running
the printed `claude --resume <new-id>`, or convert with `--workspace <dir>`.

## Options that change the result

| Flag | Effect |
|---|---|
| `--dry-run` | Report what would be converted; write nothing |
| `--source <alias-or-file>` | Force the source provider, or read one exact session file |
| `--max-context-tokens N` | Default 200000; oldest turns dropped first. `0` keeps everything |
| `--max-tool-output N` | Default 4000 characters per tool result. `0` keeps everything |
| `--keep-reasoning` | Keep source reasoning traces (dropped by default) |
| `--enrich` | Add context messages explaining the conversion to the target agent |
| `--force` | Overwrite an existing converted session in the target |
| `--workspace <dir>` | Stamp a different workspace so the target resumes from there |
| `--json` | Machine-readable output |

## Known limits

- omp subagent transcripts (files like `<parent-session>/MagneticParrotfish.jsonl`)
  carry their ID only inside the file, so lookup by ID cannot find them. Get
  the file from `casr list --provider omp --json` (field `path`) and run
  `casr resume cc <id> --source <path>`.
- `Session validation failed: Session must have at least one user message and
  one assistant message.` The source session has no assistant reply yet.
- Very large sessions are trimmed hard by the default token cap. Raise
  `--max-context-tokens` when the full history matters.

## Maintenance

The installed binary is built from the local fork. Upstream
(Dicklesworthstone/cross_agent_session_resumer) has no omp, ante or muse
provider, so do not replace it with an upstream release. Rebuild with
`cargo build --release` in the fork, then copy
`/home/cheta/.cargo/target-shared/release/casr` (the global cargo target dir,
not the repo's stale `target/`) to `/home/cheta/.local/bin/casr` with
`command cp -f` (`cp` is aliased to `cp -i`). Check `casr --version` shows the
fork's current commit.
