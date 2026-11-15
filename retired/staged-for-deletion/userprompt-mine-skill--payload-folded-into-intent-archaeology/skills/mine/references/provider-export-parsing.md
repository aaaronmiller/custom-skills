# Provider Export Parsing

## OpenAI Data Export

### Export Structure

When you request your data from OpenAI (Settings → Data Controls → Export), you receive
a ZIP file containing:

```
chatgpt-export/
├── conversations.json       # All conversations
├── user.json                # Account metadata
├── models.json              # Model usage history
├── message_feedback.json    # Thumbs up/down data
└── chatgpt-settings.json    # User settings
```

### conversations.json Format

```json
[
  {
    "id": "conv-abc123",
    "title": "Python debugging help",
    "create_time": 1705312345.678,
    "update_time": 1705312567.890,
    "mapping": {
      "msg-node-1": {
        "id": "msg-node-1",
        "message": {
          "id": "msg-1",
          "author": {"role": "user"},
          "content": {"parts": [{"type": "text", "text": "Fix this Python code"}]},
          "create_time": 1705312345.678,
          "metadata": {}
        },
        "parent": null,
        "children": ["msg-node-2"]
      },
      "msg-node-2": {
        "id": "msg-node-2",
        "message": {
          "id": "msg-2",
          "author": {"role": "assistant"},
          "content": {"parts": [{"type": "text", "text": "Here's the fix..."}]},
          "create_time": 1705312350.123,
          "metadata": {"model_slug": "gpt-4"}
        },
        "parent": "msg-node-1",
        "children": []
      }
    },
    "current_node": "msg-node-2",
    "model": "gpt-4"
  }
]
```

### Field Mappings

| Export Field | DB Column | Transform |
|-------------|-----------|-----------|
| `id` | `session_id` | Direct |
| `title` | `session_title` | Direct |
| `create_time` | `created_at` | Unix float → ISO 8601 |
| `mapping[*].message.author.role` | `role` | Direct |
| `mapping[*].message.content.parts[*].text` | `content_text` | Concatenate all text parts |
| `mapping[*].message.metadata.model_slug` | `model_id` | Direct |
| (derived) | `provider` | Always `openai` |
| `mapping[*].parent/children` | (used for ordering) | Reconstruct turn sequence |

### Tree Structure Handling

OpenAI conversations use a tree structure (not a flat list) to support message
editing and branching. The extraction must:

1. **Find the root node** (parent is null)
2. **Walk the tree** following `children` links to reconstruct the linear conversation
3. **Handle branches**: If a node has multiple children, follow the `current_node` path
   for the main branch; store alternate branches as separate conversation threads
4. **Flatten parts**: A message may have multiple content parts (text, code, images);
   concatenate text parts, note image references

### Edge Cases

- **Deleted messages**: Nodes with `message: null` (deleted but tree preserved)
- **System messages**: Filter out internal system prompts unless user wants them
- **DALL-E generations**: Content parts may include image URLs; store metadata only
- **Code interpreter**: Tool call results may be embedded; extract as tool_calls

---

## Google Gemini Data Export

### Export Structure

Google Takeout for Gemini produces:

```
takeout/
├── Takeout/
│   └── Gemini Apps/
│       ├── conversations/
│       │   ├── conversation_2024-01-15T10-30-00.json
│       │   └── conversation_2024-01-16T14-22-00.json
│       └── settings.json
└── ...
```

### Conversation JSON Format

```json
{
  "conversation_id": "gemini-conv-123",
  "title": "Explain quantum computing",
  "create_time": "2024-01-15T10:30:00Z",
  "turns": [
    {
      "user_input": {
        "text": "Explain quantum computing in simple terms",
        "timestamp": "2024-01-15T10:30:00Z"
      },
      "model_output": {
        "text": "Quantum computing uses quantum bits (qubits)...",
        "timestamp": "2024-01-15T10:30:05Z",
        "model": "gemini-1.5-pro"
      }
    }
  ],
  "metadata": {
    "model": "gemini-1.5-pro",
    "language": "en"
  }
}
```

### Field Mappings

| Export Field | DB Column | Transform |
|-------------|-----------|-----------|
| `conversation_id` | `session_id` | Direct |
| `title` | `session_title` | Direct; may be auto-generated |
| `create_time` | `created_at` | ISO 8601 (direct) |
| `turns[].user_input.text` | `content_text` (role=user) | Direct |
| `turns[].model_output.text` | `content_text` (role=assistant) | Direct |
| `turns[].user_input.timestamp` | `turn_created_at` | ISO 8601 |
| `turns[].model_output.model` | `model_id` | Direct |
| (derived) | `provider` | Always `gemini` |

### Edge Cases

- **Missing title**: Generate from first user input (first 80 chars)
- **Attached files**: May reference uploaded documents; store filename metadata only
- **Grounding URLs**: Model output may include source links; extract as citations
- **Image uploads**: User may include images; note in metadata but do not store binary

---

## Anthropic Data Export

### Export Structure

Anthropic provides exports on request (Settings → Privacy → Export Data):

```
anthropic-export/
├── conversations.json        # All conversations
├── user.json                 # Account metadata
└── usage.json                # Token usage history
```

### conversations.json Format

```json
[
  {
    "id": "anthro-conv-456",
    "title": "Review my React component",
    "created_at": "2025-01-15T10:30:00Z",
    "updated_at": "2025-01-15T10:35:00Z",
    "messages": [
      {
        "id": "msg-789",
        "role": "user",
        "content": [
          {"type": "text", "text": "Review this React component for best practices"}
        ],
        "created_at": "2025-01-15T10:30:00Z",
        "model": null
      },
      {
        "id": "msg-790",
        "role": "assistant",
        "content": [
          {"type": "text", "text": "Here's my review of your component..."},
          {"type": "tool_use", "name": "analysis", "input": {"file": "Button.tsx"}}
        ],
        "created_at": "2025-01-15T10:30:05Z",
        "model": "claude-sonnet-4-20250514"
      }
    ],
    "model": "claude-sonnet-4-20250514",
    "project": "my-react-app"
  }
]
```

### Field Mappings

| Export Field | DB Column | Transform |
|-------------|-----------|-----------|
| `id` | `session_id` | Direct |
| `title` | `session_title` | Direct |
| `created_at` | `created_at` | ISO 8601 (direct) |
| `messages[].role` | `role` | Direct |
| `messages[].content[].text` | `content_text` | Concatenate text-type content blocks |
| `messages[].model` | `model_id` | May be null on user messages |
| `model` (top-level) | `model_id` (fallback) | Use if per-message model is null |
| `project` | `project_name` | Direct if present |
| (derived) | `provider` | Always `anthropic` |

### Content Block Handling

Anthropic messages use an array of content blocks:
- `type: "text"` → extract text directly
- `type: "tool_use"` → store as tool_calls JSON
- `type: "tool_result"` → store as tool_calls JSON
- `type: "image"` → note in metadata, do not store binary
- `type: "thinking"` → store in `thinking_content` column (optional, for extended thinking)

---

## Common Processing Rules (All Providers)

1. **Deduplication**: Use `(provider, session_id, turn_index)` as unique key
2. **Timestamp normalization**: All timestamps stored as ISO 8601 UTC
3. **Character encoding**: Force UTF-8; replace invalid sequences
4. **Null handling**: Missing optional fields → NULL, not empty string
5. **Incremental processing**: Skip conversations whose `(provider, session_id)` already
   exists unless `--force-reprocess` flag is set
6. **Large exports**: Stream-parse JSON (use `ijson` or similar) to avoid loading
   multi-GB files entirely into memory
