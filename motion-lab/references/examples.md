# The lab's three pieces, with every prompt

Verbatim from "Opus 5.5 Motion Lab" by Florence (@flxrnc), X, 2026-09-30, as the prompts were sent
to Claude Opus 5.5. Use them as worked examples of the template: copy one, swap the words for your
subject, keep the numbers on the first run, then change one number at a time.

Each piece follows the same order: a directed prompt with the render contract, creative follow-ups
from stills and measurements, then one sound prompt written against frame numbers and its follow-ups.

## Opening shot: liquid chrome title (6 s loop, 60 fps, 1080x1080, three.js)

A chrome blob squashes, stretches and pinches into 7 drops; each drop pours into its letter; a glint
sweeps the word; the letters melt back into one wobbling blob that runs through frame 0. One
raymarched SDF in a shader plus real three.js TextGeometry, rendered on a GPU with subframe motion blur.
About 2 hours including 12 transition checks, plus about 45 minutes for sound.

### Prompt (416 words)

```text
Liquid Chrome: 6 s seamless loop, 60 fps, 1080x1080, one HTML file, three.js 0.160.0 via jsdelivr importmap only.

window.renderAt(t) sets everything from t in seconds; all motion and noise periodic in 6 s; with ?t= never start requestAnimationFrame; window.__ready after font and bake. Quarter-pixel camera jitter, 4 offsets from frac(t*60).

Raymarch blob, 7 droplets and text as one SDF in a full-screen shader. Smooth-min k 0.35, falling to 0.1 as droplets part; each droplet becomes its glyph through mix(dropSDF, textSDF, K). Text: TextGeometry "OPUS 5.5" per glyph, helvetiker_bold from the pinned examples/fonts, size 0.52, height 0.12 (r160 reads height, not depth), bevel 0.03, 10 bevel and 24 curve segments, tracking -0.04 em, period optically centered. Bake the same outlines into a 2048x512 signed distance texture on the GPU, extruded as a rounded box to match the mesh. From 3.3 to 4.7 s cross-fade to the real mesh (creased normals, 35 degrees), same GLSL, reflections traced into the SDF.

Chrome: F0 0.92, Schlick fresnel, roughness 0.04, 3 bounces.

Studio: white floor at y -0.8, soft overhead shadow, contact darkening, 6% reflection, black beyond z 4 (camera side) so letter faces reflect dark. Environment in azimuth and elevation, camera at 0: black camera-side panel 86x57 degrees, softboxes overhead (2.4) and upper left (3.0), black flags at 75 degrees left and right, a D97757 rim strip behind at 149 degrees, 24 up, intensity 1.4, a 2 degree glint strip, intensity 6, tilted 40 degrees, sweeping left to right 3.3 to 4.1 s.

Timeline:
0 to 1.2 s: blob radius 0.62 breathes 3% every 1.5 s, simplex noise 0.05.
1.2 to 1.4 s: squash 10%.
1.4 to 2.1 s: stretch 2.4x wide and pinch into 7 droplets sized by glyph area; each arcs 0.2 up to its glyph, overshoots 7%, stretches along its velocity.
2.2 to 2.9 s: droplets become letters left to right, 3 frames apart, 0.4 s each; bevels start 0.07 puffy and spring flat.
2.9 to 4.8 s: hold.
4.8 s: 6-frame swell, letters slump 0.12 and soften, drain to the center with ease-in, merge at 5.62 s with a 3-bounce wobble (14%, damping 0.25) running through frame 0.

Camera: 30 degree lens, dolly 5.6 to 7.2 by 2.6 s, push to 6.95 in the hold, back to 5.6 by 5.9 s; orbit 7 degrees each way centered on the hold; 6 degrees above.

Post: bloom threshold 1.0, strength 0.3; tone curve linear to 0.9, then a soft shoulder; vignette 7%; grain 1.5% seeded by frame index.
```

### Creative follow-ups (10)

Follow-ups 1 to 5 fixed what stills and measurements showed (white plastic instead of chrome, a glint
that erased the P, bevels that fused the letters, drops that left the frame). 6 to 9 came from checking
12 transitions frame by frame. 10 added a horizon line for the letter faces to reflect.

```text
1. It reads as white plastic, the letter faces only see the black floor so the glint never shows, and the mesh caps reflect bent shards. Make the studio dark (0.1 gray) with only a white cyc behind the subject, 140 degrees wide, from 10 below to 40 up. End the white floor at z 4 so camera-side rays reach the black panel. Flatten the mesh cap normals. Rim strip 12x40 degrees. Blob noise frequency 1.0.
2. The glint is a flare that erases the P: make it 0.6 degrees wide at intensity 3. The rim never reaches the letters: move the D97757 strip behind and up (165 degrees, 42 up, 70x16 degrees) and add a soft D97757 kicker on the right, azimuth 55 to 125, elevation -16 to 10, so every right-facing bevel catches it.
3. The 0.03 bevels fuse every letter pair. Space the glyphs by their measured outlines, 0.09 apart and 0.26 for the word space, and hold the camera at 7.8, pushing to 7.55. The mesh speckles on its bevels: shade it with the SDF gradient so it matches the raymarched text.
4. The outer droplets leave the frame by 8 px around frame 112. Start them at 40% of their glyph position, ease the flight with u^2.4 so the 7% overshoot lands at 1.97 s, and dolly from 1.2 to 2.5 s.
5. While the letters form they look like camouflage and the merged blob looks like crumpled foil. Surface ripple 0.008 at frequency 3.2.
6. A bump pops onto the blob at frame 85. Grow the droplets from radius -0.4 over 1.2 to 1.65 s and regrow the blob from -0.4, so their smooth-min pull fades in.
7. mix(sphere, letter) passes through flat coins. Let each droplet pour into its glyph instead: bake one SDF channel per glyph, reveal each letter inside a sphere growing from its droplet (smooth max 0.05, ease-out, 0.4 s), shrink the droplet into it, join them with smooth-min, and start the puff spring only once the letter is full (damping 0.55, 3 Hz). Melt in reverse, draining from 5.2 s.
8. The glint reaches the O late and leaves the last 5 early. Make it touch the O at 3.3 s and clear the last 5 at 4.1 s (calibrated sweep: azimuth -0.083 to 0.302).
9. The letters vanish before their drops exist and the merged ball inflates. Regrow the drops first (4.88 to 5.1 s, 1.15x glyph size), retract the letters after (5.0 to 5.35 s), and grow the central blob from 5.15 s.
10. The letter faces read as flat charcoal. Add a thin 0.5 horizon strip at -6 degrees inside the camera-side panel, and soften the floor's end over z 3.6 to 4.0.
```

### Sound prompt and follow-ups (5)

```text
# Sound prompt
Score this seamless 6 s loop (360 frames, 60 fps). Synthesize everything in code with the Web Audio API, no samples, no downloads. Each hit lands 1 frame after its visual event.
Bed: 120 BPM, four 3/4 bars of 90 frames starting on frames 67, 157, 247 and 337. Kick on 67, 247 and 337, offbeat shaker only where no hit plays, sub and pad on Bm, G, A, D.
Events: squash inhale peaking at 84, stretch glide 84 to 112, pinch bloops at 112, 113, 114 and 120, pour bloops rising through D major pentatonic at 136, 138, 141, 145, 147, 150 and 153, metallic ting at 200 (partials under 8 kHz), shimmer panned left to right until 245, liquid swell from 288 peaking at 303, drips at 309, merge blups at 319, 321, 322 and 325, slurp into a gloop at 337 wobbling at 2.4 Hz.
48 kHz stereo WAV, about -14 LUFS, peak -1 dBTP, no click at the seam. Mux into the MP4.
# Sound follow-ups (5), exactly as they were sent
1. Measured on the isolated hits: the kick and the gloop peak 8 to 11 ms late (a 4x waveshaper and sines that start at phase 0), and the levels over the bed are uneven (ting +10 dB, gloop +1 dB, drips -8 dB, dot drop +1 dB). Build every tonal hit as a buffer whose attack ends on a cosine crest at exactly (F + 1) x 800 samples, with no waveshaper. Put every hit, or pair of hits on the same frame, 3 to 6 dB above the bed (K-weighted, first 60 ms). The mix loses 4.5 dB through a 150 Hz high-pass: cut the sub 4 dB, the kicks 1.5 dB and the kick under the gloop 4 dB, and raise the pad 1.5 dB.
2. Timing is exact now. The hits sit 6.5 to 9 dB over the quieter bed: trim the hit bus 2.5 dB, then the two pinch pairs 1.4 dB, the U and S pinch 1 dB, the swell 1.2 dB and the last pour bloop 0.5 dB, and raise the drips 2.5 dB and the gloop 3 dB, so every hit reads 3 to 6 dB over the bed.
3. The limiter takes 3.4 dB off the gloop because all its partials and the kick crest on the same sample. Put the gloop's even harmonics in sine phase and lower the kick under it 2.7 dB, so the limiter stays under 1.5 dB and the gloop keeps 3 to 6 dB over the bed.
4. Sine-phase harmonics moved the gloop's biggest waveform peak 4 ms after its frame. Keep every gloop harmonic in cosine phase so the peak is on sample 270400, set the 2nd harmonic to 0.2 and the 3rd to 0.08, drop the 4th, and lower the gloop 0.5 dB.
5. The MP4's audio runs 16 ms of codec padding past the video, so the file starts on a hard step and a looping player stops the sound hard at 6.000 s, plays 16 ms of silence and restarts hard. Keep the seamless loop as the master WAV for the two-loop post, and for the single-loop article MP4 add a 2 ms raised-cosine fade to the first and last 96 samples only.
```

## Experiment 1: vague prompt vs directed prompt (earbuds, 6 s loop, 60 fps, 960x1080 per side)

Same model, same subject, same technical line; only the direction changed. The vague side is the
untouched first output of a separate context that saw only Prompt A. It came back as dark navy space,
a glowing halo ring, bloom, particles, spinning buds and a made-up tagline: most of Prompt B's banned
list. About 30 minutes for the left side, 90 for the right, plus 90 for sound.

### Prompt A, vague (27 words, 0 follow-ups by design)

```text
Create a cool 3D product animation for a pair of wireless earbuds. Make it look premium and modern. One self-contained HTML file using three.js, 960x1080, 6-second loop.
```

### Prompt B, directed (448 words)

```text
GOAL: a studio product film for wireless earbuds: case opens, buds rise to the viewer, everything clicks shut.
OUTPUT: one self-contained HTML file, three.js 0.160.0 from jsdelivr (importmap), 960x1080.
TIME: 6-second loop, 60 fps = 360 frames, 120 BPM (1 beat = 30 frames). Hits land on beats.

MODEL (1 unit = 1 cm, primitives with bevels): case 6.0 x 4.6 x 2.2, 1.0 edge radius, split at 3.3, back-hinged lid, 0.06 split bevel, 0.045 chrome wire around the seam. Inside: D97757 deck, two dark elliptical wells. Buds: ellipsoid head 1.6 x 1.5 x 1.5, lathed silicone tip, 1.6 oval stem with a chrome end cap, dark grille. Seated heads sit flush with the deck.

LOOK: satin ceramic white F4F1EC (roughness 0.38, clearcoat 0.35), chrome (metalness 1, roughness 0.05), D97757 on the deck only, ink 1C1B1A, tips E4E0DA. Backdrop F0EDE8 center to DEDAD3 corners, dithered. Key FFF4E8 3.0 upper front left, soft shadows; fill E8EEF5 0.6 low right; rim FFFFFF 4.0 upper back right. Reflections: PMREM studio built in code (warm gray dome, overhead and key softboxes, rim strip). Contact shadows, opacity 0.55. Neutral tone mapping, 8% vignette, 2% grain seeded per frame.

SHOTS:
0.0 to 0.5 s: a 2.4-wide studio strip (from 5.5 s) sweeps left to right, glinting across the closed lid and seam.
0.72 to 0.95 s: anticipation: lid presses 1.5 degrees shut, case squashes 2%, hold 3 frames.
1.0 s: lid springs to 100 degrees (damping 0.6, about 10% overshoot, settled by 1.4 s).
1.5 s: buds rise 4.0 out of the wells, right first, left 4 frames later (damping 0.7). From rise frame 8 they tilt 14 degrees outward and turn 35 degrees to camera on a looser spring (damping 0.5): stems swing through and settle.
2.0 s: camera push-in.
2.4 to 4.0 s: hold, buds float 0.05 on a 1 s sine. 3.0 s: second glint crosses the buds.
4.0 s: buds straighten (0.2 s) and descend (easeInOutCubic, 0.45 s), seating with a 0.05 magnetic dip.
4.75 s: lid falls (easeInCubic), shuts exactly at 5.0 s, bounces 3 degrees, settles by 5.3 s; case recoils 1.5%.
5.5 s: next glint starts.

CAMERA: fov 30, never parked. Azimuth 34 to 10 degrees from 5.6 s to 4.0 s (easeInOutSine), back by 5.6 s (easeInOutCubic). Distance creeps 21 to 20.2, pushes to 16 at 2.0 s (easeOutExpo, 0.8 s), returns 4.0 to 5.6 s (easeInOutCubic). Buds up: elevation 12 to 19 degrees, target height 2.3 to 4.2.

BANNED: purple or blue gradients, glow orbs, bloom, neon, lens flares, particles, generic spinning turntables, dark backgrounds, text.

QA: renderAt(t) draws exactly time t, seeded noise only. Stills around every hit; frame 359 flows into frame 0.
```

### Creative follow-ups (15, in 4 review rounds)

```text
# Round 1, after the first build (stills at 0, 1.25, 2.9 and 4.9 s)
The white case melts into the backdrop and the chrome reads gray. Drop the studio dome to about a third and push the softboxes, so the unlit sides fall off and the chrome shows dark and bright bands.
The open lid reads as a flat slab. Hollow it: 0.16 rim, 0.62 deep cavity, 0.22 fillet at the ceiling.
The round dark grille reads as an eye. Make it a slim slot.
Two dark marks poke through the bottom of the case: the well floors at 0.3 sit outside the bottom arc, which insets the wall by 0.29 at that height. Raise the floors to 0.5.
The deck reads salmon. Roughness 0.7.
# Round 2, after measuring pixels
Front and top are the same value and the right side vanishes into the backdrop. Key to (-7, 12, 8), rim to (2, 8, -12), still upper front left and upper back right. Overhead softbox 2.2, exposure 0.8.
The glint is a flood light: strip on vs off changes 178,864 pixels because the 60-tall strip lights the whole face. Keep the strip in reflections only (a second PMREM for the specular lookup, the static studio for diffuse) and go back to the 2.4 width from the brief.
Exposure 0.9 and key softbox 4.5 so the ceramic reads white. Deck specular 0.3 so the grazing reflection stops washing out D97757.
Give the wells a 0.07 machined round-over.
The buds read as mouse heads. Move the stem to the outer side, replace the ball tip with a short nozzle and a flattened silicone cap, and move the grille off the head (it read as an eye twice) onto the stem.
Crane faster: reach the high target by 2.3 s, so the heads keep headroom during the push.
# Round 3, after isolating each glint
The first glint is too shy for a hook. Clearcoat roughness 0.08, strip peak 24, and shift the sweep to -80 to 0 degrees so the band is mid-face on frame 0.
The second glint flashes the whole lid cavity (207,791 pixels at 3.3 s) because the strip crosses the mirror direction of the flat faces. Raise it to 8 to 61 degrees elevation, 4.8 wide: only the curved heads and stems catch it.
The hold parks the camera: add a 0.4 dolly creep from 2.8 to 4.0 s. Float the left bud 4 frames behind the right, like its rise.
# Round 4, frame-perfect pass
The anticipation holds 4 frames (57 to 60), not 3: the spring starts at rest exactly on 1.0 s, so the beat frame is still the pressed pose. Release half a frame early (59.5/60 s): frames 57 to 59 hold, including their motion-blur subframes, and frame 60 is the first open frame.
```

### Sound prompt and follow-ups (12, in 4 rounds, all from measurements)

```text
# Sound prompt
Score the A/B video. Synthesize everything in code with the Web Audio API, no samples, no downloads. 120 BPM, 6 s loop, 360 frames at 60 fps. Each hit lands 1 frame after its visual event, and so does the bed.
Bed: kick every 60 frames, 16th shaker, bass and pad F, B flat at 120, G minor at 240, C at 300.
Right half only:
44 to 60 reverse swell.
60 lid snap: click, 880 Hz body, 120 Hz thump.
90, 94 magnetic pops, air lift to 119.
96 to 120 push-in swell.
180 to 216, 330 to 30 glint shimmer.
240 to 267 falling swish, 270 seat click.
285 to 300 whoosh into the shut: click, 200 Hz thock, 70 Hz thump; ticks 306, 312.
Hits 3 to 6 dB over the bed, nothing above 8 kHz, mono-safe. Render twice, keep the second pass. 48 kHz stereo WAV, about -14 LUFS, peak -1 dBTP. Mux into the MP4 and check every hit in its decoded audio.
# Sound follow-ups (12), exactly as they were sent
# Round 1, after measuring the first render (80.6% of the energy under 60 Hz, 3.5% in 150 Hz to 6 kHz, median 58 Hz; hits 0.5 to 1.6 dB over the bed; bodies peaking 2.5 to 5 ms after the frame)
1. The sub buries everything. Play B flat, G and C an octave higher (117, 98, 131 Hz), open the bass to 900 Hz, shorten the kick to 80 ms and give it a 190 Hz knock. Raise the pad 5 dB and every hit 6 dB, ticks 6 and 10 dB under the shut.
2. Start every body and thump in cosine phase with a 0.5 ms attack, so the first waveform peak sits on frame + 1.
3. Give the push-in swell a clear peak: 60 ms exponential rise into frame 121, then a 25 ms drop into the camera tail.
4. Duck the bed 4 dB from the shut through tick 2 (frames 301 to 313).
5. Remove the DC: subtract each channel's loop mean.
# Round 2, after measuring the second render (full mix -14.0 LUFS but only -22.9 LUFS in the 200 Hz to 6 kHz phone band; hit stem minus bed stem, K-weighted: snap -0.3, pops -3.1 and -5.2, seat -6.9, shut +2.6, ticks -0.8 and -4.3, push-in -9.3 dB; kick peak 5 ms and snap thump 2.4 ms after frame + 1)
6. The bass still carries the loudness. Drop its sine to a third, open the saw to 1200 Hz, bass 2 dB down, pad 4 dB up and brighter (1600 Hz).
7. Hits to 3 to 6 dB over the bed: push-in swell +8 dB, seat click +6 dB, pops +4 dB, ticks 4 and 8 dB under the shut.
8. Phase every tone so its first waveform peak lands exactly on frame + 1, the kick included (cosine start, 1 ms attack).
# Round 3, after measuring the third render (phone band -17.5 LUFS against -14.0 full; phone-band hit minus bed: snap 6.4, pops 5.6 and 3.5, seat 2.3, shut 8.4, ticks 3.0 and 1.8, push-in 3.0 dB; the kick's first peak is on frame + 1 but its wider second lobe is 10% louder, 2.5 ms later; limiter up to 4.4 dB)
9. Give the kick a 3 ms transient (its level falls to 65% within 3 ms of frame + 1) and the knock 3 dB more, so its largest peak is the first one.
10. Shut 2.5 dB down with the ticks kept where they are (tick 2 then 3 dB up), seat click +2 dB, push-in swell +2 dB.
11. The kick's second lobe is still 6% louder: the knock's negative half lands on it. Knock decay 4 ms, kick attack 0.5 ms. Tick bodies decay in 12 ms so earlier tails cannot flip their lobes.
# Round 4, after decoding the muxed article MP4 in Chrome (offset -0.002 ms, every hit 0.0 to 1.3 ms after frame + 1, but the AAC encode lifts the true peak from -1.3 to -0.4 dBTP)
12. Limit the WAV to -2.2 dBTP so the decoded MP4 stays under -1 dBTP; keep -14 LUFS.
```

## Experiment 2: five animation principles on a 3D mascot (8 s loop, 60 fps, 1080x1080)

Three studio lights click on, the voxel mascot hops pad to pad along a floor that is a motion-tool
timeline, then flips back to the first pad along a dotted arc. Each principle's label lights on the
frame it happens. A numeric audit read the live scene on all 480 frames against the prompt's numbers:
71 checks, 6 failed on the first run, all fixed. About 2 hours plus 70 minutes for sound.

### Prompt (399 words)

```text
Build a 3D animation-principles loop. One HTML file, three.js 0.160.0 via jsDelivr importmap, Geist Mono from Google Fonts. 1080x1080, 8 s at 60 fps (480 frames), frame 480 equals frame 0. window.renderAt(t) draws any frame from t alone; seeded random only.

Set: a miniature studio. A floating white 12x6 slab on an F4F2EE backdrop. Its top is a timeline: 3 tracks of 0.25 frame cells (EFEEEA), a ruler with frame numbers, 5 keyframe diamonds 2 units apart on the middle track (white fill, 0F0F0F outline). Around it on stands: a key softbox, a rim strip light, a top spot on a boom.
Hero: the pixel Claude mascot as 0.1 voxels: D97757 body 14x10x8, two 3x2 arms, four 2x3 legs, 0F0F0F 2x3 eyes; roughness 0.45, clearcoat 0.3.

Lights, 0 to 1 s: key 3200 K with soft shadows at 0.1 s, rim 7500 K at 0.4 s, top spot 5000 K at 0.7 s. Each clicks on with a 3-frame flicker, and the mascot's eyes glance at it.
Hops, 1 to 5 s: 4 hops to diamonds 2 to 5, landing on frames 105, 165, 225 and 285. Each hop: 11-frame crouch (1.2x0.75), stretch 0.85x1.28 at takeoff, 25 frames of air, squash 1.25x0.7 on landing, spring back at damping 0.55; arms lag 4 frames, legs 6. Each landing lights its diamond FF6A2B, ripples the cells 0.08 high and throws 12 voxel sparks. An FF6A2B playhead carrying a point light moves at constant speed and crosses each diamond on its landing frame.
Flip, 5 to 6.4 s: a dotted arc from diamond 5 back to diamond 1 draws in, then an 18-frame deep crouch and a 360° flip along the arc, 3.5 high, landing on frame 384 while the playhead rewinds under it.
Labels, top left, Geist Mono 28 px: a checklist 01 ANTICIPATION, 02 SQUASH & STRETCH (& in D97757), 03 OVERLAPPING ACTION, 04 FOLLOW-THROUGH, 05 ARCS, in 8E8A83. Each row turns 0F0F0F and fills its FF6A2B diamond on its exact frame: 69 (first crouch), 140 (stretch), 200 (limbs trail), 285 (arms settle), 303 (arc draws).
End: hold, blink at 7.2 s; on frame 468 the lights, diamonds and labels snap off.
Camera: FOV 18, 30° elevation, ±10° orbit over 8 s, 25% push-in tracking the hops, 4% punch-in on the flip landing.
Post: bloom on emissives, depth of field focused on the mascot, 2% grain, 10% vignette, dithered backdrop.
```

### Creative follow-ups (4)

```text
1. The render is washed out and cramped. Grade so the lit front face reads D97757 and lit diamonds read FF6A2B; drop the fill so lights-off sits near 50% and each click is obvious; lower the key to 28 degrees from the front right and put the cool rim at the back left so it edges the side we see. Pull the wide shot back to 44 units so the whole floating slab and all three stands are in frame, add a soft shadow under the slab, and make sparks 0.075 to 0.12 and ruler numbers bigger.
2. Frame check fixes. Keep every prop out of the label block: track the hops at 45% and hang the top spot at 5.8 on a boom from the back right corner, above the flip. Light each lit diamond with a soft glow from its face, move the playhead light to the front edge of the track and run its line under the diamonds. Start the dotted arc above the mascot's head, keep every tripod foot on the slab, and give the arms a bigger, slower settle (2.2 Hz, damping 0.22) so the follow-through reads.
3. Turn the rim strip's panel toward the camera so its click reads.
4. Make the top spot's click read too: narrow it to a 34 degree pool at 45 cd and give the lamp a glowing lens rim.
```

### Sound prompt (0 follow-ups: the first build matched the prompt's numbers)

```text
# Sound prompt
Score this 8 s loop, 480 frames at 60 fps. Synthesize everything in code with the Web Audio API, no samples, no downloads. 120 BPM, 4 bars, F major. Each hit lands 1 frame after its visual event.
Bed: pad voices A3 E4 (key light), C5 (top), G5 (rim), each following its light's flicker. Shaker 8ths from 45, kick and bass from 60, roots F D Bb F by bar; kick and shaker rest 330 to 420, bass holds C, then F at 384.
Clicks: lights 6, 24, 42, off 468.
Crouches 69, 129, 189, 249, 312: creak, inhale riser.
Takeoffs 80, 140, 200, 260, 330: upward swish.
Landings 105, 165, 225, 285, 384: rubber squash pitched by the squash scale, spark tings, 384 biggest.
Label pings A5 C6 D6 F6 A6: 69, 140, 200, 285, 303.
Dot ticks 303 to 318, flip whoosh 330 to 384, blink blip 432.
48 kHz stereo WAV, about -14 LUFS, peak -1 dBTP, seamless loop, mux into the MP4.
```

## What to take from them

- Every drop, light and camera move came from a number in the prompt or a follow-up.
- Follow-ups name frames, sizes, angles and measurements, never feelings.
- The guardrail lines (pixel proportions, "r160 reads height, not depth") prevent known failures before they happen.
- Sound is scored against the same frame numbers as the picture, and checked by measuring the decoded file.
