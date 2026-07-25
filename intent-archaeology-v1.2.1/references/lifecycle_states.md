# Lifecycle States (5 states)

> **When to read:** before Phase 4 (lifecycle derivation), or when a
> project's status vector seems wrong.

## The five lifecycle states

Phase 4 derives each project's lifecycle state from evidence in the
session corpus + repo + spec lineage, then confirms it (the derivation
is a proposal; confirmation can be automated or human). The state
routes the project through different Phase 7–8 output shapes.

### 1. `not-started`

**Evidence:** no commits in the repo, no `tasks.md` items checked off,
no spec-kit `/specify.plan` invocations in cass for this workspace.

**Phase 3 output:** generate canonical PRD by analyzing existing
versions and sorting ideas into `discarded`, `incorporated`, `deferred`.

**Phase 7 output:** status vector with all components at `planned` or
`not-begun`. The wiki page says "Ready to start — canonical PRD
generated, see [link]".

**Sleep-time agent:** should NOT pick up these projects for autonomous
work without a user's go-ahead. They are pre-implementation.

### 2. `in-progress`

**Evidence:** commits exist, `tasks.md` (if spec-kit) has some items
checked off, recent session activity in cass.

**Phase 3 output:** recover the canonical PRD that was live at build
time, plus the comments/updates that modified it during the build.

**Phase 7 output:** status vector with components at various states
(`completed`, `in-progress`, `drifted`, `blocked`). The wiki page
shows the gap analysis.

**Sleep-time agent:** primary candidates for autonomous continuation.
Status vector drives the queue.

### 3. `completed`

**Evidence:** all `tasks.md` items checked off (or living document
worklog shows all items done), no recent session activity, repo has a
release tag or final commit.

**Phase 3 output:** recover the canonical PRD that was live at build
time, plus the post-completion updates (often present, compounding
confusion).

**Phase 7 output:** status vector with most components at `completed`.
Look for `drifted` — features that were built differently than
specified.

**Sleep-time agent:** lower priority. Improvements should be
additive, not corrective.

### 4. `under-revision`

**Evidence:** project was completed (has release tag or final commit)
but recent session activity shows new work — feature additions,
refactors, bug fixes that go beyond maintenance.

**Phase 3 output:** a **modified plan** that addresses all of the
above (original intent + post-completion updates + current revision
goals) in a considered manner. This is an outline, not a canon — the
user reviews before it becomes canon.

**Special handling:** for `under-revision` projects, there's a live
2026 argument against whole-system reverse-engineered specs — a derived
spec becomes a misalignment source, and building new features against
it raises regression risk. So Phase 3 produces **change-level specs
scoped to the next change**, not a whole-system reconstruction. (This
is proposed change #5 from the transcript; revert cost: low, just
remove the conditional in `03_spec_archaeology.py`.)

**Phase 7 output:** status vector with components at `completed` and
`in-progress` (the revision work). Distinguish revision work from
original work in the wiki.

**Sleep-time agent:** medium priority. Revision work is often
context-heavy; the agent should be cautious about over-reaching.

### 5. `archive-candidate`

**Evidence:** no session activity for >6 months, no recent commits,
`not-started` or `in-progress` state but abandoned. Often has
speculative PRDs that never went anywhere.

**Phase 3 output:** minimal — record what exists, mark for archive.

**Phase 7 output:** status vector with `abandoned` components. The
wiki page says "Archive candidate — last activity YYYY-MM-DD. Reasons:
<reasons>".

**Sleep-time agent:** should NOT resurrect these projects. The
`abandoned.md` cross-cutting wiki page exists specifically to stop
the sleep-time agent from resurrecting dead work.

## Why a fifth state was added

The user's original progression had four states (not-started,
in-progress, completed, under-revision) — but all four end in work.
An audit that can't recommend killing a project is a completion engine
wearing an audit costume. `archive-candidate` is the state that says
"this should stop".

## Derivation is a proposal, confirmation is required

Phase 4 derives the state from evidence and writes it to
`projects.derived_lifecycle`. It also writes a confidence score and
the evidence list. Confirmation can be:

- **Automated:** if confidence > 0.9 and no contradictory evidence,
  the state is auto-confirmed.
- **Human:** otherwise, the state is `proposed` and a confirmation
  prompt is added to the wiki's master index for the user to resolve.

Never run Phase 7 on a `proposed` state — the routing might be wrong,
and routing wrong is expensive to undo.
