# When an experiment breaks

The same failures come back in every project. Each row carries the fix to paste.

| Symptom | Paste this fix |
|---|---|
| Flicker or jitter | Make every value a pure function of t. Replace Math.random with a seeded generator. Remove timers and CSS transitions. |
| Wrong or fallback font | Load the font with display=block and wait for document.fonts.ready before the first frame. |
| Hiccup at the loop seam | Render frames 0 to N-1 only. Drive the loop from phase = frame / N with whole cycles. |
| Audio drifts off the beat | Compute each beat as n x 60 / BPM and round per beat. Never add a rounded frame count. |
| Jank or dropped frames | Animate only transform and opacity. No width, height, top or left. |
| Banding in the GIF | No gradients. Flat colors only, or dither the palette. |
| Blurry or shimmering text | Snap resting text to whole pixels. Render at 2x (`--scale 2`) and scale down. |
| Text moves before you can read it | Hold every text state 0.3 s per word plus 0.5 s before it moves. |
| Everything moves at once | One hero move at a time. Others start 150 ms later at 60% of its travel. |

If a fix does not hold, render the two frames on either side of the problem and compare them:

> The fix at frame 84 did not hold. Render frames 83 and 85 as PNGs, put them side by side and list
> every difference you can see. Find the line of code that causes it, fix only that line, then render
> both frames again.

When a fix works, add it to the render contract. The contract is the lab's memory: every line in it
is a failure you never have to see again.

## Pitfalls found while building this skill (2026-10-10)

These are not in the article. Each was hit and fixed while testing the scripts here.

| Symptom | Cause | Fix |
|---|---|---|
| Module import, texture or local font fails in the render | `file://` pages cannot load ES modules or local assets (CORS) | `render.mjs` serves the folder over a local HTTP server by default. For a one-file piece, paste `motion.js` inline. |
| WebGL canvas renders black headless | No GPU in headless Chromium | `render.mjs` launches with SwiftShader flags. Slow for heavy shaders; use a GPU machine for showcase renders. |
| The page's own preview loop fights the renderer | A `requestAnimationFrame` loop keeps drawing between `renderAt(t)` and the screenshot | The renderer opens `?t=0`; the contract says a page with `?t=` starts no clock. |
| First frames render before fonts, textures or bakes finish | Async setup | The page sets `window.__ready = false`, then true; the renderer waits for it. |
| Overdamped spring settles too fast | The article's `spring()` treats any damping ratio above 1 as exactly 1 | Use `motion.js`, which has the overdamped branch. At zeta 3, t 0.2 s, f 2 Hz the article's version returns 0.715 instead of 0.331. |
| Motion blur shows stepped ghosts | Too few subframes for the distance moved in half a frame | Raise `--blur` (8 to 16) for that shot. |
| Script decides a feature is missing when it is present | `cmd | grep -q` under `set -o pipefail`: grep exits early, the producer dies of SIGPIPE, the pipeline fails | Capture the output to a variable, then test it. |
