// audio.mjs: render a Web Audio score to a WAV, then check that every hit peaks on its frame.
//
//   node audio.mjs render score.html out/score.wav [--rate 48000]
//   node audio.mjs check  out/final.mp4 --fps 24 --frames 36,84 [--lead 1] [--window 3]
//
// render: the page defines  window.renderScore = async (sampleRate) => AudioBuffer,
//   built with an OfflineAudioContext. For a seamless loop, schedule two loops and return
//   only the second, so tails from the end of the loop play under its start.
// check: decodes any file ffmpeg can read (WAV, or the muxed MP4, which is what viewers hear),
//   and for each visual event frame F reports where the loudest peak in the window
//   [F, F + window] frames lands, relative to the target (F + lead) / fps. The sound should
//   arrive 1 frame after its picture: light beats sound. Measure; don't trust a listen.
// Pattern from "Opus 5.5 Motion Lab" by @flxrnc (X, 2026-09-30); see ../README.md.

import { createRequire } from 'node:module';
import { writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { resolve, dirname, join } from 'node:path';
import { pathToFileURL } from 'node:url';

const [cmd, input, output] = process.argv.slice(2);
const flags = {};
const argv = process.argv.slice(2);
for (let i = 0; i < argv.length; i++) if (argv[i].startsWith('--')) flags[argv[i].slice(2)] = argv[i + 1];

function fail(msg) { console.error('audio.mjs: ' + msg); process.exit(1); }
if (!input || !existsSync(input)) fail(`usage: node audio.mjs render score.html out.wav | check file --fps N --frames a,b`);

if (cmd === 'render') {
  if (!output) fail('render needs an output .wav path');
  let chromium;
  try { chromium = createRequire(join(process.cwd(), 'noop.js'))('playwright').chromium; } catch {
    try { chromium = (await import('playwright')).chromium; } catch {
      fail('playwright not found. In the lab folder run: npm i -D playwright && npx playwright install chromium');
    }
  }
  const rate = Number(flags.rate || 48000);
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto(pathToFileURL(resolve(input)).href, { waitUntil: 'load' });
  const data = await page.evaluate(async (rate) => {
    if (typeof window.renderScore !== 'function') throw new Error('page has no window.renderScore(sampleRate)');
    const buf = await window.renderScore(rate);
    const chans = [];
    for (let c = 0; c < buf.numberOfChannels; c++) {
      const bytes = new Uint8Array(buf.getChannelData(c).buffer);
      let s = '';
      for (let i = 0; i < bytes.length; i += 0x8000) s += String.fromCharCode.apply(null, bytes.subarray(i, i + 0x8000));
      chans.push(btoa(s));
    }
    return { rate: buf.sampleRate, chans };
  }, rate);
  await browser.close();
  const ch = data.chans.map((b64) => { const b = Buffer.from(b64, 'base64'); return new Float32Array(b.buffer, b.byteOffset, b.length / 4); });
  const n = ch[0].length, nc = ch.length;
  // 32-bit float WAV (format 3), interleaved
  const body = Buffer.alloc(n * nc * 4);
  for (let i = 0; i < n; i++) for (let c = 0; c < nc; c++) body.writeFloatLE(ch[c][i], (i * nc + c) * 4);
  const h = Buffer.alloc(44);
  h.write('RIFF', 0); h.writeUInt32LE(36 + body.length, 4); h.write('WAVE', 8);
  h.write('fmt ', 12); h.writeUInt32LE(16, 16); h.writeUInt16LE(3, 20); h.writeUInt16LE(nc, 22);
  h.writeUInt32LE(data.rate, 24); h.writeUInt32LE(data.rate * nc * 4, 28); h.writeUInt16LE(nc * 4, 32); h.writeUInt16LE(32, 34);
  h.write('data', 36); h.writeUInt32LE(body.length, 40);
  mkdirSync(dirname(resolve(output)), { recursive: true });
  writeFileSync(output, Buffer.concat([h, body]));
  let peak = 0, dc = 0;
  for (let c = 0; c < nc; c++) for (let i = 0; i < n; i++) { peak = Math.max(peak, Math.abs(ch[c][i])); dc += ch[c][i]; }
  console.log(`rendered ${(n / data.rate).toFixed(3)} s, ${nc} ch, ${data.rate} Hz, sample peak ${(20 * Math.log10(peak)).toFixed(1)} dBFS, ` +
    `DC ${(dc / (n * nc)).toExponential(1)} -> ${output}`);
} else if (cmd === 'check') {
  const fps = Number(flags.fps), lead = Number(flags.lead ?? 1), win = Number(flags.window ?? 3);
  if (!(fps > 0) || !flags.frames) fail('check needs --fps and --frames');
  const rate = 48000;
  const ff = spawnSync('ffmpeg', ['-v', 'error', '-i', input, '-vn', '-af', 'pan=mono|c0=0.5*c0+0.5*c1', '-ar', String(rate), '-f', 'f32le', '-'],
    { maxBuffer: 1 << 30 });
  if (ff.status !== 0) fail('ffmpeg decode failed: ' + ff.stderr);
  const s = new Float32Array(ff.stdout.buffer, ff.stdout.byteOffset, ff.stdout.length / 4);
  let worst = 0;
  for (const F of flags.frames.split(',').map(Number)) {
    const a = Math.floor(F / fps * rate), b = Math.min(s.length, Math.ceil((F + win) / fps * rate));
    let pi = a, pv = 0;
    for (let i = a; i < b; i++) if (Math.abs(s[i]) > pv) { pv = Math.abs(s[i]); pi = i; }
    const off = (pi / rate - (F + lead) / fps) * 1000;
    worst = Math.max(worst, Math.abs(off));
    console.log(`frame ${String(F).padStart(4)}: peak ${off >= 0 ? '+' : ''}${off.toFixed(1)} ms from frame ${F + lead}, ` +
      `${(20 * Math.log10(pv || 1e-9)).toFixed(1)} dBFS`);
  }
  const tol = 1000 / fps / 2;
  console.log(worst <= tol ? `OK: every hit within ${tol.toFixed(1)} ms (half a frame) of its target`
    : `LATE OR EARLY: worst ${worst.toFixed(1)} ms; move the hit so its first crest lands on frame + ${lead}`);
  if (worst > tol) process.exitCode = 2;
} else fail('unknown command ' + cmd);
