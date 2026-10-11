# Anatomy of a directed motion prompt

A directed prompt is not long for its own sake. Each line removes one decision the model would
otherwise make, and the model's own decisions are the default look. Anthropic's Opus 5.5 prompting
guidance says the same: without design direction the model "falls back on a few default styles", and
a general line like "avoid a generic AI look" mostly swaps one default for another. What works is
naming the exact patterns to avoid, checking which defaults the first result used, and extending the list.

## The template, line by line

```
GOAL:   what the viewer should feel or do, in one sentence
OUTPUT: one self-contained HTML file (or Remotion, HyperFrames), W x H
TIME:   seconds x fps = total frames. Loop: yes or no
LOOK:   palette in hex, one accent, typeface + weight + size + tracking
MOTION: easing as cubic-bezier, springs as damping ratio, durations in frames
SHOTS:  frame ranges, one hero move per shot, how each shot hands off
BANNED: the defaults you never want to see
QA:     stills at named frames, a contact sheet, fix, then the full render
```

- **GOAL first.** If it cannot be said in one sentence what the viewer should feel or do, the piece cannot be animated, and no easing curve rescues it.
- **TIME second.** Every other number hangs off the frame count. With music, add BPM and put hits on beats.
- **OUTPUT names the engine and its numbers.** "A Remotion composition, 1920 x 1080, 30 fps, 450 frames" leaves nothing to guess. Pin library versions ("three.js 0.160.0 via jsdelivr importmap").
- **LOOK in hex.** One accent, used in one place. Name the typeface, weight, size and tracking.
- **MOTION in curves and frames.** Motion designers talk in curves and frames, so give the model curves and frames.
- **SHOTS is where the story lives.** Each shot gets a frame range, one hero move and a handoff: a hard cut on the beat, a match cut where one shape becomes the next, or a mask wipe. Default to the cut. A transition should be a decision.
- **QA matters more than it looks.** It makes the model check stills before rendering the whole clip; that is where the lab loop starts.
- **3D adds MODEL, CAMERA and LIGHTS.** Units and sizes for every part, materials with roughness, metalness and clearcoat, a camera that never parks.
- **KEEP is the guardrail.** Say what may not change, in numbers. The mascot piece kept "a 14x10 body, 3x2 arms, 2x3 legs and 2x3 eyes, built from 0.1 voxels and 8 deep" so the character stayed recognizable in 3D. Every style you care about needs a line like that.

## The ban list

Start from this list, then extend it after every first render with what the model used anyway:

- purple or blue gradients, glow, lens flares (and bloom, neon, glow orbs for product work)
- floating particles as decoration
- everything fading in at once
- fade-and-slide-up on every element (Anthropic's frontend-design skill calls this the generic default that reads as AI-generated)
- centered-everything layouts
- text that moves while it is being read
- for studio product shots: dark backgrounds, spinning turntables, made-up taglines

## Hierarchy

One hero per shot. A single orchestrated moment lands better than scattered effects. Everything else
waits, dims to 40%, or holds still. Then rank the rest: secondary moves travel 50 to 70% as far as the
hero and start 100 to 200 ms after it. Ambient motion stays under 5% of the hero's travel, runs on a
slow sine and never stops.

## Translate feelings into numbers

When a request or a note arrives as a feeling, translate it before acting on it.

| Feeling | Numbers |
|---|---|
| "Make it pop" | scale 1.0 to 1.08 to 1.0 over 6 frames, peak on the beat |
| "Make it feel premium" | ease-out-quint on entrances, springs at damping ratio 0.8, no overshoot on text |
| "It drags" | shorten each hold by 12 frames (one beat at 120 BPM and 24 fps) so every cut stays on the grid |
| "It feels busy" | one hero move at a time; everything else starts 150 ms later at 60% of its travel |
| "It looks like AI" | list the defaults it used by name, ban each one, render again |

From the vague-versus-directed experiment (same model, same subject, only the direction changed):

| Adjective | What it became |
|---|---|
| "Premium" | materials: satin ceramic at roughness 0.38 with a 0.35 clearcoat, chrome at roughness 0.05, the accent only on one surface |
| "Cool" | a studio: key, fill and rim lights with exact colors and strengths, reflections from a studio built in code, soft contact shadows, no glow anywhere |
| "Modern" | a camera: 30-degree field of view, never parked, an orbit from 34 to 10 degrees, one push-in on easeOutExpo at 2.0 s |
| "Animation" | beats and springs: 120 BPM, a 3-frame anticipation before the lid springs open at damping 0.6, buds rising at 0.7 with a looser 0.5 follow-through |
| (unstated defaults) | named and banned: bloom, glow orbs, neon, particles, spinning turntables, dark backgrounds, text |

The vague prompt (27 words, "cool", "premium and modern") came back as dark navy space, a glowing
halo ring, bloom, particles, spinning buds and a made-up tagline: most of the directed prompt's
banned list. Full prompts in `examples.md`.

## Scale of effort, honestly

"One prompt" pieces in the feed are usually a long brief plus hours of autonomous work or several
review rounds. The lab's own counts: 10, 15 and 4 creative follow-ups on 400-word prompts. Plan for
two to four review rounds. Keep the numbers on the first run and change only the words; on the
second run change one number at a time, so you can see what each one does.
