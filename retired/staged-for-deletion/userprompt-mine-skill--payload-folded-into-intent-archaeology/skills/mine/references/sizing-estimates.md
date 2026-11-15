# Sizing Estimates

## Token Usage Analysis

Based on your stated usage patterns:

- **Coding models** (Claude Code, Roo, Kilo): Up to **50 million tokens/day**
- **Web chat interfaces** (OpenAI, Gemini, Anthropic web): Much less, primarily non-coding
- **User content ratio**: ~100-200K tokens of actual user instructions per 50M total tokens

### Why User Content Is Much Smaller

The 50M token figure is dominated by:
1. **Model output**: Responses are typically 3-10x longer than user prompts
2. **Cached context**: Claude Code caches and re-sends prior conversation turns,
   file contents, and tool results. Much of this is repeated across requests.
3. **File content injected**: When the model reads files, those file contents
   become tokens in the context window.
4. **System prompts**: Each request includes the system prompt (~2-5K tokens)

The actual **unique user instruction content** is typically 0.4-1.0% of total tokens.

## Storage Estimates

### Per-Source Daily Volume

| Source | Daily Tokens | User Content Tokens | User Content Chars | Model Response Chars |
|--------|-------------|--------------------|--------------------|---------------------|
| Claude Code (heavy day) | 50M | 200K | 800K | ~8M |
| Claude Code (typical day) | 5M | 50K | 200K | ~2M |
| Roo/Kilo Code | 2M | 20K | 80K | ~800K |
| OpenAI Web | 500K | 50K | 200K | ~2M |
| Gemini Web | 300K | 30K | 120K | ~1.2M |
| Anthropic Web | 200K | 20K | 80K | ~800K |

### Database Size Estimates

#### Text Storage (SQLite)

SQLite stores TEXT as UTF-8 with minimal overhead. Average compression ratio
in SQLite is about 1.5x compared to raw text due to page-level compression.

| Component | Daily Raw Size | Monthly Raw Size | SQLite Size (monthly) |
|-----------|---------------|-----------------|----------------------|
| User prompts | ~1.48 MB | ~44.4 MB | ~30 MB |
| Model responses | ~14.8 MB | ~444 MB | ~296 MB |
| Summaries | ~0.3 MB | ~9 MB | ~6 MB |
| Metadata/Indexes | — | — | ~20 MB |
| **Total (typical month)** | **~16.6 MB** | **~498 MB** | **~352 MB** |

#### Vector Storage (sqlite-vec)

Embedding size depends on the model:

| Model | Dimensions | Bytes per Vector | Vectors per Month | Vector DB Size |
|-------|-----------|-----------------|-------------------|----------------|
| all-MiniLM-L6-v2 | 768 | 3,072 | ~30,000 | ~88 MB |
| BAAI/bge-large | 1024 | 4,096 | ~30,000 | ~117 MB |
| text-embedding-3-small | 1536 | 6,144 | ~30,000 | ~176 MB |

Note: Vectors are for **each turn** (not chunked), so ~1,000 turns/day = ~30,000/month.
If chunking long responses, multiply by ~2-3x.

### FTS5 Index Size

The full-text search index adds approximately 30-50% overhead on the indexed text:

| Monthly Text Size | FTS5 Index Size |
|-------------------|----------------|
| ~498 MB | ~200 MB |

### Total Database Size Estimates

| Scenario | 1 Month | 6 Months | 1 Year |
|----------|---------|----------|--------|
| Light use (web only) | 50 MB | 300 MB | 600 MB |
| Typical mixed use | 350 MB | 2.1 GB | 4.2 GB |
| Heavy coding + web | 700 MB | 4.2 GB | 8.4 GB |
| Extreme (50M tokens/day every day) | 1.4 GB | 8.4 GB | 16.8 GB |

### On Your 50M Tokens/Day Pattern

At your peak usage, the database would grow by approximately **40-50 MB/day**,
or about **1.2-1.5 GB/month**. This includes:
- Raw conversation text (user + model, with summaries for long responses)
- Embedding vectors (768-dim, ~3 KB each)
- FTS5 index
- Metadata and indexes

After one year of heavy use, expect a **10-20 GB** database. SQLite handles
databases up to 281 TB, so this is well within limits. Query performance on a
20 GB SQLite database with proper indexes remains excellent for single-user workloads.

## Optimization Strategies

### 1. Response Truncation

By default, full model responses are stored, but only the summary + last 50 lines
are typically accessed. If storage is a concern, you can configure:

```yaml
storage:
  full_response_threshold: 20000   # Store full text for responses < 20K chars
  truncate_to: 10000               # Only store first+last 10K chars for larger
  always_keep_summary: true        # Always store the auto-summary
```

This can reduce storage by 40-60% for very verbose coding sessions where the model
outputs large code files that are already in your project's git history.

### 2. Embedding Dimension Reduction

Using a smaller embedding model (384-dim instead of 768-dim) halves vector storage
with modest quality loss.

### 3. Periodic Archival

Conversations older than 6 months can be archived:
- Keep metadata + summaries + embeddings in the main DB
- Move full response text to a compressed archive (gzip)
- Load on demand when the user expands a very old conversation

### 4. Deduplication

Claude Code's cached context means many turns contain duplicate file contents.
The extraction scripts detect and skip duplicate content within a session.

## Performance Expectations

| Operation | Expected Latency |
|-----------|-----------------|
| Full-text search | < 50ms (100K turns) |
| Vector search (top-50) | < 100ms (100K vectors) |
| Hybrid search (fusion) | < 200ms |
| Insert single turn | < 5ms |
| Bulk ingest (1000 turns) | < 2s |
| Web page load | < 500ms |
