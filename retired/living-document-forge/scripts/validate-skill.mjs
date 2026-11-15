/* ---
file: validate-skill.mjs
purpose: Validate skill structure, internal references, JSON, JavaScript syntax targets, and assembled example presence.
runtime: Node.js 20+
--- */

import { access, readFile, readdir, stat } from 'node:fs/promises';
import { constants as fsConstants } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const skillRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const errors = [];

async function exists(target) {
  try {
    await access(target, fsConstants.F_OK);
    return true;
  } catch {
    return false;
  }
}

async function walk(directory) {
  const output = [];
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    const full = path.join(directory, entry.name);
    if (entry.isDirectory()) output.push(...await walk(full));
    else output.push(full);
  }
  return output;
}

async function main() {
  const required = [
    'SKILL.md',
    'VERSION',
    'CHANGELOG.md',
    'references/content-model.md',
    'references/interface-design-system.md',
    'references/interaction-model.md',
    'references/adversarial-review.md',
    'scripts/scaffold-living-document.mjs',
    'scripts/validate-living-document.mjs',
    'bin/ld',
    'bin/ld-shim',
    'tests/test-ld.py',
    'references/ld-command.md',
    'references/system-prompt-clause.md',
    'schemas/document.schema.json',
    'schemas/annotations.schema.json',
    'schemas/content-plan.schema.json',
    'schemas/living-documents-index.schema.json',
    'templates/content-input/content-plan.template.json',
    'templates/content-input/section.template.md',
    'templates/registry/living-documents-index.template.json',
    'templates/app/public/index.html',
    'templates/app/public/app.js',
    'templates/app/public/styles.css',
    'examples/reference-living-document/public/content/index.json'
  ];
  for (const relative of required) {
    if (!await exists(path.join(skillRoot, relative))) errors.push(`Missing ${relative}`);
  }

  const files = await walk(skillRoot);
  for (const file of files.filter((item) => item.endsWith('.json'))) {
    try {
      JSON.parse(await readFile(file, 'utf8'));
    } catch (error) {
      errors.push(`Invalid JSON ${path.relative(skillRoot, file)}: ${error.message}`);
    }
  }

  const skillText = await readFile(path.join(skillRoot, 'SKILL.md'), 'utf8');
  const referenceMatches = [...skillText.matchAll(/`(references\/[a-z0-9./-]+\.md)`/g)].map((match) => match[1]);
  for (const reference of new Set(referenceMatches)) {
    if (!await exists(path.join(skillRoot, reference))) errors.push(`SKILL.md references missing ${reference}`);
  }

  const version = (await readFile(path.join(skillRoot, 'VERSION'), 'utf8')).trim();
  if (!/^\d+\.\d+\.\d+$/.test(version)) errors.push('VERSION must be semantic x.y.z');

  const size = (await stat(path.join(skillRoot, 'SKILL.md'))).size;
  if (size < 8000) errors.push('SKILL.md is unexpectedly small for the declared workflow');

  if (errors.length) {
    console.error('Skill validation failed');
    for (const error of errors) console.error(`- ${error}`);
    process.exitCode = 1;
    return;
  }
  console.log(`Skill ${version} structure validated`);
  console.log(`- ${files.length} files`);
  console.log(`- ${new Set(referenceMatches).size} referenced guides resolved`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
