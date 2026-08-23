-- intent-archaeology SQLite schema (v1.1.0)
-- Idempotent: safe to re-run.

CREATE TABLE IF NOT EXISTS schema_version (
  version TEXT PRIMARY KEY,
  applied_at TEXT NOT NULL DEFAULT (datetime('now'))
);

INSERT OR IGNORE INTO schema_version (version) VALUES ('1.1.0');

CREATE TABLE IF NOT EXISTS projects (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE,
  path TEXT NOT NULL,
  description TEXT,
  github_url TEXT,
  era INTEGER,                       -- 0..5, see references/era_typology.md
  era_overlap TEXT,                  -- JSON list of other eras' markers found
  derived_lifecycle TEXT,            -- proposed state, see references/lifecycle_states.md
  lifecycle_confidence REAL,         -- 0.0..1.0
  lifecycle_evidence TEXT,           -- JSON list
  lifecycle TEXT,                    -- confirmed state ('proposed' if not yet confirmed)
  canonical_prd_path TEXT,
  spec_lineage TEXT,                 -- JSON list of {path, role, attached_at}
  last_audited TEXT,
  metadata TEXT,                     -- JSON for extensible fields
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_projects_lifecycle ON projects(lifecycle);
CREATE INDEX IF NOT EXISTS idx_projects_era ON projects(era);

CREATE TABLE IF NOT EXISTS tranches (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  scope_hash TEXT NOT NULL,
  scope_json TEXT NOT NULL,          -- serialized ScopeSpec
  started_at TEXT NOT NULL DEFAULT (datetime('now')),
  completed_at TEXT,
  status TEXT NOT NULL DEFAULT 'in-progress',  -- in-progress|completed|failed
  notes TEXT,
  UNIQUE(scope_hash, started_at)
);

CREATE TABLE IF NOT EXISTS prompts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tranche_id INTEGER NOT NULL REFERENCES tranches(id),
  project_id INTEGER REFERENCES projects(id),
  source_path TEXT NOT NULL,         -- raw JSONL path
  line_number INTEGER NOT NULL,
  agent TEXT NOT NULL,               -- claude|codex|cursor|gemini|aider|chatgpt
  workspace TEXT,
  created_at TEXT NOT NULL,          -- session timestamp
  prompt_text TEXT NOT NULL,
  is_human BOOLEAN NOT NULL,
  source TEXT NOT NULL DEFAULT 'cass+jsonl',  -- 'cass+jsonl' or 'cass-only'
  parent_uuid TEXT,                  -- for rewind/edited turn detection
  UNIQUE(source_path, line_number)
);

CREATE INDEX IF NOT EXISTS idx_prompts_tranche ON prompts(tranche_id);
CREATE INDEX IF NOT EXISTS idx_prompts_project ON prompts(project_id);
CREATE INDEX IF NOT EXISTS idx_prompts_agent ON prompts(agent);
CREATE INDEX IF NOT EXISTS idx_prompts_created ON prompts(created_at);

CREATE TABLE IF NOT EXISTS prompt_audit_fields (
  prompt_id INTEGER PRIMARY KEY REFERENCES prompts(id),
  source_path TEXT NOT NULL,
  line_number INTEGER NOT NULL,
  is_sidechain BOOLEAN NOT NULL,
  git_branch TEXT,
  parent_uuid TEXT,
  tool_use_result_json TEXT,
  FOREIGN KEY (source_path, line_number) REFERENCES prompts(source_path, line_number)
);

CREATE TABLE IF NOT EXISTS intents (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  prompt_id INTEGER NOT NULL REFERENCES prompts(id),
  tranche_id INTEGER NOT NULL REFERENCES tranches(id),
  project_id INTEGER REFERENCES projects(id),
  type TEXT NOT NULL,                -- closed vocab, see references/intent_taxonomy.md
  summary TEXT NOT NULL,
  superseded_by INTEGER REFERENCES intents(id),
  taxonomy_version TEXT NOT NULL DEFAULT '1.0',
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_intents_prompt ON intents(prompt_id);
CREATE INDEX IF NOT EXISTS idx_intents_type ON intents(type);
CREATE INDEX IF NOT EXISTS idx_intents_project ON intents(project_id);
CREATE INDEX IF NOT EXISTS idx_intents_superseded ON intents(superseded_by);

CREATE TABLE IF NOT EXISTS status_vectors (
  project_id INTEGER PRIMARY KEY REFERENCES projects(id),
  tranche_id INTEGER NOT NULL REFERENCES tranches(id),
  completed REAL NOT NULL,
  in_progress REAL NOT NULL,
  drifted REAL NOT NULL,
  superseded REAL NOT NULL,
  abandoned REAL NOT NULL,
  not_begun REAL NOT NULL,
  -- CHECK constraint: components sum to ~1.0 (allow float epsilon)
  CHECK (ABS(completed + in_progress + drifted + superseded + abandoned + not_begun - 1.0) < 0.001),
  computed_at TEXT NOT NULL DEFAULT (datetime('now')),
  UNIQUE(project_id, tranche_id)
);

CREATE TABLE IF NOT EXISTS observations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tranche_id INTEGER NOT NULL REFERENCES tranches(id),
  question_id TEXT NOT NULL,         -- e.g. 'Q1', 'Q2' from retrospective.md
  observation TEXT NOT NULL,
  severity TEXT,                     -- info|warning|critical
  proposed_edit TEXT,                -- path to diff file in proposed_edits/
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS proposed_edits (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tranche_id INTEGER NOT NULL REFERENCES tranches(id),
  diff_path TEXT NOT NULL,
  held_out_score_before REAL,
  held_out_score_after REAL,
  accepted BOOLEAN NOT NULL DEFAULT 0,
  accepted_at TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- scope_hash is sha256 of the JSON-serialized ScopeSpec
-- (see scripts/lib/scope.py)
