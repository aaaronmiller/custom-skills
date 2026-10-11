// render.mjs: freeze an HTML animation at every frame and save one PNG per frame.
//
//   node render.mjs anim.html [seconds=6] [fps=24] [options]
//
//   --size WxH     viewport, the canvas of the piece (default 1080x1080)
//   --scale N      device pixel ratio; 2 renders sharper text, scale down later (default 1)
//   --from A       first frame to render (default 0)
//   --to B         last frame to render (default N-1; a loop never renders frame N)
//   --frames a,b   render only these frames, for stills during the lab loop
//   --blur S       S subframes per frame over half a frame (180-degree shutter),
//                  blended in linear light; 4 to 8 for fast moves (default off)
//   --out DIR      output folder (default out/frames)
//   --file         open the page over file:// instead of a local HTTP server
//
// Frame i is the page frozen at t = i / fps, so every PNG is exact however slow the machine.
// The page is opened with ?t=0, so a page that follows the render contract never starts its
// own clock; window.renderAt(t) and paused document animations do the rest.
// Based on render.mjs from "Opus 5.5 Motion Lab" by @flxrnc (X, 2026-09-30); see ../README.md.

import { createRequire } from 'node:module';
import { createServer } from 'node:http';
import { mkdirSync, readFileSync, rmSync, existsSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { resolve, dirname, basename, extname, join, sep } from 'node:path';
import { pathToFileURL } from 'node:url';

const args = process.argv.slice(2);
const flags = {};
const pos = [];
for (let i = 0; i < args.length; i++) {
  const a = args[i];
  if (a === '--file') flags.file = true;
  else if (a.startsWith('--')) flags[a.slice(2)] = args[++i];
  else pos.push(a);
}
const [file = 'anim.html', secs = '6', fpsArg = '24'] = pos;
const FPS = Number(fpsArg);
const N = Math.round(Number(secs) * FPS);
const [W, H] = (flags.size || '1080x1080').split('x').map(Number);
const SCALE = Number(flags.scale || 1);
const SUB = Math.max(1, Number(flags.blur || 1));
const OUT = flags.out || 'out/frames';
let frames;
if (flags.frames) frames = flags.frames.split(',').map(Number);
else {
  const from = Number(flags.from ?? 0), to = Number(flags.to ?? N - 1);
  frames = Array.from({ length: to - from + 1 }, (_, k) => from + k);
}
if (!existsSync(file)) fail(`no such file: ${file}`);
if (!(FPS > 0) || !(N > 0) || !(W > 0) || !(H > 0)) fail('seconds, fps and --size must be positive numbers');

// Resolve playwright from the lab folder first, so this script works copied or run in place.
let chromium;
try {
  chromium = createRequire(join(process.cwd(), 'noop.js'))('playwright').chromium;
} catch {
  try { chromium = (await import('playwright')).chromium; } catch {
    fail('playwright not found. In the lab folder run: npm i -D playwright && npx playwright install chromium');
  }
}

// A local static server for the HTML file's folder. file:// blocks ES module imports and
// texture or font loads from disk, which breaks most three.js pieces.
const root = dirname(resolve(file));
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript',
  '.css': 'text/css', '.json': 'application/json', '.png': 'image/png', '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg', '.svg': 'image/svg+xml', '.woff2': 'font/woff2', '.woff': 'font/woff',
  '.ttf': 'font/ttf', '.otf': 'font/otf', '.wav': 'audio/wav', '.mp3': 'audio/mpeg', '.glb': 'model/gltf-binary' };
let server, url;
if (flags.file) url = pathToFileURL(resolve(file)).href + '?t=0';
else {
  server = createServer((req, res) => {
    const p = resolve(root, '.' + decodeURIComponent(new URL(req.url, 'http://x').pathname));
    if (p !== root && !p.startsWith(root + sep)) { res.writeHead(403).end(); return; }
    try {
      res.writeHead(200, { 'content-type': TYPES[extname(p).toLowerCase()] || 'application/octet-stream' });
      res.end(readFileSync(p));
    } catch { res.writeHead(404).end(); }
  });
  await new Promise((r) => server.listen(0, '127.0.0.1', r));
  url = `http://127.0.0.1:${server.address().port}/${encodeURIComponent(basename(file))}?t=0`;
}

const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: SCALE });
const errors = [];
page.on('pageerror', (e) => errors.push(e.message));
await page.goto(url, { waitUntil: 'networkidle' });
await page.evaluate(async () => { await document.fonts.ready; });
// A page with async setup (fonts, textures, bakes) sets window.__ready = false, then true.
await page.waitForFunction(() => window.__ready !== false, null, { timeout: 120000 });
if (errors.length) fail('page error before the first frame: ' + errors[0]);

async function freeze(t) {
  await page.evaluate(async (t) => {
    if (typeof window.renderAt === 'function') await window.renderAt(t);
    document.getAnimations().forEach((a) => { a.pause(); a.currentTime = t * 1000; });
    await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
  }, t);
}

mkdirSync(OUT, { recursive: true });
const pad = (n, w = 4) => String(n).padStart(w, '0');
const subDir = join(OUT, '..', '.subframes');
for (const i of frames) {
  if (SUB === 1) {
    await freeze(i / FPS);
    await page.screenshot({ path: join(OUT, `${pad(i)}.png`) });
    continue;
  }
  // Motion blur: S subframes spread over the first half of the frame, averaged in linear light.
  rmSync(subDir, { recursive: true, force: true });
  mkdirSync(subDir, { recursive: true });
  for (let s = 0; s < SUB; s++) {
    await freeze((i + 0.5 * s / SUB) / FPS);
    await page.screenshot({ path: join(subDir, `${pad(s, 3)}.png`) });
  }
  const vf = 'zscale=tin=iec61966-2-1:t=linear,format=gbrpf32le,' +
    `tmix=frames=${SUB},select='eq(n\\,${SUB - 1})',` +
    'zscale=tin=linear:t=iec61966-2-1,format=rgb24';
  const ff = spawnSync('ffmpeg', ['-v', 'error', '-y', '-framerate', String(SUB), '-i', join(subDir, '%03d.png'),
    '-vf', vf, '-frames:v', '1', join(OUT, `${pad(i)}.png`)], { encoding: 'utf8' });
  if (ff.status !== 0) fail(`ffmpeg blend failed on frame ${i}: ${ff.stderr || ff.error}`);
}
rmSync(subDir, { recursive: true, force: true });
await browser.close();
if (server) server.close();
if (errors.length) console.error(`warning: ${errors.length} page error(s) while rendering, first: ${errors[0]}`);
console.log(`rendered ${frames.length} frame(s) of ${N} (${frames[0]}..${frames[frames.length - 1]}), ${W}x${H} at ${FPS} fps` +
  `${SCALE !== 1 ? `, scale ${SCALE}` : ''}${SUB > 1 ? `, ${SUB} subframes` : ''} -> ${OUT}`);

function fail(msg) {
  console.error('render.mjs: ' + msg);
  process.exit(1);
}

// Then turn the frames into a video (see export.sh):
// ffmpeg -framerate 24 -i out/frames/%04d.png -c:v libx264 -pix_fmt yuv420p -crf 18 -movflags +faststart out/anim.mp4
