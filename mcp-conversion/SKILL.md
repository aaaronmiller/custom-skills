---
name: mcp-conversion
description: |
  Convert existing MCP servers into CLI tools, standalone scripts, or Claude Skills.
  Reduces context window waste while preserving capabilities.
  Use when: "convert MCP", "generate CLI from MCP", "create scripts from MCP tools",
  "wrap MCP as skill", "reduce MCP context usage", "MCP to CLI", "go beyond MCP".
license: Apache-2.0
compatibility: Requires Python 3.10+ for scripts. Works in Claude Code, Claude.ai, and API.
metadata:
  author: ice-ninja
  version: "2.0"
---

# MCP Conversion

Convert MCP servers into leaner, more efficient wrappers: CLIs, scripts, or Skills.

---

## Overview

MCP servers are powerful but context-heavy. Each tool definition consumes tokens.
This skill helps you extract MCP functionality into lighter-weight forms:

| Target | Best For | Context Cost |
|--------|----------|--------------|
| **CLI** | Human + agent use, single entrypoint | Low |
| **Scripts** | Maximum progressive disclosure | Very Low |
| **Skill** | Claude-native auto-discovery | Low |

---

# Process

## Phase 1: Analyze MCP Server

**Goal**: Understand what you're converting.

### 1.1 Extract Tool Information

Run the analysis script or manually inspect:

```bash
python scripts/analyze_mcp.py <mcp_definition.json>
# Or
python scripts/analyze_mcp.py <mcp_server_url>
```

The script outputs:
- Tool list with descriptions
- Grouped by type (read-only, write, destructive)
- CLI subcommand suggestions

### 1.2 Identify Key Information

Collect:
- Tool names, descriptions, input schemas
- Auth requirements (API keys, OAuth, etc.)
- Natural groupings (search/read vs. create/update/delete)

### 1.3 Decide What to Convert

You rarely need every tool. Prioritize:
- Frequently used operations
- Operations that are context-heavy in MCP form
- Operations suitable for CLI/script usage

---

## Phase 2: Choose Target

**Goal**: Select the right wrapper type.

### Decision Tree

```
User's primary use case?
├── Terminal/automation → CLI (recommended)
├── Maximum context savings → Scripts
├── Claude-native workflows → Skill
└── Multiple targets → CLI + Skill combo
```

### Target Selection

If user specifies target, use it directly.

Otherwise, ask:
> "Which format would you like?
> 1. **CLI**: Single command with subcommands (best for most cases)
> 2. **Scripts**: One file per operation (maximum progressive disclosure)
> 3. **Skill**: Claude-native wrapper (auto-discovery in Claude environments)"

See [📋 Conversion Patterns](references/conversion-patterns.md) for detailed guidance.

---

## Phase 3: Generate Wrappers

**Goal**: Create the actual conversion output.

### 3.1 For CLI Target

**Load**: [🔧 CLI Patterns](references/cli-patterns.md)

Generate:
1. **Main CLI file** (Python/Typer, Node/Commander, or Bash)
   - One subcommand per MCP tool
   - Flags mirror MCP parameters
   - JSON output by default
2. **README.md** with command table and examples
3. **Agent prime snippet** for context-minimal usage

### 3.2 For Scripts Target

**Load**: [📝 Script Patterns](references/script-patterns.md)

Generate:
1. **One script per MCP tool** (self-contained)
   - Dependencies declared at top
   - `--help` support
   - JSON output by default
2. **SCRIPTS_REFERENCE.md** mapping scripts to intentions

### 3.3 For Skill Target

**Load**: [⚡ Skill Patterns](references/skill-patterns.md)

Generate:
1. **SKILL.md** with proper frontmatter
   - Description includes trigger keywords
   - Commands table in body
2. **scripts/** folder with underlying tools
3. **Environment documentation**

---

## Phase 4: Verify & Document

**Goal**: Ensure conversion is complete and safe.

### 4.1 Run Validation

```bash
python scripts/validate_conversion.py <output_dir> --mcp <original_mcp.json>
```

Validation checks:
- ✅ All MCP tools have wrappers (or documented gaps)
- ✅ No hardcoded secrets
- ✅ Uses environment variables for auth
- ✅ Documentation exists
- ✅ JSON output support

### 4.2 Complete Checklist

**Load**: [✓ Conversion Checklist](references/conversion-checklist.md)

Use for final sign-off before delivering to user.

### 4.3 Create Mapping Table

Always include a clear mapping:

| MCP Tool | Wrapper | Notes |
|----------|---------|-------|
| `search_items` | `cli search` / `scripts/search.py` | |
| `get_item` | `cli get` / `scripts/get.py` | |
| `create_item` | `cli create` / `scripts/create.py` | Requires `--name` |

---

# Reference Files

Load these as needed during conversion:

| File | When to Load | Purpose |
|------|--------------|---------|
| [📋 Conversion Patterns](references/conversion-patterns.md) | Phase 2 | Overall patterns and tradeoffs |
| [🔧 CLI Patterns](references/cli-patterns.md) | Phase 3 (CLI) | Python/Node/Bash CLI templates |
| [📝 Script Patterns](references/script-patterns.md) | Phase 3 (Scripts) | Standalone script templates |
| [⚡ Skill Patterns](references/skill-patterns.md) | Phase 3 (Skill) | SKILL.md templates |
| [✓ Conversion Checklist](references/conversion-checklist.md) | Phase 4 | Quality verification |

---

# Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `scripts/analyze_mcp.py` | Extract tools from MCP | `python analyze_mcp.py <source>` |
| `scripts/validate_conversion.py` | Verify conversion quality | `python validate_conversion.py <dir>` |

---

# Anti-Patterns

### ❌ Converting Everything
Not every MCP tool needs a wrapper. Skip rarely-used tools.

### ❌ Hardcoding Secrets
Never embed API keys. Always use environment variables.

### ❌ Duplicating Logic
Call the original MCP server or API. Don't reimplement business logic.

### ❌ Giant SKILL.md
Keep SKILL.md under 500 lines. Split into reference files.

### ❌ Missing Documentation
Every conversion needs README or SCRIPTS_REFERENCE.md.

---

# Example Conversion

**Input**: MCP server with 5 tools
```json
{
  "tools": [
    {"name": "search_items", "description": "Search for items"},
    {"name": "get_item", "description": "Get item by ID"},
    {"name": "list_items", "description": "List all items"},
    {"name": "create_item", "description": "Create new item"},
    {"name": "delete_item", "description": "Delete item"}
  ]
}
```

**Output**: CLI wrapper
```
mycli/
├── mycli.py           # Main CLI with 5 subcommands
├── README.md          # Documentation + examples
└── requirements.txt   # Dependencies
```

**Usage**:
```bash
# Search
mycli search "query" --limit 10

# Get single item
mycli get item-123

# Create (requires confirmation)
mycli create --name "New Item" --confirm
```

---

**System Version**: 2.0 (XL Upgrade)
**Updated**: December 2025
