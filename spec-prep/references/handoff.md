---
title: Fresh-session handoff
tags: [spec-prep]
---

# Fresh-session handoff

## Fresh-session initiation

Read only when the current request expressly authorizes project initiation. The reboot rule and the launch-authority test are owned by SKILL.md Phase 7; this file covers how an authorized initiation is carried out and verified. Specification preparation otherwise stops at the reset handoff. When initiation is authorized, no redundant confirmation is needed for the named project and allowed local work.

### Before launch

Read preparation.json and verify lifecycle `specification-prepared`, every named gate, artifact existence and artifact hashes (where the host runs code, `scripts/spec-prep-delivery.py` does this; otherwise recompute each SHA-256 and compare it by hand). Read reset-handoff.md. Resolve the harness command from the current request or installed project configuration. Preserve its chosen model, effort and permissions. If several plausible harnesses change the execution target and no configuration settles it, ask. Do not guess a provider, add permission-bypass flags, or reuse an old session ID.

Record the launch authority beside the launch record: the user's actual current launch instruction, when it was given, the exact absolute build root, and the SHA-256 digests of preparation.json and reset-handoff.md as they stand at launch. Recompute both digests immediately before launching; a mismatch means the prepared handoff changed and the launch stops. This record is an audit and scope note, not authentication of a human instruction. Preparation receipts stay `implementationAuthorized: false`; the launch record never rewrites them, and no second approval is requested.

### Launch

Launch through the host's terminal or harness mechanism (a new terminal tab or window, a tmux window, or a custom terminal command) with the real build root as the working directory and the handoff prompt as a standalone argument. Inspect the installed terminal CLI help for exact syntax; under WSL with a Windows terminal, run the harness inside the distribution with the build root as its working directory. Do not change terminal configuration, routing or credentials to make a launch succeed.

Primary terminal references: https://wezterm.org/cli/cli/spawn.html, https://learn.microsoft.com/windows/terminal/command-line-arguments, https://sw.kovidgoyal.net/kitty/launch/, https://manpages.ubuntu.com/manpages/noble/man1/gnome-terminal.1.html. Local CLI help decides installed syntax.

### Verify the new session

Record the returned pane or process identifier, the command and the time. Then require the new harness to write `fresh-session-ack.md` in the project containing its working directory, the consumed handoff hash, its session identifier and the chosen next task. The acknowledgement is valid only from a session ID with no parent linkage to the authoring session. Observe that acknowledgement before claiming initiation verified. A spawned tab alone proves only launch transport, not task execution or build completion.

### On failure

If the terminal is unavailable, use another authorized installed adapter. If launch fails, preserve the handoff and report the exact failed mechanism with a pasteable manual launch prompt. Do not kill or reset the authoring session.
