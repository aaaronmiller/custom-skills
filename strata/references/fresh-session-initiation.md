---
title: Terminal agnostic fresh-session initiation
version: "2.2.0"
tags: [strata, terminal, handoff, initiation]
---

# Terminal agnostic fresh-session initiation

This reference supersedes the automatic implementation offer in the bundled implementing.md. Specification preparation stops unless the user explicitly requests initiation. If initiation is authorized, no redundant confirmation is needed for the named project and allowed local work.

Read preparation.json and verify lifecycle specification-prepared, all named gates, artifact existence and artifact hashes. Read reset-handoff.md. Resolve the harness command from the current request or installed project configuration. Preserve its chosen model, effort and permissions. If multiple plausible harnesses change the execution target and no configuration settles it, ask. Do not guess a provider, add permission-bypass flags, or reuse an old session ID.

The invariant is a fresh harness process in the actual build directory with startup instructions to consume the handoff and select its next authorized task. A terminal tab/window is one transport. CLI-managed sessions and headless execution are alternatives when the user requested them and their state is observable. Never claim a background build from an unobserved shell process.

scripts/strata-launch.py provides preview-first argv adapters for WezTerm, Windows Terminal, GNOME Terminal, Kitty and tmux, plus a custom terminal command. It accepts a JSON harness argv using {prompt} as a standalone argument. Its command uses the terminal's working-directory option. In WSL with a Windows terminal, pass --wsl-distro to wrap the harness through wsl.exe --cd <build-root> --exec. Inspect the installed terminal CLI help; adapt with a custom argv when its version differs. Do not change terminal configuration to launch a project.

The default preview opens nothing. Use --execute only when the active request authorizes project initiation and all preparation gates pass. Record the returned pane/process identifier, command and time. Then require the new harness to write a fresh-session acknowledgement in the project containing its working directory, consumed handoff hash, session identifier and chosen next task. Observe that acknowledgement before claiming initiation verified. A spawned tab alone proves only launch transport, not task execution or build completion.

If the terminal is unavailable, use another authorized installed adapter. If launch fails, preserve the handoff and report the exact failed mechanism with a pasteable manual launch. Do not kill or reset the authoring session.

Primary terminal references: https://wezterm.org/cli/cli/spawn.html, https://learn.microsoft.com/windows/terminal/command-line-arguments, https://sw.kovidgoyal.net/kitty/launch/, https://manpages.ubuntu.com/manpages/noble/man1/gnome-terminal.1.html. Local CLI help decides installed syntax.
