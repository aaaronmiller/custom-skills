# Resource File Audit (Corrected)

## How Resources Actually Work

Resource files (`references/`) are loaded when the model reads the SKILL.md body
and sees a directive to load them:

```markdown
For detailed patterns, see `references/patterns.md`.
```

The model decides to load the file because the SKILL.md body told it to.
**No YAML frontmatter descriptions are needed in reference files.**

## What to Check

### 1. Cross-Reference Integrity

SKILL.md says: `See references/patterns.md for details.`
→ `references/patterns.md` MUST exist.

```
for skill in skills/*; do
  refs=$(grep -oP 'references/[^\s\)\]]+' "$skill/SKILL.md" 2>/dev/null)
  for ref in $refs; do
    if [ ! -f "$skill/$ref" ]; then
      echo "MISSING: $skill/$ref"
    fi
  done
done
```

### 2. Filename Quality

Filenames should be descriptive enough for the model to understand the content:

| Good | Bad |
|------|-----|
| `troubleshooting.md` | `stuff.md` |
| `api-reference.md` | `notes.md` |
| `benchmark-guide.md` | `data.md` |
| `patterns.md` | `ref1.md` |

### 3. No Orphaned Files

Files in `references/` that are NOT referenced anywhere in SKILL.md should be
removed or referenced. Otherwise they're dead weight.

### 4. Content Placement

Content should be in the right file:
- Core instructions → SKILL.md body
- Deep detail, schemas, examples → references/
- Executable code → scripts/
- Output templates → assets/

If a reference file has content that should be in the SKILL.md body (core workflow),
move it. If SKILL.md is bloated with detail that belongs in references/, move that.

### 5. No Circular References

Ref A says: "See references/patterns.md"
Patterns says: "See references/troubleshooting.md"
Troubleshooting says: "See references/patterns.md"
→ Creates unnecessary loading. Keep references tree acyclic where possible.

## Summary

No frontmatter needed in reference files.
Check for: broken cross-refs, orphaned files, bad filenames, wrong content placement.
