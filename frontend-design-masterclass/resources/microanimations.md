# Microanimations and Interactive Controls Reference

Deep implementation patterns for responsive UI feedback, button and control animations,
haptic-feel interactions, snap behaviors, navigation transitions, and motion design
that makes interfaces feel alive and tactile.

## Table of Contents

1. Animation Philosophy
2. Button and Control States
3. Navigation Feedback
4. Scroll-Driven Animations
5. Form and Input Interactions
6. Loading and State Transitions
7. Page and Route Transitions
8. Haptic-Feel Patterns
9. Snap and Magnetic Behaviors
10. Performance and Accessibility
11. Easing and Timing Reference

---

## 1. Animation Philosophy

Every animation must serve a purpose. The three valid reasons to animate:

1. **Feedback**: Confirming a user action occurred ("I pressed the button and it responded")
2. **Orientation**: Showing where something came from or went to ("The modal slid in from the right")
3. **Delight**: Creating a moment of unexpected pleasure ("The icon bounced playfully")

If an animation doesn't serve one of these, remove it. Motion for motion's sake
is visual noise that slows perception and drains battery.

### Animation Variety Mandate

LLMs converge on the same animation patterns across generations. Watch for these
and actively vary your approach:

- **Stacked text reveal**: Words sliding up one-by-one is the most overused reveal
  animation. After the first use on a page, switch to clip-reveal, fade-blur,
  letter-by-letter, or a simple opacity fade for subsequent sections.
- **Uniform stagger**: Every list with identical 80ms delays gets predictable fast.
  Vary delays, directions, or use random-offset staggers for organic feel.
- **Pop-in timing bugs**: Elements that fade in smoothly... then a batch "pops" in
  at the end. This is a common CSS bug from mismatched animation durations. Verify
  that ALL elements in a stagger sequence complete smoothly — no abrupt final frames.

Vary animation approaches across sections: if the hero uses a slide-up reveal, use
a fade-blur for the features section and a clip-path wipe for the testimonials.

### Motion Tokens (Required)

All durations and easing curves MUST be defined as CSS custom properties. This
ensures a unified motion rhythm across every component. Never hard-code
`transition: 0.3s ease` inline — always reference a token.

```css
:root {
  /* === Duration Tokens === */
  /* Asymmetric timing: enters are longer than exits.
     New content needs time to land; dismissed content should leave quickly. */
  --duration-instant: 50ms;
  --duration-fast: 100ms;
  --duration-normal: 200ms;
  --duration-slow: 350ms;
  --duration-slower: 500ms;

  /* Enter durations (slightly longer — content arriving) */
  --duration-enter-fast: 150ms;
  --duration-enter: 250ms;
  --duration-enter-slow: 400ms;
  --duration-enter-dramatic: 600ms;

  /* Exit durations (shorter — content leaving) */
  --duration-exit-fast: 100ms;
  --duration-exit: 200ms;
  --duration-exit-slow: 300ms;

  /* === Easing Tokens (MD3 Emphasized Curves) === */
  /* Decelerate on enter: fast start, gentle landing */
  --ease-enter: cubic-bezier(0.2, 0, 0, 1);
  /* Accelerate on exit: gentle start, fast departure */
  --ease-exit: cubic-bezier(0.3, 0, 0.8, 0.15);
  /* Standard: symmetric for state changes (hover, color) */
  --ease-standard: cubic-bezier(0.2, 0, 0, 1);
  /* Bounce: playful overshoot for toggles, playful UI */
  --ease-bounce: cubic-bezier(0.34, 1.56, 0.64, 1);
  /* Spring: physically-modeled feel for modals and dialogs */
  --ease-spring: cubic-bezier(0.22, 1.4, 0.36, 1);
  /* Snap: quick decisive state changes */
  --ease-snap: cubic-bezier(0.68, -0.55, 0.27, 1.55);
}
```

**Asymmetric timing rule**: When an element enters AND exits, always use
`--duration-enter-*` with `--ease-enter` for the appear, and `--duration-exit-*`
with `--ease-exit` for the dismiss. The enter should be ~1.25-1.5x the exit duration.
This gives new content time to settle while old content clears quickly.

```css
/* Example: dropdown menu */
.dropdown {
  /* Enter: 250ms decelerate — slides in, gently lands */
  transition: opacity var(--duration-enter) var(--ease-enter),
              transform var(--duration-enter) var(--ease-enter);
}
.dropdown.closing {
  /* Exit: 200ms accelerate — quick dismissal */
  transition: opacity var(--duration-exit) var(--ease-exit),
              transform var(--duration-exit) var(--ease-exit);
}
```

### The 200ms Rule

- Under 100ms: feels instant. Use for color changes, opacity shifts.
- 100-300ms: feels responsive. Use for transforms, slide-ins, fades.
- 300-500ms: feels deliberate. Use for page transitions, complex reveals.
- Over 500ms: feels slow. Only for dramatic reveals or narrative sequences.

Most UI animations should use `--duration-enter` (250ms) as the baseline.

---

## 2. Button and Control States

Every interactive element needs 5 visual states. Each state must be visibly
distinct from the others.

### The Five States

**Default**: The resting appearance. Communicates "this is interactive."
**Hover**: Mouse is over the element. Communicates "you can click this."
**Active/Pressed**: Mouse button is down. Communicates "you are clicking."
**Focus**: Element has keyboard focus. Communicates "this is selected."
**Disabled**: Element cannot be interacted with. Communicates "not available."

### Primary Button Implementation

```css
.btn-primary {
  /* Default */
  background: var(--primary-default);
  color: var(--text-inverse);
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.5rem;
  font-weight: 600;
  cursor: pointer;
  transition:
    transform var(--duration-enter-fast) var(--ease-bounce),
    box-shadow var(--duration-enter-fast) var(--ease-standard),
    background-color var(--duration-fast) var(--ease-standard);
  box-shadow: 0 2px 8px hsl(var(--primary-hue), 50%, 40%, 0.2);
}

.btn-primary:hover {
  /* Lift + glow expansion */
  transform: translateY(-2px);
  box-shadow: 0 6px 20px hsl(var(--primary-hue), 50%, 40%, 0.3);
  background: var(--primary-vivid);
}

.btn-primary:active {
  /* Press down effect */
  transform: translateY(1px) scale(0.98);
  box-shadow: 0 1px 4px hsl(var(--primary-hue), 50%, 40%, 0.2);
  transition-duration: var(--duration-instant); /* Instant press feel */
}

.btn-primary:focus-visible {
  /* Keyboard focus ring */
  outline: 2px solid var(--accent-default);
  outline-offset: 3px;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}
```

### Ghost Button (Secondary)

```css
.btn-ghost {
  background: transparent;
  color: var(--primary-default);
  border: 1.5px solid var(--primary-default);
  transition:
    background var(--duration-enter-fast) var(--ease-standard),
    color var(--duration-enter-fast) var(--ease-standard),
    transform var(--duration-enter-fast) var(--ease-bounce);
}
.btn-ghost:hover {
  background: hsl(var(--primary-hue), 50%, 50%, 0.08);
  transform: translateY(-1px);
}
.btn-ghost:active {
  background: hsl(var(--primary-hue), 50%, 50%, 0.15);
  transform: translateY(0) scale(0.98);
}
```

### Icon Button

```css
.btn-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 40px; height: 40px;
  border-radius: 50%;
  background: transparent;
  transition: background 0.15s ease, transform 0.15s ease;
}
.btn-icon:hover {
  background: hsl(var(--primary-hue), 10%, 50%, 0.08);
}
.btn-icon:active {
  transform: scale(0.9);
  background: hsl(var(--primary-hue), 10%, 50%, 0.15);
}
.btn-icon svg {
  transition: transform 0.2s ease;
}
.btn-icon:hover svg {
  transform: scale(1.1);
}
```

### Toggle Switch

```css
.toggle {
  width: 48px; height: 26px;
  border-radius: 13px;
  background: var(--base-300);
  position: relative;
  cursor: pointer;
  transition: background 0.25s ease;
}
.toggle::after {
  content: '';
  width: 22px; height: 22px;
  border-radius: 50%;
  background: white;
  position: absolute;
  top: 2px; left: 2px;
  transition: transform 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
  box-shadow: 0 1px 3px rgba(0,0,0,0.15);
}
.toggle[aria-checked="true"] {
  background: var(--primary-default);
}
.toggle[aria-checked="true"]::after {
  transform: translateX(22px);
}
```

---

## 3. Navigation Feedback

### Fixed Nav Scroll Behavior (Required)

Any fixed/sticky nav MUST add a backdrop on scroll. A transparent nav that stays
transparent as content scrolls behind it creates unreadable text contrast. This is
one of the most common bugs in AI-generated UIs.

Requirements:
- Transparent background at page top
- On scroll (> ~50px), transition to frosted glass: `backdrop-filter: blur(12px)`
  with semi-transparent background and subtle bottom border or shadow
- Smooth transition (300ms) between states
- See the "Shrinking Header" pattern in Section 8 for implementation

### Menu Item Hover

```css
.nav-item {
  position: relative;
  padding: 0.5rem 0;
  color: var(--text-secondary);
  transition: color var(--duration-fast) var(--ease-standard);
}
.nav-item::after {
  content: '';
  position: absolute;
  bottom: 0; left: 50%;
  width: 0; height: 2px;
  background: var(--accent-default);
  transition: width var(--duration-enter-fast) var(--ease-enter),
              left var(--duration-enter-fast) var(--ease-enter);
}
.nav-item:hover {
  color: var(--text-primary);
}
.nav-item:hover::after {
  width: 100%; left: 0;
}
.nav-item.active::after {
  width: 100%; left: 0;
}
```

### Mobile Hamburger Animation

Transform three lines into an X with smooth rotation:

```css
.hamburger-line {
  display: block;
  width: 24px; height: 2px;
  background: var(--text-primary);
  transition: transform 0.3s ease, opacity 0.2s ease;
}
.hamburger.open .hamburger-line:nth-child(1) {
  transform: translateY(8px) rotate(45deg);
}
.hamburger.open .hamburger-line:nth-child(2) {
  opacity: 0;
}
.hamburger.open .hamburger-line:nth-child(3) {
  transform: translateY(-8px) rotate(-45deg);
}
```

### Tab Indicator Slide

Active tab indicator slides to follow selection:

```svelte
<script>
  let activeIndex = $state(0);
  let tabRects = $state([]);

  function updateIndicator(el, index) {
    const rect = el.getBoundingClientRect();
    const parent = el.parentElement.getBoundingClientRect();
    tabRects[index] = {
      left: rect.left - parent.left,
      width: rect.width,
    };
  }
</script>

<div class="tab-bar" style="position: relative;">
  {#each tabs as tab, i}
    <button
      class="tab"
      class:active={i === activeIndex}
      onclick={() => { activeIndex = i; }}
      use:measureTab={i}
    >{tab}</button>
  {/each}
  <div
    class="tab-indicator"
    style="
      left: {tabRects[activeIndex]?.left ?? 0}px;
      width: {tabRects[activeIndex]?.width ?? 0}px;
    "
  ></div>
</div>

<style>
  .tab-indicator {
    position: absolute;
    bottom: 0; height: 2px;
    background: var(--accent-default);
    transition: left 0.25s cubic-bezier(0.22, 1, 0.36, 1),
                width 0.25s cubic-bezier(0.22, 1, 0.36, 1);
  }
</style>
```

### Breadcrumb Transitions

When navigating deeper, new breadcrumb segments slide in from the right:

```css
.breadcrumb-item {
  animation: slideInRight 0.2s ease forwards;
}
@keyframes slideInRight {
  from { opacity: 0; transform: translateX(8px); }
  to { opacity: 1; transform: translateX(0); }
}
```

---

## 4. Scroll-Driven Animations

### Staggered Reveal on Scroll

Elements fade up as they enter the viewport with increasing delays:

```svelte
<script>
  function staggerReveal(node, { delay = 0 }) {
    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) {
        node.style.transitionDelay = `${delay}ms`;
        node.classList.add('revealed');
        observer.unobserve(node);
      }
    }, { threshold: 0.15 });
    observer.observe(node);
    return { destroy: () => observer.disconnect() };
  }
</script>

<style>
  .stagger-item {
    opacity: 0;
    transform: translateY(24px);
    transition: opacity 0.5s ease, transform 0.5s cubic-bezier(0.22, 1, 0.36, 1);
  }
  .stagger-item.revealed {
    opacity: 1;
    transform: translateY(0);
  }
</style>

{#each items as item, i}
  <div class="stagger-item" use:staggerReveal={{ delay: i * 80 }}>
    {item}
  </div>
{/each}
```

### Progress Bar on Scroll

A thin bar at the top of the page showing scroll progress:

```svelte
<script>
  let progress = $state(0);

  function handleScroll() {
    const winScroll = document.documentElement.scrollTop;
    const height = document.documentElement.scrollHeight - window.innerHeight;
    progress = (winScroll / height) * 100;
  }
</script>

<svelte:window onscroll={handleScroll} />

<div class="scroll-progress" style="width: {progress}%"></div>

<style>
  .scroll-progress {
    position: fixed;
    top: 0; left: 0;
    height: 3px;
    background: var(--accent-default);
    z-index: 9999;
    transition: width 0.1s linear;
  }
</style>
```

### Counter Animation on Scroll

Numbers count up from 0 when the stat enters the viewport:

```svelte
<script>
  function countUp(node, { target, duration = 1500 }) {
    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) {
        const start = performance.now();
        function tick(now) {
          const elapsed = now - start;
          const ratio = Math.min(elapsed / duration, 1);
          const eased = 1 - Math.pow(1 - ratio, 3); // ease-out cubic
          node.textContent = Math.round(eased * target).toLocaleString();
          if (ratio < 1) requestAnimationFrame(tick);
        }
        requestAnimationFrame(tick);
        observer.unobserve(node);
      }
    }, { threshold: 0.5 });
    observer.observe(node);
    return { destroy: () => observer.disconnect() };
  }
</script>

<span class="counter" use:countUp={{ target: 42000 }}>0</span>
```

---

## 5. Form and Input Interactions

### Floating Label

Label starts as placeholder, floats up when input is focused or filled:

```css
.field-group {
  position: relative;
}
.field-input {
  padding: 1.25rem 1rem 0.5rem;
  border: 1.5px solid var(--border-default);
  border-radius: 0.5rem;
  background: var(--base-100);
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
  width: 100%;
}
.field-label {
  position: absolute;
  left: 1rem; top: 50%;
  transform: translateY(-50%);
  color: var(--text-tertiary);
  font-size: var(--text-base);
  pointer-events: none;
  transition: all 0.2s ease;
}
.field-input:focus,
.field-input:not(:placeholder-shown) {
  border-color: var(--primary-default);
  box-shadow: 0 0 0 3px hsl(var(--primary-hue), 50%, 50%, 0.12);
}
.field-input:focus + .field-label,
.field-input:not(:placeholder-shown) + .field-label {
  top: 0.5rem;
  transform: translateY(0);
  font-size: var(--text-xs);
  color: var(--primary-default);
}
```

### Validation Feedback

Instant visual feedback as the user types:

```css
.field-input.valid {
  border-color: hsl(145, 50%, 45%);
}
.field-input.invalid {
  border-color: hsl(0, 55%, 50%);
  animation: shake 0.3s ease;
}
@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-4px); }
  75% { transform: translateX(4px); }
}
```

### Checkbox Animation

Custom checkbox with a smooth checkmark draw:

```css
.checkbox-custom {
  width: 20px; height: 20px;
  border: 2px solid var(--border-strong);
  border-radius: 4px;
  position: relative;
  transition: background 0.15s ease, border-color 0.15s ease;
}
.checkbox-custom.checked {
  background: var(--primary-default);
  border-color: var(--primary-default);
}
.checkbox-custom .checkmark {
  stroke-dasharray: 20;
  stroke-dashoffset: 20;
  transition: stroke-dashoffset 0.2s ease 0.05s;
}
.checkbox-custom.checked .checkmark {
  stroke-dashoffset: 0;
}
```

---

## 6. Loading and State Transitions

### Skeleton Loading

Placeholder shapes that pulse while content loads:

```css
.skeleton {
  background: linear-gradient(
    90deg,
    var(--base-200) 25%,
    var(--base-300) 37%,
    var(--base-200) 63%
  );
  background-size: 400% 100%;
  animation: shimmer 1.5s ease-in-out infinite;
  border-radius: 0.375rem;
}
@keyframes shimmer {
  0% { background-position: 100% 50%; }
  100% { background-position: 0 50%; }
}
.skeleton-text { height: 1rem; width: 80%; margin-bottom: 0.5rem; }
.skeleton-title { height: 1.5rem; width: 60%; margin-bottom: 1rem; }
.skeleton-avatar { height: 48px; width: 48px; border-radius: 50%; }
```

### Success/Error State Transitions

After form submission, elements transition to success/error states:

```css
.submit-btn.success {
  background: hsl(145, 50%, 45%);
  transform: scale(1);
  transition: all 0.3s ease;
}
.submit-btn.success::after {
  content: '✓';
  animation: popIn 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}
@keyframes popIn {
  from { transform: scale(0); }
  to { transform: scale(1); }
}
```

### Content Swap (Cross-Fade)

When content changes (tab switch, data update), cross-fade:

```css
.content-panel {
  transition: opacity 0.15s ease;
}
.content-panel.exiting {
  opacity: 0;
}
.content-panel.entering {
  animation: fadeSlideUp 0.25s ease forwards;
}
@keyframes fadeSlideUp {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}
```

---

## 7. Page and Route Transitions

### SvelteKit Page Transitions

```svelte
<!-- +layout.svelte -->
<script>
  import { page } from '$app/stores';
  import { fade, fly } from 'svelte/transition';

  let { children } = $props();
</script>

{#key $page.url.pathname}
  <!-- Asymmetric: enter is longer (250ms) than exit (150ms) -->
  <main in:fade={{ duration: 250, delay: 100 }} out:fade={{ duration: 150 }}>
    {@render children()}
  </main>
{/key}
```

### Directional Transitions

Navigate forward: content slides in from right. Navigate back: content slides in from left.
Track navigation direction via a store.

### Spring-Based Modal / Dialog

Modals and dialogs use physically-modeled spring animation for a natural, responsive
feel. The spring curve overshoots slightly on enter, giving the dialog a sense of
weight and arrival. Exit is quick and decisive — no spring, just accelerate out.

```svelte
<!-- Modal.svelte -->
<script>
  let { open = $bindable(false), children } = $props();

  function handleBackdropClick(e) {
    if (e.target === e.currentTarget) open = false;
  }
</script>

{#if open}
  <!-- Backdrop: fast fade enter, faster fade exit -->
  <div
    class="modal-backdrop"
    onclick={handleBackdropClick}
    role="dialog"
    aria-modal="true"
    in:fade={{ duration: 250 }}
    out:fade={{ duration: 150 }}
  >
    <!-- Dialog: spring enter, accelerate exit -->
    <div
      class="modal-panel"
      in:scale={{ start: 0.92, duration: 400, easing: cubicOut }}
      out:scale={{ start: 0.95, duration: 200 }}
    >
      {@render children()}
    </div>
  </div>
{/if}

<style>
  .modal-backdrop {
    position: fixed;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    background: hsl(0, 0%, 0%, 0.5);
    backdrop-filter: blur(4px);
    z-index: 1000;
  }
  .modal-panel {
    background: var(--base-100);
    border-radius: 1rem;
    padding: 2rem;
    max-width: min(90vw, 32rem);
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
    /* Spring easing via CSS for any additional transitions */
    transition: transform var(--duration-enter-slow) var(--ease-spring);
  }
</style>
```

**CSS-only spring modal** (for simpler cases without Svelte transitions):

```css
.modal-panel {
  /* Enter: spring — overshoots slightly, settles naturally */
  animation: modal-spring-in var(--duration-enter-slow) var(--ease-spring) forwards;
}
.modal-panel.closing {
  /* Exit: accelerate out — quick, decisive dismissal */
  animation: modal-spring-out var(--duration-exit-slow) var(--ease-exit) forwards;
}

@keyframes modal-spring-in {
  from {
    opacity: 0;
    transform: scale(0.9) translateY(10px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}
@keyframes modal-spring-out {
  from {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
  to {
    opacity: 0;
    transform: scale(0.95) translateY(5px);
  }
}
```

The spring curve `--ease-spring: cubic-bezier(0.22, 1.4, 0.36, 1)` creates a
slight overshoot (the `1.4` exceeds the normal `1.0` endpoint), giving dialogs
a physical weight that flat easing lacks.

---

## 8. Haptic-Feel Patterns

Creating the sensation of physical interaction through visual feedback.

### The Press Effect

When a user clicks any interactive element, it should feel like pressing a physical button:

```css
.pressable:active {
  transform: scale(0.97);
  transition: transform var(--duration-instant) var(--ease-standard);
}
```

### The Bounce-Back

Elements that are dragged or stretched return to position with a spring animation:

```css
.bounce-back {
  transition: transform var(--duration-enter-slow) var(--ease-bounce);
}
```

### Card Lift on Interaction

Cards elevate (shadow increases, slight scale) when hovered, suggesting they can be
picked up:

```css
.card-lift {
  transition: transform var(--duration-enter-fast) var(--ease-enter),
              box-shadow var(--duration-enter-fast) var(--ease-enter);
}
.card-lift:hover {
  transform: translateY(-4px) scale(1.01);
  box-shadow: var(--shadow-lg);
}
```

### Ripple Effect (Material-Style)

A circular ripple emanates from the click point:

```svelte
<script>
  function ripple(node) {
    function handleClick(e) {
      const circle = document.createElement('span');
      const rect = node.getBoundingClientRect();
      const size = Math.max(rect.width, rect.height);
      circle.style.width = circle.style.height = `${size}px`;
      circle.style.left = `${e.clientX - rect.left - size / 2}px`;
      circle.style.top = `${e.clientY - rect.top - size / 2}px`;
      circle.classList.add('ripple-circle');
      node.appendChild(circle);
      circle.addEventListener('animationend', () => circle.remove());
    }
    node.style.position = 'relative';
    node.style.overflow = 'hidden';
    node.addEventListener('click', handleClick);
    return { destroy: () => node.removeEventListener('click', handleClick) };
  }
</script>

<style>
  :global(.ripple-circle) {
    position: absolute;
    border-radius: 50%;
    background: currentColor;
    opacity: 0.15;
    transform: scale(0);
    animation: rippleExpand 0.5s ease-out;
    pointer-events: none;
  }
  @keyframes rippleExpand {
    to { transform: scale(2.5); opacity: 0; }
  }
</style>

<button use:ripple>Click me</button>
```

---

## 9. Snap and Magnetic Behaviors

### Scroll Snap (CSS Native)

```css
.scroll-container {
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  scroll-behavior: smooth;
  -webkit-overflow-scrolling: touch;
}
.scroll-item {
  scroll-snap-align: start;
  flex: 0 0 auto;
}
```

### Magnetic Button (Cursor Attraction)

Button subtly moves toward the cursor when nearby:

```svelte
<script>
  function magnetic(node, { strength = 0.3, distance = 80 }) {
    function handleMouseMove(e) {
      const rect = node.getBoundingClientRect();
      const cx = rect.left + rect.width / 2;
      const cy = rect.top + rect.height / 2;
      const dx = e.clientX - cx;
      const dy = e.clientY - cy;
      const dist = Math.sqrt(dx * dx + dy * dy);

      if (dist < distance) {
        const pull = (1 - dist / distance) * strength;
        node.style.transform = `translate(${dx * pull}px, ${dy * pull}px)`;
      } else {
        node.style.transform = '';
      }
    }
    function handleMouseLeave() {
      node.style.transform = '';
      node.style.transition = 'transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)';
      setTimeout(() => { node.style.transition = ''; }, 300);
    }
    window.addEventListener('mousemove', handleMouseMove);
    node.addEventListener('mouseleave', handleMouseLeave);
    return {
      destroy() {
        window.removeEventListener('mousemove', handleMouseMove);
        node.removeEventListener('mouseleave', handleMouseLeave);
      }
    };
  }
</script>

<button use:magnetic={{ strength: 0.25, distance: 100 }}>Hover near me</button>
```

### Sticky Snap Header

Header that toggles between transparent (at top) and solid (on scroll):

```svelte
<script>
  let scrolled = $state(false);

  function handleScroll() {
    scrolled = window.scrollY > 50;
  }
</script>

<svelte:window onscroll={handleScroll} />

<header class="header" class:scrolled>
  <!-- nav content -->
</header>

<style>
  .header {
    position: fixed; top: 0; left: 0; right: 0;
    z-index: 100;
    padding: 1.5rem 2rem;
    transition: all var(--duration-enter) var(--ease-standard);
    background: transparent;
  }
  .header.scrolled {
    padding: 0.75rem 2rem;
    background: hsl(var(--base-hue), var(--base-sat), var(--base-light), 0.9);
    backdrop-filter: blur(12px);
    box-shadow: 0 1px 0 var(--border-default);
  }
</style>
```

---

## 10. Performance and Accessibility

### GPU-Composited Properties Only

For 60fps animations, ONLY animate these properties:
- `transform` (translate, rotate, scale)
- `opacity`
- `filter` (blur, brightness)
- `clip-path` (with care)

NEVER animate: `width`, `height`, `margin`, `padding`, `border-width`, `top/left/right/bottom`,
`font-size`, `color` (use opacity + overlay instead), `box-shadow` (pre-render both states).

### `will-change` Usage

```css
/* Apply BEFORE animation starts, remove AFTER */
.about-to-animate { will-change: transform, opacity; }
/* Never apply will-change to everything or leave it permanently */
```

### `prefers-reduced-motion`

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

### `contain` for Layout Isolation

```css
.animated-card {
  contain: layout paint;
  /* Prevents repaints from cascading to parent/sibling elements */
}
```

---

## 11. Easing and Timing Reference

### Emphasized Easing Curves (MD3-Derived)

Use these as your primary curves. They replace generic `ease` and `ease-in-out`
throughout the codebase. The key insight: **enter and exit are different motions**
and should use different curves.

| Token | CSS Value | Use For |
|-------|-----------|---------|
| **`--ease-enter`** | `cubic-bezier(0.2, 0, 0, 1)` | Elements appearing: modals, dropdowns, reveals, fade-ins |
| **`--ease-exit`** | `cubic-bezier(0.3, 0, 0.8, 0.15)` | Elements leaving: dismiss, close, fade-outs |
| **`--ease-standard`** | `cubic-bezier(0.2, 0, 0, 1)` | State changes: hover, color, opacity (no enter/exit) |
| **`--ease-bounce`** | `cubic-bezier(0.34, 1.56, 0.64, 1)` | Playful enters, toggles, switches |
| **`--ease-spring`** | `cubic-bezier(0.22, 1.4, 0.36, 1)` | Modals, dialogs, spring-feel elements |
| **`--ease-snap`** | `cubic-bezier(0.68, -0.55, 0.27, 1.55)` | Quick decisive state changes |
| **Linear** | `linear` | Only for progress bars, clocks, shimmer loops |

**NEVER** use bare `ease`, `ease-in`, `ease-out`, or `ease-in-out` — always use
the tokens above. Generic curves feel flat and lifeless compared to emphasized curves.

### Duration Guidelines (Asymmetric)

Enter durations are longer than exits. Use the token, not a raw millisecond value.

| Action | Enter | Exit | Easing (Enter / Exit) |
|--------|-------|------|-----------------------|
| Button hover/active | `--duration-fast` | `--duration-instant` | `--ease-standard` / `--ease-standard` |
| Tooltip appear/dismiss | `--duration-enter-fast` | `--duration-exit-fast` | `--ease-enter` / `--ease-exit` |
| Dropdown open/close | `--duration-enter` | `--duration-exit` | `--ease-enter` / `--ease-exit` |
| Modal open/close | `--duration-enter-slow` | `--duration-exit-slow` | `--ease-spring` / `--ease-exit` |
| Page transition | `--duration-enter-slow` | `--duration-exit` | `--ease-enter` / `--ease-exit` |
| Skeleton shimmer | 1500ms (loop) | — | ease-in-out |
| Scroll reveal | `--duration-enter-dramatic` | — | `--ease-enter` |
| Counter animation | 1000-2000ms | — | `--ease-enter` |
