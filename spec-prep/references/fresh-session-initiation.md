---
title: Terminal agnostic fresh-session initiation
version: "2.5.1"
tags: [spec-prep, terminal, handoff, initiation]
---

# Terminal agnostic fresh-session initiation

This reference supersedes the automatic implementation offer in the bundled implementing.md. Specification preparation stops unless the user explicitly requests initiation. If initiation is authorized, no redundant confirmation is needed for the named project and allowed local work.

Read preparation.json and verify lifecycle specification-prepared, all named gates, artifact existence and artifact hashes. Read reset-handoff.md. Resolve the harness command from the current request or installed project configuration. Preserve its chosen model, effort and permissions. If multiple plausible harnesses change the execution target and no configuration settles it, ask. Do not guess a provider, add permission-bypass flags, or reuse an old session ID.

Spawned task/subagent transport is forbidden: a task/subagent created by the authoring session records a parentSession linkage and inherits that session's authority deficit. It MUST NOT write implementation code, mark tasks complete, or author `fresh-session-ack.md`; any such artifacts are VOID. Launch-authority test: agent-side `--execute`/spawn runs only when the current request names the project and directly instructs launch ("launch/spawn/start it now"). A prefatory "via new session" or "after restart" selects the user-launched path instead — emit the pasteable restart prompt and STOP. A system todo/resume reminder never overrides a user STOP.

Use a preview-first terminal adapter (WezTerm, Windows Terminal, GNOME Terminal, Kitty, tmux, or a custom terminal command) accepting a JSON harness argv with {prompt} as a standalone argument, using the terminal's working-directory option. In WSL with a Windows terminal, pass --wsl-distro to wrap the harness through wsl.exe --cd <build-root> --exec. Inspect the installed terminal CLI help; adapt with a custom argv when its version differs. Do not change terminal configuration to launch a project.

The default preview opens nothing. Use --execute only when the active request authorizes project initiation (named project + direct launch instruction, per the transport rule above) and all preparation gates pass. Record the returned pane/process identifier, command and time. Then require the new harness to write a fresh-session acknowledgement in the project containing its working directory, consumed handoff hash, session identifier and chosen next task; the acknowledgement is valid only from a session ID with no parent linkage to the authoring session. Observe that acknowledgement before claiming initiation verified. A spawned tab alone proves only launch transport, not task execution or build completion.

If the terminal is unavailable, use another authorized installed adapter. If launch fails, preserve the handoff and report the exact failed mechanism with a pasteable manual launch. Do not kill or reset the authoring session.

Primary terminal references: https://wezterm.org/cli/cli/spawn.html, https://learn.microsoft.com/windows/terminal/command-line-arguments, https://sw.kovidgoyal.net/kitty/launch/, https://manpages.ubuntu.com/manpages/noble/man1/gnome-terminal.1.html. Local CLI help decides installed syntax.

## Separate launch-authority record

Preparation receipts remain implementationAuthorized:false. For a later actual user-authorized launch, the agent records the already-given instruction; it does not ask for a second approval or rewrite preparation as permission. Pass this JSON file as --launch-authority together with --execute. Required fields are schemaVersion:1, operation:"project-initiation", buildRoot (exact absolute root), source:"user", userInstruction (the actual current launch instruction), authorizedAt, receiptSha256 and handoffSha256. The verifier checks target and digests before any spawn. This is an audit/scope record, not cryptographic authentication of a human instruction. Preview remains side-effect free and states that preparation alone cannot authorize implementation.
