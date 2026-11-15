-- Intent Archaeology schema. Derived tables only.
-- Human judgment lives in files under human/, never here.

PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS meta (
    key         TEXT PRIMARY KEY,
    value       TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS project (
    id                  TEXT PRIMARY KEY,      -- stable slug
    path                TEXT NOT NULL,
    root                TEXT NOT NULL,         -- which scan root it came from
    kind                TEXT NOT NULL,         -- project | container | monorepo | unclassified
    parent_id           TEXT REFERENCES project(id),
    git_remote          TEXT,
    git_initial_sha     TEXT,
    manifest            TEXT,                  -- package.json, Cargo.toml, ...
    has_git             INTEGER NOT NULL DEFAULT 0,
    source_files        INTEGER NOT NULL DEFAULT 0,
    last_commit_ts      TEXT,
    last_mtime          TEXT,
    description         TEXT,
    description_sources TEXT,                  -- JSON: each candidate + its mtime
    description_stale   INTEGER,
    thesis              TEXT,
    lifecycle           TEXT,                  -- not-started|in-progress|complete|revision|archive-candidate
    lifecycle_evidence  TEXT,                  -- JSON of the signals used
    lifecycle_confirmed INTEGER NOT NULL DEFAULT 0,
    doc_era             INTEGER,               -- 1..5, see references/spec-archaeology.md
    pipeline_version    TEXT NOT NULL,
    created_at          TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_project_kind ON project(kind);

CREATE TABLE IF NOT EXISTS session (
    id                     TEXT PRIMARY KEY,   -- harness:session_id
    harness                TEXT NOT NULL,
    harness_session_id     TEXT,
    source_path            TEXT NOT NULL,
    workspace              TEXT,
    first_ts               TEXT,
    last_ts                TEXT,
    message_count          INTEGER,
    project_id             TEXT REFERENCES project(id),
    attribution_method     TEXT,               -- rung name
    attribution_rung       INTEGER,            -- 1..6
    attribution_confidence REAL,
    enriched               INTEGER NOT NULL DEFAULT 0,
    crashed                INTEGER,            -- ended mid tool call
    pipeline_version       TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_session_project ON session(project_id);
CREATE INDEX IF NOT EXISTS idx_session_enriched ON session(enriched);

CREATE TABLE IF NOT EXISTS event (
    id                TEXT PRIMARY KEY,        -- evt_<hash>
    session_id        TEXT NOT NULL REFERENCES session(id),
    project_id        TEXT REFERENCES project(id),
    parent_event_id   TEXT,
    seq               INTEGER NOT NULL,
    ts                TEXT,
    role              TEXT,                    -- user|assistant|tool|system
    is_human          INTEGER NOT NULL,        -- computed, never inferred at query time
    is_sidechain      INTEGER,
    is_meta           INTEGER,
    text              TEXT,
    text_hash         TEXT,
    char_len          INTEGER,
    cwd               TEXT,
    git_branch        TEXT,
    tool_name         TEXT,
    paths_touched     TEXT,                    -- JSON array
    slash_command     TEXT,
    slash_args        TEXT,
    redactions        TEXT,                    -- JSON array of pattern ids
    pipeline_version  TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_event_session ON event(session_id);
CREATE INDEX IF NOT EXISTS idx_event_project_human ON event(project_id, is_human);
CREATE INDEX IF NOT EXISTS idx_event_hash ON event(text_hash);
CREATE INDEX IF NOT EXISTS idx_event_slash ON event(slash_command);

CREATE TABLE IF NOT EXISTS intent (
    id                TEXT PRIMARY KEY,
    project_id        TEXT NOT NULL REFERENCES project(id),
    type              TEXT NOT NULL,
    statement         TEXT NOT NULL,
    verbatim          TEXT NOT NULL,           -- immutable. never updated.
    scope             TEXT,
    status            TEXT,                    -- see references/lifecycle.md
    drift_type        TEXT,                    -- orthogonal to status
    superseded_by     TEXT REFERENCES intent(id),
    first_ts          TEXT,
    last_ts           TEXT,
    occurrences       INTEGER NOT NULL DEFAULT 1,
    confidence        REAL,
    spec_context_id   TEXT,
    provisional       INTEGER NOT NULL DEFAULT 0,
    tranche           INTEGER,
    pipeline_version  TEXT NOT NULL,
    created_at        TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_intent_project ON intent(project_id);
CREATE INDEX IF NOT EXISTS idx_intent_type ON intent(type);
CREATE INDEX IF NOT EXISTS idx_intent_status ON intent(status);

CREATE TABLE IF NOT EXISTS intent_event (
    intent_id  TEXT NOT NULL REFERENCES intent(id),
    event_id   TEXT NOT NULL REFERENCES event(id),
    PRIMARY KEY (intent_id, event_id)
);

CREATE TABLE IF NOT EXISTS spec_doc (
    id                TEXT PRIMARY KEY,
    project_id        TEXT NOT NULL REFERENCES project(id),
    path              TEXT NOT NULL,
    kind              TEXT,                    -- prd|requirements|design|plan|tasks|constitution|livingdoc
    era               INTEGER,
    content_hash      TEXT NOT NULL,
    mtime             TEXT,
    git_sha           TEXT,
    used_at_spec_time INTEGER NOT NULL DEFAULT 0,
    evidence          TEXT,                    -- JSON: how we know
    pipeline_version  TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_specdoc_project ON spec_doc(project_id);

CREATE TABLE IF NOT EXISTS batch (
    id                TEXT PRIMARY KEY,
    project_id        TEXT REFERENCES project(id),
    tranche           INTEGER,
    item_count        INTEGER NOT NULL,
    emitted_at        TEXT NOT NULL,
    merged_at         TEXT,
    ids_submitted     INTEGER,
    ids_returned      INTEGER,
    pipeline_version  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS batch_item (
    batch_id  TEXT NOT NULL REFERENCES batch(id),
    event_id  TEXT NOT NULL REFERENCES event(id),
    verdict   TEXT,                            -- JSON, null until merged
    PRIMARY KEY (batch_id, event_id)
);

CREATE TABLE IF NOT EXISTS observation (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    ts                TEXT NOT NULL,
    kind              TEXT NOT NULL,
    detail            TEXT,
    event_ids         TEXT,
    tranche           INTEGER,
    pipeline_version  TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_obs_kind ON observation(kind);

CREATE TABLE IF NOT EXISTS run_log (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    ts         TEXT NOT NULL,
    phase      TEXT NOT NULL,
    status     TEXT NOT NULL,
    detail     TEXT
);
