# Imagery System Reference

Deep implementation patterns for using images to transform interfaces from functional
to atmospheric. Covers image sizing, dithering, overlays, geometric bounding, artistic
styles, background composition, and Nano Banana generative textures.

## Table of Contents

1. Image Roles in Interface Design
2. Image Sizing and Format Strategy
3. Background Image Composition
4. Dithering and Texture Techniques
5. Overlay and Geometric Bounding
6. Movement and Parallax in Imagery
7. Artistic Style Selection
8. Button, Banner, and Accent Imagery
9. Nano Banana Integration Patterns
10. Image Generation Prompting Guide

---

## 1. Image Roles in Interface Design

Every image in an interface must serve one of these roles. If it doesn't, remove it.

### Atmospheric (Background)

Creates mood without competing for attention. Low opacity, blurred, dithered, or
desaturated. The user should feel it, not study it.
- Hero section background textures
- Section divider gradients
- Full-bleed environmental imagery behind content

### Informational (Content)

Communicates specific information the text cannot. Sharp, well-lit, properly sized.
- Product screenshots and mockups
- Charts, diagrams, and illustrations
- Profile photos and team images

### Navigational (Interactive)

Guides user action or identifies clickable regions. Sized for thumbnails, with
clear borders and hover states.
- Card cover images
- Icon/illustration buttons
- Image-based navigation tiles

### Decorative (Accent)

Adds visual interest and brand personality. Small, strategic, distinctive.
- Geometric shapes and patterns
- Animated SVG accents
- Corner/edge decorative elements
- Custom cursor images

---

## 2. Image Sizing and Format Strategy

### Format Selection

| Use Case | Format | Why |
|----------|--------|-----|
| Photography | WebP (lossy) | 25-35% smaller than JPEG at equivalent quality |
| Screenshots | WebP or PNG | Needs sharp text/UI edges |
| Icons/illustrations | SVG | Vector, infinitely scalable, tiny file size |
| Textures/patterns | WebP (lossy, low-q) | Textures hide compression artifacts |
| Animations | WebP animated or CSS | Avoid GIF (huge files, limited colors) |
| Transparent overlays | WebP or PNG (8-bit) | Need alpha channel |

### Responsive Image Sizing

Serve different sizes for different viewports. Never send a 2400px image to a 375px phone.

```html
<picture>
  <source
    media="(min-width: 1024px)"
    srcset="hero-1600.webp 1600w, hero-2400.webp 2400w"
    sizes="100vw"
  >
  <source
    media="(min-width: 640px)"
    srcset="hero-800.webp 800w, hero-1200.webp 1200w"
    sizes="100vw"
  >
  <img
    src="hero-600.webp"
    srcset="hero-400.webp 400w, hero-600.webp 600w"
    sizes="100vw"
    alt="Hero description"
    loading="eager"
    decoding="async"
  >
</picture>
```

### Size Targets

| Role | Max Width | Max File Size | Loading |
|------|----------|---------------|---------|
| Hero background | 2400px | 200KB | eager |
| Content image | 1200px | 150KB | lazy |
| Card thumbnail | 600px | 50KB | lazy |
| Texture/pattern | 256-512px (tiled) | 5-15KB | eager |
| Icon/accent | SVG or 64-128px | 5KB | eager |

### Image Dimension Verification (Critical)

LLMs are consistently bad at image placement. Common failures:
- **Wrong aspect ratio**: Placing a 16:9 image in a 1:1 container, causing crop/stretch
- **Subject cutoff**: Hero images where the subject's head or key element is clipped
- **Inverted visual weight**: Empty sky/ceiling at top, important content cropped at bottom
- **Object-fit misuse**: `object-fit: cover` without checking what gets cropped

After placing any image, verify:
1. The subject/focal point is visible and centered within the container
2. The aspect ratio matches the container's proportions (or `object-fit` is used
   correctly with an appropriate `object-position`)
3. Visual weight distribution is correct — don't leave vast empty space where the
   eye should be anchored
4. On mobile, the crop still shows the important parts of the image

---

## 3. Background Image Composition

### The Three-Layer Stack

Professional backgrounds use layered composition, not single images.

**Layer 1: Base Canvas** (z-index: 0)
A solid color or gradient that ensures content is readable even if images fail to load.
```css
.hero { background: var(--base-100); }
```

**Layer 2: Primary Image** (z-index: 1)
The main visual element. Can be photography, illustration, or generative texture.
Applied with reduced opacity or blend mode.
```css
.hero-image {
  position: absolute; inset: 0;
  background-image: url('/images/hero-bg.webp');
  background-size: cover;
  background-position: center;
  opacity: 0.3;
  mix-blend-mode: luminosity;
}
```

**Layer 3: Texture Overlay** (z-index: 2)
Noise, grain, or pattern that adds tactile quality and prevents the "digital flat" look.
```css
.hero-texture {
  position: absolute; inset: 0;
  background-image: url('/textures/noise-256.webp');
  background-repeat: repeat;
  mix-blend-mode: overlay;
  opacity: 0.06;
  pointer-events: none;
}
```

### Gradient Overlays for Text Readability

When placing text over images, use a directional gradient:

```css
/* Dark gradient from bottom (text at bottom of image) */
.image-overlay-bottom::after {
  content: '';
  position: absolute; inset: 0;
  background: linear-gradient(to top, rgba(0,0,0,0.7) 0%, transparent 60%);
}

/* Radial spotlight (text at center) */
.image-overlay-center::after {
  background: radial-gradient(
    ellipse at center,
    rgba(0,0,0,0.5) 0%,
    transparent 70%
  );
}
```

---

## 4. Dithering and Texture Techniques

Dithering converts images into dot patterns, creating a retro/editorial aesthetic
while dramatically reducing file size. Different algorithms produce different textures.

### Dithering Algorithms and Their Aesthetic

**Atkinson Dithering** - Aggressive, high-contrast. Only propagates 6/8 of the error,
creating white "halos" around shapes. Best for: editorial, newspaper-print aesthetics.

**Floyd-Steinberg** - The standard. Even error distribution creates smooth gradients
in the dot pattern. Best for: general-purpose texture, backgrounds.

**Bayer (Ordered)** - Grid-based pattern. Creates a visible, regular dot grid.
Best for: geometric aesthetics, retro gaming look, fine grain overlays.

**Jarvis-Judice-Ninke** - Wide error kernel creates softer, smoother results than
Floyd-Steinberg. Best for: photographic subjects that need to remain recognizable.

### Applying Dithered Textures

1. Generate dithered versions of images at reduced resolution (400-800px)
2. Apply as `background-image` with `mix-blend-mode: overlay` or `soft-light`
3. Use very low opacity (0.05-0.15)
4. Tile small dithered textures for seamless backgrounds

### Combining Multiple Dithering Layers

```css
.textured-bg {
  position: relative;
  background: var(--base-100);
}
.textured-bg::before {
  /* Coarse Atkinson layer */
  content: '';
  position: absolute; inset: 0;
  background-image: url('/textures/dither-atkinson.webp');
  mix-blend-mode: overlay;
  opacity: 0.08;
}
.textured-bg::after {
  /* Fine Bayer grain layer */
  content: '';
  position: absolute; inset: 0;
  background-image: url('/textures/dither-bayer-fine.webp');
  mix-blend-mode: soft-light;
  opacity: 0.04;
}
```

---

## 5. Overlay and Geometric Bounding

### Diagonal Line Compositions

A large diagonal line across a background image creates structure and visual energy.
The diagonal divides the image into two zones with different treatments.

```css
.diagonal-split {
  position: relative;
  overflow: hidden;
}
.diagonal-split::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(
    135deg,
    transparent 0%,
    transparent 48%,
    var(--base-100) 48%,
    var(--base-100) 52%,
    transparent 52%,
    transparent 100%
  );
  /* Creates a diagonal band across the image */
}
```

### Clip-Path Geometric Bounding

Use `clip-path` to give images non-rectangular shapes:

```css
/* Circle-clipped image */
.img-circle { clip-path: circle(45% at center); }

/* Hexagonal image */
.img-hex {
  clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
}

/* Diagonal cut (slanted rectangle) */
.img-diagonal {
  clip-path: polygon(10% 0%, 100% 0%, 90% 100%, 0% 100%);
}

/* Soft blob */
.img-blob {
  border-radius: 30% 70% 53% 47% / 26% 46% 54% 74%;
}
```

### Frame and Border Treatments

**Double-line frame**: Two thin borders with a gap between them.
```css
.framed {
  border: 1px solid var(--border-default);
  outline: 1px solid var(--border-default);
  outline-offset: 4px;
}
```

**Accent corner marks**: L-shaped marks at corners (editorial/print aesthetic).
```css
.corner-marks {
  position: relative;
}
.corner-marks::before,
.corner-marks::after {
  content: '';
  position: absolute;
  width: 24px; height: 24px;
  border: 2px solid var(--accent-default);
}
.corner-marks::before { top: -8px; left: -8px; border-right: none; border-bottom: none; }
.corner-marks::after { bottom: -8px; right: -8px; border-left: none; border-top: none; }
```

### Grid and Line Overlays

Superimpose a subtle grid pattern over background imagery:

```css
.grid-overlay::after {
  content: '';
  position: absolute; inset: 0;
  background-image:
    linear-gradient(var(--border-default) 1px, transparent 1px),
    linear-gradient(90deg, var(--border-default) 1px, transparent 1px);
  background-size: 60px 60px;
  opacity: 0.06;
  pointer-events: none;
}
```

---

## 6. Movement and Parallax in Imagery

### Subtle Background Drift

Images that move slightly create a living, breathing atmosphere:

```css
@keyframes drift {
  0% { transform: translate(0, 0) scale(1.05); }
  50% { transform: translate(-10px, -5px) scale(1.08); }
  100% { transform: translate(0, 0) scale(1.05); }
}

.bg-drift {
  animation: drift 30s ease-in-out infinite;
  /* Very slow, barely perceptible. The image must be slightly oversized (scale > 1)
     to prevent edge gaps during movement. */
}
```

### Scroll-Linked Parallax

See `visual-kinetics.md` for full parallax implementation. Quick summary:
- Background layer: moves at 10-20% scroll speed
- Midground: moves at 40-60% scroll speed
- Foreground: moves at 80-100% scroll speed
- Always respect `prefers-reduced-motion`

### Mouse-Following Ambient Effect

Background image shifts slightly based on mouse position:

```svelte
<script>
  let offsetX = $state(0);
  let offsetY = $state(0);

  function handleMouseMove(e) {
    const centerX = window.innerWidth / 2;
    const centerY = window.innerHeight / 2;
    offsetX = (e.clientX - centerX) * 0.01; // Very subtle: 1% of offset
    offsetY = (e.clientY - centerY) * 0.01;
  }
</script>

<svelte:window on:mousemove={handleMouseMove} />

<div
  class="parallax-bg"
  style="transform: translate({offsetX}px, {offsetY}px)"
></div>
```

---

## 7. Artistic Style Selection

Select an image style that matches the site's overall aesthetic direction.
Consistency is critical: mixing photographic and illustrated styles creates visual noise.

### Photorealistic

Clean, professional photography. Best for corporate, e-commerce, portfolio sites.
- Even lighting, minimal post-processing
- Consistent color temperature across all images
- Apply a subtle LUT (color lookup table) to unify photos from different sources

### Illustrated / Vector

Custom illustrations. Best for SaaS, educational, startup sites.
- Choose one illustration style and maintain it: flat, isometric, hand-drawn, geometric
- Consistent line weight, color palette, and level of detail across all illustrations
- SVG format for scalability and animation potential

### Generative / Abstract

AI-generated or procedural imagery. Best for creative, tech, experimental sites.
- Use as textures and backgrounds, not as standalone content images
- Apply heavy post-processing: dithering, blur, color manipulation
- Combine with geometric overlays for structure

### Mixed Media / Collage

Combining photography with illustrations, shapes, and text. Best for fashion,
music, cultural sites.
- Strong compositional rules (golden ratio, rule of thirds)
- Consistent border/frame treatment
- Color unity: ensure all elements share the palette

### Duotone

Photography processed through a two-color filter. Best for bold, modern aesthetics.
```css
.duotone {
  filter: grayscale(100%);
  position: relative;
}
.duotone::after {
  content: '';
  position: absolute; inset: 0;
  background: var(--primary-default);
  mix-blend-mode: color;
  opacity: 0.7;
}
```

---

## 8. Button, Banner, and Accent Imagery

### Image-Enhanced Buttons

Buttons with subtle background textures or icon integration:

```css
.btn-textured {
  background-image:
    linear-gradient(var(--primary-default), var(--primary-vivid)),
    url('/textures/subtle-noise.webp');
  background-blend-mode: normal, overlay;
}

/* Button with integrated icon that moves on hover */
.btn-icon {
  display: inline-flex; align-items: center; gap: 0.5rem;
}
.btn-icon svg {
  transition: transform 0.2s ease;
}
.btn-icon:hover svg {
  transform: translateX(4px); /* Arrow slides right on hover */
}
```

### Banner Image Compositions

For announcement or promotional banners:
- Background: gradient or subtle image at 10-20% opacity
- Foreground: text + small product image or illustration
- Edge treatment: diagonal cut or wave SVG divider
- Height: compact (80-120px), never overwhelming

### Decorative Accent Images

Small images or SVGs that add personality to sections:
- Floating geometric shapes near headings (circles, triangles, lines)
- Corner illustrations that peek into content areas
- Background "stickers" or stamps for informal aesthetics
- Animated SVG patterns that respond to scroll position

---

## 9. Nano Banana Integration Patterns

Nano Banana generates textures, dithered images, and patterns that eliminate
flat, digital-looking backgrounds.

### Texture Generation Strategies

**Noise textures**: Generate at 256x256 or 512x512, tile seamlessly.
Apply at opacity 0.04-0.08 with `mix-blend-mode: overlay`.

**Dithered photography**: Process hero images through Nano Banana's dithering.
Use for atmospheric backgrounds at reduced opacity.

**Pattern generation**: Create geometric or organic patterns for:
- Section background variation
- Card hover state backgrounds
- Loading state placeholders

### Multi-Layer Nano Banana Composition

```
Layer Stack (bottom to top):
1. Solid color base (var(--base-100))
2. Nano Banana dithered image, Atkinson algorithm, 0.1 opacity, blend: luminosity
3. Nano Banana fine noise, Bayer algorithm, 0.05 opacity, blend: overlay
4. CSS gradient overlay for directional light effect
5. Content
```

### Image Processing Pipeline

1. Source image (photography or illustration)
2. Resize to target dimensions
3. Apply dithering algorithm via Nano Banana
4. Export as WebP at appropriate quality
5. Create multiple sizes for responsive serving
6. Apply CSS blend modes and opacity at render time

---

## 10. Image Generation Prompting Guide

When generating images via AI (for custom illustrations, textures, or backgrounds),
structure prompts for consistent, on-brand results.

### Prompt Structure

```
[Style] [Subject] [Composition] [Color directive] [Mood] [Technical specs]
```

**Example for a hero background**:
"Abstract geometric composition, intersecting angular planes and thin lines,
color palette limited to deep indigo and warm amber on dark charcoal background,
atmospheric and futuristic mood, high resolution, suitable for web background use"

**Example for a texture**:
"Seamless tileable noise pattern, organic grain texture, monochromatic gray tones,
subtle variation, no distinct objects, suitable for overlay at low opacity"

**Example for an illustration**:
"Isometric technical illustration of a server rack with glowing data streams,
flat design style with clean vector edges, color palette: teal and coral accents
on dark navy background, no text, minimal detail, icon-style"

### Consistency Rules

- Always specify the color palette explicitly (reference site palette tokens)
- Always specify the style (flat, isometric, realistic, abstract)
- Always specify the intended use (background, illustration, icon, texture)
- For texture generation, always request "seamless" or "tileable"
- For backgrounds, request "no focal point" or "ambient" to prevent competition with text
- Generate in batches with identical style prompts but varied subjects for visual variety
