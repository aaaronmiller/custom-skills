/* Verify the public, local-only Portfolio API contract without mutating source data. */

const baseUrl = process.env.LIVING_DOCUMENTS_READER_URL || 'http://127.0.0.1:4173';
const requiredKeys = [
  'portfolio', 'source', 'decisions', 'workstreams', 'activity', 'gitPulse',
  'sourceControlRisk', 'health', 'evidenceHealth', 'projectSummaries',
  'delegation', 'work',
];

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function assertOperations(payload, label) {
  assert(payload && typeof payload === 'object' && !Array.isArray(payload), `${label}: payload must be an object`);
  for (const key of requiredKeys) assert(Object.hasOwn(payload, key), `${label}: missing ${key}`);
  assert(Array.isArray(payload.portfolio.projects) && payload.portfolio.projects.length > 0, `${label}: portfolio projects must be non-empty`);
  assert(Array.isArray(payload.activity) && payload.activity.length <= 60, `${label}: activity must be bounded to 60 events`);
  assert(Array.isArray(payload.gitPulse.projects), `${label}: gitPulse.projects must be an array`);
  assert(Array.isArray(payload.evidenceHealth), `${label}: evidenceHealth must be an array`);
  assert(Array.isArray(payload.projectSummaries), `${label}: projectSummaries must be an array`);
  assert(Array.isArray(payload.delegation.actionable) && Array.isArray(payload.delegation.decisions) && Array.isArray(payload.delegation.blocked), `${label}: delegation lanes must be arrays`);

  const ids = payload.portfolio.projects.map((project) => project.projectId);
  assert(new Set(ids).size === ids.length, `${label}: portfolio project IDs must be unique`);
  for (const project of payload.portfolio.projects) {
    assert(typeof project.projectId === 'string' && project.projectId.length > 0, `${label}: project ID missing`);
    assert(/^\/projects\/[a-z0-9]+(?:-[a-z0-9]+)*\/$/.test(project.href), `${label}: project href is not constrained`);
    assert(['fresh', 'stale', 'runtime-unavailable'].includes(project.projection?.state), `${label}: projection state is invalid`);
  }
  for (const event of payload.activity) {
    assert(['ledger', 'handoff'].includes(event.kind), `${label}: activity kind is invalid`);
    assert(Array.isArray(event.sessions), `${label}: activity sessions must be an array`);
  }
  for (const record of payload.evidenceHealth) {
    assert(Array.isArray(record.evidence), `${label}: evidence record is malformed`);
    for (const item of record.evidence) assert(typeof item.path === 'string' && typeof item.available === 'boolean', `${label}: evidence item is malformed`);
  }
  for (const decision of payload.decisions) {
    assert(Number.isInteger(decision.priority) && decision.priority > 0, `${label}: decision priority is invalid`);
    if (!decision.decision.startsWith('Resolved:')) {
      assert(decision.choice && typeof decision.choice.recommendation === 'string', `${label}: unresolved decision has no recommendation`);
      assert(Array.isArray(decision.choice.options) && decision.choice.options.length >= 2, `${label}: unresolved decision needs at least two choices`);
      assert(decision.choice.options.some((option) => option.recommended === true), `${label}: unresolved decision needs one recommended choice`);
      assert(typeof decision.tracking?.trackedSince === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(decision.tracking.trackedSince), `${label}: unresolved decision needs explicit tracking start`);
      assert(Number.isInteger(decision.tracking.ageDays) && decision.tracking.ageDays >= 0, `${label}: tracking age must be a non-negative integer`);
    }
  }
}

async function request(pathname) {
  const response = await fetch(`${baseUrl}${pathname}`);
  assert(response.status === 200, `${pathname}: expected HTTP 200, received ${response.status}`);
  assert(response.headers.get('content-type')?.startsWith('application/json'), `${pathname}: expected JSON content type`);
  assert(response.headers.get('cache-control') === 'no-store', `${pathname}: expected no-store cache policy`);
  assert(response.headers.get('x-content-type-options') === 'nosniff', `${pathname}: expected nosniff`);
  assert(response.headers.get('referrer-policy') === 'no-referrer', `${pathname}: expected no-referrer`);
  return { response, body: await response.json() };
}

const operations = await request('/api/operations');
assertOperations(operations.body, 'operations');

const exported = await request('/api/portfolio-export');
assert(exported.response.headers.get('content-disposition') === 'attachment; filename="living-documents-portfolio.json"', 'export: expected deterministic attachment filename');
assert(exported.body.schema === 'living-documents-portfolio-export/v1', 'export: schema mismatch');
assert(exported.body.readOnly === true, 'export: must declare readOnly true');
assert(typeof exported.body.generatedAt === 'string' && !Number.isNaN(Date.parse(exported.body.generatedAt)), 'export: generatedAt must be an ISO timestamp');
assertOperations(exported.body.payload, 'export payload');

const inbox = await request('/api/decision-reviews');
assert(inbox.body.schema === 'living-documents-local-decision-review-inbox/v1', 'decision-review inbox: schema mismatch');
assert(inbox.body.localOnly === true && Array.isArray(inbox.body.reviews), 'decision-review inbox: expected local-only review array');

console.log(JSON.stringify({
  ok: true,
  baseUrl,
  projects: operations.body.portfolio.projects.length,
  activity: operations.body.activity.length,
  evidenceRecords: operations.body.evidenceHealth.length,
  exportSchema: exported.body.schema,
}));
