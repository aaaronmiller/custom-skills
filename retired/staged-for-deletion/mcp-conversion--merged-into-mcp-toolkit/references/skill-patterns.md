# Skill Patterns

Use this guide when Phase 3 targets a Claude/Agent Skill wrapper.

## Skill Layout

```text
skill-name/
├── SKILL.md
├── scripts/
│   ├── search_items.py
│   └── get_item.py
└── references/
    └── api-notes.md
```

## SKILL.md Requirements

The frontmatter must include `name` and `description`. The description should state what the skill does and when to use it, including likely trigger phrases.

The body should include:
- short workflow
- command table
- when to load each reference file
- safety rules for mutating or destructive operations
- auth/environment notes

Keep `SKILL.md` focused. Put long API details in `references/` and deterministic operations in `scripts/`.

## Safety

Skills wrapping mutating MCP tools should require explicit user confirmation before create/update/delete operations unless the user already gave concrete permission for that exact action.

