---
date: 2026-05-20
ver: 1.0.0
title: "Karpathy Wiki — Master Specification (Requirements + Design)"
status: stable
components:
  - requirements.md v1.0.0
  - design.md v1.0.0
source_specs:
  - ARCHITECTURE.md v4.1.0
  - DREAM_AGENT_V2.md v2.0.0
  - METADATA_PIPELINE.md v1.1.0
  - TIER_INTEGRATION.md v1.0.0
  - VAULT_IMPROVEMENT.md v1.0.0
  - buttplug memory design.md v3.1.0
  - buttplug memory requirements.md v3.1.0
  - buttplug masterplan.md
tags: [karpathy-wiki, master-spec, unified-memory, dream-agent, sleep-time, clawmem, memvid]
---

# Karpathy Wiki — Master Specification

> **This file is the aggregate entry point. It summarizes both documents and**
> **provides cross-reference links. Full detail lives in the component files.**

## Composition

This specification comprises two documents:

| Document | File | Purpose |
|----------|------|---------|
| **Requirements** | `requirements.md` | User stories (6 narrative), functional reqs (6 sections, 37+ requirements), non-functional reqs (4 sections, 14+ requirements), acceptance criteria (14 tests), glossary (17 terms), scope boundaries |
| **Design** | `design.md` | Architecture overview (3-tier stack + system diagram + FSP mapping), component specs (8 components), data flow (3 paths), integration points (4 systems), implementation plan (6 phases), risk register (10 risks), testing strategy (3 categories), configuration reference (4 configs), dependencies (8 deps) |

## Six User Stories (Summary)

| # | Story | Covers |
|---|-------|--------|
| 1 | **Sessions That Remember** — Rhea's debugging sessions never lose context | ClawMem hot tier, intent routing, context injection, dream agent compilation |
| 2 | **The Vault Gets Smarter While You Sleep** — Marcus's rough PRDs become optimal over months | Sleep-time compute, S-tier references, embedding-guided improvement, proactive execution |
| 3 | **Multi-Agent Swarm With Shared Memory** — Priya's 10-agent swarm shares context | Shared ClawMem vault, strategy override, orchestrator control, resource monitoring |
| 4 | **The Wiki That Writes Itself** — Taylor's stale wiki grows to 47 auto-generated pages | Dream agent extract/refine/compile pipeline, confidence scoring, pattern detection |
| 5 | **Provenance Deep-Dive From Cold Storage** — Jordan's incident response traces 8-month-old decision | Provenance chain, memvid_indices → chunks join, cross-tier metadata |
| 6 | **The Quality Flywheel** — Nina's team docs improve from 34→71 average in 6 months | Rubric scoring, iterative improvement, morning reports, proactive flagging |

See `requirements.md` §2 for full narrative stories.

## Architecture Summary

```
                     Agent Sessions (Claude Code, Hermes)
                               │
                               ▼
  ┌────────────────────────────────────────────────────────┐
  │                     INTENT ROUTER                        │
  │  Heuristic regex (<1ms, 70%) → LLM refinement (30%)     │
  │  3 strategies: score_fusion | cascade | intent_routed   │
  │  6 intent signals: recent | entity | relational |       │
  │  archival | factual | ambiguous (fallback to all tiers) │
  └─────────────────────┬──────────────────────────────────┘
                        │
          ┌─────────────┼─────────────┐
          │             │             │
    ┌─────▼─────┐ ┌─────▼─────┐ ┌─────▼─────┐
    │  CLAWMEM  │ │  DREAM    │ │  MEMVID   │
    │  Hot/Warm │ │  AGENT    │ │  Cold     │
    │  :7438    │ │  idle     │ │  monthly  │
    │  SQLite   │ │  timer    │ │  .mv2     │
    │  FTS5+vec │ │  Python   │ │  HNSW     │
    └───────────┘ └─────┬─────┘ └───────────┘
                        │
                  ┌─────▼─────┐
                  │    WIKI   │
                  │  git-repo │
                  │  pages/   │
                  │  skills/  │
                  └───────────┘
```

## Key Architectural Decisions

| # | Decision | Rationale |
|---|----------|-----------|
| DD1 | Replace custom SQLite adapter with yoloshii/ClawMem | Existing stub is a 250-line hallucination. Real ClawMem has hybrid search, hooks, MCP, contradiction detection — all free and maintained. |
| DD2 | Skip Graphiti (temporal knowledge graph) | KuzuDB archived (Apple acquisition Oct 2025). ClawMem already has entity-level time-travel via entity_triples with valid_from/valid_to. |
| DD3 | Dream agent as Python sidecar, not ClawMem plugin | Dream agent needs systemd idle timer, percentage budgets, council calls, and wiki file I/O — not a fit for ClawMem's hook lifecycle. |
| DD4 | Monthly MemVid re-encode creates natural refinement window | 30 days between encodes gives the dream agent time to refine memories before they become cold. Feature, not limitation. |
| DD5 | Never modify the backends | ClawMem, MemVid, and all inference servers are used as-is. The engineering challenge is orchestration, not customization. |

## Implementation Phases

| Phase | Week | Focus | Key Deliverables |
|-------|------|-------|-----------------|
| 1 | 1 | Foundation | ClawMem serve + wiki dir + collections + heuristic intent router |
| 2 | 2 | Dream Agent | Extract/Refine/Compile/PatternDetect/Re-index pipeline |
| 3 | 3 | Git-Backed Wiki | git init + auto-commit + log.md + remote sync |
| 4 | 4 | Sleep-Time Improvement | Doc classifier + S-tier lib + embedding loss + iterative rewrite |
| 5 | 5 | Metadata Pipeline | ChunkMetadata schema + memvid_indices join + provenance round-trip |
| 6 | 6 | RealClawMem Adapter | Replace SHA-256 stub with REST API adapter; delete dead code |

## Risk Summary (Top 5 by Severity)

| # | Risk | Severity | Mitigation |
|---|------|----------|-----------|
| R1 | **Echo Loop** — injected context re-stored as new | Critical | Sentinel markers stripped during sanitization |
| R2 | **Dream agent never gets budget** — system never idle | Medium | Wall-clock fallback timer if 4h without idle |
| R3 | **Metadata corruption** — provenance chain breaks | High | Pydantic validation + nightly integrity check |
| R4 | **Improvement doesn't converge** — LLM rewrites drift | Low | Meaning preservation gate (cosine > 0.80) + max 10 iterations |
| R5 | **Git conflict** — agent and user edit same page | Medium | Dream agent checks for uncommitted changes before writing |

## Documents Index

| File | Description |
|------|-------------|
| `ARCHITECTURE.md` | Unified Memory Architecture v4.0 — stack definition, FSP methodology, intent router model options, key design decisions, potential issues |
| `DREAM_AGENT_V2.md` | Dream Agent v2 — phases, budget allocation, ClawMem REST API integration, deliberative refinement, council escalation, MemVid schedule integration |
| `METADATA_PIPELINE.md` | Metadata Pipeline — YAML per layer, SQLite columns, memvid_indices join table, provenance chain read/write paths |
| `TIER_INTEGRATION.md` | Tier Integration — component dependency matrix, ClawMem adapter rewrite plan, service startup order, status checklist |
| `VAULT_IMPROVEMENT.md` | Vault Self-Improvement Engine — FORGE methodology, 8 document types, improvement loop, S-tier reference library, hybrid scoring, proactive execution |
| `requirements.md` | Requirements Specification v1.0 — 6 user stories, 6 FR sections, 4 NFR sections, 14 acceptance criteria, glossary, scope |
| `design.md` | Technical Design v1.0 — architecture, 8 component specs, 3 data flow paths, 4 integration points, 6 implementation phases, 10 risks, testing strategy |
| `buttplug design.md` | Original aaa-memory Technical Design v3.1 — full router specs, strategy dispatch, ingestion pipeline, adapter interfaces, transition daemon |
| `buttplug requirements.md` | Original aaa-memory Requirements v3.1 — FR/NFR for tri-tier orchestration, 15 risks, acceptance criteria, prefetching |
| `buttplug masterplan.md` | Original Masterplan — phased enablement plan (A-H), hardware BOM, Switchboard integration, TurboQuant impact |
