/* ---
file: app.js
purpose: Shared dependency-free Living Documents CMS renderer.
version: 2.0.0
--- */

import { projectRouteFromHash, sectionIdFromHash } from './navigation.mjs';
import { parseQuestionSection } from './question-forms.mjs';
import { annotationDialogConfig, darkThemes, resolveQuickTheme } from './review-actions.mjs';

const app = document.querySelector('#app');
const themeNames = {
  system: 'System',
  obsidian: 'Obsidian',
  graphite: 'Graphite',
  paper: 'Paper',
  'high-contrast': 'High contrast'
};
const projectViewIds = ['dashboard', 'document', 'projects', 'sources', 'ideas', 'timeline', 'history', 'changelog', 'search', 'changes'];
const motionNames = { system: 'System motion', full: 'Full motion', reduced: 'Reduced motion' };
const viewDefinitions = [
  ['dashboard', '⌂', 'Project overview'],
  ['document', '¶', 'Read all pages'],
  ['projects', '◫', 'Cross-project links'],
  ['reconciliation', '≋', 'Source audit'],
  ['changes', '✎', 'Local change draft'],
  ['history', '↺', 'Project history'],
  ['changelog', 'Δ', 'Release notes'],
  ['search', '⌕', 'Search this project']
];
const primaryViewIds = new Set(['dashboard', 'document']);
const sectionExplanations = {
  'start-here': 'Fast orientation for a fresh person or session.',
  index: 'Canonical project page index and entry points.',
  'what-to-do': 'Current priority, blockers, and next admissible action.',
  requirements: 'What this project must achieve and why.',
  plan: 'How work is sequenced and validated.',
  tasks: 'Evidence-gated work record; completed boxes link to proof.',
  decisions: 'Canonical decisions already made, rejected directions, and unresolved policy. This is separate from the Portfolio’s cross-project decision queue.',
  history: 'Append-only project milestones and recovery context.',
  resources: 'Evidence, reference material, and external source links.'
};

const state = {
  manifest: null,
  annotations: [],
  sources: [],
  ideas: [],
  projects: [],
  blockingItems: [],
  operations: null,
  sectionContent: new Map(),
  activeView: 'dashboard',
  activeSectionId: null,
  searchQuery: '',
  sectionNavQuery: '',
  sectionIndexExpanded: false,
  statusFilter: 'all',
  tagFilter: 'all',
  historyFilter: 'all',
  theme: localStorage.getItem('ldf:theme') || 'obsidian',
  motion: localStorage.getItem('ldf:motion') || 'system',
  density: localStorage.getItem('ldf:density') || 'comfortable',
  focused: localStorage.getItem('ldf:focused') === 'true',
  drafts: {},
  proposalDecisions: {},
  localAnnotations: [],
  localHistory: [],
  undoStack: [],
  redoStack: [],
  commandIndex: 0,
  observer: null,
  toastTimer: null
};

let portfolioSnapshot = null;
let portfolioRefreshTimer = null;
let portfolioView = localStorage.getItem('ldf:portfolio-view') || 'overview';
let drawerReturnFocus = null;
let dialogReturnAction = null;
let tooltipTimer = null;
const portfolioViews = [
  ['overview', 'Overview'],
  ['decisions', 'Decisions'],
  ['work', 'Work'],
  ['projects', 'Projects'],
  ['activity', 'Activity'],
  ['evidence', 'Git + evidence']
];

function escapeHtml(value = '') {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}

function safeHref(value = '') {
  const href = String(value).trim();
  return /^(https?:|mailto:|#|\/|\.\/|\.\.\/)/i.test(href) ? href : '#';
}

// Canonical Markdown cross-references point at files: [Requirements](requirements.md),
// [Lineage](../ai-gateway/gateway-archive-lineage.md). safeHref rejected every one of
// them, so all 136 in-prose links on a single page resolved to '#' and did nothing.
// Those links are the corpus's own navigation; silently dropping them is what made
// the reader feel like a set of disconnected documents. Audited 2026-08-04.
function resolveDocHref(href = '') {
  const raw = String(href).trim();
  if (!raw) return '#';
  if (/^(https?:|mailto:)/i.test(raw)) return raw;
  if (raw.startsWith('#')) return raw;

  // Cross-project: ../<project-id>/<page>.md[#frag]. The project segment must be
  // a real id: '..' here means the link climbs above projects/ to a corpus-root
  // file such as ../../system/SPECIFICATION.md. Those have no projected route,
  // so they are marked unresolved rather than rendered as /projects/../#X, which
  // looks like a working link and is not.
  let m = raw.match(/^\.\.\/([A-Za-z0-9][A-Za-z0-9._-]*)\/(.+?)\.md(#.*)?$/i);
  if (m && m[1] !== '..') {
    const page = m[2].split('/').pop();
    return `/projects/${m[1]}/#${m[3] ? m[3].slice(1) : page}`;
  }

  // Any remaining path that climbs out of the project folder is not projected.
  if (raw.startsWith('../..') || /(^|\/)\.\.\//.test(raw.replace(/^\.\.\//, ''))) return '#';

  // Same project: <page>.md, ./<page>.md, or concepts/<page>.md
  m = raw.match(/^\.?\/?(.+?)\.md(#.*)?$/i);
  if (m) {
    const page = m[1].split('/').pop();
    return `#${m[2] ? m[2].slice(1) : page}`;
  }

  return safeHref(raw);
}

function inlineMarkdown(value = '') {
  let output = escapeHtml(value);
  output = output.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, (_, label, href) => {
    const safe = escapeHtml(safeHref(href));
    return `<img src="${safe}" alt="${escapeHtml(label)}" loading="lazy" />`;
  });
  output = output.replace(/`([^`]+)`/g, '<code>$1</code>');
  output = output.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  output = output.replace(/\*([^*]+)\*/g, '<em>$1</em>');
  output = output.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (_, label, href) => {
    const resolved = resolveDocHref(href);
    const safe = escapeHtml(resolved);
    const external = /^https?:/i.test(href) ? ' target="_blank" rel="noreferrer"' : '';
    const dead = resolved === '#' ? ' class="link-unresolved" title="This link has no resolvable target"' : '';
    return `<a href="${safe}"${external}${dead}>${label}</a>`;
  });
  return output;
}

function stripFrontmatter(markdown = '') {
  return markdown.replace(/^---\s*\n[\s\S]*?\n---\s*\n?/, '').trim();
}

function renderMarkdown(markdown = '') {
  const lines = stripFrontmatter(markdown).replaceAll('\r\n', '\n').split('\n');
  const output = [];
  let paragraph = [];
  let listType = null;
  let codeFence = false;
  let codeLines = [];

  const flushParagraph = () => {
    if (!paragraph.length) return;
    output.push(`<p>${inlineMarkdown(paragraph.join(' '))}</p>`);
    paragraph = [];
  };
  const closeList = () => {
    if (!listType) return;
    output.push(`</${listType}>`);
    listType = null;
  };

  for (const line of lines) {
    if (line.trim().startsWith('```')) {
      flushParagraph();
      closeList();
      if (codeFence) {
        output.push(`<pre><code>${escapeHtml(codeLines.join('\n'))}</code></pre>`);
        codeLines = [];
        codeFence = false;
      } else {
        codeFence = true;
      }
      continue;
    }
    if (codeFence) {
      codeLines.push(line);
      continue;
    }
    if (!line.trim()) {
      flushParagraph();
      closeList();
      continue;
    }
    const heading = line.match(/^(#{2,4})\s+(.+)$/);
    if (heading) {
      flushParagraph();
      closeList();
      const level = heading[1].length;
      output.push(`<h${level}>${inlineMarkdown(heading[2])}</h${level}>`);
      continue;
    }
    if (/^---+$/.test(line.trim())) {
      flushParagraph();
      closeList();
      output.push('<hr />');
      continue;
    }
    const quote = line.match(/^>\s?(.+)$/);
    if (quote) {
      flushParagraph();
      closeList();
      output.push(`<blockquote>${inlineMarkdown(quote[1])}</blockquote>`);
      continue;
    }
    const unordered = line.match(/^[-*]\s+(.+)$/);
    const ordered = line.match(/^\d+\.\s+(.+)$/);
    if (unordered || ordered) {
      flushParagraph();
      const nextType = ordered ? 'ol' : 'ul';
      if (listType !== nextType) {
        closeList();
        listType = nextType;
        output.push(`<${listType}>`);
      }
      output.push(`<li>${inlineMarkdown((unordered || ordered)[1])}</li>`);
      continue;
    }
    paragraph.push(line.trim());
  }
  flushParagraph();
  closeList();
  if (codeFence) output.push(`<pre><code>${escapeHtml(codeLines.join('\n'))}</code></pre>`);
  return output.join('\n');
}

function questionResponseStorage() {
  try {
    const value = JSON.parse(localStorage.getItem(storageKey('question-responses')) || '{}');
    return value && typeof value === 'object' ? value : {};
  } catch {
    return {};
  }
}

function saveQuestionResponseDraft(sectionId, questionId, update) {
  const responses = questionResponseStorage();
  responses[sectionId] ||= {};
  responses[sectionId][questionId] = {
    ...(responses[sectionId][questionId] || {}),
    ...update,
    updatedAt: new Date().toISOString(),
  };
  localStorage.setItem(storageKey('question-responses'), JSON.stringify(responses));
}

function renderQuestionForm(section) {
  const parsed = parseQuestionSection(section.markdown);
  if (!parsed) return `<div class="markdown-body">${renderMarkdown(section.markdown)}</div>`;
  const responses = questionResponseStorage()[section.id] || {};
  const questions = parsed.questions.map((question) => {
    const response = responses[question.id] || {};
    const choices = question.options.map((option) => `
      <label class="portfolio-choice ${response.optionId === option.id ? 'active' : ''}">
        <input type="radio" required name="${escapeHtml(section.id)}-${escapeHtml(question.id)}" value="${escapeHtml(option.id)}" data-action="question-option" data-section="${escapeHtml(section.id)}" data-question="${escapeHtml(question.id)}" ${response.optionId === option.id ? 'checked' : ''}>
        <span><strong>${escapeHtml(option.id.toUpperCase())}. ${escapeHtml(option.label)}</strong>${option.recommended ? '<span class="tag tag-static">recommended</span>' : ''}${option.detail ? `<small>${escapeHtml(option.detail)}</small>` : ''}</span>
      </label>`).join('');
    return `
      <fieldset class="question-card" data-question-card="${escapeHtml(question.id)}">
        <legend><span class="decision-priority">${question.number}</span>${escapeHtml(question.title)}</legend>
        <div class="portfolio-choice-list">${choices}
          <label class="portfolio-choice ${response.optionId === 'write-in' ? 'active' : ''}">
            <input type="radio" required name="${escapeHtml(section.id)}-${escapeHtml(question.id)}" value="write-in" data-action="question-option" data-section="${escapeHtml(section.id)}" data-question="${escapeHtml(question.id)}" ${response.optionId === 'write-in' ? 'checked' : ''}>
            <span><strong>Write my own answer</strong><small>${escapeHtml(question.writeIn || 'Use this when none of the listed choices fit.')}</small></span>
          </label>
          <label class="portfolio-note-label" for="${escapeHtml(section.id)}-${escapeHtml(question.id)}-write-in">Custom answer</label>
          <textarea id="${escapeHtml(section.id)}-${escapeHtml(question.id)}-write-in" data-question-write-in="${escapeHtml(question.id)}" data-section="${escapeHtml(section.id)}" placeholder="Explain the direction, constraint, or alternative you want.">${escapeHtml(response.writeIn || '')}</textarea>
        </div>
      </fieldset>`;
  }).join('');
  return `
    <div class="markdown-body">${renderMarkdown(parsed.before)}</div>
    <form class="question-review-form" data-question-response-form="${escapeHtml(section.id)}">
      <div class="question-review-intro">
        <div><span class="eyebrow">Decision packet</span><h3>Answer ${parsed.questions.length} questions</h3></div>
        <p>${parsed.lead ? inlineMarkdown(parsed.lead) : 'Choose one option per question or write your own answer.'}</p>
      </div>
      ${questions}
      <div class="question-submit-bar">
        <p>Submission creates a loopback-local receipt and alerts the continuity resolver. It does not execute work or change canonical Markdown by itself.</p>
        <button class="primary-button" type="submit">Submit answers for agent review</button>
      </div>
    </form>`;
}

async function fetchJson(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`${url}: ${response.status}`);
  return response.json();
}

async function fetchText(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`${url}: ${response.status}`);
  return response.text();
}

function storageKey(name) {
  return `ldf:${state.manifest.meta.documentId}:${name}`;
}

function loadLocalState() {
  const parse = (name, fallback) => {
    try {
      return JSON.parse(localStorage.getItem(storageKey(name)) || JSON.stringify(fallback));
    } catch {
      return fallback;
    }
  };
  state.drafts = parse('drafts', {});
  state.proposalDecisions = parse('proposal-decisions', {});
  state.localAnnotations = parse('local-annotations', []);
  state.localHistory = parse('local-history', []);
}

function persistLocalState() {
  localStorage.setItem(storageKey('drafts'), JSON.stringify(state.drafts));
  localStorage.setItem(storageKey('proposal-decisions'), JSON.stringify(state.proposalDecisions));
  localStorage.setItem(storageKey('local-annotations'), JSON.stringify(state.localAnnotations));
  localStorage.setItem(storageKey('local-history'), JSON.stringify(state.localHistory));
}

function snapshot() {
  return JSON.stringify({
    drafts: state.drafts,
    proposalDecisions: state.proposalDecisions,
    localAnnotations: state.localAnnotations,
    localHistory: state.localHistory
  });
}

function pushUndo(label) {
  state.undoStack.push({ label, data: snapshot() });
  if (state.undoStack.length > 50) state.undoStack.shift();
  state.redoStack = [];
}

function restoreSnapshot(serialized) {
  const value = JSON.parse(serialized);
  state.drafts = value.drafts || {};
  state.proposalDecisions = value.proposalDecisions || {};
  state.localAnnotations = value.localAnnotations || [];
  state.localHistory = value.localHistory || [];
  persistLocalState();
}

function undo() {
  const entry = state.undoStack.pop();
  if (!entry) return toast('Nothing to undo');
  state.redoStack.push({ label: entry.label, data: snapshot() });
  restoreSnapshot(entry.data);
  render();
  toast(`Undid: ${entry.label}`);
}

function redo() {
  const entry = state.redoStack.pop();
  if (!entry) return toast('Nothing to redo');
  state.undoStack.push({ label: entry.label, data: snapshot() });
  restoreSnapshot(entry.data);
  render();
  toast(`Redid: ${entry.label}`);
}

function sectionById(id) {
  return state.manifest.sections.find((section) => section.id === id);
}

function effectiveSection(id) {
  const original = sectionById(id);
  if (!original) return null;
  const draft = state.drafts[id] || {};
  return {
    ...original,
    ...draft,
    tags: draft.tags || original.tags,
    markdown: draft.markdown ?? state.sectionContent.get(id) ?? ''
  };
}

function allAnnotations() {
  return [...state.annotations, ...state.localAnnotations];
}

function modelReplies() {
  return Array.isArray(state.manifest.modelReplies) ? state.manifest.modelReplies : [];
}

function resourceList() {
  return Array.isArray(state.manifest.resources) ? state.manifest.resources : [];
}

function projectList() {
  return state.projects;
}

function openBlockingItems() {
  return state.blockingItems.filter((item) => ['open', 'blocked'].includes(item.status));
}

function resourcesForSection(sectionId) {
  return resourceList().filter((resource) => (resource.targetIds || []).includes(sectionId));
}

function resourceHref(resource) {
  if (resource.url) return safeHref(resource.url);
  if (!resource.path) return '#';
  return resource.path.startsWith('resources/') ? `/${resource.path}` : safeHref(resource.path);
}

function renderResource(resource) {
  const href = resourceHref(resource);
  const title = escapeHtml(resource.title || resource.originalName || resource.id);
  const detail = escapeHtml(resource.description || resource.mimeType || '');
  let preview = '';
  if (resource.kind === 'image' && href !== '#') {
    preview = `<img class="resource-preview" src="${escapeHtml(href)}" alt="${title}" loading="lazy" />`;
  } else if (resource.kind === 'video' && href !== '#') {
    preview = `<video class="resource-preview" src="${escapeHtml(href)}" controls preload="metadata"></video>`;
  } else if (resource.kind === 'audio' && href !== '#') {
    preview = `<audio class="resource-audio" src="${escapeHtml(href)}" controls preload="metadata"></audio>`;
  }
  return `
    <article class="annotation-item">
      ${preview}
      <div class="annotation-title">${title} · ${escapeHtml(resource.kind || 'file')}</div>
      <p class="annotation-text">${detail}</p>
      <div class="annotation-meta"><span class="tag tag-static">${escapeHtml(resource.id)}</span><a class="tag" href="${escapeHtml(href)}" target="_blank" rel="noreferrer">${escapeHtml(resource.path || resource.url || 'external')}</a></div>
    </article>`;
}

function selectedQuote() {
  const selection = window.getSelection();
  const text = selection?.toString().trim() || '';
  if (!text) return { text: '', sectionId: state.activeSectionId || 'document' };
  let node = selection.anchorNode;
  if (node?.nodeType === Node.TEXT_NODE) node = node.parentElement;
  const section = node?.closest?.('[data-section-observe]');
  return {
    text: text.slice(0, 500),
    sectionId: section?.dataset.sectionObserve || state.activeSectionId || 'document'
  };
}

function decisionFor(proposal) {
  return state.proposalDecisions[proposal.id] || proposal.decision;
}

function localChangeCount() {
  return Object.keys(state.drafts).length + Object.keys(state.proposalDecisions).length + state.localAnnotations.length;
}

function submittedChangeReceipt() {
  try {
    const receipt = JSON.parse(localStorage.getItem(storageKey('last-change-receipt')) || 'null');
    return receipt?.snapshot === snapshot() ? receipt : null;
  } catch {
    return null;
  }
}

function currentSection() {
  return effectiveSection(state.activeSectionId || state.manifest.navigation.sectionOrder[0]);
}

function formatDate(value) {
  try {
    const dateOnly = String(value).match(/^(\d{4})-(\d{2})-(\d{2})$/);
    const date = dateOnly
      ? new Date(Number(dateOnly[1]), Number(dateOnly[2]) - 1, Number(dateOnly[3]))
      : new Date(value);
    return new Intl.DateTimeFormat(undefined, { year: 'numeric', month: 'short', day: 'numeric' }).format(date);
  } catch {
    return value;
  }
}

function formatDateTime(value) {
  try {
    return new Intl.DateTimeFormat(undefined, {
      year: 'numeric', month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit'
    }).format(new Date(value));
  } catch {
    return value;
  }
}

function statusDot(status) {
  return `<span class="status-dot ${escapeHtml(status)}" aria-hidden="true"></span>`;
}

function tagMarkup(tags = []) {
  return tags.map((tag) => `<button class="tag tag-filterable" data-action="tag-filter" data-value="${escapeHtml(tag)}" title="Show only sections tagged ${escapeHtml(tag)}">${escapeHtml(tag)}</button>`).join('');
}

function iconLabel(icon, label) {
  return `<span aria-hidden="true">${icon}</span><span>${escapeHtml(label)}</span>`;
}

function matchingSections() {
  return state.manifest.navigation.sectionOrder
    .map((id) => effectiveSection(id))
    .filter(Boolean)
    .filter((section) => state.statusFilter === 'all' || section.status === state.statusFilter)
    .filter((section) => state.tagFilter === 'all' || section.tags.includes(state.tagFilter));
}

function renderTopbar() {
  const changes = localChangeCount();
  const effectiveDark = state.theme === 'system'
    ? matchMedia('(prefers-color-scheme: dark)').matches
    : darkThemes.has(state.theme);
  const quickThemeLabel = effectiveDark ? 'Switch to light theme' : 'Switch to dark theme';
  const leftExpanded = window.matchMedia('(max-width: 840px)').matches
    ? document.body.classList.contains('left-open')
    : !document.body.classList.contains('left-collapsed');
  const rightExpanded = window.matchMedia('(max-width: 1180px)').matches
    ? document.body.classList.contains('right-open')
    : !document.body.classList.contains('right-collapsed');
  return `
    <header class="topbar">
      <div class="brand">
        <button class="rail-toggle" data-action="toggle-left" aria-controls="project-navigation" aria-expanded="${leftExpanded}" title="Show or hide project navigation"><span aria-hidden="true">☰</span><span class="rail-toggle-label">Pages</span></button>
        <a class="brand-mark" href="/" aria-label="Open Living Documents portfolio" title="Portfolio home: every project, blocker, decision, and activity surface">LD</a>
        <div class="brand-copy">
          <div class="brand-title">${escapeHtml(state.manifest.meta.title)}</div>
          <div class="brand-meta">v${escapeHtml(state.manifest.meta.version)} · ${escapeHtml(state.manifest.meta.status)}</div>
        </div>
      </div>
      <div class="top-search">
        <span class="search-glyph" aria-hidden="true">⌕</span>
        <input id="global-search" type="search" value="${escapeHtml(state.searchQuery)}" placeholder="Search sections, tags, or ideas" aria-label="Search document" />
        <span class="search-shortcut"><kbd>/</kbd></span>
      </div>
      <div class="top-actions">
        <nav class="workspace-shortcuts" aria-label="Workspace shortcuts">
          <a href="/">Portfolio</a>
          <a href="/#decisions">Decisions</a>
          <a href="/#activity">Activity</a>
        </nav>
        <button class="local-change-indicator" data-action="view" data-view="changes" data-tooltip="Review browser-local notes, drafts, and decisions before sending them.">${changes} local</button>
        <button class="theme-toggle" data-action="quick-theme" aria-label="${quickThemeLabel}" data-tooltip="${quickThemeLabel}. Shortcut — full preferences live in Settings."><span aria-hidden="true">${effectiveDark ? '☀' : '☾'}</span></button><button class="theme-toggle settings-entry" data-action="open-settings" aria-label="Open reader settings" data-tooltip="Theme, motion, and density — every reader preference in one place."><span aria-hidden="true">⚙</span></button>
        <button class="rail-toggle" data-action="toggle-right" aria-controls="context-inspector" aria-expanded="${rightExpanded}" title="Show or hide context and reader settings"><span class="rail-toggle-label">Context</span><span aria-hidden="true">◧</span></button>
      </div>
    </header>`;
}

function toggleSidebar(side) {
  const className = `${side}-collapsed`;
  document.body.classList.toggle(className);
  localStorage.setItem(`ldf:${side}-collapsed`, document.body.classList.contains(className) ? 'true' : 'false');
  document.querySelector(`[data-action="toggle-${side}"]`)?.setAttribute('aria-expanded', String(!document.body.classList.contains(className)));
}

function toggleDrawer(side, trigger) {
  const className = `${side}-open`;
  const willOpen = !document.body.classList.contains(className);
  closeDrawers(false);
  if (!willOpen) return;
  drawerReturnFocus = trigger;
  document.body.classList.add(className);
  const rail = document.querySelector(`.${side}-rail`);
  rail?.setAttribute('role', 'dialog');
  rail?.setAttribute('aria-modal', 'true');
  trigger?.setAttribute('aria-expanded', 'true');
  requestAnimationFrame(() => rail?.querySelector('input, button, a, select, summary')?.focus());
}

function restoreSidebarPreferences() {
  for (const side of ['left', 'right']) {
    document.body.classList.toggle(`${side}-collapsed`, localStorage.getItem(`ldf:${side}-collapsed`) === 'true');
  }
}

function renderLeftRail() {
  const openAnnotations = allAnnotations().filter((annotation) => annotation.status === 'open').length;
  const proposed = state.manifest.proposals.filter((proposal) => decisionFor(proposal) === 'proposed').length;
  const viewCounts = {
    dashboard: proposed,
    document: state.manifest.sections.length,
    projects: projectList().length,
    reconciliation: state.ideas.filter((idea) => ['pending', 'approved'].includes(idea.status)).length,
    changes: localChangeCount(),
    history: state.manifest.history.length + state.localHistory.length,
    changelog: state.manifest.releases.length,
    search: openAnnotations
  };
  const allTags = [...new Set(state.manifest.sections.flatMap((section) => section.tags))].sort();
  const statuses = [...new Set(state.manifest.sections.map((section) => section.status))].sort();
  const normalizedNavQuery = state.sectionNavQuery.trim().toLowerCase();
  const matching = matchingSections().filter((section) => {
    if (!normalizedNavQuery) return true;
    return `${section.index} ${section.title} ${section.dek} ${section.tags.join(' ')}`.toLowerCase().includes(normalizedNavQuery);
  });
  const pinnedIds = new Set(state.manifest.dashboard.pinnedSectionIds || []);
  const prioritySections = matching.filter((section) => pinnedIds.has(section.id));
  const boundedSections = state.sectionIndexExpanded || normalizedNavQuery
    ? matching
    : [...prioritySections, ...matching.filter((section) => !pinnedIds.has(section.id))].slice(0, 12);

  const globalBlockers = state.operations?.work?.blockers?.length;
  const globalDecisions = state.operations?.health?.unresolvedDecisions;
  const advancedOpen = localStorage.getItem('ldf:advanced-navigation-open') === 'true';
  const primaryViews = viewDefinitions.filter(([id]) => primaryViewIds.has(id));
  const advancedViews = viewDefinitions.filter(([id]) => !primaryViewIds.has(id));
  const renderView = ([id, icon, label]) => `<li><button class="view-link ${state.activeView === id ? 'active' : ''}" data-action="view" data-view="${id}" title="${id === 'dashboard' ? 'A concise project orientation and current focus.' : id === 'document' ? 'A continuous reader containing every canonical project page. The section index jumps within this reader.' : 'An optional project record or local tool.'}" ${state.activeView === id ? 'aria-current="page"' : ''}>${iconLabel(icon, label)}<span class="nav-count tag-static">${viewCounts[id]}</span></button></li>`;
  return `
    <aside class="left-rail" id="project-navigation" aria-label="Project navigation">
      <div class="rail-inner">
        <section class="rail-section">
          <p class="rail-label">Workspace attention</p>
          <nav aria-label="Workspace attention">
            <a class="view-link workspace-link" href="/#delegation" title="All preserved blockers and human decisions across every project">${iconLabel('!', 'All blockers and decisions')}<span class="nav-count tag-static">${globalBlockers ?? '…'}</span></a>
          </nav>
          <p class="nav-hint">${globalDecisions === undefined ? 'Loading workspace status.' : `${globalBlockers} blockers · ${globalDecisions} decisions`}</p>
        </section>

        <section class="rail-section">
          <p class="rail-label">This project</p>
          <nav aria-label="Core project views">
            <ul class="view-nav">
              ${primaryViews.map(renderView).join('')}
            </ul>
          </nav>
          <p class="nav-hint">Overview summarizes. Reader keeps every canonical page in one scroll.</p>
        </section>

        <section class="rail-section">
          <div class="section-heading">
            <h3>Project pages</h3>
            <span class="nav-count tag-static">${matching.length}</span>
          </div>
          <label class="rail-search">
            <span class="visually-hidden">Filter project pages</span>
            <span aria-hidden="true">⌕</span>
            <input id="section-nav-search" type="search" value="${escapeHtml(state.sectionNavQuery)}" placeholder="Filter ${state.manifest.sections.length} pages" autocomplete="off" />
          </label>
          <ol class="section-list">
            ${boundedSections.map((section) => `
              <li>
              <button class="section-link ${state.activeSectionId === section.id && ['section', 'document'].includes(state.activeView) ? 'active' : ''}" data-action="section" data-section="${section.id}" title="${escapeHtml(sectionExplanations[section.id] || 'Open this canonical project page.')}">
                  <span class="section-number">${escapeHtml(section.index)}</span>
                  <span class="section-name">${escapeHtml(section.title)}</span>
                  ${state.drafts[section.id] ? '<span class="draft-dot" title="Local draft"></span>' : statusDot(section.status)}
                </button>
              </li>`).join('') || '<li class="nav-hint">No project page matches.</li>'}
          </ol>
          ${!normalizedNavQuery && matching.length > 12 ? `<button class="index-disclosure" data-action="toggle-section-index" aria-expanded="${state.sectionIndexExpanded}">${state.sectionIndexExpanded ? 'Show priority pages' : `Browse all ${matching.length} pages`}<span aria-hidden="true">${state.sectionIndexExpanded ? '↑' : '↓'}</span></button>` : ''}
          <details class="rail-filters">
            <summary>Filter by status or tag</summary>
            <div class="filter-row" aria-label="Status filters">
              <button class="filter-button ${state.statusFilter === 'all' ? 'active' : ''}" data-action="status-filter" data-value="all">All status</button>
              ${statuses.map((status) => `<button class="filter-button ${state.statusFilter === status ? 'active' : ''}" data-action="status-filter" data-value="${escapeHtml(status)}">${escapeHtml(status)}</button>`).join('')}
            </div>
            <div class="filter-row" aria-label="Tag filters">
              <button class="filter-button ${state.tagFilter === 'all' ? 'active' : ''}" data-action="tag-filter" data-value="all">All tags</button>
              ${allTags.map((tag) => `<button class="filter-button ${state.tagFilter === tag ? 'active' : ''}" data-action="tag-filter" data-value="${escapeHtml(tag)}">${escapeHtml(tag)}</button>`).join('')}
            </div>
          </details>
        </section>

        <details class="rail-section advanced-nav" ${advancedOpen ? 'open' : ''}>
          <summary>Advanced records and local tools</summary>
          <p class="nav-hint">Optional audit, export, history, and local-only drafting tools. They never rewrite canonical Markdown by themselves. This open/closed preference stays in this browser.</p>
          <nav aria-label="Advanced project views"><ul class="view-nav">${advancedViews.map(renderView).join('')}</ul></nav>
          <dl class="meta-list">
            <div class="meta-row"><dt>Local drafts</dt><dd>${Object.keys(state.drafts).length}</dd></div>
            <div class="meta-row"><dt>Local decisions</dt><dd>${Object.keys(state.proposalDecisions).length}</dd></div>
            <div class="meta-row"><dt>Local notes</dt><dd>${state.localAnnotations.length}</dd></div>
          </dl>
        </details>
      </div>
    </aside>`;
}

function renderReviewDock() {
  const changes = localChangeCount();
  return `
    <footer class="review-dock" aria-label="Local review actions">
      <div class="review-state">
        <span class="review-pulse" aria-hidden="true"></span>
        <span><strong>Local notes</strong><small>${changes} unsent change${changes === 1 ? '' : 's'}</small></span>
      </div>
      <div class="review-actions">
        <button class="dock-primary" data-action="annotate-selection" data-scope="content" data-tooltip="Add a browser-local note to selected text or the active page."><span aria-hidden="true">✦</span><span>Annotate content</span></button>
        <button class="dock-primary" data-action="add-annotation" data-scope="layout" data-tooltip="Suggest a change to the shared reader layout or behavior."><span aria-hidden="true">⌗</span><span>Edit layout</span></button>
      </div>
    </footer>`;
}

function pageHeader(title, subtitle, eyebrow = '') {
  return `
    <header class="page-header">
      ${eyebrow ? `<p class="eyebrow">${escapeHtml(eyebrow)}</p>` : ''}
      <h1>${escapeHtml(title)}</h1>
      <p class="subtitle">${escapeHtml(subtitle)}</p>
      <div class="header-facts">
        <span>Updated ${formatDate(state.manifest.meta.updated)}</span>
        <span>${state.manifest.sections.length} sections</span>
        <span>${state.manifest.sections.reduce((total, section) => total + section.estimatedMinutes, 0)} min read</span>
        <span class="status-badge tag-static">${escapeHtml(state.manifest.meta.status)}</span>
      </div>
    </header>`;
}

function dashboardMetrics() {
  // [count, label, destination view]. A metric without a destination is inert
  // by intent, not by omission, and is rendered so it does not invite a click.
  return [
    [state.manifest.sections.length, 'Addressable sections', 'document'],
    [projectList().length, 'Related projects', null],
    [openBlockingItems().length, 'Cross-project blockers', 'dashboard'],
    [state.sources.filter((source) => source.readStatus === 'read_full').length, 'Sources read in full', null],
    [allAnnotations().filter((annotation) => annotation.status === 'open').length, 'Open annotations', 'changes'],
    [state.manifest.proposals.filter((proposal) => decisionFor(proposal) === 'proposed').length, 'Pending decisions', 'changes'],
    [modelReplies().filter((reply) => reply.status !== 'resolved').length, 'Model replies', 'changes'],
    [resourceList().length, 'Resources', null],
    [localChangeCount(), 'Local changes', 'changes']
  ];
}

function renderProjects() {
  const projects = projectList();
  const blockers = [...openBlockingItems()].sort((a, b) => {
    const rank = { critical: 0, high: 1, medium: 2, low: 3 };
    return (rank[a.priority] ?? 9) - (rank[b.priority] ?? 9);
  });
  return `
    <div class="view-frame">
      ${pageHeader('Project index', 'One navigable surface for every project family, relationship, date association, and unresolved cross-project question.', 'Federated workspace')}
      <div class="ledger-grid">
        <section class="ledger-panel">
          <div class="section-heading"><h2>Projects</h2><span class="nav-count tag-static">${projects.length}</span></div>
          <div class="record-list">${projects.map((project) => `
            <article class="record-item">
              <div class="record-heading"><strong>${escapeHtml(project.title)}</strong><span class="status-badge tag-static">${escapeHtml(project.status)}</span></div>
              <p>${escapeHtml(project.family)} · ${escapeHtml(project.dateAssociation || 'No date association')}</p>
              <div class="record-meta"><a class="tag tag-link" href="/projects/${escapeHtml(project.projectId)}/" title="Open the ${escapeHtml(project.projectId)} project folder">${escapeHtml(project.projectId)}</a><span class="tag tag-static">${escapeHtml(project.reconciliationStatus)}</span></div>
              ${project.entry ? `<a href="${escapeHtml(safeHref(project.entry))}">Open project document</a>` : ''}
            </article>`).join('') || '<div class="empty-state"><strong>No projects indexed</strong>Add a project index to the manifest federation record.</div>'}</div>
        </section>
        <section class="ledger-panel">
          <div class="section-heading"><h2>Blocking queue</h2><span class="nav-count tag-static">${blockers.length}</span></div>
          <div class="record-list">${blockers.map((item) => `
            <article class="record-item">
              <div class="record-heading"><strong>${escapeHtml(item.prompt)}</strong><span class="priority ${escapeHtml(item.priority)}">${escapeHtml(item.priority)}</span></div>
              <div class="record-meta"><a class="tag tag-link" href="/projects/${escapeHtml(item.projectId)}/" title="Open the ${escapeHtml(item.projectId)} project folder">${escapeHtml(item.projectId)}</a><span class="tag tag-static">${escapeHtml(item.status)}</span></div>
            </article>`).join('') || '<div class="empty-state"><strong>Queue clear</strong>No cross-project blocker awaits clarification.</div>'}</div>
        </section>
      </div>
    </div>`;
}

function renderReconciliation() {
  const unread = state.sources.filter((source) => !['read_full', 'duplicate_exempt', 'boilerplate_exempt'].includes(source.readStatus));
  const unresolved = state.ideas.filter((idea) => ['pending', 'approved'].includes(idea.status));
  return `
    <div class="view-frame">
      ${pageHeader('Source reconciliation', 'Every relevant source is read or explicitly exempted; every extracted idea receives a recorded disposition and rationale.', 'Evidence and adjudication')}
      <section class="metric-strip" aria-label="Reconciliation metrics">
        <div class="metric"><strong class="metric-value">${state.sources.length}</strong><span class="metric-label">Sources</span></div>
        <div class="metric"><strong class="metric-value">${unread.length}</strong><span class="metric-label">Unread or unknown</span></div>
        <div class="metric"><strong class="metric-value">${state.ideas.length}</strong><span class="metric-label">Extracted ideas</span></div>
        <div class="metric"><strong class="metric-value">${unresolved.length}</strong><span class="metric-label">Awaiting disposition</span></div>
      </section>
      <div class="ledger-grid">
        <section class="ledger-panel"><div class="section-heading"><h2>Source ledger</h2><span class="nav-count tag-static">${state.sources.length}</span></div><div class="record-list">
          ${state.sources.map((source) => `<article class="record-item"><div class="record-heading"><strong>${escapeHtml(source.originalPath)}</strong><span class="status-badge tag-static">${escapeHtml(source.readStatus)}</span></div><p>${escapeHtml(source.notes || source.kind)}</p><div class="record-meta"><span class="tag tag-static">${escapeHtml(source.id)}</span><span class="tag tag-static">${escapeHtml(source.relevance)}</span><span class="tag tag-static">${escapeHtml(source.timestamps?.confidence || 'unknown')} date confidence</span></div></article>`).join('') || '<div class="empty-state"><strong>No source records</strong>Discovery has not started.</div>'}
        </div></section>
        <section class="ledger-panel"><div class="section-heading"><h2>Idea ledger</h2><span class="nav-count tag-static">${state.ideas.length}</span></div><div class="record-list">
          ${state.ideas.map((idea) => `<article class="record-item"><div class="record-heading"><strong>${escapeHtml(idea.summary)}</strong><span class="status-badge tag-static">${escapeHtml(idea.status)}</span></div><p>${escapeHtml(idea.rationale || 'Rationale required before closure.')}</p><div class="record-meta"><span class="tag tag-static">${escapeHtml(idea.id)}</span><span class="tag tag-static">${escapeHtml(idea.type)}</span>${(idea.affectedProjectIds || []).map((id) => `<span class="tag tag-static">${escapeHtml(id)}</span>`).join('')}</div></article>`).join('') || '<div class="empty-state"><strong>No ideas extracted</strong>Read relevant sources before reconciliation.</div>'}
        </div></section>
      </div>
    </div>`;
}

function renderDashboard() {
  const pinned = state.manifest.dashboard.pinnedSectionIds.map(effectiveSection).filter(Boolean);
  const recent = [...state.localHistory, ...state.manifest.history]
    .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
    .slice(0, 5);
  const pending = state.manifest.proposals
    .filter((proposal) => decisionFor(proposal) === 'proposed')
    .slice(0, state.manifest.dashboard.decisionQueueLimit);
  const replies = modelReplies().filter((reply) => reply.status !== 'resolved').slice(0, 4);

  return `
    <div class="view-frame">
      ${pageHeader(state.manifest.meta.title, state.manifest.meta.subtitle, 'Project overview')}
      <section class="focus-band" aria-labelledby="current-focus">
        <div>
          <p class="eyebrow">Current focus</p>
          <h2 id="current-focus">${escapeHtml(state.manifest.dashboard.focus)}</h2>
        </div>
        <button class="primary-button" data-action="view" data-view="document" title="Read every canonical project page as one continuous document">Read all project pages</button>
      </section>
      <section class="metric-strip" aria-label="Document metrics">
        ${dashboardMetrics().map(([value, label, view]) => (view && value > 0)
          ? `<button class="metric metric-link" data-action="view" data-view="${view}" title="Go to ${escapeHtml(label.toLowerCase())}"><strong class="metric-value">${value}</strong><span class="metric-label">${escapeHtml(label)}</span></button>`
          : `<div class="metric metric-inert"><strong class="metric-value">${value}</strong><span class="metric-label">${escapeHtml(label)}</span></div>`).join('')}
      </section>
      <div class="dashboard-grid">
        <div class="dashboard-section">
          <div class="section-heading"><h2>Priority sections</h2><span class="eyebrow">Pinned</span></div>
          <div class="pinned-list">
            ${pinned.map((section) => `
              <article class="pinned-item">
                <span class="pinned-index">${escapeHtml(section.index)}</span>
                <button data-action="section" data-section="${section.id}">
                  <div class="pinned-title">${escapeHtml(section.title)}</div>
                  <div class="pinned-dek">${escapeHtml(section.dek)}</div>
                </button>
                ${statusDot(section.status)}
              </article>`).join('')}
          </div>

          <div class="section-heading" style="margin-top:2.4rem"><h2>Recent activity</h2><button class="ghost-button" data-action="view" data-view="history">Full history</button></div>
          <div class="timeline">
            ${recent.map(renderTimelineItem).join('') || '<div class="empty-state"><strong>No activity yet</strong>History appears after the first revision.</div>'}
          </div>
        </div>

        <div class="dashboard-section">
          <div class="section-heading"><h2>Document health</h2><span class="eyebrow">Live checks</span></div>
          <div class="health-list">
            ${state.manifest.dashboard.health.map((item) => `
              <div class="health-item">
                <span class="health-dot ${escapeHtml(item.state)}"></span>
                <div><div class="health-label">${escapeHtml(item.label)}</div><div class="health-detail">${escapeHtml(item.detail)}</div></div>
              </div>`).join('')}
          </div>

          <div class="section-heading" style="margin-top:2.4rem"><h2>Decision queue</h2><span class="nav-count tag-static">${pending.length}</span></div>
          <div class="proposal-list">
            ${pending.map(renderProposal).join('') || '<div class="empty-state"><strong>Queue clear</strong>No proposals await a decision.</div>'}
          </div>

          <div class="section-heading" style="margin-top:2.4rem"><h2>Model replies</h2><span class="nav-count tag-static">${replies.length}</span></div>
          <div class="proposal-list">
            ${replies.map(renderModelReply).join('') || '<div class="empty-state"><strong>No pending replies</strong>Model questions and answer options appear here.</div>'}
          </div>
        </div>
      </div>
    </div>`;
}

function renderProposal(proposal) {
  const decision = decisionFor(proposal);
  return `
    <article class="proposal-item">
      <div class="proposal-title">${escapeHtml(proposal.title)}</div>
      <p class="proposal-summary">${escapeHtml(proposal.summary)}</p>
      ${proposal.recommendation ? `<p class="proposal-recommendation"><strong>Recommended:</strong> ${escapeHtml(proposal.recommendation)}</p>` : ''}
      ${proposal.alternative ? `<details class="proposal-details"><summary>Alternative and context</summary><p><strong>Alternative:</strong> ${escapeHtml(proposal.alternative)}</p>${proposal.details ? `<p>${escapeHtml(proposal.details)}</p>` : ''}</details>` : ''}
      <div class="proposal-meta">
        <span class="tag tag-static">${escapeHtml(proposal.id)}</span>
        <span class="tag tag-static">impact ${escapeHtml(proposal.impact)}</span>
        <span class="tag tag-static">effort ${escapeHtml(proposal.effort)}</span>
      </div>
      <fieldset class="decision-row" aria-label="Decision for ${escapeHtml(proposal.title)}">
        <legend>Decision</legend>
        ${['approve', 'defer', 'reject'].map((value) => `<label class="segment-button ${decision === value ? 'active' : ''}"><input type="radio" name="decision-${escapeHtml(proposal.id)}" data-action="proposal-decision" data-proposal="${proposal.id}" data-value="${value}" ${decision === value ? 'checked' : ''}> ${value}</label>`).join('')}
      </fieldset>
    </article>`;
}

function renderModelReply(reply) {
  return `
    <article class="proposal-item">
      <div class="proposal-title">${escapeHtml(reply.prompt)}</div>
      <p class="proposal-summary">${escapeHtml(reply.context || '')}</p>
      <div class="proposal-meta">
        <span class="tag tag-static">${escapeHtml(reply.id)}</span>
        <span class="tag tag-static">${escapeHtml(reply.status || 'open')}</span>
        ${(reply.targetIds || []).map((id) => `<span class="tag tag-static">${escapeHtml(id)}</span>`).join('')}
      </div>
      ${(reply.options || []).length ? `<ol class="option-list">${reply.options.map((option) => `<li><strong>${escapeHtml(option.label)}</strong> ${escapeHtml(option.text)}</li>`).join('')}</ol>` : ''}
      <p class="health-detail">Human can annotate, answer in a section draft, or export a change request with a custom response.</p>
    </article>`;
}

function renderSectionArticle(section) {
  return `
    <section class="document-section" id="${section.id}" data-section-observe="${section.id}" aria-labelledby="${section.id}-title">
      <div class="section-kicker"><span>${escapeHtml(section.index)}</span><span>${escapeHtml(section.eyebrow)}</span>${statusDot(section.status)}</div>
      <h2 id="${section.id}-title">${escapeHtml(section.title)}</h2>
      <p class="section-dek">${escapeHtml(section.dek)}</p>
      ${section.id === 'decisions' ? '<aside class="reader-mode-note"><strong>About this page:</strong> it records canonical project decisions, rejected directions, and unresolved policy. It is not the same as the workspace-wide blocker and decision queue, available from <a href="/#delegation">All blockers and decisions</a>.</aside>' : ''}
      ${state.drafts[section.id] ? `<div class="local-draft-banner"><span>Local draft overlays the canonical section.</span><button class="ghost-button" data-action="discard-draft" data-section="${section.id}">Discard</button></div>` : ''}
      <div class="section-toolbar section-tags">${tagMarkup(section.tags)}</div>
      ${renderQuestionForm(section)}
    </section>`;
}

function renderFocusedSection() {
  const section = currentSection();
  if (!section) return renderDashboard();
  return `
    <div class="view-frame document-view focused-section-view">
      <div class="document-intro">
        ${pageHeader(state.manifest.meta.title, section.title, 'Focused project page')}
        <p class="reader-mode-note"><strong>Focused page:</strong> only this canonical page is shown. Use the section index for another page or <button class="text-button" data-action="view" data-view="document">read all ${state.manifest.sections.length} pages</button>.</p>
      </div>
      ${renderSectionArticle(section)}
    </div>`;
}

function renderDocument() {
  const sections = matchingSections();
  return `
    <div class="view-frame document-view">
      <div class="document-intro">
        ${pageHeader(state.manifest.meta.title, state.manifest.meta.subtitle, 'Continuous project reader')}
        <p class="thesis">${escapeHtml(state.manifest.meta.thesis)}</p>
        <p class="reader-mode-note"><strong>How to use this view:</strong> every canonical project page appears below in one scrollable reader. The section index jumps to a page; it does not open a competing document.</p>
        ${state.tagFilter !== 'all' ? `<p class="reader-mode-note"><strong>Tag filter active:</strong> showing the ${escapeHtml(state.tagFilter)} pages in this project. Choose <em>All</em> in the left rail to restore every page.</p>` : ''}
        <button class="focus-toggle" data-action="toggle-focused" title="Temporarily hide navigation rails for uninterrupted reading">${state.focused ? 'Exit focused reading' : 'Focused reading'} <kbd>F</kbd></button>
      </div>
      ${sections.map(renderSectionArticle).join('')}
      ${state.tagFilter === 'all' ? renderChangesPanel() : ''}
    </div>`;
}

function renderChangeAnnotation(annotation) {
  const scope = annotation.scope || 'content';
  return `
    <article class="annotation-item">
      <div class="annotation-title">${escapeHtml(scope)} · ${escapeHtml(annotation.kind)} · ${escapeHtml(annotation.status)}</div>
      ${annotation.quote ? `<blockquote class="annotation-quote">${escapeHtml(annotation.quote)}</blockquote>` : ''}
      <p class="annotation-text">${escapeHtml(annotation.text)}</p>
      <div class="annotation-meta">
        <span class="tag tag-static">${escapeHtml(annotation.targetId)}</span>
        <span class="tag tag-static">${escapeHtml(annotation.author)}</span>
        <span class="tag tag-static">${formatDate(annotation.createdAt)}</span>
      </div>
    </article>`;
}

function renderChangesPanel({ standalone = false } = {}) {
  const annotations = allAnnotations();
  const drafts = Object.entries(state.drafts);
  const decisions = Object.entries(state.proposalDecisions);
  const localChanges = localChangeCount();
  const submitted = submittedChangeReceipt();
  const sendLabel = submitted
    ? `Sent ${submitted.changeCount} change${submitted.changeCount === 1 ? '' : 's'} to agent`
    : localChanges
      ? `Send ${localChanges} change${localChanges === 1 ? '' : 's'} to agent`
      : 'Nothing to send yet';
  return `
    <section class="document-section" id="changes" aria-labelledby="changes-title">
      ${standalone ? '' : '<div class="section-kicker"><span>CH</span><span>Agent handoff</span></div>'}
      <h2 id="changes-title" class="${standalone ? 'visually-hidden' : ''}">${standalone ? 'Submission contents' : 'Changes'}</h2>
      <p class="section-dek">${standalone
        ? 'These changes are still saved in this browser. Send them once to create a private loopback receipt for the agent; download and copy are optional backups.'
        : 'Content notes, layout notes, local drafts, and proposal decisions collected without rewriting canonical Markdown.'}</p>
      <div class="section-toolbar">
        <button class="primary-button" data-action="submit-change" ${localChanges && !submitted ? '' : 'disabled'}>${sendLabel}</button>
        <button class="ghost-button" data-action="copy-change">Copy backup</button>
        <button class="ghost-button" data-action="export-change">Download backup</button>
      </div>
      <div class="ledger-grid">
        <section class="ledger-panel">
          <div class="section-heading"><h3>Annotations</h3><span class="nav-count tag-static">${annotations.length}</span></div>
          <div class="annotation-list">${annotations.map(renderChangeAnnotation).join('') || '<p class="health-detail">No annotations yet.</p>'}</div>
        </section>
        <section class="ledger-panel">
          <div class="section-heading"><h3>Local edits</h3><span class="nav-count tag-static">${drafts.length + decisions.length}</span></div>
          <div class="record-list">
            ${drafts.map(([sectionId]) => `<article class="record-item"><strong>Draft: ${escapeHtml(sectionId)}</strong><p>Canonical Markdown is unchanged.</p></article>`).join('')}
            ${decisions.map(([proposalId, decision]) => `<article class="record-item"><strong>${escapeHtml(proposalId)}</strong><p>Decision: ${escapeHtml(decision)}</p></article>`).join('')}
            ${drafts.length + decisions.length ? '' : '<p class="health-detail">No drafts or proposal decisions yet.</p>'}
          </div>
        </section>
      </div>
    </section>`;
}

function renderChanges() {
  return `
    <div class="view-frame">
      ${pageHeader('Review and send changes', 'Inspect the browser-local changes below, then send one private receipt to the agent.', 'Agent handoff')}
      ${renderChangesPanel({ standalone: true })}
    </div>`;
}

function renderTimelineItem(event) {
  return `
    <article class="timeline-item">
      <span class="timeline-dot" aria-hidden="true"></span>
      <time class="timeline-time" datetime="${escapeHtml(event.timestamp)}">${formatDateTime(event.timestamp)}</time>
      <div class="timeline-content">
        <div class="timeline-title">${escapeHtml(event.summary)}</div>
        <div class="timeline-details">${escapeHtml(event.actor)} · ${escapeHtml(event.kind)} · ${escapeHtml(event.source)}</div>
        ${event.details ? `<div class="timeline-details">${escapeHtml(event.details)}</div>` : ''}
      </div>
    </article>`;
}

function renderHistory() {
  const events = [...state.localHistory, ...state.manifest.history]
    .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
    .filter((event) => state.historyFilter === 'all' || event.kind === state.historyFilter);
  return `
    <div class="view-frame">
      ${pageHeader('History', 'The append-only event ledger: edits, decisions, imports, migrations, exports, and agent runs.', 'Audit trail')}
      <div class="timeline">${events.map(renderTimelineItem).join('')}</div>
    </div>`;
}

function renderChangelog() {
  return `
    <div class="view-frame">
      ${pageHeader('Changelog', 'Reader-facing release narratives explain what changed and why each version matters.', 'Release notes')}
      <div class="releases">
        ${state.manifest.releases.map((release) => `
          <article class="release">
            <div><div class="release-version">v${escapeHtml(release.version)}</div><div class="release-date">${formatDate(release.date)}</div></div>
            <div>
              <h2>${escapeHtml(release.title)}</h2>
              <p class="subtitle">${escapeHtml(release.summary)}</p>
              <div class="change-list">
                ${release.changes.map((change) => `<div class="change-row"><span class="change-type">${escapeHtml(change.type)}</span><span>${escapeHtml(change.text)}</span></div>`).join('')}
              </div>
            </div>
          </article>`).join('')}
      </div>
    </div>`;
}

function searchSections(query) {
  const normalized = query.trim().toLowerCase();
  return state.manifest.navigation.sectionOrder
    .map(effectiveSection)
    .filter(Boolean)
    .map((section) => {
      const haystacks = [
        ['title', section.title],
        ['dek', section.dek],
        ['tags', section.tags.join(' ')],
        ['body', stripFrontmatter(section.markdown)]
      ];
      let score = 0;
      let source = '';
      for (const [kind, text] of haystacks) {
        const value = text.toLowerCase();
        if (!normalized || value.includes(normalized)) {
          score += kind === 'title' ? 10 : kind === 'tags' ? 7 : kind === 'dek' ? 5 : 2;
          if (!source && normalized) {
            const index = value.indexOf(normalized);
            source = text.slice(Math.max(0, index - 70), Math.min(text.length, index + normalized.length + 130));
          }
        }
      }
      return { section, score, source: source || section.dek };
    })
    .filter((result) => !normalized || result.score > 0)
    .sort((a, b) => b.score - a.score);
}

function renderSearch() {
  const results = searchSections(state.searchQuery);
  return `
    <div class="view-frame">
      ${pageHeader('Search', 'Search section titles, summaries, tags, and Markdown without changing canonical content.', 'Document index')}
      <p class="search-summary">${state.searchQuery ? `${results.length} results for “${escapeHtml(state.searchQuery)}”` : `${results.length} indexed sections. Type in the search field above.`}</p>
      <ol class="search-results">
        ${results.map(({ section, source }) => `
          <li class="search-result">
            <button data-action="section" data-section="${section.id}">
              <div class="section-kicker"><span>${escapeHtml(section.index)}</span><span>${escapeHtml(section.eyebrow)}</span></div>
              <div class="search-result-title">${escapeHtml(section.title)}</div>
              <div class="search-snippet">${escapeHtml(source.replace(/\s+/g, ' ').trim())}</div>
              <div class="proposal-meta">${tagMarkup(section.tags)}</div>
            </button>
          </li>`).join('') || '<div class="empty-state"><strong>No matches</strong>Try a broader term or browse the section index.</div>'}
      </ol>
    </div>`;
}

function renderMain() {
  const content = {
    dashboard: renderDashboard,
    section: renderFocusedSection,
    document: renderDocument,
    projects: renderProjects,
    reconciliation: renderReconciliation,
    changes: renderChanges,
    history: renderHistory,
    changelog: renderChangelog,
    search: renderSearch
  }[state.activeView]?.() || renderDashboard();
  return `<main class="main" id="main-content" tabindex="-1">${content}</main>`;
}

function renderSectionInspector(section) {
  const annotations = allAnnotations().filter((annotation) => annotation.targetId === section.id);
  const dependencies = section.dependencies.map(sectionById).filter(Boolean);
  const backlinks = section.backlinks.map(sectionById).filter(Boolean);
  const resources = resourcesForSection(section.id);
  return `
    <div class="inspector-header"><h2>Section inspector</h2></div>
    <section class="rail-section">
      <dl class="meta-list">
        <div class="meta-row"><dt>ID</dt><dd>${escapeHtml(section.id)}</dd></div>
        <div class="meta-row"><dt>Status</dt><dd>${escapeHtml(section.status)}${state.drafts[section.id] ? ' · local draft' : ''}</dd></div>
        <div class="meta-row"><dt>Updated</dt><dd>${formatDate(section.updated)}</dd></div>
        <div class="meta-row"><dt>Reading</dt><dd>${section.estimatedMinutes} minutes</dd></div>
        <div class="meta-row"><dt>Owner</dt><dd>${escapeHtml(section.owner || 'Unassigned')}</dd></div>
      </dl>
      <p class="health-detail">Use the persistent review dock for content notes, Markdown drafts, and layout revisions.</p>
    </section>
    <section class="rail-section">
      <p class="rail-label">Tags</p><div class="tag-row">${tagMarkup(section.tags)}</div>
    </section>
    <section class="rail-section">
      <p class="rail-label">Dependencies</p>
      ${dependencies.map((item) => `<button class="view-link" data-action="section" data-section="${item.id}">${iconLabel('←', item.title)}</button>`).join('') || '<p class="health-detail">No declared dependencies.</p>'}
    </section>
    <section class="rail-section">
      <p class="rail-label">Backlinks</p>
      ${backlinks.map((item) => `<button class="view-link" data-action="section" data-section="${item.id}">${iconLabel('↗', item.title)}</button>`).join('') || '<p class="health-detail">No declared backlinks.</p>'}
    </section>
    <section class="rail-section">
      <div class="section-heading"><h3>Resources</h3><span class="nav-count tag-static">${resources.length}</span></div>
      <div class="annotation-list">
        ${resources.map(renderResource).join('') || '<p class="health-detail">No resources target this section.</p>'}
      </div>
    </section>
    <section class="rail-section">
      <div class="section-heading"><h3>Annotations</h3><span class="nav-count tag-static">${annotations.length}</span></div>
      <div class="annotation-list">
        ${annotations.map((annotation) => `
          <article class="annotation-item">
            <div class="annotation-title">${escapeHtml(annotation.scope || 'content')} · ${escapeHtml(annotation.kind)} · ${escapeHtml(annotation.status)}</div>
            ${annotation.quote ? `<blockquote class="annotation-quote">${escapeHtml(annotation.quote)}</blockquote>` : ''}
            <p class="annotation-text">${escapeHtml(annotation.text)}</p>
            <div class="annotation-meta"><span class="tag tag-static">${escapeHtml(annotation.author)}</span><span class="tag tag-static">${formatDate(annotation.createdAt)}</span></div>
          </article>`).join('') || '<p class="health-detail">No annotations target this section.</p>'}
      </div>
    </section>`;
}

function renderDashboardInspector() {
  const proposed = state.manifest.proposals.filter((proposal) => decisionFor(proposal) === 'proposed');
  return `
    <div class="inspector-header"><h2>Settings</h2><p class="health-detail">Reader preferences and local tools. Nothing here edits canonical Markdown.</p></div>
    <section class="rail-section settings-block" id="reader-settings">
      <p class="rail-label">Appearance</p>
      <p class="settings-note">Every reader preference lives here. Stored in this browser only.</p>
      <div class="field"><label for="inspector-theme">Theme</label><select class="select-control" id="inspector-theme">${Object.entries(themeNames).map(([id, label]) => `<option value="${id}" ${state.theme === id ? 'selected' : ''}>${label}</option>`).join('')}</select></div>
      <div class="field"><label for="inspector-motion">Motion</label><select class="select-control" id="inspector-motion">${Object.entries(motionNames).map(([id, label]) => `<option value="${id}" ${state.motion === id ? 'selected' : ''}>${label}</option>`).join('')}</select></div>
      <div class="field"><label for="density-select">Density</label><select class="select-control" id="density-select"><option value="comfortable" ${state.density === 'comfortable' ? 'selected' : ''}>Comfortable</option><option value="compact" ${state.density === 'compact' ? 'selected' : ''}>Compact</option></select></div>
    </section>
    <section class="rail-section">
      <p class="rail-label">Tools</p>
      <p class="settings-note">Actions that produce a file or a handoff.</p>
      <button class="view-link" data-action="export-change" title="Download local drafts, annotations, and selections for an agent to review">${iconLabel('⇧', 'Download change request')}</button>
      <button class="view-link" data-action="copy-change" title="Copy a structured local change request to the clipboard">${iconLabel('⧉', 'Copy change request')}</button>
      <button class="view-link" data-action="export-json" title="Download a local merged preview; canonical Markdown is unchanged">${iconLabel('{}', 'Download local JSON preview')}</button>
      <button class="view-link" data-action="export-md" title="Download a read-only combined Markdown copy">${iconLabel('¶', 'Download combined Markdown')}</button>
    </section>
    <section class="rail-section">
      <p class="rail-label">Local proposal review</p>
      <p class="health-detail">${proposed.length} proposals remain unresolved.</p>
      <button class="primary-button" data-action="view" data-view="dashboard" title="Review project-local proposals. Workspace-wide human decisions are under All blockers and decisions.">Review local proposals</button>
    </section>
    <section class="rail-section">
      <p class="rail-label">Shortcuts</p>
      <button class="view-link" data-action="shortcuts">${iconLabel('?', 'Keyboard map')}</button>
      <button class="view-link" data-action="reader-guide">${iconLabel('i', 'How this reader works')}</button>
      <button class="view-link" data-action="command">${iconLabel('⌘', 'Command palette')}</button>
    </section>`;
}

function renderHistoryInspector() {
  const kinds = [...new Set([...state.manifest.history, ...state.localHistory].map((event) => event.kind))].sort();
  return `
    <div class="inspector-header"><h2>History filters</h2></div>
    <section class="rail-section">
      <div class="filter-row">
        <button class="filter-button ${state.historyFilter === 'all' ? 'active' : ''}" data-action="history-filter" data-value="all">All</button>
        ${kinds.map((kind) => `<button class="filter-button ${state.historyFilter === kind ? 'active' : ''}" data-action="history-filter" data-value="${escapeHtml(kind)}">${escapeHtml(kind)}</button>`).join('')}
      </div>
    </section>
    <section class="rail-section">
      <p class="rail-label">Distinction</p>
      <p class="health-detail">History records every event. Changelog explains released meaning. Worklogs record immutable agent actions.</p>
    </section>`;
}

function renderRightRail() {
  let content = renderDashboardInspector();
  if (['section', 'document'].includes(state.activeView)) content = renderSectionInspector(currentSection());
  if (state.activeView === 'history') content = renderHistoryInspector();
  if (state.activeView === 'changelog') content = `${renderDashboardInspector()}<section class="rail-section"><p class="rail-label">Releases</p>${state.manifest.releases.map((release) => `<a class="view-link" href="#release-${escapeHtml(release.version)}">${iconLabel('v', release.version)}</a>`).join('')}</section>`;
  if (state.activeView === 'search') content = `${renderDashboardInspector()}<section class="rail-section"><p class="rail-label">Search tips</p><p class="health-detail">Title matches rank above tags, summaries, and body text. Press <kbd>/</kbd> from anywhere outside a form.</p></section>`;
  return `<aside class="right-rail" id="context-inspector" aria-label="Context inspector"><div class="rail-inner">${content}</div></aside>`;
}

function renderDialogs() {
  return `
    <dialog class="dialog" id="quick-edit-dialog" aria-labelledby="quick-edit-title">
      <form id="quick-edit-form" method="dialog"></form>
    </dialog>
    <dialog class="dialog command-dialog" id="command-dialog" aria-labelledby="command-title">
      <h2 id="command-title" class="visually-hidden">Command palette</h2>
      <input class="command-search" id="command-search" autocomplete="off" placeholder="Type a command or section title" aria-label="Filter commands" />
      <ul class="command-list" id="command-list"></ul>
    </dialog>
    <dialog class="dialog" id="annotation-dialog" aria-labelledby="annotation-title">
      <form id="annotation-form" method="dialog">
        <div class="dialog-header"><div><p class="eyebrow" id="annotation-eyebrow"></p><h2 id="annotation-title">Add a content note</h2><p class="health-detail" id="annotation-help"></p></div><button class="icon-button" type="button" data-action="close-dialog" data-dialog="annotation-dialog" aria-label="Close">×</button></div>
        <div class="dialog-body form-grid">
          <input type="hidden" name="targetId" id="annotation-target" />
          <input type="hidden" name="quote" id="annotation-quote" />
          <input type="hidden" name="scope" id="annotation-scope" />
          <div class="field full annotation-target-summary"><span>Target</span><strong id="annotation-target-label"></strong></div>
          <div class="field"><label for="annotation-kind">Kind</label><select id="annotation-kind" name="kind"><option>note</option><option>question</option><option>objection</option><option>decision</option><option>evidence</option></select></div>
          <div class="field"><label for="annotation-author">Author</label><input id="annotation-author" name="author" value="Local editor" required /></div>
          <div class="field full" id="annotation-quote-field" hidden><label for="annotation-quote-preview">Selected quote</label><textarea id="annotation-quote-preview" readonly></textarea></div>
          <div class="field full"><label for="annotation-text" id="annotation-text-label">Your note</label><textarea id="annotation-text" name="text" required></textarea></div>
        </div>
        <div class="dialog-footer"><button class="ghost-button annotation-markdown-action" type="button" data-action="annotation-markdown-draft">Draft a local Markdown change</button><div><button class="ghost-button" type="button" data-action="close-dialog" data-dialog="annotation-dialog">Cancel</button><button class="primary-button" id="annotation-submit" type="submit">Save content note</button></div></div>
      </form>
    </dialog>
    <dialog class="dialog" id="shortcuts-dialog" aria-labelledby="shortcuts-title">
      <div class="dialog-header"><h2 id="shortcuts-title">Keyboard map</h2><button class="icon-button" data-action="close-dialog" data-dialog="shortcuts-dialog" aria-label="Close">×</button></div>
      <div class="dialog-body">
        <dl class="meta-list">
          <div class="meta-row"><dt><kbd>⌘/Ctrl K</kbd></dt><dd>Command palette</dd></div>
          <div class="meta-row"><dt><kbd>/</kbd></dt><dd>Focus search</dd></div>
          <div class="meta-row"><dt><kbd>E</kbd></dt><dd>Edit active section</dd></div>
          <div class="meta-row"><dt><kbd>F</kbd></dt><dd>Toggle focused reading</dd></div>
          <div class="meta-row"><dt><kbd>⌘/Ctrl Z</kbd></dt><dd>Undo local change</dd></div>
          <div class="meta-row"><dt><kbd>⌘/Ctrl ⇧ Z</kbd></dt><dd>Redo local change</dd></div>
          <div class="meta-row"><dt><kbd>?</kbd></dt><dd>Show this map</dd></div>
          <div class="meta-row"><dt><kbd>Esc</kbd></dt><dd>Close dialog or drawer</dd></div>
        </dl>
      </div>
    </dialog>
    <dialog class="dialog" id="reader-guide-dialog" aria-labelledby="reader-guide-title">
      <div class="dialog-header"><div><p class="eyebrow">Reader guide</p><h2 id="reader-guide-title">How this reader works</h2></div><button class="icon-button" type="button" data-action="close-dialog" data-dialog="reader-guide-dialog" aria-label="Close">×</button></div>
      <div class="dialog-body reader-guide">
        <p><strong>Start at Portfolio home</strong> for every project, the current workspace picture, all blockers, decisions, activity, and exports. A dossier is one project’s canonical context.</p>
        <dl class="meta-list">
          <div class="meta-row"><dt>Project overview</dt><dd>A short orientation: current focus, priority pages, local health, and recent project activity.</dd></div>
          <div class="meta-row"><dt>Read all pages</dt><dd>One continuous reader for every canonical project page. The page index jumps within it; it does not open a separate competing document.</dd></div>
          <div class="meta-row"><dt>Section index and tags</dt><dd>Section index jumps to a canonical page. Tags filter the continuous reader to matching canonical pages in this project only.</dd></div>
          <div class="meta-row"><dt>All blockers and decisions</dt><dd>The workspace-wide human attention queue. It is separate from a project’s own Decisions page, which records project policy and prior choices.</dd></div>
          <div class="meta-row"><dt>Advanced records and local tools</dt><dd>Optional source audit, history, release notes, search, exports, and browser-local change tools. They begin collapsed so they do not compete with core reading.</dd></div>
          <div class="meta-row"><dt>Draft local change</dt><dd>A browser-only overlay. It never edits canonical Markdown until you export it and an agent deliberately applies and validates it.</dd></div>
          <div class="meta-row"><dt>Content and layout notes</dt><dd>Local comments on canonical prose or reader presentation. Export them for an agent; they are not silent edits.</dd></div>
          <div class="meta-row"><dt>Decision selection</dt><dd>A local review direction and optional instruction. It reaches the loopback review inbox for an agent to inspect, but does not execute work or grant authority by itself.</dd></div>
          <div class="meta-row"><dt>Canonical state</dt><dd>The Markdown corpus and evidence-gated work ledger. Browser preferences, drafts, reviews, and exports are derived or local until recorded canonically.</dd></div>
        </dl>
      </div>
    </dialog>
    <div class="authored-tooltip" id="authored-tooltip" role="tooltip" hidden></div>
    <div class="toast-region" id="toast-region" aria-live="polite" aria-atomic="true"></div>`;
}

function render() {
  if (state.observer) state.observer.disconnect();
  document.documentElement.dataset.theme = state.theme;
  document.documentElement.dataset.motion = state.motion;
  document.documentElement.dataset.density = state.density;
  // Operational views (changes, history) inherited the document-reading type
  // scale, which is built for a long single column and makes an H2 nearly the
  // size of the page title. Marking the active view lets those surfaces carry a
  // scale suited to scanning and acting rather than reading.
  document.documentElement.dataset.view = state.activeView;
  document.body.classList.toggle('focused', state.focused);
  app.innerHTML = `
    <div class="app-shell">
      ${renderTopbar()}
      ${renderLeftRail()}
      ${renderMain()}
      ${renderRightRail()}
      <div class="reading-progress" aria-hidden="true"><span id="progress-bar"></span></div>
      <button class="scrim" data-action="close-drawers" aria-label="Close navigation drawers"></button>
      ${renderReviewDock()}
    </div>
    ${renderDialogs()}`;
  document.querySelector('.advanced-nav')?.addEventListener('toggle', (event) => {
    localStorage.setItem('ldf:advanced-navigation-open', String(event.currentTarget.open));
  });
  document.title = `${state.manifest.meta.title} · Living Document`;
  syncBodyClasses();
  if (state.activeView === 'document') setupSectionObserver();
  updateReadingProgress();
}

function syncBodyClasses() {
  document.body.classList.toggle('focused', state.focused);
}

function setView(view) {
  state.activeView = view;
  if (view === 'section' && state.activeSectionId) {
    replaceLocationHash(state.activeSectionId);
  } else if (view !== 'dashboard') {
    replaceLocationView(view);
  } else {
    replaceLocationHash('');
  }
  document.body.classList.remove('left-open', 'right-open');
  render();
  requestAnimationFrame(() => document.querySelector('#main-content')?.focus({ preventScroll: true }));
}

function replaceLocationView(view) {
  const next = `${window.location.pathname}${window.location.search}#view=${encodeURIComponent(view)}`;
  history.replaceState(null, '', next);
}

function sectionIdFromLocation() {
  return sectionIdFromHash(window.location.hash, state.manifest?.sections.map((section) => section.id) || []);
}

function replaceLocationHash(id) {
  const next = id
    ? `${window.location.pathname}${window.location.search}#${encodeURIComponent(id)}`
    : `${window.location.pathname}${window.location.search}`;
  history.replaceState(null, '', next);
}

function scrollToSection(id, behavior = 'smooth') {
  const section = document.getElementById(id);
  if (!section) return;
  if (behavior === 'auto') {
    const priorScrollBehavior = document.documentElement.style.scrollBehavior;
    document.documentElement.style.scrollBehavior = 'auto';
    const placeSection = () => section.scrollIntoView({ behavior: 'auto', block: 'start' });
    placeSection();
    requestAnimationFrame(() => {
      placeSection();
      requestAnimationFrame(placeSection);
    });
    setTimeout(() => {
      placeSection();
      document.documentElement.style.scrollBehavior = priorScrollBehavior;
    }, 150);
    return;
  }
  section.scrollIntoView({ behavior: motionReduced() ? 'auto' : 'smooth', block: 'start' });
}

function goToSection(id) {
  if (!sectionById(id)) return;
  state.activeView = 'section';
  state.activeSectionId = id;
  replaceLocationHash(id);
  document.body.classList.remove('left-open', 'right-open');
  render();
  requestAnimationFrame(() => scrollToSection(id));
}

function motionReduced() {
  return state.motion === 'reduced' || matchMedia('(prefers-reduced-motion: reduce)').matches;
}

function applyTheme(theme) {
  state.theme = theme;
  document.documentElement.dataset.theme = theme;
  localStorage.setItem('ldf:theme', theme);
  if (darkThemes.has(theme)) localStorage.setItem('ldf:last-dark-theme', theme);
  document.querySelectorAll('#theme-select, #inspector-theme').forEach((select) => { select.value = theme; });
}

function toggleQuickTheme() {
  const readingPosition = window.scrollY;
  const next = resolveQuickTheme({
    theme: state.theme,
    prefersDark: matchMedia('(prefers-color-scheme: dark)').matches,
    lastDark: localStorage.getItem('ldf:last-dark-theme') || 'obsidian'
  });
  applyTheme(next);
  render();
  requestAnimationFrame(() => {
    const restorePosition = () => window.scrollTo({ top: readingPosition, behavior: 'auto' });
    restorePosition();
    requestAnimationFrame(restorePosition);
    setTimeout(restorePosition, 120);
    document.querySelector('[data-action="quick-theme"]')?.focus({ preventScroll: true });
  });
  toast(`${themeNames[next]} theme selected`);
}

function applyMotion(motion) {
  state.motion = motion;
  document.documentElement.dataset.motion = motion;
  localStorage.setItem('ldf:motion', motion);
  document.querySelectorAll('#motion-select, #inspector-motion').forEach((select) => { select.value = motion; });
  toast(`${motionNames[motion]} selected`);
}

function applyDensity(density) {
  state.density = density;
  document.documentElement.dataset.density = density;
  localStorage.setItem('ldf:density', density);
  toast(`${density === 'compact' ? 'Compact' : 'Comfortable'} density selected`);
}

function setupSectionObserver() {
  const sections = [...document.querySelectorAll('[data-section-observe]')];
  if (!sections.length) return;
  state.observer = new IntersectionObserver((entries) => {
    const visible = entries.filter((entry) => entry.isIntersecting).sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)[0];
    if (!visible) return;
    state.activeSectionId = visible.target.dataset.sectionObserve;
    document.querySelectorAll('.section-link').forEach((link) => link.classList.toggle('active', link.dataset.section === state.activeSectionId));
    const section = currentSection();
    const inspector = document.querySelector('.right-rail .rail-inner');
    if (inspector && section && !inspector.contains(document.activeElement)) inspector.innerHTML = renderSectionInspector(section);
  }, { rootMargin: '-20% 0px -68% 0px', threshold: [0, 0.1, 0.5] });
  sections.forEach((section) => state.observer.observe(section));
}

function updateReadingProgress() {
  const max = document.documentElement.scrollHeight - window.innerHeight;
  const progress = max <= 0 ? 0 : Math.min(100, Math.max(0, (window.scrollY / max) * 100));
  document.documentElement.style.setProperty('--reading-progress', progress.toFixed(2));
}

function quickEditMarkup(section) {
  return `
    <div class="dialog-header">
      <div><p class="eyebrow">Local overlay · ${escapeHtml(section.id)}</p><h2 id="quick-edit-title">Draft a local change</h2><p class="health-detail">This stays in this browser until exported. It does not edit canonical Markdown.</p></div>
      <button class="icon-button" type="button" data-action="close-dialog" data-dialog="quick-edit-dialog" aria-label="Close">×</button>
    </div>
    <div class="dialog-body form-grid">
      <input type="hidden" name="sectionId" value="${escapeHtml(section.id)}" />
      <div class="field full"><label for="edit-title">Title</label><input id="edit-title" name="title" value="${escapeHtml(section.title)}" required /></div>
      <div class="field full"><label for="edit-dek">Deck</label><input id="edit-dek" name="dek" value="${escapeHtml(section.dek)}" required /></div>
      <div class="field"><label for="edit-status">Status</label><select id="edit-status" name="status">${['draft', 'active', 'review', 'stable', 'deprecated', 'archived'].map((status) => `<option ${section.status === status ? 'selected' : ''}>${status}</option>`).join('')}</select></div>
      <div class="field"><label for="edit-tags">Tags</label><input id="edit-tags" name="tags" value="${escapeHtml(section.tags.join(', '))}" /></div>
      <div class="field full"><label for="edit-markdown">Markdown</label><textarea id="edit-markdown" name="markdown" spellcheck="true">${escapeHtml(stripFrontmatter(section.markdown))}</textarea></div>
    </div>
    <div class="dialog-footer">
      <button class="ghost-button" type="button" data-action="discard-draft" data-section="${section.id}" ${state.drafts[section.id] ? '' : 'disabled'}>Discard local draft</button>
      <div><button class="ghost-button" type="button" data-action="close-dialog" data-dialog="quick-edit-dialog">Cancel</button><button class="primary-button" type="submit">Save local draft</button></div>
    </div>`;
}

function openQuickEdit(id = state.activeSectionId) {
  const section = effectiveSection(id || state.manifest.navigation.sectionOrder[0]);
  if (!section || !section.editable) return toast('This section is not editable');
  if (!dialogReturnAction) dialogReturnAction = 'quick-edit';
  state.activeSectionId = section.id;
  const form = document.querySelector('#quick-edit-form');
  form.innerHTML = quickEditMarkup(section);
  document.querySelector('#quick-edit-dialog').showModal();
  requestAnimationFrame(() => document.querySelector('#edit-title')?.focus());
}

function saveQuickEdit(form) {
  const data = new FormData(form);
  const id = data.get('sectionId');
  const section = effectiveSection(id);
  if (!section) return;
  pushUndo(`edit ${section.title}`);
  state.drafts[id] = {
    title: String(data.get('title')).trim(),
    dek: String(data.get('dek')).trim(),
    status: String(data.get('status')),
    tags: String(data.get('tags')).split(',').map((tag) => tag.trim()).filter(Boolean),
    markdown: String(data.get('markdown')).trim(),
    updated: new Date().toISOString().slice(0, 10),
    updatedAt: new Date().toISOString()
  };
  state.localHistory.unshift({
    id: `LOCAL-${Date.now()}`,
    timestamp: new Date().toISOString(),
    actor: 'Local editor',
    kind: 'edit',
    summary: `Saved a local draft for “${state.drafts[id].title}”`,
    targetIds: [id],
    version: state.manifest.meta.version,
    source: 'local',
    details: 'The canonical Markdown file is unchanged until this draft is exported and applied.'
  });
  persistLocalState();
  document.querySelector('#quick-edit-dialog').close();
  render();
  restoreDialogFocus();
  toast('Local draft saved');
}

function discardDraft(id) {
  if (!state.drafts[id]) return;
  pushUndo(`discard draft ${id}`);
  delete state.drafts[id];
  state.localHistory.unshift({
    id: `LOCAL-${Date.now()}`,
    timestamp: new Date().toISOString(),
    actor: 'Local editor',
    kind: 'edit',
    summary: `Discarded the local draft for ${id}`,
    targetIds: [id],
    version: state.manifest.meta.version,
    source: 'local'
  });
  persistLocalState();
  document.querySelector('#quick-edit-dialog')?.close();
  render();
  restoreDialogFocus();
  toast('Local draft discarded');
}

function saveProposalDecision(id, decision) {
  const proposal = state.manifest.proposals.find((item) => item.id === id);
  if (!proposal) return;
  pushUndo(`decide ${id}`);
  state.proposalDecisions[id] = decision;
  state.localHistory.unshift({
    id: `LOCAL-${Date.now()}`,
    timestamp: new Date().toISOString(),
    actor: 'Local editor',
    kind: 'decision',
    summary: `${decision[0].toUpperCase() + decision.slice(1)}d proposal ${id}`,
    targetIds: [id, ...proposal.targetIds],
    version: state.manifest.meta.version,
    source: 'local'
  });
  persistLocalState();
  render();
  toast(`Proposal ${id}: ${decision}`);
}

function openAnnotationDialog(id = state.activeSectionId, quote = '', scope = 'content') {
  const target = id || state.activeSectionId || state.manifest.navigation.sectionOrder[0] || 'document';
  const section = effectiveSection(target);
  const config = annotationDialogConfig(scope, {
    targetTitle: scope === 'layout' ? state.manifest.meta.title : (section?.title || state.manifest.meta.title),
    quote
  });
  dialogReturnAction = config.scope === 'layout' ? 'add-annotation' : 'annotate-selection';
  document.querySelector('#annotation-target').value = target;
  document.querySelector('#annotation-quote').value = config.quote;
  document.querySelector('#annotation-quote-preview').value = config.quote;
  document.querySelector('#annotation-quote-field').hidden = !config.showQuote;
  document.querySelector('#annotation-scope').value = config.scope;
  document.querySelector('#annotation-eyebrow').textContent = config.eyebrow;
  document.querySelector('#annotation-title').textContent = config.title;
  document.querySelector('#annotation-help').textContent = config.help;
  document.querySelector('#annotation-target-label').textContent = config.target;
  document.querySelector('#annotation-text-label').textContent = config.fieldLabel;
  document.querySelector('#annotation-submit').textContent = config.submitLabel;
  document.querySelector('.annotation-markdown-action').hidden = !config.showMarkdownDraft;
  document.querySelector('#annotation-text').value = '';
  document.querySelector('#annotation-dialog').showModal();
  requestAnimationFrame(() => document.querySelector('#annotation-text')?.focus());
}

function openSelectionAnnotationDialog(scope = 'content') {
  const quote = selectedQuote();
  openAnnotationDialog(quote.sectionId || state.activeSectionId, quote.text, scope);
}

function restoreDialogFocus() {
  const action = dialogReturnAction;
  dialogReturnAction = null;
  if (!action) return;
  requestAnimationFrame(() => document.querySelector(`[data-action="${action}"]`)?.focus({ preventScroll: true }));
}

function closeDialog(id, { restore = true } = {}) {
  document.getElementById(id)?.close();
  if (restore) restoreDialogFocus();
}

function openAnnotationMarkdownDraft() {
  closeDialog('annotation-dialog', { restore: false });
  openQuickEdit(state.activeSectionId);
}

function saveAnnotation(form) {
  const data = new FormData(form);
  const targetId = String(data.get('targetId'));
  const quote = String(data.get('quote') || '').trim();
  pushUndo(`annotate ${targetId}`);
  state.localAnnotations.push({
    id: `A-LOCAL-${Date.now()}`,
    targetId,
    quote,
    scope: String(data.get('scope') || 'content'),
    kind: String(data.get('kind')),
    text: String(data.get('text')).trim(),
    tags: ['local'],
    status: 'open',
    author: String(data.get('author')).trim(),
    createdAt: new Date().toISOString()
  });
  state.localHistory.unshift({
    id: `LOCAL-${Date.now() + 1}`,
    timestamp: new Date().toISOString(),
    actor: String(data.get('author')).trim(),
    kind: 'edit',
    summary: `Added a ${String(data.get('scope') || 'content')} annotation to ${targetId}`,
    targetIds: [targetId],
    version: state.manifest.meta.version,
    source: 'local'
  });
  persistLocalState();
  document.querySelector('#annotation-dialog').close();
  render();
  restoreDialogFocus();
  toast(`${String(data.get('scope')) === 'layout' ? 'Layout' : 'Content'} note added`);
}

function commands(query = '') {
  const base = [
    { group: 'Navigate', label: 'Open dashboard', hint: 'G D', run: () => setView('dashboard') },
    { group: 'Navigate', label: 'Open document', hint: 'G R', run: () => setView('document') },
    { group: 'Navigate', label: 'Open projects', hint: 'G P', run: () => setView('projects') },
    { group: 'Navigate', label: 'Open reconciliation', hint: 'G A', run: () => setView('reconciliation') },
    { group: 'Navigate', label: 'Open changes', hint: 'G X', run: () => setView('changes') },
    { group: 'Navigate', label: 'Open history', hint: 'G H', run: () => setView('history') },
    { group: 'Navigate', label: 'Open changelog', hint: 'G C', run: () => setView('changelog') },
    { group: 'Edit', label: 'Quick edit active section', hint: 'E', run: () => openQuickEdit() },
    { group: 'Edit', label: 'Annotate selected content', hint: '', run: () => openSelectionAnnotationDialog('content') },
    { group: 'Edit', label: 'Annotate current layout', hint: '', run: () => openAnnotationDialog(state.activeSectionId, '', 'layout') },
    { group: 'Edit', label: 'Undo local change', hint: '⌘ Z', run: undo },
    { group: 'Edit', label: 'Redo local change', hint: '⌘ ⇧ Z', run: redo },
    { group: 'View', label: state.focused ? 'Exit focused reading' : 'Enter focused reading', hint: 'F', run: toggleFocused },
    { group: 'Export', label: 'Export change request', hint: '', run: exportChangeRequest },
    { group: 'Export', label: 'Copy changes for agent', hint: '', run: copyChangeRequest },
    { group: 'Export', label: 'Export combined Markdown', hint: '', run: exportMarkdown },
    ...Object.entries(themeNames).map(([id, label]) => ({ group: 'Theme', label: `Theme: ${label}`, hint: '', run: () => { applyTheme(id); toast(`${label} theme selected`); } })),
    ...state.manifest.navigation.sectionOrder.map((id) => {
      const section = effectiveSection(id);
      return { group: 'Sections', label: `${section.index} · ${section.title}`, hint: section.status, run: () => goToSection(id) };
    })
  ];
  const normalized = query.trim().toLowerCase();
  return normalized ? base.filter((command) => `${command.group} ${command.label} ${command.hint}`.toLowerCase().includes(normalized)) : base;
}

function renderCommandList(query = '') {
  const list = document.querySelector('#command-list');
  if (!list) return;
  const items = commands(query);
  state.commandIndex = Math.min(state.commandIndex, Math.max(0, items.length - 1));
  let group = '';
  list.innerHTML = items.map((command, index) => {
    const heading = command.group !== group ? `<li class="command-group">${escapeHtml(command.group)}</li>` : '';
    group = command.group;
    return `${heading}<li class="command-item"><button data-action="command-run" data-index="${index}" class="${index === state.commandIndex ? 'selected' : ''}"><span>${escapeHtml(command.label)}</span>${command.hint ? `<kbd>${escapeHtml(command.hint)}</kbd>` : ''}</button></li>`;
  }).join('') || '<li class="empty-state"><strong>No command found</strong>Try a section title or action.</li>';
  list.dataset.query = query;
}

function openCommandPalette() {
  const dialog = document.querySelector('#command-dialog');
  const input = document.querySelector('#command-search');
  state.commandIndex = 0;
  input.value = '';
  renderCommandList('');
  dialog.showModal();
  requestAnimationFrame(() => input.focus());
}

function runCommand(index) {
  const query = document.querySelector('#command-search')?.value || '';
  const command = commands(query)[index];
  if (!command) return;
  document.querySelector('#command-dialog').close();
  command.run();
}

function toggleFocused() {
  state.focused = !state.focused;
  localStorage.setItem('ldf:focused', String(state.focused));
  render();
  toast(state.focused ? 'Focused reading enabled' : 'Living Documents restored');
}

function download(name, body, type) {
  const blob = new Blob([body], { type });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = name;
  document.body.append(anchor);
  anchor.click();
  anchor.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

function changeRequestPayload() {
  return {
    requestId: `CR-${Date.now()}`,
    document: {
      documentId: state.manifest.meta.documentId,
      version: state.manifest.meta.version,
      formatVersion: state.manifest.meta.compatibility.formatVersion
    },
    createdAt: new Date().toISOString(),
    scope: [...new Set([...Object.keys(state.drafts), ...state.manifest.proposals.filter((proposal) => state.proposalDecisions[proposal.id]).flatMap((proposal) => proposal.targetIds), ...state.localAnnotations.map((annotation) => annotation.targetId)])],
    drafts: Object.entries(state.drafts).map(([sectionId, draft]) => ({ sectionId, ...draft })),
    proposalDecisions: Object.entries(state.proposalDecisions).map(([proposalId, decision]) => ({ proposalId, decision })),
    annotations: state.localAnnotations,
    constraints: ['Preserve stable IDs', 'Do not rewrite unrelated sections', 'Append history and worklog entries', `Validate format ${state.manifest.meta.compatibility.formatVersion}`],
    expectedOutputs: ['Updated source files', 'Validation report', 'Appended history event', 'Appended worklog entry']
  };
}

function exportChangeRequest() {
  const payload = changeRequestPayload();
  download(`${state.manifest.meta.documentId}-change-request.json`, `${JSON.stringify(payload, null, 2)}\n`, 'application/json');
  toast('Change request exported');
}

async function submitChangeRequest(button) {
  if (localChangeCount() < 1) return toast('Add a note, draft, or decision before sending');
  button.disabled = true;
  button.textContent = 'Sending…';
  try {
    const response = await fetch('/api/change-requests', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(changeRequestPayload()),
    });
    if (!response.ok) throw new Error(`change request: ${response.status}`);
    const payload = await response.json();
    localStorage.setItem(storageKey('last-change-receipt'), JSON.stringify({
      receiptId: payload.receipt.receiptId,
      submittedAt: payload.receipt.submittedAt,
      changeCount: payload.receipt.changeCount,
      snapshot: snapshot(),
    }));
    button.textContent = `Sent ${payload.receipt.changeCount} change${payload.receipt.changeCount === 1 ? '' : 's'} to agent`;
    toast(`Sent ${payload.receipt.changeCount} change${payload.receipt.changeCount === 1 ? '' : 's'}; no download needed`);
  } catch (error) {
    console.error(error);
    button.disabled = false;
    button.textContent = `Send ${localChangeCount()} change${localChangeCount() === 1 ? '' : 's'} to agent`;
    toast('Send failed; your browser changes are preserved');
  }
}

async function copyChangeRequest() {
  const body = `${JSON.stringify(changeRequestPayload(), null, 2)}\n`;
  try {
    await navigator.clipboard.writeText(body);
  } catch {
    const text = document.createElement('textarea');
    text.value = body;
    text.setAttribute('readonly', '');
    text.style.position = 'fixed';
    text.style.opacity = '0';
    document.body.append(text);
    text.select();
    const copied = document.execCommand('copy');
    text.remove();
    if (!copied) {
      toast('Clipboard unavailable; download the change request instead');
      return;
    }
  }
  toast('Page changes copied for an agent');
}

function exportJson() {
  const merged = structuredClone(state.manifest);
  merged.sections = merged.sections.map((section) => {
    const effective = effectiveSection(section.id);
    return { ...section, ...state.drafts[section.id], markdown: effective.markdown };
  });
  merged.proposals = merged.proposals.map((proposal) => ({ ...proposal, decision: decisionFor(proposal) }));
  merged.annotations = allAnnotations();
  merged.sourceLedger = { sources: state.sources };
  merged.ideaLedger = { ideas: state.ideas };
  merged.projectIndex = { projects: state.projects, blockingItems: state.blockingItems };
  merged.history = [...state.localHistory, ...merged.history];
  merged._export = { generatedAt: new Date().toISOString(), localOverlayApplied: true };
  download(`${state.manifest.meta.documentId}-merged.json`, `${JSON.stringify(merged, null, 2)}\n`, 'application/json');
  toast('Merged JSON exported');
}

function exportMarkdown() {
  const header = `# ${state.manifest.meta.title}\n\n${state.manifest.meta.subtitle}\n\n> ${state.manifest.meta.thesis}\n`;
  const sections = state.manifest.navigation.sectionOrder.map((id) => {
    const section = effectiveSection(id);
    return `\n---\n\n## ${section.title}\n\n_${section.dek}_\n\n${stripFrontmatter(section.markdown)}\n`;
  }).join('');
  download(`${state.manifest.meta.documentId}.md`, `${header}${sections}`, 'text/markdown');
  toast('Combined Markdown exported');
}

function toast(message) {
  const region = document.querySelector('#toast-region');
  if (!region) return;
  region.innerHTML = `<div class="toast">${escapeHtml(message)}</div>`;
  clearTimeout(state.toastTimer);
  state.toastTimer = setTimeout(() => { if (region) region.innerHTML = ''; }, 2800);
}

function closeDrawers(restoreFocus = true) {
  document.body.classList.remove('left-open', 'right-open');
  for (const side of ['left', 'right']) {
    const rail = document.querySelector(`.${side}-rail`);
    rail?.removeAttribute('role');
    rail?.removeAttribute('aria-modal');
    const desktopVisible = !matchMedia(side === 'left' ? '(max-width: 840px)' : '(max-width: 1180px)').matches
      && !document.body.classList.contains(`${side}-collapsed`);
    document.querySelector(`[data-action="toggle-${side}"]`)?.setAttribute('aria-expanded', String(desktopVisible));
  }
  if (restoreFocus && drawerReturnFocus?.isConnected) drawerReturnFocus.focus();
  drawerReturnFocus = null;
}

function isTypingTarget(target) {
  return target instanceof HTMLInputElement || target instanceof HTMLTextAreaElement || target instanceof HTMLSelectElement || target?.isContentEditable;
}

function hideTooltip() {
  clearTimeout(tooltipTimer);
  const tooltip = document.querySelector('#authored-tooltip');
  document.querySelectorAll('[aria-describedby="authored-tooltip"]').forEach((control) => control.removeAttribute('aria-describedby'));
  if (tooltip) tooltip.hidden = true;
}

function showTooltip(control, immediate = false) {
  if (!control?.dataset.tooltip) return;
  hideTooltip();
  const reveal = () => {
    const tooltip = document.querySelector('#authored-tooltip');
    if (!tooltip || !control.isConnected) return;
    tooltip.textContent = control.dataset.tooltip;
    tooltip.hidden = false;
    control.setAttribute('aria-describedby', 'authored-tooltip');
    const controlRect = control.getBoundingClientRect();
    const tooltipRect = tooltip.getBoundingClientRect();
    const left = Math.min(window.innerWidth - tooltipRect.width - 12, Math.max(12, controlRect.left + controlRect.width / 2 - tooltipRect.width / 2));
    const top = Math.max(12, controlRect.top - tooltipRect.height - 10);
    tooltip.style.left = `${left}px`;
    tooltip.style.top = `${top}px`;
  };
  if (immediate || motionReduced()) reveal();
  else tooltipTimer = setTimeout(reveal, 450);
}

app.addEventListener('click', (event) => {
  const control = event.target.closest('[data-action]');
  if (!control) return;
  const action = control.dataset.action;
  if (action === 'view') setView(control.dataset.view);
  if (action === 'section') goToSection(control.dataset.section);
  if (action === 'status-filter') { state.statusFilter = control.dataset.value; render(); }
  if (action === 'tag-filter') { state.tagFilter = control.dataset.value; state.activeView = 'document'; render(); }
  if (action === 'toggle-section-index') { state.sectionIndexExpanded = !state.sectionIndexExpanded; render(); }
  if (action === 'history-filter') { state.historyFilter = control.dataset.value; render(); }
  if (action === 'toggle-left') {
    if (matchMedia('(max-width: 840px)').matches) toggleDrawer('left', control);
    else toggleSidebar('left');
  }
  if (action === 'toggle-right') {
    if (matchMedia('(max-width: 1180px)').matches) toggleDrawer('right', control);
    else toggleSidebar('right');
  }
  if (action === 'close-drawers') closeDrawers();
  if (action === 'toggle-focused') toggleFocused();
  if (action === 'open-settings') {
    // Reuse the rail's own open path rather than poking state directly; the rail
    // is a drawer below 1180px and a sidebar above it, and only these helpers
    // know which. Setting a state flag skipped both and opened nothing.
    if (matchMedia('(max-width: 1180px)').matches) {
      if (!document.body.classList.contains('right-open')) toggleDrawer('right', control);
    } else if (document.body.classList.contains('right-collapsed')) {
      toggleSidebar('right');
    }
    requestAnimationFrame(() => {
      const block = document.getElementById('reader-settings');
      if (!block) return;
      block.scrollIntoView({ block: 'start', behavior: state.motion === 'reduced' ? 'auto' : 'smooth' });
      block.classList.add('settings-flash');
      setTimeout(() => block.classList.remove('settings-flash'), 900);
      document.getElementById('inspector-theme')?.focus({ preventScroll: true });
    });
    return;
  }
  if (action === 'quick-theme') toggleQuickTheme();
  if (action === 'quick-edit') openQuickEdit(control.dataset.section);
  if (action === 'annotation-markdown-draft') openAnnotationMarkdownDraft();
  if (action === 'discard-draft') discardDraft(control.dataset.section);
  if (action === 'proposal-decision') saveProposalDecision(control.dataset.proposal, control.dataset.value);
  if (action === 'add-annotation') openAnnotationDialog(control.dataset.section, '', control.dataset.scope || 'content');
  if (action === 'annotate-selection') openSelectionAnnotationDialog(control.dataset.scope || 'content');
  if (action === 'close-dialog') closeDialog(control.dataset.dialog);
  if (action === 'command') openCommandPalette();
  if (action === 'command-run') runCommand(Number(control.dataset.index));
  if (action === 'shortcuts') document.querySelector('#shortcuts-dialog').showModal();
  if (action === 'reader-guide') document.querySelector('#reader-guide-dialog').showModal();
  if (action === 'undo') undo();
  if (action === 'redo') redo();
  if (action === 'submit-change') void submitChangeRequest(control);
  if (action === 'export-change') exportChangeRequest();
  if (action === 'copy-change') copyChangeRequest();
  if (action === 'export-json') exportJson();
  if (action === 'export-md') exportMarkdown();
  if (action === 'portfolio-view' && portfolioSnapshot) {
    portfolioView = control.dataset.portfolioView;
    localStorage.setItem('ldf:portfolio-view', portfolioView);
    history.replaceState(null, '', portfolioView === 'overview' ? '/' : `/#${portfolioView}`);
    document.activeViewTransition?.skipTransition();
    renderPortfolioShell(portfolioSnapshot);
    requestAnimationFrame(() => document.querySelector('#main-content')?.focus({ preventScroll: true }));
  }
  if (action === 'portfolio-decision') {
    savePortfolioReview(control.dataset.priority, { optionId: control.dataset.option });
    setTimeout(() => { if (window.location.pathname === '/') void initPortfolio(); }, 300);
  }
  if (action === 'retry-portfolio-decision') void publishPortfolioReview(control.dataset.priority);
  if (action === 'clear-portfolio-decision') void clearPortfolioReview(control.dataset.priority);
  if (action === 'export-portfolio-reviews') exportPortfolioReviews();
});

app.addEventListener('pointerover', (event) => {
  const control = event.target.closest('[data-tooltip]');
  if (control) showTooltip(control);
});

app.addEventListener('pointerout', (event) => {
  const control = event.target.closest('[data-tooltip]');
  if (control && !control.contains(event.relatedTarget)) hideTooltip();
});

app.addEventListener('focusin', (event) => {
  const control = event.target.closest('[data-tooltip]');
  if (control) showTooltip(control, true);
});

app.addEventListener('focusout', (event) => {
  if (event.target.closest('[data-tooltip]')) hideTooltip();
});

app.addEventListener('submit', (event) => {
  event.preventDefault();
  if (event.target.id === 'quick-edit-form') saveQuickEdit(event.target);
  if (event.target.id === 'annotation-form') saveAnnotation(event.target);
  if (event.target.dataset.questionResponseForm) void submitQuestionResponses(event.target);
});

app.addEventListener('input', (event) => {
  if (event.target.id === 'global-search') state.searchQuery = event.target.value;
  if (event.target.id === 'section-nav-search') {
    state.sectionNavQuery = event.target.value;
    const cursor = event.target.selectionStart;
    render();
    requestAnimationFrame(() => {
      const input = document.querySelector('#section-nav-search');
      input?.focus();
      input?.setSelectionRange(cursor, cursor);
    });
  }
  if (event.target.dataset.portfolioNote) savePortfolioReview(event.target.dataset.portfolioNote, { note: event.target.value });
  if (event.target.dataset.questionWriteIn) {
    saveQuestionResponseDraft(event.target.dataset.section, event.target.dataset.questionWriteIn, { writeIn: event.target.value });
    if (event.target.value.trim()) {
      const radio = event.target.closest('[data-question-card]')?.querySelector('input[value="write-in"]');
      if (radio && !radio.checked) {
        radio.checked = true;
        saveQuestionResponseDraft(event.target.dataset.section, event.target.dataset.questionWriteIn, { optionId: 'write-in' });
      }
    }
  }
  if (event.target.id === 'command-search') {
    state.commandIndex = 0;
    renderCommandList(event.target.value);
  }
});

app.addEventListener('change', (event) => {
  if (event.target.dataset.action === 'question-option') {
    saveQuestionResponseDraft(event.target.dataset.section, event.target.dataset.question, { optionId: event.target.value });
    event.target.closest('[data-question-card]')?.querySelectorAll('.portfolio-choice').forEach((choice) => {
      choice.classList.toggle('active', choice.contains(event.target));
    });
  }
});

async function submitQuestionResponses(form) {
  const sectionId = form.dataset.questionResponseForm;
  const parsed = parseQuestionSection(state.sectionContent.get(sectionId) || '');
  if (!parsed || !form.reportValidity()) return;
  const responses = questionResponseStorage()[sectionId] || {};
  const answers = parsed.questions.map((question) => ({
    questionId: question.id,
    optionId: responses[question.id]?.optionId || '',
    writeIn: responses[question.id]?.writeIn || '',
  }));
  if (answers.some((answer) => !answer.optionId || (answer.optionId === 'write-in' && !answer.writeIn.trim()))) {
    toast('Answer every question before submitting');
    return;
  }
  const button = form.querySelector('button[type="submit"]');
  button.disabled = true;
  button.textContent = 'Submitting…';
  try {
    const response = await fetch('/api/question-responses', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ projectId: state.manifest.meta.documentId, sectionId, answers }),
    });
    if (!response.ok) throw new Error(`question response: ${response.status}`);
    const payload = await response.json();
    button.textContent = 'Submitted for agent review';
    form.dataset.receiptId = payload.receipt.receiptId;
    toast('Answers saved; agent attention queued');
  } catch (error) {
    console.error(error);
    button.disabled = false;
    button.textContent = 'Submit answers for agent review';
    toast('Submission failed; your browser draft is preserved');
  }
}

app.addEventListener('change', (event) => {
  if (['theme-select', 'inspector-theme'].includes(event.target.id)) applyTheme(event.target.value);
  if (['motion-select', 'inspector-motion'].includes(event.target.id)) applyMotion(event.target.value);
  if (event.target.id === 'density-select') applyDensity(event.target.value);
});

app.addEventListener('keydown', (event) => {
  if (event.target.id === 'global-search' && event.key === 'Enter') {
    state.searchQuery = event.target.value;
    setView('search');
  }
  if (event.target.id === 'command-search') {
    const items = commands(event.target.value);
    if (event.key === 'ArrowDown') {
      event.preventDefault();
      state.commandIndex = Math.min(items.length - 1, state.commandIndex + 1);
      renderCommandList(event.target.value);
    }
    if (event.key === 'ArrowUp') {
      event.preventDefault();
      state.commandIndex = Math.max(0, state.commandIndex - 1);
      renderCommandList(event.target.value);
    }
    if (event.key === 'Enter') {
      event.preventDefault();
      runCommand(state.commandIndex);
    }
  }
});

window.addEventListener('keydown', (event) => {
  const openRail = document.body.classList.contains('left-open')
    ? document.querySelector('.left-rail')
    : document.body.classList.contains('right-open')
      ? document.querySelector('.right-rail')
      : null;
  if (event.key === 'Tab' && openRail) {
    const focusable = [...openRail.querySelectorAll('a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), summary, [tabindex]:not([tabindex="-1"])')]
      .filter((item) => !item.hidden && item.getClientRects().length);
    if (focusable.length) {
      const first = focusable[0];
      const last = focusable.at(-1);
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
      if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
    }
  }
  const typing = isTypingTarget(event.target);
  if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') {
    event.preventDefault();
    openCommandPalette();
    return;
  }
  if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'z' && !typing) {
    event.preventDefault();
    event.shiftKey ? redo() : undo();
    return;
  }
  if (event.key === 'Escape') {
    hideTooltip();
    closeDrawers();
    document.querySelectorAll('dialog[open]').forEach((dialog) => closeDialog(dialog.id));
    return;
  }
  if (typing) return;
  if (event.key === '/') {
    event.preventDefault();
    document.querySelector('#global-search')?.focus();
  }
  if (event.key.toLowerCase() === 'e') openQuickEdit();
  if (event.key.toLowerCase() === 'f') toggleFocused();
  if (event.key === '?') document.querySelector('#shortcuts-dialog')?.showModal();
});

let scrollTicking = false;
window.addEventListener('scroll', () => {
  if (scrollTicking) return;
  scrollTicking = true;
  requestAnimationFrame(() => {
    updateReadingProgress();
    scrollTicking = false;
  });
}, { passive: true });

window.addEventListener('hashchange', () => {
  if (window.location.pathname === '/') return;
  const route = projectRouteFromHash(
    window.location.hash,
    state.manifest?.sections.map((section) => section.id) || [],
    state.manifest?.navigation.defaultView || 'dashboard',
    projectViewIds,
  );
  if (route.sectionId) goToSection(route.sectionId);
  else if (route.view !== state.activeView) setView(route.view);
});

async function init() {
  if (window.location.pathname === '/') {
    await initPortfolio();
    return;
  }
  try {
    const [manifest, annotationsFile, operations] = await Promise.all([
      fetchJson('content/index.json'),
      fetchJson('data/annotations.json'),
      fetchJson('/api/operations').catch(() => null)
    ]);
    state.manifest = manifest;
    state.annotations = annotationsFile.annotations || [];
    state.operations = operations;
    if (manifest.reconciliation?.sourceLedger) {
      const ledger = await fetchJson(manifest.reconciliation.sourceLedger);
      state.sources = ledger.sources || [];
    }
    if (manifest.reconciliation?.ideaLedger) {
      const ledger = await fetchJson(manifest.reconciliation.ideaLedger);
      state.ideas = ledger.ideas || [];
    }
    if (manifest.federation?.projectIndex) {
      const index = await fetchJson(manifest.federation.projectIndex);
      state.projects = index.projects || [];
      state.blockingItems = index.blockingItems || [];
    }
    const route = projectRouteFromHash(
      window.location.hash,
      manifest.sections.map((section) => section.id),
      manifest.navigation.defaultView || 'dashboard',
      projectViewIds,
    );
    const linkedSectionId = route.sectionId;
    state.activeView = route.view;
    state.activeSectionId = linkedSectionId || manifest.navigation.sectionOrder[0];
    if (!manifest.visual.themes.includes(state.theme)) state.theme = manifest.visual.defaultTheme;
    if (!['system', 'full', 'reduced'].includes(state.motion)) state.motion = manifest.visual.defaultMotion;
    loadLocalState();
    restoreSidebarPreferences();
    await Promise.all(manifest.sections.map(async (section) => {
      state.sectionContent.set(section.id, await fetchText(section.source));
    }));
    render();
    if (linkedSectionId) {
      requestAnimationFrame(() => scrollToSection(linkedSectionId, 'auto'));
    }
  } catch (error) {
    console.error(error);
    app.innerHTML = `<div class="boot-screen"><div class="boot-mark">!</div><h1>Document failed to open</h1><p>${escapeHtml(error.message)}</p><p>Serve the project with <code>npm run dev</code>; browsers block local file fetches.</p></div>`;
  }
}

function portfolioCard(project) {
  return `<a class="portfolio-card" href="${escapeHtml(project.href)}">
    <div class="record-heading"><strong>${escapeHtml(project.title)}</strong><span class="status-badge tag-static">${escapeHtml(project.status)}</span></div>
    <p>${escapeHtml(project.subtitle || 'Open the dossier for its canonical current state.')}</p>
    <div class="record-meta"><span class="tag tag-static">${escapeHtml(project.lifecycle)}</span><span class="tag tag-static">${project.sectionCount} pages</span><span class="tag tag-static">projection ${escapeHtml(project.projection?.state || 'unknown')}</span><span class="tag tag-static">updated ${escapeHtml(project.updated || 'unknown')}</span></div>
  </a>`;
}

function operationWorkCard(work) {
  return `<article class="operation-work-card"><div class="record-heading"><strong>${escapeHtml(work.project)}</strong><span class="status-badge tag-static">blocked</span></div><p>${escapeHtml(work.blocker)}</p><p class="operation-next"><strong>Next:</strong> ${escapeHtml(work.nextAction)}</p><a href="${escapeHtml(work.href)}">Open dossier</a></article>`;
}

const portfolioReviewStorageKey = 'ldf:portfolio-decision-review';
const portfolioReviewTimers = new Map();

function portfolioReviewState() {
  try {
    const value = JSON.parse(localStorage.getItem(portfolioReviewStorageKey) || '{}');
    return value && typeof value === 'object' ? value : {};
  } catch {
    return {};
  }
}

function savePortfolioReview(priority, update) {
  const review = portfolioReviewState();
  review[String(priority)] = { ...(review[String(priority)] || {}), ...update, updatedAt: new Date().toISOString() };
  localStorage.setItem(portfolioReviewStorageKey, JSON.stringify(review));
  clearTimeout(portfolioReviewTimers.get(String(priority)));
  portfolioReviewTimers.set(String(priority), setTimeout(() => { void publishPortfolioReview(priority); }, 250));
}

async function publishPortfolioReview(priority) {
  const key = String(priority);
  const review = portfolioReviewState()[key];
  if (!review?.optionId) return;

  // Delivery outcome is recorded and shown. It used to be swallowed by a
  // console.warn: when the review inbox was unreachable the answer stayed in
  // this browser only, while the card gave every appearance of having sent it.
  // A submission surface that cannot report its own failure is worse than one
  // with no submit at all, because the user stops waiting for an answer that
  // was never delivered.
  const record = (delivery, error) => {
    const state = portfolioReviewState();
    state[key] = { ...(state[key] || {}), delivery, deliveryError: error || '', deliveredAt: new Date().toISOString() };
    localStorage.setItem(portfolioReviewStorageKey, JSON.stringify(state));
    if (window.location.pathname === '/') void initPortfolio();
  };

  record('sending');
  try {
    const response = await fetch('/api/decision-reviews', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ priority: Number(priority), optionId: review.optionId, note: review.note || '' }),
    });
    if (!response.ok) throw new Error(`review inbox returned ${response.status}`);
    record('sent');
  } catch (error) {
    record('failed', error?.message || String(error));
    console.warn('Local decision review remains browser-only', error);
  }
}

async function clearPortfolioReview(priority) {
  const reviews = portfolioReviewState();
  delete reviews[String(priority)];
  localStorage.setItem(portfolioReviewStorageKey, JSON.stringify(reviews));
  try { await fetch(`/api/decision-reviews?priority=${encodeURIComponent(priority)}`, { method: 'DELETE' }); } catch (error) { console.warn('Could not clear local decision review inbox', error); }
  initPortfolio();
}

function mergeInboxReviews(inbox) {
  if (!Array.isArray(inbox?.reviews)) return;
  const local = portfolioReviewState();

  // Merge fields; never replace the record wholesale. The previous version
  // assigned the server copy over the local one, which discarded client-side
  // delivery state on every poll, so an answer that had reached the inbox still
  // displayed as unconfirmed.
  //
  // Presence in the inbox is itself the delivery proof: the server only holds a
  // review because a POST succeeded. That is a stronger signal than anything the
  // browser can assert about its own request, so it wins.
  const seen = new Set();
  for (const review of inbox.reviews) {
    const key = String(review.priority);
    seen.add(key);
    const existing = local[key] || {};
    const serverIsNewer = String(review.updatedAt || '') > String(existing.updatedAt || '');
    local[key] = {
      ...existing,
      ...(serverIsNewer ? review : {}),
      delivery: 'sent',
      deliveredAt: review.updatedAt || existing.deliveredAt || new Date().toISOString(),
      deliveryError: '',
    };
  }

  // A selection this browser holds that the inbox does not is undelivered, and
  // is marked so rather than left ambiguous.
  for (const [key, value] of Object.entries(local)) {
    if (!seen.has(key) && value?.optionId && value.delivery !== 'sending') {
      local[key] = { ...value, delivery: value.delivery === 'failed' ? 'failed' : 'pending' };
    }
  }

  localStorage.setItem(portfolioReviewStorageKey, JSON.stringify(local));
}

function exportPortfolioReviews() {
  const review = portfolioReviewState();
  download('living-documents-portfolio-decision-review.json', `${JSON.stringify({ schema: 'living-documents-portfolio-decision-review/v1', createdAt: new Date().toISOString(), localOnly: true, reviews: review }, null, 2)}\n`, 'application/json');
}

function deliveryStatus(review, priority) {
  const when = review.deliveredAt ? new Date(review.deliveredAt).toLocaleString() : '';
  if (review.delivery === 'sent') {
    return `<p class="delivery-state delivery-sent" role="status"><strong>Sent to the review inbox</strong> at ${escapeHtml(when)}. An agent records it canonically from there.</p>`;
  }
  if (review.delivery === 'sending') {
    return '<p class="delivery-state delivery-sending" role="status"><strong>Sending…</strong></p>';
  }
  if (review.delivery === 'failed') {
    return `<p class="delivery-state delivery-failed" role="alert"><strong>Not sent.</strong> Your choice is saved in this browser only and no agent can see it. Reason: ${escapeHtml(review.deliveryError || 'unknown')}. <button class="ghost-button" data-action="retry-portfolio-decision" data-priority="${priority}">Retry sending</button></p>`;
  }
  return '<p class="delivery-state delivery-pending" role="status"><strong>Saved locally, delivery not confirmed.</strong> If this does not change, the review inbox is unreachable.</p>';
}

function decisionCard(decision) {
  const work = decision.work.map((item) => `<li><a href="${escapeHtml(item.href)}">${escapeHtml(item.project)}</a>: ${escapeHtml(item.nextAction)}</li>`).join('');
  const choice = decision.choice;
  const review = portfolioReviewState()[String(decision.priority)] || {};
  const choices = choice?.options?.map((option) => `<label class="portfolio-choice ${review.optionId === option.id ? 'active' : ''}"><input type="radio" name="portfolio-decision-${decision.priority}" data-action="portfolio-decision" data-priority="${decision.priority}" data-option="${escapeHtml(option.id)}" ${review.optionId === option.id ? 'checked' : ''} /><span><strong>${escapeHtml(option.label)}</strong>${option.recommended ? '<span class="tag tag-static">recommended</span>' : ''}<small>${escapeHtml(option.text)}</small></span></label>`).join('') || '';
  const trackingAge = Number.isInteger(decision.tracking?.ageDays)
    ? (decision.tracking.ageDays === 0 ? 'today' : `${decision.tracking.ageDays} ${decision.tracking.ageDays === 1 ? 'day' : 'days'}`)
    : 'an unknown interval';
  const tracking = decision.tracking?.trackedSince ? `<p class="health-detail"><strong>Queue tracking age:</strong> ${escapeHtml(trackingAge)} since ${escapeHtml(decision.tracking.trackedSince)}. This is not an inferred original decision age.</p>` : '';
  return `<article class="decision-card"><div class="record-heading"><span class="decision-priority">${decision.priority}</span><strong>${escapeHtml(decision.decision)}</strong></div><p>${escapeHtml(decision.unblocks)}</p>${tracking}${choice ? `<div class="decision-recommendation"><strong>Recommended next action:</strong> ${escapeHtml(choice.recommendation)}</div><fieldset class="portfolio-choice-list"><legend>Choose a direction</legend>${choices}<label class="portfolio-note-label" for="portfolio-note-${decision.priority}">Optional instructions for the agent</label><textarea id="portfolio-note-${decision.priority}" data-portfolio-note="${decision.priority}" placeholder="Add a target, reporting period, path, or another instruction.">${escapeHtml(review.note || '')}</textarea>${review.optionId ? deliveryStatus(review, decision.priority) : '<p class="health-detail">Choose an option above. Your selection is sent to the review inbox for an agent to record canonically; it does not execute work by itself.</p>'}${review.optionId ? `<button class="ghost-button" data-action="clear-portfolio-decision" data-priority="${decision.priority}" title="Remove this local selection from the browser and loopback review inbox">Clear local selection</button>` : ''}</fieldset>` : '<p class="health-detail">This decision is already resolved in the canonical queue.</p>'}<div class="operation-next"><strong>Released work:</strong><ul>${work || '<li>Ledger mapping unavailable</li>'}</ul></div></article>`;
}

function workstreamCard(workstream) {
  const projects = workstream.projects.map((project) => `<a class="tag" href="${escapeHtml(project.href)}">${escapeHtml(project.title)}</a>`).join('');
  const relationships = workstream.relationships.map((relationship) => `<li><strong>${escapeHtml(relationship.from)} → ${escapeHtml(relationship.to)}</strong> <span class="tag tag-static">${escapeHtml(relationship.type)}</span><br />${escapeHtml(relationship.statement)}${relationship.work.length ? `<div class="workstream-work">${relationship.work.map((work) => `<a href="${escapeHtml(work.href)}">${escapeHtml(work.project)}: ${escapeHtml(work.nextAction)}</a>`).join('')}</div>` : ''}</li>`).join('');
  return `<article class="workstream-card"><div class="record-heading"><strong>${escapeHtml(workstream.title)}</strong><span class="status-badge tag-static">${workstream.relationships.length} links</span></div><p>${escapeHtml(workstream.summary)}</p><div class="record-meta">${projects}</div><ol class="workstream-relationships">${relationships}</ol></article>`;
}

function activityCard(event) {
  return `<article class="activity-card"><div class="record-heading"><strong>${escapeHtml(event.project)}</strong><span class="tag tag-static">${escapeHtml(event.kind)} · ${escapeHtml(event.status)}</span></div><p>${escapeHtml(event.summary)}</p><div class="record-meta"><span class="tag tag-static">${escapeHtml(event.timestamp)}</span><span class="tag tag-static">${escapeHtml(event.workId)}</span></div><a href="${escapeHtml(event.href)}">Open dossier</a></article>`;
}

function timelineState(status) {
  return ['active', 'interrupted', 'blocked', 'complete', 'unclassified'].includes(status) ? status : 'unknown';
}

function renderWorkTimeline(events) {
  const dated = events.map((event) => ({ ...event, epoch: Date.parse(event.timestamp) })).filter((event) => Number.isFinite(event.epoch));
  if (!dated.length) return '<div class="empty-state"><strong>No timestamped activity yet</strong>The timeline appears after an explicit ledger or handoff record.</div>';
  const latest = Math.max(...dated.map((event) => event.epoch));
  const earliest = Math.min(...dated.map((event) => event.epoch));
  const span = Math.max(latest - earliest, 60 * 60 * 1000);
  const rows = [...new Map(dated.map((event) => [`${event.project}/${event.workId}`, { project: event.project, workId: event.workId, events: [] }])).values()];
  for (const event of dated) rows.find((row) => row.project === event.project && row.workId === event.workId).events.push(event);
  rows.sort((a, b) => Math.max(...b.events.map((event) => event.epoch)) - Math.max(...a.events.map((event) => event.epoch)));
  return `<div class="work-timeline" role="region" aria-label="Explicit work record timeline"><div class="timeline-axis"><span>${escapeHtml(formatDateTime(new Date(earliest).toISOString()))}</span><span>${escapeHtml(formatDateTime(new Date(latest).toISOString()))}</span></div>${rows.slice(0, 20).map((row) => `<div class="work-timeline-row"><a class="work-timeline-label" href="${escapeHtml(row.events[0].href)}">${escapeHtml(row.project)}<small>${escapeHtml(row.workId)}</small></a><div class="work-timeline-track">${row.events.map((event) => { const position = ((event.epoch - earliest) / span) * 100; const sessions = event.sessions?.length ? ` Sessions: ${event.sessions.join(', ')}.` : ''; return `<a class="timeline-marker ${timelineState(event.status)}" href="${escapeHtml(event.href)}" style="left:${position.toFixed(3)}%" title="${escapeHtml(`${event.timestamp}: ${event.kind} ${event.status}. ${event.summary}${sessions}`)}"><span class="sr-only">${escapeHtml(`${event.timestamp}: ${event.project} ${event.workId}, ${event.status}`)}</span></a>`; }).join('')}</div></div>`).join('')}</div>`;
}

function gitPulseCard(pulse) {
  if (pulse.state !== 'git') return `<article class="git-pulse-card"><div class="record-heading"><strong>${escapeHtml(pulse.projectId)}</strong><span class="status-badge tag-static">${escapeHtml(pulse.state)}</span></div><p>Git status is unavailable for this registered source root; no repository action was attempted.</p></article>`;
  return `<article class="git-pulse-card"><div class="record-heading"><strong>${escapeHtml(pulse.projectId)}</strong><span class="status-badge tag-static">${pulse.dirtyCount ? `${pulse.dirtyCount} dirty` : 'clean'}</span></div><p><strong>${escapeHtml(pulse.branch)}</strong>${pulse.upstream ? ` → ${escapeHtml(pulse.upstream)}` : ''} · ahead ${pulse.ahead}, behind ${pulse.behind}</p><p>${escapeHtml(pulse.shortSha)} · ${escapeHtml(pulse.committedAt)}<br />${escapeHtml(pulse.subject)}</p></article>`;
}

function evidenceHealthCard(record) {
  const missing = record.evidence.filter((item) => !item.available);
  return `<article class="operation-work-card"><div class="record-heading"><strong>${escapeHtml(record.project)}</strong><span class="status-badge tag-static">${missing.length ? `${missing.length} missing` : 'evidence present'}</span></div><p>${escapeHtml(record.workId)}</p>${missing.length ? `<p class="operation-next"><strong>Missing:</strong> ${escapeHtml(missing.map((item) => item.path).join(', '))}</p>` : '<p>All cited local evidence paths resolve.</p>'}<a href="${escapeHtml(record.href)}">Open dossier</a></article>`;
}

function projectSummaryRow(project) {
  const search = `${project.title} ${project.projectId} ${project.state} ${project.nextAction}`.toLowerCase();
  return `<tr data-project-summary-row data-search="${escapeHtml(search)}"><th scope="row"><a href="${escapeHtml(project.href)}">${escapeHtml(project.title)}</a></th><td>${escapeHtml(project.state)}</td><td>${escapeHtml(project.nextAction)}</td></tr>`;
}

function sourceControlRiskCard(pulse) {
  const degradedState = {
    'no-source-root': 'No source root is registered for this dossier.',
    'unavailable-source-root': 'The registered source root is currently unavailable.',
    'not-git': 'The registered source root is available, but it is not a Git worktree.',
    'git-unavailable': 'The registered source root is available, but its Git metadata could not be read.',
  };
  const detail = pulse.state === 'git'
    ? `${escapeHtml(pulse.branch)}${pulse.upstream ? ` → ${escapeHtml(pulse.upstream)}` : ''} · ahead ${pulse.ahead}, behind ${pulse.behind}`
    : degradedState[pulse.state] || 'Git state could not be determined for this registered source root.';
  return `<article class="git-pulse-card"><div class="record-heading"><strong>${escapeHtml(pulse.projectId)}</strong><span class="status-badge tag-static">${escapeHtml(pulse.conditions.join(' · '))}</span></div><p>${detail}</p><a href="${escapeHtml(pulse.href)}">Open dossier</a></article>`;
}

function healthMetric(label, value, target) {
  return `<a class="portfolio-card" href="${escapeHtml(target)}"><div class="record-heading"><strong>${escapeHtml(label)}</strong><span class="status-badge tag-static">${escapeHtml(value)}</span></div><p>Open the source-backed detail.</p></a>`;
}

function delegationCard(item, kind) {
  if (kind === 'decision') return `<article class="decision-card"><div class="record-heading"><span class="decision-priority">${item.priority}</span><strong>${escapeHtml(item.decision)}</strong></div><p>${escapeHtml(item.unblocks)}</p><div class="record-meta"><span class="tag tag-static">${item.workIds.join(', ')}</span></div></article>`;
  const detail = kind === 'blocked' ? item.blocker : item.summary;
  return `<article class="operation-work-card"><div class="record-heading"><strong>${escapeHtml(item.project)}</strong><span class="status-badge tag-static">${kind}</span></div><p>${escapeHtml(detail)}</p><p class="operation-next"><strong>Next:</strong> ${escapeHtml(item.nextAction)}</p><a href="${escapeHtml(item.href)}">Open dossier</a></article>`;
}

function portfolioMetric(label, value, target, tone = '') {
  return `<button class="portfolio-metric ${tone}" data-action="portfolio-view" data-portfolio-view="${escapeHtml(target)}"><strong>${escapeHtml(value)}</strong><span>${escapeHtml(label)}</span></button>`;
}

function portfolioProjectTable(projects) {
  return `
    <div class="table-scroll" role="region" aria-label="Registered project dossiers" tabindex="0">
      <table class="portfolio-table">
        <caption>Registered dossiers and projection state</caption>
        <thead><tr><th scope="col">Project</th><th scope="col">Status</th><th scope="col">Lifecycle</th><th scope="col">Pages</th><th scope="col">Projection</th><th scope="col">Updated</th></tr></thead>
        <tbody>${projects.map((project) => `<tr><th scope="row"><a href="${escapeHtml(project.href)}">${escapeHtml(project.title)}</a><small>${escapeHtml(project.subtitle || project.projectId)}</small></th><td>${escapeHtml(project.status)}</td><td>${escapeHtml(project.lifecycle)}</td><td class="numeric">${project.sectionCount}</td><td>${escapeHtml(project.projection?.state || 'unknown')}</td><td>${escapeHtml(project.updated || 'unknown')}</td></tr>`).join('')}</tbody>
      </table>
    </div>`;
}

function portfolioViewHeader(eyebrow, title, description, count = '') {
  return `<header class="workspace-view-header"><div><p class="eyebrow">${escapeHtml(eyebrow)}</p><h1>${escapeHtml(title)}</h1><p>${escapeHtml(description)}</p></div>${count !== '' ? `<strong class="view-total">${escapeHtml(count)}</strong>` : ''}</header>`;
}

function renderPortfolioOverview(operations) {
  const decisions = operations.decisions.filter((decision) => decision.status !== 'resolved').slice(0, 3);
  const nextWork = (operations.work.actionable.length ? operations.work.actionable : operations.work.blockers).slice(0, 4);
  return `
    ${portfolioViewHeader('Workspace signal', 'What needs attention now', 'A bounded current-state view. Open a dedicated view for the full record.')}
    <section class="portfolio-metrics" aria-label="Portfolio counts">
      ${portfolioMetric('Decisions', operations.health.unresolvedDecisions, 'decisions', operations.health.unresolvedDecisions ? 'attention' : '')}
      ${portfolioMetric('Blocked work', operations.health.blockedWork, 'work', operations.health.blockedWork ? 'danger' : '')}
      ${portfolioMetric('Active work', operations.health.activeWork, 'work')}
      ${portfolioMetric('Projects', operations.health.dossiers, 'projects')}
      ${portfolioMetric('Git risks', operations.health.sourceControlRisk, 'evidence', operations.health.sourceControlRisk ? 'attention' : '')}
    </section>
    <div class="workspace-split">
      <section class="workspace-panel" aria-labelledby="overview-decisions">
        <div class="section-heading"><h2 id="overview-decisions">Decision queue</h2><button class="text-button" data-action="portfolio-view" data-portfolio-view="decisions">View all ${operations.decisions.length}</button></div>
        <div class="decision-list">${decisions.map(decisionCard).join('') || '<p class="empty-state">No unresolved decisions.</p>'}</div>
      </section>
      <section class="workspace-panel" aria-labelledby="overview-work">
        <div class="section-heading"><h2 id="overview-work">Next work</h2><button class="text-button" data-action="portfolio-view" data-portfolio-view="work">Open work view</button></div>
        <div class="work-list">${nextWork.map(operationWorkCard).join('') || '<p class="empty-state">No actionable or blocked work records.</p>'}</div>
      </section>
    </div>
    <section class="workspace-panel overview-projects" aria-labelledby="overview-projects">
      <div class="section-heading"><h2 id="overview-projects">Project pulse</h2><button class="text-button" data-action="portfolio-view" data-portfolio-view="projects">Compare all ${operations.portfolio.projects.length}</button></div>
      ${portfolioProjectTable(operations.portfolio.projects.slice(0, 8))}
    </section>`;
}

function renderPortfolioDecisions(operations) {
  return `
    ${portfolioViewHeader('Human attention', 'Decisions', 'Choose the recommended direction, an alternative, or add instructions. Selections remain local until an agent records them canonically.', operations.decisions.length)}
    <div class="decision-list decision-list-wide">${operations.decisions.map(decisionCard).join('') || '<p class="empty-state">The decision queue is clear.</p>'}</div>`;
}

function renderPortfolioWork(operations) {
  return `
    ${portfolioViewHeader('Delegation surface', 'Work', 'Source-backed next actions grouped by what can continue, what awaits a decision, and what must not be bypassed.')}
    <section class="work-lanes" aria-label="Work board">
      <div class="work-lane"><div class="section-heading"><h2>Continue now</h2><span class="nav-count tag-static">${operations.delegation.actionable.length}</span></div>${operations.delegation.actionable.map((item) => delegationCard(item, 'actionable')).join('') || '<p class="empty-state">No independently actionable work.</p>'}</div>
      <div class="work-lane"><div class="section-heading"><h2>Needs direction</h2><span class="nav-count tag-static">${operations.delegation.decisions.length}</span></div>${operations.delegation.decisions.map((item) => delegationCard(item, 'decision')).join('') || '<p class="empty-state">No work awaits a decision.</p>'}</div>
      <div class="work-lane"><div class="section-heading"><h2>Do not bypass</h2><span class="nav-count tag-static">${operations.delegation.blocked.length}</span></div>${operations.delegation.blocked.map((item) => delegationCard(item, 'blocked')).join('') || '<p class="empty-state">No explicit blockers.</p>'}</div>
    </section>
    <section class="workspace-panel"><div class="section-heading"><h2>Cross-project workstreams</h2><span class="nav-count tag-static">${operations.workstreams.length}</span></div><div class="workstream-grid">${operations.workstreams.map(workstreamCard).join('')}</div></section>`;
}

function renderPortfolioProjects(operations) {
  return `
    ${portfolioViewHeader('Canonical dossiers', 'Projects', 'Compare current state, projection freshness, lifecycle, and next admissible action.', operations.portfolio.projects.length)}
    <section class="workspace-panel">${portfolioProjectTable(operations.portfolio.projects)}</section>
    <section class="workspace-panel"><div class="section-heading"><h2>Reconciliation summary</h2><span class="nav-count tag-static">${operations.projectSummaries.length}</span></div><label class="workspace-filter" for="project-summary-filter">Filter by project, state, or next action<input id="project-summary-filter" type="search" placeholder="Start typing to filter" autocomplete="off" /></label><div class="table-scroll" role="region" aria-label="Project reconciliation summary" tabindex="0"><table class="portfolio-table"><caption>Current reconciliation state and next admissible action</caption><thead><tr><th scope="col">Project</th><th scope="col">Current state</th><th scope="col">Next admissible action</th></tr></thead><tbody>${operations.projectSummaries.map(projectSummaryRow).join('')}</tbody></table></div></section>`;
}

function renderPortfolioActivity(operations) {
  return `
    ${portfolioViewHeader('Explicit records', 'Activity', 'Recorded ledger and handoff milestones. Blank time means no explicit event, not inferred inactivity.', operations.activity.length)}
    <section class="workspace-panel"><div class="section-heading"><h2>Work timeline</h2><span class="nav-count tag-static">latest 20 records</span></div>${renderWorkTimeline(operations.activity)}</section>
    <section class="workspace-panel"><div class="section-heading"><h2>Recent milestones</h2><span class="nav-count tag-static">${operations.activity.length}</span></div><div class="activity-grid">${operations.activity.slice(0, 24).map(activityCard).join('')}</div></section>`;
}

function renderPortfolioEvidence(operations) {
  const evidenceRisks = operations.evidenceHealth.filter((record) => record.status === 'blocked' || record.evidence.some((item) => !item.available));
  return `
    ${portfolioViewHeader('Operational evidence', 'Git + evidence', 'Read-only repository and evidence health. This view never fetches, stages, commits, resets, or pushes.')}
    <div class="workspace-split">
      <section class="workspace-panel"><div class="section-heading"><h2>Source-control risk</h2><span class="nav-count tag-static">${operations.sourceControlRisk.length}</span></div><div class="git-pulse-grid">${operations.sourceControlRisk.map(sourceControlRiskCard).join('') || '<p class="empty-state">No source-control risks observed.</p>'}</div></section>
      <section class="workspace-panel"><div class="section-heading"><h2>Evidence health</h2><span class="nav-count tag-static">${evidenceRisks.length}</span></div><div class="work-list">${evidenceRisks.map(evidenceHealthCard).join('') || '<p class="empty-state">All cited evidence paths resolve.</p>'}</div></section>
    </div>
    <section class="workspace-panel"><div class="section-heading"><h2>Git pulse</h2><span class="nav-count tag-static">${operations.gitPulse.projects.length}</span></div><div class="git-pulse-grid">${operations.gitPulse.projects.map(gitPulseCard).join('')}</div></section>`;
}

function renderPortfolioView(operations) {
  return ({
    overview: renderPortfolioOverview,
    decisions: renderPortfolioDecisions,
    work: renderPortfolioWork,
    projects: renderPortfolioProjects,
    activity: renderPortfolioActivity,
    evidence: renderPortfolioEvidence
  }[portfolioView] || renderPortfolioOverview)(operations);
}

function renderPortfolioShell(operations) {
  const localReviews = Object.keys(portfolioReviewState()).length;
  app.innerHTML = `
    <div class="portfolio-shell">
      <header class="portfolio-topbar">
        <a class="portfolio-brand" href="/" aria-label="Living Documents portfolio"><span>LD</span><strong>Living Documents</strong><small>Workspace</small></a>
        <nav class="portfolio-tabs" aria-label="Portfolio views">
          ${portfolioViews.map(([id, label]) => `<button data-action="portfolio-view" data-portfolio-view="${id}" class="${portfolioView === id ? 'active' : ''}" ${portfolioView === id ? 'aria-current="page"' : ''}>${label}${id === 'decisions' && operations.health.unresolvedDecisions ? `<span>${operations.health.unresolvedDecisions}</span>` : ''}</button>`).join('')}
        </nav>
        <div class="portfolio-utilities">
          <a href="/api/portfolio-export" download title="Download the current read-only workspace export">Export data</a>
          <button data-action="export-portfolio-reviews" title="Download local decision selections for an agent">Reviews <span>${localReviews}</span></button>
        </div>
      </header>
      <main class="portfolio-main" id="main-content" tabindex="-1">${renderPortfolioView(operations)}</main>
      <footer class="portfolio-status"><span><i aria-hidden="true"></i> Auto-refresh on</span><span>Canonical sources: portfolio index, project Markdown, and explicit ledger</span><time datetime="${escapeHtml(new Date().toISOString())}">Observed ${escapeHtml(formatDateTime(new Date().toISOString()))}</time></footer>
      <div class="toast-region" id="toast-region" role="status" aria-live="polite" aria-atomic="true"></div>
    </div>`;
  const projectFilter = document.querySelector('#project-summary-filter');
  const projectCount = document.querySelector('#project-summary-count');
  projectFilter?.addEventListener('input', () => {
    const query = projectFilter.value.trim().toLowerCase();
    const rows = [...document.querySelectorAll('[data-project-summary-row]')];
    const visible = rows.filter((row) => { const matches = !query || row.dataset.search.includes(query); row.hidden = !matches; return matches; });
    if (projectCount) projectCount.textContent = String(visible.length);
  });
}

async function initPortfolio() {
  try {
    const [operations, inbox] = await Promise.all([
      fetchJson('/api/operations'),
      fetchJson('/api/decision-reviews').catch(() => null),
    ]);
    mergeInboxReviews(inbox);
    portfolioSnapshot = operations;
    const hashView = {
      decisions: 'decisions',
      delegation: 'work',
      now: 'work',
      workstreams: 'work',
      activity: 'activity',
      timeline: 'activity',
      'project-summary': 'projects',
      'portfolio-projects': 'projects',
      'source-control-risk': 'evidence',
      'evidence-health': 'evidence',
      'git-pulse': 'evidence'
    }[window.location.hash.slice(1)];
    if (hashView) portfolioView = hashView;
    if (!portfolioViews.some(([id]) => id === portfolioView)) portfolioView = 'overview';
    document.title = 'Living Documents portfolio';
    renderPortfolioShell(operations);
    clearTimeout(portfolioRefreshTimer);
    portfolioRefreshTimer = window.setTimeout(initPortfolio, 15000);
  } catch (error) {
    app.innerHTML = `<div class="boot-screen"><div class="boot-mark">!</div><h1>Portfolio failed to open</h1><p>${escapeHtml(error.message)}</p></div>`;
  }
}

init();
