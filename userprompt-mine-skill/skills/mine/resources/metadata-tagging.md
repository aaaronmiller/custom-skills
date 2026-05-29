# Metadata Tagging, Project Detection, and Topic Clustering

## Auto-Tagging Pipeline

When conversations are ingested, the system automatically applies tags based on
detectable patterns in the content. This runs as part of the `daily_ingest.py` pipeline
or can be triggered separately with `rag_pipeline.py --tag`.

### Tag Types and Detection Rules

#### 1. Language Tags (`language:*`)

Detected by analyzing code blocks and file references in conversation content.

| Pattern | Tag | Detection Method |
|---------|-----|-----------------|
| `*.py`, `pip install`, `import numpy` | `language:python` | Regex on file extensions + import patterns |
| `*.ts`, `*.tsx`, `npm install`, `import React` | `language:typescript` | Regex on file extensions + import patterns |
| `*.js`, `*.jsx`, `require('...')` | `language:javascript` | Regex on file extensions + require patterns |
| `*.rs`, `cargo build`, `fn main()` | `language:rust` | Regex on file extensions + cargo patterns |
| `*.go`, `go mod`, `package main` | `language:go` | Regex on file extensions + go patterns |
| `*.sql`, `CREATE TABLE`, `SELECT * FROM` | `language:sql` | Regex on SQL keywords |
| `*.sh`, `#!/bin/bash` | `language:bash` | Regex on shebangs + shell patterns |

#### 2. Framework Tags (`framework:*`)

| Pattern | Tag | Detection Method |
|---------|-----|-----------------|
| `next.config`, `NextResponse`, `useRouter` | `framework:nextjs` | Pattern matching |
| `FastAPI`, `@app.get`, `uvicorn` | `framework:fastapi` | Pattern matching |
| `app.get(`, `express()`, `router.` | `framework:express` | Pattern matching |
| `docker-compose`, `Dockerfile`, `FROM alpine` | `framework:docker` | Pattern matching |
| `prisma`, `schema.prisma`, `prisma migrate` | `framework:prisma` | Pattern matching |
| `tailwind`, `className=`, `@apply` | `framework:tailwind` | Pattern matching |

#### 3. Topic Tags (`topic:*`)

Detected using keyword frequency + embedding similarity to known topic centroids.

| Topic | Indicator Keywords | Weight |
|-------|-------------------|--------|
| `topic:debugging` | "fix", "bug", "error", "traceback", "exception", "not working" | TF-IDF |
| `topic:refactoring` | "refactor", "clean up", "restructure", "simplify", "DRY" | TF-IDF |
| `topic:testing` | "test", "pytest", "jest", "unit test", "coverage" | TF-IDF |
| `topic:deployment` | "deploy", "CI/CD", "pipeline", "production", "staging" | TF-IDF |
| `topic:security` | "vulnerability", "auth", "CVE", "encryption", "sanitize" | TF-IDF |
| `topic:performance` | "optimize", "slow", "latency", "memory leak", "profiling" | TF-IDF |
| `topic:architecture` | "design", "pattern", "microservice", "scalab", "system design" | TF-IDF |
| `topic:documentation` | "README", "document", "docstring", "API docs" | TF-IDF |
| `topic:rag` | "embedding", "vector", "chunking", "retrieval", "semantic search" | TF-IDF |
| `topic:agents` | "agent", "subagent", "skill", "plugin", "MCP" | TF-IDF |

#### 4. Task Type Tags (`type:*`)

| Type | Detection |
|------|-----------|
| `type:code-generation` | Assistant wrote new files (Write tool calls) |
| `type:code-edit` | Assistant modified files (Edit tool calls) |
| `type:code-review` | User asked to review; assistant primarily used Read tool |
| `type:explanation` | User asked "explain", "what is", "how does"; no file edits |
| `type:debugging` | User mentioned errors; assistant used Bash to run/test |
| `type:planning` | User asked for plan/architecture; no code written |
| `type:search` | User asked to find/search; assistant primarily used Grep/Glob |

### Tagging Confidence

Each auto-applied tag includes a confidence score (0.0-1.0):
- **High confidence** (> 0.8): Direct pattern match (e.g., file extension `.py` → `language:python`)
- **Medium confidence** (0.5-0.8): Keyword frequency above threshold
- **Low confidence** (0.3-0.5): Embedding similarity to topic centroid

Tags below 0.3 confidence are not applied automatically but may be suggested to the user
via the browse interface.

---

## Project Detection

### Detection Strategies (in priority order)

1. **Explicit project field**: Some providers (Anthropic exports, Claude Code sessions)
   include a project/workspace field. Use this directly.

2. **File path extraction**: Scan tool calls for file paths. The common prefix of all
   referenced file paths indicates the project root. The project name is the basename.

3. **Git repository detection**: If the conversation references git commands or working
   directories, extract the repo name from the remote URL or directory name.

4. **Directory context**: For Claude Code / Roo / Kilo conversations, the workspace
   directory is typically available. Use its basename as the project name.

5. **Semantic clustering**: If no structural signal exists, cluster conversations by
   embedding similarity. Conversations about the same project tend to reference the
   same files, libraries, and domain terms.

### Project Normalization

Project names are normalized to handle variants:
```python
PROJECT_ALIASES = {
    "data-kiln": ["datakiln", "data_kiln", "dk"],
    "my-react-app": ["myreactapp", "my_react_app"],
    # ... user can add more in config.yaml
}
```

---

## Topic Clustering

### Algorithm: HDBSCAN on Embedding Space

Conversations are clustered using HDBSCAN on the mean embedding of their user turns:

1. **Compute conversation embeddings**: Average the embeddings of all user turns in a
   conversation to get a single vector per conversation.

2. **Run HDBSCAN**: Fit on the conversation embedding matrix. HDBSCAN is preferred
   over K-means because:
   - Does not require specifying the number of clusters
   - Handles noise points (conversations that don't belong to any cluster)
   - Produces clusters of varying density

3. **Label clusters**: For each cluster, extract the top TF-IDF terms across all
   conversation titles and user prompts in the cluster. These become the cluster label.

4. **Apply cluster tags**: Each conversation in a cluster gets a `topic:cluster-N` tag
   with the cluster label as metadata.

### When to Re-cluster

Clustering is computationally expensive. It should be re-run:
- After the initial full ingest
- When 500+ new conversations have been added since last clustering
- On user request (`rag_pipeline.py --cluster`)

### Incremental Clustering

For incremental updates (new conversations since last clustering):
1. Assign new conversations to the nearest existing cluster if the distance is below
   the cluster's epsilon threshold
2. Conversations that don't fit any existing cluster are marked as "unclustered"
3. Periodically re-run full clustering to handle concept drift

---

## Natural Language Processing for Metadata

### Summarization

For model responses > 2000 chars, an auto-summary is generated:

```python
def generate_summary(text: str, max_length: int = 200) -> str:
    """
    Generate a concise summary of a long model response.
    Uses extractive summarization (no LLM call) for speed.
    """
    # 1. Split into sentences
    # 2. Score sentences by TF-IDF similarity to the full text
    # 3. Select top-N sentences that fit within max_length
    # 4. Return joined sentences
```

For users who want higher-quality abstractive summaries, configure an LLM backend:

```yaml
summarization:
  method: "extractive"    # "extractive" (fast, local) or "abstractive" (LLM call)
  model: "claude-sonnet-4-20250514"     # Only for abstractive
  max_summary_length: 200
```

### Related Conversation Detection

Two conversations are considered "related" if:

1. **Same project**: They reference files in the same project directory
2. **Similar topics**: Their mean embeddings have cosine similarity > 0.7
3. **Shared entities**: They mention the same file names, class names, or function names
4. **Temporal proximity**: They occurred within 24 hours of each other

The `find_related()` API returns conversations ranked by a weighted combination of
these signals.
