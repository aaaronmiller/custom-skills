---
date: 2026-05-20
ver: 1.0.0
author: synthesis of ARCHITECTURE.md v4.1.0, DREAM_AGENT_V2.md v2.0.0, METADATA_PIPELINE.md v1.1.0, TIER_INTEGRATION.md v1.0.0, VAULT_IMPROVEMENT.md v1.0.0, buttplug memory design.md v3.1.0, buttplug requirements.md v3.1.0, buttplug masterplan.md
tags: [karpathy-wiki, requirements, unified-memory, dream-agent, sleep-time, clawmem, memvid, tri-tier]
---

# Karpathy Wiki — Requirements Specification v1.0

## 1. Vision

The Karpathy Wiki is an **auto-compiling knowledge system** for development teams and knowledge workers. It transforms raw session data, notes, and project artifacts into a structured, permanent wiki — then continuously improves that wiki during idle compute cycles using embedding-guided quality optimization.

The system unifies three memory tiers (Hot → Warm → Cold) through a coherent orchestration layer, treating the vault as "shared RAM" for LLM-human collaboration (Fractal Synthesis Protocol methodology). Sleep-time compute refines vault content toward S-tier references, while a dream agent compiles observations from active sessions into wiki pages with full provenance chains.

Three principles govern the design:

1. **Zero custom models.** Every component uses off-the-shelf backends (ClawMem, MemVid V2) or standard inference APIs. The engineering challenge is orchestration, not model training.
2. **No opaque metadata.** Every layer preserves traceable provenance chains. A memory retrieved from cold storage can be reverse-linked to its original source session, confidence scores, and every intermediate transformation.
3. **Quality compounds over time.** A document dropped raw into the vault today is measurably better in six months — without human effort. When a document reaches threshold quality, the system proactively acts on it.

## 2. User Stories

### Story 1: Sessions That Remember

Rhea is a senior engineer working across 6 repos. Every morning she dives into a different codebase — debugging a production issue in one, reviewing a PR in another, exploring a spike for next quarter's architecture.

Before the wiki, Rhea's sessions were islands. Each Claude Code or Hermes agent session started from zero. She'd re-explain context, re-discover past decisions, and lose thread across days. The error from two weeks ago — the one with the exact workaround she needed — was gone because it scrolled off context and the session was compacted.

With the wiki in place, every session contributes. When Rhea types a prompt, ClawMem surfaces relevant past decisions from the hot tier. When she asks "why did we choose X over Y six months ago," the intent router recognizes the archival signal and queries MemVid's cold storage. The injected context includes provenance — she can trace the memory back to the original session, see the confidence score, and decide whether to trust it.

Over weeks, the dream agent compiles these session observations into permanent wiki pages. The workaround she discovered for that obscure Postgres lock issue is now a first-class wiki page with cross-references and a confidence score. Next time she (or anyone on the team) hits the same problem, it surfaces immediately.

### Story 2: The Vault Gets Smarter While You Sleep

Marcus keeps his entire project portfolio in the vault — rough PRDs, architecture sketches, research transcripts, meeting notes. He drops them in `raw/` and moves on. He doesn't have time to polish documentation.

Before sleep-time compute, the vault was a dumping ground. Documents stayed as-written — rough and incomplete. Marcus would dig through raw transcripts to find the decision he made three months ago, cursing his past self for not writing a proper ADR.

Sleep-time compute changes this. Every night, the dream agent wakes during idle GPU cycles. It classifies each document by type: project plan, research note, tutorial, narrative. For each classified document, it loads the matching S-tier reference — Stripe's API design guide for project plans, a Nobel-winning paper structure for research notes. It embeds both documents and measures the vector distance as a quality metric.

Then it iterates. The first cycle adds a missing timeline section to Marcus's PRD (score 34→52). Next week it adds risk assessment (52→68). Next month it fills dependency mapping (68→84). Each improvement is small, specific, and reversible — committed to git with a descriptive message.

Marcus opens the morning report four months later. "Your AcmeAuth project plan reached optimal quality (92/100). Starting implementation as a background task." The agent scaffolds the project, implements core features, writes tests, and opens a PR. Marcus reviews the code over coffee.

### Story 3: The Multi-Agent Swarm With Shared Memory

Priya runs an always-on agent swarm — 5-10 concurrent sessions working across feature development, code review, testing, and documentation. Each session has its own focus, but they share context through the memory layer.

Before shared memory, Priya's swarm suffered from fragmentation. Session A's discovery about the authentication race condition never reached Session B, which was building the auth integration tests. Priya manually cross-posted findings — a bottleneck that defeated the purpose of automation.

With the unified memory architecture, every session contributes to a shared ClawMem vault. When Session A's decision extractor hook captures the race condition fix, it's immediately indexed in the hot tier — 50ms query latency. Session B's next prompt picks it up automatically through context injection.

Priya configures the orchestrator to use Strategy B (cascade) for latency-sensitive sessions and Strategy A (score fusion) for research-heavy sessions. The strategy override system lets her switch per-session: `AAA_MEMORY_STRATEGY=cascade` for CI tasks, `intent_routed` for exploratory work. She monitors everything through Switchboard's multiplexed terminal view.

The resource monitor tracks VRAM across both GPUs (RTX 3070 + RTX 2080S). When the swarm hits memory pressure, it scales down gracefully — idle sessions get compacted, then paused. Sleep-time compute uses overnight idle cycles when the GPUs would otherwise sit empty.

### Story 4: The Wiki That Writes Itself

Taylor started a wiki project three months ago — a Karpathy-style knowledge base for their team's platform architecture. They wrote 5 pages and got busy. The wiki stagnated.

With the auto-compiling dream agent, the wiki doesn't stagnate. Taylor's daily sessions generate observations: decisions about the event sourcing migration, patterns in the new message broker, errors from the CI pipeline. The ClawMem decision-extractor hook captures these automatically.

During idle cycles, the dream agent processes the intake queue. It reads each new ClawMem document via REST API, parses the YAML frontmatter, categorizes the content, and extracts key claims. Then it cross-references existing wiki pages — does this contradict or extend the "Event Sourcing" page? Confidence scoring gates the output: high-confidence claims auto-compile into wiki pages, medium-confidence gets flagged for Taylor's review, low-confidence is rejected.

Every wiki page carries full provenance. The `sources` field links back to the original ClawMem doc IDs. The `confidence` field reflects the deliberative refinement score (weighing self-consistency, source freshness, cross-reference agreement, and evidence count). When there's contradictory information — two sessions taking different positions on the same question — both sides are preserved with dates and confidence scores.

Taylor returns three months later and finds 47 well-structured wiki pages, each with cross-references, provenance chains, and quality scores. The wiki grew itself.

### Story 5: Provenance Deep-Dive From Cold Storage

Jordan is investigating a production incident. The error traces back to a decision made 8 months ago about the database migration strategy. Jordan searches the wiki but the relevant page only says "see archived context."

Before the metadata pipeline, cold storage was a black hole. Jordan would find the archived MemVid entry but have no idea where it came from, what confidence score it carried, or whether it was superseded by a later decision.

With the provenance chain intact, every cold-stored memory is reverse-linkable. Jordan finds the MemVid hit at 4096-dimensional resolution. A single SQL join through `memvid_indices → chunks.metadata_json` reveals the full story:

```
metadata_json.provenance.source_uri = "clawmem://docid/a1b2c3"
metadata_json.identity.content_hash = "sha256:..."
metadata_json.quality.confidence_score = 0.72
metadata_json.semantic.entities = ["database-migration", "event-sourcing", "postgres"]
metadata_json.graph.incoming_references = [
  "wiki://pages/concepts/migration-strategy.md",
  "clawmem://docid/d4e5f6/pinned"
]
```

The pinned reference leads to a later wiki page that supersedes the old decision. Jordan has the complete lineage: original session → ClawMem entry → wiki page → cold archive → superseding decision. The incident is resolved in 20 minutes instead of 2 hours.

### Story 6: The Quality Flywheel

Nina manages a team of 4 engineers. She's responsible for the platform's architecture documentation — but nobody has time to write docs, and the docs that exist are stale.

The vault improvement engine changes the incentives. Every document in the vault is scored against S-tier references. The scores are visible in the morning report. Nina's team can see their docs improving week over week — a quality flywheel.

Month 1: Raw architecture notes score 22/100. The engine adds structure: abstract, context, decision, consequences (22→45).
Month 2: Cross-references to related ADRs are populated (45→61).
Month 3: Risk identification and dependency mapping are filled in (61→78).
Month 4: Clarity improvements from rubrics (78→89). Flagged as "near optimal."

The morning report: "Your migration ADR reached 89/100. One gap remaining: execution readiness score (0.6/1.0). Suggested: add a rollback plan section before the timeline."

Nina's team collectively adds the rollback plan. Score hits 94. The engine flags it for proactive execution — but the migration is already in progress. The well-structured ADR becomes the reference document for next quarter's similar migration.

Over 6 months, the vault's average quality score rises from 34 to 71. The lowest-scoring document is 52 (up from 11). Documentation quality is no longer a function of who had time to write it — it's a property of the system.

## 3. Glossary

| Term | Definition |
|------|-----------|
| **Karpathy Wiki** | Human-readable compiled knowledge base at `~/ai-wiki/`. Three-layer structure: `raw/` (immutable sources), `pages/` (compiled markdown with YAML frontmatter), `AGENTS_WIKI.md` (schema/conventions). |
| **ClawMem** | Hot/Warm memory tier. SQLite-based hybrid memory system with FTS5, vector search, cross-encoder reranking, graph traversal, and lifecycle hooks. yoloshii/ClawMem v0.10.1, TypeScript on Bun. |
| **MemVid V2** | Cold memory tier. Single-file `.mv2` format with HNSW vector index, BM25 search, and WAL. Multi-resolution: 256/768/1568/2064/4096 dimensions. ~90% compression via video codec. |
| **Dream Agent** | Python sidecar running on systemd idle timer. Reads ClawMem vault via REST API, compiles wiki pages, performs vault improvement. Talks to ClawMem over HTTP, never directly to SQLite. |
| **Tier Transition** | Hot→Warm→Cold lifecycle: ClawMem entries aged 24h+ move to archive, decisions/patterns/errors get promoted to wiki pages (warm), 30-day stale nodes serialize to MemVid (cold). |
| **Provenance Chain** | Cross-layer metadata linkage: ClawMem entry_id → wiki page `sources[]` → MemVid frame → `memvid_indices → chunks.metadata_json`. Every layer round-trips to full metadata. |
| **Intent Router** | Classifies query intent (recent, relational, archival, factual, ambiguous) to select memory tiers. Two-tier pipeline: heuristic regex (0ms, covers ~70%) + LLM refinement (for the ~30% ambiguous). |
| **Deliberative Refinement** | Multi-factor confidence scoring for wiki compilation: 35% self-consistency + 25% source freshness + 25% cross-ref agreement + 15% evidence count. Council escalation for borderline contradictory claims. |
| **Sleep-Time Compute** | Background quality improvement engine. Uses embedding vector distance as loss function between vault document and S-tier reference. Iterative LLM rewriting with meaning preservation gate. |
| **S-Tier Reference** | Curated exemplar document for a content type (project plan, research note, tutorial, etc.). Lives at `wiki/.meta/references/`. Sourced from permissive-license works or user-provided. |
| **FORGE Methodology** | Feedback-Orchestrated Refinement with Grounded Evaluation. Profiles: Lite V(3,1,0), Standard V(8,3,1), Deep V(12,5,2), Exhaustive V(15,5,3). Mapped to improvement profiles. |
| **Fractal Synthesis Protocol (FSP)** | Methodology treating vault as "shared RAM" for LLM-human collaboration. 7 pillars: Amnestic Compensation, Multi-Temporal Perspective, Fractal Branching, Adversarial Council Validation, Self-Referential Improvement, etc. |
| **Token Budget** | Maximum tokens the memory router may inject as context. Configurable per invocation. Default: 2000 tokens. |
| **Echo Loop** | Anti-pattern where injected memory context is re-captured as new content and re-stored, creating infinite self-referential growth. Mitigated by sentinel markers stripped during sanitization. |

## 4. Functional Requirements

### 4.1 Memory Routing & Retrieval

| ID | Requirement |
|----|------------|
| FR-ROUTE-001 | The system SHALL support three retrieval strategies selectable at runtime: score_fusion (parallel all tiers with weighted fusion), cascade (sequential escalation with early-exit), intent_routed (classify then route with automatic fallback on low confidence). |
| FR-ROUTE-002 | The active strategy SHALL be determined by precedence: hook argument > override file > environment variable > config file > hardcoded default (`intent_routed` with `score_fusion` fallback). |
| FR-ROUTE-003 | The intent classifier SHALL support two backends: heuristic regex (built-in, 0ms, covers ~70% of queries) and LLM refinement (for ~30% ambiguous queries, using hardware-adaptive model selection). |
| FR-ROUTE-004 | Intent classification SHALL map to tier routing: "recent" → ClawMem only; "relational/why" → ClawMem + graph; "entity" → ClawMem + graph; "historical/archival" → ClawMem + MemVid; "ambiguous" → all tiers (fallback to score_fusion). |
| FR-ROUTE-005 | ClawMem SHALL always be queried regardless of strategy — its sub-millisecond latency makes it zero-cost to include. |
| FR-ROUTE-006 | Score fusion SHALL use: `score = (semantic_relevance × 0.6) + (recency × 0.25) + (importance × 0.15)`. Weights SHALL be configurable. |
| FR-ROUTE-007 | Cascade strategy SHALL define configurable confidence thresholds per tier: hot ≥ 0.8 (stop), warm ≥ 0.7 (escalation), cold (final escalation). |
| FR-ROUTE-008 | Token budget SHALL be enforced via greedy selection by fused score, with truncation at sentence boundaries for partial results. |
| FR-ROUTE-009 | Graphiti (future) or ClawMem-graph queries SHALL support multi-group queries across domain boundaries. |
| FR-ROUTE-010 | Intent classifications SHALL be cached per session. Reuse cached classification when new prompt embedding cosine similarity > 0.95 with a cached entry. |
| FR-ROUTE-011 (Anticipatory Prefetch) | During async hooks, a background process SHALL analyze the last 6 conversation turns, predict 3-5 likely follow-up topics, and pre-query relevant tiers into a session-local cache. |

### 4.2 Dream Agent & Wiki Compilation

| ID | Requirement |
|----|------------|
| FR-DREAM-001 | The dream agent SHALL run as a Python sidecar triggered by systemd idle timer (30-minute check, 5-minute idle threshold). |
| FR-DREAM-002 | Budget SHALL be calculated as `idle_seconds × 0.25`, capped at 7200 seconds (2 hours) per cycle. |
| FR-DREAM-003 | The dream cycle SHALL have 5 phases: Budget Allocation, Extract, Refine, Compile, Pattern Detect, Re-index. |
| FR-DREAM-004 | Intake-to-refinement ratio SHALL shift dynamically based on wiki refinement state: 80/20 at raw, 50/50 at mid, 33/67 at mature. |
| FR-DREAM-005 | The agent SHALL read ClawMem vault via REST API only (GET /documents/:docid, POST /search, etc.) — never direct SQLite access. |
| FR-DREAM-006 | The agent SHALL write compiled wiki pages to `pages/` with full YAML frontmatter: title, created/updated dates, tags, confidence, status, sources (clawmem://docid/...), wikilinks, contradictions, entity_types. |
| FR-DREAM-007 | Confidence scoring SHALL use deliberative refinement: 35% self-consistency + 25% source freshness + 25% cross-ref agreement + 15% evidence count. Thresholds: >0.8 auto-add, 0.5-0.8 flag for review, <0.5 reject. |
| FR-DREAM-008 | Council escalation SHALL trigger when confidence ∈ [0.5, 0.6] AND the claim contradicts existing high-confidence content. Two-model adversarial deliberation (primary + secondary LLM) with consensus output. |
| FR-DREAM-009 | Pattern detection SHALL scan ClawMem observations for 3+ similar task completions. On detection, distill procedure into a SKILL.md in the skills directory. |

### 4.3 Vault Improvement (Sleep-Time Compute)

| ID | Requirement |
|----|------------|
| FR-IMPROVE-001 | The improvement engine SHALL classify vault documents into types: project plan/PRD, research note, instruction/tutorial, code, narrative/writing, raw transcript (extract only), configuration, frontmatter-only (metadata enrich). |
| FR-IMPROVE-002 | Improvement SHALL use embedding vector distance as loss function: `loss = cosine_distance(embed(vault_doc), embed(reference))`. |
| FR-IMPROVE-003 | A rubric-based gap analysis SHALL run alongside embedding distance for interpretable improvement suggestions. Each document type has a weighted rubric (completeness, clarity, timeline_realism, dependency_mapping, risk_identification, execution_ready). |
| FR-IMPROVE-004 | Each improvement SHALL be specific (not "improve clarity" but "add prerequisites section"), minimal (one section at a time), and traceable (git commit with descriptive message). |
| FR-IMPROVE-005 | Improvement SHALL be accepted only when `new_loss < old_loss AND cosine_sim(new_doc, old_doc) > 0.80` (meaning preservation gate). |
| FR-IMPROVE-006 | Maximum 10 iterations per document per cycle. Convergence threshold: improvement < 0.01 per iteration. |
| FR-IMPROVE-007 | Documents reaching score ≥ 90 MAY be flagged for proactive execution: project plans → build MVP, PRDs → implement feature, research notes → draft paper, tutorials → validate steps. |
| FR-IMPROVE-008 | S-tier references SHALL live at `wiki/.meta/references/` organized by type. At minimum: project-plan, research-note, tutorial, code, narrative. User-curated, not auto-generated. |
| FR-IMPROVE-009 | Backups of originals SHALL be preserved alongside improvements (-improved suffix). Operator approval required by default before replacing originals. |

### 4.4 Metadata & Provenance

| ID | Requirement |
|----|------------|
| FR-META-001 | Every wiki page SHALL have full YAML frontmatter: title, created, updated, tags, confidence, status (stable/draft/needs_review/stale), sources, wikilinks, contradictions, entity_types, expires. |
| FR-META-002 | The provenance chain SHALL be: ClawMem entry_id → wiki page sources[] → MemVid memvid_indices → chunks.metadata_json. Every link in the chain SHALL be traversable in both directions. |
| FR-META-003 | The memvid_indices join table SHALL map (memvid_file, frame_index) → chunk_id → full ChunkMetadata (provenance, identity, graph, quality, semantic, embedding). |
| FR-META-004 | No metadata SHALL be lost at any transition: session→ClawMem preserves all, ClawMem→wiki compresses conversation turns but preserves claims+confidence, wiki→ClawMem reindex round-trips through YAML, ClawMem→MemVid preserves all through SQL join. |
| FR-META-005 | The pipeline SHALL support the existing buttplug/memory schema for memvid_indices and chunks tables. |

### 4.5 Tier Integration & Backends

| ID | Requirement |
|----|------------|
| FR-TIER-001 | ClawMem SHALL be used as-is from npm (yoloshii/ClawMem v0.10.1). No fork, no modification. Integration via REST API (localhost:7438). |
| FR-TIER-002 | The existing buttplug memory ClawMem adapter (250-line SHA-256 stub) SHALL be deleted and replaced with a thin REST API wrapper. |
| FR-TIER-003 | Graphiti SHALL be skipped. ClawMem already has native entity-level time-travel via entity_triples with valid_from/valid_to, temporal graph edges, and recency scoring. |
| FR-TIER-004 | The dream agent SHALL NOT modify ClawMem's SQLite directly — all reads/writes through HTTP API. |
| FR-TIER-005 | MemVid encoding SHALL be monthly. The 30-day window between encodes gives the dream agent time to refine before cold archival. |
| FR-TIER-006 | Multi-resolution vector storage SHALL support 5 dimension tiers: 256, 768, 1568, 2064, 4096. |
| FR-TIER-007 | The memvid_indices table SHALL be populated AT ENCODE TIME — not as a separate pass. |

### 4.6 Scheduler & Operations

| ID | Requirement |
|----|------------|
| FR-SCHED-001 | Services SHALL start in order: clawmem serve → clawmem watch → clawmem-embed.timer → bootstrap ClawMem collections → dream agent scheduler (systemd idle timer) → MemVid cron (monthly). |
| FR-SCHED-002 | Budget allocation across dream agent phases SHALL be: 33% intake, 33% compilation, 33% improvement, 1% lint/health. |
| FR-SCHED-003 | The improvement phase SHALL target lowest-scoring documents first. |
| FR-SCHED-004 | Nightly integrity check SHALL verify all `.mv2` files via MemVid V2 WAL recovery. |
| FR-SCHED-005 | Structured JSON logging to configurable directory with 50MB rotation, 5 file retention. |

## 5. Non-Functional Requirements

### 5.1 Latency

| Operation | Target |
|-----------|--------|
| UserPromptSubmit hook total | < 300ms |
| ClawMem query (FTS5 + vector) | < 50ms |
| MemVid query (per .mv2 file) | < 50ms |
| Intent classifier (heuristic) | < 5ms |
| Intent classifier (LLM, ~30% queries) | < 200ms |
| Score fusion + assembly | < 50ms |
| Prefetch cache hit | < 5ms |
| Dream agent budget check | < 1s |
| ClawMem REST API round-trip | < 100ms |

### 5.2 Reliability

| ID | Requirement |
|----|------------|
| NFR-REL-001 | All ClawMem writes SHALL be atomic (SQLite transaction or atomic POSIX rename). |
| NFR-REL-002 | Dream agent failures SHALL NOT corrupt the wiki. Wiki writes are git-committed. Partial writes roll back on failure. |
| NFR-REL-003 | Dead letter queue for failed Graphiti (future) or improvement operations. No silent drops. |
| NFR-REL-004 | Nightly `.mv2` integrity check via MemVid V2 WAL recovery. |
| NFR-REL-005 | LLM classifier / improvement LLM unavailability SHALL degrade gracefully to rules/heuristics within 2 seconds. |
| NFR-REL-006 | All external API calls SHALL have configurable timeouts with fallback behavior on failure. |

### 5.3 Concurrency

| ID | Requirement |
|----|------------|
| NFR-CONC-001 | ClawMem SQLite WAL mode for safe concurrent reads. Writes serialized by SQLite internal locking. |
| NFR-CONC-002 | MemVid `.mv2` writes SHALL hold exclusive lock during archival. |
| NFR-CONC-003 | Dream agent wiki writes SHALL be serialized — no concurrent dream cycles. |

### 5.4 Security

| ID | Requirement |
|----|------------|
| NFR-SEC-001 | Wiki content SHALL be version-controlled in git. Full history of every improvement. |
| NFR-SEC-002 | S-tier references SHALL only come from permissive-license works or user-provided content. No unlicensed copyrighted material. |
| NFR-SEC-003 | ClawMem REST API access SHOULD be localhost-only by default. API key optional for network-exposed deployments. |

## 6. Acceptance Criteria

| ID | Test | Passes When |
|----|------|------------|
| AC-01 | Intent routing accuracy | "the error I just got" → ClawMem only; "why that architecture choice" → ClawMem + graph; "last year's design" → ClawMem + MemVid |
| AC-02 | Strategy override chain | Hook arg > env var > config > default; expiry respected |
| AC-03 | Token budget enforcement | Router returns ≤ budget tokens, truncated at sentence boundaries |
| AC-04 | Dream agent compilation | 50 ClawMem docs → wiki pages with full YAML frontmatter and provenance links |
| AC-05 | Confidence scoring | Known-true claim scores > 0.8; known-contradictory scores < 0.5 |
| AC-06 | Council escalation | Contradictory claim with 0.55 confidence triggers 2-model deliberation |
| AC-07 | Improvement convergence | 10 iterations on a low-scoring doc shows measurable embedding distance reduction |
| AC-08 | Meaning preservation gate | Improvement that changes semantics > 20% is rejected |
| AC-09 | Provenance round-trip | Cold-stored memory → join → full ChunkMetadata with source_uri, confidence, entities |
| AC-10 | Echo loop prevention | Injected context from turn N absent from ClawMem on turn N+1 |
| AC-11 | Sleep-time safety | Original preserved alongside improvement; operator approval required by default |
| AC-12 | Git traceability | Every improvement committed with descriptive message; full version history |
| AC-13 | Startup sequence | clawmem serve → watch → embed → collections → dream scheduler → MemVid cron (all green) |
| AC-14 | Pattern detection → skill | 3+ similar task observations produce a SKILL.md in skills/ |

## 7. Constraints & Out of Scope

### In Scope
- Memory routing with 3 strategies and 2-tier intent classification
- Dream agent: ClawMem REST → wiki compilation → pattern detection → skill creation
- Vault improvement: embedding-guided iterative rewriting with rubric gap analysis
- Metadata pipeline: YAML frontmatter → SQLite → memvid_indices join → full provenance chain
- Tier integration: ClawMem as hot/warm, MemVid as cold, dream agent as orchestrator
- Scheduler: systemd timers for dream cycles, monthly MemVid encode, nightly integrity

### Out of Scope
- Training or fine-tuning any model (improvement uses frozen inference APIs)
- Modifying or forking ClawMem, MemVid, or any backend
- Building a custom proxy or API shim (ClawMem hooks handle interception)
- Implementing adversarial quality gates, multi-agent memory validation
- Graphiti integration (ClawMem covers time-travel natively)
- Custom model deployment (uses existing ClawMem llama-server or cloud APIs)
- Hardware cluster management (Switchboard integration is downstream)

## 8. References

1. ARCHITECTURE.md v4.1.0 — Unified Memory Architecture including FSP methodology
2. DREAM_AGENT_V2.md v2.0.0 — Dream agent phases, budget, confidence scoring
3. METADATA_PIPELINE.md v1.1.0 — YAML schema, SQLite columns, memvid_indices join chain
4. TIER_INTEGRATION.md v1.0.0 — Component dependencies, ClawMem adapter rewrite plan, startup order
5. VAULT_IMPROVEMENT.md v1.0.0 — Sleep-time improvement engine, FORGE methodology, S-tier references
6. buttplug memory design.md v3.1.0 — aaa-memory router, ingestion, tri-strategy, adapter specs
7. buttplug memory requirements.md v3.1.0 — FR/NFR, risks, acceptance criteria
8. buttplug memory masterplan.md — System integration map, phased implementation plan
9. Fractal Synthesis Protocol — User's Obsidian vault `old vault/Fractal Synthesis Protocol...md`
10. FORGE methodology — `old vault/ChetasVault PRD appendix I YAML.md`
11. yoloshii/ClawMem v0.10.1 — github.com/yoloshii/ClawMem
12. MemVid V2 — github.com/memvid/memvid
