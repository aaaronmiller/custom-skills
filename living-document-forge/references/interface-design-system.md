---
title: Obsidian Editorial Workbench design system
version: 1.0.0
---

# Interface design system

## Direction

The starter uses **Obsidian Editorial Workbench**: an editorial research surface fused with a restrained developer tool. It is dark-first, information-dense, calm under long reading sessions, and tactile without becoming theatrical.

This direction applies the local `frontend-design-masterclass` guidance for an Education/Docs plus Dashboard/Analytics product: editorial hierarchy first, data-dense governance views second, restrained cards only for real widgets, semantic theme tokens, visible focus states, and microanimations that clarify state instead of performing.

The visual language deliberately rejects:

- generic purple AI gradients;
- neon grids and glowing robot imagery;
- glass on every surface;
- rounded cards around ordinary prose;
- ornamental gauges, brass, rivets, or fake machinery;
- endless entrance animations;
- low-contrast gray text on charcoal.

## Composition

Wide layout:

- 17–19rem section rail;
- fluid reading canvas constrained to a readable measure;
- 19–22rem contextual inspector;
- top command bar;
- thin reading-progress rail.

The reading canvas is primary. Rails support navigation and action without competing with the argument.

At medium widths, the inspector becomes a drawer. At narrow widths, both rails become independent drawers and the top bar collapses into essential controls.

## Surface hierarchy

Use rules, background steps, and spacing before containers.

- page canvas: deepest base;
- navigation rail: one step elevated;
- reading canvas: minimally elevated or contiguous;
- inspector: distinct border, not a floating glass slab;
- dashboard instruments: repeated interactive objects may use subtle bounded surfaces;
- dialogs: strongest elevation and focus isolation.

Corner radius is restrained: 4–10 px. Pills are reserved for compact status and tags.

## Typography

- Display and section headings: Iowan Old Style, Palatino Linotype, Charter, Georgia, serif.
- Interface and body: Aptos, Avenir Next, Segoe UI Variable, ui-sans-serif, system-ui, sans-serif.
- Data, IDs, shortcuts: IBM Plex Mono, SFMono-Regular, Consolas, Liberation Mono, ui-monospace, monospace.

The starter intentionally avoids remote webfont loading so the example has no hidden network dependency. Production deployments may add self-hosted fonts when licensing and performance budgets are clear.

Use sentence case. Uppercase is limited to tiny eyebrows and keyboard labels. Body measure should stay near 68–76 characters.

## Palette architecture

Every theme defines semantic tokens rather than component colors:

- canvas, rail, surface, elevated surface;
- text strong, text normal, text muted;
- rule, rule strong;
- primary, primary vivid, primary wash;
- accent, accent wash;
- success, warning, danger, info;
- focus ring, selection, shadow.

Themes:

1. `system`: chooses obsidian or paper from the OS preference.
2. `obsidian`: deep blue-black with mineral teal and amber annotations.
3. `graphite`: near-monochrome dark theme with a single cool accent.
4. `paper`: warm light editorial surface with ink text.
5. `high-contrast`: black/white surfaces with highly visible focus and semantic colors.

Dark and light themes are independently tuned. Do not derive paper by inverting obsidian.

## Dashboard styling

The dashboard is a workbench, not a marketing bento grid.

- Use a strong current-focus band.
- Present metrics as aligned instruments with shared baselines.
- Use one compact decision queue.
- Show document health as labeled checks, not decorative charts.
- Keep section status distribution textual or bar-based and accessible.
- Avoid duplicating the full document outline.

## Controls

Every control needs default, hover, active, focus-visible, and disabled states.

Tactile feedback:

- hover: small luminance shift or 1 px lift;
- press: 1 px downward translation and slight scale reduction;
- selected navigation: sliding rail marker;
- save: brief success flash and toast;
- theme change: token transition or progressive view transition;
- dialog: short fade and 4–8 px settle.

Do not animate width, height, layout position, or large reading surfaces during ordinary edits.

## Motion tokens

Required custom properties:

```css
--duration-instant: 60ms;
--duration-fast: 110ms;
--duration-normal: 190ms;
--duration-enter: 240ms;
--duration-exit: 160ms;
--ease-enter: cubic-bezier(0.2, 0, 0, 1);
--ease-exit: cubic-bezier(0.3, 0, 0.8, 0.15);
--ease-standard: cubic-bezier(0.2, 0, 0, 1);
--ease-tactile: cubic-bezier(0.34, 1.2, 0.64, 1);
```

Full motion still stays subtle. Reduced motion removes transforms, scrolling effects, and nonessential transitions while preserving instant state changes.

## Accessibility

- Maintain visible keyboard focus in every theme.
- Provide a skip link.
- Use landmarks and meaningful headings.
- Ensure drawers and dialogs manage focus.
- Provide text alongside status colors.
- Keep controls at least 40 px where practical.
- Respect OS and explicit motion preferences.
- Do not use color alone for proposal decisions or health state.
- Keep the document readable at 200% zoom without horizontal page scrolling.

## Theme-selector behavior

- Persist selection locally.
- Apply the theme before first paint when possible to prevent flashing.
- Let `system` update when the OS scheme changes.
- Set CSS `color-scheme` for native form controls.
- Use a native select in the reference starter for dependable keyboard behavior.
- Keep theme names visible; icons alone are insufficient.
