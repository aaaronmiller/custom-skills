# RAG Pipeline — Embedding, Chunking, and Hybrid Search

## Embedding Model Selection

### Default: all-MiniLM-L6-v2

- **Dimensions**: 768
- **Speed**: ~10ms per text on CPU (via sentence-transformers)
- **Quality**: Good for general-purpose semantic similarity
- **License**: Apache 2.0
- **Runs locally**: No API calls, no data leaves the machine

### Alternative Models

| Model | Dimensions | Quality | Speed | Use Case |
|-------|-----------|---------|-------|----------|
| `all-MiniLM-L6-v2` | 768 | Good | Fast | Default, balanced |
| `BAAI/bge-small-en-v1.5` | 384 | Good | Very fast | Lower storage, faster search |
| `BAAI/bge-large-en-v1.5` | 1024 | Excellent | Slower | Maximum quality |
| `text-embedding-3-small` (OpenAI) | 1536 | Excellent | API call | If you want cloud-based |
| `text-embedding-3-large` (OpenAI) | 3072 | Best | API call, expensive | Research-grade |

To change the embedding model, update `~/.prompt-mine/config.yaml`:
```yaml
embedding:
  model: "all-MiniLM-L6-v2"
  dimensions: 768
  device: "cpu"         # "cuda" for GPU acceleration
  batch_size: 64
```

After changing models, you must re-embed all turns:
```bash
python scripts/rag_pipeline.py --reembed-all
```

## Chunking Strategy

### For User Prompts (role = user)

User prompts are typically short (100-2000 chars). They are embedded **as-is** without
chunking. Each user turn gets exactly one embedding.

### For Model Responses (role = assistant)

Model responses can be very long. The chunking strategy is:

1. **Short responses** (< 2000 chars): Single embedding of full text
2. **Medium responses** (2000-20000 chars):
   - Split into paragraphs (double-newline delimiter)
   - Group paragraphs into chunks of ~1000 chars with 200-char overlap
   - Each chunk gets its own embedding with parent turn reference
3. **Long responses** (> 20000 chars):
   - Split into sections by markdown headers (##, ###)
   - If sections are still > 5000 chars, split by paragraphs with overlap
   - Each chunk gets its own embedding
   - A "summary chunk" is also created from the auto-generated summary

### For Tool Calls (role = tool)

Tool calls are embedded separately:
- Tool name + truncated input (first 500 chars)
- This enables searching for "when did I use the Bash tool to run pytest"

### Chunk Metadata

Each embedding row stores:
```python
{
    "turn_id": 12345,
    "chunk_index": 0,        # 0 for unchunked, 0..N for chunked
    "chunk_type": "full",    # "full"|"section"|"paragraph"|"summary"
    "chunk_text": "...",     # The actual text that was embedded
    "char_start": 0,         # Start position in original content_text
    "char_end": 1500,        # End position in original content_text
}
```

## Hybrid Search Algorithm

The search system combines three retrieval methods:

### 1. Full-Text Search (FTS5)

```sql
SELECT ct.id, ct.content_text, c.session_title, rank
FROM conversation_turns_fts fts
JOIN conversation_turns ct ON ct.id = fts.rowid
JOIN conversations c ON c.id = ct.conversation_id
WHERE conversation_turns_fts MATCH ?
ORDER BY rank
LIMIT 50;
```

### 2. Vector Similarity Search (sqlite-vec)

```sql
SELECT te.turn_id, te.distance
FROM turn_embeddings te
WHERE te.embedding MATCH ?
  AND te.distance < 0.5   -- Cosine distance threshold
ORDER BY te.distance
LIMIT 50;
```

### 3. SQL Filtering (Structured Metadata)

```sql
SELECT ct.* FROM conversation_turns ct
JOIN conversations c ON c.id = ct.conversation_id
WHERE c.provider = ?
  AND c.project_name = ?
  AND ct.created_at BETWEEN ? AND ?
  AND ct.role = 'user';
```

### Fusion (Reciprocal Rank Fusion)

The three result sets are combined using Reciprocal Rank Fusion (RRF):

```python
def reciprocal_rank_fusion(result_lists, k=60):
    """
    Combine multiple ranked lists using RRF.
    k is a constant that reduces the impact of high rankings.
    """
    scores = defaultdict(float)
    for result_list in result_lists:
        for rank, item in enumerate(result_list):
            scores[item.id] += 1.0 / (k + rank + 1)
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)
```

### Search Flow

```
User Query (natural language)
    │
    ├──→ FTS5 keyword search ──→ ranked results ──┐
    │                                               │
    ├──→ Embed query → vec search ──→ ranked results ──┤──→ RRF fusion ──→ final ranked list
    │                                               │
    └──→ Parse filters → SQL filter ──→ results ───┘
```

## Search API (Python)

```python
from rag_pipeline import PromptMineSearch

search = PromptMineSearch(db_path="~/.prompt-mine/prompt_mine.db")

# Natural language semantic search
results = search.semantic("how did I configure the RAG pipeline", limit=20)

# Filtered search
results = search.search(
    query="Python debugging",
    provider="anthropic",
    project="data-kiln",
    role="user",              # Only user turns
    date_from="2025-01-01",
    date_to="2025-06-01",
    limit=20
)

# SQL-only search (no semantic component)
results = search.sql(
    "SELECT c.session_title, ct.content_text FROM conversation_turns ct "
    "JOIN conversations c ON c.id = ct.conversation_id "
    "WHERE c.provider = 'openai' AND ct.role = 'user' "
    "ORDER BY ct.created_at DESC LIMIT 50"
)

# Find related conversations
related = search.find_related(conversation_id=42, limit=10)
```

## MCP-JDBC / SQL Search for Natural Language Queries

The database schema is designed so that an LLM with SQL capabilities can generate
correct queries from natural language. The key design features enabling this are:

1. **Descriptive column names**: `provider`, `project_name`, `model_id`, `role` — all
   self-documenting so the LLM understands what to filter on.

2. **Normalized tag system**: Tags use a `type:name` format (`project:data-kiln`,
   `topic:python`, `language:typescript`) that maps naturally to user queries like
   "show me all my Python conversations" or "everything about data-kiln".

3. **Pre-computed aggregates**: `turn_count`, `user_turn_count`, `total_chars` on the
   conversations table avoid the need for subqueries.

4. **The FTS5 index** enables natural language queries that an LLM can translate to
   MATCH expressions.

When an LLM generates SQL for this schema, it should be given the DDL from
`database-schema.md` as context, plus the available tag values (queried at runtime).
