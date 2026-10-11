# The last mile: sound, loops, export for X

The part tutorials skip, and the part viewers notice first.

## Sound

The feed plays video muted until someone taps, so the picture has to work in silence first.

- **Sync:** put each visual hit 1 frame before its sound, never after. A sound that arrives before its picture feels wrong sooner than one that arrives a little late; light beats sound.
- **Loudness:** about -14 LUFS (a common web-video target) with peaks at -1 dBTP.
- **Synthesize in code** with the Web Audio API, no samples: every hit, bed and swell is a function of time, so it can be placed to the sample. Render offline (`OfflineAudioContext`) with `node audio.mjs render score.html out/score.wav`.
- **Write the score against frame numbers.** Template in `assets/sound-prompt.txt`; three real scores in `examples.md`.
- **Measure; do not listen.** The model cannot hear. Check sync by decoding the finished MP4 and lining each hit up with its frame: `node audio.mjs check out/final.mp4 --fps 60 --frames 67,84,112`.

Measured pitfalls from the lab's sound follow-ups:

| Problem | Fix |
|---|---|
| Hits peak 8 to 11 ms late | A waveshaper or sines that start at phase 0 delay the first crest. Build tonal hits as buffers that start on a cosine crest, so the first peak is the start time. |
| Hits uneven against the bed | Put every hit 3 to 6 dB over the bed (K-weighted, first 60 ms). |
| Most energy under 60 Hz | Phone speakers play nothing there. Move bass up an octave, open filters, and check the 200 Hz to 6 kHz phone band's loudness, not just the full mix. |
| The limiter squashes a hit | Partials and kick cresting on the same sample stack up. Lower what sits under it, or change harmonic phase, so the limiter stays under 1.5 dB. |
| AAC lifts the true peak | -1.3 became -0.4 dBTP after encoding. Limit the WAV to about -2.2 dBTP so the decoded MP4 stays under -1. |
| Codec padding at the seam | The MP4's audio ran 16 ms past the video. Keep the seamless WAV as the master; for a single-loop MP4 add a 2 ms raised-cosine fade to the first and last samples only. |
| Click at the loop seam | Render two loops and keep the second, so tails ring into the start. Remove DC (subtract each channel's mean). |
| Integrated loudness under target | The mix is too peaky to reach -14 under a -1 dBTP ceiling. Raise the bed or trim the loudest hits; `export.sh loudness` reports it. |

## Seamless loops

- Render frames 0 to N-1, never N. Frame N is frame 0 again, and showing it twice is the hiccup people see at the seam.
- Drive every loop from `phase = frame / N` with whole-number cycles. A square that turns exactly 90 degrees per loop, or a wave that completes exactly 2 cycles, lands back on its first frame.
- For organic drift, sample noise along a circle, so it comes back to where it started.
- Make frame 0 a finished composition. It is the first thing on screen while a GIF loads.
- Anything that rings across the seam (a wobble, a settle) must run through frame 0 continuously: compute it from the previous loop's event time, wrapped by the loop length.
- Check with `./export.sh loop` (three loops back to back), and compare both position and velocity into and out of frame 0.

## Export

```bash
# MP4 for an X post: H.264 High, yuv420p, starts playing at once
ffmpeg -framerate 24 -i out/frames/%04d.png -c:v libx264 -profile:v high -pix_fmt yuv420p -crf 18 -movflags +faststart out/anim.mp4

# GIF for an X Article: one palette for the whole clip, 1200 px wide
ffmpeg -framerate 24 -i out/frames/%04d.png -vf "scale=1200:-1:flags=lanczos,split[a][b];[a]palettegen=stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle" -loop 0 out/anim.gif

# Loop check: play it three times back to back and watch the seam
ffmpeg -stream_loop 2 -i out/anim.mp4 -c copy out/loop_check.mp4
```

`scripts/export.sh` wraps these (`mp4`, `gif`, `loop`, `mux`, `loudness`) and warns on X's GIF limits.

MP4 for posts, GIF for X Articles and inline loops. One palette for the whole GIF keeps colors from
flickering between frames.

### X limits (X media docs and Help Center)

| Spec | GIF | Video |
|---|---|---|
| Size limit | 15 MB | 140 s without Premium |
| Frame size | up to 1280 x 1080 | 1920 x 1080 for 16:9 |
| Frames and speed | at most 350 frames | up to 60 fps |
| Format | one palette, loop forever | H.264 High, yuv420p, AAC audio |
| Lab default | 1200 px wide, 24 fps | CRF 18, faststart |

At 24 fps the 350-frame cap means a GIF tops out at about 14.5 seconds. A 4 to 6 second loop is 96 to 144 frames.

X accepts video between 1:3 and 3:1. Common canvases: 1920 x 1080 (16:9), 1080 x 1080 (1:1),
1080 x 1350 (4:5), 1080 x 1920 (9:16). Pick the canvas before the first frame; changing it later
means re-directing every shot.

### GIF timing

GIF delays are stored in hundredths of a second, so a 24 fps frame (41.7 ms) cannot be stored exactly.
Rounding every frame to 40 ms makes the loop run 4% fast, off the beat grid. The fix is to mix delays:
five frames at 40 ms, then one at 50 ms. **ffmpeg already does this** when given `-framerate 24`
(verified 2026-10-10: a 96-frame export used delays of 4 and 5 centiseconds and totals exactly 4.00 s).
Check other GIF tools before trusting them.
