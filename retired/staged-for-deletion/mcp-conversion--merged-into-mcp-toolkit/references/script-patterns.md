# Script Patterns

Use this guide when Phase 3 targets standalone scripts.

## Structure

Create one script per MCP operation:

```text
scripts/search_items.py
scripts/get_item.py
scripts/create_item.py
SCRIPTS_REFERENCE.md
```

Each script should:
- include `--help`
- accept all required inputs as flags or positional arguments
- output JSON by default
- document required environment variables at the top
- exit non-zero on failures

## Naming

Use lowercase names based on MCP tool names. Convert separators to underscores for Python files and hyphens for shell commands only when that matches the local style.

## Context Use

Scripts are best when the agent should load only the operation it needs. Keep shared logic small and explicit; if helper modules are necessary, document them in `SCRIPTS_REFERENCE.md`.

