# Data Graphics Reference

Deep implementation patterns for tables, charts, Mermaid diagrams, illustrations,
infographic-style visuals, and AI-generated data graphics. How to make data beautiful
and prompt AI tools to create publication-quality visuals.

## Table of Contents

1. Table Design Beyond Defaults
2. Chart Aesthetics and Storytelling
3. Mermaid Diagram Styling
4. Infographic Design Patterns
5. AI Image Prompting for Data Visuals
6. Illustration Integration
7. Print-Ready Data Graphics

---

## 1. Table Design Beyond Defaults

### The No-Grid Table

Remove all vertical borders and minimize horizontal rules. Data alignment and spacing
create the structure, not grid lines.

```css
.table-clean {
  width: 100%;
  border-collapse: collapse;
  font-variant-numeric: tabular-nums; /* Align numbers in columns */
}
.table-clean th {
  text-align: left;
  font-weight: 600;
  font-size: var(--text-sm);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-secondary);
  padding: 0.75rem 1rem;
  border-bottom: 2px solid var(--border-strong);
}
.table-clean td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--border-default);
}
.table-clean tr:last-child td {
  border-bottom: none;
}
.table-clean tr:hover {
  background: hsl(var(--primary-hue), 10%, 50%, 0.04);
}
```

### Status Indicators (Geometry Over Words)

Replace text status labels with visual indicators:

```svelte
<!-- Glowing status dot -->
<span
  class="status-dot"
  class:active={status === 'active'}
  class:pending={status === 'pending'}
  class:error={status === 'error'}
></span>

<style>
  .status-dot {
    display: inline-block;
    width: 8px; height: 8px;
    border-radius: 50%;
    background: var(--text-tertiary);
  }
  .status-dot.active {
    background: hsl(145, 60%, 45%);
    box-shadow: 0 0 8px hsl(145, 60%, 45%, 0.5);
  }
  .status-dot.pending {
    background: hsl(40, 70%, 50%);
    animation: pulse 2s ease-in-out infinite;
  }
  .status-dot.error {
    background: hsl(0, 60%, 50%);
  }
</style>
```

### Sparkline Cells

Embed mini charts directly in table cells for trend data:

```svelte
<td class="sparkline-cell">
  <svg viewBox="0 0 100 24" class="sparkline">
    <polyline
      fill="none"
      stroke="var(--accent-default)"
      stroke-width="1.5"
      points={data.map((v, i) => `${(i / (data.length - 1)) * 100},${24 - (v / max) * 20}`).join(' ')}
    />
  </svg>
</td>
```

### Sticky Headers with Blur

```css
.table-sticky thead {
  position: sticky;
  top: 0;
  z-index: 10;
  backdrop-filter: blur(12px);
  background: hsl(var(--base-hue), var(--base-sat), var(--base-light), 0.85);
}
```

### Data Emphasis Techniques

- **Heat coloring**: Tint cell backgrounds based on value magnitude
  (green for high, red for low, or primary color at varying opacity)
- **Bar-in-cell**: Horizontal bar behind the number showing relative magnitude
- **Trend arrows**: SVG arrows (up/down/flat) color-coded next to values
- **Highlighted rows**: Accent-tinted background for rows meeting a condition
- **Expandable rows**: Click to reveal detailed sub-data with slide animation

---

## 2. Chart Aesthetics and Storytelling

### Chart as Narrative

Every chart should tell a story. Before building, answer:
- What is the single insight this chart communicates?
- What is the "so what" for the viewer?
- Which data points deserve emphasis (annotation, color, size)?

### Gradient Area Fills (The Standard)

Never use solid fills under line charts. Gradient from accent color to transparent:

```svelte
<defs>
  <linearGradient id="area-fill" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="var(--accent-default)" stop-opacity="0.4" />
    <stop offset="100%" stop-color="var(--accent-default)" stop-opacity="0" />
  </linearGradient>
</defs>
```

### Line Glow Effect (Dark Theme)

```svelte
<defs>
  <filter id="line-glow">
    <feGaussianBlur stdDeviation="3" result="blur" />
    <feMerge>
      <feMergeNode in="blur" />
      <feMergeNode in="SourceGraphic" />
    </feMerge>
  </filter>
</defs>
<path d={linePath} stroke="var(--accent-default)" filter="url(#line-glow)" />
```

### Annotation Patterns

Highlight key data points with callouts:

```svelte
<!-- Data point with annotation -->
<g transform={`translate(${x}, ${y})`}>
  <circle r="4" fill="var(--accent-default)" />
  <line y1="-8" y2="-30" stroke="var(--text-secondary)" stroke-dasharray="2 2" />
  <text y="-34" text-anchor="middle" class="annotation-text">
    Peak: {value}
  </text>
</g>
```

### Grid Replacement Strategies

Standard grid lines are visual noise. Replace with:
- **Dot grid**: `stroke-dasharray="1 8"` at 0.1 opacity
- **No grid**: let data lines and axes speak alone
- **Horizontal only**: dashed lines `stroke-dasharray="4 4"` at 0.06 opacity
- **Reference line**: single horizontal rule at a meaningful threshold value

### Chart Color Strategy

- Primary data series: `--accent-default`
- Secondary series: `--primary-default`
- Tertiary series: 40% opacity version of accent
- Comparison/baseline: `--text-tertiary` (muted, dashed line)
- Do NOT use more than 4 colors. If you have 5+ series, use progressive
  lightness steps of a single hue.

---

## 3. Mermaid Diagram Styling

For full Mermaid theming, see `mermaid-theming.md`. Key integration points:

### Embedding in Site Design

Mermaid diagrams should feel like part of the page, not an embedded iframe:

1. Render via `beautiful-mermaid` with site theme colors
2. Wrap in a styled container matching the card treatment
3. Add texture overlay (dot pattern or grain) for cohesion
4. Apply `drop-shadow` for depth
5. Responsive: set `max-width: 100%` with horizontal scroll for wide diagrams

### Diagram as Hero Element

For architecture or flow-focused pages, the diagram IS the hero:

```css
.diagram-hero {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  padding: 4rem;
  background: var(--base-200);
}
.diagram-hero :global(svg) {
  max-width: 900px;
  width: 100%;
  filter: drop-shadow(0 8px 24px rgba(0,0,0,0.12));
}
```

---

## 4. Infographic Design Patterns

Infographics combine data, icons, and narrative flow into a single visual.
They work best as standalone SVG compositions or structured HTML layouts.

### The Number Block

Large number + label + supporting context:

```svelte
<div class="stat-block">
  <span class="stat-number">4.2M</span>
  <span class="stat-label">Active Users</span>
  <span class="stat-context">+23% from last quarter</span>
</div>

<style>
  .stat-number {
    font-family: var(--font-display);
    font-size: var(--text-5xl);
    font-weight: 800;
    color: var(--accent-default);
    line-height: 1;
  }
  .stat-label {
    font-size: var(--text-sm);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-secondary);
  }
  .stat-context {
    font-size: var(--text-sm);
    color: hsl(145, 50%, 45%);
  }
</style>
```

### The Timeline Strip

Horizontal or vertical timeline with milestone markers:

```css
.timeline {
  display: flex;
  flex-direction: column;
  gap: 0;
  position: relative;
  padding-left: 2rem;
}
.timeline::before {
  content: '';
  position: absolute;
  left: 0.5rem;
  top: 0; bottom: 0;
  width: 2px;
  background: var(--border-default);
}
.timeline-item {
  position: relative;
  padding: 1.5rem 0;
}
.timeline-item::before {
  content: '';
  position: absolute;
  left: -1.75rem;
  top: 1.75rem;
  width: 12px; height: 12px;
  border-radius: 50%;
  background: var(--accent-default);
  border: 3px solid var(--base-100);
}
```

### The Comparison Grid

Side-by-side comparison of options/features:

```css
.compare-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2px;
  background: var(--border-default);
  border-radius: 0.75rem;
  overflow: hidden;
}
.compare-cell {
  background: var(--base-100);
  padding: 1.5rem;
}
.compare-header {
  background: var(--base-200);
  font-weight: 700;
  text-align: center;
}
```

### The Process Flow

Numbered steps with connecting lines:

Steps presented as numbered circles connected by dashed lines, each with a title
and brief description. Works both horizontally (desktop) and vertically (mobile).

---

## 5. AI Image Prompting for Data Visuals

### Infographic-Style Image Prompts

Generate custom data visualizations as images when SVG/code isn't sufficient.

**For abstract data backgrounds**:
```
Prompt: "Abstract data visualization artwork, flowing lines representing data streams,
gradient from [primary color] to [accent color] on [base color] background,
no text or numbers, ethereal and atmospheric, suitable as a website section background,
high resolution"
```

**For stylized charts**:
```
Prompt: "Artistic bar chart illustration in [style] aesthetic, using only [palette colors],
isometric perspective, soft shadows, no axis labels needed, decorative/illustrative
rather than functional, clean vector style"
```

**For process illustrations**:
```
Prompt: "Step-by-step process illustration showing [concept], numbered steps 1-4,
connected by flowing arrows, flat design with [color palette], icons representing
each step, no text, clean modern style suitable for web infographic"
```

### Nano Banana Prompting for Data Textures

**Chart background texture**:
```
Prompt: "Subtle dot matrix pattern, evenly spaced, monochromatic, seamless tileable,
appropriate as background for data visualization overlay"
```

**Infographic accent pattern**:
```
Prompt: "Geometric repeating pattern, triangles and circles, low contrast,
[accent color] on transparent, suitable for infographic section divider"
```

### Consistency Rules for Generated Visuals

- Generate a "style sheet" image first, then reference it for all subsequent generations
- Always specify: color palette, style (flat/3D/hand-drawn), intended placement
- Request "no text" for images that will have HTML text overlaid
- Request "high resolution, clean edges" for images used at large sizes
- For icons/illustrations: "consistent line weight, [X]px stroke"

---

## 6. Illustration Integration

### Icon Systems

Use a consistent icon library throughout. Recommended: Lucide, Phosphor, or Heroicons.

- Size: 20-24px for inline, 32-48px for feature blocks, 64-96px for hero elements
- Stroke width: match across all icons (typically 1.5-2px)
- Color: `currentColor` for theme-adaptive coloring
- Animation: subtle rotation, scale, or stroke-draw on hover/scroll

### Feature Illustrations

Larger illustrations for feature sections or empty states:

- Keep within the site's color palette (3-5 colors maximum)
- Consistent style: all flat, all isometric, all hand-drawn (pick one)
- Same level of detail across all illustrations
- SVG format for scalability and potential animation

### Hero Illustrations

For illustration-driven hero sections:

- Illustration should occupy 40-60% of the hero viewport
- Leave breathing room (don't fill every pixel)
- Animation: subtle parallax or gentle floating motion
- Ensure the illustration doesn't compete with the headline

---

## 7. Print-Ready Data Graphics

### SVG Charts for Print

SVG charts print at any resolution as vector. Ensure:

- `-webkit-print-color-adjust: exact` on chart containers
- Explicit `width` and `height` attributes on the SVG (not just CSS)
- `break-inside: avoid` on chart containers
- Remove interactive elements (tooltips, hover states) in print CSS
- Add axis labels that are hidden on screen but visible in print

### Table Print Optimization

```css
@media print {
  table { page-break-inside: auto; }
  tr { page-break-inside: avoid; }
  thead { display: table-header-group; } /* Repeat header on each page */
  .sparkline-cell, .status-dot { display: none; }
  td, th { border: 1px solid #ccc !important; }
}
```

### Infographic Export

For infographics that need to be shared as images:
- Build as a fixed-width HTML component (1200px for social sharing)
- Use `html2canvas` or Puppeteer to capture as PNG
- Include a 2x resolution version for high-DPI displays
- Add attribution/watermark in the bottom margin
