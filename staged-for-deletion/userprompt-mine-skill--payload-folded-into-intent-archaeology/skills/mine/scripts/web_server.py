#!/usr/bin/env python3
"""
Prompt Mine — Web Server & Browse Interface

Lightweight Flask server providing:
  - Web UI for browsing and searching conversations
  - REST API for search, filtering, and tagging
  - Capture API endpoint for Tampermonkey scripts

Usage:
    python web_server.py [--port 8420] [--enable-capture-api]
"""

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = os.path.expanduser("~/.prompt-mine/prompt_mine.db")

# ============================================================
# HTML/CSS/JS for the browse interface
# ============================================================

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Prompt Mine</title>
<style>
:root {
  --bg: #0f0f0f;
  --surface: #1a1a1a;
  --surface2: #252525;
  --border: #333;
  --text: #e0e0e0;
  --text-dim: #888;
  --accent: #6366f1;
  --accent-hover: #818cf8;
  --user-bg: #1e293b;
  --assistant-bg: #1a1a2e;
  --tag-bg: #2d2d44;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
       background: var(--bg); color: var(--text); line-height: 1.6; }

/* Layout */
.app { display: flex; height: 100vh; }
.sidebar { width: 260px; background: var(--surface); border-right: 1px solid var(--border);
           padding: 16px; overflow-y: auto; flex-shrink: 0; }
.main { flex: 1; display: flex; flex-direction: column; overflow: hidden; }

/* Search bar */
.search-bar { padding: 16px; background: var(--surface); border-bottom: 1px solid var(--border); }
.search-bar input { width: 100%; padding: 10px 16px; background: var(--surface2);
  border: 1px solid var(--border); border-radius: 8px; color: var(--text); font-size: 14px; }
.search-bar input:focus { outline: none; border-color: var(--accent); }

/* Sidebar */
.sidebar h3 { font-size: 12px; text-transform: uppercase; color: var(--text-dim);
              margin-bottom: 8px; letter-spacing: 1px; }
.sidebar-section { margin-bottom: 20px; }
.provider-check { display: flex; align-items: center; gap: 8px; padding: 4px 0;
                  cursor: pointer; font-size: 13px; }
.provider-check input { accent-color: var(--accent); }
.tag-pill { display: inline-block; padding: 2px 8px; margin: 2px; background: var(--tag-bg);
            border-radius: 4px; font-size: 11px; cursor: pointer; }
.tag-pill:hover { background: var(--accent); }

/* Conversation list */
.conv-list { flex: 1; overflow-y: auto; padding: 0; }
.conv-item { padding: 12px 20px; border-bottom: 1px solid var(--border);
             cursor: pointer; transition: background 0.15s; }
.conv-item:hover { background: var(--surface2); }
.conv-item.active { background: var(--surface2); border-left: 3px solid var(--accent); }
.conv-title { font-size: 14px; font-weight: 500; margin-bottom: 4px; }
.conv-meta { font-size: 12px; color: var(--text-dim); display: flex; gap: 12px; }
.conv-preview { font-size: 12px; color: var(--text-dim); margin-top: 4px;
                max-height: 40px; overflow: hidden; }

/* Detail view */
.detail { flex: 1; overflow-y: auto; padding: 24px; }
.detail-header { margin-bottom: 24px; }
.detail-header h2 { font-size: 20px; margin-bottom: 8px; }
.detail-header .meta { font-size: 13px; color: var(--text-dim); display: flex; gap: 12px; flex-wrap: wrap; }
.detail-header .tags { margin-top: 8px; }

.turn { margin-bottom: 16px; padding: 12px 16px; border-radius: 8px; position: relative; }
.turn-user { background: var(--user-bg); border-left: 3px solid #3b82f6; }
.turn-assistant { background: var(--assistant-bg); border-left: 3px solid var(--accent); }
.turn-role { font-size: 11px; text-transform: uppercase; font-weight: 600;
             margin-bottom: 6px; letter-spacing: 0.5px; }
.turn-user .turn-role { color: #3b82f6; }
.turn-assistant .turn-role { color: var(--accent); }
.turn-content { font-size: 14px; white-space: pre-wrap; word-break: break-word; }
.turn-collapsed .turn-content { max-height: 60px; overflow: hidden;
  position: relative; cursor: pointer; }
.turn-collapsed .turn-content::after {
  content: ''; position: absolute; bottom: 0; left: 0; right: 0; height: 30px;
  background: linear-gradient(transparent, var(--assistant-bg)); }
.expand-btn { font-size: 12px; color: var(--accent); cursor: pointer; margin-top: 4px; }
.expand-btn:hover { text-decoration: underline; }
.full-response { display: none; max-height: 400px; overflow-y: auto; padding: 8px;
  background: var(--surface); border-radius: 4px; margin-top: 8px; font-size: 13px;
  white-space: pre-wrap; }
.full-response.visible { display: block; }

.related { margin-top: 24px; padding-top: 16px; border-top: 1px solid var(--border); }
.related h4 { font-size: 13px; color: var(--text-dim); margin-bottom: 8px; }
.related-item { font-size: 13px; padding: 4px 0; cursor: pointer; color: var(--accent); }

/* Stats bar */
.stats-bar { padding: 8px 20px; background: var(--surface); border-top: 1px solid var(--border);
             font-size: 12px; color: var(--text-dim); display: flex; justify-content: space-between; }
</style>
</head>
<body>
<div class="app">
  <div class="sidebar">
    <div class="sidebar-section">
      <h3>Projects</h3>
      <div id="projects-list"></div>
    </div>
    <div class="sidebar-section">
      <h3>Providers</h3>
      <div id="providers-list"></div>
    </div>
    <div class="sidebar-section">
      <h3>Tags</h3>
      <div id="tags-list"></div>
    </div>
  </div>
  <div class="main">
    <div class="search-bar">
      <input type="text" id="search-input" placeholder="Search conversations (natural language or SQL)..." />
    </div>
    <div class="conv-list" id="conv-list"></div>
    <div class="stats-bar">
      <span id="stats-count">Loading...</span>
      <span id="stats-db"></span>
    </div>
  </div>
  <div class="detail" id="detail-view" style="display:none;">
    <div class="detail-header" id="detail-header"></div>
    <div id="detail-turns"></div>
    <div class="related" id="detail-related"></div>
  </div>
</div>
<script>
const API = '';
let conversations = [];
let filters = { provider: null, project: null, tag: null };

async function api(path, opts = {}) {
  const res = await fetch(API + path, opts);
  return res.json();
}

async function loadConversations(params = {}) {
  const qs = new URLSearchParams(params).toString();
  const data = await api('/api/conversations?' + qs);
  conversations = data.conversations || [];
  renderConversations();
  document.getElementById('stats-count').textContent =
    `Showing ${conversations.length} of ${data.total} conversations`;
}

async function loadSidebar() {
  const stats = await api('/api/stats');
  // Projects
  const projHtml = (stats.projects || []).slice(0, 20).map(p =>
    `<div class="provider-check" onclick="filterBy('project','${p.name}')">${p.name} (${p.conversation_count})</div>`
  ).join('');
  document.getElementById('projects-list').innerHTML = projHtml;
  // Providers
  const provHtml = Object.entries(stats.providers || {}).map(([k, v]) =>
    `<div class="provider-check" onclick="filterBy('provider','${k}')">
      <input type="checkbox" checked /> ${k} (${v.conversations})</div>`
  ).join('');
  document.getElementById('providers-list').innerHTML = provHtml;
  // Tags
  const tags = await api('/api/tags');
  const tagHtml = (tags.tags || []).slice(0, 30).map(t =>
    `<span class="tag-pill" onclick="filterBy('tag','${t.tag_name}')">${t.tag_name}</span>`
  ).join('');
  document.getElementById('tags-list').innerHTML = tagHtml;
  document.getElementById('stats-db').textContent = `${stats.db_size_mb?.toFixed(1) || '?'} MB`;
}

function renderConversations() {
  const html = conversations.map(c => {
    const preview = (c.preview?.first_user_turn || '').substring(0, 120);
    const timeAgo = relativeTime(c.created_at);
    return `<div class="conv-item" onclick="showConversation(${c.id})">
      <div class="conv-title">${escapeHtml(c.session_title || 'Untitled')}</div>
      <div class="conv-meta">
        <span>${c.provider}</span>
        <span>${c.project_name || ''}</span>
        <span>${timeAgo}</span>
        <span>${c.turn_count} turns</span>
      </div>
      ${preview ? `<div class="conv-preview">${escapeHtml(preview)}</div>` : ''}
    </div>`;
  }).join('');
  document.getElementById('conv-list').innerHTML = html || '<div style="padding:20px;color:var(--text-dim)">No conversations found</div>';
}

async function showConversation(id) {
  const data = await api('/api/conversations/' + id);
  document.getElementById('conv-list').style.display = 'none';
  document.getElementById('detail-view').style.display = 'block';
  const c = data.conversation;
  const tags = (data.tags || []).map(t =>
    `<span class="tag-pill">${t}</span>`).join('');

  document.getElementById('detail-header').innerHTML = `
    <h2>${escapeHtml(c.session_title || 'Untitled')}</h2>
    <div class="meta">
      <span>${c.provider}</span>
      <span>${c.project_name || ''}</span>
      <span>${c.model_id || ''}</span>
      <span>${c.created_at}</span>
      <span>${c.turn_count} turns</span>
    </div>
    <div class="tags">${tags}</div>
    <div style="margin-top:8px">
      <a href="#" onclick="goBack(); return false;" style="color:var(--accent);font-size:13px">&larr; Back to list</a>
      <a href="#" onclick="findRelated(${id}); return false;" style="color:var(--accent);font-size:13px;margin-left:16px">Find Related</a>
    </div>`;

  const turnsHtml = (data.turns || []).map((t, i) => {
    const isLong = t.char_count > 2000 && t.role === 'assistant';
    const collapsed = isLong ? 'turn-collapsed' : '';
    const content = isLong
      ? (t.content_truncated || t.content_summary || t.content_text.substring(0, 200) + '...')
      : t.content_text;
    const fullBtn = isLong
      ? `<div class="expand-btn" onclick="expandTurn(this, ${t.id})">View Full Response (${t.char_count.toLocaleString()} chars)</div>
         <div class="full-response" id="full-${t.id}">${escapeHtml(t.content_text)}</div>`
      : '';
    return `<div class="turn turn-${t.role} ${collapsed}">
      <div class="turn-role">${t.role === 'user' ? '👤 User' : '🤖 Assistant'}</div>
      <div class="turn-content">${escapeHtml(content)}</div>
      ${fullBtn}
    </div>`;
  }).join('');
  document.getElementById('detail-turns').innerHTML = turnsHtml;
}

function expandTurn(btn, turnId) {
  const full = document.getElementById('full-' + turnId);
  full.classList.toggle('visible');
  btn.textContent = full.classList.contains('visible')
    ? 'Collapse Response' : `View Full Response`;
}

function goBack() {
  document.getElementById('conv-list').style.display = 'block';
  document.getElementById('detail-view').style.display = 'none';
}

async function findRelated(id) {
  const data = await api('/api/conversations/' + id + '/related');
  const html = (data.related || []).map(r =>
    `<div class="related-item" onclick="showConversation(${r.id})">${escapeHtml(r.session_title)} (${r.provider})</div>`
  ).join('');
  document.getElementById('detail-related').innerHTML = `<h4>Related Conversations</h4>` + html;
}

function filterBy(type, value) {
  const params = {};
  if (type === 'provider') params.provider = value;
  if (type === 'project') params.project = value;
  if (type === 'tag') params.tag = value;
  loadConversations(params);
}

// Search
let searchTimeout;
document.getElementById('search-input').addEventListener('input', (e) => {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    const query = e.target.value.trim();
    if (query.startsWith('SELECT')) {
      loadConversations({ sql: query });
    } else if (query) {
      loadConversations({ semantic: query });
    } else {
      loadConversations();
    }
  }, 500);
});

function escapeHtml(text) {
  if (!text) return '';
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function relativeTime(isoStr) {
  if (!isoStr) return '';
  const diff = Date.now() - new Date(isoStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 60) return mins + 'm ago';
  const hours = Math.floor(mins / 60);
  if (hours < 24) return hours + 'h ago';
  const days = Math.floor(hours / 24);
  return days + 'd ago';
}

// Init
loadConversations();
loadSidebar();
</script>
</body>
</html>"""


# ============================================================
# Flask Application
# ============================================================

def create_app(db_path: str = DB_PATH, enable_capture: bool = False):
    """Create and configure the Flask application."""
    try:
        from flask import Flask, request, jsonify, send_from_directory
        from flask_cors import CORS
    except ImportError:
        print("Flask not installed. Install with: pip install flask flask-cors")
        sys.exit(1)

    app = Flask(__name__)
    CORS(app)

    def get_db():
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.row_factory = sqlite3.Row
        return conn

    @app.route("/")
    def index():
        return HTML_TEMPLATE

    @app.route("/api/conversations")
    def list_conversations():
        db = get_db()
        try:
            provider = request.args.get("provider")
            project = request.args.get("project")
            tag = request.args.get("tag")
            semantic = request.args.get("semantic")
            q = request.args.get("q")
            limit = min(int(request.args.get("limit", 50)), 200)
            offset = int(request.args.get("offset", 0))

            # If semantic search requested
            if semantic:
                from rag_pipeline import hybrid_search
                results = hybrid_search(db, semantic, provider=provider, project=project, limit=limit)
                return jsonify({
                    "conversations": results,
                    "total": len(results),
                    "limit": limit,
                    "offset": offset,
                })

            # Build SQL query
            where_clauses = ["c.is_deleted = 0"]
            params = []

            if provider:
                where_clauses.append("c.provider = ?")
                params.append(provider)
            if project:
                where_clauses.append("c.project_name = ?")
                params.append(project)
            if tag:
                where_clauses.append(
                    """c.id IN (SELECT ct.conversation_id FROM conversation_tags ct
                       JOIN tags t ON t.id = ct.tag_id WHERE t.tag_name = ?)"""
                )
                params.append(tag)
            if q:
                where_clauses.append(
                    """c.id IN (SELECT rowid FROM conversation_turns_fts WHERE conversation_turns_fts MATCH ?)"""
                )
                params.append(q)

            where = " AND ".join(where_clauses)

            total = db.execute(
                f"SELECT COUNT(*) FROM conversations c WHERE {where}", params
            ).fetchone()[0]

            rows = db.execute(
                f"""SELECT c.* FROM conversations c
                    WHERE {where}
                    ORDER BY c.created_at DESC
                    LIMIT ? OFFSET ?""",
                params + [limit, offset],
            ).fetchall()

            conversations = []
            for r in rows:
                # Get first user turn preview
                first_user = db.execute(
                    """SELECT content_text FROM conversation_turns
                       WHERE conversation_id = ? AND role = 'user'
                       ORDER BY turn_index LIMIT 1""",
                    (r["id"],),
                ).fetchone()

                first_summary = db.execute(
                    """SELECT content_summary FROM conversation_turns
                       WHERE conversation_id = ? AND role = 'assistant' AND content_summary IS NOT NULL
                       ORDER BY turn_index LIMIT 1""",
                    (r["id"],),
                ).fetchone()

                conv_tags = db.execute(
                    """SELECT t.tag_name FROM tags t
                       JOIN conversation_tags ct ON ct.tag_id = t.id
                       WHERE ct.conversation_id = ?""",
                    (r["id"],),
                ).fetchall()

                conversations.append({
                    "id": r["id"],
                    "provider": r["provider"],
                    "session_id": r["session_id"],
                    "session_title": r["session_title"],
                    "project_name": r["project_name"],
                    "model_id": r["model_id"],
                    "turn_count": r["turn_count"],
                    "user_turn_count": r["user_turn_count"],
                    "total_chars": r["total_chars"],
                    "created_at": r["created_at"],
                    "updated_at": r["updated_at"],
                    "tags": [t[0] for t in conv_tags],
                    "preview": {
                        "first_user_turn": first_user["content_text"][:200] if first_user else None,
                        "first_assistant_summary": first_summary["content_summary"] if first_summary else None,
                    },
                })

            return jsonify({
                "conversations": conversations,
                "total": total,
                "limit": limit,
                "offset": offset,
            })
        finally:
            db.close()

    @app.route("/api/conversations/<int:conv_id>")
    def get_conversation(conv_id):
        db = get_db()
        try:
            conv = db.execute(
                "SELECT * FROM conversations WHERE id = ?", (conv_id,)
            ).fetchone()

            if not conv:
                return jsonify({"error": "Not found"}), 404

            turns = db.execute(
                """SELECT id, turn_index, role, content_text, content_summary,
                          content_truncated, model_id, char_count, created_at
                   FROM conversation_turns
                   WHERE conversation_id = ?
                   ORDER BY turn_index""",
                (conv_id,),
            ).fetchall()

            tags = db.execute(
                """SELECT t.tag_name FROM tags t
                   JOIN conversation_tags ct ON ct.tag_id = t.id
                   WHERE ct.conversation_id = ?""",
                (conv_id,),
            ).fetchall()

            return jsonify({
                "conversation": dict(conv),
                "turns": [dict(t) for t in turns],
                "tags": [t[0] for t in tags],
            })
        finally:
            db.close()

    @app.route("/api/conversations/<int:conv_id>/related")
    def get_related(conv_id):
        db = get_db()
        try:
            from rag_pipeline import find_related
            related = find_related(db, conv_id, limit=10)
            return jsonify({"related": related})
        finally:
            db.close()

    @app.route("/api/tags")
    def list_tags():
        db = get_db()
        try:
            tags = db.execute(
                "SELECT t.*, COUNT(ct.conversation_id) as usage_count FROM tags t "
                "LEFT JOIN conversation_tags ct ON ct.tag_id = t.id "
                "GROUP BY t.id ORDER BY usage_count DESC"
            ).fetchall()
            return jsonify({"tags": [dict(t) for t in tags]})
        finally:
            db.close()

    @app.route("/api/stats")
    def get_stats():
        db = get_db()
        try:
            total_convs = db.execute(
                "SELECT COUNT(*) FROM conversations WHERE is_deleted = 0"
            ).fetchone()[0]
            total_turns = db.execute("SELECT COUNT(*) FROM conversation_turns").fetchone()[0]

            providers = {}
            for row in db.execute(
                "SELECT provider, COUNT(*) as cnt FROM conversations WHERE is_deleted = 0 GROUP BY provider"
            ).fetchall():
                providers[row["provider"]] = {"conversations": row["cnt"]}

            projects = [
                {"name": r["project_name"], "conversation_count": r["cnt"]}
                for r in db.execute(
                    "SELECT project_name, COUNT(*) as cnt FROM conversations "
                    "WHERE is_deleted = 0 AND project_name IS NOT NULL "
                    "GROUP BY project_name ORDER BY cnt DESC"
                ).fetchall()
            ]

            db_size_mb = os.path.getsize(db_path) / (1024 * 1024) if os.path.exists(db_path) else 0

            return jsonify({
                "total_conversations": total_convs,
                "total_turns": total_turns,
                "providers": providers,
                "projects": projects,
                "db_size_mb": db_size_mb,
            })
        finally:
            db.close()

    # Capture API for Tampermonkey scripts
    if enable_capture:
        @app.route("/api/capture", methods=["POST"])
        def capture():
            data = request.json
            provider = data.get("provider", "browser-capture")
            session_id = data.get("session_id", f"browser-{datetime.now(timezone.utc).timestamp()}")
            session_title = data.get("session_title", "Browser Capture")
            turns = data.get("turns", [])

            if not turns:
                return jsonify({"status": "ok", "turns_stored": 0}), 200

            db = get_db()
            try:
                # Upsert conversation
                existing = db.execute(
                    "SELECT id FROM conversations WHERE provider = ? AND session_id = ?",
                    (provider, session_id),
                ).fetchone()

                if existing:
                    conv_id = existing["id"]
                    # Update existing - add new turns only
                    max_idx = db.execute(
                        "SELECT MAX(turn_index) FROM conversation_turns WHERE conversation_id = ?",
                        (conv_id,),
                    ).fetchone()[0] or 0

                    stored = 0
                    for i, turn in enumerate(turns):
                        idx = max_idx + i + 1
                        content_text = turn.get("content_text", "")
                        char_count = len(content_text)

                        # Check if this turn already exists (by content similarity)
                        existing_turn = db.execute(
                            """SELECT id FROM conversation_turns
                               WHERE conversation_id = ? AND role = ?
                               AND content_text = ? LIMIT 1""",
                            (conv_id, turn.get("role"), content_text),
                        ).fetchone()

                        if existing_turn:
                            continue

                        db.execute(
                            """INSERT INTO conversation_turns
                                (conversation_id, turn_index, role, content_text,
                                 model_id, char_count, token_estimate, created_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                            (conv_id, idx, turn.get("role"), content_text,
                             turn.get("model_id"), char_count, char_count // 4,
                             turn.get("created_at", datetime.now(timezone.utc).isoformat())),
                        )
                        stored += 1

                    db.execute(
                        """UPDATE conversations SET
                            turn_count = (SELECT COUNT(*) FROM conversation_turns WHERE conversation_id = ?),
                            updated_at = strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
                        WHERE id = ?""",
                        (conv_id, conv_id),
                    )
                else:
                    now = datetime.now(timezone.utc).isoformat()
                    cursor = db.execute(
                        """INSERT INTO conversations
                            (provider, session_id, session_title, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?)""",
                        (provider, session_id, session_title, now, now),
                    )
                    conv_id = cursor.lastrowid

                    stored = 0
                    for i, turn in enumerate(turns):
                        content_text = turn.get("content_text", "")
                        char_count = len(content_text)

                        db.execute(
                            """INSERT INTO conversation_turns
                                (conversation_id, turn_index, role, content_text,
                                 model_id, char_count, token_estimate, created_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                            (conv_id, i, turn.get("role"), content_text,
                             turn.get("model_id"), char_count, char_count // 4,
                             turn.get("created_at", now)),
                        )
                        stored += 1

                    db.execute(
                        """UPDATE conversations SET
                            turn_count = ?,
                            user_turn_count = (SELECT COUNT(*) FROM conversation_turns WHERE conversation_id = ? AND role = 'user'),
                            total_chars = (SELECT COALESCE(SUM(char_count), 0) FROM conversation_turns WHERE conversation_id = ?),
                            ingested_at = strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
                        WHERE id = ?""",
                        (stored, conv_id, conv_id, conv_id),
                    )

                db.commit()
                return jsonify({"status": "ok", "turns_stored": stored}), 201

            except Exception as e:
                db.rollback()
                return jsonify({"status": "error", "message": str(e)}), 500
            finally:
                db.close()

        @app.route("/api/capture/status")
        def capture_status():
            return jsonify({"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()})

    return app


def main():
    parser = argparse.ArgumentParser(description="Prompt Mine Web Server")
    parser.add_argument("--port", type=int, default=8420)
    parser.add_argument("--enable-capture-api", action="store_true",
                        help="Enable the capture API for Tampermonkey scripts")
    parser.add_argument("--db-path", default=DB_PATH)
    args = parser.parse_args()

    if not os.path.exists(args.db_path):
        print(f"Database not found at {args.db_path}")
        print("Run init_database.py first.")
        sys.exit(1)

    app = create_app(args.db_path, args.enable_capture_api)
    print(f"Starting Prompt Mine web server on http://localhost:{args.port}")
    if args.enable_capture_api:
        print("Capture API enabled — Tampermonkey scripts can POST to /api/capture")
    app.run(host="0.0.0.0", port=args.port, debug=False)


if __name__ == "__main__":
    main()
