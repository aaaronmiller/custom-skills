# MCP Conversion Patterns

Use this guide in Phase 2 when deciding what kind of wrapper should replace or supplement an MCP server.

## Target Selection

Choose a CLI when users and agents need one stable command with subcommands. This is the default because it works in terminals, scripts, CI jobs, and agent shells.

Choose standalone scripts when progressive disclosure matters more than a polished interface. One operation per file keeps context small and makes each action easy to inspect.

Choose a skill when the conversion should be invoked by natural language and distributed as an agent capability. A skill can still call scripts for deterministic operations.

Choose a CLI plus skill when the capability needs both terminal ergonomics and agent-native discovery.

## Scope Rules

Convert frequently used tools first. Skip rare tools unless the user explicitly needs full coverage.

Group operations by intent:
- Search/list/read operations should be safe by default.
- Create/update operations should expose confirmation flags.
- Delete/destructive operations should require explicit confirmation and dry-run support.

Preserve auth boundaries. Use environment variables or existing credential helpers. Do not embed tokens.

## Mapping Pattern

Every conversion should end with a table mapping MCP tools to wrappers:

| MCP Tool | Wrapper | Notes |
|---|---|---|
| `search_items` | `cli search` | Read-only |
| `get_item` | `cli get` | Read-only |
| `create_item` | `cli create --confirm` | Mutating |

