---
date: 2026-05-19
ver: 4.1.0
tags: [karpathy-wiki, architecture, clawmem, memvid, sleep-time, tri-tier]
---

> **Methodology:** This system implements the **Fractal Synthesis Protocol (FSP)**
> (see user's Obsidian vault: `old vault/Fractal Synthesis Protocol...md`), treating
> the vault as "shared RAM" for LLM-human collaboration. The seven FSP pillars
> map to: Amnestic Compensation → ClawMem persistence, Multi-Temporal Perspective →
> MemVid cold storage tiers, Fractal Branching → parallel dream agents,
> Adversarial Council Validation → deliberative refinement,
> Self-Referential Improvement → vault improvement engine.

# Unified Memory Architecture v4.0

## Stack (Hottest → Coldest)

```
┌──────────────────────────────────────────────────────────────┐
│                    KARPATHY WIKI (Hottest)                    │
│  Path: /home/cheta/code/karpathy-wiki/wiki/pages/            │
│  Format: YAML frontmatter + markdown + [[wikilinks]]          │
│  Purpose: Human-readable compiled knowledge                   │
│  Owner: Dream agent writes, human reads/edits                  │
│  Decay: None — permanent, human-curated                      │
│  Metadata: Full YAML (provenance, confidence, tags, sources)  │
├──────────────────────────────────────────────────────────────┤
│                    CLAWMEM (Hot/Warm)                         │
│  Path: ~/.cache/clawmem/index.sqlite                          │
│  Project: yoloshii/ClawMem v0.10.1 (npm install -g clawmem)   │
│  Format: SQLite + FTS5 + sqlite-vec + memory_relations        │
│  Purpose: Hybrid search, session memory, graph traversal       │
│  Owner: Hooks + MCP tools + consolidation worker              │
│  Decay: Content-type half-lives (30d handoff to ∞ decision)    │
│  Metadata: YAML frontmatter → SQLite columns + JSON blobs     │
│  Features: BM25, vector search, cross-encoder reranking,       │
│            intent classification, graph traversal (semantic,   │
│            temporal, causal), A-MEM evolution, contradiction   │
│            detection, feedback loops, pin/snooze lifecycle     │
├──────────────────────────────────────────────────────────────┤
│                    MEMVID V2 (Cold)                            │
│  Format: .mv2 files (QR-coded vectors → MP4 compression)      │
│  Purpose: Compressed archival with multi-resolution search     │
│  Schedule: Monthly/90-day full re-encode                       │
│  Resolution tiers: 256, 768, 1568, 2064, 4096 dims            │
│  Compression: ~90% via video codec                             │
│  Metadata: Embedded index + origin_id pointers                 │
└──────────────────────────────────────────────────────────────┘
```

## Data Flow

```
Session Hook → ClawMem vault (live memory)
                    │
                    ▼
          ┌──────────────────┐
          │  Dream Agent     │  ← systemd idle timer
          │  (Python sidecar)│     budget = idle × 0.25
          └────────┬─────────┘
                   │ 1. Reads ClawMem vault via REST API (localhost:7438)
                   │ 2. Extracts observations, compiles wiki pages
                   │ 3. Scores confidence via deliberative refinement
                   │ 4. Detects patterns → creates skills
                   │ 5. Writes wiki pages to pages/
                   │ 6. Writes skills to skills/
                   │ 7. Re-indexes wiki dir into ClawMem collection
                   │
                   ▼
          ┌──────────────────┐
          │  Karpathy Wiki   │  ← human-readable, permanent
          │  pages/          │
          └────────┬─────────┘
                   │ (monthly/90d batch)
                   ▼
          ┌──────────────────┐
          │  MemVid V2       │  ← compressed archival
          │  .mv2 files      │     multi-resolution search
          └──────────────────┘
```

## Metadata Pipeline

All three layers preserve full provenance through SQLite join tables.
Metadata never goes opaque.

### The Join Chain

```
MemVid frame (.mv2 + frame_index)
    │
    ▼
memvid_indices table (SQLite, in buttplug's schema)
    │  memvid_file TEXT, frame_index INT, chunk_id TEXT
    ▼
chunks table (SQLite, same database)
    │  chunk_id TEXT PRIMARY KEY, metadata_json TEXT (full ChunkMetadata)
    │
    ├──► metadata_json.confidence, metadata_json.provenance
    ├──► metadata_json.semantic.keywords, entities
    ├──► metadata_json.graph.incoming_references
    └──► metadata_json.quality.validation_status
```

Every vector in MemVid is reverse-linkable to its full ChunkMetadata
via `memvid_indices → chunks` join. The ChunkMetadata contains provenance
chains back to ClawMem documents and wiki pages.

### Layer Summary

| Layer | Storage | Query Method | Provenance Retrieval |
|-------|---------|-------------|---------------------|
| Wiki | YAML frontmatter in .md | grep, editor | Direct |
| ClawMem | SQLite columns + JSON | SQL, MCP, REST | Direct |
| MemVid | .mv2 binary | MemVid SDK | SQL join: memvid_indices → chunks.metadata_json |

### Cross-Layer Provenance

Every wiki page has `sources: [clawmem://docid/abc123]` in its frontmatter.
Every ClawMem document has `origin: wiki://pages/concepts/foo.md` in its metadata.
Every MemVid frame maps through `memvid_indices` to a `chunks` row with full ChunkMetadata.
No circular dependencies.

## Intent Router — Model Selection by Hardware

The intent classifier decides whether a query hits ClawMem only (fast path) or
ClawMem + MemVid (historical/archival). It uses ClawMem's existing two-tier
pipeline (heuristic regex + LLM refinement) with an extended taxonomy.

### Taxonomy

| Intent Signal | Route | Example |
|---------------|-------|---------|
| Recent/recency | ClawMem only | "the error I just got", "this session" |
| Causal/why | ClawMem + graph | "why did we decide X" |
| Entity | ClawMem + graph | "what does X relate to" |
| **Historical (NEW)** | **ClawMem + MemVid** | "last year's architecture", "the old project" |
| Ambiguous | Fallback to max recall | All tiers |

### Pipeline

```
[0ms] Heuristic regex classifier
    │
    ├── Strong signal (e.g. "2024", "last year", "archive") → historical → MemVid
    ├── Strong signal (e.g. "just now", "this session") → recent → ClawMem only
    │
    └── Ambiguous (no match or low confidence)
            │
            ▼
    LLM refinement (model selected by hardware)
            │
            ├── "historical" intent → ClawMem + MemVid in parallel
            └── everything else → ClawMem ± graph
```

### Model Options (selectable by hardware profile)

ClawMem already bundles the heuristic regex (0ms, covers ~70%) and the 1.7B QMD
model (27ms on GPU). The intent taxonomy extension only adds a handful of regex
patterns for historical keywords — zero new model cost for the fast path.

For the LLM refinement stage (ambiguous queries, ~30% of prompts), the optimal
model depends on available hardware. Fine-tuning any of these for 4-class
intent classification is trivial — a few hundred examples, one epoch, standard
LoRA or full fine-tune.

| Model | Params | Released | Hardware | Latency | License | Notes |
|-------|--------|----------|----------|---------|---------|-------|
| **Heuristic regex** | 0 | Built-in | CPU | 0ms | MIT | Default, covers 70% |
| **LittleLamb 0.3B Tool-Calling** | 0.3B | Apr 29, 2026 | CPU/GPU | ~50ms CPU | Apache 2.0 | **Best pick.** Compressed from Qwen3-0.6B. Tuned for structured JSON. English + Spanish. |
| **Granite 4.0 Nano 350M** | 0.35B | Oct 2025 | CPU/GPU | ~80ms CPU | Apache 2.0 | IBM's smallest. Strong structured output. English. |
| **SmolLM2 360M** | 0.36B | Feb 2025 | CPU/GPU | ~80ms CPU | Apache 2.0 | Hugging Face, SOTA for size. Well-documented fine-tuning. |
| **Qwen3.5 0.8B** | 0.8B | Apr 24, 2026 | CPU/GPU | ~120ms CPU | Apache 2.0 | Very recent. Likely strong classifier. |
| **SmolLM2 1.7B** | 1.7B | Feb 2025 | GPU pref'd | 27ms GPU / ~250ms CPU | Apache 2.0 | What ClawMem already bundles. Falls back to CPU. |
| **ClawMem QMD 1.7B** | 1.7B | Bundled | GPU pref'd | 27ms GPU / ~200ms CPU | MIT | Already installed with ClawMem. Default LLM refinement. |

**Recommendation:** Ship with two defaults:
- **GPU available:** Use ClawMem's bundled 1.7B QMD model (already there, 27ms).
- **CPU only:** Drop in LittleLamb 0.3B Tool-Calling (50ms, Apache 2.0, designed for structured output).

Both only fire on the ~30% of queries that the heuristic regex can't classify at
0.8+ confidence. The effective latency add is <15ms on GPU or <15ms on CPU
(for 30% of queries at 50ms).

### Fine-tuning Note

All models above can be fine-tuned for intent classification with minimal effort:
- Dataset: ~200-500 labelled queries (synthetic or real)
- Method: LoRA or full fine-tune
- Time: <1 hour on a single GPU, <4 hours on CPU
- Tools: Unsloth, Hugging Face TRL, or standard transformers

## Key Design Decisions

### DD1: Replace custom SQLite adapter with yoloshii/ClawMem
- **Why**: The existing adapter is a hallucinated 250-line stub with SHA-256 "embeddings."
  The real ClawMem (170 stars, MIT, active) has hybrid search, hooks, MCP, lifecycle,
  contradiction detection, and graph traversal — all free.
- **Integration**: Dream agent talks to ClawMem via REST API (localhost:7438).
  ClawMem indexes the wiki pages/ directory as a collection.
- **No fork needed**: ClawMem is never modified. It's used as-is from npm.

### DD2: Skip Graphiti (temporal knowledge graph)
- **Why**: KuzuDB was archived Oct 2025 (Apple acquisition). LadybugDB is unproven.
  ClawMem ALREADY has entity-level time-travel via `entity_triples` with
  `valid_from`/`valid_to` and `kg_query(entity, as_of?)` for point-in-time
  SPO lookups. Combined with temporal graph edges, timeline tool, and recency
  scoring, ClawMem covers everything Graphiti was needed for.
- **Cost**: None — ClawMem ships this feature natively.

### DD3: Dream agent as Python sidecar, not ClawMem plugin
- **Why**: Dream agent needs systemd idle timer, percentage budgets, council calls,
  and wiki file I/O. These don't map to ClawMem's hook lifecycle.
- **Integration**: REST API calls to ClawMem serve (localhost:7438).
  Webhook from ClawMem on new content to trigger dream cycles.

### DD4: Monthly MemVid re-encode creates natural refinement window
- **Why**: The monthly encoding cadence means the dream agent has up to 30 days
  to refine memories before they become cold. This is a feature.
- **Multi-resolution**: 5 dimension tiers × 90% compression = feasible storage.
  The extra dimensions enable word/sentence/paragraph/document-level search.

## Potential Issues

1. **Dream agent ↔ ClawMem consolidation overlap**: ClawMem already has Phase 2/3
   consolidation (dedup, contradiction detection, deductive synthesis). The dream
   agent's wiki compilation is higher-level (cross-page synthesis, skill creation).
   Keep them separate: ClawMem handles SQLite-level consolidation; dream agent
   handles wiki-level compilation.

2. **Multi-resolution vector storage**: 5× dimension count × 10% post-compression
   = ~50% of uncompressed single-resolution storage. Acceptable tradeoff for
   multi-granularity search.

3. **ClawMem requires Bun**: yoloshii/ClawMem is TypeScript on Bun. This is an
   additional runtime dependency alongside Python (dream agent) and whatever MemVid needs.

4. **memvid_indices table must be populated at encode time**: The join chain
   from MemVid frames back to ClawMem metadata only works if the mapping table
   is populated during the encoding pass. If the encoding script doesn't write
   to the shared SQLite database, the provenance chain breaks. Must be part
   of the encode pipeline.
