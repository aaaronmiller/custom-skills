# Data Architecture Decision Guide

> Reference for Phase 3: Making data storage, schema, and hosting decisions based on project requirements.

## Storage Type Decision Tree

Start with the fundamental question:

```
Does the system need to persist data at all?
├── NO (stateless/ephemeral): Client-side state only (React/Svelte state, URL params, localStorage)
│   Consider: sessionStorage for tab-scoped, in-memory for process-scoped
│   Skip the rest of this decision tree
├── YES: Is data primarily relational (entities with FK relationships)?
├── YES: Does the dataset exceed 10GB or need concurrent multi-user writes?
│   ├── YES: PostgreSQL (or MySQL/MariaDB)
│   │   Consider: Supabase, Neon, PlanetScale, Turso (if edge-first)
│   └── NO: SQLite (single-file, zero-config)
│       Consider: Turso (distributed SQLite), local file
├── NO: Is data primarily key-value or document-shaped?
│   ├── YES: Is the schema highly variable per record?
│   │   ├── YES: Document store (MongoDB, DynamoDB, Firestore)
│   │   └── NO: Key-value (Redis, Cloudflare KV, Deno KV)
│   └── Is data graph-structured (many-to-many, traversals)?
│       ├── YES: Graph DB (Neo4j, KuzuDB/LadybugDB)
│       │   OR: PostgreSQL with recursive CTEs if graph is secondary
│       └── Is data primarily searched by content similarity?
│           ├── YES: Vector store (Qdrant, Pinecone, pgvector)
│           └── Is data time-series (append-only, time-indexed)?
│               ├── YES: TimescaleDB, InfluxDB, or partitioned PostgreSQL
│               └── Simple file storage (JSON, YAML, JSONL)
```

## Schema Design Principles

### For Relational Data (SQL)

1. **Normalize first, denormalize for performance:**
   - Start at 3NF (Third Normal Form)
   - Denormalize only when read patterns demand it
   - Document every denormalization with rationale

2. **Essential schema elements:**
   - `id`: UUID or ULID (prefer ULID for sortable, non-leaking IDs)
   - `created_at`: TIMESTAMPTZ, always populated
   - `updated_at`: TIMESTAMPTZ, auto-updated via trigger
   - Soft delete via `deleted_at` column (nullable TIMESTAMPTZ) unless hard delete is a requirement

3. **Join strategy:**
   - Inner joins: when both sides must exist (user + user_profile)
   - Left joins: when the right side is optional (user + user_settings)
   - Avoid cross joins in application code
   - Prefer `EXISTS` subqueries over `IN` for large sets

4. **Index strategy:**
   - Primary keys are automatically indexed
   - Add indexes for columns used in WHERE, JOIN ON, and ORDER BY
   - Composite indexes: put equality columns first, range columns last
   - Partial indexes for filtered queries (e.g., `WHERE deleted_at IS NULL`)

### For Document Stores

1. **Embed vs Reference decision:**
   - Embed when: data is always accessed together, child data is small, updates are infrequent
   - Reference when: data is accessed independently, child data is large, updates are frequent

2. **Document shape conventions:**
   - Flat is better than nested (max 3 levels deep)
   - Arrays of embedded documents: cap at ~100 items
   - Use consistent field naming (camelCase or snake_case, not mixed)

### For Key-Value Stores

1. **Key naming convention:** `namespace:entity:id` (e.g., `user:session:abc123`)
2. **TTL strategy:** Set expiry on all ephemeral data
3. **Serialization:** JSON for structured data, raw strings for simple values

## Access Pattern Analysis

For each identified entity, classify its primary access pattern:

| Pattern | Characteristics | Optimization |
|---------|----------------|-------------|
| **Read-heavy** | >90% reads, infrequent writes | Caching, read replicas, materialized views |
| **Write-heavy** | Frequent inserts/updates, less reads | Write-optimized storage, async processing, batch writes |
| **Mixed** | Balanced read/write | Connection pooling, careful index selection |
| **Append-only** | Log-style, never updated | Partitioned tables, time-series optimization |
| **Search-heavy** | Full-text or similarity search dominant | Dedicated search index (FTS5, Meilisearch, vector store) |

## Hosting Decision Matrix

| Factor | Cloudflare Workers | Vercel | Self-hosted | AWS/GCP |
|--------|-------------------|--------|-------------|---------|
| **Best for** | Static, API, edge, cost-sensitive | SSR, background jobs, long-running | Full control, GPU, privacy | Enterprise, complex infra |
| **Free tier** | Generous (100K req/day) | Hobby tier available | Hardware cost only | 12-month trial |
| **Cold start** | ~0ms (V8 isolates) | ~250ms (serverless) | None (always-on) | Varies |
| **Max execution** | 30s (paid), 10ms CPU (free) | 60s (hobby), 300s (pro) | Unlimited | Varies |
| **Database pairing** | D1, KV, R2, Turso | Vercel Postgres, Neon | Any | RDS, DynamoDB |
| **When to avoid** | Long-running tasks, WebSockets (limited) | Cost-sensitive at scale | Ops overhead too high | Budget constraints |

### Free Tier Optimization

When the user prioritizes zero-cost operation:

| Service | Free Tier Highlights |
|---------|---------------------|
| Cloudflare Workers | 100K requests/day, 1GB KV storage, 5GB R2 |
| Cloudflare D1 | 5M rows read/day, 100K writes/day, 5GB storage |
| Turso | 9GB storage, 500M rows read/month, 25 databases |
| Neon | 0.5GB storage, 190 compute hours/month |
| Supabase | 500MB database, 50K monthly active users |
| Vercel | 100GB bandwidth, serverless functions |
| Railway | $5 free credit/month |
| Fly.io | 3 shared VMs, 3GB persistent storage |

## Security Baseline

Every data architecture decision should address:

1. **Encryption:** TLS in transit (mandatory), encryption at rest (when storing PII)
2. **Access control:** Principle of least privilege for all database credentials
3. **Input validation:** All user input validated before storage
4. **Secrets management:** Environment variables, never committed to repo
5. **Backup strategy:** Automated backups with tested restore procedure
6. **Audit trail:** Log who changed what and when for sensitive data

## Output Format

Data architecture decisions should appear in the design document as:

- Section 3: Data Model (schema, relationships, access patterns)
- Section 7: Hosting and Deployment (infrastructure choices)
- Section 8: Security Considerations (data protection specifics)

Each decision should include the rationale connecting it back to specific requirements (FR-XXX or NFR-XXX).
