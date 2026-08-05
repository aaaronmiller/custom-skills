#!/usr/bin/env bash
# strata-scaffold.sh
# Creates an empty, valid STRATA artifact tree for a new project.
# Defaults to macOS bash semantics. Spaces in the project name are handled.
#
# Usage:
#   ./strata-scaffold.sh "My Project Name" [parent-dir]
#
# Produces:
#   <parent-dir>/strata/<slug>/{intent,spec,context,substrate,constitution}.md
#   <parent-dir>/strata/<slug>/plays/{scaffold,commit,deploy}.md
#   <parent-dir>/strata/<slug>/ledger/{ledger,standing}.md
#   <parent-dir>/strata/<slug>/evals/README.md   (eval set lives OUTSIDE the build tree by rule;
#                                                  this directory is the pointer, not the store)

set -euo pipefail

if [ "$#" -lt 1 ]; then
  echo "usage: $0 \"Project Name\" [parent-dir]" >&2
  exit 2
fi

PROJECT_NAME="$1"
PARENT_DIR="${2:-.}"

# Slug: lowercase, spaces and non-alphanumerics to single hyphens, trimmed.
SLUG="$(printf '%s' "$PROJECT_NAME" \
  | tr '[:upper:]' '[:lower:]' \
  | sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$//')"

if [ -z "$SLUG" ]; then
  echo "error: project name produced an empty slug" >&2
  exit 2
fi

ROOT="$PARENT_DIR/strata/$SLUG"

if [ -e "$ROOT" ]; then
  echo "error: $ROOT already exists; STRATA does not overwrite an existing tree" >&2
  exit 1
fi

NOW="$(date '+%Y-%m-%d %H:%M:%S %Z')"

mkdir -p "$ROOT/plays" "$ROOT/ledger" "$ROOT/evals"

fm() {
  # $1 = tag list, $2 = title
  printf -- '---\ndate: %s\nver: 1.0.0\nauthor: ice-ninja\nmodel: claude-opus-4-7\ntags: [%s]\n---\n\n# %s\n\n' \
    "$NOW" "$1" "$2"
}

{
  fm "strata,intent" "$PROJECT_NAME Intent v1.0"
  printf '## 1. Goal\n[One sentence outcome. No technology tokens anywhere in this file.]\n\n'
  printf '## 2. Intent level\n[Consumer or engineering, list each.]\n\n'
  printf '## 3. Constraints\n[Hard constraints. The deployment target lives here as a constraint.]\n\n'
  printf '## 4. Scale and quality expectations\n[The numbers architecture is derived from.]\n\n'
  printf '## 5. Success conditions\n\n## 6. Failure conditions\n\n## 7. Personas\n\n'
  printf '## 8. Scope boundaries\n\n## 9. Prior art\n\n## 10. Assumptions and dependencies\n\n'
  printf '## 11. Open intent questions\n[Max three NEEDS CLARIFICATION markers.]\n'
} > "$ROOT/intent.md"

{
  fm "strata,spec" "$PROJECT_NAME Specification v1.0"
  printf '## 1. Contract clauses\n[Every clause testable. Every clause carries an EVAL-ID. No technology tokens.]\n\n'
  printf 'SPEC-001 [EVAL-001] THE system SHALL [observable behavior].\n\n'
  printf '## 2. Acceptance scenarios\n\n## 3. Eval index\n| EVAL-ID | Asserts | Bound clause | Stored at |\n|---|---|---|---|\n| EVAL-001 | ... | SPEC-001 | evals/ outside build tree |\n'
} > "$ROOT/spec.md"

{
  fm "strata,context,system-derived" "$PROJECT_NAME Context v1.0 (derived)"
  printf '## 1. Derivation summary\n[System-derived. State explicitly if the ledger was empty.]\n\n'
  printf '## 2. Architecture overview\n\n## 3. Decisions\nCTX-001: [decision]\n- Derived from: intent section [n]\n- Memory: ledger entry [id] OR "no empirical memory, intuition-based"\n\n'
  printf '## 4. Data model\n\n## 5. Component specifications\n\n## 6. Hosting and deployment\n[Derived from the deployment constraint in intent section 3.]\n\n'
  printf '## 7. Security\n\n## 8. Build phases\n[Phase and step notation only, no dates.]\n\n## 9. Project structure\n'
} > "$ROOT/context.md"

{
  fm "strata,substrate,self-location" "Substrate Self-Location"
  printf '## Declared level\nS3\n\n## Pre-locked decisions\n[Be specific. This is the required honesty.]\n\n'
  printf '## Live-resolved decisions\n\n## Empirical memory state\nempty (Context Crafting is intuition-based on this project)\n\n## Known reach\n'
} > "$ROOT/substrate.md"

{
  fm "strata,constitution,governance" "Constitution (reference only)"
  printf 'STRATA does not generate a constitution from scratch. If the project has one, replace this file with it. If not, create one through SpecKit or OpenSpec tooling and place it here. The human owns this file.\n'
} > "$ROOT/constitution.md"

for play in scaffold commit deploy; do
  {
    fm "strata,plays,$play" "Play: $play"
    printf '## Reads\n[Every variable and its location, e.g. deployment target: intent.md section 3. Never store the value.]\n\n'
    printf '## Preconditions\n\n## Steps\n[Ordered, deterministic, each step references SPEC-IDs.]\n\n'
    printf '## Halt conditions\n[When to stop and surface to a human rather than guess.]\n\n'
    printf '## Ledger emission\n[What this play appends to ledger/ledger.md on completion.]\n'
  } > "$ROOT/plays/$play.md"
done

{
  fm "strata,ledger,continuity" "Ledger (append-only)"
  printf '## 0001 0.0 decision\n- What: STRATA tree scaffolded for %s.\n- Why: project kickoff.\n- Effect: created intent, spec, context, substrate, constitution, plays, ledger.\n- Outcome: tree created, validation pending.\n' "$PROJECT_NAME"
} > "$ROOT/ledger/ledger.md"

{
  fm "strata,standing,continuity" "Standing"
  printf '## Where this is\n%s was scaffolded. Artifacts are stubs awaiting intake-driven content.\n\n' "$PROJECT_NAME"
  printf '## Last decisions that matter\n- 0001: tree scaffolded.\n\n'
  printf '## Not yet decided\nAll content. Intake and the Confidence Gate come next.\n\n'
  printf '## Next\nRun Phase 1 intake, then Phase 2 research.\n\n'
  printf '## Substrate note\nDeclared S3, empirical memory empty.\n'
} > "$ROOT/ledger/standing.md"

{
  fm "strata,evals" "Eval store pointer"
  printf 'The eval set bound to spec.md EVAL-IDs MUST live outside this build tree and out of the implementing agent view. This file records where it lives; it is not the store itself.\n\nStore location: [set this to a path or repository outside the build tree]\n'
} > "$ROOT/evals/README.md"

echo "scaffolded: $ROOT"
echo "next: fill intent.md and spec.md (human), let the system derive context.md and plays/, then run strata-validate.py"
