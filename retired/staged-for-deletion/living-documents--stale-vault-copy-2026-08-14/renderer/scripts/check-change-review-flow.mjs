import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

const app = await readFile(new URL('../public/app.js', import.meta.url), 'utf8');
const server = await readFile(new URL('../serve.mjs', import.meta.url), 'utf8');

assert.match(app, /pageHeader\('Review and send changes'/, 'review page needs one explicit send-oriented title');
assert.match(app, /renderChangesPanel\(\{ standalone: true \}\)/, 'standalone review must suppress the duplicate Changes title');
assert.match(app, /data-action="submit-change"/, 'review panel needs a direct send action');
assert.match(app, /fetch\('\/api\/change-requests'/, 'send action must create a loopback receipt');
assert.match(app, /download and copy are optional backups/, 'review page must explain that export is optional');
assert.match(server, /living-documents-change-request\/v1/, 'server must persist a versioned change receipt');
assert.match(server, /request\.url \|\| '\/'\) === '\/api\/change-requests'/, 'server must expose the receipt endpoint');

console.log('change review flow checks passed');
