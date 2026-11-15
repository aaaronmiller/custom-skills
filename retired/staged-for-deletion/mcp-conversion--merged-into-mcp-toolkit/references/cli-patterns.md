# CLI Patterns

Use this guide when Phase 3 targets a single command-line interface.

## Structure

Create one command with subcommands that mirror MCP tool groups:

```text
mycli search <query> [--limit N]
mycli get <id>
mycli create --name <name> --confirm
```

## Behavior

Default output should be JSON so agents can parse it reliably. Add human-readable output only as an explicit option.

Use flags that mirror MCP input schema fields. Required MCP fields should become required CLI flags or positional arguments.

Mutating operations must have one of:
- `--confirm`
- `--dry-run`
- an interactive confirmation prompt

Prefer Python Typer/argparse or Node Commander when the MCP surface is large. Bash is acceptable for thin wrappers around existing commands.

## Documentation

Generate a README with:
- installation command
- auth environment variables
- command table
- examples for each subcommand
- mapping table from MCP tools to CLI operations

