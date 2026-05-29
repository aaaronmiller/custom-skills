# Data Visualization Reference

Implementation patterns for making charts, tables, and dashboards that look like editorial
infographics rather than Excel exports. Built around LayerChart (the Svelte-native standard)
and shadcn-svelte's table components.

## Chart Stack Architecture

### LayerChart (Primary)
LayerChart is a composable Svelte chart library built on Layer Cake. It provides unopinionated
SVG/Canvas/HTML components: Bar, Area, Stack, Scatter, Pie, Arc, Sunburst, Treemap, Sankey,
Choropleth, and more. shadcn-svelte's chart component is literally built on LayerChart.

**Why LayerChart wins for this stack:**
- Native Svelte 5 support (v2+)
- Composable architecture: mix SVG, Canvas, and HTML layers in one chart
- Built on Layer Cake's scale system (auto-syncs with container dimensions)
- Full access to SVG primitives for custom styling
- Works seamlessly with shadcn-svelte's `Chart` wrapper components

### Integration with shadcn-svelte

shadcn-svelte provides Chart wrapper components that use LayerChart under the hood without
abstracting it away. You get `ChartTooltip`, `ChartLegend`, and theme-aware CSS variables:

```css
:root {
  --chart-1: oklch(0.646 0.222 41.116);
  --chart-2: oklch(0.6 0.118 184.704);
  --chart-3: oklch(0.398 0.07 227.392);
  --chart-4: oklch(0.828 0.189 84.429);
  --chart-5: oklch(0.769 0.188 70.08);
}
.dark {
  --chart-1: oklch(0.488 0.243 264.376);
  --chart-2: oklch(0.696 0.17 162.48);
  --chart-3: oklch(0.769 0.188 70.08);
  --chart-4: oklch(0.627 0.265 303.9);
  --chart-5: oklch(0.645 0.246 16.439);
}
```

Override these variables to match the 2+1 color system from the main skill.

## Making Charts Pop: The "Data Art" Techniques

### Gradient Area Fills
Never use solid fills under line charts. Apply SVG `<linearGradient>` fading from the
accent color at 50% opacity to transparent at the bottom:

```svelte
<defs>
  <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="var(--accent)" stop-opacity="0.5" />
    <stop offset="100%" stop-color="var(--accent)" stop-opacity="0" />
  </linearGradient>
</defs>
```

### Line Glow Effect
Apply an SVG filter behind the main data line for a neon glow:

```svelte
<defs>
  <filter id="glow">
    <feGaussianBlur stdDeviation="3" result="blur" />
    <feMerge>
      <feMergeNode in="blur" />
      <feMergeNode in="SourceGraphic" />
    </feMerge>
  </filter>
</defs>
```

Use `filter="url(#glow)"` on the line path. Especially effective on dark themes with
neon accent colors.

### Custom Data Points
Replace default circles with contextual SVG shapes:
- Diamonds for financial data
- Squares for discrete categories
- Small icons for domain-specific data (e.g., weather symbols for temperature charts)
- Filled shapes with white stroke on dark backgrounds

### Grid Replacement
Remove standard axis grid lines. Replace with:
- Subtle dot patterns (`stroke-dasharray="1 8"` with 0.1 opacity)
- No grid at all (let the data speak)
- Horizontal-only dashed lines (`stroke-dasharray="4 4"`, opacity 0.08)

### Interaction Patterns

**Crosshair tooltip**: A vertical line tracking mouse X-position across the full chart
width. All series values at that X position display in a floating tooltip panel.

**Focus mode**: When hovering a data point, dim all other series to `opacity: 0.15`.
Isolates the active series visually.

**Custom tooltip**: Never use default browser tooltips. Render a `position: fixed` div
that follows mouse coordinates. Style with `backdrop-filter: blur(8px)`, the glassmorphic
treatment from the visual-kinetics reference.

## Chart Aesthetic Modes

### "Neon" (Dark Theme)
- Lines: `stroke-width: 2.5`, color: accent
- Glow filter applied
- Area: gradient from accent/50 to transparent
- Grid: dashed, 0.08 opacity
- Axis labels: mono font, muted color
- Background: deep charcoal or navy

### "Editorial" (Light Theme)
- Lines: solid, thick black (`stroke: #000; stroke-width: 2`)
- Area: solid muted fill or hatching patterns
- Points: custom shapes, white fill, thick black stroke
- Axis labels: serif font (e.g., Instrument Serif)
- Grid: thin horizontal rules only

### "Minimal" (Either Theme)
- Single metric, large number display
- Sparkline (tiny inline chart) with no axes
- Accent color line only, no fills
- Ultra-clean, dashboard KPI style

## Table Styling (shadcn-svelte)

shadcn-svelte provides headless table components. Style them aggressively to match
the design system.

### Visual Treatment
- Remove all vertical borders. Keep horizontal separators as `border-b border-white/10`
- Sticky header: `backdrop-filter: blur(12px); background: var(--base)/80`
- Zebra striping: NOT with color blocks. Use `background: color-mix(in srgb, var(--bg), var(--fg) 2%)` on alternating rows for subtle texture
- Row hover: `bg-accent/8` with smooth transition
- Cell padding: Generous (`px-4 py-3` minimum)

### Status Indicators (Geometry Over Text)
Replace text labels ("Active", "Pending", "Error") with visual indicators:
- Active: `w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_theme(colors.emerald.500)]` (glowing dot)
- Pending: `w-2 h-2 rounded-full bg-amber-500 animate-pulse`
- Error: `w-2 h-2 rounded-full bg-red-500`
- Inactive: `w-2 h-2 rounded-full bg-zinc-600` (no glow)

### Sortable Column Headers
Active sort column gets the accent color underline. Sort direction arrow uses a subtle
CSS transition to flip.

## Dashboard Layout: Bento Grids

Use CSS Grid for asymmetric, visually interesting dashboard layouts.

### Structure Pattern
```css
.dashboard {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  grid-template-rows: auto;
  gap: 1.5rem;
}
.metric-card { grid-column: span 1; }
.main-chart { grid-column: span 3; grid-row: span 2; }
.sidebar-list { grid-column: span 1; grid-row: span 2; }
.wide-table { grid-column: span 4; }
```

### Card Treatment
- Borders: `border border-white/5` (dark) or `border border-zinc-200` (light)
- Background: subtle gradient `bg-gradient-to-br from-white/5 to-transparent`
- Padding: `p-6` for breathing room
- Data hierarchy: Big number `text-4xl font-bold`, small label `text-xs uppercase tracking-widest text-muted`

## Sparklines

For inline mini-charts (in table cells, metric cards, or next to KPI numbers):
Use LayerChart's composable API with minimal configuration. No axes, no grid, no labels.
Just a single SVG path with the accent color and optional area gradient below.

Height: 32-48px. Width: fills container.

## Real-Time Data Visualization

For live-updating charts (token latency, server metrics, stock prices):
- Use Svelte's `$state` to hold the data array
- Push new data points and shift old ones with `$effect`
- Smooth transitions via LayerChart's built-in transition support or CSS
- "Heartbeat" sparkline: Neon green line on dark background with a subtle horizontal
  "scanline" animation overlay for a monitoring-terminal aesthetic

## Fallback Libraries

When LayerChart's composable approach is too low-level for a quick prototype:
- **Apache ECharts**: Framework-agnostic, feature-rich. Wrap in a Svelte component via `onMount`. Good for complex interactions (brush selection, data zoom). Not Svelte-native.
- **Unovis**: Modular, CSS-variable-driven theming, TypeScript-first, framework-agnostic with Svelte wrapper. Good for custom design systems that avoid Tailwind.
- **Lightweight Charts**: TradingView's library. Best for financial time-series (candlestick, area, baseline). Wrap via `onMount`.

LayerChart remains the primary choice for this stack due to native Svelte integration
and shadcn-svelte alignment.
