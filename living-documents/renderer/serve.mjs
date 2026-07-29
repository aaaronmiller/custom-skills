/* ---
file: serve.mjs
purpose: Serve every central Living Document through one shared renderer.
runtime: Node.js 20+
--- */

import http from 'node:http';
import { execFile } from 'node:child_process';
import { mkdir, readFile, readdir, rename, stat, unlink, writeFile } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { promisify } from 'node:util';

const rendererRoot = path.dirname(fileURLToPath(import.meta.url));
const shellRoot = path.join(rendererRoot, 'public');
const runtimeRoot = path.resolve(
  process.env.LIVING_DOCUMENTS_RUNTIME
    ? process.env.LIVING_DOCUMENTS_RUNTIME.replace(/^~(?=\/|$)/, os.homedir())
    : path.join(os.homedir(), '.cache/living-documents/runtime'),
);
const projectsRoot = path.join(runtimeRoot, 'projects');
const portfolioIndex = path.join(os.homedir(), 'LIVING_DOCUMENTS', 'INDEX.md');
const unblockQueue = path.join(os.homedir(), 'LIVING_DOCUMENTS', 'projects', 'living-documents', 'portfolio-unblock-queue.md');
const workstreamRegistry = path.join(os.homedir(), 'LIVING_DOCUMENTS', 'projects', 'living-documents', 'cross-project-workstream-registry.md');
const reconciliationMatrix = path.join(os.homedir(), 'LIVING_DOCUMENTS', 'projects', 'living-documents', 'project-reconciliation-status.md');
const ledgerRoot = path.join(os.homedir(), '.local', 'state', 'living-documents', 'ledger');
const handoffRoot = path.join(os.homedir(), '.local', 'state', 'living-documents', 'handoffs');
const decisionReviewRoot = path.join(os.homedir(), '.local', 'state', 'living-documents', 'decision-reviews');
const questionResponseRoot = path.join(os.homedir(), '.local', 'state', 'living-documents', 'question-responses');
const changeRequestRoot = path.join(os.homedir(), '.local', 'state', 'living-documents', 'change-requests');
const execFileAsync = promisify(execFile);
let gitPulseCache = { observedAt: 0, projects: [] };
const defaultProjectId = process.env.LIVING_DOCUMENT_PROJECT || 'living-documents';
const directDocumentRoot = process.env.LIVING_DOCUMENT_ROOT
  ? path.resolve(process.env.LIVING_DOCUMENT_ROOT)
  : null;
const port = Number.parseInt(process.env.PORT || '4173', 10);
const host = process.env.HOST || '127.0.0.1';
const shellFiles = new Set(['index.html', 'app.js', 'navigation.mjs', 'question-forms.mjs', 'styles.css', 'manifest.webmanifest']);
const mime = new Map([
  ['.html', 'text/html; charset=utf-8'],
  ['.js', 'text/javascript; charset=utf-8'],
  ['.mjs', 'text/javascript; charset=utf-8'],
  ['.css', 'text/css; charset=utf-8'],
  ['.json', 'application/json; charset=utf-8'],
  ['.md', 'text/markdown; charset=utf-8'],
  ['.svg', 'image/svg+xml'],
  ['.png', 'image/png'],
  ['.jpg', 'image/jpeg'],
  ['.jpeg', 'image/jpeg'],
  ['.gif', 'image/gif'],
  ['.webp', 'image/webp'],
  ['.mp4', 'video/mp4'],
  ['.webm', 'video/webm'],
  ['.mp3', 'audio/mpeg'],
  ['.m4a', 'audio/mp4'],
  ['.wav', 'audio/wav'],
  ['.csv', 'text/csv; charset=utf-8'],
  ['.txt', 'text/plain; charset=utf-8'],
  ['.ico', 'image/x-icon'],
  ['.webmanifest', 'application/manifest+json'],
]);

function inside(candidate, root) {
  return candidate === root || candidate.startsWith(`${root}${path.sep}`);
}

function jsonResponse(response, status, payload, extra = {}) {
  response.writeHead(status, {
    'Content-Type': 'application/json; charset=utf-8',
    'Cache-Control': 'no-store',
    'X-Content-Type-Options': 'nosniff',
    'Referrer-Policy': 'no-referrer',
    ...extra,
  });
  response.end(`${JSON.stringify(payload)}\n`);
}

async function requestJson(request, limit = 16 * 1024) {
  const chunks = [];
  let size = 0;
  for await (const chunk of request) {
    size += chunk.length;
    if (size > limit) throw Object.assign(new Error('Request body too large'), { code: 'E2BIG' });
    chunks.push(chunk);
  }
  return JSON.parse(Buffer.concat(chunks).toString('utf8'));
}

function validReview(payload) {
  const priority = Number(payload?.priority);
  const optionId = String(payload?.optionId || '');
  const note = String(payload?.note || '');
  if (!Number.isSafeInteger(priority) || priority < 1 || priority > 999) throw Object.assign(new Error('Invalid review priority'), { code: 'EINVAL' });
  if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(optionId)) throw Object.assign(new Error('Invalid review option'), { code: 'EINVAL' });
  if (note.length > 2000) throw Object.assign(new Error('Review note is too long'), { code: 'EINVAL' });
  return { schema: 'living-documents-local-decision-review/v1', priority, optionId, note, updatedAt: new Date().toISOString(), localOnly: true };
}

async function decisionReviews() {
  const entries = await readdir(decisionReviewRoot, { withFileTypes: true }).catch(() => []);
  const records = await Promise.all(entries.filter((item) => item.isFile() && /^decision-\d+\.json$/.test(item.name)).map(async (item) => {
    try { return JSON.parse(await readFile(path.join(decisionReviewRoot, item.name), 'utf8')); } catch { return null; }
  }));
  return records.filter(Boolean).sort((a, b) => a.priority - b.priority);
}

async function saveDecisionReview(payload) {
  const review = validReview(payload);
  await mkdir(decisionReviewRoot, { recursive: true, mode: 0o700 });
  const target = path.join(decisionReviewRoot, `decision-${review.priority}.json`);
  const temporary = path.join(decisionReviewRoot, `.decision-${review.priority}-${process.pid}.tmp`);
  await writeFile(temporary, `${JSON.stringify(review, null, 2)}\n`, { mode: 0o600 });
  await rename(temporary, target);
  return review;
}

async function clearDecisionReview(urlPath) {
  const priority = Number(new URL(urlPath, `http://${host}`).searchParams.get('priority'));
  if (!Number.isSafeInteger(priority) || priority < 1 || priority > 999) throw Object.assign(new Error('Invalid review priority'), { code: 'EINVAL' });
  const target = path.join(decisionReviewRoot, `decision-${priority}.json`);
  await unlink(target).catch((error) => { if (error?.code !== 'ENOENT') throw error; });
  return { priority, cleared: true, localOnly: true };
}

function questionIdentifier(value, label) {
  const result = String(value || '');
  if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(result) || result.length > 120) {
    throw Object.assign(new Error(`Invalid ${label}`), { code: 'EINVAL' });
  }
  return result;
}

async function validQuestionResponse(payload) {
  const projectId = questionIdentifier(payload?.projectId, 'project ID');
  const sectionId = questionIdentifier(payload?.sectionId, 'section ID');
  const documentRoot = await currentDocumentRoot(projectId);
  if (!documentRoot) throw Object.assign(new Error('Unknown project'), { code: 'ENOENT' });
  const manifest = JSON.parse(await readFile(path.join(documentRoot, 'public', 'content', 'index.json'), 'utf8'));
  if (!manifest.sections?.some((section) => section.id === sectionId)) {
    throw Object.assign(new Error('Unknown project section'), { code: 'ENOENT' });
  }
  if (!Array.isArray(payload?.answers) || payload.answers.length < 1 || payload.answers.length > 100) {
    throw Object.assign(new Error('Invalid answers'), { code: 'EINVAL' });
  }
  const seen = new Set();
  const answers = payload.answers.map((answer) => {
    const questionId = questionIdentifier(answer?.questionId, 'question ID');
    const optionId = questionIdentifier(answer?.optionId, 'option ID');
    const writeIn = String(answer?.writeIn || '').trim();
    if (seen.has(questionId)) throw Object.assign(new Error('Duplicate question ID'), { code: 'EINVAL' });
    if (writeIn.length > 4000) throw Object.assign(new Error('Write-in is too long'), { code: 'E2BIG' });
    if (optionId === 'write-in' && !writeIn) throw Object.assign(new Error('Write-in answer is empty'), { code: 'EINVAL' });
    seen.add(questionId);
    return { questionId, optionId, writeIn };
  });
  return { projectId, sectionId, answers };
}

async function saveQuestionResponse(payload) {
  const value = await validQuestionResponse(payload);
  const submittedAt = new Date().toISOString();
  const receiptId = `qr-${Date.now()}-${crypto.randomUUID().slice(0, 8)}`;
  const prompt = `Input received. Review Living Document ${value.projectId} / ${value.sectionId}, record the answers canonically, and continue only authorized unblocked work.`;
  const receipt = {
    schema: 'living-documents-question-response/v1',
    receiptId,
    ...value,
    submittedAt,
    status: 'pending',
    localOnly: true,
    sourceHref: `/projects/${value.projectId}/#${value.sectionId}`,
    attention: { transport: 'local-continuity', prompt },
  };
  const directory = path.join(questionResponseRoot, value.projectId, value.sectionId);
  await mkdir(directory, { recursive: true, mode: 0o700 });
  const target = path.join(directory, `${receiptId}.json`);
  const temporary = path.join(directory, `.${receiptId}.${process.pid}.tmp`);
  await writeFile(temporary, `${JSON.stringify(receipt, null, 2)}\n`, { mode: 0o600 });
  await rename(temporary, target);
  return receipt;
}

function boundedText(value, label, limit = 8000) {
  const result = String(value || '').trim();
  if (result.length > limit) throw Object.assign(new Error(`${label} is too long`), { code: 'E2BIG' });
  return result;
}

async function validChangeRequest(payload) {
  const projectId = questionIdentifier(payload?.document?.documentId, 'project ID');
  const documentRoot = await currentDocumentRoot(projectId);
  if (!documentRoot) throw Object.assign(new Error('Unknown project'), { code: 'ENOENT' });
  const manifest = JSON.parse(await readFile(path.join(documentRoot, 'public', 'content', 'index.json'), 'utf8'));
  const sectionIds = new Set((manifest.sections || []).map((section) => section.id));
  const drafts = Array.isArray(payload?.drafts) ? payload.drafts : [];
  const proposalDecisions = Array.isArray(payload?.proposalDecisions) ? payload.proposalDecisions : [];
  const annotations = Array.isArray(payload?.annotations) ? payload.annotations : [];
  const changeCount = drafts.length + proposalDecisions.length + annotations.length;
  if (changeCount < 1 || changeCount > 500) {
    throw Object.assign(new Error('Change request must contain 1-500 changes'), { code: 'EINVAL' });
  }
  const cleanDrafts = drafts.map((draft) => {
    const sectionId = questionIdentifier(draft?.sectionId, 'draft section ID');
    if (!sectionIds.has(sectionId)) throw Object.assign(new Error('Unknown draft section'), { code: 'ENOENT' });
    return {
      sectionId,
      title: boundedText(draft?.title, 'Draft title', 500),
      dek: boundedText(draft?.dek, 'Draft description', 2000),
      markdown: boundedText(draft?.markdown, 'Draft Markdown', 100000),
    };
  });
  const cleanDecisions = proposalDecisions.map((decision) => ({
    proposalId: questionIdentifier(decision?.proposalId, 'proposal ID'),
    decision: questionIdentifier(decision?.decision, 'proposal decision'),
  }));
  const cleanAnnotations = annotations.map((annotation) => {
    const targetId = questionIdentifier(annotation?.targetId, 'annotation target ID');
    if (targetId !== 'document' && !sectionIds.has(targetId)) {
      throw Object.assign(new Error('Unknown annotation target'), { code: 'ENOENT' });
    }
    return {
      id: boundedText(annotation?.id, 'Annotation ID', 160),
      targetId,
      quote: boundedText(annotation?.quote, 'Annotation quote', 12000),
      scope: ['content', 'layout'].includes(annotation?.scope) ? annotation.scope : 'content',
      kind: boundedText(annotation?.kind, 'Annotation kind', 80),
      text: boundedText(annotation?.text, 'Annotation text', 12000),
      status: boundedText(annotation?.status, 'Annotation status', 80),
      author: boundedText(annotation?.author, 'Annotation author', 200),
      createdAt: boundedText(annotation?.createdAt, 'Annotation timestamp', 80),
    };
  });
  return {
    projectId,
    changeCount,
    request: {
      document: {
        documentId: projectId,
        version: boundedText(payload?.document?.version, 'Document version', 80),
        formatVersion: boundedText(payload?.document?.formatVersion, 'Format version', 80),
      },
      scope: Array.isArray(payload?.scope)
        ? payload.scope.map((item) => questionIdentifier(item, 'scope ID')).filter((item) => item === 'document' || sectionIds.has(item))
        : [],
      drafts: cleanDrafts,
      proposalDecisions: cleanDecisions,
      annotations: cleanAnnotations,
    },
  };
}

async function saveChangeRequest(payload) {
  const value = await validChangeRequest(payload);
  const submittedAt = new Date().toISOString();
  const receiptId = `cr-${Date.now()}-${crypto.randomUUID().slice(0, 8)}`;
  const receipt = {
    schema: 'living-documents-change-request/v1',
    receiptId,
    ...value,
    submittedAt,
    status: 'pending',
    localOnly: true,
    sourceHref: `/projects/${value.projectId}/#view=changes`,
    attention: {
      transport: 'local-continuity',
      prompt: `Input received. Review Living Document change receipt ${receiptId} for ${value.projectId}, record valid changes canonically, and continue only authorized unblocked work.`,
    },
  };
  const directory = path.join(changeRequestRoot, value.projectId);
  await mkdir(directory, { recursive: true, mode: 0o700 });
  const target = path.join(directory, `${receiptId}.json`);
  const temporary = path.join(directory, `.${receiptId}.${process.pid}.tmp`);
  await writeFile(temporary, `${JSON.stringify(receipt, null, 2)}\n`, { mode: 0o600 });
  await rename(temporary, target);
  return receipt;
}

async function currentDocumentRoot(projectId) {
  if (projectId === defaultProjectId && directDocumentRoot) return directDocumentRoot;
  if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(projectId)) return null;
  const projectDirectory = path.resolve(projectsRoot, projectId);
  if (!inside(projectDirectory, projectsRoot)) return null;
  const pointerPath = path.join(projectDirectory, 'current.json');
  const pointer = JSON.parse(await readFile(pointerPath, 'utf8'));
  const documentRoot = path.resolve(pointer.root);
  if (!inside(documentRoot, projectDirectory)) return null;
  return documentRoot;
}

async function projectionFreshness(projectId) {
  const sourceRoot = path.join(os.homedir(), 'LIVING_DOCUMENTS', 'projects', projectId);
  const runtimeIndex = path.join(projectsRoot, projectId, 'current', 'public', 'content', 'index.json');
  const [entries, runtime] = await Promise.all([readdir(sourceRoot, { recursive: true }).catch(() => []), stat(runtimeIndex).catch(() => null)]);
  const markdown = entries.filter((entry) => entry.endsWith('.md'));
  const sourceStats = await Promise.all(markdown.map((entry) => stat(path.join(sourceRoot, entry)).catch(() => null)));
  const sourceUpdatedAt = Math.max(0, ...sourceStats.filter(Boolean).map((item) => item.mtimeMs));
  const runtimeUpdatedAt = runtime?.mtimeMs || 0;
  return { state: !runtime ? 'runtime-unavailable' : sourceUpdatedAt > runtimeUpdatedAt ? 'stale' : 'fresh', sourceUpdatedAt: sourceUpdatedAt ? new Date(sourceUpdatedAt).toISOString() : null, runtimeUpdatedAt: runtimeUpdatedAt ? new Date(runtimeUpdatedAt).toISOString() : null };
}

async function resolveDocumentFile(projectId, relative) {
  if (shellFiles.has(relative)) {
    const shellTarget = path.resolve(shellRoot, relative);
    return inside(shellTarget, shellRoot) ? shellTarget : null;
  }
  const documentRoot = await currentDocumentRoot(projectId);
  if (!documentRoot) return null;
  const publicRoot = path.join(documentRoot, 'public');
  const target = relative.startsWith('resources/')
    ? path.resolve(documentRoot, relative)
    : path.resolve(publicRoot, relative);
  const allowedRoot = relative.startsWith('resources/') ? documentRoot : publicRoot;
  return inside(target, allowedRoot) ? target : null;
}

async function resolveRequest(urlPath) {
  const decoded = decodeURIComponent(urlPath.split('?')[0]);
  const normalized = path.posix.normalize(decoded).replace(/^\.\.(?:\/|$)/, '');
  if (normalized.startsWith('/projects/')) {
    const [projectId, ...remainder] = normalized
      .slice('/projects/'.length)
      .split('/')
      .filter(Boolean);
    if (!projectId) return null;
    const relative = remainder.length ? remainder.join('/') : 'index.html';
    return resolveDocumentFile(projectId, relative);
  }
  const relative = normalized === '/' ? 'index.html' : normalized.replace(/^\/+/, '');
  return resolveDocumentFile(defaultProjectId, relative);
}

async function portfolioPayload() {
  const source = await readFile(portfolioIndex, 'utf8');
  const projectIds = [...source.matchAll(/\(projects\/([a-z0-9]+(?:-[a-z0-9]+)*)\/index\.md\)/g)].map((match) => match[1]);
  const projects = await Promise.all([...new Set(projectIds)].map(async (projectId) => {
    const documentRoot = await currentDocumentRoot(projectId);
    if (!documentRoot) return null;
    const manifest = JSON.parse(await readFile(path.join(documentRoot, 'public', 'content', 'index.json'), 'utf8'));
    return {
      projectId,
      title: manifest.meta?.title || projectId,
      subtitle: manifest.meta?.subtitle || '',
      status: manifest.meta?.status || 'unknown',
      lifecycle: manifest.meta?.lifecycle || 'unknown',
      updated: manifest.meta?.updated || null,
      sectionCount: Array.isArray(manifest.sections) ? manifest.sections.length : 0,
      sourceRoot: manifest.meta?.projectRoot || null,
      projection: await projectionFreshness(projectId),
      href: `/projects/${projectId}/`,
    };
  }));
  return { source: '/home/cheta/LIVING_DOCUMENTS/INDEX.md', projects: projects.filter(Boolean) };
}

async function ledgerRecords() {
  const files = await readdir(ledgerRoot, { withFileTypes: true });
  const records = await Promise.all(files.filter((item) => item.isFile() && item.name.endsWith('.json')).map(async (item) => (
    JSON.parse(await readFile(path.join(ledgerRoot, item.name), 'utf8'))
  )));
  return records;
}

async function handoffRecords() {
  const projects = await readdir(handoffRoot, { withFileTypes: true });
  const files = (await Promise.all(projects.filter((item) => item.isDirectory()).map(async (project) => (
    (await readdir(path.join(handoffRoot, project.name), { withFileTypes: true }))
      .filter((item) => item.isFile() && item.name.endsWith('.json'))
      .map((item) => path.join(handoffRoot, project.name, item.name))
  )))).flat();
  return Promise.all(files.map(async (file) => JSON.parse(await readFile(file, 'utf8'))));
}

async function gitPulse(projects) {
  const now = Date.now();
  if (now - gitPulseCache.observedAt < 60_000) return gitPulseCache.projects;
  const pulse = await Promise.all(projects.map(async (project) => {
    const root = project.sourceRoot;
    if (!root) return { projectId: project.projectId, state: 'no-source-root' };
    const source = await stat(root).catch(() => null);
    if (!source?.isDirectory()) return { projectId: project.projectId, state: 'unavailable-source-root' };
    try {
      const { stdout } = await execFileAsync('git', ['status', '--porcelain=v1', '--branch'], { cwd: root, timeout: 5000, maxBuffer: 256 * 1024 });
      const lines = stdout.trimEnd().split('\n');
      const branchLine = lines.shift() || '';
      const branch = branchLine.match(/^##\s+([^ .]+)(?:\.\.\.([^ ]+))?/);
      const ahead = Number(branchLine.match(/ahead (\d+)/)?.[1] || 0);
      const behind = Number(branchLine.match(/behind (\d+)/)?.[1] || 0);
      const log = await execFileAsync('git', ['log', '-1', '--format=%h%x09%aI%x09%s'], { cwd: root, timeout: 5000, maxBuffer: 256 * 1024 });
      const [shortSha = '', committedAt = '', subject = ''] = log.stdout.trim().split('\t');
      return { projectId: project.projectId, state: 'git', branch: branch?.[1] || 'detached', upstream: branch?.[2] || null, ahead, behind, dirtyCount: lines.filter(Boolean).length, shortSha, committedAt, subject };
    } catch (error) {
      if (error?.code === 128) return { projectId: project.projectId, state: 'not-git' };
      return { projectId: project.projectId, state: 'git-unavailable' };
    }
  }));
  gitPulseCache = { observedAt: now, projects: pulse };
  return pulse;
}

async function frontmatterJson(sourcePath, key) {
  const source = await readFile(sourcePath, 'utf8');
  const match = source.match(new RegExp(`^${key}:\\s*(.+)$`, 'm'));
  if (!match) throw new Error(`${path.basename(sourcePath)} has no ${key} value`);
  return JSON.parse(match[1]);
}

function trackingAgeDays(trackedSince) {
  if (typeof trackedSince !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(trackedSince)) return null;
  const started = Date.parse(`${trackedSince}T00:00:00.000Z`);
  if (!Number.isFinite(started)) return null;
  return Math.max(0, Math.floor((Date.now() - started) / 86_400_000));
}

async function operationsPayload() {
  const [portfolio, queueSource, records, workstreams, handoffs, reconciliationSource, decisionOptions, decisionTracking] = await Promise.all([
    portfolioPayload(),
    readFile(unblockQueue, 'utf8'),
    ledgerRecords(),
    frontmatterJson(workstreamRegistry, 'workstreams'),
    handoffRecords(),
    readFile(reconciliationMatrix, 'utf8'),
    frontmatterJson(unblockQueue, 'decision-options'),
    frontmatterJson(unblockQueue, 'decision-tracking'),
  ]);
  const mappingMatch = queueSource.match(/^decision-work-ids:\s*(.+)$/m);
  if (!mappingMatch) throw new Error('portfolio unblock queue has no decision-work-ids mapping');
  const decisionWorkIds = JSON.parse(mappingMatch[1]);
  const byId = new Map(records.map((record) => [record.work_id, record]));
  const decisions = queueSource.split('\n')
    .filter((line) => /^\|\s*\d+\s*\|/.test(line))
    .map((line) => line.split('|').slice(1, -1).map((cell) => cell.trim()))
    .map(([priority, decision, unblocks]) => {
      const workIds = decisionWorkIds[priority] || [];
      const work = workIds.map((workId) => byId.get(workId)).filter(Boolean);
      return {
        priority: Number(priority), decision, unblocks, workIds,
        choice: decisionOptions[priority] || null,
        tracking: decisionTracking[priority]
          ? { ...decisionTracking[priority], ageDays: trackingAgeDays(decisionTracking[priority].trackedSince) }
          : null,
        work: work.map((record) => ({
          workId: record.work_id, project: record.project, summary: record.summary,
          blocker: record.blocker, nextAction: record.next_action,
          evidence: record.evidence, updatedAt: record.updated_at,
          href: `/projects/${record.project}/`,
        })),
      };
    });
  const intake = records.filter((record) => record.status === 'unclassified');
  const actionable = records.filter((record) => ['active', 'interrupted'].includes(record.status));
  const blockers = records.filter((record) => record.status === 'blocked');
  const delegation = {
    intake: intake.map((record) => ({ workId: record.work_id, project: record.project, summary: record.summary, nextAction: record.next_action, href: `/projects/${record.project}/` })),
    actionable: actionable.map((record) => ({ workId: record.work_id, project: record.project, summary: record.summary, nextAction: record.next_action, href: `/projects/${record.project}/` })),
    decisions: decisions.filter((decision) => !decision.decision.startsWith('Resolved:')).map((decision) => ({ priority: decision.priority, decision: decision.decision, unblocks: decision.unblocks, workIds: decision.workIds })),
    blocked: blockers.map((record) => ({ workId: record.work_id, project: record.project, blocker: record.blocker, nextAction: record.next_action, href: `/projects/${record.project}/` })),
  };
  const activity = [
    ...records.map((record) => ({ kind: 'ledger', timestamp: record.updated_at, project: record.project, workId: record.work_id, status: record.status, summary: record.summary, sessions: record.sessions || [], href: `/projects/${record.project}/` })),
    ...handoffs.map((handoff) => ({ kind: 'handoff', timestamp: handoff.updated_at, project: handoff.project, workId: handoff.work_id, status: handoff.status, summary: handoff.summary, sessions: handoff.sessions || [], href: `/projects/${handoff.project}/` })),
  ].filter((event) => event.timestamp).sort((a, b) => b.timestamp.localeCompare(a.timestamp)).slice(0, 60);
  const projectById = new Map(portfolio.projects.map((project) => [project.projectId, project]));
  const hydratedWorkstreams = workstreams.map((workstream) => ({
    ...workstream,
    projects: workstream.projects.map((projectId) => projectById.get(projectId) || { projectId, title: projectId, href: `/projects/${projectId}/` }),
    relationships: workstream.relationships.map((relationship) => ({
      ...relationship,
      work: relationship.workIds.map((workId) => byId.get(workId)).filter(Boolean).map((record) => ({
        workId: record.work_id, project: record.project, status: record.status, nextAction: record.next_action,
        href: `/projects/${record.project}/`,
      })),
    })),
  }));
  const evidenceHealth = await Promise.all(records.map(async (record) => {
    const evidence = await Promise.all((record.evidence || []).map(async (item) => ({ path: item, available: Boolean(await stat(item).catch(() => null)) })));
    return { workId: record.work_id, project: record.project, status: record.status, evidence, href: `/projects/${record.project}/` };
  }));
  const sourceControlRisk = (await gitPulse(portfolio.projects)).filter((pulse) => pulse.state !== 'git' || pulse.dirtyCount > 0 || pulse.behind > 0).map((pulse) => ({
    ...pulse,
    href: `/projects/${pulse.projectId}/`,
    conditions: pulse.state !== 'git'
      ? [pulse.state]
      : [pulse.dirtyCount > 0 ? `${pulse.dirtyCount} dirty paths` : null, pulse.behind > 0 ? `${pulse.behind} behind upstream` : null].filter(Boolean),
  }));
  const portfolioById = new Map(portfolio.projects.map((project) => [project.projectId, project]));
  const projectSummaries = reconciliationSource.split('\n')
    .filter((line) => /^\|\s*[a-z0-9][a-z0-9-]*\s*\|/.test(line))
    .map((line) => line.split('|').slice(1, -1).map((cell) => cell.trim()))
    .map(([projectId, state, nextAction]) => ({
      projectId, state, nextAction,
      title: portfolioById.get(projectId)?.title || projectId,
      href: portfolioById.get(projectId)?.href || `/projects/${projectId}/`,
    }));
  const health = {
    dossiers: portfolio.projects.length,
    intakeWork: intake.length,
    activeWork: actionable.length,
    blockedWork: blockers.length,
    completedWork: records.filter((record) => record.status === 'complete').length,
    unresolvedDecisions: decisions.filter((decision) => !decision.decision.startsWith('Resolved:')).length,
    missingEvidencePaths: evidenceHealth.flatMap((record) => record.evidence).filter((item) => !item.available).length,
    sourceControlRisk: sourceControlRisk.length,
    staleProjections: portfolio.projects.filter((project) => project.projection?.state !== 'fresh').length,
  };
  return {
    portfolio,
    source: '/home/cheta/LIVING_DOCUMENTS/projects/living-documents/portfolio-unblock-queue.md',
    decisions,
    workstreams: hydratedWorkstreams,
    activity,
    gitPulse: { observedAt: new Date().toISOString(), projects: await gitPulse(portfolio.projects) },
    sourceControlRisk,
    health,
    evidenceHealth,
    projectSummaries,
    delegation,
    work: { intake, actionable, blockers, completeCount: records.filter((record) => record.status === 'complete').length },
  };
}

const server = http.createServer(async (request, response) => {
  try {
    if ((request.url || '/') === '/api/decision-reviews' && request.method === 'GET') {
      jsonResponse(response, 200, { schema: 'living-documents-local-decision-review-inbox/v1', localOnly: true, reviews: await decisionReviews() });
      return;
    }
    if ((request.url || '/') === '/api/decision-reviews' && request.method === 'POST') {
      jsonResponse(response, 201, { review: await saveDecisionReview(await requestJson(request)) });
      return;
    }
    if ((request.url || '/').startsWith('/api/decision-reviews') && request.method === 'DELETE') {
      jsonResponse(response, 200, { review: await clearDecisionReview(request.url || '/') });
      return;
    }
    if ((request.url || '/') === '/api/question-responses' && request.method === 'POST') {
      jsonResponse(response, 201, { receipt: await saveQuestionResponse(await requestJson(request, 128 * 1024)) });
      return;
    }
    if ((request.url || '/') === '/api/change-requests' && request.method === 'POST') {
      jsonResponse(response, 201, { receipt: await saveChangeRequest(await requestJson(request, 512 * 1024)) });
      return;
    }
    if ((request.url || '/') === '/api/portfolio') {
      const body = Buffer.from(`${JSON.stringify(await portfolioPayload())}\n`);
      response.writeHead(200, {
        'Content-Type': 'application/json; charset=utf-8',
        'Cache-Control': 'no-store',
        'X-Content-Type-Options': 'nosniff',
        'Referrer-Policy': 'no-referrer',
      });
      response.end(body);
      return;
    }
    if ((request.url || '/') === '/api/operations') {
      const body = Buffer.from(`${JSON.stringify(await operationsPayload())}\n`);
      response.writeHead(200, {
        'Content-Type': 'application/json; charset=utf-8',
        'Cache-Control': 'no-store',
        'X-Content-Type-Options': 'nosniff',
        'Referrer-Policy': 'no-referrer',
      });
      response.end(body);
      return;
    }
    if ((request.url || '/') === '/api/portfolio-export') {
      const body = Buffer.from(`${JSON.stringify({ schema: 'living-documents-portfolio-export/v1', generatedAt: new Date().toISOString(), readOnly: true, payload: await operationsPayload() })}\n`);
      response.writeHead(200, {
        'Content-Type': 'application/json; charset=utf-8',
        'Cache-Control': 'no-store',
        'Content-Disposition': 'attachment; filename="living-documents-portfolio.json"',
        'X-Content-Type-Options': 'nosniff',
        'Referrer-Policy': 'no-referrer',
      });
      response.end(body);
      return;
    }
    let target = await resolveRequest(request.url || '/');
    if (!target) {
      response.writeHead(400).end('Bad request');
      return;
    }
    const info = await stat(target).catch(() => null);
    if (info?.isDirectory()) target = path.join(target, 'index.html');
    const body = await readFile(target);
    const extension = path.extname(target).toLowerCase();
    response.writeHead(200, {
      'Content-Type': mime.get(extension) || 'application/octet-stream',
      'Cache-Control': extension === '.html' ? 'no-store' : 'no-cache',
      'X-Content-Type-Options': 'nosniff',
      'Referrer-Policy': 'no-referrer',
    });
    response.end(body);
  } catch (error) {
    response.writeHead(error?.code === 'ENOENT' ? 404 : 500, {
      'Content-Type': 'text/plain; charset=utf-8',
    });
    response.end(error?.code === 'ENOENT' ? 'Not found' : 'Server error');
  }
});

server.listen(port, host, () => {
  console.log(`Living Documents: http://${host}:${port}`);
});
