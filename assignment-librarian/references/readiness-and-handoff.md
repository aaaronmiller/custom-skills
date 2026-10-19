---
title: Readiness triage and spec-prep handoff
version: "1.0"
tags: [assignment-librarian, triage, readiness, handoff, spec-prep]
---

# Readiness triage and spec-prep handoff

This reference covers Operations 3–4 of `SKILL.md`: classifying packets and
handing the ready ones to spec-prep (2.4.0 at
`/home/cheta/code/custom-skills/spec-prep/`) as intake, requirements/design
sources, or intent material.

## Status taxonomy

Exactly one status per packet (`scripts/scan.py` derives it; this is the
normative definition):

- **`unstaged`** — no `project-intake.json`. Raw drop, not yet a packet.
- **`needs-intake`** — manifest present but invalid (schema, dead paths, hash
  mismatch), or any `missing-input` issue (no brief, absent referenced files,
  empty container). Includes research-only and tooling packets whose gaps are
  correctly recorded — `needs-intake` can be a correct terminal state.
- **`ready-for-spec-prep`** — manifest valid, `readOrder` resolves, hashes match,
  brief present, no `missing-input` issues. spec-prep may consume it as-is.
- **`has-specs`** — specification artifacts already exist in the folder
  (`requirements*`, `design*`, `intent*`, `constitution*`, Spec Kit
  `spec.md`/`plan.md`/`tasks.md`) or lifecycle is `specification-prepared` /
  `initiated`. Preparation happened; do not re-prepare, route to the build.

Triage checklist per packet: validator passes; `readOrder` entries open and
read in listed order; declared sha256 values match bytes on disk;
`workbench.json` parses if present (broken workbench is a `conversion` issue,
never a silent drop); status matches the rules above; outcome recorded in
manifest `issues`/`fileNotes`.

## spec-prep handoff

A `ready-for-spec-prep` packet hands off with three verified pieces:

1. **Read order.** `readOrder` first, then `sources` by role. Confirm the
   order tells the story (brief → evidence → detail). spec-prep reads
   `project-intake.json` first, then follows this order.
2. **Findings.** Every conversion-relevant fact is already in `issues` with
   the right severity: what the material is (requirements vs transcript vs
   skill pack vs research), what is missing, what must not be mistaken for a
   build root. spec-prep's intake staging consumes these to choose its operation
   (intake staging vs specification preparation vs recovery).
3. **Workbench check.** If `workbench.json` exists, validate its pointers
   resolve; if absent, note that spec-prep auto mode will generate it. Never
   hand-craft pointers to build roots that do not exist yet.

Handoff statement (paste into the spec-prep request or packet review):

> Packet `<projectId>` is `<readiness>`: manifest v1 valid, `<N>` sources
> hashed, read order `<a> → <b> → ...`. Findings: `<key issues>`. Workbench:
> `<present-valid | absent-automode | needs-repair>`. spec-prep operation:
> `<intake-staging | specification-preparation>`. No specs authored, no
> initiation authorized by this handoff.

spec-prep then owns: intent/spec separation, confidence gate, Spec Kit
constitution/spec/plan/tasks, preparation evidence, reset handoff. This skill
never authors `intent.md`, `spec.md`, `plan.md`, `tasks.md`, or constitutions
inside library folders.

## What stays separate

- Preparation failures belong to spec-prep's gates, not to triage — send the
  packet back with a new `missing-input` issue, do not patch specs in place.
- Initiation (fresh harness, terminal launch) is never implied by readiness;
  `has-specs` is still not launch authority.
- Packets that overlap (shared subsystems, competing contracts) are flagged
  via `relatedProjects` + an `info` issue, not merged by the librarian.
  Merging is a human decision with its own proposal.
