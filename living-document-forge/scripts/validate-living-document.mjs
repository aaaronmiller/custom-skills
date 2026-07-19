/* ---
file: validate-living-document.mjs
purpose: Validate format-2 living-document structure, relationships, sources, and starter assets.
runtime: Node.js 20+
--- */

import { access, readFile, readdir } from 'node:fs/promises';
import { constants as fsConstants } from 'node:fs';
import path from 'node:path';

const projectRoot = path.resolve(process.argv[2] || process.cwd());
const errors = [];
const warnings = [];

async function exists(target) {
  try {
    await access(target, fsConstants.F_OK);
    return true;
  } catch {
    return false;
  }
}

function requireValue(condition, message) {
  if (!condition) errors.push(message);
}

function uniqueIds(items, label) {
  const seen = new Set();
  for (const item of items) {
    if (!item?.id) {
      errors.push(`${label} contains an item without id`);
      continue;
    }
    if (seen.has(item.id)) errors.push(`Duplicate ${label} id: ${item.id}`);
    seen.add(item.id);
  }
  return seen;
}

function checkDate(value, label) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value || '')) errors.push(`${label} must be YYYY-MM-DD`);
}

async function main() {
  const required = [
    'RAISON_DETRE.md',
    'package.json',
    'serve.mjs',
    'public/index.html',
    'public/app.js',
    'public/styles.css',
    'public/content/index.json',
    'public/data/annotations.json'
  ];

  for (const relative of required) {
    requireValue(await exists(path.join(projectRoot, relative)), `Missing required file: ${relative}`);
  }
  if (errors.length) throw new Error('Required file check failed');

  const manifestPath = path.join(projectRoot, 'public/content/index.json');
  const annotationsPath = path.join(projectRoot, 'public/data/annotations.json');
  const manifest = JSON.parse(await readFile(manifestPath, 'utf8'));
  const annotationsFile = JSON.parse(await readFile(annotationsPath, 'utf8'));

  requireValue(manifest.meta?.documentId, 'meta.documentId is required');
  requireValue(/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(manifest.meta?.documentId || ''), 'meta.documentId must be kebab-case');
  requireValue(manifest.meta?.compatibility?.formatVersion === '2.1.0', 'formatVersion must be 2.1.0');
  requireValue(Array.isArray(manifest.sections) && manifest.sections.length > 0, 'sections must contain at least one section');
  requireValue(Array.isArray(manifest.navigation?.sectionOrder), 'navigation.sectionOrder must be an array');
  requireValue(Array.isArray(manifest.proposals), 'proposals must be an array');
  requireValue(Array.isArray(manifest.releases), 'releases must be an array');
  requireValue(Array.isArray(manifest.history), 'history must be an array');
  requireValue(Array.isArray(manifest.worklogs), 'worklogs must be an array');
  requireValue(Array.isArray(manifest.modelReplies), 'modelReplies must be an array');
  requireValue(Array.isArray(manifest.resources), 'resources must be an array');
  requireValue(Array.isArray(annotationsFile.annotations), 'annotations must be an array');
  checkDate(manifest.meta?.updated, 'meta.updated');

  const sectionIds = uniqueIds(manifest.sections || [], 'section');
  uniqueIds(manifest.proposals || [], 'proposal');
  uniqueIds(manifest.history || [], 'history event');
  uniqueIds(manifest.worklogs || [], 'worklog');
  uniqueIds(manifest.modelReplies || [], 'model reply');
  uniqueIds(manifest.resources || [], 'resource');
  uniqueIds(annotationsFile.annotations || [], 'annotation');

  const order = manifest.navigation?.sectionOrder || [];
  requireValue(order.length === sectionIds.size, 'navigation.sectionOrder must contain every section exactly once');
  for (const id of order) requireValue(sectionIds.has(id), `sectionOrder references unknown section: ${id}`);

  for (const section of manifest.sections || []) {
    requireValue(order.includes(section.id), `Section ${section.id} is missing from sectionOrder`);
    requireValue(/^content\/sections\/.+\.md$/.test(section.source || ''), `Section ${section.id} has invalid source path`);
    const sourcePath = path.join(projectRoot, 'public', section.source || '');
    requireValue(await exists(sourcePath), `Missing source for section ${section.id}: ${section.source}`);
    if (await exists(sourcePath)) {
      const markdown = await readFile(sourcePath, 'utf8');
      requireValue(markdown.includes(`id: ${section.id}`), `Markdown frontmatter id mismatch for ${section.id}`);
      requireValue(markdown.trim().length > 80, `Section ${section.id} appears empty or unfinished`);
    }
    for (const relation of [...(section.dependencies || []), ...(section.backlinks || [])]) {
      requireValue(sectionIds.has(relation), `Section ${section.id} references unknown section ${relation}`);
      requireValue(relation !== section.id, `Section ${section.id} may not reference itself`);
    }
  }

  const validTargets = new Set([
    'document',
    'dashboard',
    'proposal-queue',
    'visual-system',
    ...sectionIds,
    ...(manifest.proposals || []).map((proposal) => proposal.id)
  ]);

  for (const annotation of annotationsFile.annotations || []) {
    requireValue(validTargets.has(annotation.targetId), `Annotation ${annotation.id} targets unknown id ${annotation.targetId}`);
  }
  for (const proposal of manifest.proposals || []) {
    for (const targetId of proposal.targetIds || []) {
      requireValue(validTargets.has(targetId), `Proposal ${proposal.id} targets unknown id ${targetId}`);
    }
  }
  for (const reply of manifest.modelReplies || []) {
    for (const targetId of reply.targetIds || []) {
      requireValue(validTargets.has(targetId), `Model reply ${reply.id} targets unknown id ${targetId}`);
    }
  }
  for (const resource of manifest.resources || []) {
    for (const targetId of resource.targetIds || []) {
      requireValue(validTargets.has(targetId), `Resource ${resource.id} targets unknown id ${targetId}`);
    }
  }
  for (const pinned of manifest.dashboard?.pinnedSectionIds || []) {
    requireValue(sectionIds.has(pinned), `Dashboard pins unknown section ${pinned}`);
  }

  const themes = manifest.visual?.themes || [];
  for (const requiredTheme of ['system', 'obsidian', 'graphite', 'paper', 'high-contrast']) {
    requireValue(themes.includes(requiredTheme), `visual.themes must include ${requiredTheme}`);
  }
  requireValue(themes.includes(manifest.visual?.defaultTheme), 'visual.defaultTheme must be listed in visual.themes');

  const publicFiles = await readdir(path.join(projectRoot, 'public'));
  if (!publicFiles.includes('manifest.webmanifest')) warnings.push('No web manifest; installability is optional but useful');

  if (errors.length) {
    console.error(`Validation failed for ${projectRoot}`);
    for (const error of errors) console.error(`- ERROR: ${error}`);
    for (const warning of warnings) console.error(`- WARNING: ${warning}`);
    process.exitCode = 1;
    return;
  }

  console.log(`Validated ${manifest.meta.documentId} ${manifest.meta.version}`);
  console.log(`- ${manifest.sections.length} sections`);
  console.log(`- ${manifest.proposals.length} proposals`);
  console.log(`- ${manifest.modelReplies.length} model replies`);
  console.log(`- ${manifest.resources.length} resources`);
  console.log(`- ${manifest.history.length} history events`);
  console.log(`- ${annotationsFile.annotations.length} annotations`);
  console.log(`- ${themes.length} themes`);
  for (const warning of warnings) console.log(`- WARNING: ${warning}`);
}

main().catch((error) => {
  if (!errors.length) console.error(`Validation failed: ${error.message}`);
  for (const item of errors) console.error(`- ERROR: ${item}`);
  process.exitCode = 1;
});
