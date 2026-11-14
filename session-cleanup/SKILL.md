---
name: session-cleanup
description: "Closes out a long agent session: finishes small loose ends, writes handoff docs for big ones, and checks every touched repo is committed and pushed. Also surveys all running sessions."
metadata:
  description-reviewed: "2026-11-10"
---

# Session Cleanup

Goal: leave **zero ambiguous state** — every piece of work is either done-and-pushed or written into a handoff a fresh session can start from cold. Minor items get finished inline; big items get handoffs. Then the whole sweep runs a second time so nothing escapes.

Two passes, same checklist. Pass 1 does the work. Pass 2 re-runs every check from scratch (fresh `git status`, fresh test run, re-read handoffs) and fixes anything Pass 1 missed or broke.

## Pass 1 — Triage and close

### 1. Find every loose end (evidence first, no guessing)

- **Uncommitted/unpushed work:** `git status --porcelain` + `git log origin/HEAD..HEAD --oneline` in every repo touched this session. The session transcript names them; verify with the commands, don't trust memory.
- **Background jobs:** `crontab -l`, cron logs/stamps in `~/.local/state/cronjobs/`, any `proc://` or detached agents still running. A job that exited non-zero or never ran is a loose end.
- **Failing or skipped tests:** re-run the suites touched this session (`pytest -q`, `cargo test`, `bun test` — whichever the repo uses). A "green" you remember from an hour ago is not evidence.
- **Session history via CASS:** run targeted searches, not broad ones (default no-limit queries page 6k+ hits against a 4GB DB and take 60s+; always pass `--limit 10`):
  ```bash
  cass search "<project> handoff" --limit 10
  cass search "<project> uncommitted OR unpushed OR TODO left" --limit 10
  cass search "context compact summary" --limit 10   # what did past sessions lose?
  ```
  Look specifically for: handoffs that were promised but never written, mid-handoff cutoffs (the 2026-07-25 omp sessions show the failure mode: handoff fired mid-answer and the user never got the doc), and compaction postmortems (2026-06-01 hermes 128K-vs-1M misconfig caused compactions at 6% of real capacity — check current thresholds if compaction came up).
- **Out-of-scope discoveries:** anything noticed but not part of the original task (failing test in a file you didn't touch, stale cron comment, dirty telemetry artifact). Each one gets resolved inline or written into a handoff — never silently dropped.

### 2. Sort: finish small, hand off big

| Size | Action |
|---|---|
| ≤ ~15 min, no design decisions | Do it now: fix, commit, push. |
| Needs user judgment, a big build, or a fresh context window | Write a handoff (see §3), don't start it. |
| Blocked on something outside the session | Handoff with the blocker named exactly (what, where, who unblocks). |

The cutoff is about **judgment and context cost**, not line count. When unsure, hand off — a fresh session with a good handoff beats a tired session pushing through.

### 3. Handoff format (one file per workstream)

Write to the owning repo (alongside the work, not in /tmp): `HANDOFF-<topic>.md` or the repo's existing handoff convention. Each handoff contains:

1. **Goal in one sentence** — what "done" looks like.
2. **Current state with evidence** — last verified command + output (commit SHA, test count, version string). No "should be" or "probably".
3. **Exact next commands** — copy-pasteable, in order, with working directory.
4. **Blockers / open questions** — named, with who or what resolves each.
5. **Files touched** — paths + one line each on what's pending in them.
6. **What NOT to redo** — completed steps with their evidence, so the next session doesn't re-verify from zero.

### 4. Commit, push, document — every touched repo

Per repo, in order:
1. Secrets scan (`github_pat_|ghp_|sk-(live|proj)-|BEGIN.*PRIVATE KEY|aws_secret|AIza` over diff + untracked) and junk check (`__pycache__`, `node_modules`, `dist/`, `*.pyc`, swap files stay out).
2. Review the diff, commit with a real message naming what changed, `git pull --ff-only`, `git push`. Never force; reconcile or flag.
3. Update README/docs to reflect the change (new script? new cron line? new collector? — the doc that lists such things gets the new row). A feature with no doc update is unfinished.
4. Confirm: `git status` clean, `git log origin/HEAD..HEAD` empty.

Ownership rule: push only to remotes you own. Foreign origins get a fork-or-leave-local decision from the user, never an automatic push. (See `git-audit-sync` for the full flag table.)

### 5. Cron and background jobs

- Every cron line added this session must exist in the repo-owned crontab file (`guardian/cronjobs/crontab`) **and** the live `crontab -l` (installed via `/home/cheta/code/guardian/install.sh`, diff-verified). A repo-only line never fires; a live-only line gets wiped on next install.
- Every new job script must be in the `/home/cheta/code/guardian/install.sh` preflight list and executable, with one observed run (`START`/`EXIT rc=0` in its log).
- Any job that failed since the break: read its log tail, fix or hand off — don't leave a red EXIT for the next session to discover.

## Pass 2 — Verify from zero

Re-run **all of Pass 1's checks** as if you hadn't just done them:
1. Fresh `git status` + unpushed-log in every touched repo (catches the file you edited after committing).
2. Re-run the affected tests once more (catches the fix that broke its neighbor).
3. Re-read each handoff: is the next-command block actually runnable cold? Are SHAs/versions current?
4. Re-check cron install state and job logs.
5. Confirm docs match the final code (not the intermediate version).

Pass 2 findings go through the same sort (finish small / hand off big). Two consecutive clean passes = done.

## Cross-session survey (every running session on the machine)

Use when the operator asks what all the open sessions are doing, or before closing a batch of them. Built and proven 2026-11-07 on 9 laptop sessions (claude, codex, omp, agy).

1. `python3 -I scripts/find-sessions.py > sessions.tsv`: every running claude, codex, omp and agy session, mapped to its folder, session file and process id. Daemons are skipped. For another host, run it there over SSH.
2. `python3 -I scripts/digest.py <harness> <session_file> <KEY>.txt` per row: operator messages, last replies, paths touched.
3. `OPENCODE_GO_API_KEY=... python3 -I scripts/summarize.py <dir> L1 L2 ...`: each digest is redacted, then summarized by Gemini 4 Argon on OpenCode Go (no training, zero retention) into JSON: task, status, done, remaining, repos, action, close_safe, evidence. Calls are logged to `~/.local/state/capacity-watch/calls-direct.jsonl`.
4. Git state per repository the sessions touched (`git status --porcelain`, ahead and behind), then one handoff file per session and the master page: `/home/cheta/code/masterplan/tools/master-report.py`.
5. Spot-check the summaries before reporting: named commits exist (`git log`), loops and counts are counted directly. A model summary is evidence, not proof.

Closing a session is the operator's call: list it under decisions with its handoff path; never kill a session process unasked.

## Done criteria

- [ ] Every touched repo: `status` clean, nothing unpushed, README/docs updated.
- [ ] Every loose end: finished + pushed, or in a handoff with cold-startable next commands.
- [ ] Every out-of-scope discovery: resolved or handed off — none silently dropped.
- [ ] Cron/background: repo crontab == live crontab, new jobs observed green.
- [ ] Two full passes completed; Pass 2 found nothing (or its findings are closed above).
- [ ] Session summary stated: what closed, what handed off (with file paths), what remains red.
