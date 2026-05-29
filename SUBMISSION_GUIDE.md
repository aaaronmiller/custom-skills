# Skill Marketplace Submission Guide

This guide provides comprehensive instructions for packaging and submitting skills to the Anthropic Claude marketplace, based on the latest research and official specifications.

## Current Marketplace Status (January 2026)

### Official Anthropic Marketplace
**Status**: In development - launch expected Q1 2026
- Skills can currently be distributed via GitHub repositories
- Plugin marketplace system exists for Claude Code
- Enterprise customers have managed distribution capabilities

### Community Marketplaces
- **claude-plugins.dev**: Community-maintained directory
- **agentskills.io**: Open standard specification (December 2025)
- **Direct distribution**: Via `.skill` files or GitHub repositories

## Skill Packaging Standards

### Directory Structure
```
skill-name/
├── SKILL.md              # Required: Main skill file
├── resources/           # Optional: Reference materials
│   ├── templates/
│   └── examples/
├── scripts/             # Optional: Executable helpers
│   └── validate.sh
└── .claude-skill        # Optional: Metadata file
```

### SKILL.md File Requirements

**1. YAML Frontmatter (Required)**
```yaml
---
name: skill-name
description: Clear description of capabilities and triggers
license: MIT                    # or Apache 2.0, Proprietary
metadata:
  author: your-name
  version: "1.0"
  tools: [Read, Write, Edit]    # Allowed tools
  context: fork                  # optional: isolation level
  model: claude-sonnet-4-20250514  # optional: model compatibility
  user-invocable: true           # optional: show in slash menu
---
```

**2. Instructions (Required)**
- Clear activation triggers
- Usage examples
- Guidelines and constraints
- No more than 500 lines (prefer 200-300)

### The .skill File Format

A `.skill` file is simply a ZIP archive with the skill directory structure.

**Packaging Commands:**

```bash
# Navigate to parent directory
cd /path/to/skill-parent

# Create .skill file (ZIP with .skill extension)
zip -r my-skill.skill my-skill/ \
  -x "*.DS_Store" "*.git*" "*.mdx" "*.test.*"

# Alternative using tar (better compression)
tar -czf my-skill.skill my-skill/ \
  --exclude='.git' --exclude='.DS_Store' \
  --exclude='node_modules' --exclude='*.test.*'

# Verify structure
unzip -l my-skill.skill
```

**Validation Checklist:**
- ✅ YAML frontmatter starts with `---`
- ✅ `name` field present (lowercase, hyphens, max 64 chars)
- ✅ `description` field present (max 1024 chars)
- ✅ Directory name matches skill name
- ✅ SKILL.md exists in root
- ✅ No extraneous files (README, package.json, etc.)
- ✅ Scripts have executable permissions
- ✅ File paths use forward slashes
- ✅ No absolute paths
- ✅ All external resources use relative paths

## Installation Methods

### For Claude Code Users
```bash
# Install from local directory
/plugin add /path/to/skill-directory

# Install from .skill file
/plugin add /path/to/skill.skill

# Install from GitHub repository
/plugin add https://github.com/username/skill-repo

# Install from marketplace (when available)
/plugin marketplace add username/skill-name
```

### For Claude.ai Users
1. **Settings** → **Capabilities** → **Skills**
2. Enable skills toggle
3. Click **"Upload skill"**
4. Select `.skill` file
5. Skill becomes available in conversations

### For Enterprise Teams
```bash
# Managed deployment via organization settings
/plugin deploy --org my-org --skill /path/to/skill.skill

# Centralized installation
/plugin install @company/design-system-skill
```

## Integration Patterns

### Reference Existing Skills
Our project contains two high-quality examples:

**1. frontend-design-shadcn (v2.0)**
- Modern frontend development with shadcn/ui
- Includes deliberative refinement integration
- Comprehensive performance guidelines
- **Location**: `/Users/macuser/git/0MY_PROJECTS/skills/Claude-Skills/frontend-design-shadcn/`

**2. autoskill (v3.0)**
- Self-improving learning system
- Git-based versioning
- Deliberative validation pipeline
- **Location**: `/Users/macuser/git/0MY_PROJECTS/skills/Claude-Skills/autoskill/`

### Copy Pattern from Deliberative Refinement
Both skills integrate the **deliberative refinement** framework:
- **V(5,3,1)** for standard validation
- **Pre-validation checklists** for quality gates
- **Confidence scoring** for change proposals

## Packaging Best Practices

### 1. Progressive Loading
Keep the base SKILL.md under 500 lines:
- **Metadata**: Always loaded (name, description)
- **Instructions**: Loaded when triggered
- **Resources**: Loaded only when needed

**Pattern:**
```markdown
# Skill Name

## Quick Start
[2-3 sentence usage guide]

## Detailed Instructions
[Link to external resources for deep dives]
- See `resources/guide.md` for comprehensive examples
- See `resources/api.md` for API reference
```

### 2. Tool Permissions
Specify allowed tools in metadata:
```yaml
tools: [Read, Write, Edit, Grep, Glob]
```
This prevents unnecessary permission prompts.

### 3. Context Isolation
```yaml
context: fork    # Run in isolated sub-agent
agent: general-purpose  # Agent type for forked context
```
Use for skills that need independent execution.

### 4. Hooks Integration
```yaml
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/security-check.sh $TOOL_INPUT"
          once: true
```
Add security scanning for risky operations.

## Advanced: Self-Improving Skills

### Integration with autoskill
Skills can be designed to improve themselves using the autoskill pattern:

**In your skill:**
```markdown
## Learning Mechanism

When users provide corrections or improvements:
1. Note the specific feedback
2. Run autoskill after the session
3. Propose updates to this skill
4. Use deliberative refinement to validate changes
```

**Benefits:**
- Skills evolve based on real usage
- Version tracking via Git
- Quality control via deliberative validation
- User satisfaction metrics

## Marketplace Submission Process (Expected)

### Phase 1: Preparation
1. **Package skill** following standards above
2. **Test thoroughly** across multiple scenarios
3. **Document clearly** with examples
4. **Add security review** for risky capabilities
5. **Version control** with Git

### Phase 2: Quality Assurance
1. **Self-validation** using deliberative refinement
2. **User testing** with target audience
3. **Peer review** from community
4. **Performance audit** for large skill files
5. **Accessibility check** for inclusive design

### Phase 3: Submission
1. **Upload to marketplace portal** (when available)
2. **Provide metadata**:
   - Category (Development, Design, Productivity, etc.)
   - Tags (React, TypeScript, etc.)
   - Compatibility (Claude versions)
   - Pricing (Free, Paid, Freemium)
3. **Submit for review**
4. **Respond to feedback**
5. **Publish and maintain**

### Phase 4: Maintenance
1. **Monitor usage metrics**
2. **Respond to user feedback**
3. **Update for new Claude features**
4. **Version bumps** for improvements
5. **Security patches** as needed

## Community Distribution (Current Best Practice)

### GitHub Repository Setup
```
your-skill/
├── .git/
├── SKILL.md              # Main skill file
├── resources/           # Documentation
├── examples/            # Usage examples
├── LICENSE              # License file
├── .gitignore
└── README.md           # For GitHub display
```

**README.md for GitHub:**
```markdown
# Skill Name

A brief description for humans.

## Installation

```bash
/plugin add https://github.com/username/skill-name
```

## Usage

[Examples and documentation]

## Development

[How to contribute/improve]
```

### Direct File Distribution
```bash
# Share .skill file via:
# - Email attachment
# - Cloud storage (Dropbox, Google Drive)
# - Shared team folders
# - Release page on GitHub

# Users install via:
/plugin add /path/to/downloaded.skill
```

## Security Considerations

### What Skills Can Do
Skills have access to:
- File system (Read, Write, Edit)
- Command execution (Bash)
- Web searches (WebSearch, WebFetch)
- Memory operations (via context)
- Tool orchestration

### Security Best Practices
1. **Audit all code** before installation
2. **Review allowed tools** in metadata
3. **Check for network operations**
4. **Examine file system access patterns**
5. **Verify no credential harvesting**

### Risk Categories
- **Low Risk**: Read-only operations, data analysis
- **Medium Risk**: File modifications, web searches
- **High Risk**: Command execution, network calls
- **Critical**: Credential access, system modifications

**Skills should document their risk level and provide security guidelines.**

## Performance Optimization

### Skill File Size
- **Target**: < 1000 lines for SKILL.md
- **Resources**: Move large examples to separate files
- **Images**: Use external URLs, not embedded
- **Dependencies**: No package.json or external deps

### Loading Performance
- **First load**: Metadata only (~100 tokens)
- **Trigger load**: Full SKILL.md (~5000 tokens)
- **Resource load**: On-demand only

### Context Management
```markdown
## Quick Reference

For most use cases, just follow these steps:
1. [Step 1]
2. [Step 2]
3. [Step 3]

**See `detailed-guide.md` for:**
- Advanced configurations
- Troubleshooting
- API reference
```

## Examples from Research

### Modern Patterns to Follow

**1. Humanize-Writing Skill**
- Automatic activation based on content type
- Comprehensive validation checklist (16-point)
- Progressive complexity (Lite/Standard/Deep)
- **Lesson**: Clear activation triggers reduce friction

**2. Create-Viral-Content Skill**
- Platform-specific optimization (Reddit, LinkedIn, etc.)
- Research-backed formulas with statistics
- Ethical framework with clear boundaries
- **Lesson**: Specific examples beat general principles

**3. Deliberative-Refinement Skill**
- Multi-round validation (V(8,3,1) standard)
- Agent-based critique system
- Anti-pattern avoidance warnings
- **Lesson**: Built-in validation improves quality

### Integration Opportunities

**Cross-skill collaboration:**
- `frontend-design-shadcn` ↔ `autoskill` (learning loop)
- `humanize-writing` ↔ `create-viral-content` (content polishing)
- `deliberative-refinement` ↔ `any skill` (quality assurance)

## Packaging for Different Platforms

### Claude Code Plugin
```bash
# Standard structure
my-skill/
└── SKILL.md

# Package
zip -r my-skill.skill my-skill/

# Install
/plugin add my-skill.skill
```

### Claude.ai Upload
```bash
# Same .skill file
# Upload via web interface
# Skill becomes available in conversations
```

### Enterprise Distribution
```bash
# Use managed settings
# Deploy via organization admin panel
# Centralized updates
```

### Future Marketplace
```bash
# Expected workflow:
# 1. Package skill
# 2. Submit to marketplace portal
# 3. Pass security review
# 4. Publish listing
# 5. Handle user feedback
```

## Checklist Before Submission

### Technical Requirements
- [ ] SKILL.md follows proper format
- [ ] YAML frontmatter complete
- [ ] Description includes trigger terms
- [ ] Instructions under 500 lines
- [ ] No broken links or missing files
- [ ] Scripts have correct permissions
- [ ] Package includes all necessary files
- [ ] No absolute paths or external dependencies

### Quality Standards
- [ ] Clear, actionable instructions
- [ ] Multiple usage examples
- [ ] Error handling documented
- [ ] Performance considerations addressed
- [ ] Accessibility guidelines followed
- [ ] Security implications documented
- [ ] Test cases provided
- [ ] User feedback incorporated

### Legal & Licensing
- [ ] License file included
- [ ] Third-party attributions documented
- [ ] Privacy policy for data handling
- [ ] Terms of use for users

### Packaging Validation
```bash
# Final validation script
#!/bin/bash

SKILL_DIR="./my-skill"
SKILL_FILE="my-skill.skill"

# Check required files
[ -f "$SKILL_DIR/SKILL.md" ] || { echo "Missing SKILL.md"; exit 1; }

# Validate YAML
grep -q "^---" "$SKILL_DIR/SKILL.md" || { echo "Invalid YAML frontmatter"; exit 1; }

# Check name format
NAME=$(grep "^name:" "$SKILL_DIR/SKILL.md" | cut -d' ' -f2)
[[ $NAME =~ ^[a-z0-9-]+$ ]] || { echo "Invalid name format"; exit 1; }

# Create package
zip -r "$SKILL_FILE" "$SKILL_DIR" -x "*.DS_Store" "*.git*"

echo "✓ Package ready: $SKILL_FILE"
```

## Support & Resources

### Official Documentation
- [Anthropic Skills Documentation](https://support.claude.com/en/articles/12512198-creating-custom-skills)
- [Agent Skills Open Standard](https://agentskills.io)
- [Claude Code Skills](https://code.claude.com/docs/en/skills)

### Community Resources
- **anthropics/skills**: Official examples repository
- **obra/superpowers**: Battle-tested community skills
- **Discord/Slack**: Skill development communities

### This Project Examples
- `frontend-design-shadcn/SKILL.md` - Modern frontend patterns
- `autoskill/SKILL.md` - Self-improvement framework
- `deliberative-refinement/SKILL.md` - Validation methodology

---

**Status**: This guide reflects the current state as of January 2026
**Next Update**: Check for marketplace launch announcements
**Feedback**: Open issues for improvements to this guide