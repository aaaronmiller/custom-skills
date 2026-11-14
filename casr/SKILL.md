---
name: casr
description: "Converts a session from one coding agent into another (omp, Codex, Gemini, Claude Code and more) so it can be resumed there."
license: MIT
metadata:
  version: 1.3.0
  requires: casr CLI on PATH, built from the private fork at /home/cheta/code/cross_agent_session_resumer
  tags: "sessions, handoff, meta, TOOL"
---

# casr: Cross Agent Session Resumer

One command for every harness. You name the target; casr finds the source
from the session ID.

```bash
casr -cc <session-id>                        # shorthand: convert into Claude Code
casr resume <target> <session-id>            # canonical form, any target
casr resume <target> <session-id> --dry-run  # preview, write nothing
```

Examples: `casr -cc 01a16dcc-0848-726e-b7a1-90cc0f7ea280` (omp into Claude
Code), `casr resume cod <claude-session-id>` (Claude into Codex).

The alias always names the **target**. There is no `casr <source> ...` form.
`casr <target> resume <id>` also works and means the same as the canonical
form.

Shorthand flags: `-cc`, `-cod`, `-gmi`, `-agy`, `-omp`, `-mus`, `-jcd`, `-ant`.
Every other target needs the canonical form.

Targets: `cc` Claude Code, `cod` Codex, `gmi` Gemini, `agy` Antigravity, `opc`
OpenCode, `pi` Pi-Agent, `omp` Oh My Pi, `ant` Ante, `mus` Muse Code, `jcd`
J-Code, `ocl` OpenClaw, `kr` Kiro, `grk` Grok, `cur`, `cln`, `aid`, `amp`,
`gpt`. `casr providers` shows which are installed.

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

The installed binary is built from the private fork at
`/home/cheta/code/cross_agent_session_resumer`. In that repo `origin` is
`aaaronmiller/cross_agent_session_resumer` (private) and `upstream` is
`Dicklesworthstone/cross_agent_session_resumer`. Upstream has no omp, Ante,
Muse or J-Code provider and does not merge outside contributions, so never
replace the binary with an upstream release. `FORK-CHANGES.md` in the repo
root lists every fork change, the path index and the upstream sync steps.

Rebuild with `cargo build --release` in the fork, then copy
`/home/cheta/.cargo/target-shared/release/casr` (the global cargo target dir,
not the repo's stale `target/`) to `/home/cheta/.local/bin/casr` with
`command cp -f` (`cp` is aliased to `cp -i`). `casr --version` must show the
fork's HEAD commit (`git -C /home/cheta/code/cross_agent_session_resumer
rev-parse --short HEAD`).
