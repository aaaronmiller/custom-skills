# Web Interface Design

## Architecture

The browse interface is a lightweight web application served by the prompt-mine
web server (`scripts/web_server.py`). It uses vanilla HTML + CSS + JavaScript with
no build step, keeping it simple and dependency-free.

```
Browser ←→ web_server.py (Flask/FastAPI)
                  │
                  ├── /               → Browse UI (SPA)
                  ├── /api/search     → Hybrid search endpoint
                  ├── /api/capture    → Tampermonkey capture endpoint
                  ├── /api/conversations → List/filter conversations
                  ├── /api/conversations/:id → Get conversation with turns
                  ├── /api/tags       → List/manage tags
                  ├── /api/projects   → List projects
                  └── /api/stats      → Database statistics
```

## UI Layout

```
┌──────────────────────────────────────────────────────────────────┐
│  🔍 [Search bar - natural language or SQL]          [Filters ▾] │
├──────────────┬───────────────────────────────────────────────────┤
│              │                                                   │
│  Projects    │  Conversation List                                │
│  ──────────  │  ──────────────────                               │
│  data-kiln   │  ▸ Python debugging help          openai  3m ago │
│  my-react    │    Fix the auth bug in login.py...                │
│  prompt-mine │    ─────────────────────────                      │
│  ...         │  ▸ Configure RAG pipeline     anthropic  1h ago  │
│              │    Set up the embedding model and...              │
│  Providers   │    ─────────────────────────                      │
│  ──────────  │  ▸ Docker compose setup        claude-code 2h ago│
│  ☑ OpenAI    │    Create a docker-compose.yaml...               │
│  ☑ Anthropic │                                                   │
│  ☑ Gemini    │                                                   │
│  ☑ Claude    │                                                   │
│  ☑ Roo/Kilo  │                                                   │
│              │                                                   │
│  Tags        │                                                   │
│  ──────────  │                                                   │
│  topic:rag   │                                                   │
│  lang:python │                                                   │
│  type:debug  │                                                   │
│              │                                                   │
├──────────────┴───────────────────────────────────────────────────┤
│  [← Prev]  Showing 1-50 of 1,247 conversations   [Next →]      │
└──────────────────────────────────────────────────────────────────┘
```

### Expanded Conversation View

When a user clicks on a conversation preview:

```
┌──────────────────────────────────────────────────────────────────┐
│  ← Back    Python debugging help              openai  3m ago    │
│             Tags: topic:debugging, language:python, project:dk   │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  👤 User:                                                        │
│  Fix the auth bug in login.py — it's throwing a 401 when the    │
│  session cookie expires but the token is still valid.            │
│                                                                  │
│  🤖 Assistant:                                           [▼ 3▼]  │
│  I'll examine the auth middleware to identify the issue...       │
│  ┌─────────────────────────────────────────────────────┐        │
│  │ The problem is in the session validation logic.     │        │
│  │ When the session cookie expires, the middleware     │        │
│  │ returns 401 before checking the bearer token.       │        │
│  │ ...                                                 │        │
│  │ ─── last 50 lines ───                              │        │
│  │ return Response(status=200)                         │        │
│  │                                                     │        │
│  │ This ensures the bearer token is checked even when  │        │
│  │ the session cookie has expired.                     │        │
│  └─────────────────────────────────────────────────────┘        │
│  [View Full Response (4,231 chars)]  [Copy]  [Find Related]     │
│                                                                  │
│  👤 User:                                                        │
│  That fixes it, but now the tests are failing.                   │
│                                                                  │
│  🤖 Assistant:                                           [▼ 2▼]  │
│  The tests need to be updated to reflect the new auth flow...    │
│  [View Full Response (2,100 chars)]  [Copy]  [Find Related]     │
│                                                                  │
├──────────────────────────────────────────────────────────────────┤
│  Related: Configure auth middleware (anthropic) • Session fix... │
└──────────────────────────────────────────────────────────────────┘
```

## Collapsed/Expanded Display Rules

### Default State (Collapsed)

- **User prompts**: Show first 2-3 lines (max 150 chars), then "..."
- **Model responses**: Show content_summary if available (max 150 chars)
- If no summary, show first 2-3 lines of content_truncated

### Expanded State

Clicking the `[▼ N▼]` badge expands to show:
- For responses < 2000 chars: full text
- For responses 2000-20000 chars: summary + last 50 lines
- For responses > 20000 chars: summary + last 50 lines + "[View Full Response]" button

The "[View Full Response]" button loads the full text in a scrollable container
with client-side search (Ctrl+F within the response).

## API Endpoints

### GET /api/conversations

```json
{
    "conversations": [
        {
            "id": 1,
            "provider": "openai",
            "session_title": "Python debugging help",
            "project_name": "data-kiln",
            "model_id": "gpt-4",
            "turn_count": 6,
            "user_turn_count": 3,
            "total_chars": 8542,
            "created_at": "2025-01-15T10:30:00Z",
            "tags": ["topic:debugging", "language:python", "project:data-kiln"],
            "preview": {
                "first_user_turn": "Fix the auth bug in login.py...",
                "first_assistant_summary": "I'll examine the auth middleware..."
            }
        }
    ],
    "total": 1247,
    "offset": 0,
    "limit": 50
}
```

Query parameters:
- `provider` — Filter by provider
- `project` — Filter by project name
- `tag` — Filter by tag (repeatable)
- `model` — Filter by model ID
- `date_from`, `date_to` — Date range filter
- `q` — Full-text search query
- `semantic` — Semantic search query (triggers embedding + vector search)
- `sort` — Sort field (`created_at`, `total_chars`, `turn_count`)
- `order` — Sort direction (`asc`, `desc`)
- `limit`, `offset` — Pagination

### GET /api/conversations/:id

Returns a conversation with all its turns, tags, and related conversations.

### GET /api/search

Combined search endpoint that accepts natural language queries:

```json
{
    "query": "how did I configure the RAG pipeline",
    "provider": null,
    "project": null,
    "limit": 20,
    "method": "hybrid"   // "hybrid"|"semantic"|"fts"|"sql"
}
```

Response includes ranked results with relevance scores and highlighted snippets.

### POST /api/tags

Add, remove, or modify tags on conversations:

```json
{
    "conversation_id": 42,
    "tags": ["project:data-kiln", "topic:rag"],
    "source": "user"
}
```

### GET /api/stats

Database statistics for the dashboard:

```json
{
    "total_conversations": 1247,
    "total_turns": 28456,
    "total_user_turns": 9832,
    "providers": {
        "openai": {"conversations": 423, "turns": 8934},
        "anthropic": {"conversations": 312, "turns": 7456},
        "gemini": {"conversations": 189, "turns": 3421},
        "claude-code": {"conversations": 198, "turns": 5890},
        "roo": {"conversations": 125, "turns": 2755}
    },
    "projects": [
        {"name": "data-kiln", "conversation_count": 342},
        {"name": "my-react-app", "conversation_count": 198}
    ],
    "last_ingest": "2025-01-15T14:30:00Z",
    "db_size_mb": 847.3
}
```

## Technology Stack

- **Backend**: Python Flask (lightweight, single-file)
- **Frontend**: Vanilla HTML + CSS + JavaScript (no framework)
- **Styling**: CSS custom properties + flexbox/grid
- **Search**: Handled by backend API; frontend just renders results
- **No build step**: Serve static files directly

This keeps the interface simple, fast to load, and easy to modify without
any JavaScript bundler or framework knowledge.
