---
name: motion-lab
description: Direct motion design that looks studio-made instead of AI-default, built as code that paints frames (HTML, CSS, SVG, Canvas or three.js) and rendered frame-exact with Playwright and ffmpeg. Use when asked to animate something, make a motion loop, GIF or MP4 for X, a product shot, logo sting, title reveal, 3D scene or launch clip, or when existing motion looks generic, janky, jittery, late on the beat, or hiccups at the loop seam. Supplies the directed-prompt template, the render contract, the motion numbers (easing, springs, durations, stagger, beat grid), the render-look-fix loop with frame-numbered notes, synthesized sound synced to frames, loop and export rules for X, and a symptom-to-fix table. For HyperFrames or Remotion projects, use those skills for engine mechanics and this one for direction and QA.
tags:
- motion-design
- animation
- video
- three-js
- playwright
- ffmpeg
- creative-coding
- prompting
source: custom
---

# Motion Lab

Claude does not generate pixels. It writes a program that paints pixels, and a headless browser
records it. Three things follow, and this skill uses all three:

1. **Every frame is reproducible.** Every pixel is a pure function of `t`. Render frame 84 twice, get the same image twice.
2. **Edits are cheap.** Change one number, re-render. No re-rolling.
3. **The work can be checked.** Render stills and contact sheets, look at them, fix by frame number.

The core lesson: **adjectives are where the default look lives.** "Premium", "modern", "cool"
produce dark navy space, glow, bloom, particles and a spinning turntable. Every adjective replaced
with a number is a decision taken back from the model's defaults.

Source: "Opus 5.5 Motion Lab: Make Claude Animate Like a Studio" by Florence (@flxrnc), X, 2026-09-30.
See README.md for provenance and what changed.

## Workflow

Follow these steps in order. Do not skip step 2 because the request is short. A short request is
exactly the case where the defaults take over.

### 1. Set up the lab folder (once per project)

```bash
mkdir -p motion-lab && cd motion-lab
npm init -y && npm i -D playwright && npx playwright install chromium
cp <skill>/scripts/*.mjs <skill>/scripts/*.sh <skill>/scripts/motion.js .
```

Needs Node and ffmpeg on PATH. `render.mjs` resolves Playwright from the current folder, so the
scripts also run in place from the skill directory.

### 2. Write the brief: fill every line of the template

Copy `assets/directed-prompt.txt` to `BRIEF.md` in the project and fill every line before building.
Write **GOAL** first: one sentence on what the viewer should feel or do. If it cannot be said in one
sentence, nothing downstream rescues the piece. Write **TIME** second, because every other number
hangs off the frame count. Then LOOK, MOTION, SHOTS, BANNED, QA (and MODEL, CAMERA for 3D).

- Turn every adjective in the request into numbers. See "Translate feelings into numbers" in `references/prompt-anatomy.md`.
- Pick the engine and put it in OUTPUT with its numbers (`references/engines.md`).
- Pick the canvas before frame 1: 1080x1080 (1:1), 1080x1350 (4:5), 1920x1080 (16:9), 1080x1920 (9:16).
- When the user gave no numbers, choose them from `references/motion-numbers.md` and state them in the brief, so the user can change one at a time.
- Add a guardrail line for anything that must not change (a character's proportions, a logo's geometry, brand colors).

### 3. Build against the render contract

Paste `assets/render-contract.txt` under the brief, and build one self-contained HTML file that
honors it. Put every number in one tokens block at the top (`scripts/motion.js` has easings,
springs, beat and hold helpers, and seeded randomness). Use no inline numbers in the motion code.
Add the freeze snippet (`assets/freeze-snippet.html`) so `anim.html?t=2.5` shows exactly that frame.
`examples/demo.html` is a small working piece that follows every rule.

### 4. Run the lab loop: render, look, fix

The first render is a draft. Two to four rounds is normal.

1. Render stills at named frames, not the whole clip:
   `node render.mjs anim.html 6 24 --size 1080x1080 --frames 0,24,48,72,96 --out out/stills`
2. **Read the PNGs.** Describe each in one sentence as a viewer would and compare with the shot list.
3. Make a contact sheet of the whole clip: `./contact-sheet.sh out/frames 12 4 3` (tiles carry frame numbers).
4. Write notes that point at frames, not feelings: "the punch at frame 84 peaks late, move it 2 frames earlier".
5. Fix, then re-render only what changed (`--from`/`--to` or `--frames`).

Use one or two of the review moves in `assets/follow-ups.txt` per round. Pasting all of them at
once turns a fix into a rewrite. After every first render, list the defaults the model used anyway
and add them to BANNED. Details and the onion-skin and speed-graph checks: `references/lab-loop.md`.

### 5. Final render and export

```bash
node render.mjs anim.html 6 60 --size 1080x1080 --blur 6     # 3D or fast moves: subframe motion blur
./export.sh mp4 60                                           # H.264 High, yuv420p, faststart
./export.sh gif 24 out/frames out/anim.gif 1200              # one palette; X: 15 MB, 350 frames max
./export.sh loop                                             # three loops back to back: watch the seam
```

A loop renders frames 0 to N-1, never N. Frame 0 must be a finished composition.
Full export rules and X limits: `references/last-mile.md`.

### 6. Sound, last and optional

The feed plays muted, so the picture must work in silence first. To add sound, synthesize it
in code with the Web Audio API and render it with `node audio.mjs render score.html out/score.wav`
(`examples/demo-score.html` shows the pattern). Then:

- Write the score against frame numbers. Each hit peaks **1 frame after** its picture.
- Mix with `./export.sh mux out/anim.mp4 out/final.mp4 out/score.wav`, which targets -14 LUFS with peaks at -1 dBTP.
- Verify the decoded MP4 with `node audio.mjs check out/final.mp4 --fps 24 --frames 36,84`.

Measure; do not trust a listen. Sound prompt shape and measured pitfalls: `references/last-mile.md`.

### 7. Keep receipts

Log every prompt and follow-up in `RECEIPTS.md`, split into creative follow-ups (change the look or
motion) and technical fixes. Count them. When posting, publish the prompt and every follow-up.
"One prompt" claims make people suspicious; receipts convince them.

## The rules that matter most

- **One hero per shot.** Secondary moves travel 50 to 70% as far and start 100 to 200 ms later. Ambient motion stays under 5% of the hero's travel, on a slow sine, and never stops.
- **Enter with ease-out, exit with ease-in**, exits 40 to 50% shorter. Move across the screen with ease-in-out. Linear easing only for rotation, progress bars and loop phase.
- **Springs by damping ratio:** 1.0 never bounces, 0.7 to 0.85 premium, 0.4 to 0.6 playful, under 0.3 cartoon. Position and size may bounce; opacity and color never do.
- **Durations in frames.** At 24 fps one frame is about 42 ms: 400 ms is 10 frames, 750 ms is 18.
- **Beat grid:** frames per beat = fps x 60 / BPM. Compute each beat from time and round each one; never add a rounded count repeatedly. Cut on the beat; change layout on the bar (every 4 beats).
- **Text holds** at least 0.3 s per word plus 0.5 s. Text never moves while it is being read.
- **Phone size:** push key poses 10 to 30% further than feels right. Keep text at 4.5:1 contrast on every frame. Never flash more than 3 times per second.
- **Transitions are decisions.** Default to a hard cut on the beat; use a match cut or mask wipe only on purpose.

The full numbers, with sources: `references/motion-numbers.md`.

## Starting ban list

Purple or blue gradients, glow, lens flares, bloom, neon. Floating particles as decoration. Everything
fading in at once. Fade-and-slide-up on every element. Centered-everything layouts. Text that moves
while it is being read. Dark backgrounds and spinning turntables when a studio look is wanted.
Keep the list alive: after each first render, name what the model used anyway and ban it by name.
A general line like "avoid a generic AI look" only swaps one default for another.

## When something breaks

Use the symptom table in `references/fixes.md`. If a fix does not hold, render the frames on either
side of the problem, compare them side by side, list every difference, and fix only the line that
causes it. When a fix works, add a line to the project's render contract. The contract is the
lab's memory: every line in it is a failure you never have to see again.

## Files

| Path | What it is |
|---|---|
| `assets/directed-prompt.txt` | The brief template, with MODEL, CAMERA and guardrail lines for 3D |
| `assets/render-contract.txt` | Paste under any motion prompt |
| `assets/freeze-snippet.html` | `?t=` freezes any frame by URL |
| `assets/follow-ups.txt` | Review moves for the lab loop, ready to paste |
| `assets/sound-prompt.txt` | Sound brief template written against frame numbers |
| `references/prompt-anatomy.md` | Line-by-line template guidance, feelings to numbers, vague vs directed |
| `references/motion-numbers.md` | Easing, springs, durations, stagger, beats, holds, camera, principles |
| `references/lab-loop.md` | Stills, contact sheets, onion skin, speed graph, review notes |
| `references/engines.md` | Three.js, Remotion, HyperFrames, GSAP, Motion, plain HTML: when to use each |
| `references/last-mile.md` | Sound, seamless loops, export commands, X limits |
| `references/fixes.md` | Symptom to fix table, plus pitfalls found while building this skill |
| `references/examples.md` | The article's three pieces: full prompts, every follow-up, sound prompts |
| `scripts/render.mjs` | Frame-exact renderer: `--size --scale --frames --from --to --blur --out` |
| `scripts/motion.js` | Tokens, `cubicBezier`, `spring`, `dampingRatio`, beat, hold, loop, seeded RNG |
| `scripts/contact-sheet.sh` | Every Nth frame on one image, labelled with frame numbers |
| `scripts/export.sh` | `mp4`, `gif`, `loop`, `mux` (two-pass -14 LUFS), `loudness` |
| `scripts/audio.mjs` | Render a Web Audio score to WAV; check hit timing in the decoded file |
| `examples/demo.html`, `examples/demo-score.html` | A 4 s loop and its score that follow every rule |
