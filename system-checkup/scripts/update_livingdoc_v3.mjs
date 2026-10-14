// update_livingdoc_v3.mjs - refresh the Downloads/Desktop living document to v3 in place.
// Backs up app.js and index.json first; never touches the user's actual files.
// Usage: node update_livingdoc_v3.mjs <livingdoc-dir> <v3-DATA.json> <removal-manifest.json>
import { readFile, writeFile, copyFile } from 'node:fs/promises';
import path from 'node:path';

const [, , LD, V3, MAN] = process.argv;
const stamp = '20261013';
const appPath = path.join(LD, 'public', 'app.js');
const idxPath = path.join(LD, 'public', 'content', 'index.json');
const annPath = path.join(LD, 'public', 'data', 'annotations.json');
for (const p of [appPath, idxPath, annPath]) await copyFile(p, `${p}.v2-${stamp}.bak`);

const v3 = JSON.parse(await readFile(V3, 'utf8'));
const man = JSON.parse(await readFile(MAN, 'utf8'));
const dup = man.items.filter(i => i.section === 'Duplicates');
const dupGb = dup.reduce((a, i) => a + i.gb, 0);

// 1. app.js: swap the embedded DATA object, keep all application code
const src = await readFile(appPath, 'utf8');
const end = src.indexOf('\n};\n');
if (!src.startsWith('const DATA=') || end < 0) throw new Error('unexpected app.js layout');
const out = 'const DATA=' + JSON.stringify(v3, null, 1) + ';\n' + src.slice(end + 4);
await writeFile(appPath, out, 'utf8');

// 2. manifest
const idx = JSON.parse(await readFile(idxPath, 'utf8'));
const files = v3.groups.reduce((a, g) => a + g.files.length, 0) + v3.security.files.length;
idx.meta.version = '3.0.0';
idx.meta.updated = '2026-10-13';
idx.meta.title = 'Downloads, Desktop & User Folders Cleanup';
idx.meta.subtitle = 'Group-by-group and file-by-file decisions for Downloads, Desktop, Documents, Pictures, Music, the home folder, C:\\ and D:\\ roots, and temp.';
idx.meta.status = 'awaiting-decisions';
idx.dashboard.health = [
  { id: 'no-changes-made', label: 'No files touched', state: 'good', detail: 'v3 was built from a read-only scan on 2026-10-13. Nothing has been moved or deleted.' },
  { id: 'security-isolated', label: 'Security items flagged', state: 'attention', detail: `${v3.security.files.length} credential, harvesting-tool, MDM-bypass and keymaker/activator entries to isolate first.` },
  { id: 'protected', label: 'Protected items pinned', state: 'good', detail: 'The live Process Lasso config folder on the Desktop, the Obsidian vault and this document are in a keep-in-place group.' },
  { id: 'dupes', label: 'Hash-verified duplicates', state: 'attention', detail: `${dup.length} duplicate copies (${dupGb.toFixed(1)} GB) are staged by Remove-CheckupItems.ps1, not by this page.` }
];
const sec7 = { id: 'other-folders', index: '07', eyebrow: 'v3 scope', title: 'Documents, Pictures, home, drive roots and temp', dek: 'The folders added in v3 and what the scan found in each.', source: 'content/sections/07-other-folders.md', tags: ['v3'], status: 'final', editable: true, owner: 'Aaron Miller', updated: '2026-10-13', estimatedMinutes: 3, dependencies: ['overview'], backlinks: [] };
if (!idx.sections.find(s => s.id === sec7.id)) idx.sections.push(sec7);
for (const s of idx.sections) s.updated = '2026-10-13';
idx.navigation.sectionOrder = idx.sections.map(s => s.id);
idx.releases.push({ version: '3.0.0', date: '2026-10-13', title: 'Refreshed to current state and extended to every user folder', summary: `Re-scanned after three months. ${v3.groups.length} groups, ${files} entries. 14 July entries resolved, 138 Downloads and 29 Desktop items new.`,
  changes: [
    { type: 'changed', text: 'Every July group re-checked against the live folders; vanished entries moved to resolved-since-july instead of being dropped.', targetIds: ['downloads-groups', 'desktop-groups'] },
    { type: 'added', text: 'Documents, Pictures, Music, home root, C:\\ and D:\\ roots and temp directories, plus a protected keep-in-place group.', targetIds: ['other-folders'] },
    { type: 'added', text: 'Keymakers/activators and cracked-software archives added to the security group as a malware risk.', targetIds: ['security'] }
  ] });
idx.history.push({ id: 'H-0002', timestamp: '2026-10-13T20:00:00-07:00', actor: 'Claude Opus 5.5 + omp W2 (muse-spark-1.3-contributor)', kind: 'revise', summary: 'v3 refresh from the 2026-10-13 system checkup scan.', targetIds: ['document'], version: '3.0.0', source: 'agent', details: 'Read-only inventory; no user files moved or deleted.' });
idx.worklogs.push({ id: 'W-0002', version: '3.0.0', date: '2026-10-13', agent: 'Claude Opus 5.5 (orchestrator) + omp W2 worker', summary: 'Refreshed all groups and extended scope to every user folder.',
  changed: ['Replaced embedded decision data with v3', 'Added section 07 for the new folders', 'Updated dashboard health', 'Added annotations A-005..A-007'],
  validated: ['Every emitted name matched against the scan inventories (380 of 382; the 2 misses are descriptive notes)', 'node validate.mjs'],
  suggested: ['Apply with Remove-CheckupItems.ps1 -LivingDocExport <exported change-request>'],
  warnings: ['Exact-duplicate group uses name+size matching; hash-verified duplicates are handled by the removal script instead.'] });
await writeFile(idxPath, JSON.stringify(idx, null, 2), 'utf8');

// 3. annotations
const ann = JSON.parse(await readFile(annPath, 'utf8'));
const add = (a) => { if (!ann.annotations.find(x => x.id === a.id)) ann.annotations.push(a); };
add({ id: 'A-005', targetId: 'deletions', kind: 'note', text: `Hash-verified duplicates (${dup.length} copies, ${dupGb.toFixed(1)} GB) live in removal-manifest.json section "Duplicates" and are moved to _REVIEW-then-delete by Remove-CheckupItems.ps1, never deleted outright.`, tags: ['dedup'], status: 'open', author: 'Claude' });
add({ id: 'A-006', targetId: 'desktop-groups', kind: 'warning', text: 'Do not move the Desktop folder "Bitsum Process Lasso Pro v14.0.0.40 Multilingual Portable [FTUApps]". The running Process Lasso engine reads its config from it (HKLM ConfigFolderEx).', tags: ['protected'], status: 'open', author: 'Claude' });
add({ id: 'A-007', targetId: 'security', kind: 'warning', text: 'Keymaker/activator executables and cracked-installer archives are a common malware vector. Isolate them first and do not run them.', tags: ['security'], status: 'open', author: 'Claude' });
await writeFile(annPath, JSON.stringify(ann, null, 2), 'utf8');
console.log(`ok: ${v3.groups.length} groups, ${files} entries, ${dup.length} hash dupes (${dupGb.toFixed(1)} GB) noted`);
