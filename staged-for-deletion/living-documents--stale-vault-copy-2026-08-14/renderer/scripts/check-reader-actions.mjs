import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { annotationDialogConfig, resolveQuickTheme } from '../public/review-actions.mjs';

const app = await readFile(new URL('../public/app.js', import.meta.url), 'utf8');

assert.equal((app.match(/class="dock-primary"/g) || []).length, 2, 'reader dock must render exactly two primary actions');
assert.doesNotMatch(app, /class="dock-primary"[^>]*data-action="quick-edit"/, 'Markdown drafting must not be a primary dock action');
assert.match(app, /data-action="annotation-markdown-draft"/, 'content-note flow must expose local Markdown drafting');
assert.match(app, /data-action="quick-theme"/, 'upper-right quick theme control must exist');
assert.match(app, /data-tooltip=/, 'reader controls must use authored tooltip content');
assert.doesNotMatch(app, /startViewTransition/, 'theme changes must not animate the whole document');

const contentWithQuote = annotationDialogConfig('content', { targetTitle: 'Requirements', quote: 'Selected text' });
assert.equal(contentWithQuote.showQuote, true);
assert.equal(contentWithQuote.quote, 'Selected text');
assert.equal(contentWithQuote.submitLabel, 'Save content note');
assert.equal(contentWithQuote.showMarkdownDraft, true);

const contentWithoutQuote = annotationDialogConfig('content', { targetTitle: 'Requirements' });
assert.equal(contentWithoutQuote.showQuote, false);
assert.equal(contentWithoutQuote.quote, '');

const layout = annotationDialogConfig('layout', { targetTitle: 'Living Documents', quote: 'ignored' });
assert.equal(layout.showQuote, false);
assert.equal(layout.quote, '');
assert.equal(layout.submitLabel, 'Save layout note');
assert.equal(layout.showMarkdownDraft, false);

assert.equal(resolveQuickTheme({ theme: 'paper', lastDark: 'graphite' }), 'graphite');
assert.equal(resolveQuickTheme({ theme: 'obsidian', lastDark: 'graphite' }), 'paper');
assert.equal(resolveQuickTheme({ theme: 'system', prefersDark: true, lastDark: 'high-contrast' }), 'paper');
assert.equal(resolveQuickTheme({ theme: 'system', prefersDark: false, lastDark: 'high-contrast' }), 'high-contrast');
assert.equal(resolveQuickTheme({ theme: 'paper', lastDark: 'invalid' }), 'obsidian');

console.log('reader action checks passed');
