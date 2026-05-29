# UI/UX Doctor

Diagnose, audit, and improve existing user interfaces. This skill reviews, fixes, and elevates what already exists rather than creating from scratch.

## What This Skill Does

Provides 10 operating modes for UI/UX analysis: full audits across 8 quality dimensions, UX anti-pattern scanning against a 99-item database, stack-specific best practices, style discovery and migration advice, accessibility compliance reports, design token extraction, competitive analysis, and pre-ship QA checklists.

## When Claude Uses This Skill

Activates when you ask Claude to review, audit, fix, improve, check, or diagnose an existing interface. Also triggers on accessibility audits, UX issue identification, style modernization, and pre-launch quality checks. Does NOT trigger for building new interfaces from scratch (use frontend-design-masterclass for that).

## Companion Skills

Part of a coordinated skill library. Each operates independently:
- **frontend-design-masterclass**: Build new interfaces (SvelteKit/Bun/Hono)
- **humanize-writing**: Polish UI copy for human voice
- **create-viral-content**: Optimize CTAs and marketing content
- **deliberative-refinement**: Iterative improvement with expert councils

## Operating Modes

| Mode | Trigger | Output |
|------|---------|--------|
| 1. UI Audit | "audit", "review", "evaluate" | Scored report across 8 dimensions |
| 2. UX Anti-Pattern Scan | "UX issues", "anti-patterns" | Do/Don't pairs with fixes |
| 3. Stack Best Practices | "best practices for React" | Framework-specific guidance |
| 4. Style Discovery | "what style should" | 2-3 style recommendations |
| 5. Quick Lookup | "what font for", "chart type" | Single-domain answer |
| 6. Pre-Ship QA | "ready to ship", "QA" | Pass/fail checklist |
| 7. Style Migration | "modernize", "feels dated" | Migration path with steps |
| 8. Competitive Analysis | "stand out from" | Differentiation strategy |
| 9. Accessibility Report | "a11y", "WCAG", "accessible" | WCAG compliance audit |
| 10. Design Tokens | "extract tokens", "tokenize" | design-tokens.json output |

## Structure

```
ui-ux-doctor/
  SKILL.md                    # Core instructions (10 modes, audit framework)
  README.md                   # This file
  LICENSE.txt                 # MIT License
  marketplace.json            # Claude Code plugin metadata
  references/
    ux-guidelines.md          # 99 anti-patterns across 18 categories
    styles.md                 # Visual style database with migration paths
    products.md               # Product type to style mapping
    colors.md                 # Color palettes by mood and industry
    typography-ref.md         # 57 font pairings with use-case mapping
    charts.md                 # 25 chart types with selection guide
```

## Installation

### Claude.ai (web)
Package as ZIP, upload via Settings > Capabilities > Upload Skill.

### Claude Code
```bash
cp -r ui-ux-doctor ~/.claude/skills/
```

## License

MIT
