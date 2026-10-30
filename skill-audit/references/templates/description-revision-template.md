# Description Revision Report Template

## Summary
- **Audit date**: YYYY-MM-DD
- **Total skills**: ____
- **Current total tokens**: ____
- **Realistic savings target**: ____ (without removing trigger coverage)

## Skills Needing TRIGGER COVERAGE (Add triggers — not shortening)

### Skills with NO trigger mechanism (urgent)

| # | Skill | Current Description | Missing |
|---|-------|-------------------|---------|
| 1 | | | "Use when:" and "Triggers:" |
| 2 | | | |

### Skills with weak trigger coverage

| # | Skill | Current Triggers | Suggested Additions |
|---|-------|-----------------|-------------------|
| 1 | | | |
| 2 | | | |

## Skills with Safe Trims (waste removal only)

Remove only version strings, URLs, and YAML artifacts. DO NOT strip trigger data.

```
skill-name (path):
BEFORE (XX): version: 1.0.0, full description with triggers intact
AFTER  (XX): full description with triggers intact
→ Savings: ~5 tokens | Removed version string (already in frontmatter)
```
