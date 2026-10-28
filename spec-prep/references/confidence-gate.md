---
date: 2026-05-18 10:00:00 PDT
ver: 1.0.0
author: ice-ninja
model: claude-opus-4-7
tags: [spec-prep, confidence-gate, intake, rubric]
---

# Confidence Gate

Use the dimensions to identify missing information. A weighted score is advisory, not an empirical probability or an approval gate. Sufficient information for the next authorized action controls progress; no score changes the output mode.

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

Ask only about material missing inputs that block their dependent action; continue independent reversible preparation. State the understood scope and provisional defaults without redundant confirmation. Respect native clarification marker limits, keeping other unresolved source needs in the assumption/source map rather than dropping them.

The two spec-prep-specific dimensions matter most. Layer-separation integrity below 50% means the user is speaking in fused layers and the artifacts will inherit the fusion unless intake separates it first. Continuity readiness below 50% means the project cannot seed a ledger and will be born without the spine.
