---
name: git-audit-sync
description: Automatically audit, commit, push, and pull every git repo in a directory tree. Detects uncommitted work, ahead/behind status, merge conflicts, and non-main branches. Handles trivial merges automatically and flags conflicts for user review. Use when asked to sync git repos, audit code folders, push/pull all projects, check for uncommitted work, or prepare a machine's git state.
---

# Git Audit & Sync

Audits every git repo in a folder and brings them to a clean, synced state.

## Workflow

1. Run the automation script (see [scripts/audit_sync.py](scripts/audit_sync.py))
2. Review the report it generates
3. Address any flagged conflicts manually

## Decision Tree

```
                    ┌──────────────┐
                    │  Fetch each  │
                    │    repo      │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │  Check state │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
         Clean +      Dirty +      Dirty +
         behind       ahead        diverged
              │            │            │
         pull --ff-only  commit &    flag for
                          push       review
```

## Repo States & Actions

| State | Uncommitted | vs Upstream | Action | Script method |
|---|---|---|---|---|
| **Clean** | 0 | even | ✅ skip | `.report()` |
| **Pullable** | 0 | behind | `git pull --ff-only` | `.pull_ff()` |
| **Pushable** | 0 | ahead | `git push` | `.push()` |
| **Local work** | >0 | even | commit → push | `.commit_push()` |
| **Diverged** | >0 | behind | commit → push → pull | `.commit_push_pull()` |
| **Conflict** | >0 | ahead+behind | assess → auto-resolve or flag | `.assess_conflict()` |
| **Feature branch** | any | no upstream | push with `--set-upstream` | `.push_upstream()` |

### Rollback Safety

Before any write operation, the script creates a lightweight tag:
```
git-audit-sync/backup-YYYYMMDD-HHMMSS-<reponame>
```

Restore with:
```bash
git checkout git-audit-sync/backup-YYYYMMDD-HHMMSS-<reponame>
```

### Conflict Assessment

The script classifies conflicts into two tiers:

- **Auto-resolve**: Changes touch different files, or only data/generated files (`.json`, `.csv`, `.db`, `lockfiles`) — the script chooses upstream or local based on file modification time
- **Needs user**: Same source files changed in both — creates backup tag and reports the conflicting files with diffs

## Automation Script

The core logic is in [scripts/audit_sync.py](scripts/audit_sync.py). It handles all repo states deterministically.

```bash
# Full sync (commit, push, pull)
python3 scripts/audit_sync.py ~/code

# Read-only audit (no changes)
python3 scripts/audit_sync.py ~/code --audit-only

# Dry run (show what would happen)
python3 scripts/audit_sync.py ~/code --dry-run

# Skip specific repos
python3 scripts/audit_sync.py ~/code --exclude whisper.cpp,agents
```

## Output

Creates a timestamped report at `~/git-audit-logs/`:
```
git-audit-2026-06-17-190000.md
├── ✅ surface-quell — clean, up-to-date
├── ⏩ wiki-memory — pulled (3 commits ff-only)
├── 💾 voice-agent — committed + pushed (6 files)
├── ⚠️  claude-code-proxy-old — CONFLICT: src/config.py
├── 📊 12 repos: 8 clean, 2 updated, 1 pushed, 1 conflict
```

## Cases that always need user input

- **Uncommitted work on a non-main branch** — may be work-in-progress, won't auto-commit
- **Binary file conflicts** — can't auto-merge
- **Merge conflicts after pull** — `--ff-only` fails safely, leaves repo untouched
