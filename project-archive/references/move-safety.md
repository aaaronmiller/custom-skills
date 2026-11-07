# Move safety: where each DA-032 rule comes from

Sources are relative to `~/work/jobs/lineage-archive/in/` unless stated.

## The clause and its register row

- DA-032 (durable-agent spec 1.4.0, `~/work/jobs/da-integrate/out/agentic-workbench/specs/002-durable-agent/spec.md` line 107): folder moves always never-class; under a migration hold an approved move first lists every consumer, passes a sandbox test, and writes a manifest, path map, old-path links, working-copy repair and live-use guard.
- Row C269 (`durable-agent-plan-2026-11-04.md` line 348) carries the same list; row C054 (line 131) puts "folder move" among the never-class actions refused when unattended.

## Why moves are dangerous: the path-move hazard

`project-atlas/sources/atlas-pack/atlas-process-design.md` line 312: harnesses
key session history and project memory by absolute path, so every move writes
an old-to-new path map. The Atlas prompt, Phase 7 (`atlas-agent-prompt.md`
lines 243 to 250), lists what a migration must also do: write
`registry/path-map.yaml` and add every old path as an alias; leave a link at
each old path (a Windows junction where symlinks need privilege); run
`git worktree repair` after moving a linked worktree or main repository, with a
backup of the metadata it changes; rewrite path fields in Living Documents;
flag virtual environments with embedded absolute paths as punch items; flag
dirty repos, never committing.

How this skill maps them: `path-map.json` (entries, aliases, rewrites,
relinks); `old-path-links.json` (symlink, or a junction note under `/mnt/<drive>/`);
`working-copy-repair.json` (repair commands, metadata files with hashes to back
up, embedded absolute paths as punch items, dirty state recorded and never
committed).

## Consumers: what to scan

Plan section 6 (`durable-agent-plan-2026-11-04.md` lines 764 to 770) names the
consumer check for the five durable-agent folders: references in the
assignment `catalog.json` and `index.html`, the assignment-library index,
plan-lineage `repos.json` and `links.json`, Living Documents `source-root`
fields, skillshare sources, cron jobs and symlinks. `consumers.py` finds
consumers by path reference, never by name, in whatever roots it is given; it
cannot find a reference in a file it is not shown. Pass those files or their
folders as `--roots` and add `--crontab`.

## Reversibility tiers and the hold

`atlas-process-design.md` lines 228 to 237: R2 covers folder moves and renames,
with the undo path "path map, symlink at the old path, generated rollback
script", autonomous unless `hold: [migration]` is set; the Never tier bans
delete, commit, push, pull, merge, rebase, reset, checkout, stash, clean,
prune, installing software and reading or printing secrets.

The lineage report (`lineage-2026-11-03/routing-archive-atlas.md` line 195,
conflict C12) resolved the clash with the Workbench: keep both, honour the hold
as never-class, and after it lifts make the move a journaled, path-mapped,
reversible effect with a live-use guard; moves of projects are Red unless the
exact target is authorised. DA-032 then made moves never-class always. This
skill therefore needs an approval naming the exact source and destination for
every move and treats every move as held (all seven artifacts required).

## Live-use guard

`atlas-agent-prompt.md` line 252: immediately before executing, re-run the dry
run and a live-use guard that skips and defers any row whose folder has files
changed in the last hour or a running process inside it. `plan.py` writes the
guard; `move_dryrun.py` re-runs it at print time. Processes are found by
working directory and open files under `/proc`; only the command name is
recorded, never arguments (they can hold secrets).

## After the move: verification and rollback

`atlas-agent-prompt.md` line 252: after executing, verify every target exists,
every old-path link resolves, every repo reports the same HEAD as before, and
every rewritten Living Document passes audit; any failure runs that row's
rollback and is logged. The lineage-archive job found this unregistered
(project-atlas index entry AT-095) and proposed adding it to C269.
`verify_move.py` checks the first three and also compares the tree digest and
the Git status, stash list and changed-content hash. The Living Documents audit
belongs to the Living Documents tools and is a human-confirm item.

## Cross-filesystem moves

`mv` across filesystems copies and then deletes the source. The archive rule is
"move, never delete" (`foundation-plan-2026-11-03.md` line 169), so
`move_dryrun.py` refuses such a move; a human copies, verifies, and only then
decides about the source.
