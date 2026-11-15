/* ---
file: app.js
purpose: Dependency-free living-document dashboard, reader, search, history, changelog, quick edit, local overlays, themes, and exports.
version: 1.2.0
--- */

const app = document.querySelector('#app');
const themeNames = {
  system: 'System',
  obsidian: 'Obsidian',
  graphite: 'Graphite',
  paper: 'Paper',
  'high-contrast': 'High contrast'
};
const motionNames = { system: 'System motion', full: 'Full motion', reduced: 'Reduced motion' };
const viewDefinitions = [
  ['dashboard', '⌂', 'Dashboard'],
  ['document', '¶', 'Document'],
  ['history', '↺', 'History'],
  ['changelog', 'Δ', 'Changelog'],
  ['search', '⌕', 'Search']
];

const state = {
  manifest: null,
  annotations: [],
  sectionContent: new Map(),
  activeView: 'dashboard',
  activeSectionId: null,
  searchQuery: '',
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
    const safe = escapeHtml(safeHref(href));
    const external = /^https?:/i.test(href) ? ' target="_blank" rel="noreferrer"' : '';
    return `<a href="${safe}"${external}>${label}</a>`;
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
      <div class="annotation-meta"><span class="tag">${escapeHtml(resource.id)}</span><a class="tag" href="${escapeHtml(href)}" target="_blank" rel="noreferrer">${escapeHtml(resource.path || resource.url || 'external')}</a></div>
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

function currentSection() {
  return effectiveSection(state.activeSectionId || state.manifest.navigation.sectionOrder[0]);
}

function formatDate(value) {
  try {
    return new Intl.DateTimeFormat(undefined, { year: 'numeric', month: 'short', day: 'numeric' }).format(new Date(value));
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
  return tags.map((tag) => `<span class="tag">${escapeHtml(tag)}</span>`).join('');
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
  return `
    <header class="topbar">
      <div class="brand">
        <button class="icon-button mobile-only" data-action="toggle-left" aria-label="Open section index">☰</button>
        <div class="brand-mark" aria-hidden="true">LDF</div>
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
        <button class="icon-button" data-action="command" aria-label="Open command palette" title="Command palette">⌘</button>
        <button class="icon-button" data-action="undo" aria-label="Undo" title="Undo" ${state.undoStack.length ? '' : 'disabled'}>↶</button>
        <button class="icon-button" data-action="redo" aria-label="Redo" title="Redo" ${state.redoStack.length ? '' : 'disabled'}>↷</button>
        <select class="select-control desktop-only" id="theme-select" aria-label="Theme">
          ${Object.entries(themeNames).map(([id, label]) => `<option value="${id}" ${state.theme === id ? 'selected' : ''}>${label}</option>`).join('')}
        </select>
        <select class="select-control desktop-only" id="motion-select" aria-label="Motion preference">
          ${Object.entries(motionNames).map(([id, label]) => `<option value="${id}" ${state.motion === id ? 'selected' : ''}>${label}</option>`).join('')}
        </select>
        <button class="icon-button mobile-inspector-button" data-action="toggle-right" aria-label="Open inspector" title="Inspector">ⓘ</button>
        <button class="text-button desktop-only" data-action="export-change" title="Export local edits">
          Export${changes ? ` · ${changes}` : ''}
        </button>
      </div>
    </header>`;
}

function renderLeftRail() {
  const openAnnotations = allAnnotations().filter((annotation) => annotation.status === 'open').length;
  const proposed = state.manifest.proposals.filter((proposal) => decisionFor(proposal) === 'proposed').length;
  const viewCounts = {
    dashboard: proposed,
    document: state.manifest.sections.length,
    history: state.manifest.history.length + state.localHistory.length,
    changelog: state.manifest.releases.length,
    search: openAnnotations
  };
  const allTags = [...new Set(state.manifest.sections.flatMap((section) => section.tags))].sort();
  const statuses = [...new Set(state.manifest.sections.map((section) => section.status))].sort();
  const sections = matchingSections();

  return `
    <aside class="left-rail" aria-label="Document navigation">
      <div class="rail-inner">
        <section class="rail-section">
          <p class="rail-label">Workbench</p>
          <nav aria-label="Primary views">
            <ul class="view-nav">
              ${viewDefinitions.map(([id, icon, label]) => `
                <li><button class="view-link ${state.activeView === id ? 'active' : ''}" data-action="view" data-view="${id}" ${state.activeView === id ? 'aria-current="page"' : ''}>
                  ${iconLabel(icon, label)}<span class="nav-count">${viewCounts[id]}</span>
                </button></li>`).join('')}
            </ul>
          </nav>
        </section>

        <section class="rail-section">
          <div class="section-heading">
            <h3>Section index</h3>
            <span class="nav-count">${sections.length}</span>
          </div>
          <div class="filter-row" aria-label="Status filters">
            <button class="filter-button ${state.statusFilter === 'all' ? 'active' : ''}" data-action="status-filter" data-value="all">All</button>
            ${statuses.map((status) => `<button class="filter-button ${state.statusFilter === status ? 'active' : ''}" data-action="status-filter" data-value="${escapeHtml(status)}">${escapeHtml(status)}</button>`).join('')}
          </div>
          <ol class="section-list">
            ${sections.map((section) => `
              <li>
                <button class="section-link ${state.activeSectionId === section.id && state.activeView === 'document' ? 'active' : ''}" data-action="section" data-section="${section.id}">
                  <span class="section-number">${escapeHtml(section.index)}</span>
                  <span class="section-name">${escapeHtml(section.title)}</span>
                  ${state.drafts[section.id] ? '<span class="draft-dot" title="Local draft"></span>' : statusDot(section.status)}
                </button>
              </li>`).join('')}
          </ol>
        </section>

        <section class="rail-section">
          <p class="rail-label">Tags</p>
          <div class="filter-row">
            <button class="filter-button ${state.tagFilter === 'all' ? 'active' : ''}" data-action="tag-filter" data-value="all">All</button>
            ${allTags.slice(0, 12).map((tag) => `<button class="filter-button ${state.tagFilter === tag ? 'active' : ''}" data-action="tag-filter" data-value="${escapeHtml(tag)}">${escapeHtml(tag)}</button>`).join('')}
          </div>
        </section>

        <section class="rail-section">
          <p class="rail-label">Local state</p>
          <dl class="meta-list">
            <div class="meta-row"><dt>Drafts</dt><dd>${Object.keys(state.drafts).length}</dd></div>
            <div class="meta-row"><dt>Decisions</dt><dd>${Object.keys(state.proposalDecisions).length}</dd></div>
            <div class="meta-row"><dt>Notes</dt><dd>${state.localAnnotations.length}</dd></div>
          </dl>
        </section>
      </div>
    </aside>`;
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
        <span class="status-badge">${escapeHtml(state.manifest.meta.status)}</span>
      </div>
    </header>`;
}

function dashboardMetrics() {
  return [
    [state.manifest.sections.length, 'Addressable sections'],
    [allAnnotations().filter((annotation) => annotation.status === 'open').length, 'Open annotations'],
    [state.manifest.proposals.filter((proposal) => decisionFor(proposal) === 'proposed').length, 'Pending decisions'],
    [modelReplies().filter((reply) => reply.status !== 'resolved').length, 'Model replies'],
    [resourceList().length, 'Resources'],
    [localChangeCount(), 'Local changes']
  ];
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
      ${pageHeader(state.manifest.meta.title, state.manifest.meta.subtitle, 'Living document · dashboard')}
      <section class="focus-band" aria-labelledby="current-focus">
        <div>
          <p class="eyebrow">Current focus</p>
          <h2 id="current-focus">${escapeHtml(state.manifest.dashboard.focus)}</h2>
        </div>
        <button class="primary-button" data-action="view" data-view="document">Enter document</button>
      </section>
      <section class="metric-strip" aria-label="Document metrics">
        ${dashboardMetrics().map(([value, label]) => `<div class="metric"><strong class="metric-value">${value}</strong><span class="metric-label">${escapeHtml(label)}</span></div>`).join('')}
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

          <div class="section-heading" style="margin-top:2.4rem"><h2>Decision queue</h2><span class="nav-count">${pending.length}</span></div>
          <div class="proposal-list">
            ${pending.map(renderProposal).join('') || '<div class="empty-state"><strong>Queue clear</strong>No proposals await a decision.</div>'}
          </div>

          <div class="section-heading" style="margin-top:2.4rem"><h2>Model replies</h2><span class="nav-count">${replies.length}</span></div>
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
      <div class="proposal-meta">
        <span class="tag">${escapeHtml(proposal.id)}</span>
        <span class="tag">impact ${escapeHtml(proposal.impact)}</span>
        <span class="tag">effort ${escapeHtml(proposal.effort)}</span>
      </div>
      <div class="decision-row" aria-label="Proposal decision">
        ${['approve', 'defer', 'reject'].map((value) => `<button class="segment-button ${decision === value ? 'active' : ''}" data-action="proposal-decision" data-proposal="${proposal.id}" data-value="${value}">${value}</button>`).join('')}
      </div>
    </article>`;
}

function renderModelReply(reply) {
  return `
    <article class="proposal-item">
      <div class="proposal-title">${escapeHtml(reply.prompt)}</div>
      <p class="proposal-summary">${escapeHtml(reply.context || '')}</p>
      <div class="proposal-meta">
        <span class="tag">${escapeHtml(reply.id)}</span>
        <span class="tag">${escapeHtml(reply.status || 'open')}</span>
        ${(reply.targetIds || []).map((id) => `<span class="tag">${escapeHtml(id)}</span>`).join('')}
      </div>
      ${(reply.options || []).length ? `<ol class="option-list">${reply.options.map((option) => `<li><strong>${escapeHtml(option.label)}</strong> ${escapeHtml(option.text)}</li>`).join('')}</ol>` : ''}
      <p class="health-detail">Human can annotate, answer in a section draft, or export a change request with a custom response.</p>
    </article>`;
}

function renderDocument() {
  const sections = state.manifest.navigation.sectionOrder.map(effectiveSection).filter(Boolean);
  return `
    <div class="view-frame document-view">
      <div class="document-intro">
        ${pageHeader(state.manifest.meta.title, state.manifest.meta.subtitle, 'Canonical reader')}
        <p class="thesis">${escapeHtml(state.manifest.meta.thesis)}</p>
        <div class="section-toolbar">
          <button class="ghost-button" data-action="toggle-focused">${state.focused ? 'Exit focus' : 'Focused reading'} <kbd>F</kbd></button>
          <button class="ghost-button" data-action="quick-edit">Edit active <kbd>E</kbd></button>
          <button class="ghost-button" data-action="annotate-selection">Annotate selection</button>
          <button class="ghost-button" data-action="export-md">Export Markdown</button>
        </div>
      </div>
      ${sections.map((section) => `
        <section class="document-section" id="${section.id}" data-section-observe="${section.id}" aria-labelledby="${section.id}-title">
          <div class="section-kicker"><span>${escapeHtml(section.index)}</span><span>${escapeHtml(section.eyebrow)}</span>${statusDot(section.status)}</div>
          <h2 id="${section.id}-title">${escapeHtml(section.title)}</h2>
          <p class="section-dek">${escapeHtml(section.dek)}</p>
          ${state.drafts[section.id] ? `<div class="local-draft-banner"><span>Local draft overlays the canonical section.</span><button class="ghost-button" data-action="discard-draft" data-section="${section.id}">Discard</button></div>` : ''}
          <div class="section-toolbar">
            ${tagMarkup(section.tags)}
            ${section.editable ? `<button class="ghost-button" data-action="quick-edit" data-section="${section.id}">Quick edit</button>` : ''}
          </div>
          <div class="markdown-body">${renderMarkdown(section.markdown)}</div>
        </section>`).join('')}
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
    document: renderDocument,
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
      <div class="section-toolbar">
        <button class="primary-button" data-action="quick-edit" data-section="${section.id}" ${section.editable ? '' : 'disabled'}>Quick edit</button>
        <button class="ghost-button" data-action="add-annotation" data-section="${section.id}">Add note</button>
        <button class="ghost-button" data-action="annotate-selection">Annotate selection</button>
      </div>
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
      <div class="section-heading"><h3>Resources</h3><span class="nav-count">${resources.length}</span></div>
      <div class="annotation-list">
        ${resources.map(renderResource).join('') || '<p class="health-detail">No resources target this section.</p>'}
      </div>
    </section>
    <section class="rail-section">
      <div class="section-heading"><h3>Annotations</h3><span class="nav-count">${annotations.length}</span></div>
      <div class="annotation-list">
        ${annotations.map((annotation) => `
          <article class="annotation-item">
            <div class="annotation-title">${escapeHtml(annotation.kind)} · ${escapeHtml(annotation.status)}</div>
            ${annotation.quote ? `<blockquote class="annotation-quote">${escapeHtml(annotation.quote)}</blockquote>` : ''}
            <p class="annotation-text">${escapeHtml(annotation.text)}</p>
            <div class="annotation-meta"><span class="tag">${escapeHtml(annotation.author)}</span><span class="tag">${formatDate(annotation.createdAt)}</span></div>
          </article>`).join('') || '<p class="health-detail">No annotations target this section.</p>'}
      </div>
    </section>`;
}

function renderDashboardInspector() {
  const proposed = state.manifest.proposals.filter((proposal) => decisionFor(proposal) === 'proposed');
  return `
    <div class="inspector-header"><h2>Control surface</h2></div>
    <section class="rail-section">
      <p class="rail-label">Appearance</p>
      <div class="field"><label for="inspector-theme">Theme</label><select class="select-control" id="inspector-theme">${Object.entries(themeNames).map(([id, label]) => `<option value="${id}" ${state.theme === id ? 'selected' : ''}>${label}</option>`).join('')}</select></div>
      <div class="field" style="margin-top:.7rem"><label for="inspector-motion">Motion</label><select class="select-control" id="inspector-motion">${Object.entries(motionNames).map(([id, label]) => `<option value="${id}" ${state.motion === id ? 'selected' : ''}>${label}</option>`).join('')}</select></div>
      <div class="field" style="margin-top:.7rem"><label for="density-select">Density</label><select class="select-control" id="density-select"><option value="comfortable" ${state.density === 'comfortable' ? 'selected' : ''}>Comfortable</option><option value="compact" ${state.density === 'compact' ? 'selected' : ''}>Compact</option></select></div>
    </section>
    <section class="rail-section">
      <p class="rail-label">Exports</p>
      <button class="view-link" data-action="export-change">${iconLabel('⇧', 'Change request')}</button>
      <button class="view-link" data-action="export-json">${iconLabel('{}', 'Merged JSON')}</button>
      <button class="view-link" data-action="export-md">${iconLabel('¶', 'Combined Markdown')}</button>
    </section>
    <section class="rail-section">
      <p class="rail-label">Pending decisions</p>
      <p class="health-detail">${proposed.length} proposals remain unresolved.</p>
      <button class="primary-button" data-action="view" data-view="dashboard">Review queue</button>
    </section>
    <section class="rail-section">
      <p class="rail-label">Shortcuts</p>
      <button class="view-link" data-action="shortcuts">${iconLabel('?', 'Keyboard map')}</button>
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
  if (state.activeView === 'document') content = renderSectionInspector(currentSection());
  if (state.activeView === 'history') content = renderHistoryInspector();
  if (state.activeView === 'changelog') content = `${renderDashboardInspector()}<section class="rail-section"><p class="rail-label">Releases</p>${state.manifest.releases.map((release) => `<a class="view-link" href="#release-${escapeHtml(release.version)}">${iconLabel('v', release.version)}</a>`).join('')}</section>`;
  if (state.activeView === 'search') content = `${renderDashboardInspector()}<section class="rail-section"><p class="rail-label">Search tips</p><p class="health-detail">Title matches rank above tags, summaries, and body text. Press <kbd>/</kbd> from anywhere outside a form.</p></section>`;
  return `<aside class="right-rail" aria-label="Context inspector"><div class="rail-inner">${content}</div></aside>`;
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
        <div class="dialog-header"><h2 id="annotation-title">Add annotation</h2><button class="icon-button" type="button" data-action="close-dialog" data-dialog="annotation-dialog" aria-label="Close">×</button></div>
        <div class="dialog-body form-grid">
          <input type="hidden" name="targetId" id="annotation-target" />
          <input type="hidden" name="quote" id="annotation-quote" />
          <div class="field"><label for="annotation-kind">Kind</label><select id="annotation-kind" name="kind"><option>note</option><option>question</option><option>objection</option><option>decision</option><option>evidence</option></select></div>
          <div class="field"><label for="annotation-author">Author</label><input id="annotation-author" name="author" value="Local editor" required /></div>
          <div class="field full"><label for="annotation-quote-preview">Selected quote</label><textarea id="annotation-quote-preview" readonly placeholder="Select text in the document, then choose Annotate selection."></textarea></div>
          <div class="field full"><label for="annotation-text">Text</label><textarea id="annotation-text" name="text" required></textarea></div>
        </div>
        <div class="dialog-footer"><button class="ghost-button" type="button" data-action="close-dialog" data-dialog="annotation-dialog">Cancel</button><button class="primary-button" type="submit">Save annotation</button></div>
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
    <div class="toast-region" id="toast-region" aria-live="polite" aria-atomic="true"></div>`;
}

function render() {
  if (state.observer) state.observer.disconnect();
  document.documentElement.dataset.theme = state.theme;
  document.documentElement.dataset.motion = state.motion;
  document.documentElement.dataset.density = state.density;
  document.body.classList.toggle('focused', state.focused);
  app.innerHTML = `
    <div class="app-shell">
      ${renderTopbar()}
      ${renderLeftRail()}
      ${renderMain()}
      ${renderRightRail()}
      <div class="reading-progress" aria-hidden="true"><span id="progress-bar"></span></div>
      <button class="scrim" data-action="close-drawers" aria-label="Close navigation drawers"></button>
    </div>
    ${renderDialogs()}`;
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
  document.body.classList.remove('left-open', 'right-open');
  render();
  requestAnimationFrame(() => document.querySelector('#main-content')?.focus({ preventScroll: true }));
}

function goToSection(id) {
  state.activeView = 'document';
  state.activeSectionId = id;
  document.body.classList.remove('left-open', 'right-open');
  render();
  requestAnimationFrame(() => document.getElementById(id)?.scrollIntoView({ behavior: motionReduced() ? 'auto' : 'smooth', block: 'start' }));
}

function motionReduced() {
  return state.motion === 'reduced' || (state.motion === 'system' && matchMedia('(prefers-reduced-motion: reduce)').matches);
}

function applyTheme(theme) {
  const update = () => {
    state.theme = theme;
    document.documentElement.dataset.theme = theme;
    localStorage.setItem('ldf:theme', theme);
    document.querySelectorAll('#theme-select, #inspector-theme').forEach((select) => { select.value = theme; });
  };
  if (!motionReduced() && document.startViewTransition) document.startViewTransition(update);
  else update();
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
    if (inspector && section) inspector.innerHTML = renderSectionInspector(section);
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
      <div><p class="eyebrow">Local overlay · ${escapeHtml(section.id)}</p><h2 id="quick-edit-title">Quick edit section</h2></div>
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

function openAnnotationDialog(id = state.activeSectionId, quote = '') {
  const target = id || 'document';
  document.querySelector('#annotation-target').value = target;
  document.querySelector('#annotation-quote').value = quote;
  document.querySelector('#annotation-quote-preview').value = quote;
  document.querySelector('#annotation-text').value = '';
  document.querySelector('#annotation-dialog').showModal();
  requestAnimationFrame(() => document.querySelector('#annotation-text')?.focus());
}

function openSelectionAnnotationDialog() {
  const quote = selectedQuote();
  if (!quote.text) {
    toast('Select document text before annotating');
    return;
  }
  openAnnotationDialog(quote.sectionId, quote.text);
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
    summary: `Added an annotation to ${targetId}`,
    targetIds: [targetId],
    version: state.manifest.meta.version,
    source: 'local'
  });
  persistLocalState();
  document.querySelector('#annotation-dialog').close();
  render();
  toast('Annotation added');
}

function commands(query = '') {
  const base = [
    { group: 'Navigate', label: 'Open dashboard', hint: 'G D', run: () => setView('dashboard') },
    { group: 'Navigate', label: 'Open document', hint: 'G R', run: () => setView('document') },
    { group: 'Navigate', label: 'Open history', hint: 'G H', run: () => setView('history') },
    { group: 'Navigate', label: 'Open changelog', hint: 'G C', run: () => setView('changelog') },
    { group: 'Edit', label: 'Quick edit active section', hint: 'E', run: () => openQuickEdit() },
    { group: 'Edit', label: 'Annotate selected text', hint: '', run: openSelectionAnnotationDialog },
    { group: 'Edit', label: 'Undo local change', hint: '⌘ Z', run: undo },
    { group: 'Edit', label: 'Redo local change', hint: '⌘ ⇧ Z', run: redo },
    { group: 'View', label: state.focused ? 'Exit focused reading' : 'Enter focused reading', hint: 'F', run: toggleFocused },
    { group: 'Export', label: 'Export change request', hint: '', run: exportChangeRequest },
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
  toast(state.focused ? 'Focused reading enabled' : 'Workbench restored');
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

function exportChangeRequest() {
  const payload = {
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
    constraints: ['Preserve stable IDs', 'Do not rewrite unrelated sections', 'Append history and worklog entries', 'Validate format 2.1.0'],
    expectedOutputs: ['Updated source files', 'Validation report', 'Appended history event', 'Appended worklog entry']
  };
  download(`${state.manifest.meta.documentId}-change-request.json`, `${JSON.stringify(payload, null, 2)}\n`, 'application/json');
  toast('Change request exported');
}

function exportJson() {
  const merged = structuredClone(state.manifest);
  merged.sections = merged.sections.map((section) => {
    const effective = effectiveSection(section.id);
    return { ...section, ...state.drafts[section.id], markdown: effective.markdown };
  });
  merged.proposals = merged.proposals.map((proposal) => ({ ...proposal, decision: decisionFor(proposal) }));
  merged.annotations = allAnnotations();
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

function closeDrawers() {
  document.body.classList.remove('left-open', 'right-open');
}

function isTypingTarget(target) {
  return target instanceof HTMLInputElement || target instanceof HTMLTextAreaElement || target instanceof HTMLSelectElement || target?.isContentEditable;
}

app.addEventListener('click', (event) => {
  const control = event.target.closest('[data-action]');
  if (!control) return;
  const action = control.dataset.action;
  if (action === 'view') setView(control.dataset.view);
  if (action === 'section') goToSection(control.dataset.section);
  if (action === 'status-filter') { state.statusFilter = control.dataset.value; render(); }
  if (action === 'tag-filter') { state.tagFilter = control.dataset.value; render(); }
  if (action === 'history-filter') { state.historyFilter = control.dataset.value; render(); }
  if (action === 'toggle-left') document.body.classList.toggle('left-open');
  if (action === 'toggle-right') document.body.classList.toggle('right-open');
  if (action === 'close-drawers') closeDrawers();
  if (action === 'toggle-focused') toggleFocused();
  if (action === 'quick-edit') openQuickEdit(control.dataset.section);
  if (action === 'discard-draft') discardDraft(control.dataset.section);
  if (action === 'proposal-decision') saveProposalDecision(control.dataset.proposal, control.dataset.value);
  if (action === 'add-annotation') openAnnotationDialog(control.dataset.section);
  if (action === 'annotate-selection') openSelectionAnnotationDialog();
  if (action === 'close-dialog') document.getElementById(control.dataset.dialog)?.close();
  if (action === 'command') openCommandPalette();
  if (action === 'command-run') runCommand(Number(control.dataset.index));
  if (action === 'shortcuts') document.querySelector('#shortcuts-dialog').showModal();
  if (action === 'undo') undo();
  if (action === 'redo') redo();
  if (action === 'export-change') exportChangeRequest();
  if (action === 'export-json') exportJson();
  if (action === 'export-md') exportMarkdown();
});

app.addEventListener('submit', (event) => {
  event.preventDefault();
  if (event.target.id === 'quick-edit-form') saveQuickEdit(event.target);
  if (event.target.id === 'annotation-form') saveAnnotation(event.target);
});

app.addEventListener('input', (event) => {
  if (event.target.id === 'global-search') state.searchQuery = event.target.value;
  if (event.target.id === 'command-search') {
    state.commandIndex = 0;
    renderCommandList(event.target.value);
  }
});

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
    closeDrawers();
    document.querySelectorAll('dialog[open]').forEach((dialog) => dialog.close());
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

async function init() {
  try {
    const [manifest, annotationsFile] = await Promise.all([
      fetchJson('content/index.json'),
      fetchJson('data/annotations.json')
    ]);
    state.manifest = manifest;
    state.annotations = annotationsFile.annotations || [];
    state.activeView = manifest.navigation.defaultView || 'dashboard';
    state.activeSectionId = manifest.navigation.sectionOrder[0];
    if (!manifest.visual.themes.includes(state.theme)) state.theme = manifest.visual.defaultTheme;
    if (!['system', 'full', 'reduced'].includes(state.motion)) state.motion = manifest.visual.defaultMotion;
    loadLocalState();
    await Promise.all(manifest.sections.map(async (section) => {
      state.sectionContent.set(section.id, await fetchText(section.source));
    }));
    render();
  } catch (error) {
    console.error(error);
    app.innerHTML = `<div class="boot-screen"><div class="boot-mark">!</div><h1>Document failed to open</h1><p>${escapeHtml(error.message)}</p><p>Serve the project with <code>npm run dev</code>; browsers block local file fetches.</p></div>`;
  }
}

init();
