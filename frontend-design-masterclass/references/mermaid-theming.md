# Mermaid Theming Reference

Implementation patterns for rendering beautiful, site-integrated Mermaid diagrams.
Covers `beautiful-mermaid` (the preferred library), native Mermaid theming, SVG
post-processing, and SvelteKit component patterns.

## Library: beautiful-mermaid

`beautiful-mermaid` (by Craft/lukilabs) is the recommended renderer for this stack.

**Why it wins:**
- 15 built-in themes (Tokyo Night, Dracula, Nord, Catppuccin, GitHub, Monokai, etc.)
- Live theme switching via CSS custom properties (no re-render needed)
- Full Shiki VS Code theme compatibility (use any VS Code theme directly)
- Zero DOM dependencies (pure TypeScript)
- SVG and ASCII/Unicode dual output
- Ultra-fast (100+ diagrams in <500ms)

### Installation
```bash
bun add beautiful-mermaid
```

### Basic Usage
```typescript
import { renderMermaid, THEMES } from 'beautiful-mermaid';

const svg = await renderMermaid(diagramCode, THEMES['tokyo-night']);
```

### Custom Theme (Matching Site Palette)
```typescript
const siteTheme = {
  bg: 'var(--color-base)',      // or resolved hex
  fg: 'var(--color-text)',
  accent: 'var(--color-accent)', // for arrows and highlights
  muted: 'var(--color-muted)',   // for subdued labels
};

const svg = await renderMermaid(diagram, siteTheme);
```

For richer control, add optional fields: `surface`, `border`, `success`, `warning`, `error`.

### Live Theme Switching
After rendering, update CSS variables directly on the SVG element:
```javascript
svg.style.setProperty('--bg', '#282a36');
svg.style.setProperty('--fg', '#f8f8f2');
// Diagram updates immediately without re-rendering
```

### Shiki Integration
Extract colors from any VS Code theme:
```typescript
import { extractShikiColors } from 'beautiful-mermaid';
import tokyoNight from 'shiki/themes/tokyo-night';

const theme = extractShikiColors(tokyoNight);
const svg = await renderMermaid(diagram, theme);
```

## Native Mermaid Theming (Fallback)

When using Mermaid's built-in renderer (e.g., for static site generation or markdown
previews where beautiful-mermaid cannot be used):

### Available Looks (Mermaid v11+)
- `neo`: Modern, clean, current default
- `handDrawn`: Sketch-style via RoughJS
- `classic`: Traditional Mermaid appearance

Set via frontmatter in the diagram code:
```
---
config:
  look: neo
  theme: base
---
flowchart LR
  A --> B
```

### Theme Variables (base theme only)
Only the `base` theme accepts custom `themeVariables`. Map them to your site's CSS
variables at initialization time:

```javascript
import mermaid from 'mermaid';

function getCSSVar(name, fallback) {
  return getComputedStyle(document.documentElement)
    .getPropertyValue(name).trim() || fallback;
}

mermaid.initialize({
  startOnLoad: false,
  theme: 'base',
  themeVariables: {
    primaryColor: getCSSVar('--color-accent', '#3b82f6'),
    primaryTextColor: getCSSVar('--color-text', '#f8fafc'),
    primaryBorderColor: getCSSVar('--color-accent', '#3b82f6'),
    lineColor: getCSSVar('--color-muted', '#64748b'),
    secondaryColor: getCSSVar('--color-surface', '#1e293b'),
    tertiaryColor: getCSSVar('--color-base', '#0f172a'),
    edgeLabelBackground: getCSSVar('--color-surface', '#1e293b'),
    fontFamily: getCSSVar('--font-body', 'DM Sans, sans-serif'),
    fontSize: '14px',
  },
  look: 'neo',
});
```

**Critical**: `themeVariables` only accepts hex colors, not CSS variable references or
color names. Resolve variables to hex at runtime before passing.

## SVG Post-Processing

Mermaid outputs raw SVG. Treat it as a base layer to enhance.

### Texture Overlay
Wrap the rendered SVG in a container with `position: relative`. Add a `::after`
pseudo-element with a geometric noise or dot pattern:

```css
.mermaid-container {
  position: relative;
}
.mermaid-container::after {
  content: '';
  position: absolute;
  inset: 0;
  background-image: radial-gradient(circle, var(--color-muted) 1px, transparent 1px);
  background-size: 16px 16px;
  mix-blend-mode: overlay;
  opacity: 0.06;
  pointer-events: none;
}
```

### Drop Shadow
Apply CSS `filter: drop-shadow(0 4px 12px rgba(0,0,0,0.15))` to the SVG container
for subtle depth separation from the page background.

### Border Treatment
Wrap in a card-style container with the site's border and background tokens:
```css
.mermaid-card {
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  padding: 2rem;
  background: var(--color-surface);
  overflow: hidden;
}
```

### Dark Mode Adaptation
When switching between light and dark modes, Mermaid SVGs rendered with
`beautiful-mermaid` update automatically via CSS variables. For native Mermaid,
re-initialize with updated `themeVariables` or maintain two pre-rendered versions.

## SvelteKit Component Pattern

Create a reusable `<MermaidDiagram>` component:

```svelte
<script lang="ts">
  import { renderMermaid } from 'beautiful-mermaid';

  let { code, theme = undefined }: { code: string; theme?: object } = $props();
  let svgHtml = $state('');

  $effect(() => {
    renderMermaid(code, theme).then((svg) => {
      svgHtml = svg.outerHTML;
    });
  });
</script>

<div class="mermaid-container">
  {@html svgHtml}
</div>

<style>
  .mermaid-container {
    position: relative;
    border: 1px solid var(--color-border);
    border-radius: 0.75rem;
    padding: 1.5rem;
    background: var(--color-surface);
  }
  .mermaid-container :global(svg) {
    width: 100%;
    height: auto;
  }
</style>
```

## Diagram Type Styling Notes

### Flowcharts
- Use `neo` look for professional contexts
- Use `handDrawn` look for documentation, educational content, or casual aesthetics
- Node shapes: rounded rectangles for processes, diamonds for decisions, stadiums for start/end

### Sequence Diagrams
- Set `rightAngles: true` in config for cleaner lines
- Custom font via `themeVariables.fontFamily`
- Activation boxes benefit from the accent color as `actorBorder`
- Use `autonumber` for step numbering in technical documentation

### State Diagrams
- Map state colors to semantic meaning (green = active, amber = transitional, red = error)
- Use notes (`note right of State`) for annotations

### Gantt Charts
- Section colors should map to team/workstream identity
- Critical path highlighting via custom class assignments

## Print Considerations

Mermaid SVGs print cleanly at any resolution since they are vector graphics. Ensure:
- Container has `-webkit-print-color-adjust: exact` to preserve colors
- Remove the texture overlay pseudo-element in `@media print` (noise patterns waste ink)
- Set explicit `width` and `max-width` on the SVG to prevent overflow on A4/Letter
- Apply `break-inside: avoid` to prevent diagrams splitting across pages
