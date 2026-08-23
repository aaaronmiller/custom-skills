# Conversion Checklist

Use this checklist in Phase 4 before delivering a conversion.

- [ ] Every converted MCP tool appears in the mapping table.
- [ ] Any skipped MCP tool has a documented reason.
- [ ] Required auth is documented and uses environment variables or existing credential helpers.
- [ ] No secrets are hardcoded.
- [ ] Read-only operations work without confirmation.
- [ ] Mutating operations require `--confirm`, `--dry-run`, or an interactive prompt.
- [ ] Output is JSON by default or has a JSON mode.
- [ ] `--help` works for every generated command or script.
- [ ] README or script reference includes examples.
- [ ] Generated files follow the target project's language and packaging conventions.
- [ ] Validation was run with `scripts/validate_conversion.py` or an equivalent manual check.

