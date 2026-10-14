#!/usr/bin/env bash
# render-briefs.sh - copy the skill's worker briefs into a new checkup folder, filling placeholders.
# Usage (Git Bash or WSL): render-briefs.sh <skill-dir> <checkup-dir> <checkup-name e.g. checkup-20261201> <date e.g. 2026-12-01>
set -euo pipefail
SKILL="$1"; CK="$2"; NAME="$3"; DATE="$4"
mkdir -p "$CK/workers/prompts"
for f in "$SKILL"/prompts/W*.md; do
  sed -e "s/{{CHECKUP}}/$NAME/g" -e "s/{{DATE}}/$DATE/g" "$f" > "$CK/workers/prompts/$(basename "$f")"
done
ls "$CK/workers/prompts"
