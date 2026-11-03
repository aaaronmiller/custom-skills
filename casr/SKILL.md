---
name: casr
description: >-
  Cross Agent Session Resumer. Convert a session from one coding agent into
  another and resume it there: omp, pi-agent, muse, codex, gemini, kiro or
  claude-code history into Claude Code, Codex, Gemini, Antigravity, OpenCode
  and others. Use when asked to open, resume, continue, hand off, or move a
  session across harnesses. Triggers: "casr", "open this omp session in
  claude", "resume in codex", "move session to", "cross-agent resume".
license: MIT
metadata:
  version: 1.1.0
  requires: casr CLI on PATH (verified against casr 0.3.0)
tags:
  - sessions
  - handoff
  - meta
  - TOOL
---

# casr: Cross Agent Session Resumer

Converts a session from one agent's history format into another's, then prints
the command that resumes it.

## Command shape

```bash
casr resume <target> <session-id> [--source <provider|file-path>] [--dry-run]
```

There are no `-cc` / `-cod` / `-gmi` shortcut flags. The target is a positional
alias.

Targets (write side): `cc` Claude Code, `cod` Codex, `gmi` Gemini, `agy`
Antigravity, `opc` OpenCode, `cur`, `cln`, `aid`, `amp`, `gpt`.
omp, pi-agent, muse and kiro are readable sources only, not resume targets.
Run `casr providers` to see which are installed.

## Find the session

```bash
casr list --provider omp --sort date --limit 10
casr list --provider omp --limit 10 --json   # includes the session file "path"
```

- `casr list` is scoped to the current directory **and its subdirectories**. Run
  it from `$HOME` to see everything.
- `--limit` applies per provider and casr parses every file up to it. Always pass
  `--provider` and a small limit: one provider at 30 takes about 5 s, all
  providers at 30 take about 16 s, and 500 can run for minutes.

## Quick path on this machine: `omp2cc`

`/home/cheta/.local/bin/omp2cc` wraps everything below. It is a command on
PATH, not a casr subcommand, so run `omp2cc <id-prefix>`, never
`casr omp2cc ...`:

```bash
omp2cc 01a16dcc                          # convert omp session into Claude Code
omp2cc 01a16dcc --dry-run                # preview
OMP2CC_PROVIDER=pi-agent omp2cc <prefix> # another path-keyed source
OMP2CC_LIMIT=500 omp2cc <old-prefix>     # search deeper for old sessions
```

It searches from `$HOME`, rejects ambiguous prefixes, and ends with a
ready-to-paste `cd '<workspace>' && claude --resume <id>` line.

## Resume by file path (required for omp and pi-agent)

In casr 0.3.0, looking up an omp or pi-agent session by ID fails with
`Session '<id>' not found ... (0 sessions scanned)`, even though `casr list`
shows it. `casr info <id>` fails the same way. Claude Code and Codex IDs resolve
normally. Some omp IDs also map to a subagent file, not to `<id>.jsonl`, so the
file name cannot be guessed. Read the path from `casr list --json` and pass it
as `--source`. This works for every provider:

```bash
PREFIX=01a19ae3   # first characters of the session ID
read -r ID SRC < <(casr list --provider omp --limit 30 --json 2>/dev/null \
  | python3 -c 'import json,sys; p=sys.argv[1]; print(*next((i["session_id"],i["path"]) for i in json.load(sys.stdin)["items"] if i["session_id"].startswith(p)))' "$PREFIX")
casr resume cc "$ID" --source "$SRC" --dry-run   # preview
casr resume cc "$ID" --source "$SRC"             # convert
```

Use a variable name other than `path` in zsh: `path` is tied to `$PATH`.

## After converting

Successful output looks like:

```text
✓ Converted omp session to claude-code
  Target → c46e3e8a-...
  Written → /home/<user>/.claude/projects/-home-<user>-tmp/c46e3e8a-....jsonl
  Resume: claude --resume c46e3e8a-...
```

Claude Code finds sessions by working directory. Run the printed
`claude --resume <id>` from the source session's workspace (the folder encoded
in the `Written` path). To resume from somewhere else, convert with
`--workspace <dir>`.

## Options that change the result

| Flag | Effect |
|---|---|
| `--dry-run` | Report what would be converted; write nothing |
| `--max-context-tokens N` | Default 200000; oldest turns dropped first. `0` keeps everything |
| `--max-tool-output N` | Default 4000 characters per tool result. `0` keeps everything |
| `--keep-reasoning` | Keep source reasoning traces (dropped by default) |
| `--enrich` | Add context messages explaining the conversion to the target agent |
| `--force` | Overwrite an existing converted session in the target |
| `--json` | Machine-readable output |

## Known failures

- `Session validation failed: Session must have at least one user message and
  one assistant message.` The source session has no assistant reply yet. Pick
  another session.
- Very large sessions (tens of MB) are trimmed hard by the default token cap.
  Raise `--max-context-tokens` when the full history matters.
