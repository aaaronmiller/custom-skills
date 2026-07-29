import assert from 'node:assert/strict';
import { sectionIdFromHash } from '../public/navigation.mjs';

const sectionIds = ['start-here', 'current project', 'what-to-do'];

assert.equal(sectionIdFromHash('#start-here', sectionIds), 'start-here');
assert.equal(sectionIdFromHash('#current%20project', sectionIds), 'current project');
assert.equal(sectionIdFromHash('#missing', sectionIds), null);
assert.equal(sectionIdFromHash('#%E0%A4%A', sectionIds), null);
assert.equal(sectionIdFromHash('', sectionIds), null);

console.log('section deep-link checks passed');
