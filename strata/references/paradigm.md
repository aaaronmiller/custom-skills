---
date: 2026-05-18 10:00:00 PDT
ver: 1.0.0
author: ice-ninja
model: claude-opus-4-7
tags: [strata, paradigm, three-layer, four-crafts, substrate, continuity]
---

# The STRATA Paradigm

## The one failure with two faces

Vibe coding and spec-driven development do not fail for different reasons. They fail for the same reason, expressed two ways. Both treat three distinct concerns as one. Vibe refuses to separate them and lets the model resolve all three live with no memory and no contract. Spec-driven fuses them into a single document: intent buried inside the spec, the testable contract diluted with prose, and architecture pre-locked at the top before the system that should own that decision ever reasons about it.

Two observable consequences. First, an upstream change such as a deployment target moving detonates a spec-driven scaffold, because every downstream task inherited the fused assumption. Second, a project that sits dormant develops amnesia, because the intent lived only in a human head and an untrusted git log, and reconstruction becomes archaeology.

## The three layers

Intent is what the user wants, under what constraints, with what success and failure conditions, including the scale and quality expectations that downstream architecture is derived from. Non-functional requirements belong here, not in the spec, because they drive architecture decisions the spec never makes. The deployment target is intent: it is a constraint, not an architecture.

Specification is the evaluable contract. The single litmus: can a clause be converted into an evaluation that returns pass or fail. If not, it is intent disguised as spec or it is noise. The spec describes nothing; it verifies.

Implementation is the architectural layer. It belongs to the system, derived from intent plus empirical memory plus the existing stack plus risk tolerance. It does not belong to the user and it does not belong to the spec document. The user writing a technology choice into the spec is the original sin.

## The four crafts (lineage: Nate B. Jones, February 2026)

Intent Crafting and Spec Crafting are performed by the human. Context Crafting and Prompt Crafting are performed by the system. STRATA assigns each craft to exactly one artifact and one author so the layers cannot silently re-fuse.

## The substrate stack (lineage: Dan Shapiro, January 2026)

Shapiro's zero-indexed levels run from spicy autocomplete (S0) to the dark factory (S5), where a specification enters and tested software exits with no human writing or reviewing code, evaluated against scenarios stored separately so the system cannot game them. STRATA operationalizes S3, the intent-driven level, honestly. It does not pretend to be S5.

## The gap STRATA closes (lineage: Kapil Viren Ahuja, May 2026, extended here)

Kapil's autopsy is correct and stops one layer short. He names continuity as the unsolved problem and does not ship the fix. Spec-driven development solves structure at the moment of creation and has no answer for continuity across time. Memory is not a feature. It is the prerequisite for any level above the one where a human is continuously present.

STRATA's contribution is to treat the system's memory of where it is standing as a first-class, load-bearing artifact authored with the same rigor as the contract. The continuity ledger plus a plain-language standing pointer is the spine. It also feeds backward: recorded outcomes become the empirical memory that Context Crafting derives from on the next project, which is what turns architecture selection from guesswork into repeatable engineering.

## What STRATA inherits and what it adds

It inherits, unchanged in spirit, the create-new-project discipline: two intake modes plus a fast track, a conservative confidence gate, mandatory prior-art research, data-architecture decision-making, deliberative refinement, and a clean delivery handoff. It adds the six-artifact separation, the validator that fails the build on a fused layer or an unbound clause, the append-only continuity ledger as load-bearing structure, and the honest substrate self-location file.

The methodology is the product. The tool is downstream of the discipline.
