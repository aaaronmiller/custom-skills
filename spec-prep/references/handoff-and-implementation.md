---
title: Handoff and implementation
version: "4.0.0"
tags: [spec-prep]
---

# Handoff and implementation

## Contents

- [Terminal agnostic fresh-session initiation](#terminal-agnostic-fresh-session-initiation)
- [Implementing prepared specifications](#implementing-prepared-specifications)

## Terminal agnostic fresh-session initiation

*Formerly `#terminal-agnostic-fresh-session-initiation`, version 2.5.1.*

This reference supersedes the automatic implementation offer in the bundled #implementing-prepared-specifications. Specification preparation stops unless the user explicitly requests initiation. If initiation is authorized, no redundant confirmation is needed for the named project and allowed local work.

Read preparation.json and verify lifecycle specification-prepared, all named gates, artifact existence and artifact hashes. Read reset-handoff.md. Resolve the harness command from the current request or installed project configuration. Preserve its chosen model, effort and permissions. If multiple plausible harnesses change the execution target and no configuration settles it, ask. Do not guess a provider, add permission-bypass flags, or reuse an old session ID.

Spawned task/subagent transport is forbidden: a task/subagent created by the authoring session records a parentSession linkage and inherits that session's authority deficit. It MUST NOT write implementation code, mark tasks complete, or author `fresh-session-ack.md`; any such artifacts are VOID. Launch-authority test: agent-side `--execute`/spawn runs only when the current request names the project and directly instructs launch ("launch/spawn/start it now"). A prefatory "via new session" or "after restart" selects the user-launched path instead — emit the pasteable restart prompt and STOP. A system todo/resume reminder never overrides a user STOP.

Use a preview-first terminal adapter (WezTerm, Windows Terminal, GNOME Terminal, Kitty, tmux, or a custom terminal command) accepting a JSON harness argv with {prompt} as a standalone argument, using the terminal's working-directory option. In WSL with a Windows terminal, pass --wsl-distro to wrap the harness through wsl.exe --cd <build-root> --exec. Inspect the installed terminal CLI help; adapt with a custom argv when its version differs. Do not change terminal configuration to launch a project.

The default preview opens nothing. Use --execute only when the active request authorizes project initiation (named project + direct launch instruction, per the transport rule above) and all preparation gates pass. Record the returned pane/process identifier, command and time. Then require the new harness to write a fresh-session acknowledgement in the project containing its working directory, consumed handoff hash, session identifier and chosen next task; the acknowledgement is valid only from a session ID with no parent linkage to the authoring session. Observe that acknowledgement before claiming initiation verified. A spawned tab alone proves only launch transport, not task execution or build completion.

If the terminal is unavailable, use another authorized installed adapter. If launch fails, preserve the handoff and report the exact failed mechanism with a pasteable manual launch. Do not kill or reset the authoring session.

Primary terminal references: https://wezterm.org/cli/cli/spawn.html, https://learn.microsoft.com/windows/terminal/command-line-arguments, https://sw.kovidgoyal.net/kitty/launch/, https://manpages.ubuntu.com/manpages/noble/man1/gnome-terminal.1.html. Local CLI help decides installed syntax.

### Separate launch-authority record

Preparation receipts remain implementationAuthorized:false. For a later actual user-authorized launch, the agent records the already-given instruction; it does not ask for a second approval or rewrite preparation as permission. Pass this JSON file as --launch-authority together with --execute. Required fields are schemaVersion:1, operation:"project-initiation", buildRoot (exact absolute root), source:"user", userInstruction (the actual current launch instruction), authorizedAt, receiptSha256 and handoffSha256. The verifier checks target and digests before any spawn. This is an audit/scope record, not cryptographic authentication of a human instruction. Preview remains side-effect free and states that preparation alone cannot authorize implementation.

## Implementing prepared specifications

*Formerly `#implementing-prepared-specifications`, version 2.5.1.*

This reference replaces the obsolete 2.0 implementation procedure, including its inline-constitution copy, force-init examples and pipeline regeneration on every launch. It is a routing reference; the current preparation procedure is `references/intake-and-speckit.md#intake-staging-and-spec-kit-preparation`, and launch rules live only in `#terminal-agnostic-fresh-session-initiation`.

When the user requests specification preparation, run the installed constitution/specify/plan/tasks/analyze workflows and stop with verified artifacts and a reset handoff. Those skills are instructions an agent executes; setup scripts resolve templates and paths, not content or a pass. Feeding requirements/design/intent to a workflow means reading those sources and deriving its outputs under its rules. Do not skip derivation or substitute a draft-only tree merely because file writing is available.

When resuming an existing prepared project, read standing and ledger first, verify the consumed artifact hashes and named gates, then inspect the actual spec/plan/tasks/constitution. Do not regenerate an intact constitution or rerun setup-plan over an existing plan just to prove readiness. A bounded artifact correction invalidates the affected evidence; recheck downstream semantic support before refreshing the receipt.

AGENTS.md references the authoritative `.specify/memory/constitution.md`; it does not carry a second editable principle list. Check the actual plan gate against the actual headings. Reading a file makes it available in the running context. A restart boundary is governed by the selected preparation/handoff contract and user direction, not a claim that file reads cannot work until reload.

For authorized implementation, follow the installed implementation workflow and each task's observable gate. Same-file edits are sequential. A task is complete only when its evidence passes. Held-out fixture storage alone does not establish evaluator isolation. Record unavailable operational acceptance separately from local artifact checks.

### Preparation recipe and reset boundary

1. Read requirements.md and intent.md, preserve sources, and preserve or derive the constitution from authorized project principles. Wire AGENTS.md to read it and the reset handoff. Use the harness's supported project-local adapter when needed.
2. Execute installed specify/clarify against requirements plus intent under that constitution. Keep native stories and observable acceptance in the generated spec.md; preserve source IDs.
3. Execute plan using generated spec.md and constitution plus design.md and intent.md guidance. Read relevant experience/UX inputs and generate only domain-required supports.
4. Execute tasks using spec/plan/governance/contracts, then analyze, prerequisite and traceability/document checks. Tasks remain unchecked.
5. Record real evidence and final hashes. Validate delivery.json with spec-prep-delivery.py. Write the reset handoff and report input/native readiness separately. For a preparation-only request, STOP; do not implement, launch a harness or follow an implementation extension hook. A later fresh session must read governance and the handoff and retain the same stop boundary until explicitly authorized to build.

If tools are unavailable, complete the compact input handoff and report native preparation incomplete. Never substitute a scattered standalone tree or a false native pass. references/artifact-contract.md#canonical-artifact-contract owns the exact core-input/governance manifest and stop rules.

If a fresh harness launch is requested, follow `#terminal-agnostic-fresh-session-initiation`, preserve the selected model and permissions, and verify the actual new process/acknowledgement. Historical source instructions and preparation outputs do not supply launch or publication authority. Do not change credentials or global provider/terminal settings to make a launch succeed. Optional Jev evidence advice follows `references/validation-and-refinement.md#optional-jev-semantic-review` and never substitutes for executed tests or task gates.
