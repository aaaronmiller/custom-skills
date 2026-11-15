/* ---
file: validate.mjs
purpose: Validate a scaffolded living-document project without external dependencies.
runtime: Node.js 20+
--- */

import { access, readFile } from 'node:fs/promises';
import { constants } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.dirname(fileURLToPath(import.meta.url));
const failures = [];

async function exists(relative) {
  try {
    await access(path.join(root, relative), constants.F_OK);
    return true;
  } catch {
    return false;
  }
}

const required = [
  'RAISON_DETRE.md',
  'public/index.html',
  'public/app.js',
  'public/styles.css',
  'public/content/index.json',
  'public/data/annotations.json'
];

for (const file of required) if (!await exists(file)) failures.push(`Missing ${file}`);

if (!failures.length) {
  const manifest = JSON.parse(await readFile(path.join(root, 'public/content/index.json'), 'utf8'));
  const annotations = JSON.parse(await readFile(path.join(root, 'public/data/annotations.json'), 'utf8'));
  const ids = new Set();
  for (const section of manifest.sections || []) {
    if (ids.has(section.id)) failures.push(`Duplicate section id ${section.id}`);
    ids.add(section.id);
    if (!await exists(`public/${section.source}`)) failures.push(`Missing section source ${section.source}`);
  }
  for (const id of manifest.navigation?.sectionOrder || []) {
    if (!ids.has(id)) failures.push(`Unknown section in navigation ${id}`);
  }
  if (manifest.navigation?.sectionOrder?.length !== ids.size) failures.push('Navigation must contain every section exactly once');
  if (!Array.isArray(annotations.annotations)) failures.push('annotations.json must contain annotations array');
  if (manifest.meta?.compatibility?.formatVersion !== '2.1.0') failures.push('Expected formatVersion 2.1.0');
}

if (failures.length) {
  console.error('Validation failed');
  for (const failure of failures) console.error(`- ${failure}`);
  process.exitCode = 1;
} else {
  console.log('Living document validated');
}
