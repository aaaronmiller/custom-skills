---
date: 2026-05-18 10:00:00 PDT
ver: 1.0.0
author: ice-ninja
model: claude-opus-4-7
tags: [strata, confidence-gate, intake, rubric]
---

# Confidence Gate

Score conservatively. One extra question round costs minutes. A fused-layer artifact costs hours. Threshold to proceed is 85% weighted.

| Dimension | Weight | 0 to 25% | 50% | 75% | 100% |
|-----------|--------|----------|-----|-----|------|
| Problem clarity | 12% | Vague pain | Stated, root cause unclear | Root cause with evidence | Quantified before and after |
| Solution definition | 12% | "Something like X" | Concept described | Workflow walkthrough possible | End-to-end journey articulable |
| User personas | 8% | "People who" | One persona | 2 to 3 distinct | Goals, frustrations, context |
| Success criteria | 10% | "It should work" | Qualitative | Measurable | Testable with targets |
| Data model | 12% | No entities | Some named | Entities and relationships | Access patterns and lifecycle |
| Scope boundaries | 8% | Open-ended | Some exclusions | In and out list | Boundary rationale documented |
| Technical constraints | 10% | None | Platform mentioned | Platform, perf, integration | Full constraint matrix |
| Business context | 10% | None | OSS vs commercial decided | Distribution and monetization | Competitive position |
| Layer-separation integrity | 10% | Intent, spec, implementation fully fused in what the user said | Two of three separable | All three separable with effort | User already speaks in distinct layers |
| Continuity readiness | 8% | Nothing to seed a ledger | Some decisions implied | Kickoff decisions extractable | First standing.md writable now |

Below 85%, ask 3 to 5 questions targeting the lowest-weighted-times-lowest-scored dimensions. Reassess after each round. At or above 85%, confirm a one-paragraph understanding summary with the user before proceeding. Dimensions below 75% at proceed time become `[NEEDS CLARIFICATION]` markers in `intent.md`, maximum three.

The two STRATA-specific dimensions matter most. Layer-separation integrity below 50% means the user is speaking in fused layers and the artifacts will inherit the fusion unless intake separates it first. Continuity readiness below 50% means the project cannot seed a ledger and will be born without the spine.
