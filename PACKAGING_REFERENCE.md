# Skill Packaging Quick Reference

## Format Specification

```bash
skill-name/
├── SKILL.md              # Required: Main instructions
├── resources/           # Optional: Reference docs
└── scripts/             # Optional: Helper tools
```

## SKILL.md Template

```yaml
---
name: your-skill-name
description: What it does & when to use it
license: MIT
metadata:
  author: your-name
  version: "1.0"
  tools: [Read, Write, Edit, Grep, Glob]
---

# Your Skill Name

## Quick Start
[2-3 sentence usage]

## Detailed Instructions
[Comprehensive guide]

## Examples
[Concrete examples]
```

## Packaging Commands

```bash
# Create .skill file
zip -r skill.skill skill/ -x "*.DS_Store" "*.git*"

# Or using tar
tar -czf skill.skill skill/ --exclude='.git' --exclude='.DS_Store'

# Verify structure
unzip -l skill.skill
```

## Installation

```bash
# Claude Code
/plugin add /path/to/skill.skill
/plugin add https://github.com/user/repo

# Claude.ai
# Settings → Capabilities → Skills → Upload
```

## Quality Checklist

- [ ] YAML starts with `---`
- [ ] name: lowercase with hyphens
- [ ] description: under 1024 chars
- [ ] Instructions < 500 lines
- [ ] No absolute paths
- [ ] All files in skill/ directory
- [ ] Scripts have +x permissions
- [ ] Excludes .git, .DS_Store, node_modules

## Example: Frontend Design Skill

```yaml
---
name: frontend-design-shadcn
description: Create distinctive React UIs with shadcn/ui, modern patterns, and accessibility
license: MIT
metadata:
  author: team-name
  version: "2.0"
  tools: [Read, Write, Edit, Glob, Grep, Bash]
---

# Frontend Design Skill

## Activation
Use when: "Build a frontend", "Create React component", "Design dashboard"

## Core Instructions
1. Ask user for shadcn preferences (style, theme, icons)
2. Use `npx shadcn create` for project setup
3. Follow modern React 19 patterns
4. Optimize for Core Web Vitals
5. Apply deliberative refinement validation

## Key Features
- Modern shadcn setup (npx shadcn create)
- React 19 + TypeScript
- WCAG 2.2 AA accessibility
- Performance optimization
- Distinctive aesthetics
```

## Self-Improving Skills

Add learning capability:
```markdown
## Learning Protocol

After sessions with user corrections:
1. Note specific feedback patterns
2. Run autoskill to extract insights
3. Validate changes via deliberative refinement
4. Apply improvements with Git commits
5. Track success metrics

See `autoskill/SKILL.md` for complete framework.
```

## Current Project Skills

**Available for reference:**
- `frontend-design-shadcn/` - Modern frontend development
- `autoskill/` - Self-improving learning system
- `deliberative-refinement/` - Quality validation framework

**Quick usage:**
```bash
# Install existing skills
/plugin add /Users/macuser/git/0MY_PROJECTS/skills/Claude-Skills/frontend-design-shadcn
/plugin add /Users/macuser/git/0MY_PROJECTS/skills/Claude-Skills/autoskill
```

## Distribution Methods

### 1. GitHub Repository (Recommended)
```
Repository: yourname/skill-name
Contents: SKILL.md + optional resources
Install: /plugin add https://github.com/yourname/skill-name
```

### 2. Direct .skill File
```
Share: Email, cloud storage, downloads
Install: /plugin add /path/to/skill.skill
```

### 3. Future Marketplace
```
Submit: marketplace portal (when available)
Benefits: Discovery, ratings, updates
```

## Security Notes

**Skills can:**
- Read/write files
- Execute commands (if Bash allowed)
- Search the web
- Access system resources

**Always:**
- Review code before installing
- Check allowed tools in metadata
- Verify source is trusted

## Validation Command

```bash
#!/bin/bash
# validate-skill.sh

DIR="$1"
[ -f "$DIR/SKILL.md" ] || { echo "❌ Missing SKILL.md"; exit 1; }

# Check YAML format
grep -q "^---" "$DIR/SKILL.md" || { echo "❌ Invalid YAML"; exit 1; }

# Check name format
NAME=$(grep "^name:" "$DIR/SKILL.md" | cut -d' ' -f2)
[[ $NAME =~ ^[a-z0-9-]+$ ]] || { echo "❌ Invalid name format"; exit 1; }

# Check line count
LINES=$(wc -l < "$DIR/SKILL.md")
if [ "$LINES" -gt 500 ]; then
  echo "⚠️  SKILL.md is long ($LINES lines). Consider splitting."
fi

echo "✓ Skill validation passed"
```

## Current Status

- **Official Marketplace**: Expected Q1 2026
- **Current Best Practice**: GitHub repositories
- **Standard**: agentskills.io open specification
- **Examples**: See skills in this repository

## Next Steps

1. **Package your skill** following the template
2. **Test thoroughly** with real scenarios
3. **Create GitHub repo** for distribution
4. **Document with examples**
5. **Monitor for marketplace launch**

---

**For detailed guidance, see**: `SUBMISSION_GUIDE.md`