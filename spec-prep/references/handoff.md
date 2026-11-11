---
title: Fresh-session handoff
tags: [spec-prep]
---

# Fresh-session handoff

## Contents

- [What counts as a fresh session](#what-counts-as-a-fresh-session)
- [Fresh-session initiation](#fresh-session-initiation)

## What counts as a fresh session

Read whenever deciding whether a session may implement, mark tasks complete or write `fresh-session-ack.md`. SKILL.md Phase 7 requires "no parent linkage to the authoring session"; this section defines it.

A fresh session is one the user starts, or an explicitly authorized launcher starts, that does not inherit the authoring session's conversation, context or agent tree. It begins with an empty conversation in the real build root, loads AGENTS.md and the constitution at its own start, and receives only the reset handoff (or the pasteable resume prompt) as its task input.

Counts as fresh:

- A new harness process the user starts in a terminal, IDE or app, in the build root.
- A new terminal tab, window or tmux window that an explicitly authorized launcher (SKILL.md Phase 7 launch authority) opens with the build root as working directory and the handoff prompt as its only input.
- A new session in a different harness that the user starts from the handoff.
- A scheduled or cloud agent the user creates whose only task input is the handoff.

Does not count:

- A subagent, task, fork, teammate or background agent of the authoring session, at any depth.
- Resuming, continuing or reattaching the authoring session (a resume or continue flag, the same session ID, or a reopened tab of it), including after compaction or a context clear inside it.
- A session seeded with the authoring transcript or its summary (a converted, forked or replayed session), rather than the handoff alone.
- A process the authoring session spawns without explicit launch authority, whatever its harness.

Evidence: `fresh-session-ack.md` names a session identifier different from the authoring session's, and that session records no parent, fork or resume link to it. When the harness exposes no such linkage data, say so in the acknowledgement instead of asserting freshness.

## Fresh-session initiation

Read only when the current request expressly authorizes project initiation. The reboot rule and the launch-authority test are owned by SKILL.md Phase 7; this file covers how an authorized initiation is carried out and verified. Specification preparation otherwise stops at the reset handoff. When initiation is authorized, no redundant confirmation is needed for the named project and allowed local work.

### Before launch

Read preparation.json and verify lifecycle `specification-prepared`, every named gate, artifact existence and artifact hashes (where the host runs code, `scripts/spec-prep-delivery.py` does this; otherwise recompute each SHA-256 and compare it by hand). Read reset-handoff.md. Resolve the harness command from the current request or installed project configuration. Preserve its chosen model, effort and permissions. If several plausible harnesses change the execution target and no configuration settles it, ask. Do not guess a provider, add permission-bypass flags, or reuse an old session ID.

Record the launch authority beside the launch record: the user's actual current launch instruction, when it was given, the exact absolute build root, and the SHA-256 digests of preparation.json and reset-handoff.md as they stand at launch. Recompute both digests immediately before launching; a mismatch means the prepared handoff changed and the launch stops. This record is an audit and scope note, not authentication of a human instruction. Preparation receipts stay `implementationAuthorized: false`; the launch record never rewrites them, and no second approval is requested.

### Launch

Launch through the host's terminal or harness mechanism (a new terminal tab or window, a tmux window, or a custom terminal command) with the real build root as the working directory and the handoff prompt as a standalone argument. Inspect the installed terminal CLI help for exact syntax; under WSL with a Windows terminal, run the harness inside the distribution with the build root as its working directory. Do not change terminal configuration, routing or credentials to make a launch succeed.

Primary terminal references: https://wezterm.org/cli/cli/spawn.html, https://learn.microsoft.com/windows/terminal/command-line-arguments, https://sw.kovidgoyal.net/kitty/launch/, https://manpages.ubuntu.com/manpages/noble/man1/gnome-terminal.1.html. Local CLI help decides installed syntax.

### Verify the new session

Record the returned pane or process identifier, the command and the time. Then require the new harness to write `fresh-session-ack.md` in the project containing its working directory, the consumed handoff hash, its session identifier and the chosen next task. The acknowledgement is valid only from a session ID with no parent linkage to the authoring session ([What counts as a fresh session](#what-counts-as-a-fresh-session)). Observe that acknowledgement before claiming initiation verified. A spawned tab alone proves only launch transport, not task execution or build completion.

### On failure

If the terminal is unavailable, use another authorized installed adapter. If launch fails, preserve the handoff and report the exact failed mechanism with a pasteable manual launch prompt. Do not kill or reset the authoring session.
