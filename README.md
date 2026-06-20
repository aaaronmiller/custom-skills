# Custom Skills

[![GitHub stars](https://img.shields.io/github/stars/aaaronmiller/custom-skills?style=flat-square)](https://github.com/aaaronmiller/custom-skills)

Aggregate collection of user-created agent skills for Claude Code, Codex, Hermes, and other CLI agents.

50+ skills covering: task orchestration, deliberative refinement, goal loops, memory systems, security audits, frontend design, viral content generation, and more.

## Usage

Skills are markdown files in `SKILL.md` format. Install to your agent's skills directory:

```bash
# Clone into your agent's skills directory
cp -r skills/ ~/.claude/skills/
```

Or use the included `install.sh` to symlink all skills automatically.

## Highlights

| Skill | Description |
|---|---|
| deliberative-refinement | Multi-round AI self-critique with adversarial pressure |
| create-viral-content | Optimize posts for social media engagement |
| goal-loop | Iterative task completion with quality gates |
| frontend-design-masterclass | Premium UI/UX patterns for SvelteKit/Bun |
| security-audit | Comprehensive vulnerability assessment |

Synced via master-user-skills → agents/skills bridge, then skillshare propagates to all CLI targets.

Skills with their own repos live in `aaaronmiller/master-user-skills`.
