// motion.js: one tokens file, used everywhere, no inline numbers.
// Paste it into the piece's <script type="module"> (a one-file HTML piece cannot import a
// sibling file over file://), or import it when the piece is served (render.mjs serves it).
// Tokens and spring from "Opus 5.5 Motion Lab" by @flxrnc (X, 2026-09-30); the overdamped
// branch, cubicBezier, beat, hold and seeded-random helpers are additions. See ../README.md.

// CSS easing strings (Andrey Sitnik's easings.net values)
export const EASE = {
  enter: 'cubic-bezier(0.16, 1, 0.3, 1)',    // ease-out-expo: text and logo reveals
  premium: 'cubic-bezier(0.22, 1, 0.36, 1)', // ease-out-quint: premium entrances
  move:  'cubic-bezier(0.76, 0, 0.24, 1)',   // ease-in-out-quart: moves and camera pushes
  exit:  'cubic-bezier(0.7, 0, 0.84, 0)',    // ease-in-expo: fast exits
  pop:   'cubic-bezier(0.34, 1.56, 0.64, 1)' // ease-out-back: playful pop with overshoot
};
export const BEZIER = {
  enter: [0.16, 1, 0.3, 1], premium: [0.22, 1, 0.36, 1], move: [0.76, 0, 0.24, 1],
  exit: [0.7, 0, 0.84, 0], pop: [0.34, 1.56, 0.64, 1]
};
export const MS = { feedback: 150, move: 400, hero: 750, exit: 240 };
export const STAGGER = { letter: 30, word: 90, item: 60 };

// A cubic-bezier easing as a JS function of progress p in 0..1, for motion drawn in renderAt(t).
export function cubicBezier(x1, y1, x2, y2) {
  const bx = (u) => 3 * x1 * u * (1 - u) ** 2 + 3 * x2 * u * u * (1 - u) + u ** 3;
  const by = (u) => 3 * y1 * u * (1 - u) ** 2 + 3 * y2 * u * u * (1 - u) + u ** 3;
  return (p) => {
    if (p <= 0) return 0;
    if (p >= 1) return 1;
    let lo = 0, hi = 1, u = p;
    for (let i = 0; i < 40; i++) {           // bisection: monotonic in x, always converges
      u = (lo + hi) / 2;
      if (bx(u) < p) lo = u; else hi = u;
    }
    return by(u);
  };
}
export const ease = Object.fromEntries(Object.entries(BEZIER).map(([k, v]) => [k, cubicBezier(...v)]));

// Progress of a move that starts at t0 and lasts dur seconds, eased, clamped to 0..1.
export const tween = (t, t0, dur, fn = ease.move) => fn(Math.min(1, Math.max(0, (t - t0) / dur)));

// Damping ratio from any library's numbers: 1 = no bounce, 0.7 to 0.85 premium,
// 0.4 to 0.6 playful, under 0.3 cartoon. Remotion's default (k 100, d 10, m 1) is 0.5;
// react-spring's default (tension 170, friction 26) is 1.0.
export const dampingRatio = (k, d, m = 1) => d / (2 * Math.sqrt(k * m));

// A spring as a pure function of time, from 0 at rest to 1 settled. No simulation, so
// frame 84 renders on its own. zeta: damping ratio. f: natural frequency in Hz.
export function spring(t, zeta = 0.7, f = 2) {
  if (t <= 0) return 0;
  const w = 2 * Math.PI * f;
  if (zeta === 1) return 1 - Math.exp(-w * t) * (1 + w * t);         // critical: no bounce
  if (zeta > 1) {                                                     // overdamped: slower, no bounce
    const s = Math.sqrt(zeta * zeta - 1);
    const r1 = -w * (zeta - s), r2 = -w * (zeta + s);
    return 1 - (r2 * Math.exp(r1 * t) - r1 * Math.exp(r2 * t)) / (r2 - r1);
  }
  const wd = w * Math.sqrt(1 - zeta * zeta);                          // underdamped: bounces
  return 1 - Math.exp(-zeta * w * t) * (Math.cos(wd * t) + (zeta * w / wd) * Math.sin(wd * t));
}

// Frames and beats. Compute every beat from time and round each one; never add a rounded
// frame count again and again (at 128 BPM and 30 fps that drifts 2 frames in 32 beats).
export const framesPerBeat = (bpm, fps) => fps * 60 / bpm;
export const beatFrame = (n, bpm, fps) => Math.round(n * 60 * fps / bpm);
export const msToFrames = (ms, fps) => Math.round(ms * fps / 1000);

// Text holds: at least 0.3 s per word plus 0.5 s.
export const holdSeconds = (words) => 0.3 * words + 0.5;

// Loops: drive every cycle from phase = frame / N with whole-number cycles.
export const loopPhase = (t, loopSeconds) => (((t / loopSeconds) % 1) + 1) % 1;
export const loopWave = (t, loopSeconds, cycles = 1) => Math.sin(2 * Math.PI * cycles * loopPhase(t, loopSeconds));

// Seeded randomness: the same seed gives the same shapes on every frame and every run.
export function seeded(seed = 1) {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6D2B79F5) >>> 0;
    let x = Math.imul(a ^ (a >>> 15), 1 | a);
    x = (x + Math.imul(x ^ (x >>> 7), 61 | x)) ^ x;
    return ((x ^ (x >>> 14)) >>> 0) / 4294967296;
  };
}
