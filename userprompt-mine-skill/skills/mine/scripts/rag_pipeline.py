#!/usr/bin/env python3
"""
Prompt Mine — RAG Pipeline

Handles embedding generation, semantic search, FTS5 text search, hybrid
search (Reciprocal Rank Fusion), auto-tagging, and topic clustering.

Usage:
    python rag_pipeline.py --search "query" [--provider P] [--project P] [--limit N]
    python rag_pipeline.py --sql "SELECT ..." 
    python rag_pipeline.py --tag [--force]
    python rag_pipeline.py --cluster [--force]
    python rag_pipeline.py --reembed-all
"""

import argparse
import json
import os
import re
import sqlite3
import sys
from collections import defaultdict
from typing import Optional

DB_PATH = os.path.expanduser("~/.prompt-mine/prompt_mine.db")


# ============================================================
# Embedding Functions
# ============================================================

class Embedder:
    """Generate embeddings using sentence-transformers (local) or OpenAI API."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", device: str = "cpu"):
        self.model_name = model_name
        self.device = device
        self._model = None

    def _load_model(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name, device=self.device)
            except ImportError:
                raise ImportError(
                    "sentence-transformers not installed. "
                    "Install with: pip install sentence-transformers"
                )

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a list of texts."""
        self._load_model()
        embeddings = self._model.encode(texts, show_progress_bar=False, batch_size=64)
        return embeddings.tolist()

    def embed_single(self, text: str) -> list[float]:
        """Generate embedding for a single text."""
        return self.embed([text])[0]


# ============================================================
# Search Functions
# ============================================================

def fts_search(conn: sqlite3.Connection, query: str, limit: int = 50) -> list[dict]:
    """Full-text search using FTS5."""
    results = conn.execute(
        """SELECT ct.id, ct.content_text, ct.content_summary, ct.role, ct.created_at,
                  c.session_title, c.provider, c.project_name, c.id as conv_id
           FROM conversation_turns_fts fts
           JOIN conversation_turns ct ON ct.id = fts.rowid
           JOIN conversations c ON c.id = ct.conversation_id
           WHERE conversation_turns_fts MATCH ?
           ORDER BY rank
           LIMIT ?""",
        (query, limit),
    ).fetchall()

    return [
        {
            "turn_id": r[0], "content_text": r[1], "content_summary": r[2],
            "role": r[3], "created_at": r[4], "session_title": r[5],
            "provider": r[6], "project_name": r[7], "conversation_id": r[8],
        }
        for r in results
    ]


def vector_search(
    conn: sqlite3.Connection,
    query_embedding: list[float],
    limit: int = 50,
    distance_threshold: float = 0.5,
) -> list[dict]:
    """Vector similarity search using sqlite-vec."""
    try:
        import numpy as np
        query_vec = json.dumps(query_embedding)

        results = conn.execute(
            """SELECT te.turn_id, te.distance
               FROM turn_embeddings te
               WHERE te.embedding MATCH ?
                 AND te.distance < ?
               ORDER BY te.distance
               LIMIT ?""",
            (query_vec, distance_threshold, limit),
        ).fetchall()

        # Fetch turn details for matching IDs
        turn_ids = [r[0] for r in results]
        if not turn_ids:
            return []

        placeholders = ",".join("?" * len(turn_ids))
        turns = conn.execute(
            f"""SELECT ct.id, ct.content_text, ct.content_summary, ct.role, ct.created_at,
                       c.session_title, c.provider, c.project_name, c.id as conv_id
                FROM conversation_turns ct
                JOIN conversations c ON c.id = ct.conversation_id
                WHERE ct.id IN ({placeholders})""",
            turn_ids,
        ).fetchall()

        distance_map = {r[0]: r[1] for r in results}

        return [
            {
                "turn_id": t[0], "content_text": t[1], "content_summary": t[2],
                "role": t[3], "created_at": t[4], "session_title": t[5],
                "provider": t[6], "project_name": t[7], "conversation_id": t[8],
                "distance": distance_map.get(t[0], 1.0),
            }
            for t in turns
        ]

    except Exception as e:
        print(f"Vector search error (sqlite-vec may not be available): {e}")
        return []


def reciprocal_rank_fusion(result_lists: list[list[dict]], k: int = 60) -> list[dict]:
    """Combine multiple ranked lists using Reciprocal Rank Fusion."""
    scores = defaultdict(float)
    item_map = {}

    for result_list in result_lists:
        for rank, item in enumerate(result_list):
            item_id = item["turn_id"]
            scores[item_id] += 1.0 / (k + rank + 1)
            item_map[item_id] = item

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [
        {**item_map[item_id], "rrf_score": score}
        for item_id, score in ranked
    ]


def hybrid_search(
    conn: sqlite3.Connection,
    query: str,
    provider: Optional[str] = None,
    project: Optional[str] = None,
    role: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    limit: int = 20,
    method: str = "hybrid",
) -> list[dict]:
    """Combined hybrid search with optional filters."""
    result_lists = []

    # FTS5 search
    if method in ("hybrid", "fts"):
        fts_results = fts_search(conn, query, limit=limit * 2)
        if fts_results:
            result_lists.append(fts_results)

    # Vector search
    if method in ("hybrid", "semantic"):
        try:
            embedder = Embedder()
            query_embedding = embedder.embed_single(query)
            vec_results = vector_search(conn, query_embedding, limit=limit * 2)
            if vec_results:
                result_lists.append(vec_results)
        except Exception as e:
            print(f"Semantic search unavailable: {e}")

    # Fuse results
    if len(result_lists) > 1:
        results = reciprocal_rank_fusion(result_lists)
    elif len(result_lists) == 1:
        results = result_lists[0]
    else:
        results = []

    # Apply filters
    filtered = []
    for r in results[:limit * 3]:
        if provider and r.get("provider") != provider:
            continue
        if project and r.get("project_name") != project:
            continue
        if role and r.get("role") != role:
            continue
        if date_from and r.get("created_at", "") < date_from:
            continue
        if date_to and r.get("created_at", "") > date_to:
            continue
        filtered.append(r)

    return filtered[:limit]


def sql_search(conn: sqlite3.Connection, sql_query: str) -> list[dict]:
    """Execute a raw SQL query (read-only)."""
    # Safety: only allow SELECT
    stripped = sql_query.strip().upper()
    if not stripped.startswith("SELECT"):
        raise ValueError("Only SELECT queries are allowed")

    forbidden = ["DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "CREATE", "ATTACH"]
    for word in forbidden:
        if word in stripped:
            raise ValueError(f"Forbidden keyword: {word}")

    cursor = conn.execute(sql_query)
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()

    return [dict(zip(columns, row)) for row in rows]


def find_related(
    conn: sqlite3.Connection,
    conversation_id: int,
    limit: int = 10,
) -> list[dict]:
    """Find conversations related to a given conversation."""
    # Get the target conversation's info
    target = conn.execute(
        "SELECT project_name, provider, created_at FROM conversations WHERE id = ?",
        (conversation_id,),
    ).fetchone()

    if not target:
        return []

    project, provider, created_at = target

    # Strategy 1: Same project
    results = []
    if project:
        same_project = conn.execute(
            """SELECT id, session_title, provider, created_at
               FROM conversations
               WHERE project_name = ? AND id != ?
               ORDER BY created_at DESC LIMIT ?""",
            (project, conversation_id, limit),
        ).fetchall()
        results.extend(same_project)

    # Strategy 2: Same provider, temporally close (within 24h)
    if len(results) < limit:
        from datetime import datetime, timedelta
        try:
            ts = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            window_start = (ts - timedelta(hours=24)).isoformat()
            window_end = (ts + timedelta(hours=24)).isoformat()
            temporal = conn.execute(
                """SELECT id, session_title, provider, created_at
                   FROM conversations
                   WHERE provider = ? AND id != ?
                     AND created_at BETWEEN ? AND ?
                   ORDER BY created_at DESC LIMIT ?""",
                (provider, conversation_id, window_start, window_end, limit - len(results)),
            ).fetchall()
            results.extend(temporal)
        except (ValueError, TypeError):
            pass

    return [
        {"id": r[0], "session_title": r[1], "provider": r[2], "created_at": r[3]}
        for r in results[:limit]
    ]


# ============================================================
# Auto-Tagging
# ============================================================

TAG_PATTERNS = {
    "language:python": [r"\.py\b", r"pip install", r"import \w+", r"def \w+\(", r"print\("],
    "language:typescript": [r"\.tsx?\b", r"npm install", r"import .* from", r"interface \w+"],
    "language:javascript": [r"\.jsx?\b", r"require\(", r"module\.exports", r"function \w+\("],
    "language:rust": [r"\.rs\b", r"cargo ", r"fn main\(", r"impl \w+"],
    "language:go": [r"\.go\b", r"go mod", r"package main", r"func \w+\("],
    "language:sql": [r"\.sql\b", r"SELECT .* FROM", r"CREATE TABLE", r"INSERT INTO"],
    "framework:nextjs": [r"next\.config", r"useRouter", r"NextResponse", r"getServerSideProps"],
    "framework:fastapi": [r"FastAPI", r"@app\.(get|post)", r"uvicorn"],
    "framework:docker": [r"docker-compose", r"Dockerfile", r"FROM \w+"],
    "framework:prisma": [r"schema\.prisma", r"prisma migrate", r"prisma generate"],
    "topic:debugging": [r"\bfix\b", r"\bbug\b", r"\berror\b", r"\btraceback\b", r"\bexception\b"],
    "topic:testing": [r"\btest\b", r"\bpytest\b", r"\bjest\b", r"\bcoverage\b"],
    "topic:deployment": [r"\bdeploy\b", r"\bCI.?CD\b", r"\bpipeline\b", r"\bproduction\b"],
    "topic:security": [r"\bvulnerability\b", r"\bauth\b", r"\bCVE\b", r"\bencryption\b"],
    "topic:performance": [r"\boptimize\b", r"\bslow\b", r"\blatency\b", r"\bprofiling\b"],
    "topic:rag": [r"\bembedding\b", r"\bvector\b", r"\bchunking\b", r"\bsemantic search\b"],
    "topic:agents": [r"\bagent\b", r"\bsubagent\b", r"\bskill\b", r"\bplugin\b", r"\bMCP\b"],
}

TAG_TYPE_MAP = {
    "language": "language",
    "framework": "framework",
    "topic": "topic",
}

TASK_TYPE_RULES = {
    "type:code-generation": lambda tc: tc.get("Write", 0) > 0 and tc.get("Edit", 0) == 0,
    "type:code-edit": lambda tc: tc.get("Edit", 0) > 0,
    "type:code-review": lambda tc: tc.get("Read", 0) > 3 and tc.get("Write", 0) == 0 and tc.get("Edit", 0) == 0,
    "type:debugging": lambda tc: tc.get("Bash", 0) > 0 and tc.get("Read", 0) > 0,
    "type:explanation": lambda tc: sum(tc.values()) <= 2 and tc.get("Read", 0) <= 1,
    "type:search": lambda tc: tc.get("Grep", 0) + tc.get("Glob", 0) > tc.get("Read", 0),
}


def auto_tag_conversations(conn: sqlite3.Connection, force: bool = False) -> int:
    """Auto-tag all untagged conversations (or all if force=True)."""
    tagged = 0

    # Get conversations to tag
    if force:
        convs = conn.execute(
            "SELECT id FROM conversations WHERE is_deleted = 0"
        ).fetchall()
    else:
        convs = conn.execute(
            """SELECT c.id FROM conversations c
               LEFT JOIN conversation_tags ct ON ct.conversation_id = c.id
               WHERE c.is_deleted = 0 AND ct.conversation_id IS NULL"""
        ).fetchall()

    for (conv_id,) in convs:
        # Get all user + assistant text for pattern matching
        turns = conn.execute(
            """SELECT ct.role, ct.content_text, ct.tool_calls
               FROM conversation_turns ct
               WHERE ct.conversation_id = ? AND ct.role IN ('user', 'assistant')
               ORDER BY ct.turn_index""",
            (conv_id,),
        ).fetchall()

        all_text = " ".join(t[1] for t in turns if t[1]).lower()

        # Pattern-based tagging
        for tag_name, patterns in TAG_PATTERNS.items():
            matches = sum(1 for p in patterns if re.search(p, all_text, re.IGNORECASE))
            if matches >= 2:  # Require at least 2 pattern matches
                confidence = min(matches / len(patterns), 1.0)
                _apply_tag(conn, conv_id, tag_name, confidence)
                tagged += 1

        # Tool-call-based task type detection
        tool_counts = defaultdict(int)
        for t in turns:
            if t[2]:  # tool_calls JSON
                try:
                    calls = json.loads(t[2]) if isinstance(t[2], str) else t[2]
                    if isinstance(calls, list):
                        for call in calls:
                            tool_name = call.get("name", call.get("tool", ""))
                            if tool_name:
                                tool_counts[tool_name] += 1
                except (json.JSONDecodeError, TypeError):
                    pass

        for type_tag, rule_fn in TASK_TYPE_RULES.items():
            if rule_fn(dict(tool_counts)):
                _apply_tag(conn, conv_id, type_tag, 0.7)
                tagged += 1

        # Project-based tagging
        project = conn.execute(
            "SELECT project_name FROM conversations WHERE id = ?", (conv_id,)
        ).fetchone()
        if project and project[0] and project[0] != "unknown":
            _apply_tag(conn, conv_id, f"project:{project[0]}", 1.0)
            tagged += 1

    conn.commit()
    return tagged


def _apply_tag(conn: sqlite3.Connection, conv_id: int, tag_name: str, confidence: float):
    """Apply a tag to a conversation, creating the tag if needed."""
    tag_type = tag_name.split(":")[0] if ":" in tag_name else "custom"

    # Ensure tag exists
    tag_id = conn.execute("SELECT id FROM tags WHERE tag_name = ?", (tag_name,)).fetchone()
    if not tag_id:
        cursor = conn.execute(
            "INSERT INTO tags (tag_name, tag_type) VALUES (?, ?)",
            (tag_name, tag_type),
        )
        tag_id = cursor.lastrowid
    else:
        tag_id = tag_id[0]

    # Apply (ignore if already exists)
    try:
        conn.execute(
            """INSERT INTO conversation_tags (conversation_id, tag_id, confidence, source)
               VALUES (?, ?, ?, 'auto')""",
            (conv_id, tag_id, confidence),
        )
    except sqlite3.IntegrityError:
        pass  # Already tagged


# ============================================================
# Clustering
# ============================================================

def cluster_conversations(conn: sqlite3.Connection, force: bool = False) -> int:
    """Cluster conversations by topic using HDBSCAN on embeddings."""
    try:
        import numpy as np
        from sklearn.preprocessing import normalize
        try:
            import hdbscan
        except ImportError:
            print("hdbscan not installed. Install with: pip install hdbscan")
            print("Falling back to simple k-means clustering...")
            from sklearn.cluster import KMeans
            hdbscan = None
    except ImportError:
        print("scikit-learn not installed. Install with: pip install scikit-learn hdbscan")
        return 0

    # Get conversation-level embeddings (mean of user turn embeddings)
    convs = conn.execute(
        """SELECT c.id, c.session_title FROM conversations c
           WHERE c.is_deleted = 0 AND c.user_turn_count > 0"""
    ).fetchall()

    if len(convs) < 10:
        print("Not enough conversations for clustering (need at least 10)")
        return 0

    # For now, use TF-IDF on conversation titles as a lightweight alternative
    # to full embedding-based clustering (which requires all turns to be embedded)
    from sklearn.feature_extraction.text import TfidfVectorizer

    titles = [c[1] or "" for c in convs]
    conv_ids = [c[0] for c in convs]

    vectorizer = TfidfVectorizer(max_features=1000, stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(titles)

    if hdbscan:
        clusterer = hdbscan.HDBSCAN(min_cluster_size=5, metric="euclidean")
        labels = clusterer.fit_predict(tfidf_matrix.toarray())
    else:
        n_clusters = min(max(len(convs) // 20, 3), 50)
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(tfidf_matrix.toarray())

    # Get top terms per cluster
    feature_names = vectorizer.get_feature_names_out()
    clustered = 0

    for cluster_id in set(labels):
        if cluster_id == -1:
            continue  # Noise point

        # Find top terms for this cluster
        cluster_mask = labels == cluster_id
        cluster_tfidf = tfidf_matrix[cluster_mask].mean(axis=0).A1
        top_indices = cluster_tfidf.argsort()[-5:][::-1]
        top_terms = [feature_names[i] for i in top_indices]
        cluster_label = f"cluster:{cluster_id}-{'-'.join(top_terms[:3])}"

        # Tag all conversations in this cluster
        for i, conv_id in enumerate(conv_ids):
            if labels[i] == cluster_id:
                _apply_tag(conn, conv_id, cluster_label, 0.6)
                clustered += 1

    conn.commit()
    print(f"Clustered {clustered} conversations into {len(set(labels)) - (1 if -1 in labels else 0)} clusters")
    return clustered


# ============================================================
# Re-embedding
# ============================================================

def reembed_all(conn: sqlite3.Connection):
    """Re-embed all conversation turns."""
    print("Re-embedding all turns... This may take a while.")
    embedder = Embedder()

    # Clear existing embeddings
    try:
        conn.execute("DELETE FROM turn_embeddings")
    except Exception:
        pass

    # Get all turns
    turns = conn.execute(
        "SELECT id, content_text FROM conversation_turns ORDER BY id"
    ).fetchall()

    batch_size = 64
    for i in range(0, len(turns), batch_size):
        batch = turns[i:i + batch_size]
        ids = [t[0] for t in batch]
        texts = [t[1][:2000] for t in batch]  # Truncate for embedding

        embeddings = embedder.embed(texts)

        for turn_id, embedding in zip(ids, embeddings):
            try:
                conn.execute(
                    "INSERT INTO turn_embeddings (turn_id, embedding) VALUES (?, ?)",
                    (turn_id, json.dumps(embedding)),
                )
            except Exception as e:
                # sqlite-vec may not be available
                print(f"Embedding insert failed: {e}")
                return

        if i % 1000 == 0:
            print(f"  Embedded {i}/{len(turns)} turns...")

    conn.commit()
    print(f"Re-embedded {len(turns)} turns")


# ============================================================
# Main
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="Prompt Mine RAG Pipeline")
    parser.add_argument("--search", help="Natural language search query")
    parser.add_argument("--sql", help="SQL SELECT query")
    parser.add_argument("--provider", help="Filter by provider")
    parser.add_argument("--project", help="Filter by project name")
    parser.add_argument("--role", help="Filter by role (user/assistant)")
    parser.add_argument("--date-from", help="Start date filter (ISO 8601)")
    parser.add_argument("--date-to", help="End date filter (ISO 8601)")
    parser.add_argument("--limit", type=int, default=20, help="Max results")
    parser.add_argument("--method", default="hybrid", choices=["hybrid", "semantic", "fts", "sql"])
    parser.add_argument("--tag", action="store_true", help="Auto-tag conversations")
    parser.add_argument("--cluster", action="store_true", help="Cluster conversations")
    parser.add_argument("--reembed-all", action="store_true", help="Re-embed all turns")
    parser.add_argument("--force", action="store_true", help="Force re-tag/re-cluster")
    parser.add_argument("--db-path", default=DB_PATH)
    args = parser.parse_args()

    if not os.path.exists(args.db_path):
        print(f"Database not found at {args.db_path}")
        print("Run init_database.py first.")
        sys.exit(1)

    conn = sqlite3.connect(args.db_path)
    conn.execute("PRAGMA journal_mode=WAL")

    try:
        if args.search:
            results = hybrid_search(
                conn, args.search,
                provider=args.provider,
                project=args.project,
                role=args.role,
                date_from=args.date_from,
                date_to=args.date_to,
                limit=args.limit,
                method=args.method,
            )
            for i, r in enumerate(results, 1):
                title = r.get("session_title", "Untitled")
                provider = r.get("provider", "?")
                role = r.get("role", "?")
                preview = (r.get("content_summary") or r.get("content_text", ""))[:150]
                print(f"\n{i}. [{provider}/{role}] {title}")
                print(f"   {preview}...")

        elif args.sql:
            results = sql_search(conn, args.sql)
            for r in results:
                print(json.dumps(r, indent=2, default=str))

        elif args.tag:
            count = auto_tag_conversations(conn, args.force)
            print(f"Applied {count} tags")

        elif args.cluster:
            count = cluster_conversations(conn, args.force)
            print(f"Clustered {count} conversations")

        elif args.reembed_all:
            reembed_all(conn)

        else:
            parser.print_help()

    finally:
        conn.close()


if __name__ == "__main__":
    main()
