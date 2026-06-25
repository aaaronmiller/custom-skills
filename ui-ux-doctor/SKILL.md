---
name: auditing-ui-ux
description: "Audits and improves existing UI/UX. Triggers on: review, fix, audit, improve, check, redesign, accessibility, what's wrong, best practices, UX issues, style migration."
license: MIT
---

# UI/UX Doctor v1.0

Diagnose, audit, and improve existing interfaces. This skill modifies, repairs, and
elevates what already exists. It does not create from scratch.

## Companion Skills

This skill is part of a coordinated library. Each skill operates independently. Do
NOT load or invoke another skill mid-task. Instead, complete the current task fully,
then recommend the user pivot to the appropriate skill for the next phase.

Companion skills available to the user (reference only, never co-load):
- `frontend-design-masterclass`: Build new interfaces from scratch with SvelteKit/Bun/Hono.
  Recommend when audit reveals the interface needs a ground-up rebuild rather than fixes.
- `humanize-writing`: Polish written content for human voice. Recommend when UI copy
  reads as robotic or corporate.
- `create-viral-content`: Optimize content for engagement. Recommend when UI contains
  marketing copy, CTAs, or social-facing content that needs engagement optimization.
- `deliberative-refinement`: Run iterative improvement loops with virtual expert councils.
  Recommend after completing an audit when the user wants structured multi-round refinement
  of the fixes. Operates in three modes: expand, compress, or substitute (refine without
  changing token size).

Cross-skill protocol: Complete your audit or fix task fully. In the final summary,
note which companion skill would benefit the next phase. Example: "Audit complete.
The CTA copy could benefit from the create-viral-content skill for engagement
optimization." Never load companion skill content into this context.

## 1. Operating Modes

### Mode 1: UI Audit
Systematic quality scan across 8 dimensions. Produces a scored report.
Trigger: "audit", "review", "scan", "evaluate", "grade"

### Mode 2: UX Anti-Pattern Scan
Search for common UX violations against the anti-pattern database in
references/ux-guidelines.md. Output Do/Don't pairs with fix suggestions.
Trigger: "UX issues", "anti-patterns", "what's wrong", "pain points"

### Mode 3: Stack Best Practices
Load the appropriate stack reference from data/stacks/ and provide
framework-specific guidance for the user's actual tech stack.
Trigger: "best practices for [framework]", "React patterns", "Vue tips"

### Mode 4: Style Discovery
Search product/style databases to recommend 2-3 visual styles with rationale.
Uses references/styles.md and references/products.md.
Trigger: "what style should", "design direction", "visual identity"

### Mode 5: Quick Lookup
Single-domain search. Color palette for fintech. Font pairing for luxury.
Chart type for correlation data.
Trigger: "what color", "which font", "what chart type", "palette for"

### Mode 6: Pre-Ship QA
Run the full quality checklist adapted to the user's actual framework.
Produces pass/fail report with severity ratings.
Trigger: "pre-ship", "launch check", "QA", "ready to ship", "final review"

### Mode 7: Style Migration Advisor
Analyze current design language, recommend migration path to modern alternatives.
Flat design to modern. Bootstrap to Tailwind. Material to custom.
Trigger: "modernize", "migrate style", "update design", "feels dated"

### Mode 8: Competitive Style Analysis
Identify industry visual patterns, recommend differentiation strategies.
Cross-reference product type with style database.
Trigger: "competitors look like", "stand out from", "differentiate"

### Mode 9: Accessibility Compliance Report
WCAG audit combining UX guidelines with stack-specific a11y patterns.
Produces remediation checklist with priority levels.
Trigger: "accessibility", "a11y", "WCAG", "screen reader", "ADA"

### Mode 10: Design Token Extraction
Generate design-tokens.json from analyzed interface. Extract colors,
typography, spacing, shadows, radii into a portable token format.
Trigger: "extract tokens", "design tokens", "design system", "tokenize"

## 2. Intent Identification (Pre-Audit)

Before executing any mode, identify:

1. **What stack?** React / Next.js / Vue / Nuxt / Svelte / SvelteKit / Flutter /
   React Native / HTML-Tailwind / Other
2. **What product type?** SaaS / E-commerce / Fintech / Healthcare / Gaming /
   Portfolio / Admin Panel / Marketing / Media / Social
3. **What concern?** Visual quality / UX flow / Performance / Accessibility /
   Responsiveness / Style consistency / All
4. **What mode?** Map user intent to modes 1-10 above. If ambiguous, default
   to Mode 1 (full UI Audit).

### Product-Type Mapping

| Product Type | Expected Patterns | Common Issues |
|-------------|-------------------|---------------|
| SaaS | Swiss grid, muted palette, clear hierarchy | Feature creep, inconsistent density |
| E-commerce | Vibrant blocks, strong CTAs, trust signals | Visual noise, buried actions |
| Fintech | Data-dense, high contrast, number clarity | Over-decoration, poor number alignment |
| Healthcare | Calm palette, generous spacing, clear nav | Institutional coldness, poor mobile |
| Gaming | Dark themes, neon accents, immersive | Readability sacrifice, a11y neglect |
| Portfolio | Bold type, minimal chrome, curated grid | Self-indulgent animation, slow load |
| Admin | Dense data, collapsible panels, keyboard nav | Overwhelming density, no breathing room |
| Marketing | Hero-driven, scroll-reveal, social proof | Empty calories, slow paint, CLS |
| Media/News | Scan-friendly, clear typography hierarchy | Ad clutter, content displacement |
| Social | Feed-based, real-time, interaction-heavy | Infinite scroll fatigue, notification noise |

## 3. UI Audit Framework (Mode 1)

Score each dimension 1-5. Report as radar chart or table.

### 3A. Eight Audit Dimensions

**Typography** (weight: high)
- Heading hierarchy clear and consistent?
- Body text readable (16px+, 1.5+ line-height)?
- Font count <= 2 families?
- Responsive type scaling?

**Color** (weight: high)
- Palette cohesive (3-5 intentional colors)?
- Sufficient contrast ratios (AA minimum, AAA preferred)?
- Color never sole indicator of state?
- Dark/light mode handled consistently?

**Spacing** (weight: high)
- Consistent spacing scale (4px/8px base)?
- Adequate breathing room between sections?
- Content density appropriate to product type?
- Responsive spacing adjustments?

**Interaction** (weight: medium)
- Hover/focus/active states on all interactive elements?
- Loading states present?
- Error states informative and recoverable?
- Transitions under 300ms, purposeful?

**Accessibility** (weight: critical)
- Keyboard navigation complete?
- ARIA labels on dynamic content?
- Skip-to-content link present?
- Form inputs have visible labels (not just placeholders)?
- Focus indicators visible and styled?

**Responsive** (weight: high)
- Breakpoints tested at 320, 768, 1024, 1440?
- Touch targets 44px+ on mobile?
- No horizontal scroll on any breakpoint?
- Images responsive with proper srcset?

**Performance** (weight: medium)
- No layout shift (CLS < 0.1)?
- LCP element loads fast?
- Fonts loaded efficiently (swap/optional)?
- Images lazy-loaded below fold?

**Hierarchy** (weight: high)
- Primary action immediately identifiable?
- Visual flow guides eye logically?
- Information density matches product type?
- Secondary content clearly subordinate?

### 3B. Scoring Guide

| Score | Label | Meaning |
|-------|-------|---------|
| 5 | Excellent | Production-ready, exceeds standards |
| 4 | Good | Minor polish needed, functional |
| 3 | Adequate | Meets minimum, improvement recommended |
| 2 | Needs Work | Noticeable issues affecting UX |
| 1 | Critical | Broken or significantly harmful |

### 3C. Report Format

```
## UI Audit Report: [Component/Page Name]
Stack: [detected]  |  Product Type: [detected]  |  Date: [date]

| Dimension      | Score | Priority | Key Finding                    |
|---------------|-------|----------|-------------------------------|
| Typography     | ?/5   | P?       | [one-line finding]            |
| Color          | ?/5   | P?       | [one-line finding]            |
| Spacing        | ?/5   | P?       | [one-line finding]            |
| Interaction    | ?/5   | P?       | [one-line finding]            |
| Accessibility  | ?/5   | P?       | [one-line finding]            |
| Responsive     | ?/5   | P?       | [one-line finding]            |
| Performance    | ?/5   | P?       | [one-line finding]            |
| Hierarchy      | ?/5   | P?       | [one-line finding]            |

Overall: ??/40  |  Grade: [A/B/C/D/F]

### Critical Issues (fix immediately)
### Recommended Improvements (next sprint)
### Polish Items (nice to have)
### Companion Skill Recommendations
```

## 4. Anti-Slop Mandate

When suggesting fixes, NEVER recommend:
- Generic blue (#007bff) as primary color
- System font stack without intentional choice
- opacity-50 placeholders as "minimalist design"
- Card grids with uniform 1rem gap and no hierarchy
- Emoji as icons in professional interfaces
- Layout-shifting hover transforms
- Light-mode glass effects under 30% opacity
- Muted text below gray-500 equivalent
- "Modern and clean" as design direction (meaningless)

## 5. Stack-Specific Guidance

When a stack is identified, read the corresponding file from data/stacks/:
- data/stacks/react.csv for React/Next.js
- data/stacks/vue.csv for Vue/Nuxt
- data/stacks/svelte.csv for Svelte/SvelteKit (PRIMARY - weight heavily)
- data/stacks/html-tailwind.csv for vanilla HTML + Tailwind
- data/stacks/react-native.csv for React Native
- data/stacks/flutter.csv for Flutter
- data/stacks/swiftui.csv for SwiftUI
- data/stacks/android.csv for Android/Jetpack Compose

Priority weighting: Svelte/SvelteKit guidance is most detailed. React/Next.js second.
All others treated equally.

## 6. Reference Files

Load these on-demand based on the active mode:

- references/ux-guidelines.md: 99 UX anti-patterns across 18 categories. Use for
  Mode 2 (Anti-Pattern Scan) and Mode 6 (Pre-Ship QA).
- references/styles.md: 58 visual styles with CSS keyword mappings. Use for
  Mode 4 (Style Discovery) and Mode 7 (Style Migration).
- references/products.md: 96 product types mapped to recommended styles. Use for
  Mode 4 and Mode 8 (Competitive Analysis).
- references/colors.md: 96 color palettes by mood and industry. Use for
  Mode 5 (Quick Lookup) and token extraction.
- references/typography-ref.md: 57 font pairings with use-case mappings. Use for
  Mode 5 and token extraction.
- references/charts.md: 25 chart types with data-type mappings. Use for Mode 5.

## 7. Pre-Delivery Checklist (Mode 6)

Before marking any fix task complete, verify:

**Visual Quality**
- [ ] No orphaned headings (heading always followed by content)
- [ ] Consistent border-radius across component family
- [ ] Shadow system uses max 3 elevation levels
- [ ] No raw hex colors (all from design tokens or CSS variables)
- [ ] Image aspect ratios maintained under all breakpoints

**Interaction**
- [ ] Every clickable element has cursor:pointer
- [ ] Disabled states visually distinct and non-interactive
- [ ] Form validation shows inline errors, not just alerts
- [ ] Loading skeletons match content layout shape
- [ ] Success/error states auto-dismiss or have explicit close

**Light/Dark Mode**
- [ ] Both modes tested, not just the default
- [ ] No hardcoded colors bypassing theme variables
- [ ] Shadows adjust for dark mode (softer, lower opacity)
- [ ] Images/illustrations work in both modes
- [ ] System preference detection with manual override

**Layout**
- [ ] No content wider than viewport at any breakpoint
- [ ] Sticky elements don't overlap content
- [ ] Footer reaches bottom on short-content pages
- [ ] Scroll containers have visible scroll indicators
- [ ] Grid/flex gaps consistent with spacing scale

**Accessibility**
- [ ] All images have alt text (decorative images use alt="")
- [ ] Color is never the sole indicator of state
- [ ] Focus order follows visual order
- [ ] All form inputs have associated labels
- [ ] Error messages reference the field by name

**Performance**
- [ ] No render-blocking resources above fold
- [ ] Fonts use display:swap or display:optional
- [ ] Below-fold images use loading="lazy"
- [ ] No CSS @import chains (use bundler)
- [ ] Animations use transform/opacity only (GPU-composited)
