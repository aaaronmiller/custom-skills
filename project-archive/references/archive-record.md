# The archive record and the move artifacts

## Archive record (`W/archive-record.json`, schema project-archive/record/1)

Source of the field list: unified-agentic-stack plan section 7.8
(`~/work/jobs/lineage-archive/in/unified-agentic-stack/sources/unified-agentic-stack/unified-agentic-stack-plan.md`
lines 590 to 600), the register row C270 (`durable-agent-plan-2026-11-04.md`
line 349) and DA-033.

| Section 7.8 asks for | Record field |
|---|---|
| stable project and artifact identity | `identity.project_id`, `identity.folder_name`, `identity.repository` (remotes and root commits, the Atlas identity rule), `identity.tree_digest` |
| original and current locators | `locators.original_path`, `locators.archive_path`, `locators.old_path_link`, `locators.index_path`, `locators.remotes` |
| retirement reason and date | `retirement.reason`, `retirement.date` |
| predecessor and successor links | `predecessor`, `successor` |
| source revisions | `source_revisions.head`, `source_revisions.branch` |
| a content manifest | `content_manifest.tree_digest`, `content_manifest.file_count`; the full manifest is `W/plan/manifest.json` |
| exact recovery instructions | `recovery.instructions` (structured: remove-link, move, verify) and `recovery.human_steps` |
| preserve dirty and untracked work | `uncommitted_state` (status porcelain, untracked list, changed-content hash) |
| Git common-directory and worktree relationships | `working_copy_state` (branch, stash list and count, worktrees, linked-worktree flag) |
| test the recovery with a process that did not construct it, including a dirty or untracked file and a metadata-dependent case | `recovery.tested`, set only by `recovery_test.py`, which reads the record alone and checks bytes, status (dirty and untracked files) and the stash list (Git metadata) |

Section 7.8 also says a remote URL is not a tested backup, and that sensitive
material stays in its private scope. The record stores remotes with any
embedded credentials redacted, and file hashes only, never contents.

## Where the index goes

The foundation plan puts `ARCHIVE-INDEX.md` in the archived folder. Writing a
file into the folder would change its bytes and its `git status`, which DA-033
requires to stay the same. This skill writes the index beside the folder,
`<archive root>/<project>/ARCHIVE-INDEX-<folder>.md`. A human can choose
otherwise; see REPORT.md.

## The seven move artifacts (`W/plan/`, written by plan.py)

| DA-032 names | File | Key content |
|---|---|---|
| list every consumer | `consumers.json` | kind, path, line, redacted snippet; internal absolute self-references |
| sandbox test | `sandbox-test.json` | copy, move, link, read through the old path, Git state, recover, each step with ok |
| manifest | `manifest.json` | the Atlas manifest row (current path, target path, operation, risk, reason, deletions none), files with sha256 and mode, tree digest, Git facts, sensitive file names |
| path map | `path-map.json` | old to new, aliases, consumer rewrites, symlink relinks |
| old-path links | `old-path-links.json` | link at the old path, method, command, parent writable |
| working-copy repair | `working-copy-repair.json` | worktree repair commands, metadata backups with hashes, punch items, never-commit note |
| live-use guard | `live-use-guard.json` | recent files, processes inside, passed |

`readiness.json` ties them together: move class never, hold, approval (present,
matches the exact move, approver), each artifact's file, sha256 and time
written, blockers, ready. `move_dryrun.py` refuses if any artifact changed
after it was hashed or was written after the readiness record.
