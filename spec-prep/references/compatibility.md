---
date: 2026-05-18 10:00:00 PDT
ver: 1.0.0
author: ice-ninja
model: claude-opus-4-7
tags: [spec-prep, compatibility, speckit, openspec, kiro, handoff]
---

# Compatibility and Handoff

spec-prep artifacts are plain markdown and feed directly into existing spec-driven toolchains. The mapping below also shows what spec-prep adds that those tools do not have.

## SpecKit

For the current preparation pipeline and native artifact paths, read `intake-and-speckit.md`. That 2.2 reference supersedes this legacy mapping.

For new native preparation, requirements.md plus intent.md feed specify under the constitution; generated spec.md plus constitution, design.md and intent guidance feed plan. Preserve native stories and scenarios, then generate tasks and analyze. Read intake-and-speckit.md for the actual procedure. Do not feed an already-generated spec back into specify as raw intake or duplicate an operational plan. Existing legacy context/design sources remain accepted. The input trio is the compact interface; generated native artifacts and governance are separate outputs.

## OpenSpec

`intent.md` and `spec.md` map to the proposal and `specs/` capabilities, using SHALL and MUST language already present in the spec template. `context.md` maps to `design.md`. Plays map to the change tasks. The ledger and substrate files travel alongside the OpenSpec change directory.

## Kiro

Both `intent.md` and `spec.md` load as Kiro spec input. `context.md` is the technical plan. Kiro's living-specs concept is a partial overlap with the spec-prep ledger; keep the spec-prep ledger as the authoritative continuity record because it is append-only and carries the backward feed into Context Crafting, which living specs do not.

## Cursor and generic agents

All files are self-contained markdown with no tool-specific syntax. Any agent that reads markdown can consume the tree.

## Handoff protocol

A fresh session reads AGENTS.md, the constitution and reset handoff first. Read existing standing/ledger and verify receipt hashes when present, then intent and the applicable native spec/plan/task. An input handoff does not need a fabricated ledger or native pass. Preparation-only status survives reset: stop before implementation until the user explicitly authorizes it. The handoff must supply the context needed without the authoring conversation.

## Next-step commands

Spec Kit: inspect installed syntax/integration and existing tree, initialize safely only when needed, then run constitution/specify/clarify/plan/tasks/analyze with the source mapping above. Finish the reset handoff and stop before implementation for a preparation-only request.
OpenSpec: `openspec init` then `/opsx:propose` with the intent and spec.
Kiro: load `intent.md` and `context.md` into the spec workflow.
Direct: hand the tree to any markdown-reading coding agent and point it at `standing.md` first.
