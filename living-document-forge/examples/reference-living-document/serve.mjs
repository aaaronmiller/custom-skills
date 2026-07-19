/* ---
file: serve.mjs
purpose: Serve the dependency-free living-document workbench with safe path resolution.
runtime: Node.js 20+
--- */

import http from 'node:http';
import { readFile, stat } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const projectRoot = path.dirname(fileURLToPath(import.meta.url));
const root = path.join(projectRoot, 'public');
const resourcesRoot = path.join(projectRoot, 'resources');
const port = Number.parseInt(process.env.PORT || '4173', 10);
const host = process.env.HOST || '127.0.0.1';
const mime = new Map([
  ['.html', 'text/html; charset=utf-8'],
  ['.js', 'text/javascript; charset=utf-8'],
  ['.css', 'text/css; charset=utf-8'],
  ['.json', 'application/json; charset=utf-8'],
  ['.md', 'text/markdown; charset=utf-8'],
  ['.svg', 'image/svg+xml'],
  ['.png', 'image/png'],
  ['.jpg', 'image/jpeg'],
  ['.jpeg', 'image/jpeg'],
  ['.gif', 'image/gif'],
  ['.webp', 'image/webp'],
  ['.mp4', 'video/mp4'],
  ['.webm', 'video/webm'],
  ['.mp3', 'audio/mpeg'],
  ['.m4a', 'audio/mp4'],
  ['.wav', 'audio/wav'],
  ['.csv', 'text/csv; charset=utf-8'],
  ['.txt', 'text/plain; charset=utf-8'],
  ['.ico', 'image/x-icon'],
  ['.webmanifest', 'application/manifest+json']
]);

function resolveRequest(urlPath) {
  const decoded = decodeURIComponent(urlPath.split('?')[0]);
  const normalized = path.posix.normalize(decoded).replace(/^\.\.(?:\/|$)/, '');
  if (normalized.startsWith('/resources/')) {
    const resourceRelative = normalized.slice('/resources/'.length);
    const target = path.resolve(resourcesRoot, resourceRelative);
    if (!target.startsWith(path.resolve(resourcesRoot))) return null;
    return target;
  }
  const relative = normalized === '/' ? '/index.html' : normalized;
  const target = path.resolve(root, `.${relative}`);
  if (!target.startsWith(path.resolve(root))) return null;
  return target;
}

const server = http.createServer(async (request, response) => {
  try {
    let target = resolveRequest(request.url || '/');
    if (!target) {
      response.writeHead(400).end('Bad request');
      return;
    }
    const info = await stat(target).catch(() => null);
    if (info?.isDirectory()) target = path.join(target, 'index.html');
    const body = await readFile(target);
    const extension = path.extname(target).toLowerCase();
    response.writeHead(200, {
      'Content-Type': mime.get(extension) || 'application/octet-stream',
      'Cache-Control': extension === '.html' ? 'no-store' : 'no-cache',
      'X-Content-Type-Options': 'nosniff',
      'Referrer-Policy': 'no-referrer'
    });
    response.end(body);
  } catch (error) {
    response.writeHead(error?.code === 'ENOENT' ? 404 : 500, { 'Content-Type': 'text/plain; charset=utf-8' });
    response.end(error?.code === 'ENOENT' ? 'Not found' : 'Server error');
  }
});

server.listen(port, host, () => {
  console.log(`Living Document Workbench: http://${host}:${port}`);
});
