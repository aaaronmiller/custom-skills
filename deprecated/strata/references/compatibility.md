---
date: 2026-05-18 10:00:00 PDT
ver: 1.0.0
author: ice-ninja
model: claude-opus-4-7
tags: [strata, compatibility, speckit, openspec, kiro, handoff]
---

# Compatibility and Handoff

STRATA artifacts are plain markdown and feed directly into existing spec-driven toolchains. The mapping below also shows what STRATA adds that those tools do not have.

## SpecKit

`intent.md` plus `spec.md` feed `/speckit.specify`. Append intent for the why and constraints, spec for the testable contract. `context.md` feeds `/speckit.plan`; SpecKit decomposes it into its multi-file plan structure during the plan phase, no manual splitting needed. `plays/` feeds `/speckit.tasks`, but STRATA plays are intent-encoded so they survive the pivots that shatter a generated `tasks.md`. `constitution.md` is the shared governance file SpecKit also uses. SpecKit has no equivalent of `ledger/` or `substrate.md`; those are the STRATA value-add and should be carried alongside the SpecKit tree, not discarded.

## OpenSpec

`intent.md` and `spec.md` map to the proposal and `specs/` capabilities, using SHALL and MUST language already present in the spec template. `context.md` maps to `design.md`. Plays map to the change tasks. The ledger and substrate files travel alongside the OpenSpec change directory.

## Kiro

Both `intent.md` and `spec.md` load as Kiro spec input. `context.md` is the technical plan. Kiro's living-specs concept is a partial overlap with the STRATA ledger; keep the STRATA ledger as the authoritative continuity record because it is append-only and carries the backward feed into Context Crafting, which living specs do not.

## Cursor and generic agents

All files are self-contained markdown with no tool-specific syntax. Any agent that reads markdown can consume the tree.

## Handoff protocol

A fresh session resumes by reading `ledger/standing.md` and the tail of `ledger/ledger.md` first, then `intent.md` and `spec.md`, then proceeds. It never needs the originating conversation's context. This is the property that makes the tree dormancy-proof: the continuity files carry what the chat history used to carry, and they do not evaporate when the session ends.

## Next-step commands

SpecKit: `specify init <project>` then `/speckit.specify` with `intent.md` and `spec.md`.
OpenSpec: `openspec init` then `/opsx:propose` with the intent and spec.
Kiro: load `intent.md` and `context.md` into the spec workflow.
Direct: hand the tree to any markdown-reading coding agent and point it at `standing.md` first.
