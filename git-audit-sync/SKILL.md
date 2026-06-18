---
name: git-audit-sync
description: Automatically audit, commit, push, and pull every git repo in a directory tree. Detects uncommitted work, ahead/behind status, merge conflicts, active rebase/merge states, detached HEAD, and non-main branches. Handles trivial merges automatically and flags conflicts for user review. Use when asked to sync git repos, audit code folders, push/pull all projects, check for uncommitted work, or prepare a machine's git state.
---

# Git Audit & Sync

Audits every git repo in a folder and brings them to a clean, synced state.

## Workflow

1. Run the automation script (see [scripts/audit_sync.py](scripts/audit_sync.py))
2. Read the report it generates to the user
3. For any flagged repos, show the details and ask for instructions

## After Running

After the script finishes, do the following for the user:

1. **Read** `~/git-audit-logs/git-audit-<timestamp>.md` and present the Summary table
2. **For ✅ Clean repos**: Just note the count — no action needed
3. **For ⏩ Pulled / 📤 Pushed / 💾 Committed / 🔄 Synced repos**: Mention what happened and any notable commit counts
4. **For ⚠️ Conflict repos**: Show the conflicting files and diffs, then ask the user how to proceed on each
5. **For ⏭️ Skipped repos**: Explain why (in-progress merge, non-main branch, detached HEAD)

If there are no conflicts, summarize the result as "X repos processed, all clean."

## Decision Tree

```
                    ┌──────────────────┐
                    │  Check for merge │
                    │  /rebase/cherry- │
                    │  pick in progress│
                    └──────┬───────────┘
                           │
                    ┌──────▼───────────┐
                    │  1. Fetch each   │
                    │     repo         │
                    └──────┬───────────┘
                           │
                    ┌──────▼───────────┐
                    │  2. Classify     │
                    │     state        │
                    └──────┬───────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   Active op          Has origin          No origin
   (merge, etc.)      + upstream          or upstream
        │                  │                  │
   ⏭️ Skip, warn     ┌──────▼──────┐    Dirty?→ commit&push
        │           │  Compare    │    Clean? → ✅ skip
        │           │  local vs   │
        │           │  upstream   │
        │           └──────┬──────┘
        │                  │
        │      ┌───────────┼───────────┐
        │      │           │           │
        │  Clean       Dirty       Dirty +
        │  behind      ahead       diverged
        │  (pullable)  (pushable)  (behind
        │      │           │       +ahead)
        │  pull --ff-  push      ┌──────┘
        │  only                  │
        │              ┌─────────┴────────┐
        │              │                  │
        │         Same files        Different files
        │         changed?          changed?
        │              │                  │
        │         ⚠️ Flag for        commit → push
        │         user review        → pull (auto)
        │
        └──────────────── Non-main branch?
                           Yes → ⏭️ Skip (WIP)
                           No  → process normally
```

## Repo States & Actions

| State | Uncommitted | vs Upstream | Branch | Action |
|---|---|---|---|---|
| **Clean** | 0 | even | any | ✅ Skip — nothing to do |
| **Pullable** | 0 | behind | any | `git pull --ff-only` |
| **Pushable** | 0 | ahead | any | `git push` |
| **Local work** | >0 | even | main/master | Stage all → commit → push |
| **Local work** | >0 | even | other | ⏭️ Skip — WIP on feature branch |
| **Diverged** | >0 | behind | main/master | Commit → push → pull |
| **Diverged** | >0 | behind | other | ⏭️ Skip — WIP on feature branch |
| **Conflict risk** | >0 | ahead+behind | main/master | Check file overlap → auto-merge or flag |
| **No upstream** | any | n/a | any | Push with `--set-upstream` or skip if detached |
| **In progress** | any | any | any | ⏭️ Skip — active merge/rebase/cherry-pick |
| **Error** | any | any | any | Report error and continue |

## Rollback Safety

Before any write operation, the script creates a backup tag:
```
git-audit-sync/backup-YYYYMMDD-HHMMSS-<reponame>
```

Restore with:
```bash
# Creates a branch from the tag so you're not in detached HEAD
git switch -c recovery-<reponame> git-audit-sync/backup-YYYYMMDD-HHMMSS-<reponame>
```

## Known Limitations

- **Binary files**: The script cannot detect or merge binary file conflicts. If a `.png`, `.ico`, or other binary file diverges, git's native merge will report the conflict.
- **Detached HEAD**: If a repo is in detached HEAD state, the script reports it and skips it. Run `git switch <branch>` first.
- **Active operations**: If a merge, rebase, cherry-pick, or revert is in progress, the script skips the repo and reports it.
- **Large binary files in history**: The script is not designed for repos with large binary files or LFS-managed assets.
- **Pre-commit hooks**: The script does not trigger pre-commit hooks during auto-commit. If hooks are configured, run `git commit` manually.

## Automation Script

The core logic is in [scripts/audit_sync.py](scripts/audit_sync.py). It handles all repo states deterministically and processes repos in **parallel** using independent worker threads — each repo has its own `.git` so no shared state or conflict is possible.

**Repo discovery**: Recursively walks the target directory tree (skipping `node_modules`, `.cache`, `venv`, build artifacts). Finds repos at any nesting depth — not just direct children.

### Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--workers N` | `min(8, cpu_count)` | Number of parallel workers. Each gets its own repos — zero shared state. |
| `--since N` | all | Only process repos modified in the last N days (checks `.git` mtime). |
| `--exclude repo1,repo2` | none | Comma or space-separated repo names to skip. |
| `--maxdepth N` | 3 | Max directory depth for recursive repo discovery. |
| `--commit-message "msg"` | `git-audit-sync: auto-commit` | Custom commit message for auto-commits. |
| `--update-submodules` | off | Run `git submodule update --recursive` after pull. |
| `--audit-only` | off | Read-only audit — no changes made. |
| `--dry-run` | off | Simulate all operations without making changes. |

```bash
# Full sync (8 workers in parallel)
python3 scripts/audit_sync.py ~/code

# Read-only audit
python3 scripts/audit_sync.py ~/code --audit-only

# Dry run (show what would happen)
python3 scripts/audit_sync.py ~/code --dry-run

# Fast parallel scan with 12 workers, skip old repos
python3 scripts/audit_sync.py ~/code --workers 12 --since 30

# Skip specific repos
python3 scripts/audit_sync.py ~/code --exclude whisper.cpp,agents

# Custom commit message + update submodules
python3 scripts/audit_sync.py ~/code --commit-message "chore: sync" --update-submodules
```

### Parallel workers (sub-agent pattern)

Each repo is dispatched to an independent worker thread. Workers don't share state — each has its own `GitRepo` object and writes results back through a thread-safe collector. This design:

- **Scales linearly** with CPU count — 20 repos on 8 workers finishes in ~3 batches
- **Eliminates conflict risk** — no two workers touch the same `.git`
- **Preserves ordering** — results are merged in completion order, then sorted by severity
- **Survives crashes** — one repo failing doesn't block the rest

## Output

Creates a timestamped report at `~/git-audit-logs/` — both markdown (human) and JSON (machine):
```
📊 Report: ~/git-audit-logs/git-audit-2026-06-17-192525.md

# Git Audit — /home/user/code
## Summary
| Stat | Count |
|------|-------|
| ✅ Clean / up-to-date | 8 |
| ⏩ Pulled | 2 |
| 💾 Committed + pushed | 1 |
| ⚠️ Conflicts | 1 |
| ⏭️ Skipped | 1 |
| **Health** | **89%** |

## Per-repo results
- ✅ surface-fixed-event-quell — clean, up-to-date
- ⏩ wiki-memory — pulled (3 commits ff-only)
- 💾 voice-agent — committed + pushed (6 files)
- ⚠️ aaa-memory — DIVERGED in same files: src/config.py. Needs review.
- ⏭️ AutoResearchClaw — active merge in progress (skipped)
```

## Cases that always need user input

- **Uncommitted work on a non-main branch** — may be work-in-progress, won't auto-commit
- **Same-file divergence between local and upstream** — flagged for review with file list
- **Binary file conflicts** — can't auto-merge
- **Active merge/rebase/cherry-pick** — skipped, user must resolve first
- **Detached HEAD** — skipped, user must `git switch <branch>` first
