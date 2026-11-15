/* ---
file: scaffold-living-document.mjs
purpose: Assemble a blank or reference living-document project from the bundled portable app.
runtime: Node.js 20+
--- */

import { cp, mkdir, readFile, writeFile, access } from 'node:fs/promises';
import { constants as fsConstants } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const skillRoot = path.resolve(scriptDir, '..');

function parseArgs(argv) {
  const args = { template: 'blank' };
  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (!token.startsWith('--')) continue;
    const key = token.slice(2);
    const value = argv[index + 1];
    if (!value || value.startsWith('--')) throw new Error(`Missing value for --${key}`);
    args[key] = value;
    index += 1;
  }
  return args;
}

function kebab(value) {
  return value
    .normalize('NFKD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

async function exists(target) {
  try {
    await access(target, fsConstants.F_OK);
    return true;
  } catch {
    return false;
  }
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const template = args.template;
  const target = args.target ? path.resolve(args.target) : null;

  if (!target) throw new Error('Required: --target <directory>');
  if (!['blank', 'reference'].includes(template)) {
    throw new Error('--template must be blank or reference');
  }
  if (await exists(target)) {
    const entries = await import('node:fs/promises').then(({ readdir }) => readdir(target));
    if (entries.length > 0) throw new Error(`Target is not empty: ${target}`);
  }

  const appSource = template === 'reference'
    ? path.join(skillRoot, 'examples', 'reference-living-document')
    : path.join(skillRoot, 'templates', 'app');
  const contentSource = path.join(skillRoot, 'templates', 'blank-content');

  await mkdir(target, { recursive: true });
  await cp(appSource, target, { recursive: true });
  if (template === 'blank') {
    await cp(contentSource, target, { recursive: true, force: true });
  }

  const manifestPath = path.join(target, 'public', 'content', 'index.json');
  const manifest = JSON.parse(await readFile(manifestPath, 'utf8'));
  const title = args.title?.trim();
  const documentId = args['document-id']?.trim();

  if (title) {
    manifest.meta.title = title;
    manifest.meta.subtitle = template === 'blank'
      ? `An evolving, auditable living document for ${title}.`
      : manifest.meta.subtitle;
  }
  if (documentId) {
    const normalized = kebab(documentId);
    if (!normalized) throw new Error('--document-id did not contain a valid identifier');
    manifest.meta.documentId = normalized;
  } else if (title && template === 'blank') {
    manifest.meta.documentId = kebab(title);
  }

  await writeFile(manifestPath, `${JSON.stringify(manifest, null, 2)}\n`, 'utf8');

  const result = {
    target,
    template,
    documentId: manifest.meta.documentId,
    title: manifest.meta.title,
    next: [
      `cd ${target}`,
      'npm run validate',
      'npm run dev'
    ]
  };
  process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
}

main().catch((error) => {
  console.error(`Scaffold failed: ${error.message}`);
  process.exitCode = 1;
});
