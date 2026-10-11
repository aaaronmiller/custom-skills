# The motion numbers

Give the model curves and frames. Every number below has a source or is marked as a lab starting point.
`scripts/motion.js` implements them as tokens; hand it over with one line: use only these tokens, no inline numbers.

## Easing

Values from the Easings reference by Andrey Sitnik (easings.net).

| Name | cubic-bezier | Use it for |
|---|---|---|
| ease-out-expo | 0.16, 1, 0.3, 1 | Text and logo reveals |
| ease-out-quint | 0.22, 1, 0.36, 1 | Premium entrances |
| ease-in-out-quart | 0.76, 0, 0.24, 1 | Moves and camera pushes |
| ease-in-expo | 0.7, 0, 0.84, 0 | Fast exits |
| ease-out-back | 0.34, 1.56, 0.64, 1 | A playful pop with overshoot |

Rules:
- Enter with ease-out, exit with ease-in, and make exits 40 to 50% shorter (Material 3 pairs a 400 ms entrance with a 200 ms exit).
- Move across the screen with ease-in-out.
- Linear only for rotation, progress bars and the phase of a loop. Linear easing on a move is the fastest way to make a render look like a render.
- Camera moves get the softest curves (ease-in-out-quart); objects get the snappier ones.

## Springs

Every library names its knobs differently. One number translates between all of them: the damping
ratio, `zeta = damping / (2 * sqrt(stiffness * mass))`.

| Damping ratio | Feel |
|---|---|
| 1.0 | never bounces |
| 0.7 to 0.85 | premium |
| 0.4 to 0.6 | playful |
| under 0.3 | cartoon |

- Remotion's default spring (mass 1, damping 10, stiffness 100) is 0.5; react-spring's default (tension 170, friction 26) is 1.0.
- Material 3's rule: position and size may bounce, opacity and color never do.
- `spring(t, zeta, f)` in motion.js returns progress at any t directly, with no simulation, so frame 84 renders without computing frames 0 to 83. That is what the render contract needs. It handles all three regimes; the article's version treated every zeta above 1 as exactly 1.

## Durations and stagger

| What | Duration |
|---|---|
| UI feedback | 100 to 200 ms (Nielsen Norman Group: 100 ms feels instant) |
| UI moves | 200 to 500 ms (lab starting point) |
| Hero reveals | 600 to 900 ms (lab starting point) |
| Letters | 1 frame apart |
| Words | 60 to 120 ms apart |
| List items | 40 to 80 ms apart |

Start the next element when the previous one is 30 to 50% done. Fully sequential looks robotic; all at once looks cheap.

For video, say it in frames. At 24 fps one frame is about 42 ms: a 400 ms move is 10 frames, a 750 ms reveal is 18.

## Beat grid

Frames per beat = fps x 60 / BPM. At 120 BPM and 24 fps that is 12 frames. At 128 BPM and 30 fps it is
14.06, so compute every beat from time and round each one (`beatFrame(n, bpm, fps)`). Adding a rounded
14 again and again drifts off the music: after 32 beats you are 2 frames off.

Cut on the beat and change the layout on the bar, every 4 beats. Changing everything on every beat wears the viewer out.

## Holds

On-screen text stays at least 0.3 s per word plus 0.5 s, so a two-word title needs 1.1 s. During a
hold, a slow 2% push keeps the frame alive while the words stay readable. Nothing should be frozen
except the final hold.

## Camera

- Field of view 35 to 50 degrees is a good starting point for three.js; product shots used 30, a miniature studio 18.
- Parallax speeds: 1.0 foreground, 0.5 middle, 0.2 background.
- A camera that never parks: slow orbit or creep through holds.

## Contrast and flashes (WCAG)

Keep text at 4.5:1 contrast on every frame, including over moving backgrounds. Never flash more than 3 times per second.

## Animation principles, written as numbers

Frank Thomas and Ollie Johnston, *The Illusion of Life* (1981). Five do most of the work in a short
loop, plus two that ride along with every move. Values are from the mascot experiment.

| Principle | What it does | Write it in the prompt as |
|---|---|---|
| Anticipation | Winds up before the move | 11-frame crouch (1.2x0.75) |
| Squash and stretch | Shows weight and speed | stretch 0.85x1.28 at takeoff, squash 1.25x0.7 on landing |
| Overlapping action | Limbs start later than the body | arms lag 4 frames, legs 6 |
| Follow-through | Parts keep moving after the body stops | arms settle at 2.2 Hz, damping 0.22 |
| Arcs | Makes motion feel natural | a flip along a dotted arc, 3.5 high |
| Slow in and slow out | Speeds up and settles softly | spring back at damping 0.55 |
| Timing | Frame count sets weight | 25 frames of air per hop, 18 frames of crouch before the flip |

The rest of the twelve still apply. Staging is the one-hero rule. Exaggeration matters more at phone
size: push key poses 10 to 30% further than feels right, because the feed shrinks everything.

Pin each principle to a frame and show a label or keyframe marker on that frame while iterating: a
move that runs late shows up as a label that lights before its move.
