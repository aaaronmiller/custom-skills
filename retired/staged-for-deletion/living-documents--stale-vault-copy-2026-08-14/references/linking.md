# Living Documents linking

Use `parent` for hierarchy and `related` for non-hierarchical relationships. Both use stable page IDs.

Use `related-projects` in `project.md` for cross-project relationships. Prefix external page links with the project ID in prose, for example:

```markdown
[Gateway requirements](../claude-code-proxy/requirements.md)
```

Run `ld sync --all` after adding or moving pages. It regenerates the portfolio and project index blocks and fails on dangling identifiers.
