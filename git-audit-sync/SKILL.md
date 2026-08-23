---
name: git-audit-sync
description: Audit every git repo in a directory tree and make each one current with its cloud remote. The script performs only operations that cannot break a repo or lose work (fast-forward pull, push to a remote you own); everything needing judgment — commits, merges, rebases, conflicts, missing or foreign push destinations — is flagged for the agent to resolve. Use when asked to sync git repos, audit code folders, push all projects to the cloud, check for uncommitted work, or prepare a machine's git state.
---

## Purpose: Back Up YOUR Work Off This Machine

The point of this skill is to make **your own** GitHub account current with every committed change on this laptop, so the laptop itself stops being a single point of failure. If the machine is lost, stolen, crashes, or the drive dies, everything that was pushed is recoverable from the cloud. That is why the scope is exact:

> Only repos whose `origin` is owned by you (verified against your `gh` / `git config` GitHub username) are eligible to be pushed. The script enforces this; the agent must also never push to a repo you do not own. A flag `NEEDS INPUT: origin not owned by you` is **not** a task — it means "leave this repo as-is." Do not fork, re-point, or push it unless the user explicitly says to.

# Git Audit & Sync
clean fast-forwards pulled down, end state nothing pending. The work is split:

- **The script** does only what is provably safe: `git pull --ff-only` and
  `git push` to a remote you own. It never commits, merges, rebases, forces, or
  pushes to a repo that isn't yours. A safe op that can't apply cleanly is left
  untouched and flagged.
- **The agent (you)** clears up everything the script flags — reviewing and
  committing uncommitted work, reconciling divergence, resolving simple
  conflicts, and asking the user when there is no valid destination.

This division is deliberate: the script is never given the power to break a repo
or do the wrong thing. All judgment lives with the agent.

## Workflow

1. Run the script: `repo <dir>` (or `python3 scripts/audit_sync.py <dir>`).
2. Read the report at `~/git-audit-logs/git-audit-<timestamp>.md` (+ `.json`).
3. Present the summary, then **handle each flagged repo yourself** (see below).

## Handling flagged repos (the agent's job)

The script tags each repo it won't touch. For each:

| Flag | Meaning | What you do |
|---|---|---|
| `⚠️ NEEDS AGENT: uncommitted…` | Local uncommitted work | Inspect the diff. Check for secrets, accidental deletions, and junk/build artifacts. Commit only what belongs, with a real message, then push. Never blind `git add -A`. |
| `⚠️ NEEDS AGENT: <N> unpushed…` | Committed but not pushed | Push if origin is yours; otherwise treat as the foreign-origin case below. |
| `⚠️ NEEDS AGENT: diverged…` | Behind **and** ahead | Read `git diff HEAD..@{u}`. If the changes don't overlap, integrate (ff/rebase) and push. If they overlap, resolve the conflict **keeping all functionality** — find the reason for the conflict before editing; never delete to clear it. Ask if non-trivial. |
| `⚠️ NEEDS AGENT: not a fast-forward…` | Clean but diverged from remote | Same as diverged — reconcile, don't force. |
| `⚠️ NEEDS INPUT: origin not owned by you` | Push target is someone else's repo | **Ask the user.** Never push to a repo that isn't theirs. Offer: fork to their account and push there, or leave local-only. |
| `⚠️ NEEDS INPUT: no remote / nowhere to push` | No destination | Ask the user where it should go (add a remote they own), or confirm it stays local. |
| `❌ remote not found` | Origin deleted/renamed (404) | Ask whether to repoint or remove the remote. Never auto-remove a remote. |
| `⏭️ active merge/rebase in progress` | Repo mid-operation | Finish or abort the operation with the user, then re-run. |
| `secrets`/`untracked` in detail | Hints attached to the result | Use them: don't commit secrets; decide per-file whether untracked artifacts belong. |

If the script reports no flags: "X repos processed, all current — nothing to do."

## What the script does on its own (safe states only)

| State | Condition | Script action |
|---|---|---|
| **Clean** | even, no uncommitted | nothing |
| **Pullable** | clean, behind | `git pull --ff-only` (refuses if not a clean fast-forward) |
| **Pushable** | clean, ahead, **origin owned** | `git push` (no force; a rejected push changes nothing) |
| **No upstream / no remote, nothing pending** | clean | nothing (reported clean) |
| Anything else | — | **flagged for the agent — no changes made** |

Ownership is verified against your GitHub username (auto-detected via `gh api
user`, then `git config github.user`; override with `--github-user`). If origin
isn't yours, the script does **not** push and flags `NEEDS INPUT`.

## Installation

The `repo` command is a thin wrapper at [bin/repo](bin/repo). Install it onto
PATH with [install.sh](install.sh), which symlinks `~/.local/bin/repo` to the
tracked wrapper so script and wrapper updates are picked up automatically:

```bash
bash install.sh            # installs to ~/.local/bin/repo
bash install.sh /usr/local/bin   # or a custom dir
```

## Automation Script

The core logic is in [scripts/audit_sync.py](scripts/audit_sync.py). It inspects
and classifies every repo, then performs only the two safe operations above, in
**parallel** across independent worker threads — each repo has its own `.git`, so
there is no shared state. The script writes **nothing** into the repos themselves
(not even a plan file — that would dirty the tree); all actionable detail lives in
the report.

**Repo discovery**: recursively walks the tree (skipping `node_modules`,
`.cache`, `venv`, build artifacts), finding repos at any nesting depth.

### Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--workers N` | `min(16, cpu*2)` | Parallel workers. Each gets its own repos — zero shared state. |
| `--since-days N` | all | Only process repos modified in the last N days (`.git` mtime). |
| `--exclude r1,r2` | none | Comma/space-separated repo names to skip. |
| `--maxdepth N` | 3 | Max directory depth for discovery. |
| `--github-user NAME` | auto (gh/git) | Your GitHub username; the script pushes only to an origin you own. |
| `--audit-only` | off | Read-only audit — no writes at all. |
| `--dry-run` | off | Simulate; show what the safe ops would do. |
| `--check-only` | off | Exit non-zero if any repo is dirty/diverged/conflicted (CI). |
| `--prune-backups N` | off | Remove `git-audit-sync/*` backup branches older than N days. |

```bash
repo ~/code                      # audit + safe sync (push owned, ff-pull)
repo ~/code --audit-only         # read-only audit
repo ~/code --dry-run            # show what the safe ops would do
repo ~/code --workers 12 --since-days 30
repo ~/code --exclude whisper.cpp,agents
```

### Parallel workers

Each repo is dispatched to an independent worker thread with its own `GitRepo`
object; results merge through a thread-safe collector, then sort by severity.
One repo failing never blocks the rest.

## Output

A timestamped report at `~/git-audit-logs/` — markdown (human) and JSON (machine).
The JSON carries per-repo `state`, `ahead`/`behind`, `needs` (the agent's
to-do), `conflict_files`, `secrets`, and `untracked` so the agent can act
precisely:

```
## Summary
| ✅ Clean | 37 | ⏩ Pulled | 2 | 📤 Pushed | 1 | ⚠️ Needs agent | 10 | ❌ Errors | 2 |

## Per-repo results
- 📤 ante-spec — would push (1 commits)
- ⏩ wiki-memory — pulled (1 commits, ff-only)
- ⚠️ custom-skills — NEEDS AGENT: 1 uncommitted file(s) on 'main' — review, commit, push
- ⚠️ multi-agent-workflow — NEEDS INPUT: origin not owned by you (apolopena/…)
- ❌ agents — remote repository not found — update or remove the remote
```

## Cases the agent must handle (never the script)

- **Any uncommitted work** — review the diff, exclude secrets/junk/accidental deletions, commit deliberately, push.
- **Divergence** — reconcile keeping all functionality; understand the conflict before resolving; never delete to clear a conflict.
- **Foreign origin (not yours)** — ask; fork to the user's account or leave local. Never push to a repo that isn't theirs.
- **No / dead remote** — ask whether to add, repoint, or remove. Never auto-remove a remote.
- **Active merge/rebase/cherry-pick** — finish or abort with the user first.
- **Detached HEAD** — `git switch <branch>` first.

## Rollback Safety

The only writes are `pull --ff-only` (cannot lose committed work) and `push`
(changes nothing locally), so there is little to undo. Backup branches created by
older versions can be pruned with `--prune-backups N`, or restored with:

```bash
git switch -c recovery-<name> git-audit-sync/backup-YYYYMMDD-HHMMSS-<name>
```
