/*
---
title: Living document validator
purpose: Validate IDs, media paths, worklogs, proposal states, and required canvas fields.
runtime: Node.js 20+
---
*/
import { promises as fs } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '../../..');
const contentPath = process.argv[2] ? path.resolve(process.argv[2]) : path.join(root, 'public', 'content.json');
const content = JSON.parse(await fs.readFile(contentPath, 'utf8'));
const errors = [];
const warnings = [];

function requireField(object, field, label) {
  if (object?.[field] === undefined || object?.[field] === null || object?.[field] === '') errors.push(`${label}.${field} is required`);
}

for (const field of ['documentId', 'title', 'subtitle', 'version', 'updated', 'status', 'thesis']) requireField(content.meta, field, 'meta');
if (!Array.isArray(content.sections) || !content.sections.length) errors.push('sections must be a non-empty array');
if (!Array.isArray(content.proposals)) errors.push('proposals must be an array');
if (!Array.isArray(content.worklogs) || !content.worklogs.length) errors.push('worklogs must be a non-empty array');

const sectionIds = new Set();
for (const [index, section] of (content.sections || []).entries()) {
  const label = `sections[${index}]`;
  for (const field of ['id', 'title', 'dek', 'markdown']) requireField(section, field, label);
  if (sectionIds.has(section.id)) errors.push(`Duplicate section id: ${section.id}`);
  sectionIds.add(section.id);
  if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(section.id)) warnings.push(`Section id is not kebab-case: ${section.id}`);
  for (const [mediaIndex, media] of (section.media || []).entries()) {
    requireField(media, 'src', `${label}.media[${mediaIndex}]`);
    requireField(media, 'alt', `${label}.media[${mediaIndex}]`);
    if (media.src && !/^https?:/.test(media.src)) {
      const file = path.join(root, 'public', media.src.replace(/^\//, ''));
      try { await fs.access(file); } catch { errors.push(`Missing media file: ${media.src}`); }
    }
  }
}

const proposalIds = new Set();
for (const [index, proposal] of (content.proposals || []).entries()) {
  const label = `proposals[${index}]`;
  for (const field of ['id', 'title', 'summary', 'impact', 'effort', 'decision']) requireField(proposal, field, label);
  if (proposalIds.has(proposal.id)) errors.push(`Duplicate proposal id: ${proposal.id}`);
  proposalIds.add(proposal.id);
  if (!['approve', 'defer', 'reject'].includes(proposal.decision)) errors.push(`Invalid decision for ${proposal.id}: ${proposal.decision}`);
}

const worklogIds = new Set();
for (const [index, entry] of (content.worklogs || []).entries()) {
  const label = `worklogs[${index}]`;
  for (const field of ['id', 'version', 'date', 'summary']) requireField(entry, field, label);
  if (worklogIds.has(entry.id)) errors.push(`Duplicate worklog id: ${entry.id}`);
  worklogIds.add(entry.id);
}

if (!content.visualRefactor || typeof content.visualRefactor !== 'object') errors.push('visualRefactor object is required');
if (content.visualRefactor?.density && (content.visualRefactor.density < 1 || content.visualRefactor.density > 10)) errors.push('visualRefactor.density must be 1-10');
if (content.visualRefactor?.ornament && (content.visualRefactor.ornament < 1 || content.visualRefactor.ornament > 10)) errors.push('visualRefactor.ornament must be 1-10');

const report = { ok: errors.length === 0, contentPath, sections: sectionIds.size, proposals: proposalIds.size, worklogs: worklogIds.size, errors, warnings };
console.log(JSON.stringify(report, null, 2));
if (errors.length) process.exit(1);
