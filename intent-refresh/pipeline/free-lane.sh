#!/usr/bin/env bash
# free-lane.sh: run one text-only job on a free opencode model, fully isolated.
#
#   free-lane.sh MODEL PROMPT_FILE OUT_FILE
#
# - Pure text in, text out: the model gets no shell, no edits, no web and no
#   folders outside an empty work dir (opencode.json below denies them all).
# - XDG_* point at a private state folder, so the operator's own opencode
#   config, agents and database are never read or written. (2026-11-05: the
#   operator's install fails on a database migration and an invalid agent
#   file; isolation sidesteps both without touching them.)
# - Callers must pass REDACTED text only. Prompt text goes to a free endpoint.
# - Exit 0 only when OUT_FILE is non-empty.
set -euo pipefail
[ $# -eq 3 ] || { echo "usage: free-lane.sh MODEL PROMPT_FILE OUT_FILE" >&2; exit 2; }
MODEL=$1; PROMPT=$(realpath -- "$2"); OUT=$(realpath -m -- "$3")
STATE=${FREE_LANE_STATE:-$HOME/.local/state/intent-refresh/free-lane}
WORK=$(mktemp -d "${TMPDIR:-/tmp}/free-lane.XXXXXX")
trap 'rm -rf "$WORK"' EXIT
mkdir -p "$STATE/data" "$STATE/config" "$STATE/cache"
printf '%s' '{"$schema":"https://opencode.ai/config.json","permission":{"edit":"deny","webfetch":"deny","external_directory":"deny","bash":"deny"}}' > "$WORK/opencode.json"
cd "$WORK"
XDG_DATA_HOME="$STATE/data" XDG_CONFIG_HOME="$STATE/config" XDG_CACHE_HOME="$STATE/cache" \
  timeout "${FREE_LANE_TIMEOUT:-600}" opencode run -m "$MODEL" --dir "$WORK" "$(cat "$PROMPT")" \
  < /dev/null 2> "$OUT.err" | sed -e 's/\x1b\[[0-9;]*m//g' > "$OUT.raw"
# Drop opencode's banner lines ("> build · model") before the answer.
grep -v -E '^> (build|plan) · ' "$OUT.raw" | sed '/./,$!d' > "$OUT"
rm -f "$OUT.raw"
[ -s "$OUT" ]
