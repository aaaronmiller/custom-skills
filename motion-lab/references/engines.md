# Pick the engine

The model can write for every engine below. Name the one you want in OUTPUT, with its numbers, or
it will choose for you.

| Engine | Use it for | Notes |
|---|---|---|
| Plain HTML and CSS | One idea under 10 seconds, 2D: type, shapes, UI | Zero installs. `render.mjs` turns it into frames. |
| Three.js | Anything 3D: scenes, lights, materials, shaders on WebGL | Pin the version. Drive time from the frame number, never the clock. Give the camera numbers. |
| Remotion | A series, a template, a data-driven or long video | Video as React components, frame-exact. Free for individuals and companies of up to 3 employees; bigger companies need a company license. |
| HyperFrames (HeyGen) | You think in web pages and GSAP timelines | Open source, Apache 2.0. Agents write HTML, CSS and GSAP; its CLI renders the MP4. |
| GSAP | Web timelines, also inside HyperFrames | Now free, including SplitText, MorphSVG, DrawSVG and ScrollTrigger. The license only bars building a competing no-code animation builder. |
| Motion (formerly Framer Motion) | Motion inside a live React product | MIT. Animates interfaces; has no video renderer. |

Rule of thumb: one idea under 10 seconds, plain HTML. A series, a template or a data-driven video,
Remotion. Web pages and GSAP, HyperFrames. Anything 3D, Three.js. Motion that lives inside a product
instead of a video, Motion or GSAP.

## Skills already on this machine

When the engine is HyperFrames or Remotion, load that engine's skill for mechanics and keep this
skill for direction, numbers and QA:

- `hyperframes` (front door), `hyperframes-core`, `hyperframes-animation`, `hyperframes-keyframes`, `hyperframes-cli`, `hyperframes-audio`, `motion-graphics`
- `remotion-best-practices`, `remotion-to-hyperframes`
- `gsap-core`, `gsap-timeline`, `gsap-plugins`, `gsap-react`, `gsap-performance`, `gsap-utils`, `gsap-scrolltrigger`, `gsap-frameworks`

## Setup

```bash
# Remotion: video as React components
npx create-video@latest          # pick a template, name it my-video
cd my-video && npm i
npx remotion skills add          # Remotion's Agent Skills for Claude Code
npm run dev                      # Remotion Studio in the browser
npx remotion render MyComp out/video.mp4   # MyComp = your composition id

# HyperFrames: HTML + GSAP in, MP4 out (needs Node 22+ and FFmpeg)
npx hyperframes init my-video
cd my-video
npx hyperframes preview
npx hyperframes render
```

## Three.js specifics

- Load through an importmap pinned to an exact version, e.g. `three@0.160.0` from jsdelivr.
- Version traps are real. In r160, `TextGeometry` reads `height` for the extrusion depth; a `depth` parameter is overwritten with 50, so letters meant to be 0.12 deep come out 50 deep. Pin the version and name the right parameter in the prompt.
- Build reflections from a studio made in code (PMREM of a scene with softboxes and strips) instead of downloading an HDRI, so nothing depends on the network.
- Seed all noise and grain by frame index.
- Headless Chromium on a machine without a GPU renders WebGL through SwiftShader (`render.mjs` sets the flags): correct but slow for heavy shaders. The lab's showcase pieces rendered on a real GPU at 60 fps.
