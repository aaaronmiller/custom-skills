---
date: 2026-05-20
ver: 1.0.0
author: synthesis of ARCHITECTURE.md v4.1.0, DREAM_AGENT_V2.md v2.0.0, METADATA_PIPELINE.md v1.1.0, TIER_INTEGRATION.md v1.0.0, VAULT_IMPROVEMENT.md v1.0.0, buttplug memory design.md v3.1.0, buttplug requirements.md v3.1.0, buttplug masterplan.md
tags: [karpathy-wiki, design, architecture, dream-agent, sleep-time, clawmem, memvid, tri-tier, metadata]
---

# Karpathy Wiki — Technical Design v1.0

## 1. Architecture Overview

The Karpathy Wiki is a three-tier memory system with an autonomous compilation and improvement layer. It combines off-the-shelf backends with a custom orchestration layer to transform raw session data into a permanent, self-improving knowledge base.

### 1.1 Tier Stack (Hottest → Coldest)

```
┌─────────────────────────────────────────────────────────────────────┐
│                   KARPATHY WIKI (L1 — Permanent)                     │
│  Path: ~/ai-wiki/pages/                                              │
│  Format: YAML frontmatter + markdown + [[wikilinks]]                  │
│  Purpose: Human-readable compiled knowledge                          │
│  Owner: Dream agent writes, human reads/edits                         │
│  Decay: None — permanent, human-curated with git history             │
│  Metadata: Full YAML (provenance, confidence, tags, sources)          │
│  Git: All changes committed with descriptive messages                │
├─────────────────────────────────────────────────────────────────────┤
│                  CLAWMEM (L2 — Hot/Warm)                              │
│  Path: ~/.cache/clawmem/index.sqlite                                  │
│  Project: yoloshii/ClawMem v0.10.1 (npm install -g clawmem)           │
│  Runtime: Bun + TypeScript                                            │
│  Format: SQLite + FTS5 + sqlite-vec + memory_relations                │
│  Purpose: Hybrid search, session memory, graph traversal               │
│  Owner: Hooks + MCP tools + consolidation worker                      │
│  Decay: Content-type half-lives (30d handoff to ∞ decision)           │
│  Features: BM25, vector search, cross-encoder reranking,              │
│            intent classification, graph traversal (semantic,          │
│            temporal, causal), A-MEM evolution, contradiction          │
│            detection, feedback loops, pin/snooze lifecycle            │
│  Access: REST API at localhost:7438                                   │
|  Embedding: llama-server at :8088 or cloud (Jina v5)                 │
├─────────────────────────────────────────────────────────────────────┤
│                   MEMVID V2 (L3 — Cold)                               │
│  Format: .mv2 files (QR-coded vectors → MP4 compression)              │
│  Purpose: Compressed archival with multi-resolution search            │
│  Schedule: Monthly/90-day full re-encode                              │
│  Resolution tiers: 256, 768, 1568, 2064, 4096 dims                   │
│  Compression: ~90% via video codec                                    │
│  Access: memvid_sdk Python bindings                                   │
│  Metadata: Embedding index + memvid_indices SQLite join table         │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.2 System Architecture

```
                           ┌──────────────────────┐
                           │    Claude Code /      │
                           │    Hermes Agent       │
                           │    Sessions           │
                           └─────┬────────────────┘
                                 │ lifecycle hooks
                                 ▼
┌────────────────────────────────────────────────────────────────┐
│                     CLAWMEM (REST API :7438)                   │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐  ┌──────────────┐  │
│  │ search   │  │ retrieve │  │ vsearch   │  │ intent_search│  │
│  └──────────┘  └──────────┘  └───────────┘  └──────────────┘  │
│  ┌──────────┐  ┌──────────┐  ┌─────────────┐  ┌────────────┐  │
│  │ graph    │  │ lifecycle│  │ hcapsule    │  │ consolidate│  │
│  └──────────┘  └──────────┘  └─────────────┘  └────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ SQLite: FTS5 + sqlite-vec + memory_relations + metadata  │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
         │                          ▲
         │ REST API                 │ REST API
         ▼                          │
┌────────────────────────────────────────────────────────────────┐
│                    DREAM AGENT (Python sidecar)                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────────────┐  │
│  │ Phase 1  │  │ Phase 2  │  │ Phase 3  │  │ Phase 4       │  │
│  │ Extract  │→ │ Refine   │→ │ Compile  │→ │ Pattern Detect│  │
│  └──────────┘  └──────────┘  └──────────┘  └───────┬───────┘  │
│                                                     │          │
│  ┌──────────────────────────────────────────────┐   │          │
│  │ Phase 5: Re-index (POST /reindex to ClawMem)  │◄──┘          │
│  └──────────────────────────────────────────────┘              │
│  ┌────────────────────────────────────────────────────────────┐│
│  │ Phase 6: Improve (Sleep-time vault improvement engine)     ││
│  └────────────────────────────────────────────────────────────┘│
└────────────────────────────────────────────────────────────────┘
         │
         │ writes .md files
         ▼
┌────────────────────────────────────────────────────────────────┐
│                  KARPATHY WIKI (git-backed)                     │
│  ~/ai-wiki/pages/     ~/ai-wiki/raw/      ~/ai-wiki/skills/    │
│  ┌────────────┐      ┌────────────┐      ┌─────────────┐      │
│  │ compiled   │      │ immutable  │      │ auto-created│      │
│  │ wiki pages │      │ sources    │      │ skills      │      │
│  │ *.md       │      │ (drop here)│      │ SKILL.md    │      │
│  └────────────┘      └────────────┘      └─────────────┘      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ AGENTS_WIKI.md — schema, conventions, lint rules          │  │
│  │ .meta/references/ — S-tier reference exemplars            │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
         │ (monthly/90d batch)
         ▼
┌────────────────────────────────────────────────────────────────┐
│                    MEMVID V2 (Cold Archive)                     │
│  ~/.cache/memvid/<domain>.mv2 (per-domain archives)            │
│  Hybrid search: HNSW + BM25, multi-resolution                  │
│  Metadata linked via: memvid_indices → chunks → ChunkMetadata  │
└────────────────────────────────────────────────────────────────┘
```

### 1.3 Methodology: Fractal Synthesis Protocol (FSP)

The system implements the user's **Fractal Synthesis Protocol (FSP)** (see Obsidian vault: `old vault/Fractal Synthesis Protocol...md`). The seven FSP pillars map to system components:

| FSP Pillar | System Component |
|------------|-----------------|
| Amnestic Compensation | ClawMem hot tier persists session state across compactions |
| Multi-Temporal Perspective | MemVid cold storage + wiki provides permanent historical record |
| Fractal Branching | Parallel dream agents exploring different wiki improvements |
| Adversarial Council Validation | Two-model adversarial deliberation for contradictory claims |
| Self-Referential Improvement | Sleep-time compute engine iteratively improves vault content |
| (Additional pillars) | (Mapped to downstream systems) |

## 2. Component Specifications

### 2.1 Intent Router

The intent classifier decides which memory tiers to query. Two-tier pipeline: heuristic regex (fast path, covers ~70%) + LLM refinement (ambiguous remainder).

#### 2.1.1 Heuristic Tier (Built-in, 0ms)

```python
import re

INTENT_PATTERNS: list[tuple[re.Pattern, str]] = [
    # Historical / archival signal
    (re.compile(r"\b(202[0-5]|last year|old project|archive|months ago|way back|original design|historically)\b", re.I), "archival"),
    # Recent session signal
    (re.compile(r"\b(just now|this session|the error|latest|current|fresh|right now|just got)\b", re.I), "recent"),
    # Causal / relational
    (re.compile(r"\b(why did|how does .+ relate|pattern|architecture|decision|trade-?off|relationship)\b", re.I), "relational"),
    # Entity lookup
    (re.compile(r"\b(what is|show me|tell me about|what does .+ relate to)\b", re.I), "entity"),
    # Factual lookup
    (re.compile(r"\b(API for|config for|command to|syntax|parameter)\b", re.I), "factual"),
]

def classify_heuristic(prompt: str) -> tuple[str, float]:
    """Fast intent classification. Returns (intent, confidence) or (None, 0) if ambiguous."""
    scores: dict[str, int] = {}
    for pattern, intent in INTENT_PATTERNS:
        matches = pattern.findall(prompt)
        if matches:
            scores[intent] = scores.get(intent, 0) + len(matches)
    if not scores:
        return None, 0.0
    best = max(scores, key=scores.get)
    confidence = min(0.6 + (scores[best] - 1) * 0.2, 0.95)
    return best, confidence
```

#### 2.1.2 LLM Refinement Tier (For ~30% Ambiguous Queries)

When heuristic confidence < 0.8, the router escalates to LLM classification. Model selection depends on hardware:

| Model | Params | Hardware | Latency | Notes |
|-------|--------|----------|---------|-------|
| ClawMem QMD 1.7B | 1.7B | GPU | 27ms | Already bundled, default if GPU available |
| LittleLamb Tool-Calling | 0.3B | CPU | ~50ms | Apache 2.0, best CPU pick |
| Granite 4.0 Nano 350M | 0.35B | CPU | ~80ms | IBM's smallest, strong structured output |
| SmolLM2 360M | 0.36B | CPU | ~80ms | Hugging Face SOTA for size |
| Heuristic regex fallback | 0 | CPU | 0ms | Always available, covers 70% |

**Recommendation:** Ship with two defaults — ClawMem's bundled 1.7B QMD when GPU available, LittleLamb 0.3B Tool-Calling for CPU-only. Both only fire on ~30% of queries; effective latency add is <15ms on GPU or ~15ms on CPU (30% × 50ms).

#### 2.1.3 Intent-to-Tier Mapping

```python
INTENT_TIER_MAP = {
    "recent":     ["hot"],             # ClawMem only
    "entity":     ["hot", "graph"],    # ClawMem + graph traversal
    "relational": ["hot", "graph"],    # ClawMem + graph traversal
    "archival":   ["hot", "cold"],     # ClawMem + MemVid
    "factual":    ["hot", "warm"],     # ClawMem + Graphiti (future)
    None:         ["hot", "warm", "cold"],  # Fallback: all tiers (ambiguous)
}
```

#### 2.1.4 Strategy Resolution

Strategy is set per-invocation or per-session with this precedence chain:

```
1. Hook argument (orchestrator-controlled, per-invocation)
2. Strategy override file (~/.aaa-memory/run/strategy_override.json)
3. Environment variable (AAA_MEMORY_STRATEGY)
4. Configuration file (~/.aaa-memory/config/config.yaml)
5. Hardcoded default: intent_routed with score_fusion fallback
```

Supported strategies:

| Strategy | Behavior | Use Case |
|----------|----------|----------|
| `score_fusion` (A) | Query all tiers in parallel, weighted score fusion | Research, archival lookups |
| `cascade` (B) | Sequential tier escalation with early-exit | Latency-sensitive, CI tasks |
| `intent_routed` (C) | Classify then route; fallback to A on low confidence | Default for general use |

**Strategy override file** format (written by orchestrator agents):

```json
{
  "strategy": "cascade",
  "reason": "debugging_session",
  "set_by": "orchestrator_agent",
  "set_at": "2026-05-20T14:00:00Z",
  "expires_at": "2026-05-20T16:00:00Z"
}
```

#### 2.1.5 Token Budget Enforcement

```python
def assemble_context(results: list[MemoryResult], token_budget: int) -> str:
    """Greedily select top results within token budget, truncate at sentence boundary."""
    selected = []
    remaining = token_budget
    for r in sorted(results, key=lambda x: x.score, reverse=True):
        if r.token_count <= remaining:
            selected.append(r.text)
            remaining -= r.token_count
        elif remaining > 50:
            truncated = truncate_at_sentence(r.text, remaining)
            if truncated:
                selected.append(truncated)
                break
        else:
            break
    return "\n---\n".join(selected)
```

### 2.2 Dream Agent

The dream agent is a Python sidecar that compiles session observations into wiki pages during idle cycles.

#### 2.2.1 Trigger & Budget

```
systemd --user --idle timer (30min check)
    │
    ▼
idle-check.sh → Is pi/ante process running?
    │                 │
    │ (active)        │ (idle for 5+ min)
    ▼                 ▼
  Skip              Compute budget:
                    budget = idle_seconds × 0.25
                    cap at 7200s (2 hours)
                    │
                    ▼
                  Run dream cycle
```

#### 2.2.2 Dream Cycle Phases

**Phase 0: Budget Allocation**

Budget splits dynamically based on wiki refinement state:

```python
refinement_state = calc_refinement_state(wiki)
# 0.0 = raw wiki, 1.0 = maximally refined
intake_ratio = 0.80 - (0.50 × refinement_state)
intake_budget = total_budget × intake_ratio
refine_budget = total_budget × (1 - intake_ratio)

# At raw (0.0):  80% intake, 20% refinement
# At mid (0.5):  50% intake, 50% refinement
# At mature (0.94): 33% intake, 67% refinement
```

**Phase 1: Extract** (uses intake budget)
- Read ClawMem vault for new/updated documents since last cycle
- Fetch full content via REST API `GET /documents/:docid`
- Parse YAML frontmatter, categorize (decision, preference, problem, milestone, note, etc.)
- Extract key claims with source citations
- Store in intake queue

**Phase 2: Refine** (uses refine budget)
For each extracted claim:
1. Self-consistency check: Does the claim contradict itself?
2. Cross-reference check: Does it match/contradict/extend existing wiki pages?
3. Source freshness check: How recent is the source?
4. Confidence score (see §2.2.3)
5. Council escalation for borderline contradictory claims (see §2.2.4)
6. Apply threshold: >0.8 auto-add, 0.5-0.8 flag for review, <0.5 reject

**Phase 3: Compile**
- Find best existing wiki page or create new one
- Update page with new information; add/update [[wikilinks]]
- Add provenance to YAML frontmatter
- If contradictory: note both positions with dates and confidence scores

**Phase 4: Pattern Detect**
- Scan recent ClawMem observations for 3+ similar task completions
- Distill procedure into SKILL.md in skills directory
- Write reference into ClawMem vault for future retrieval

**Phase 5: Re-index**
- Trigger ClawMem reindex after all wiki page writes
- ClawMem auto-embeds new fragments on next embed timer cycle

#### 2.2.3 Confidence Scoring (Deliberative Refinement)

```python
confidence = (
    0.35 × self_consistency +   # Does LLM agree with its own extraction?
    0.25 × source_freshness +   # max(0, 1 - age_days / 365)
    0.25 × cross_ref_agreement + # Fraction of related pages that don't contradict
    0.15 × evidence_count_bonus  # min(1, count / 5)
)
```

#### 2.2.4 Council Escalation

Triggers when confidence ∈ [0.5, 0.6] AND claim contradicts existing high-confidence content.

Two-model adversarial deliberation:
1. Both models receive: claim, source text, existing wiki content
2. Judge A argues for accepting the claim
3. Judge B argues for rejecting it
4. Consensus output: accept, reject, or flag-for-user

#### 2.2.5 ClawMem REST API Integration

| Operation | Endpoint | Frequency |
|-----------|----------|-----------|
| List new docs | `GET /stats` (compare doc count) | Every cycle |
| Get doc content | `GET /documents/:docid` | Per new doc |
| Search for related pages | `POST /search` | Per claim |
| Get graph edges | `GET /graph/similar/:docid` | Per claim |
| Reindex after wiki writes | `POST /reindex` | End of cycle |
| Get session history | `GET /sessions` | Pattern detection |
| Get lifecycle status | `GET /lifecycle/status` | Health check |

### 2.3 Wiki Data Model

#### 2.3.1 Directory Structure

```
~/ai-wiki/
├── raw/                          # Immutable source documents (drop here)
├── pages/                        # Compiled wiki pages (dream agent writes)
│   ├── concepts/
│   │   ├── async-io.md
│   │   └── event-loop.md
│   ├── decisions/
│   │   └── auth-migration-adr.md
│   └── index.md                  # Auto-generated page index
├── skills/                       # Auto-created SKILL.md files
│   └── some-repeated-pattern/
│       └── SKILL.md
├── .meta/
│   ├── references/               # S-tier reference exemplars
│   │   ├── project-plan/
│   │   ├── research-note/
│   │   ├── tutorial/
│   │   ├── code/
│   │   └── narrative/
│   └── AGENTS_WIKI.md            # Schema, conventions, lint rules
└── log.md                        # Immutable append-only log of all operations
```

#### 2.3.2 Page Frontmatter Schema

Every wiki page MUST have this YAML frontmatter:

```yaml
---
title: "Concept Name"
created: 2026-05-19
updated: 2026-05-19
tags: [python, async, patterns]
confidence: 0.85                     # 0.0-1.0 from deliberative refinement
status: stable | draft | needs_review | stale
sources:
  - clawmem://docid/a1b2c3           # Provenance back to ClawMem
  - clawmem://docid/d4e5f6
wikilinks:                            # Explicit cross-refs
  - concepts/async-io.md
  - concepts/event-loop.md
contradictions:                       # If applicable
  - topic: "Best async pattern"
    position_a: "asyncio (source X, 2026-01)"
    position_b: "trio (source Y, 2026-03)"
    resolution: null                  # null = unresolved
entity_types: [concept, pattern]
expires: 2027-05-19                   # For staleness detection
---
```

#### 2.3.3 Naming Convention

- Lowercase-hyphens.md (`concurrent-processing.md`, never `Concurrent Processing.md`)
- One concept per file
- `[[page-name]]` cross-refs between pages

#### 2.3.4 Changelog

Every operation (compilation, improvement, edit) is recorded in:

**`log.md`** — Immutable append-only log:
```markdown
## 2026-05-20
- [add] concepts/event-loop.md — extracted from session abc123
- [improve] decisions/auth-migration-adr.md — added risk assessment (score 68→81)
- [pattern] skills/cicd-hook-pattern/SKILL.md — distilled from 4 observations
```

**Git history** — All wiki changes committed with descriptive messages:
```
improve: event-loop.md — added asyncio vs trio comparison (score 72→85)
compile: auth-migration-adr.md — from session abc123 (confidence 0.87)
create: skills/cicd-hook-pattern/SKILL.md — 4 observations, identical procedure
```

### 2.4 Vault Improvement Engine

The sleep-time compute engine improves existing vault documents using embedding-guided iterative rewriting.

#### 2.4.1 Document Classification

Two-tier classification (same as intent router):

1. **Heuristic rules** (instant): file path patterns, frontmatter tags, content markers
2. **LLM refinement** for ambiguous: using hardware-adaptive model

Types and quality dimensions:

| Type | Quality Dimensions | S-Tier Reference |
|------|-------------------|-----------------|
| Project Plan / PRD | completeness, clarity, timeline_realism, dependency_mapping, risk_identification, execution_ready | Stripe API design docs |
| Research Note | citation_quality, argument_structure, evidence_strength, reproducibility | Nobel-winning papers |
| Instruction / Tutorial | step_clarity, prerequisites, examples, troubleshooting, beginner_friendliness | Apple HIG, Divio docs |
| Code | readability, docs, error_handling, test_coverage, api_design | SQLite source, Redis |
| Narrative / Writing | structure, voice, pacing, evidence, hook, conclusion | Pulitzer features |
| Raw Transcript | — extracted only, not improved | N/A |
| Configuration | completeness, security, documented_overrides | Reference implementations |
| Frontmatter-Only | minimal metadata enrichment | N/A |

#### 2.4.2 Improvement Loop

```
Raw vault file (any type)
    │
    ▼
Phase 1: CLASSIFY (type + current quality score)
    │
    ▼
Phase 2: LOAD REFERENCE (S-tier example for type)
    │
    ▼
Phase 3: EMBED & MEASURE (both docs via ClawMem's embedding server)
    │  → cosine distance = loss metric
    │  → rubric scoring = interpretable gap analysis
    ▼
Phase 4: IMPROVE (generate targeted improvements from rubric gaps)
    │  → LLM rewrite to move embedding closer to reference
    ▼
Phase 5: RE-EMBED & CHECK
    │  → IF distance shrank AND meaning preserved (cosine_sim > 0.80):
    │       Accept improvement, git commit
    │  → ELSE: try different approach or skip
    ▼
Phase 6: ITERATE (max 10 iterations)
    │  → Repeat 3-5 until convergence (< 0.01 improvement/iteration)
    │  → Then move to next document (lowest-scoring first)
    ▼
Phase 7: FLAG FOR EXECUTION (if ≥ 90)
    │  → "Your project plan is ready. Build started."
```

#### 2.4.3 Loss Function

```python
def improvement_loss(vault_doc: str, reference: str) -> float:
    """Cosine distance as quality loss. 0 = identical, >0 = diverging."""
    vault_emb = embed(vault_doc)      # ClawMem embedding server
    ref_emb = embed(reference)
    cos_sim = np.dot(vault_emb, ref_emb) / (np.linalg.norm(vault_emb) * np.linalg.norm(ref_emb))
    return 1.0 - cos_sim

def accept_improvement(original: str, improved: str, old_loss: float, new_loss: float) -> bool:
    """Accept if loss decreased AND meaning preserved."""
    meaning_sim = embedding_cosine_sim(improved, original)
    return new_loss < old_loss and meaning_sim > 0.80
```

#### 2.4.4 Rubric Scoring (Interpretable Gap Analysis)

```python
def score_project_plan(doc: str, reference: str) -> tuple[float, list[dict]]:
    dimensions = {
        "completeness": 0.25,
        "clarity": 0.20,
        "timeline_realism": 0.15,
        "dependency_mapping": 0.15,
        "risk_identification": 0.15,
        "execution_ready": 0.10,
    }
    gaps = []
    for dim, weight in dimensions.items():
        score = assess_dimension(doc, reference, dim)  # LLM-judged 0-1
        if score < 0.7:
            gaps.append({"dimension": dim, "score": score,
                         "suggestion": generate_improvement(doc, reference, dim)})
    overall = sum(assess_dimension(doc, reference, d) * w for d, w in dimensions.items())
    return overall * 100, gaps
```

#### 2.4.5 Budget Allocation Across Dream Agent Phases

```python
budget_split = {
    "intake": 0.33,        # Process new raw sources
    "compilation": 0.33,   # Write wiki pages from observations
    "improvement": 0.33,   # Upgrade existing documents
    "lint": 0.01,          # Health checks
}
```

### 2.5 Metadata Pipeline

#### 2.5.1 Cross-Layer Provenance Chain

```
Layer 1: Wiki pages
  └─> YAML frontmatter: sources: ["clawmem://docid/a1b2c3"]
      └─> Direct read: open the page, see the source

Layer 2: ClawMem (SQLite)
  └─> Columns: title, content_type, metadata_json, hash, quality_score, confidence, origin
      └─> metadata_json contains full YAML fields as JSON blob
      └─> origin = "wiki://pages/concepts/foo.md" when round-tripping

Layer 3: MemVid (.mv2 + SQLite join)
  └─> memvid_indices table: (memvid_file, frame_index) → chunk_id
      └─> chunks table: chunk_id → metadata_json (full ChunkMetadata)
          └─> ChunkMetadata contains: provenance, identity, graph, quality, semantic, embedding
              └─> provenance.source_uri → clawmem:// or wiki:// origin
```

#### 2.5.2 Join Table Schema

```sql
-- In buttplug/memory SQLite database
CREATE TABLE memvid_indices (
    memvid_file TEXT NOT NULL,
    frame_index INTEGER NOT NULL,
    chunk_id TEXT NOT NULL,
    embedding_id TEXT NOT NULL,
    corpus_id TEXT NOT NULL,
    PRIMARY KEY (memvid_file, frame_index),
    FOREIGN KEY (chunk_id) REFERENCES chunks(chunk_id),
    FOREIGN KEY (embedding_id) REFERENCES embeddings(embedding_id)
);

-- Round-trip lookup:
-- MemVid frame → memvid_indices.chunk_id → chunks.metadata_json → full ChunkMetadata
```

#### 2.5.3 Transition Metadata Preservation

| Transition | Preserved | Compressed/Lost |
|-----------|-----------|-----------------|
| Session → ClawMem | All (timestamp, content, type, source) | Nothing |
| ClawMem → Wiki | Key claims, confidence, provenance | Raw conversation turns |
| Wiki → ClawMem (reindex) | All (round-trips through YAML) | Nothing |
| ClawMem → MemVid (encode) | All (via memvid_indices → chunks join) | Nothing |

### 2.6 RealClawMem Adapter (Replacement for Existing Stub)

Current state: `src/buttplug_memory/adapters/clawmem.py` is a 250-line stub storing SHA-256 hashes as "embeddings."

**Action:** Delete and replace with:

```python
class RealClawMemAdapter(TierAdapter):
    """Thin wrapper around yoloshii/ClawMem v0.10.1 via REST API."""

    def __init__(self, config):
        self.base_url = config.get("clawmem_url", "http://localhost:7438")
        self.api_key = config.get("clawmem_api_key", None)

    def query(self, prompt, limit=10, filters=None) -> list[dict]:
        """POST /retrieve with auto-routing.
        Returns: [{text, score, docid, metadata, source_tier}, ...]"""
        ...

    def ingest(self, content, metadata) -> bool:
        """POST to ClawMem's file watcher or write .md into indexed collection."""
        ...

    def health_check(self) -> bool:
        """GET /health"""
        ...
```

### 2.7 Scheduler

#### 2.7.1 Service Startup Order

```
1. clawmem serve --port 7438        → REST API for dream agent + adapter
2. clawmem watch                    → File watcher, auto-indexes wiki pages/
3. clawmem-embed.timer (systemd)    → Daily embedding refresh
4. Bootstrap ClawMem collections:
   clawmem collection add ~/ai-wiki/wiki --name wiki
5. Dream agent scheduler (systemd idle timer)
6. MemVid cron (monthly)
```

#### 2.7.2 Schedule Details

| Timer | Frequency | Trigger | Action |
|-------|-----------|---------|--------|
| Dream agent check | 30 min | systemd idle | Compute budget, run dream cycle |
| clawmem embed | Daily | systemd timer | Re-embed all collections |
| MemVid encode | Monthly | cron | Read ClawMem vault, write .mv2 files |
| Vault integrity | Nightly | systemd timer | Verify .mv2 WAL, git health |
| Log rotation | On write, >50MB | Logging handler | Rotate, keep 5 files |

#### 2.7.3 MemVid Schedule Integration

The monthly MemVid encoding creates natural refinement checkpoints:

```
Week 1-3: Dream agent refines actively (high budget, lots of idle time)
Week 4:   Freeze snapshot → run MemVid encoding
          Dream agent still runs but targets next cycle
Day 1-30: Refined memories stay in ClawMem + wiki
Day 31:   Full re-encode includes all refinements from the month
```

Cold storage is always 0-30 days behind live memory — an acceptable design tradeoff.

## 3. Data Flow

### 3.1 Session → Wiki → Archive (Full Lifecycle)

```
Session produces output
    │
    ▼
ClawMem decision-extractor hook captures observation
    │  type: decision | pattern | error
    │  metadata: timestamp, session_id, git_branch
    ▼
Observation stored in ClawMem SQLite vault
    │  queryable via FTS5, vector search, graph traversal
    │  DECAY: 30d half-life for ephemeral, ∞ for decisions
    │
    ▼  (during idle cycles)
Dream agent Phase 1: Extract
    │  Reads ClawMem via REST API
    ▼
Dream agent Phase 2: Refine
    │  Confidence scoring, council escalation if needed
    ▼
Dream agent Phase 3: Compile
    │  Creates/updates wiki page with YAML frontmatter
    │  sources: ["clawmem://docid/abc123"]
    ▼
Dream agent Phase 5: Re-index
    │  POST /reindex → ClawMem picks up wiki changes
    ▼
Wiki page now has origin: "wiki://pages/concepts/x.md"
    │  Both directions linkable:
    │  ClawMem → wiki via origin field
    │  Wiki → ClawMem via sources field
    │
    ▼  (monthly)
MemVid encode reads ClawMem vault
    │  Writes .mv2 files
    │  Populates memvid_indices table
    ▼
Cold-stored frame is reverse-linkable to full metadata
    memvid_indices → chunks.metadata_json → provenance.source_uri
```

### 3.2 Query Flow

```
User prompt (from Claude Code / Hermes session)
    │
    ▼
Intent Router (heuristic, <1ms)
    │
    ├── Strong signal (confidence ≥ 0.8)
    │   └── Route to matching tier(s)
    │
    └── Ambiguous (confidence < 0.8, ~30% of queries)
        │
        ▼
    LLM refinement (hardware-adaptive model)
        │
        ├── "historical" → ClawMem + MemVid (parallel)
        ├── "relational" → ClawMem + graph
        └── anything else → ClawMem only
        │
        └── Fallback: Strategy A (all tiers) on failure
            │
            ▼
    Tier queries execute (parallel or cascade per strategy)
        │
        ▼
    Score fusion or early-exit decision
        │
        ▼
    Context assembly within token budget
        │
        ▼
    Context injected into prompt
        │
        ▼
    Response captured → sanitized → classified → stored → ClawMem
```

### 3.3 Improvement Flow

```
Select document (lowest-scoring first, max 10 iter/doc/cycle)
    │
    ▼
Classify type (heuristic + LLM if needed)
    │
    ▼
Load S-tier reference for type
    │
    ▼
Embed both (ClawMem embedding server)
    │
    ▼
Score via rubric (completeness, clarity, etc.)
    │
    ▼
Identify largest gap (score < 0.7)
    │
    ▼
Generate targeted improvement
    │  Specific, minimal, one section at a time
    ▼
Improve document
    │
    ▼
Re-embed improved version
    │
    ├── loss < old_loss AND meaning preserved (cosine > 0.80)
    │   └── Accept, git commit, continue to next gap
    │
    └── otherwise
        └── Try different approach, or skip, or mark edge case
```

## 4. Integration Points

### 4.1 With Existing buttplug/memory Package

| Current State | Target State |
|---------------|-------------|
| 250-line SHA-256 ClawMem adapter stub | Real REST API adapter (RealClawMemAdapter) |
| No ClawMem integration | Full ClawMem REST integration |
| No proper metadata pipeline | YAML → SQLite → memvid_indices chain |
| No dream agent | Python sidecar with systemd idle timer |
| No sleep-time improvement | Embedding-guided quality engine |

**Adapter rewrite plan:**
1. Delete `src/buttplug_memory/adapters/clawmem.py`
2. Write `RealClawMemAdapter` using ClawMem REST API
3. Ship in `buttplug_memory` package as a drop-in replacement

### 4.2 With ClawMem Backend

| Integration | Method | Port |
|-------------|--------|------|
| Query/search | REST API | 7438 |
| Document retrieval | REST API | 7438 |
| Graph traversal | REST API | 7438 |
| Write via file watcher | File system | N/A (watches ~/ai-wiki/pages/) |
| Reindex trigger | REST API | 7438 |
| Embedding | llama-server or cloud | 8088 or Jina API |

### 4.3 With MemVid V2

| Integration | Method | Schedule |
|-------------|--------|----------|
| Encode | memvid_sdk Python | Monthly cron |
| Query | memvid_sdk Python | On demand (via cold adapter) |
| Metadata linkage | memvid_indices SQLite table | At encode time |
| Integrity check | memvid_sdk WAL recovery | Nightly |

### 4.4 With Git

Every wiki operation goes through git:

```bash
~/ai-wiki/
├── .git/                   # Full version history
├── pages/                  # Tracked
├── skills/                 # Tracked
├── raw/                    # Tracked (immutable source documents)
├── .meta/                  # Tracked (references, config)
└── log.md                  # Tracked (append-only log)
```

Commit format: `type: file — description (detail)`

| Type | Example |
|------|---------|
| compile | `compile: event-loop.md — from session abc123 (confidence 0.87)` |
| improve | `improve: event-loop.md — added asyncio vs trio comparison (scored 72→85)` |
| create | `create: skills/cicd-hook-pattern/SKILL.md — 4 observations` |
| fix | `fix: broken wikilink in auth-migration-adr.md` |
| lint | `lint: 3 stale pages flagged, 2 broken wikilinks repaired` |

## 5. Implementation Plan

### Phase 1: Foundation (Week 1)

| Task | Description | Deliverable |
|------|-------------|-------------|
| 1.1 | Install ClawMem, run init, verify `clawmem serve --port 7438` works | Working ClawMem REST API |
| 1.2 | Set up wiki directory structure: `raw/`, `pages/`, `skills/`, `.meta/references/`, `log.md`, `AGENTS_WIKI.md` | Git-initialized wiki repo |
| 1.3 | Bootstrap ClawMem with wiki collection: `clawmem collection add ~/ai-wiki/wiki --name wiki` | ClawMem indexes wiki pages |
| 1.4 | Install systemd user units: `clawmem watch`, `clawmem-embed.timer` | Auto-indexing and daily embed |
| 1.5 | Build intent router with heuristic classification + strategy resolution | configurable-router.py |

**Exit criteria:** `clawmem query "test"` returns wiki content. Strategy resolution works (hook > env > config > default). Heuristic classifier correctly routes by intent.

### Phase 2: Dream Agent (Week 2)

| Task | Description | Deliverable |
|------|-------------|-------------|
| 2.1 | Write dream agent skeleton: idle-timer trigger, budget calc, ClawMem REST client | dream_agent.py scaffold |
| 2.2 | Implement Phase 1 (Extract): list new docs, fetch content, categorize, key claims | Extract pipeline |
| 2.3 | Implement Phase 2 (Refine): self-consistency, cross-ref, freshness, confidence scoring | Refine pipeline |
| 2.4 | Implement Phase 3 (Compile): wiki page creation/update with YAML frontmatter, wikilinks | Compile pipeline |
| 2.5 | Implement Phase 4 (Pattern Detect): detect 3+ similar tasks → SKILL.md | Pattern detect |
| 2.6 | Implement Phase 5 (Re-index): POST /reindex after writes | Re-index hook |
| 2.7 | End-to-end test: ClawMem doc → dream agent → wiki page → reindex → ClawMem finds it | Integration test |

**Exit criteria:** Dream agent runs on systemd idle timer, compiles observations into wiki pages with full frontmatter, re-indexes ClawMem, detects patterns.

### Phase 3: Git-Backed Wiki (Week 3)

| Task | Description | Deliverable |
|------|-------------|-------------|
| 3.1 | Initialize git repo for wiki directory | `git init ~/ai-wiki` |
| 3.2 | Add git operations to dream agent: commit after every compilation/improvement | git commit integration |
| 3.3 | Implement `log.md` append-only changelog (dream agent writes on every operation) | Changelog integration |
| 3.4 | Git push on significant changes (configurable threshold) | Remote sync |
| 3.5 | Test: 50 wiki operations, verify full git history, all commits have descriptive messages | git log verification |

**Exit criteria:** Every wiki change is git-committed with a descriptive message. Full history is replayable. `log.md` mirrors git history.

### Phase 4: Sleep-Time Improvement (Week 4)

| Task | Description | Deliverable |
|------|-------------|-------------|
| 4.1 | Implement document classifier (type detection: heuristic + LLM) | Doc type classifier |
| 4.2 | Build S-tier reference library: structure `.meta/references/` with exemplars | Reference library |
| 4.3 | Implement embedding-based loss measurement and rubric scoring | Quality scorer |
| 4.4 | Implement improvement loop: embed → measure → improve → re-embed → gate → iterate | Improvement engine |
| 4.5 | Add safety rails: meaning preservation gate (cosine > 0.80), max iterations, original backup | Safety system |
| 4.6 | Integrate improvement into dream agent budget allocation (33%) | Budget integration |
| 4.7 | Test: 10 improvement cycles on a low-scoring doc, verify measurable distance reduction | Improvement test |

**Exit criteria:** Improvement engine runs within dream agent budget, iteratively improves documents, rejects semantic drift, commits each improvement to git.

### Phase 5: Metadata Pipeline (Week 5)

| Task | Description | Deliverable |
|------|-------------|-------------|
| 5.1 | Define ChunkMetadata schema (provenance, identity, graph, quality, semantic, embedding) | Schema definition |
| 5.2 | Integrate with existing buttplug/memory `chunks` table | Schema integration |
| 5.3 | Build `memvid_indices` join table population at encode time | Encode pipeline |
| 5.4 | Read path: MemVid frame → join → full ChunkMetadata | Read pipeline |
| 5.5 | Test: round-trip provenance from session → ClawMem → wiki → MemVid → back to source | Provenance test |

**Exit criteria:** Full provenance chain works in both directions. A memory retrieved from cold storage can be traced back to its original ClawMem document and session.

### Phase 6: RealClawMem Adapter + Integration (Week 6)

| Task | Description | Deliverable |
|------|-------------|-------------|
| 6.1 | Write `RealClawMemAdapter` with query/ingest/health_check using ClawMem REST API | New adapter |
| 6.2 | Delete old 250-line SHA-256 stub adapter | Dead code removed |
| 6.3 | Wire adapter into buttplug/memory package | Package integration |
| 6.4 | Test: adapter returns correct results; backward compatibility with existing API consumers | Integration test |

**Exit criteria:** Old adapter deleted. RealClawMemAdapter works via REST API. buttplug/memory package tests pass.

## 6. Risk Register

| # | Risk | Severity | Probability | Mitigation | Phase |
|---|------|----------|------------|-----------|-------|
| R1 | **ClawMem is TypeScript on Bun** — introduces Bun runtime dependency alongside Python | Medium | High | Runtime managed by systemd. No cross-language calls (HTTP-only). Bun is well-maintained. | 1 |
| R2 | **Echo loop** — injected context from memory routing gets re-captured and re-stored | Critical | Medium | Sentinel markers `[AAA_MEMORY_INJECTED]` stripped during sanitization. ClawMem HTML-style `<vault-context>` tags also stripped. | 2 |
| R3 | **Dream agent never gets budget** — system never idle long enough | Medium | Medium | Configurable threshold (default 5 min). Falls back to wall-clock timer if no idle detected for 4 hours. | 2 |
| R4 | **Improvement doesn't converge** — LLM rewrites move away from reference | Low | Medium | Meaning preservation gate (cosine > 0.80 with original). Max 10 iterations. Skips and logs failures. | 4 |
| R5 | **Metadata corruption** — provenance chain breaks due to schema mismatch | High | Low | Pydantic validation on all metadata writes. Nightly integrity check compares cross-layer counts. | 5 |
| R6 | **MemVid SDK instability** — V2 API changes break the encoding pipeline | Medium | Medium | Thin adapter that isolates all MemVid calls. When SDK changes, only adapter methods need updates. | 5 |
| R7 | **Git conflicts** — dream agent and user both edit the same wiki page | Medium | Low | User edits are authoritative. Dream agent checks for uncommitted changes before writing. Flags human-modified pages as "needs_review." | 3 |
| R8 | **Multi-resolution vector storage overhead** — 5× dimensions × ~10% = 50% of single-res uncompressed | Low | Medium | Acceptable tradeoff for granular search. If storage grows, reduce to 3 tiers (256, 768, 4096). | 5 |
| R9 | **Concurrent dream cycles** — dream agent overlap on systemd timer | Low | Medium | File lock on dream agent PID file. Second instance detects existing PID and exits. | 2 |
| R10 | **S-tier reference copyright** — accidental inclusion of copyrighted material | Medium | Low | Only permissive-license or user-provided content. Automated scan for known copyrighted texts (SHA matching). | 4 |

## 7. Testing Strategy

### 7.1 Unit Tests

| Module | Key Test Cases |
|--------|---------------|
| Intent router | Heuristic classifier accuracy across 50 varied prompts; strategy resolution precedence chain; token budget enforcement |
| Dream agent extract | ClawMem REST parsing; YAML frontmatter extraction; content categorization accuracy |
| Dream agent refine | Confidence scoring formula; cross-reference detection (claim matches/contradicts/extends); council escalation trigger |
| Dream agent compile | Wiki page creation with full frontmatter; wikilink generation; provenance preservation |
| Improvement engine | Embedding loss calculation; rubric scoring correctness; meaning preservation gate; acceptance/rejection logic |
| Metadata | ChunkMetadata schema validation; memvid_indices join path; provenance chain round-trip |
| RealClawMemAdapter | REST API query/ingest/health_check; error handling; timeout behavior |

### 7.2 Integration Tests

| Scenario | Validates |
|----------|-----------|
| Full round-trip (session → ClawMem → dream → wiki → reindex) | All phases work end-to-end |
| Intent routing (archival query hits MemVid) | Correct tier selection |
| Intent routing (recent query hits ClawMem only) | Correct tier selection |
| Improvement cycle (10 iterations on test doc) | Loss decreases, meaning preserved |
| Provenance chain (MemVid frame → chunks → source_uri) | Join path works both directions |
| Git history (50 operations → full replayable history) | Git integration works |
| Echo loop prevention (100 query cycles, zero duplicate entries) | Sentinel stripping works |
| Concurrent safety (overlapping timers don't corrupt) | File lock prevents double cycles |

### 7.3 Performance Benchmarks

| Benchmark | Target | Method |
|-----------|--------|--------|
| Intent router heuristic | < 1ms | 1000 prompts |
| Intent router LLM refinement | < 200ms | 100 ambiguous prompts |
| ClawMem query (REST) | < 100ms | 100 queries |
| Dream agent budget check | < 1s | idle threshold detection |
| Improvement loss measurement | < 500ms | embedding + rubric |
| Wiki page write + git commit | < 2s | 100 write iterations |
| Full dream cycle (no budget limit) | < 30min | max 2hr budget |

## 8. Configuration Reference

### 8.1 Intent Router Config

```yaml
router:
  default_strategy: intent_routed    # score_fusion | cascade | intent_routed
  fallback_strategy: score_fusion
  token_budget: 2000
  heuristic_confidence_threshold: 0.8  # Below this, escalate to LLM
  weights:
    semantic: 0.6
    recency: 0.25
    importance: 0.15
```

### 8.2 Dream Agent Config

```yaml
dream_agent:
  idle_threshold_seconds: 300         # 5 min idle before cycle
  budget_percentage: 0.25             # 25% of idle time
  max_budget_seconds: 7200            # 2 hour cap
  clawmem_url: "http://localhost:7438"
  confidence_threshold_auto: 0.8      # Auto-add
  confidence_threshold_flag: 0.5      # Flag for review
  council_confidence_range:           # [low, high] for council escalation
    - 0.5
    - 0.6
```

### 8.3 Improvement Engine Config

```yaml
improvement:
  max_iterations_per_doc: 10
  convergence_threshold: 0.01         # Improvement < 0.01 loss reduction = converged
  meaning_preservation_threshold: 0.80
  optimal_score_threshold: 90          # Flag for execution
  budget_allocation:
    intake: 0.33
    compilation: 0.33
    improvement: 0.33
    lint: 0.01
```

### 8.4 Metadata Config

```yaml
metadata:
  memvid_join_db: "/home/cheta/code/buttplug/memory/memory.db"
  chunk_metadata_schema_version: "1.0.0"
  nightly_integrity_check: true
```

## 9. Dependencies

| Component | Dependency | Version | Install |
|-----------|-----------|---------|---------|
| ClawMem | Bun, TypeScript | v0.10.1 | `npm install -g clawmem` |
| MemVid SDK | Python | v2.0.157+ | `pip install memvid-sdk` |
| Dream agent | Python 3.10+ | stdlib | System Python |
| Intent router | Python stdlib | stdlib | No additional deps |
| Wiki management | Git | 2.x | System package |
| Systemd timers | systemd | 250+ | System package |
| Embedding llama-server | llama.cpp | CUDA | ClawMem manages |
| ClawMem adapter | httpx | 0.27+ | `pip install httpx` |

## 10. References

1. ARCHITECTURE.md v4.1.0 — Unified Memory Architecture including FSP methodology
2. DREAM_AGENT_V2.md v2.0.0 — Dream agent phases, budget, confidence scoring
3. METADATA_PIPELINE.md v1.1.0 — YAML schema, SQLite columns, memvid_indices join chain
4. TIER_INTEGRATION.md v1.0.0 — Component dependencies, ClawMem adapter rewrite, startup order
5. VAULT_IMPROVEMENT.md v1.0.0 — Sleep-time improvement engine, FORGE methodology, S-tier references
6. buttplug memory design.md v3.1.0 — aaa-memory router, ingestion, tri-strategy, adapter specs
7. buttplug memory requirements.md v3.1.0 — FR/NFR, risks, acceptance criteria
8. buttplug memory masterplan.md — System integration map, phased implementation plan
9. Fractal Synthesis Protocol — User's Obsidian vault `old vault/Fractal Synthesis Protocol...md`
10. FORGE methodology — `old vault/ChetasVault PRD appendix I YAML.md`
11. yoloshii/ClawMem v0.10.1 — github.com/yoloshii/ClawMem
12. MemVid V2 — github.com/memvid/memvid
