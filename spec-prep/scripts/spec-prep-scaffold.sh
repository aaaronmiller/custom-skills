#!/usr/bin/env bash
# spec-prep-scaffold.sh
# Creates legacy standalone authoring templates, not a compact input handoff or prepared native project.
# Defaults to macOS bash semantics. Spaces in the project name are handled.
#
# Usage:
#   ./spec-prep-scaffold.sh "My Project Name" [repo-dir]
#
# Environment (all optional):
#   SPECPREP_AUTHOR   frontmatter author   (default: ice-ninja)
#   SPECPREP_MODEL    frontmatter model    (default: unknown; set to the model doing the work)
#   SPECPREP_EVALS    eval store directory (default: ~/.spec-prep/evals/<slug>), kept OUTSIDE the repo
#   SPECPREP_LAYOUT   docs | spec-prep        (default: docs -> <repo>/docs/specs/<slug>;
#                                         spec-prep -> <repo>/spec-prep/<slug>)
#
# Produces:
#   <root>/{intent,spec,context,experience,substrate,constitution}.md
#   <root>/plays/{scaffold,commit,deploy,build}.md
#   <root>/ledger/{ledger,standing}.md
#   <root>/EVALS-LOCATION.md                 pointer only; the store lives outside the repo
#   $SPECPREP_EVALS/evals.md                   held-out eval manifest skeleton
#   <repo>/AGENTS.md and <repo>/CLAUDE.md    only if absent: standing gates, CLAUDE.md imports AGENTS.md

set -euo pipefail

if [ "$#" -lt 1 ]; then
  echo "usage: $0 \"Project Name\" [parent-dir]" >&2
  exit 2
fi

PROJECT_NAME="$1"
PARENT_DIR="${2:-.}"
resolve_setting() {
  local primary="SPECPREP_$1" alias="SPEC_PREP_$1"
  local a="${!primary-}" b="${!alias-}"
  if [ -n "$a" ] && [ -n "$b" ] && [ "$a" != "$b" ]; then
    echo "error: conflicting $primary and $alias" >&2
    return 2
  fi
  printf '%s' "${a:-${b:-$2}}"
}
AUTHOR="$(resolve_setting AUTHOR ice-ninja)" || exit 2
MODEL="$(resolve_setting MODEL unknown)" || exit 2
LAYOUT="$(resolve_setting LAYOUT docs)" || exit 2

# Slug: lowercase, spaces and non-alphanumerics to single hyphens, trimmed.
SLUG="$(printf '%s' "$PROJECT_NAME" \
  | tr '[:upper:]' '[:lower:]' \
  | sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$//')"

if [ -z "$SLUG" ]; then
  echo "error: project name produced an empty slug" >&2
  exit 2
fi

EVALS_DIR="$(resolve_setting EVALS "$HOME/.spec-prep/evals/$SLUG")" || exit 2

case "$LAYOUT" in
  spec-prep) ROOT="$PARENT_DIR/spec-prep/$SLUG" ;;
  docs)   ROOT="$PARENT_DIR/docs/specs/$SLUG" ;;
  *)      echo "error: SPECPREP_LAYOUT must be docs or spec-prep" >&2; exit 2 ;;
esac

if [ -e "$ROOT" ]; then
  echo "error: $ROOT already exists; spec-prep does not overwrite an existing tree" >&2
  exit 1
fi

# Validate the eval boundary before any directory or template mutation.
python3 - "$PARENT_DIR" "$EVALS_DIR" <<'PYBOUNDARY'
from pathlib import Path
import sys
repo = Path(sys.argv[1]).expanduser().resolve()
for ancestor in [repo, *repo.parents]:
    if (ancestor / '.git').exists():
        repo = ancestor
        break
evals = Path(sys.argv[2]).expanduser().resolve()
if evals == repo or repo in evals.parents:
    raise SystemExit('error: held-out eval store must be outside the build root')
PYBOUNDARY

NOW="$(date '+%Y-%m-%d %H:%M:%S %Z')"

mkdir -p "$ROOT/plays" "$ROOT/ledger" "$EVALS_DIR"

fm() {
  # $1 = tag list, $2 = title
  printf -- '---\ndate: %s\nver: 1.0.0\nauthor: %s\nmodel: %s\ntags: [%s]\n---\n\n# %s\n\n' \
    "$NOW" "$AUTHOR" "$MODEL" "$1" "$2"
}

{
  fm "spec-prep,intent" "$PROJECT_NAME Intent v1.0"
  printf '## 1. Goal\n[One sentence outcome. No technology tokens anywhere in this file.]\n\n'
  printf '## 2. Intent level\n[Consumer or engineering, list each.]\n\n'
  printf '## 3. Constraints\n[Hard constraints. The deployment target lives here as a constraint.]\n\n'
  printf '## 4. Scale and quality expectations\n[The numbers architecture is derived from.]\n\n'
  printf '## 5. Success conditions\n\n## 6. Failure conditions\n\n## 7. Personas\n\n## 8. User stories\n[As a <persona>, I want <capability> so that <outcome>. Given/When/Then acceptance; each story lists the SPEC-IDs that verify it.]\n\n'
  printf '## 9. Scope boundaries\n\n## 10. Prior art\n\n## 11. Assumptions and dependencies\n\n'
  printf '## 12. Open intent questions\n[Material unresolved decisions and explicit provisional defaults; respect the installed native template limits.]\n'
} > "$ROOT/intent.md"

{
  fm "spec-prep,spec" "$PROJECT_NAME Specification v1.0"
  printf '## 1. Contract clauses\n[Every clause testable. Every clause carries an EVAL-ID. No technology tokens.]\n\n'
  printf '**SPEC-001** [EVAL-001] THE system SHALL [observable behavior].\n- Eval: [what the held-out evaluation asserts]\n- Traces to: intent section [n]\n\n'
  printf '## 2. Acceptance scenarios\n\n## 3. Eval index\n| EVAL-ID | Asserts | Bound clause | Stored at |\n|---|---|---|---|\n| EVAL-001 | ... | SPEC-001 | held-out store (see EVALS-LOCATION.md) |\n'
} > "$ROOT/spec.md"

{
  fm "spec-prep,context,system-derived" "$PROJECT_NAME Context v1.0 (derived)"
  printf '## 1. Derivation summary\n[System-derived. State explicitly if the ledger was empty.]\n\n'
  printf '## 2. Architecture overview\n\n## 3. Decisions\nCTX-001: [decision]\n- Derived from: intent section [n]\n- Memory: ledger entry [id] OR "no empirical memory, intuition-based"\n\n'
  printf '## 4. Data model\n\n## 5. Component specifications\n\n## 6. Hosting and deployment\n[Derived from the deployment constraint in intent section 3.]\n\n'
  printf '## 7. Security\n\n## 8. Build phases\n[Phase and step notation only, no dates.]\n\n## 9. Project structure\n'
} > "$ROOT/context.md"

{
  fm "spec-prep,substrate,self-location" "Substrate Self-Location"
  printf '## Declared level\nS0\n\n## Pre-locked decisions\n[Be specific. This is the required honesty.]\n\n'
  printf '## Live-resolved decisions\n\n## Empirical memory state\nempty (Context Crafting is intuition-based on this project)\n\n## Known reach\n'
} > "$ROOT/substrate.md"

{
  fm "spec-prep,constitution,governance" "Constitution (reference only)"
  printf 'Governance is human-owned. During specification preparation, use the project constitution or create it through the installed Spec Kit constitution workflow from authorized principles. The authoritative path is .specify/memory/constitution.md; this file is only a reference.\n'
} > "$ROOT/constitution.md"

{
  printf -- '---\ndate: %s\nver: 1.0.0\nauthor: %s (system-derived)\nmodel: %s\nlayer: derived\ntags: [spec-prep,experience,ux]\n---\n\n# %s Experience v1.0 (derived)\n\n' "$NOW" "$AUTHOR" "$MODEL" "$PROJECT_NAME"
  printf '## 1. Interaction model
[Screens or states, navigation, first thirty seconds. Each element cites the intent persona or story it serves.]

'
  printf '## 2. Design tokens
[Colour, type, spacing, radius, motion. Source of truth is the mockup when one exists.]

'
  printf '## 3. Copy rules
[Voice, banned terms, error and empty-state patterns.]

'
  printf '## 4. Mockup
[Path to the interactive mockup and its screenshots, both themes, phone and desktop.]

'
  printf '## 5. Accessibility
[Target level and how each SPEC accessibility clause is met.]
'
} > "$ROOT/experience.md"

for play in scaffold commit deploy build; do
  {
    fm "spec-prep,plays,$play" "Play: $play"
    printf '## Reads\n[Every variable and its location, e.g. deployment target: intent.md section 3. Never store the value.]\n\n'
    printf '## Preconditions\n\n## Steps\n[Ordered, deterministic, each step references SPEC-IDs.]\n\n'
    printf '## Halt conditions\n[When to stop and surface to a human rather than guess.]\n\n'
    printf '## Ledger emission\n[What this play appends to ledger/ledger.md on completion.]\n'
  } > "$ROOT/plays/$play.md"
done

{
  fm "spec-prep,ledger,continuity" "Ledger (append-only)"
  printf '## 0001 0.0 decision\n- What: spec-prep tree scaffolded for %s.\n- Why: project kickoff.\n- Effect: created intent, spec, context, substrate, constitution, plays, ledger.\n- Outcome: tree created, validation pending.\n' "$PROJECT_NAME"
} > "$ROOT/ledger/ledger.md"

{
  fm "spec-prep,standing,continuity" "Standing"
  printf '## Where this is\n%s was scaffolded. Artifacts are stubs awaiting intake-driven content.\n\n' "$PROJECT_NAME"
  printf '## Last decisions that matter\n- 0001: tree scaffolded.\n\n'
  printf '## Not yet decided\nAll content. Intake and the Confidence Gate come next.\n\n'
  printf '## Next\nRun Phase 1 intake, then Phase 2 research.\n\n'
  printf '## Substrate note\nDeclared S0 (templates only), empirical memory empty.\n'
} > "$ROOT/ledger/standing.md"

{
  fm "spec-prep,evals,pointer" "Eval store location"
  printf 'The held-out evals bound to spec EVAL-IDs live OUTSIDE this repository. Genuine held-out isolation also requires an evaluator context inaccessible to the implementing agent; an external path alone does not establish that boundary.\n\nStore: %s/evals.md\n\nValidate with: spec-prep-validate.py %s --evals %s\n' "$EVALS_DIR" "$ROOT" "$EVALS_DIR"
} > "$ROOT/EVALS-LOCATION.md"

if [ ! -e "$EVALS_DIR/evals.md" ]; then
  {
    fm "spec-prep,evals,held-out" "$PROJECT_NAME held-out evals"
    printf '## EVAL-001\n- Bound clause: SPEC-001\n- Asserts: [pass/fail statement, no implementation reference]\n- Method: [manual check, scripted scenario, metric with threshold]\n- Fixture: [inputs, stored here, never in the repo]\n'
  } > "$EVALS_DIR/evals.md"
fi

if [ ! -e "$PARENT_DIR/AGENTS.md" ]; then
  {
    printf '# AGENTS.md\n\nSession-scoped instructions for coding agents in this repository.\n\n'
    printf '## Before anything else\nRead %s/ledger/standing.md and the last five entries of %s/ledger/ledger.md, then intent.md and spec.md in that folder.\n\n' "${ROOT#$PARENT_DIR/}" "${ROOT#$PARENT_DIR/}"
    printf '## Governance and initiation\nRead .specify/memory/constitution.md when present; it is the project governance authority and must not be duplicated here. Specification preparation creates it from authorized principles. Read reset-handoff.md before changes when it exists. Preparation only: do not implement or launch after generating tasks. A later explicit implementation request requires the verified receipt, native tasks and current project-initiation authority.\n\n'
    printf '## Standing gates\n- Every change maps to a SPEC-ID; if it cannot, stop and append a ledger entry instead of guessing.\n- Record material decisions, outcomes and task-state changes in the ledger; refresh standing.md when resumable state changes.\n- Goal changes enter intent; behavior, architecture and workflow corrections enter their owning layer and propagate to affected dependents; reusable plays read their variables.\n- Claims of done require evidence: commands run, results, screenshots for UI.\n- Never search for, open or request the held-out evals.\n'
  } > "$PARENT_DIR/AGENTS.md"
fi
if [ ! -e "$PARENT_DIR/CLAUDE.md" ]; then
  printf '@AGENTS.md\n' > "$PARENT_DIR/CLAUDE.md"
fi

echo "scaffolded: $ROOT"
echo "evals: $EVALS_DIR/evals.md (outside the repo)"
echo "next: fill intent.md and spec.md (human), let the system derive context.md, experience.md and plays/, then run spec-prep-validate.py $ROOT --evals $EVALS_DIR"
