import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

const [app, server] = await Promise.all([
  readFile(new URL('../public/app.js', import.meta.url), 'utf8'),
  readFile(new URL('../serve.mjs', import.meta.url), 'utf8'),
]);

const moduleImports = [...app.matchAll(/from ['"]\.\/([^'"]+)['"]/g)].map((match) => match[1]);

for (const asset of moduleImports) {
  assert.match(server, new RegExp(`shellFiles[^\\n]+['"]${asset.replace('.', '\\.')}['"]`), `${asset} must be served as a shell asset`);
}

assert.match(server, /\['\.mjs', 'text\/javascript; charset=utf-8'\]/, '.mjs must use a JavaScript MIME type');

console.log('shell asset checks passed');
