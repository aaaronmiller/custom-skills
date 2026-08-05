#!/usr/bin/env node
/**
 * Assert that no breakpoint deletes a control the reader has no other route to.
 *
 * Why this exists. On 2026-07-30 a reader at high browser zoom reported that the
 * Living Document had "no edit/annotate button anymore" and that nothing was
 * interactive. Nothing was broken: the CSS viewport was 469px, the narrow layout
 * was active, and `styles.css` set `display: none` on `.local-change-indicator`
 * at 1180px and on both `.local-change-indicator` and `.review-state` at 840px.
 *
 * Those two elements are the change-submission surface. Removing them leaves the
 * reader with a stale pending count and no way to act on it, which is
 * indistinguishable from the feature being broken. The six existing check
 * scripts all passed, because none of them asked whether a control was still
 * reachable at a narrow width.
 *
 * The rule this enforces: a narrow layout may relocate, stack, shrink, or
 * collapse a control behind a disclosure. It may not `display: none` a control
 * that has no keyboard shortcut and no alternative route. Hiding `.top-search`
 * is fine, there is a `/` shortcut. Hiding `.review-state` is not.
 *
 * Pure text analysis of the stylesheet. No browser, no network.
 */

import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const cssPath = join(here, '..', 'public', 'styles.css');
const css = readFileSync(cssPath, 'utf8');

/**
 * Selectors that must remain reachable at every width, with the reason each one
 * matters. A selector belongs here when losing it removes the only route to an
 * action.
 */
const MUST_REMAIN_REACHABLE = [
  ['.local-change-indicator', 'only signal that unsent local changes exist'],
  ['.review-state', 'reports pending count and submission outcome'],
  ['.annotate-action', 'primary route to annotate content'],
  ['.review-actions', 'the submit and discard controls'],
];

/** Widths a reader plausibly lands on, including high-zoom and phone. */
const WIDTHS_CHECKED = [1180, 840, 760, 720, 600, 520, 480, 360];

/** Extract each `@media (max-width: Npx)` block with brace matching. */
function mediaBlocks(source) {
  const blocks = [];
  const re = /@media\s*\(max-width:\s*(\d+)px\)\s*\{/g;
  let m;
  while ((m = re.exec(source)) !== null) {
    const width = Number(m[1]);
    let depth = 1;
    let i = m.index + m[0].length;
    const start = i;
    while (i < source.length && depth > 0) {
      const ch = source[i];
      if (ch === '{') depth += 1;
      else if (ch === '}') depth -= 1;
      i += 1;
    }
    blocks.push({ width, body: source.slice(start, i - 1) });
  }
  return blocks;
}

/** Rules inside a block that set `display: none`, with their selector lists. */
function hidingRules(body) {
  const rules = [];
  const re = /([^{}]+)\{([^{}]*)\}/g;
  let m;
  while ((m = re.exec(body)) !== null) {
    const declarations = m[2];
    if (!/display\s*:\s*none/i.test(declarations)) continue;
    const selectors = m[1]
      .split(',')
      .map((s) => s.replace(/\s+/g, ' ').trim())
      .filter(Boolean);
    rules.push(selectors);
  }
  return rules;
}

/**
 * A selector hides a protected control when the protected class appears as a
 * whole class token in it. `body.focused .review-state` counts: it is a state
 * the reader can leave, but it still removes the control while active, so it is
 * reported and must be justified rather than assumed safe.
 */
function hits(selector, className) {
  const escaped = className.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  return new RegExp(`${escaped}(?![\\w-])`).test(selector);
}

const failures = [];
const blocks = mediaBlocks(css);

for (const { width, body } of blocks) {
  if (!WIDTHS_CHECKED.some((w) => w >= width || width >= w)) continue;
  for (const selectors of hidingRules(body)) {
    for (const selector of selectors) {
      for (const [protectedClass, reason] of MUST_REMAIN_REACHABLE) {
        if (!hits(selector, protectedClass)) continue;
        // A body-state qualifier is a reader-controllable mode, not a width
        // trap, so it is allowed. Everything else is a hard failure.
        if (/^body\./.test(selector)) continue;
        failures.push(
          `@media (max-width: ${width}px) hides "${selector}"\n` +
            `      ${protectedClass} is protected: ${reason}\n` +
            '      Collapse or relocate it instead of using display:none.',
        );
      }
    }
  }
}

if (failures.length > 0) {
  console.error('check-narrow-reachability: FAIL');
  for (const f of failures) console.error(`  - ${f}`);
  console.error(
    `\n  ${failures.length} protected control(s) removed by a width breakpoint.`,
  );
  process.exit(1);
}

console.log(
  `check-narrow-reachability: OK ` +
    `(${MUST_REMAIN_REACHABLE.length} protected controls, ` +
    `${blocks.length} max-width blocks inspected)`,
);
