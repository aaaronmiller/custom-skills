# Color System Reference

Deep implementation patterns for building structured, theme-aware color palettes using
color theory principles. Every site gets a custom light theme, dark theme, and optional
accent themes that are mathematically harmonious and visually distinctive.

## Table of Contents

1. Color Theory Foundations
2. The Structured Palette Architecture
3. Palette Generation Workflow
4. Light Theme Construction
5. Dark Theme Construction
6. Theme Selector (Bonus Themes)
7. Semantic Color Tokens
8. CSS Custom Property System
9. Accessibility and Contrast
10. Anti-Patterns

---

## 1. Color Theory Foundations

### The Color Wheel and HSL

All palette work should be done in HSL (Hue, Saturation, Lightness) or OKLCH (perceptually
uniform). HSL is more intuitive for generation; OKLCH produces more visually consistent results.

- **Hue**: Position on the color wheel (0-360 degrees). 0=red, 120=green, 240=blue.
- **Saturation**: Color intensity (0%=gray, 100%=pure color).
- **Lightness**: Brightness (0%=black, 50%=pure color, 100%=white).

### Harmony Models (How to Pick Colors That Work Together)

**Complementary**: Two colors opposite on the wheel (180 degrees apart).
Maximum contrast. Use for primary + accent pairs. Example: Blue (220) + Orange (40).

**Split-Complementary**: One base color + two colors adjacent to its complement.
High contrast with more nuance. Example: Blue (220) + Yellow-Orange (30) + Red-Orange (10).

**Triadic**: Three colors equidistant (120 degrees apart).
Vibrant, balanced. Example: Blue (220) + Red (340) + Yellow (100).

**Analogous**: 2-3 colors adjacent on the wheel (within 30-60 degrees).
Harmonious, low contrast. Example: Teal (180) + Blue (210) + Indigo (240).

**Tetradic (Rectangle)**: Two complementary pairs.
Rich palette with many options. Example: Blue (220) + Orange (40) + Green (160) + Red (340).

### The 60-30-10 Rule

- **60%** Dominant: Background/canvas color. Sets the mood.
- **30%** Secondary: Surfaces, cards, borders. Creates depth.
- **10%** Accent: CTAs, highlights, active states. Creates focus.

---

## 2. The Structured Palette Architecture

Every site palette consists of exactly 3 color groups + semantic colors.
This replaces the "pick 5 random colors" approach with a systematic structure.

### Group A: Base Tones (The Canvas)

3 colors derived from a single hue at varying lightness levels.
These form the background layers of the site.

| Token | Role | Light Theme | Dark Theme |
|-------|------|-------------|------------|
| `--base-100` | Page background | Very light (L: 96-99%) | Very dark (L: 5-10%) |
| `--base-200` | Card/surface background | Light (L: 92-96%) | Dark (L: 10-16%) |
| `--base-300` | Elevated surface/hover | Medium-light (L: 86-92%) | Medium-dark (L: 16-22%) |

**Hue source**: NOT pure gray. Tint with the primary hue at very low saturation (S: 2-8%).
This prevents the "dead gray" look and gives subtle warmth or coolness.

Example for a blue-tinted base (H: 220):
- Light: `hsl(220, 6%, 97%)`, `hsl(220, 5%, 94%)`, `hsl(220, 4%, 90%)`
- Dark: `hsl(220, 15%, 8%)`, `hsl(220, 12%, 13%)`, `hsl(220, 10%, 18%)`

### Group B: Primary Tones (The Identity)

3 colors derived from the primary brand hue at varying saturation/lightness.
These carry the brand's visual identity.

| Token | Role | Characteristics |
|-------|------|----------------|
| `--primary-muted` | Backgrounds behind primary content | Low saturation (S: 15-30%), mid lightness |
| `--primary-default` | Primary buttons, links, active indicators | Full saturation, optimal contrast |
| `--primary-vivid` | Hover states, focus rings, emphasis | Higher saturation or slight hue shift |

**Hue selection**: Do NOT use pure purple (H: 270-280). It is the most overused AI-generated
color. Instead, shift toward:
- Indigo (H: 230-245) for depth and sophistication
- Teal (H: 170-190) for freshness and trust
- Coral (H: 10-20) for warmth and energy
- Emerald (H: 140-160) for nature and growth
- Amber (H: 35-50) for warmth and creativity
- Slate blue (H: 210-225) for calm professionalism

### Group C: Accent Tones (The Pop)

3 colors using a secondary hue chosen via color theory relationship to the primary.
These create contrast and visual interest.

| Token | Role | Characteristics |
|-------|------|----------------|
| `--accent-subtle` | Tags, badges, secondary indicators | Low opacity or muted version |
| `--accent-default` | Secondary CTAs, highlights, chart accents | Full saturation, distinct from primary |
| `--accent-bold` | Alert states, data visualization emphasis | Maximum impact version |

**Accent hue selection strategy** (based on primary hue):

1. **Complementary accent** (180 degrees away): Maximum contrast. Best for CTAs that
   must stand out from the primary color.
2. **Triadic accent** (120 degrees away): Vibrant but harmonious. Good for secondary
   navigation or chart colors.
3. **Split-complementary accent** (150-160 degrees away): Sophisticated contrast
   without the harshness of pure complementary.

---

## 3. Palette Generation Workflow

### Step 1: Choose Primary Hue

Start with the brand color or desired mood:
- Warm moods: Hue 0-60 (reds, oranges, yellows)
- Cool moods: Hue 180-260 (teals, blues, indigos)
- Neutral moods: Hue 100-120 or 280-320 with low saturation

### Step 2: Derive Accent Hue via Harmony Model

```
Primary Hue: 210 (slate blue)
Complementary accent: 210 + 180 = 30 (warm orange)
Triadic accent: 210 + 120 = 330 (magenta-rose)
Split-comp accent: 210 + 150 = 360/0 (warm red)
```

### Step 3: Generate Base Tones

Take the primary hue, reduce saturation to 3-8%, and create 3 lightness steps.

### Step 4: Generate Primary Scale

From the primary hue, create a 3-step scale: muted (S: 20%, L: adjusted for theme),
default (S: 60-80%, L: 45-55%), vivid (S: 90%+, L: 50-60%).

### Step 5: Generate Accent Scale

Same process as primary but with the accent hue.

### Step 6: Add Semantic Colors

Standard semantic colors (success, warning, error, info) should relate to the
palette through shared saturation levels or slight hue shifts toward the primary.

### Step 7: Verify Contrast Ratios

Every text/background combination must meet WCAG AA (4.5:1 body, 3:1 large text).

---

## 4. Light Theme Construction

Light themes use high-lightness backgrounds with dark text. The challenge is
creating depth and hierarchy without harsh shadows or pure white fatigue.

### Light Theme Principles

- Page background: NEVER pure white (#fff). Use `--base-100` with subtle tint.
  Examples: `hsl(40, 20%, 98%)` (warm ivory), `hsl(220, 14%, 97%)` (cool blue-gray).
- Text: NEVER pure black (#000). Use `hsl(primary-hue, 10%, 12-18%)`.
  This creates a softer reading experience with subtle color connection.
- Shadows: Use colored shadows, not pure gray/black.
  `box-shadow: 0 4px 20px hsl(primary-hue, 20%, 80%)` instead of `rgba(0,0,0,0.1)`.
- Borders: `hsl(primary-hue, 8%, 88%)` for subtle, tinted borders.
- Emphasis: Use heavier font weights AND color shifts (not just bold).
- Highlighting: Light-tinted backgrounds behind text
  (`background: hsl(primary-hue, 40%, 94%)`).

### Light Theme Specific Effects

- **Hard shadows** for neo-brutalist: `box-shadow: 4px 4px 0px var(--primary-default)`
- **Thin lines** as decorative elements: 1px borders at low opacity
- **Heavy typography** for hierarchy: use weight extremes (200 vs 800)
- **Color blocks** for section differentiation: alternate between `--base-100` and `--base-200`

---

## 5. Dark Theme Construction

Dark themes invert the lightness model but require additional care. Human eyes are
more sensitive to brightness differences in low-light conditions.

### Dark Theme Principles

- Page background: NEVER pure black (#000). Use `hsl(primary-hue, 10-20%, 6-10%)`.
  True black creates excessive contrast and "floating element" syndrome.
- Text: NEVER pure white (#fff). Use `hsl(primary-hue, 5%, 86-92%)`.
  Pure white on dark causes eye strain. `#E8E8E8` to `#EBEBEB` is the sweet spot.
- Surfaces: Create depth by stacking progressively lighter dark tones.
  Background < Card < Elevated card < Popover (each step: +4-6% lightness).
- Borders: `hsl(primary-hue, 8%, 18-22%)` or `rgba(255,255,255, 0.06-0.1)`.
  Borders are more important in dark themes for element separation.
- Shadows: Barely visible or replaced with subtle glows.
  `box-shadow: 0 0 20px rgba(accent-r, accent-g, accent-b, 0.15)`

### Dark Theme Specific Effects

- **Colored glows** instead of shadows: accent-colored `box-shadow` with blur
- **Reduced image brightness**: `filter: brightness(0.85)` on images to prevent glare
- **Neon accent treatment**: accent color at full saturation with glow filter
- **Gradient depth**: subtle `bg-gradient-to-b from-base-200 to-base-100` on cards
- **Highlighting**: accent-tinted backgrounds at very low opacity
  (`background: hsl(accent-hue, 50%, 50%, 0.08)`).

### Dark Theme Color Adjustments

Colors that work in light themes often fail in dark themes:
- Saturated colors on dark backgrounds appear to "vibrate." Reduce saturation by 10-20%.
- Blues and purples on near-black can disappear. Lighten by 10-15%.
- Warm accents (orange, yellow) glow naturally on dark. Use at lower saturation.
- Green on dark should shift toward cyan/teal for readability.

---

## 6. Theme Selector (Bonus Themes)

When a site offers a theme selector, generate 3-5 cohesive theme variants from the
base palette. Each theme redefines the CSS custom properties.

### Theme Generation Strategy

**Theme 1: Default Light** - The base light theme as designed.
**Theme 2: Default Dark** - The base dark theme as designed.
**Theme 3: High Contrast** - Maximize contrast for accessibility. Pure white/black
backgrounds, maximum saturation accent.
**Theme 4: Warm Variant** - Shift base hue +20-30 degrees toward warm. Rotate
accent accordingly. Reduces blue light, feels cozier.
**Theme 5: Cool Variant** - Shift base hue -20-30 degrees toward cool.
Feels more professional, technical.
**Theme 6: Monochrome** - Reduce all saturation to 0-5%. Accent becomes the only
color. Maximum editorial sophistication.

### CSS Theme Implementation

```css
:root, [data-theme="light"] {
  --base-100: hsl(220, 6%, 97%);
  --base-200: hsl(220, 5%, 94%);
  --base-300: hsl(220, 4%, 90%);
  --primary-default: hsl(220, 70%, 50%);
  --accent-default: hsl(40, 85%, 55%);
  --text-primary: hsl(220, 10%, 15%);
  --text-secondary: hsl(220, 8%, 45%);
}

[data-theme="dark"] {
  --base-100: hsl(220, 15%, 8%);
  --base-200: hsl(220, 12%, 13%);
  --base-300: hsl(220, 10%, 18%);
  --primary-default: hsl(220, 65%, 60%);
  --accent-default: hsl(40, 80%, 60%);
  --text-primary: hsl(220, 5%, 90%);
  --text-secondary: hsl(220, 5%, 60%);
}

[data-theme="warm"] {
  --base-100: hsl(30, 15%, 97%);
  --base-200: hsl(30, 12%, 93%);
  --primary-default: hsl(20, 75%, 52%);
  --accent-default: hsl(200, 70%, 50%);
  --text-primary: hsl(20, 15%, 12%);
}

[data-theme="mono"] {
  --base-100: hsl(0, 0%, 97%);
  --base-200: hsl(0, 0%, 93%);
  --primary-default: hsl(220, 70%, 50%); /* only color */
  --accent-default: hsl(220, 70%, 50%); /* same as primary */
  --text-primary: hsl(0, 0%, 10%);
}
```

### Theme Toggle Component (Svelte 5)

```svelte
<script>
  let theme = $state('light');
  const themes = ['light', 'dark', 'warm', 'cool', 'mono'];

  function setTheme(t) {
    theme = t;
    document.documentElement.setAttribute('data-theme', t);
    localStorage?.setItem('theme', t);
  }

  $effect(() => {
    const saved = localStorage?.getItem('theme');
    if (saved && themes.includes(saved)) setTheme(saved);
  });
</script>
```

---

## 7. Semantic Color Tokens

Beyond the 3-group palette, every site needs semantic colors for states and feedback.
These should be related to the palette through shared characteristics.

```css
:root {
  /* Success: green family, saturation matched to primary */
  --success-bg: hsl(145, 40%, 94%);
  --success-text: hsl(145, 60%, 30%);
  --success-border: hsl(145, 50%, 45%);

  /* Warning: amber family */
  --warning-bg: hsl(45, 50%, 94%);
  --warning-text: hsl(30, 70%, 28%);
  --warning-border: hsl(40, 60%, 50%);

  /* Error: red family */
  --error-bg: hsl(0, 45%, 95%);
  --error-text: hsl(0, 65%, 35%);
  --error-border: hsl(0, 55%, 50%);

  /* Info: blue family (can match primary if primary is blue) */
  --info-bg: hsl(210, 40%, 95%);
  --info-text: hsl(210, 60%, 30%);
  --info-border: hsl(210, 50%, 50%);
}

[data-theme="dark"] {
  --success-bg: hsl(145, 30%, 12%);
  --success-text: hsl(145, 50%, 65%);
  --success-border: hsl(145, 40%, 35%);
  /* ... mirror for warning, error, info with dark-appropriate lightness */
}
```

---

## 8. CSS Custom Property System

### Full Token Architecture

```css
:root {
  /* === Base canvas === */
  --base-100: /* page bg */;
  --base-200: /* surface bg */;
  --base-300: /* elevated surface */;

  /* === Text === */
  --text-primary: /* headings, main body */;
  --text-secondary: /* descriptions, metadata */;
  --text-tertiary: /* placeholders, disabled */;
  --text-inverse: /* text on primary/accent bg */;

  /* === Primary brand === */
  --primary-muted: /* soft bg tint */;
  --primary-default: /* buttons, links */;
  --primary-vivid: /* hover, focus */;

  /* === Accent === */
  --accent-subtle: /* tags, badges */;
  --accent-default: /* secondary CTA */;
  --accent-bold: /* emphasis, charts */;

  /* === Borders === */
  --border-default: /* standard borders */;
  --border-strong: /* active/focus borders */;

  /* === Shadows === */
  --shadow-sm: /* cards, subtle depth */;
  --shadow-md: /* popovers, dropdowns */;
  --shadow-lg: /* modals, overlays */;
}
```

---

## 9. Accessibility and Contrast

### WCAG Contrast Requirements

- Normal text (< 24px): 4.5:1 minimum contrast ratio
- Large text (24px+ or 18.66px+ bold): 3:1 minimum
- UI components and graphical objects: 3:1 minimum
- Focus indicators: 3:1 against adjacent colors

### Testing Tools

- Chrome DevTools: Inspect element -> Color picker shows contrast ratio
- WebAIM Contrast Checker: webaim.org/resources/contrastchecker
- OKLCH-based palette tools: oklch.com, huetone.ardov.me

### Common Pitfalls

- Light gray text on white background (fails AA)
- Accent color as text on a tinted background (check both themes!)
- Placeholder text too faint to read
- Disabled state indistinguishable from enabled

---

## 10. Anti-Patterns

- **The Default Purple**: `hsl(270, 70%, 55%)` is the single most overused color in
  AI-generated interfaces. NEVER use it as primary. Shift to indigo (230-245) or
  violet-blue (250-260) if you need that family.
- **The Purple-Blue Gradient**: Purple-to-blue gradients on white backgrounds are the
  #1 "this was AI-generated" tell. Half of all LLM models default to this exact scheme
  unprompted. If you see purple-blue gradient in your output, immediately replace with
  a palette derived from the product's actual brand or context.
- **The Rainbow Dashboard**: Using 8+ unrelated colors for chart series.
  Instead, use 3-4 shades/tints of 2 hues.
- **The Neon Assault**: Full-saturation colors everywhere. Reserve S:80%+ for
  the 10% accent allocation only.
- **The Gray Wasteland**: All grays with one blue link color. Add warmth or coolness
  to grays by tinting with the primary hue.
- **Theme Amnesia**: Building a light theme and bolting on a dark theme by
  inverting colors. Dark themes require independent design decisions (see Section 5).
