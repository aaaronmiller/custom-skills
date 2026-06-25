# Landing Page Architecture Reference

Deep implementation patterns for crafting high-converting, visually distinctive landing pages.
The landing page (or hero section) is the single most impactful element of any website. It
determines whether a visitor stays or bounces within 2-3 seconds. Every choice here must be
deliberate and bold.

## Table of Contents

1. The Site Title
2. Hero Section Anatomy
3. Timeless Landing Page Styles
4. Visual Flow and Eye-Guide Patterns
5. Conversion Architecture
6. Hero Section Code Patterns
7. Mobile-First Landing Strategy
8. Common Anti-Patterns

---

## 1. The Site Title

The site title is the first text element a visitor registers. It must accomplish three things
simultaneously: communicate what the site does, establish the brand's personality, and create
an emotional hook.

### Title Formula Patterns

**The Value Declaration**: Lead with outcome, not product.
- "Ship faster." (not "A deployment platform")
- "Design at the speed of thought." (not "A design tool")
- "Your research, amplified." (not "An AI research assistant")

**The Provocation**: Challenge an assumption to create tension.
- "You don't need another dashboard."
- "Meetings are broken. We fixed them."
- "The last form builder you'll ever use."

**The Poetic Fragment**: Use rhythm and economy like a headline poet.
- "Build. Break. Ship."
- "Where ideas become interfaces."
- "Code that writes itself. Almost."

### Title Typography Rules

- H1 should be the largest text on the page, minimum 48px desktop / 32px mobile
- Use the Display font at its heaviest weight (700-900)
- Letter-spacing: tighten slightly for large display text (-0.02em to -0.04em)
- Line-height: tight (1.0 to 1.15) for multi-line titles
- Maximum 8 words for single-line titles, 12 words for two-line
- Color: either pure contrast against background OR the accent color on a single keyword

### Title Animation

The title should be the first element to animate on page load. Preferred patterns:

**Clip-reveal**: Container has `overflow: hidden`. Title starts at `translateY(100%)` and
slides up into view over 600-800ms with a smooth deceleration curve.

**Word-by-word stagger**: Split into `<span>` per word. Each fades up from below with
`animation-delay: calc(var(--i) * 80ms)`. Creates a reading-speed reveal.

**Typewriter with cursor**: Characters appear sequentially with a blinking cursor. Best for
terminal/tech aesthetics. Use `$state` to drive character count.

---

## 2. Hero Section Anatomy

The hero section sits above the fold and contains 5 critical elements in priority order:

### Element Hierarchy

1. **Headline (H1)**: The site title. Largest, boldest, first to animate.
2. **Subheadline**: 1-2 sentences expanding on the title. Lighter weight, muted color.
   Maximum 25 words. Should answer "how?" or "for whom?"
3. **Primary CTA**: The single most important action. Large button, accent color,
   prominent placement. Text should be action-oriented: "Start building", "Try free",
   "See it in action" (avoid "Learn more" or "Submit").
4. **Visual Proof**: Screenshot, demo, video, or illustration that demonstrates the
   product/concept. This is the "show, don't tell" element.
5. **Trust Signal**: Logo bar, testimonial snippet, metric ("10,000+ teams"), or
   social proof element. Appears last, often as a scrolling marquee or grid.

### The Composition Rule

The first viewport must read as ONE unified composition — not a dashboard of cards,
not a collection of widgets. Every element in the hero serves the single narrative.

**Brand Test**: After designing the hero, mentally remove the nav and logo. If the
remaining design could belong to any other product, the branding is too weak. The hero
should feel inseparable from its brand through typography choices, color, imagery, and
voice.

### Design Constraints (Defaults)

Apply these unless the user specifies otherwise:
- 1 H1 headline (the main title — there can only be one)
- No more than 6 sections total on the page
- 2 typefaces maximum (display + body, with an optional mono for code)
- 1 accent color (derive supporting colors via color theory, not by adding more)
- 1 primary CTA above the fold (secondary CTA as ghost button is acceptable)
- Full-bleed sections preferred over centered card columns

### Spacing and Rhythm

- Hero height: `min-height: 100vh` or `min-height: 90vh` with a visible peek of the
  next section to invite scrolling
- Vertical padding: generous (8rem+ top/bottom on desktop)
- Content should be vertically centered or placed in the upper-third for editorial feel
- Maximum content width: 72ch for text-centric heroes, full-bleed for visual heroes

---

## 3. Timeless Landing Page Styles

These are proven, enduring approaches that transcend trend cycles. Each has been
refined across decades of web design. Select ONE and commit fully.

### 3.1 The Apple Keynote (Product Showcase)

**Origin**: Apple.com, circa 2007-present. Still the gold standard.
**Essence**: Massive product image on pure background. Minimal text. Let the product speak.
**Key elements**:
- Full-bleed product photography or 3D render, centered
- Dark background (deep black or near-black) with the product as the light source
- Title above product, subtitle below, CTA below that
- No visible UI chrome, no borders, no cards. Pure negative space
- Scroll reveals additional product angles or feature callouts
- Subtle ambient light effects (gradient glow behind product)

**When to use**: Physical products, hardware, premium SaaS with strong visual identity.

### 3.2 The Editorial Broadsheet (Content Authority)

**Origin**: The New York Times, Medium, Stripe's documentation.
**Essence**: Typography-driven. The page reads like a beautifully typeset article.
**Key elements**:
- Serif display heading at massive scale (80px+)
- Columnar layout with visible vertical rules (1px borders)
- Generous line-height (1.6-1.8) for body text
- Pull-quotes and large numbers as section breaks
- Monochrome or limited palette (2 colors maximum)
- Subtle texture or grain overlay on background

**When to use**: Content platforms, journalism, editorial, thought leadership, documentation.

### 3.3 The Geometric Playground (Creative Energy)

**Origin**: Bauhaus movement, Memphis design, modern SaaS like Linear, Vercel.
**Essence**: Bold shapes, diagonal lines, and geometric elements create visual energy.
**Key elements**:
- Large geometric shapes (circles, triangles, lines) as decorative elements
- Diagonal dividers via `clip-path: polygon()` between sections
- Asymmetric grid with overlapping elements
- High-contrast color blocks (accent on dark, or complementary pairs)
- Grid lines visible as design elements (not just structure)
- SVG patterns or dot grids as background texture

**When to use**: Creative tools, developer platforms, startups, portfolios.

### 3.4 The Cinematic Immersive (Full-Screen Experience)

**Origin**: Fashion houses, film studios, luxury brands.
**Essence**: Video or massive imagery fills the entire viewport. Text overlays float.
**Key elements**:
- Full-viewport background video (muted, autoplay, loop) or parallax image stack
- Text positioned with `position: absolute` over imagery
- Semi-transparent overlay gradient to ensure text readability
- Minimal UI: just the title, one CTA, and a scroll indicator
- Mouse-following elements or parallax depth layers
- Page loads with a brief fade-from-black or curtain-reveal animation

**When to use**: Fashion, film, luxury, real estate, travel, experiences.

### 3.5 The Swiss Grid (Clean Precision)

**Origin**: International Typographic Style (1950s), Josef Muller-Brockmann.
**Essence**: Rigid grid, mathematical spacing, objective clarity.
**Key elements**:
- Strict 12-column or 8-column grid, visible or implied
- Sans-serif typography only (Helvetica successors: Neue Haas Grotesk, Aktiv Grotesk)
- Black, white, and one accent color
- Generous whitespace as a deliberate design element
- Content aligned to grid intersections
- No decorative elements. Information IS the design

**When to use**: Corporate, fintech, analytics, data-heavy products, government.

### 3.6 The Neo-Brutalist (Raw Authenticity)

**Origin**: Craigslist aesthetic meets modern design rebellion.
**Essence**: Intentionally raw, with visible structure and thick borders.
**Key elements**:
- Thick black borders (3-4px) on all elements
- Hard drop shadows (`box-shadow: 6px 6px 0px #000`)
- Bright, clashing colors (yellow + black, pink + blue)
- System or monospace fonts at large sizes
- No border-radius (or very small: 2-4px)
- Visible grid structure, elements feel "stamped" onto the page
- Hover states: shift shadow direction, elements feel physically pressed

**When to use**: Creative agencies, indie products, developer tools, portfolios.

### 3.7 The Organic Flow (Natural Movement)

**Origin**: Nature-inspired design, Japanese aesthetics, wellness brands.
**Essence**: Soft curves, flowing shapes, and natural color palettes.
**Key elements**:
- Blob shapes via SVG or `border-radius: 30% 70% 70% 30% / 30% 30% 70% 70%`
- Earth-tone or pastel color palette
- Flowing section dividers (SVG wave paths instead of straight lines)
- Soft shadows (`box-shadow: 0 20px 60px rgba(0,0,0,0.08)`)
- Serif or humanist sans-serif fonts
- Smooth, slow animations (800ms+ durations, gentle easing)

**When to use**: Wellness, food, sustainability, lifestyle, education.

### 3.8 The Retro Terminal (Developer Nostalgia)

**Origin**: Early computing, Matrix aesthetic, hacker culture.
**Essence**: Monospace everything. Green-on-black. Blinking cursor.
**Key elements**:
- Monospace font for ALL text (JetBrains Mono, Fira Code)
- Dark background (#0a0a0a to #1a1a1a) with green (#00ff41) or amber (#ffb000) accent
- ASCII art or box-drawing characters as decorative elements
- Typing animation for headlines
- Scanline overlay effect (repeating 2px horizontal lines at 0.03 opacity)
- CTA styled as terminal commands: `$ npm install awesome`
- Cursor blink animation on interactive elements

**When to use**: Developer tools, CLI products, cybersecurity, tech blogs.

**WARNING**: This style is a trap. Across ALL major LLMs, terminal-themed outputs are
consistently the worst-performing style. The aesthetic is so constrained that models
produce near-identical, mediocre results every time. Only use when explicitly requested
by the user and even then, keep it to accent elements rather than the full page.

---

## 4. Visual Flow and Eye-Guide Patterns

### The Z-Pattern

For landing pages with mixed visual/text content. The eye travels:
top-left (logo) -> top-right (nav/CTA) -> diagonal down -> bottom-left (content) -> bottom-right (CTA).

Place your primary CTA at both the top-right AND bottom-right positions.

### The F-Pattern

For text-heavy landing pages. The eye scans:
top line fully -> drops down -> scans shorter line -> drops -> scans even shorter.

Front-load critical information in the first 2-3 words of each line.

### The Golden Section (Phi Grid)

Divide the hero into a 1:1.618 ratio. Place the primary content (headline + CTA)
in the larger section, visual proof in the smaller section. This creates a
mathematically balanced asymmetry that feels "right" without the viewer understanding why.

### Diagonal Flow

Use a diagonal line (via `clip-path`, rotated element, or image composition) to
guide the eye from top-left to bottom-right. This creates dynamic energy and
prevents the "stacked boxes" feeling of standard layouts.

### Geometric Bounding

Place a large geometric shape (circle, triangle, hexagon) behind or around the
primary content area. This creates a visual "container" that focuses attention
without using a visible card or border. Implement via:
- SVG shape with low-opacity fill
- CSS `clip-path` on a colored div
- Border-only shape (`border: 2px solid var(--accent)`) at large scale

---

## 5. Conversion Architecture

### Above-the-Fold Checklist

Every element above the fold must answer one of these questions:
- What is this? (headline)
- Why should I care? (subheadline/value prop)
- What does it look like? (visual proof)
- What do I do next? (CTA)
- Can I trust this? (social proof)

If an element doesn't answer any of these, remove it.

### CTA Design Rules

- Minimum size: 48px height, 160px width (touch-friendly)
- Accent color fill with high contrast text
- Subtle shadow for depth: `box-shadow: 0 4px 14px rgba(accent, 0.3)`
- Hover: lift (`translateY(-2px)`), shadow expands, slight brightness increase
- Active: press down (`translateY(1px)`, shadow contracts)
- Text: first-person action verb + benefit ("Start my free trial", "Get my report")
- Secondary CTA: ghost button (border only, no fill) for alternative action

### Scroll Invitation

If the hero is full-viewport, indicate more content exists below:
- Animated chevron at bottom center, pulsing or bouncing
- Partially visible section below the fold (peek: 60-80px of next section visible)
- Mouse-scroll animation icon
- Text prompt: "Scroll to explore" in small, muted type

---

## 6. Hero Section Code Patterns (SvelteKit 5)

### Split Layout Hero

```svelte
<section class="hero">
  <div class="hero-content">
    <h1 class="hero-title">Ship faster<span class="accent">.</span></h1>
    <p class="hero-sub">Deploy to production in seconds, not hours.</p>
    <div class="hero-actions">
      <button class="btn-primary">Start building</button>
      <button class="btn-ghost">See demo</button>
    </div>
  </div>
  <div class="hero-visual">
    <!-- Product screenshot, 3D render, or illustration -->
  </div>
</section>

<style>
  .hero {
    display: grid;
    grid-template-columns: 1fr 1fr;
    min-height: 100vh;
    align-items: center;
    gap: 4rem;
    padding: 0 clamp(2rem, 5vw, 8rem);
  }
  @media (max-width: 768px) {
    .hero { grid-template-columns: 1fr; text-align: center; }
  }
</style>
```

### Centered Hero with Background Layers

```svelte
<section class="hero-centered">
  <div class="hero-bg-layer" aria-hidden="true"></div>
  <div class="hero-noise" aria-hidden="true"></div>
  <div class="hero-content">
    <h1>Where ideas become interfaces</h1>
    <p>The design tool that thinks like you do.</p>
    <button class="btn-primary">Try free</button>
  </div>
  <div class="scroll-indicator" aria-hidden="true">
    <span class="chevron"></span>
  </div>
</section>

<style>
  .hero-centered {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    text-align: center;
    overflow: hidden;
  }
  .hero-bg-layer {
    position: absolute;
    inset: 0;
    background: radial-gradient(ellipse at 50% 0%, var(--accent-dim) 0%, transparent 70%);
    opacity: 0.3;
  }
  .hero-noise {
    position: absolute;
    inset: 0;
    background-image: url('/textures/noise.webp');
    mix-blend-mode: overlay;
    opacity: 0.06;
    pointer-events: none;
  }
</style>
```

---

## 7. Mobile-First Landing Strategy

### Hierarchy Adjustments for Small Screens

- Title: 32-40px (down from 56-80px desktop). Maintain heavy weight.
- Subheadline: 16-18px, max 2 lines visible without scroll
- CTA: full-width button, sticky at bottom of viewport on scroll
- Visual proof: reduce to inline preview or collapse into a tab/accordion
- Trust signals: horizontal scroll carousel instead of grid
- Remove: parallax effects, complex animations, multi-column layouts

### Thumb Zone Optimization

- Primary CTA positioned in the lower-third of the screen (natural thumb reach)
- Navigation hamburger in top-right (right-hand dominant)
- Swipe gestures for image carousels
- All tap targets: minimum 48x48px with 8px spacing between

### Performance Budget

- Hero image: WebP format, max 200KB, `loading="eager"`
- Background textures: tiny tiled patterns (< 5KB each)
- Fonts: subset to needed characters, `font-display: swap`
- Total above-fold payload target: under 500KB
- First Contentful Paint target: under 1.5 seconds

---

## 8. Common Anti-Patterns (Reject These)

- **Card Sickness**: The #1 LLM frontend failure. Every section wrapped in a
  rounded-corner card with shadow, turning a landing page into a dashboard. Cards on
  homepages are almost never needed. Use full-bleed sections, typographic hierarchy,
  and whitespace instead. If you see a card-within-a-card, the design has failed.
- **The Generic SaaS**: Purple gradient, "Transform your workflow", stock photo of
  people in a meeting, centered text, rounded card with shadow. This is the default
  output of every AI design tool. Fight it.
- **Pill Cluster Slop**: 3-5 pill-shaped badges ("AI Powered", "New", "Enterprise
  Ready") floating near the hero that add no functional value. These are the single
  clearest tell that UI was vibe-coded by an LLM. Remove them all, fix layout shifts.
- **The Stat Strip**: A row of metrics ("10K+ users | 99.9% uptime | 50ms latency")
  that appears on every generated page regardless of context. Unless these numbers are
  meaningful differentiators, delete them.
- **Eyebrow Title Spam**: Small muted text above every heading ("Our Approach",
  "Why Choose Us", "The Platform"). If your headline needs a preface to make sense,
  rewrite the headline.
- **The Kitchen Sink**: Cramming features, pricing, testimonials, FAQ, and a contact
  form above the fold. Pick ONE message.
- **The Orphaned CTA**: A button floating with no supporting context. CTAs need
  proximity to the value proposition they fulfill.
- **The Invisible Hero**: White background, gray text, no visual anchor. Nothing to
  remember, nothing to feel. Add texture, color, or imagery.
- **The Slideshow Carousel**: Auto-advancing hero carousels reduce conversion by
  splitting attention. Commit to ONE hero message.
- **The Wall of Logos**: 30 partner logos in a static grid. Instead, use a slow-scroll
  marquee with 8-10 carefully selected logos.
- **Style-Name Copy Leakage**: When the design style bleeds into the actual page copy.
  A brutalist page should NOT say "A brutal, uncompromising platform." An organic flow
  page should NOT say "Flowing naturally into your workflow." The aesthetic is visual,
  not verbal.
- **Aggressive Hover Inflation**: Hover effects that dramatically scale elements,
  add thick borders, or shift layout. Cards that grow 10% on hover cause layout thrash.
  Prefer subtle opacity, color, or shadow changes.
- **Missing Hover States**: The opposite problem — elements that look interactive but
  have no hover feedback at all. This is the easiest way to spot unchecked AI output.
  If it looks clickable, it MUST respond to hover.
- **Image Dimension Crimes**: Images placed with wrong aspect ratios, bad crops that
  cut off subjects, or excessive empty space in hero imagery. Always verify image
  placement produces good visual weight distribution.
- **The Three Nav Items**: LLMs default to exactly 3 items in the top nav on every
  single generation. Vary nav structure to match the actual site needs — 4-6 items
  is normal for real products. The cookie-cutter 3-item nav is an AI fingerprint.
- **Identical Layout Syndrome**: Generating multiple pages that are structurally
  identical with only color swaps. If doing multiple generations or pages, each must
  have a meaningfully different layout structure — not the same grid with different hues.
