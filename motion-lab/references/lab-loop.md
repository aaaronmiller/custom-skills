# The lab loop: render, look, fix

The first render is a draft. The loop that finishes it: render stills, look at them, write notes with
frame numbers, fix, and re-render only what changed. Two to four rounds is normal.

## Freeze any frame by URL

The freeze snippet (`assets/freeze-snippet.html`) makes `anim.html?t=2.5` show the exact frame at
2.5 s. In a browser preview, also add a frame counter in a corner and a Space key that pauses, so
notes can name exact frames; hide both when `?t=` is present (`examples/demo.html` does this).

## Stills first

```bash
node render.mjs anim.html 6 24 --size 1080x1080 --frames 0,24,48,72,96 --out out/stills
```

Read each PNG. Describe it in one sentence as a viewer would, then compare it with the shot list.
Render stills around every hit and every transition, not just on round numbers. The chrome piece
found its worst defects by checking 12 transitions frame by frame (a bump that popped onto the blob
at frame 85).

## Contact sheet

```bash
node render.mjs anim.html 6 24 --size 1080x1080      # all frames to out/frames
./contact-sheet.sh out/frames 12 4 3 out/contact.png   # every 12th frame, 4 across, 3 down, labelled
```

The model reads a contact sheet like a storyboard. Use it to find frames where two things move at
once (a hierarchy problem), dead holds, and compositions that do not read at thumbnail size.

## Onion skin and speed graph

Two views borrowed from animators sharpen the notes:

- **Onion skin:** stack a run of frames at low opacity. Even spacing means robotic motion; spacing that tightens near the keys means the easing works. Quick version with ffmpeg: `ffmpeg -start_number 24 -i out/frames/%04d.png -frames:v 24 -vf "tmix=frames=24" -update 1 out/onion.png` (an average of frames 24 to 47; the last output frame holds the full stack).
- **Speed graph:** plot the hero's position per frame. Straight lines are linear motion; sharp corners are dead starts and stops. Have renderAt store the hero's numbers in `window.__probe`, sample them per frame through the renderer's page, and draw the chart on a canvas or with any plotting tool.

## Notes that work

Every note points at frames, not feelings, and carries a number:

- "The outer droplets leave the frame by 8 px around frame 112."
- "The anticipation holds 4 frames (57 to 60), not 3."
- "The glint reaches the O late and leaves the last 5 early."

Measure what can be measured. The earbuds piece counted pixels to prove a glint was lighting the whole
face ("strip on vs off changes 178,864 pixels"). The mascot piece ran a numeric audit of the live scene
on all 480 frames against the prompt's numbers: 71 checks, 6 failed on the first run, all fixed before
the final render.

Review moves ready to paste are in `assets/follow-ups.txt`. Pick one or two per round.

## Receipts

| Piece | Prompt words | Creative follow-ups | Frames |
|---|---|---|---|
| Opening shot, liquid chrome | 416 | 10 | 360 |
| Experiment 1, vague side | 27 | 0 (by design) | 360 |
| Experiment 1, directed side | 448 | 15 | 360 |
| Experiment 2, 3D mascot | 399 | 4 | 480 |

A creative follow-up is any note that changes how the piece looks or moves. Technical fixes (a
capture hook, font loading) are logged separately and do not count. Sound follow-ups: 5, 12 and 0.
Time: about 2 hours per 3D piece plus 45 to 90 minutes for sound.
