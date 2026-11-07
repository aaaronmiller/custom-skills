# Lineage vocabulary, evidence ladder and decision policy

Copied out of project-atlas 5.1.0, as plan section 6.1 directs
(`durable-agent-plan-2026-11-04.md` line 783: lineage vocabulary, evidence
ladder, fingerprint method, two status vectors and decision policy go to the
portfolio-lineage references). Source files, relative to
`~/work/jobs/lineage-archive/in/project-atlas/sources/atlas-pack/`:
`atlas-agent-prompt.md` (P) and `atlas-process-design.md` (D). Atlas never ran;
this is design, not proven practice.

## Data model (P lines 141 to 147)

- Artifact: any directory, archive, worktree or remote-only repository that may
  hold project material.
- Repository: identity is the canonical remote URL plus the root commit SHA
  (`git rev-list --max-parents=0 HEAD`). Many artifacts can share one repository.
- Project family: the durable idea, recorded as one Living Document; its id is
  the Living Document id or a kebab-case slug, never a folder name.
- Variant: a materially distinct implementation or state, `<project_id>/<slug>`.
  Ordinary branches are not variants unless they differ materially.
- Edge: source variant, target variant, origin, axes, optional `supersedes`,
  spec version on each side, confidence, evidence pointers, explanation.

## Origins, axes and supersedes (P lines 149 to 157)

- Every edge has exactly one origin: `copy`, `worktree`, `history-fork`,
  `regeneration`, `rewrite`, `port`, `spin-off`, `merge`, `snapshot`, `spec-only`.
- Every edge has one or more divergence axes: `frontend`, `architecture`,
  `platform`, `scope`, `spec-version`, `harness`, `none`.
- A separate temporal edge, `supersedes`, marks the preferred successor.
- A shared root commit proves `copy`, `worktree` or `history-fork`. A matching
  spec fingerprint with no shared history and different session harnesses
  indicates `regeneration`.
- Group by purpose first: write each artifact's purpose before comparing
  anything, cluster by purpose, then use Git, spec and session evidence to
  classify the origin inside each cluster. Low code similarity never rules out
  a family match.
- D line 211: two frontends on shared code are `history-fork` + `frontend`; two
  harness builds of one spec are `regeneration` + `harness`; both stay in one family.

## Evidence ladder, strongest first (D lines 213 to 220)

1. Git identity: root commit, remote, shared SHAs. Proves copy, worktree, history-fork.
2. Session logs: which harness worked in which folder, and when. Proves regeneration and harness divergence.
3. Spec fingerprints: which PRD or design version each variant was built from.
4. Code fingerprints: exact hash, normalised hash, MinHash Jaccard. Weak for regeneration by design.
5. Living Documents and notes: stated intent and history.
6. Names: weakest. Never sufficient alone to merge or split a family.

Fingerprints, cheapest first (P line 187): exact tree hash; normalised file
hashes (whitespace and comments stripped) as a set; MinHash Jaccard only for
pairs purpose grouping left unresolved. Exclude secrets, lockfiles, generated
and vendored files.

## Status: two vectors, not one label (D lines 222 to 226)

- Lifecycle: `not-started` to ready-to-start; `in-progress` and `revision` to
  in-progress; `complete` to completed; `archive-candidate` to archive.
  `activity_year` comes from the last meaningful commit or source edit, never
  from file times alone.
- Git state: worktree (`clean`, `dirty`); sync (`current`, `behind`, `ahead`,
  `diverged`, `no-upstream`, `unverified`); local-only branch count; stash count.

## Decision policy (P lines 132 to 139)

- One evidence pass per ambiguous item, then decide: best guess, confidence
  low, a line in an exceptions file, move on.
- Exceptions are revisited in a second pass, never mid-batch.
- Cosmetic issues never block anything.
- If a step cannot run, skip it, log why, finish everything else, retry later.
- Proportionality: build only the machinery the outputs need.

## What not to reuse

The lineage report (`lineage-2026-11-03/routing-archive-atlas.md` line 213):
not the Environment paths, not the "run for hours without stopping" autonomy
(it conflicts with the Red-action rules; register row C279 rejects it), and not
the portfolio scoring.
