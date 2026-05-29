# Visual Kinetics Reference

Deep implementation patterns for lightweight 3D effects, parallax depth, microanimation
orchestration, and kinetic typography in SvelteKit 5.

## Animation Stack

**Tier 1 - CSS Native** (zero JS, best performance):
`transition`, `@keyframes`, `animation-delay` for staggering, `scroll-timeline` for
scroll-driven animations (check browser support). Use for hover states, loading skeletons,
simple reveals, infinite loops (marquees).

**Tier 2 - Svelte Built-in** (`svelte/transition`, `svelte/animate`):
`fade`, `fly`, `scale`, `slide`, `blur`, `draw` transitions on `in:`/`out:`/`transition:`
directives. `flip` from `svelte/animate` for list reordering (FLIP technique). `tweened`
and `spring` stores from `svelte/motion` for reactive animated values.

**Tier 3 - Svelte Motion** (`@humanspeak/svelte-motion`):
Port of Framer Motion for Svelte 5. Provides `<motion.div>` components with `animate`,
`initial`, `exit`, `whileHover`, `whileTap`, `whileInView` props. Use for complex
orchestration, `AnimatePresence` for exit animations, layout animations, gesture-driven
effects, and scroll-linked transforms.

**Tier 4 - GSAP** (via CDN or npm):
For timeline-based sequences, ScrollTrigger pinning, morphSVG, and effects that require
frame-precise control. Heavier dependency. Use sparingly, only when lower tiers cannot
achieve the effect.

## Fake 3D: The Holographic Tilt Card

Creates a card that rotates based on mouse position, simulating a floating physical object.

### Math (Svelte 5 Action)

```svelte
<script>
  function useTilt(node, options = { maxRotation: 10, scale: 1.02 }) {
    function handleMouseMove(e) {
      const rect = node.getBoundingClientRect();
      const centerX = rect.left + rect.width / 2;
      const centerY = rect.top + rect.height / 2;
      const rotateY = ((e.clientX - centerX) / (rect.width / 2)) * options.maxRotation;
      const rotateX = -((e.clientY - centerY) / (rect.height / 2)) * options.maxRotation;
      node.style.transform =
        `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(${options.scale}, ${options.scale}, ${options.scale})`;
    }
    function handleMouseLeave() {
      node.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1,1,1)';
    }
    node.style.transition = 'transform var(--duration-enter-fast) var(--ease-enter)';
    node.style.transformStyle = 'preserve-3d';
    node.addEventListener('mousemove', handleMouseMove);
    node.addEventListener('mouseleave', handleMouseLeave);
    return {
      destroy() {
        node.removeEventListener('mousemove', handleMouseMove);
        node.removeEventListener('mouseleave', handleMouseLeave);
      }
    };
  }
</script>

<div use:useTilt={{ maxRotation: 12, scale: 1.03 }}>
  <!-- Card content -->
</div>
```

### The Glare Effect

Add a child `<div>` with `pointer-events: none` inside the tilt card. Set its background
to `radial-gradient(circle at ${mouseX}% ${mouseY}%, rgba(255,255,255,0.3) 0%, transparent 60%)`.
Move the gradient center opposite to the tilt direction for realistic light simulation.
Apply `mix-blend-mode: overlay` or `soft-light`.

## Parallax Hero (Nano Banana Integration)

Separate the hero into 3+ layers moving at different scroll speeds.

### Layer Strategy

| Layer | z-index | Opacity | Dithering | Scroll Speed |
|-------|---------|---------|-----------|-------------|
| Background | 0 | 0.3-0.5 | Atkinson (heavy) | `scrollY * 0.1` |
| Midground | 10 | 0.8-1.0 | None (sharp subject) | `scrollY * 0.4` |
| Foreground | 20 | 0.1-0.3 | Bayer (fine grain) | `scrollY * 0.8` |

### Implementation Pattern

Each layer uses `position: absolute` within an `overflow: hidden; height: 100vh` container.
Drive transforms via `requestAnimationFrame` + `window.scrollY`. Apply `will-change: transform`
and use `translate3d(0, ${offset}px, 0)` to force GPU compositing.

Always wrap in a `prefers-reduced-motion` check:
```js
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
```

## Glassmorphism 2.0 (Holographic Panels)

Create elements that feel like projected light or frosted glass.

- Background: `bg-white/5` (dark) or `bg-black/5` (light)
- Border: `border border-white/10`
- Blur: `backdrop-filter: blur(16px) saturate(180%)`
- Noise overlay: Layer a Nano Banana noise texture at `opacity: 0.04`, `mix-blend-mode: overlay`
  to eliminate the "plastic" digital look
- Glow: `box-shadow: 0 8px 32px rgba(var(--accent-rgb), 0.15)` matching the accent color

## Kinetic Typography

### The Reveal Mask
Container: `overflow-hidden`. Text starts at `translate-y-full`.
Animate to `translate-y-0` on scroll/entry. Stagger individual letters by wrapping in
`<span>` with `animation-delay: calc(var(--index) * 50ms)`.

### Infinite Marquee
Container: `overflow-hidden flex whitespace-nowrap`. Duplicate the text content to ensure
seamless looping. Animation: `translateX(-50%) linear infinite`. On hover:
`animation-play-state: paused`.

### Split Text Entrance
Split heading into words. Each word fades up from below with increasing delay.
Use Svelte `{#each}` with `in:fly={{ y: 20, delay: i * 80 }}`.

## Scroll-Triggered Reveals

Use `IntersectionObserver` via a Svelte action:

```svelte
<script>
  function inView(node, options = { threshold: 0.2 }) {
    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) {
        node.classList.add('in-view');
        observer.unobserve(node);
      }
    }, options);
    observer.observe(node);
    return { destroy: () => observer.disconnect() };
  }
</script>

<style>
  .reveal { opacity: 0; transform: translateY(24px); transition: all 0.6s cubic-bezier(0.22, 1, 0.36, 1); }
  .reveal.in-view { opacity: 1; transform: translateY(0); }
</style>

<div class="reveal" use:inView>Content appears on scroll</div>
```

Stagger multiple elements by adding `transition-delay` via CSS custom properties.

## Physics-Based Easing Reference

| Name | Value | Feel |
|------|-------|------|
| Bouncy | `cubic-bezier(0.34, 1.56, 0.64, 1)` | Overshoots then settles |
| Smooth Decel | `cubic-bezier(0.22, 1, 0.36, 1)` | Fast start, gentle stop |
| Snap | `cubic-bezier(0.68, -0.55, 0.27, 1.55)` | Pulls back then snaps |
| Material Standard | `cubic-bezier(0.2, 0, 0, 1)` | Android-style natural |
| Elastic | `cubic-bezier(0.68, -0.6, 0.32, 1.6)` | Springy, playful |

## Magnetic Button Pattern

The button subtly moves toward the cursor before click:
Track mouse position relative to button center. Apply a small `translate` (max 4-6px)
in the cursor direction. On mouse leave, spring back to origin.

## Performance Checklist

- `will-change`: Apply only to the specific property being animated, remove after animation
- `contain: layout paint` on card containers to prevent repaint cascading
- Use `transform` and `opacity` exclusively for 60fps (avoid animating `width`, `height`, `margin`)
- `requestAnimationFrame` for scroll-driven effects, never raw scroll listeners
- Respect `prefers-reduced-motion` throughout: disable parallax, tilt, complex sequences
