# motion-lab

A skill that directs Claude to make studio-grade motion design as code: one HTML file whose every
frame is a pure function of time, rendered frame-exact with Playwright and ffmpeg, reviewed by frame
number, scored with synthesized sound, and exported for X.

## Source

Built from "Opus 5.5 Motion Lab: Make Claude Animate Like a Studio" by Florence
([@flxrnc](https://x.com/flxrnc)), an X Article posted 2026-09-30:
https://x.com/flxrnc/status/2105311836190978392

The author published the method and prompts in the article only. As of 2026-10-10 there is no
download, repository or skill: the article, the author's replies and the author's site have no link.
The article carries no license; the author keeps copyright. This skill is for personal use. The
example prompts in `references/examples.md` are quoted verbatim with credit so the worked examples
stay exact. Do not republish this skill without reworking or removing that file.

## What is from the article and what was added

From the article: the directed-prompt template, the render contract (first 8 lines), the ban list,
the motion numbers and principles table, the lab loop and review moves, the sound rules, the loop and
export commands, the X limits, the fixes table, and the three worked pieces.

Added or changed here, each tested on 2026-10-10 (Node 26, Playwright 1.62.1, Chromium 151, ffmpeg):

- `render.mjs`: viewport and scale flags, frame subsets for stills, a local HTTP server (file:// breaks modules and assets), `?t=0` so the page starts no clock, a `window.__ready` wait for async setup, awaited async `renderAt`, SwiftShader flags for headless WebGL, and `--blur` subframe motion blur blended in linear light (the article describes it but gives no code). Two full renders of `examples/demo.html` were byte-identical across all 96 frames.
- `motion.js`: fixed `spring()`, which treated every damping ratio above 1 as exactly 1; added `cubicBezier`, `tween`, beat, hold, loop and seeded-random helpers. Checked: settles at every ratio, no overshoot at 1 and above, 16.3% overshoot at 0.5 (theory 16.3%), Remotion default 0.5, react-spring default 0.997.
- `contact-sheet.sh`: tiles labelled with their source frame numbers.
- `export.sh`: two-pass loudness for `mux` (single-pass loudnorm misses the target on short loops), a `loudness` report, and warnings for X's GIF limits.
- `audio.mjs`: renders a Web Audio score to WAV and checks hit timing in any decoded file. The demo score's two landing hits peaked +0.0 ms from frame + 1, both in the WAV and after AAC muxing. The demo score is sparse (mostly silence between hits) and measures -15.5 LUFS after `mux`; `export.sh` flags that it is too peaky to reach -14 under a -1 dBTP ceiling, which is the intended warning.
- Verified that ffmpeg already mixes 40 and 50 ms GIF delays, so the article's GIF timing trap does not apply to ffmpeg exports.

## Other skills found, and why this one exists

Searched 2026-10-10. None reproduces the article's method:

- `howseen-ai/claude-motion-design` (MIT): the same HTML + Playwright + ffmpeg pipeline, written for one company's brand, assets and music library.
- `yazzang-homelab/motion-studio`: a plugin built from a different article (Movez's course); PolyForm Noncommercial license.
- `lottiefiles/motion-design-skill` (MIT): UI motion principles only.
- On this machine: the `hyperframes` and `remotion-best-practices` skills cover engines, not direction or QA. This skill points to them for engine mechanics.

## Try it

```bash
cd "$(mktemp -d)" && npm init -y >/dev/null && npm i -D playwright && npx playwright install chromium
S=<path to this skill>
cp $S/examples/demo.html $S/examples/demo-score.html .
node $S/scripts/render.mjs demo.html 4 24
$S/scripts/contact-sheet.sh out/frames 8 4 3
$S/scripts/export.sh mp4 24
node $S/scripts/audio.mjs render demo-score.html out/score.wav
$S/scripts/export.sh mux out/anim.mp4 out/final.mp4 out/score.wav
node $S/scripts/audio.mjs check out/final.mp4 --fps 24 --frames 36,84
```
