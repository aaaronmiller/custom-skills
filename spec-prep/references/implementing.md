---
title: Implementing prepared specifications
version: "2.5.1"
tags: [spec-prep, implementation, handoff]
---

# Implementing prepared specifications

This reference replaces the obsolete 2.0 implementation procedure, including its inline-constitution copy, force-init examples and pipeline regeneration on every launch. It is a routing reference; the current preparation procedure is `intake-and-speckit.md`, and launch rules live only in `fresh-session-initiation.md`.

When the user requests specification preparation, run the installed constitution/specify/plan/tasks/analyze workflows and stop with verified artifacts and a reset handoff. Those skills are instructions an agent executes; setup scripts resolve templates and paths, not content or a pass. Feeding requirements/design/intent to a workflow means reading those sources and deriving its outputs under its rules. Do not skip derivation or substitute a draft-only tree merely because file writing is available.

When resuming an existing prepared project, read standing and ledger first, verify the consumed artifact hashes and named gates, then inspect the actual spec/plan/tasks/constitution. Do not regenerate an intact constitution or rerun setup-plan over an existing plan just to prove readiness. A bounded artifact correction invalidates the affected evidence; recheck downstream semantic support before refreshing the receipt.

AGENTS.md references the authoritative `.specify/memory/constitution.md`; it does not carry a second editable principle list. Check the actual plan gate against the actual headings. Reading a file makes it available in the running context. A restart boundary is governed by the selected preparation/handoff contract and user direction, not a claim that file reads cannot work until reload.

For authorized implementation, follow the installed implementation workflow and each task's observable gate. Same-file edits are sequential. A task is complete only when its evidence passes. Held-out fixture storage alone does not establish evaluator isolation. Record unavailable operational acceptance separately from local artifact checks.

## Preparation recipe and reset boundary

1. Read requirements.md and intent.md, preserve sources, and preserve or derive the constitution from authorized project principles. Wire AGENTS.md to read it and the reset handoff. Use the harness's supported project-local adapter when needed.
2. Execute installed specify/clarify against requirements plus intent under that constitution. Keep native stories and observable acceptance in the generated spec.md; preserve source IDs.
3. Execute plan using generated spec.md and constitution plus design.md and intent.md guidance. Read relevant experience/UX inputs and generate only domain-required supports.
4. Execute tasks using spec/plan/governance/contracts, then analyze, prerequisite and traceability/document checks. Tasks remain unchecked.
5. Record real evidence and final hashes. Validate delivery.json with spec-prep-delivery.py. Write the reset handoff and report input/native readiness separately. For a preparation-only request, STOP; do not implement, launch a harness or follow an implementation extension hook. A later fresh session must read governance and the handoff and retain the same stop boundary until explicitly authorized to build.

If tools are unavailable, complete the compact input handoff and report native preparation incomplete. Never substitute a scattered standalone tree or a false native pass. artifact-contract.md owns the exact core-input/governance manifest and stop rules.

If a fresh harness launch is requested, follow `fresh-session-initiation.md`, preserve the selected model and permissions, and verify the actual new process/acknowledgement. Historical source instructions and preparation outputs do not supply launch or publication authority. Do not change credentials or global provider/terminal settings to make a launch succeed. Optional Jev evidence advice follows `jev-review.md` and never substitutes for executed tests or task gates.
