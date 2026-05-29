# Typography System Reference

Deep implementation patterns for font selection, pairing, hierarchy, and typographic
systems that transform interfaces from readable to remarkable.

## Table of Contents

1. Font Selection Philosophy
2. Display Font Catalog
3. Body Font Catalog
4. Monospace Font Catalog
5. Font Pairing Strategies
6. Type Scale Construction
7. Responsive Typography
8. Variable Fonts
9. Loading and Performance
10. Typographic Details

---

## 1. Font Selection Philosophy

Typography carries more emotional weight than color. A font choice communicates
personality before a single word is read. The shape of letters triggers subconscious
associations built over centuries of print culture.

### The Character Test

Before selecting a font, check these distinguishing characters:
- **a, g**: Single-story or double-story? Double-story adds sophistication.
- **1, l, I**: Are they clearly distinguishable? Critical for readability.
- **0, O**: Can you tell them apart? Essential for data-heavy interfaces.
- **Q**: Does it have personality? The Q tail is a font's signature.

### The Context Matrix

| Context | Recommended Style | Weight Range | Why |
|---------|------------------|--------------|-----|
| SaaS dashboard | Geometric sans | 400-700 | Clean, functional, data-friendly |
| Editorial/blog | Serif display + sans body | 300-900 | Authority, reading comfort |
| Creative portfolio | Eclectic display + neutral body | 200-900 | Personality, contrast |
| E-commerce | Humanist sans | 400-700 | Friendly, trustworthy |
| Developer tool | Monospace + geometric sans | 400-700 | Technical precision |
| Luxury brand | High-contrast serif | 300-700 | Elegance, tradition |
| Startup MVP | Versatile sans family | 400-800 | Speed, flexibility |

---

## 2. Display Font Catalog (Headlines, H1-H3)

Organized by personality axis. Each entry includes Google Fonts availability,
key characteristics, and ideal pairing direction.

### Bold and Commanding

**Syne** (Google Fonts) - Geometric, wide, futuristic. Excellent for tech and creative.
Weights: 400-800. Pair with: DM Sans, Public Sans.

**Clash Display** (Fontsource) - Sharp, angular, high-impact. Modern editorial feel.
Weights: 200-700. Pair with: General Sans, Satoshi.

**Oswald** (Google Fonts) - Condensed, tall, industrial. Efficient use of horizontal space.
Weights: 200-700. Pair with: Source Sans 3, Quattrocento Sans.

**Bricolage Grotesque** (Google Fonts) - Quirky grotesque with optical sizing. Personality
without being unreadable. Weights: 200-800. Pair with: DM Sans, Inter (only if heavily
modified in weight/spacing).

**Cabinet Grotesk** (Fontsource) - Bold, friendly geometric with character. Stands out
from generic geometrics. Weights: 100-900. Pair with: General Sans, IBM Plex Sans.

### Elegant and Refined

**Instrument Serif** (Google Fonts) - Modern editorial serif with sharp contrast.
Feels like a luxury magazine. Weight: 400 (regular/italic only). Pair with: DM Sans, Satoshi.

**Fraunces** (Google Fonts) - Optical size axis gives it different personalities at
different sizes. Playful at small, authoritative at large. Weights: 100-900.
Pair with: Public Sans, DM Sans.

**Playfair Display** (Google Fonts) - High-contrast transitional serif. Classic editorial
workhorse. Weights: 400-900. Pair with: Source Sans 3, Lato.

**Crimson Pro** (Google Fonts) - Book-quality serif, excellent at body sizes too.
Scholarly and warm. Weights: 200-900. Pair with: Public Sans, IBM Plex Sans.

**Newsreader** (Google Fonts) - Modern news serif with excellent readability.
Designed for screen reading. Weights: 200-800. Pair with: DM Sans, Satoshi.

### Expressive and Unconventional

**Chakra Petch** (Google Fonts) - Thai-inspired geometric. Angular, techy, distinctive.
Weights: 300-700. Pair with: IBM Plex Mono, JetBrains Mono, DM Sans.

**Space Mono** (Google Fonts) - Monospace display with personality. Use for titles
in terminal/tech contexts. Weight: 400-700. Pair with: DM Sans, General Sans.
NOTE: Use sparingly. Do NOT default to this or Space Grotesk.

**Unbounded** (Google Fonts) - Variable width from condensed to expanded.
Futuristic and playful. Weights: 200-900. Pair with: Public Sans, Source Sans 3.

**Archivo Black** (Google Fonts) - Ultra-bold grotesque. Maximum impact for single words
or short phrases. Weight: 400 only. Pair with: anything clean.

---

## 3. Body Font Catalog (Paragraphs, UI Text)

Body fonts must be invisible. If a reader notices the body font, something is wrong.
Optimize for: large x-height, open counters, clear letterforms, comfortable at 16px.

**DM Sans** (Google Fonts) - Geometric sans with warmth. Slightly rounded terminals
make it friendlier than pure geometrics. Weights: 100-1000. The default recommendation
when unsure.

**General Sans** (Fontsource) - Grotesque with geometric influences. Professional,
neutral, versatile. Weights: 200-700.

**Public Sans** (Google Fonts) - USWDS typeface. Neutral, authoritative, excellent for
government/institutional contexts. Weights: 100-900.

**Satoshi** (Fontsource) - Modern geometric sans. Clean, balanced, works at all sizes.
Weights: 300-900.

**Source Sans 3** (Google Fonts) - Adobe's workhorse. Humanist construction aids
readability in long passages. Weights: 200-900. Variable font available.

**IBM Plex Sans** (Google Fonts) - Technical precision with human warmth. Includes
matching serif and mono companions. Weights: 100-700.

**Geist** (Fontsource) - Vercel's custom font. Modern, clean, designed for
developer-facing interfaces. Weights: 100-900.

---

## 4. Monospace Font Catalog (Code, Data, Terminal)

**JetBrains Mono** (Google Fonts) - Purpose-built for code. Ligatures for common
operators. Tallest x-height in class. Weights: 100-800.

**Fira Code** (Google Fonts) - Mozilla's coding font with ligatures. Excellent
Unicode coverage. Weights: 300-700.

**IBM Plex Mono** (Google Fonts) - Matches IBM Plex Sans. Slightly wider than
JetBrains, excellent for tabular data. Weights: 100-700.

**Geist Mono** (Fontsource) - Vercel's mono companion. Pairs perfectly with Geist Sans.
Weights: 100-900.

**Commit Mono** (Fontsource) - Neutral, anonymous mono. Lets code speak without font
personality interfering. Weight: 400-700.

---

## 5. Font Pairing Strategies

### The Contrast Principle

The best pairings create tension through difference. Pair fonts that share ONE common
trait (x-height, era, geometric structure) but differ in everything else.

**Serif display + Sans body** (most reliable):
- Instrument Serif + DM Sans
- Fraunces + Public Sans
- Playfair Display + Source Sans 3
- Crimson Pro + IBM Plex Sans
- Newsreader + Satoshi

**Geometric display + Humanist body**:
- Syne + Source Sans 3
- Cabinet Grotesk + IBM Plex Sans
- Clash Display + General Sans
- Bricolage Grotesque + DM Sans

**Display + Monospace** (editorial/tech hybrid):
- Any serif display + JetBrains Mono (for code blocks, data)
- Syne + IBM Plex Mono
- Fraunces + Fira Code

### The Three-Font System

For complex sites, use exactly three fonts with strict role assignments:

1. **Display** (H1-H2): The personality font. Bold, distinctive, memorable.
2. **Body** (H3-H6, paragraphs, UI): The workhorse. Clean, invisible, readable.
3. **Mono** (code, data, labels): The precision font. Technical, tabular.

Never use more than three font families. Never use fewer than two (unless
deliberately monochromatic as a design choice).

### Weight Contrast Rules

- Headlines: 700-900 weight (bold to black)
- Subheadings: 500-600 weight (medium to semibold)
- Body: 400 weight (regular)
- Captions/metadata: 300-400 weight (light to regular)
- NEVER use 400 vs 500 adjacent. The difference is too subtle. Jump at least 200 units.
- Size jumps should be 1.5x minimum between hierarchy levels. 3x+ between H1 and body.

---

## 6. Type Scale Construction

### Mathematical Scales

Build font sizes from a ratio applied to a base size (typically 16px).

| Scale Name | Ratio | Sizes (base 16px) | Feel |
|-----------|-------|-------------------|------|
| Minor Third | 1.200 | 16, 19, 23, 28, 33, 40 | Gentle, conservative |
| Major Third | 1.250 | 16, 20, 25, 31, 39, 49 | Balanced, versatile |
| Perfect Fourth | 1.333 | 16, 21, 28, 38, 50, 67 | Clear hierarchy |
| Augmented Fourth | 1.414 | 16, 23, 32, 45, 64, 90 | Dramatic, editorial |
| Golden Ratio | 1.618 | 16, 26, 42, 67, 109, 176 | Maximum drama |

### CSS Implementation

```css
:root {
  --text-xs: 0.75rem;    /* 12px - captions, labels */
  --text-sm: 0.875rem;   /* 14px - secondary text, metadata */
  --text-base: 1rem;     /* 16px - body text baseline */
  --text-lg: 1.25rem;    /* 20px - large body, H6 */
  --text-xl: 1.5625rem;  /* 25px - H5, card titles */
  --text-2xl: 1.953rem;  /* ~31px - H4, section headers */
  --text-3xl: 2.441rem;  /* ~39px - H3, major section titles */
  --text-4xl: 3.052rem;  /* ~49px - H2, page subtitles */
  --text-5xl: 3.815rem;  /* ~61px - H1, hero headlines */
  --text-6xl: 4.768rem;  /* ~76px - Display, maximum impact */
}
```

### Line Height by Size

Larger text needs tighter line-height. Smaller text needs more breathing room.

| Size Range | Line Height | Why |
|-----------|-------------|-----|
| Display (48px+) | 1.0 - 1.1 | Tight. Large text creates its own space. |
| Heading (24-48px) | 1.1 - 1.25 | Moderate. Keeps multi-line headings compact. |
| Body (14-20px) | 1.5 - 1.75 | Generous. Reading comfort over long passages. |
| Small (12-14px) | 1.4 - 1.6 | Moderate. Prevents cramping at small sizes. |

---

## 7. Responsive Typography

### Fluid Typography with `clamp()`

Sizes scale smoothly between breakpoints without media queries:

```css
h1 {
  font-size: clamp(2rem, 5vw + 1rem, 4.5rem);
  /* min: 32px, preferred: viewport-relative, max: 72px */
}

h2 {
  font-size: clamp(1.5rem, 3vw + 0.75rem, 3rem);
}

p {
  font-size: clamp(1rem, 0.5vw + 0.875rem, 1.125rem);
  /* Body text: 16px min, gentle scaling, 18px max */
}
```

### Breakpoint Adjustments

```css
/* Mobile: tighter spacing, smaller sizes */
@media (max-width: 640px) {
  :root {
    --heading-tracking: -0.01em;
    --body-line-height: 1.6;
  }
  h1 { letter-spacing: -0.02em; }
}

/* Desktop: can afford more dramatic sizing */
@media (min-width: 1024px) {
  :root {
    --heading-tracking: -0.03em;
    --body-line-height: 1.7;
  }
}
```

---

## 8. Variable Fonts

Variable fonts contain multiple weight/width/slant axes in a single file, reducing
HTTP requests and enabling smooth weight animations.

### Key Variable Font Families

- **DM Sans** - Weight axis (100-1000), Optical size
- **Fraunces** - Weight, Optical size, Softness, Wonk
- **Source Sans 3** - Weight, Optical size, Width (italic)
- **Bricolage Grotesque** - Weight, Width, Optical size
- **JetBrains Mono** - Weight

### CSS Variable Font Syntax

```css
@font-face {
  font-family: 'DM Sans';
  src: url('/fonts/DMSans-Variable.woff2') format('woff2');
  font-weight: 100 1000;
  font-display: swap;
}

/* Smooth weight transitions on hover */
.nav-link {
  font-variation-settings: 'wght' 400;
  transition: font-variation-settings 0.2s ease;
}
.nav-link:hover {
  font-variation-settings: 'wght' 700;
}
```

---

## 9. Loading and Performance

### Font Loading Strategy

```html
<!-- Preload critical fonts -->
<link rel="preload" href="/fonts/display.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/body.woff2" as="font" type="font/woff2" crossorigin>
```

```css
/* font-display strategies */
@font-face {
  font-display: swap;    /* Show fallback immediately, swap when loaded */
  /* Use for body text - prevents invisible text */
}
@font-face {
  font-display: optional; /* Use font only if already cached */
  /* Use for decorative/display fonts on repeat visits */
}
```

### Self-Hosting vs CDN

Self-host fonts for production. Google Fonts CDN adds an extra DNS lookup and
potential privacy concerns. Download from Google Fonts or Fontsource, subset
to needed character ranges (Latin typically sufficient for English sites):

```bash
# Subset with glyphhanger or pyftsubset
pyftsubset DMSans-Variable.ttf \
  --output-file=DMSans-Variable-latin.woff2 \
  --flavor=woff2 \
  --layout-features='*' \
  --unicodes='U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+2000-206F'
```

### Performance Budget

- Maximum 3 font files loaded above the fold
- Total font payload: under 150KB
- Use variable fonts to replace multiple static weights
- Fallback stack: always include a system font that roughly matches metrics

```css
font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
```

---

## 10. Typographic Details

### Letter Spacing (Tracking)

- Headlines (48px+): tighten to `-0.02em` to `-0.04em`
- All-caps text: loosen to `0.05em` to `0.1em` (caps need extra space)
- Body text: leave at default (`0` or `normal`)
- Small labels/captions: slight loosening `0.01em` to `0.02em`

### Hanging Punctuation

For editorial layouts, let quotation marks and bullets hang outside the text block:

```css
blockquote {
  text-indent: -0.45em; /* Hang opening quote mark */
}
```

### Optical Margin Alignment

Large display text often looks misaligned because of optical illusion. Compensate:

```css
h1 {
  margin-left: -0.04em; /* Nudge left to optically align with body text below */
}
```

### Smart Typography Replacements

In content systems, auto-replace:
- `"straight quotes"` with "smart quotes"
- `--` with en-dash, `---` with em-dash (though prefer en-dashes)
- `...` with proper ellipsis `…`
- `x` between dimensions with `×` (multiplication sign)

### The Readability Checklist

- Line length: 50-75 characters (use `max-width: 65ch` on text containers)
- Paragraph spacing: 1em to 1.5em between paragraphs
- No justified text on the web (creates uneven word spacing without hyphenation)
- Left-aligned text for body (centered only for short headings)
- Sufficient contrast: minimum 4.5:1 for body, 3:1 for large text (WCAG AA)
