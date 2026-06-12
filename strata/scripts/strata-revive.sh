#!/usr/bin/env bash
# strata-revive.sh
# Reconstructs where a dormant STRATA project is standing, without diff archaeology.
# Pure read. Mutates nothing. This is the anti-dreamstate tool.
#
# Usage:
#   ./strata-revive.sh <path-to-strata-project-dir> [num-ledger-entries]
#
# Prints standing.md in full, then the last N ledger entries (default 5),
# then the immediate next action. A resuming session reads this BEFORE code.

set -euo pipefail

if [ "$#" -lt 1 ]; then
  echo "usage: $0 <path-to-strata-project-dir> [num-ledger-entries]" >&2
  exit 2
fi

ROOT="$1"
N="${2:-5}"

STANDING="$ROOT/ledger/standing.md"
LEDGER="$ROOT/ledger/ledger.md"

if [ ! -f "$STANDING" ]; then
  echo "error: $STANDING not found; this project has no continuity spine and must be triaged manually" >&2
  exit 1
fi
if [ ! -f "$LEDGER" ]; then
  echo "error: $LEDGER not found; continuity record missing" >&2
  exit 1
fi

echo "=============================================================="
echo " STRATA REVIVE :: $ROOT"
echo " Read this before touching code. No archaeology required."
echo "=============================================================="
echo
echo "----- STANDING (full) ----------------------------------------"
# Strip the frontmatter block for readability, keep the body.
awk 'BEGIN{fm=0} /^---$/{fm++; next} fm>=2{print}' "$STANDING"
echo
echo "----- LAST $N LEDGER ENTRIES ---------------------------------"
# Ledger entries begin with a line like "## NNNN ...". Print the last N blocks.
awk -v n="$N" '
  /^## [0-9]+ /{ idx++; starts[idx]=NR }
  { lines[NR]=$0 }
  END{
    total=NR
    first = (idx>n) ? starts[idx-n+1] : (starts[1] ? starts[1] : 1)
    for (i=first; i<=total; i++) print lines[i]
  }
' "$LEDGER"
echo
echo "----- RESUME RULE --------------------------------------------"
echo "Proceed from the 'Next' section of STANDING above."
echo "If you find yourself reading diffs to reconstruct intent, the"
echo "ledger failed: record that failure as the next ledger entry."
echo "=============================================================="
