/*
---
title: Mechanism specification validator
purpose: Validate reusable mechanism IDs, controls, states, locks, accessibility, and compiler metadata.
runtime: Node.js 20+
---
*/
import { promises as fs } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const defaultSpec = path.resolve(here, '../examples/mechanism-spec.example.json');
const specPath = process.argv[2] ? path.resolve(process.argv[2]) : defaultSpec;
const spec = JSON.parse(await fs.readFile(specPath, 'utf8'));
const errors = [];
const warnings = [];
const ids = new Set();

for (const field of ['schemaVersion', 'id', 'version', 'title', 'medium', 'sections', 'serialization', 'accessibility', 'compiler']) {
  if (spec[field] === undefined) errors.push(`Missing top-level field: ${field}`);
}
if (!Array.isArray(spec.sections) || !spec.sections.length) errors.push('sections must be non-empty');
for (const section of spec.sections || []) {
  if (!section.id) errors.push('Every section requires id');
  if (ids.has(section.id)) errors.push(`Duplicate id: ${section.id}`);
  ids.add(section.id);
  if (!Array.isArray(section.controls)) errors.push(`Section ${section.id} requires controls array`);
  for (const control of section.controls || []) {
    if (!control.id || !control.type) errors.push(`Control in ${section.id} requires id and type`);
    if (ids.has(control.id)) errors.push(`Duplicate id: ${control.id}`);
    ids.add(control.id);
    if (control.lock?.enabled && !control.lock.scope) errors.push(`Locked control ${control.id} requires scope`);
    if (control.authority && !['manual', 'bank', 'artist', 'culture', 'reference', 'rival', 'random-constrained', 'mutation'].includes(control.authority)) warnings.push(`Unknown authority ${control.authority} on ${control.id}`);
  }
}
if (spec.accessibility?.keyboard !== true) errors.push('accessibility.keyboard must be true');
if (spec.accessibility?.reducedMotion !== true) errors.push('accessibility.reducedMotion must be true');
if (!spec.compiler?.output) errors.push('compiler.output is required');

const report = { ok: errors.length === 0, specPath, ids: ids.size, errors, warnings };
console.log(JSON.stringify(report, null, 2));
if (errors.length) process.exit(1);
