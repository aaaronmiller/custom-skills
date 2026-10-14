#!/usr/bin/env bash
# run-omp-worker.sh - launch one headless omp worker (opencode-go / muse-spark-1.3-contributor)
#
# From Windows (Git Bash), ALWAYS like this (login shell = provider keys; MSYS_NO_PATHCONV stops
# Git Bash from rewriting /mnt/c paths; run it as a background Bash task so wsl.exe stays open -
# a nohup'd child dies with SIGHUP when wsl.exe exits):
#   MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu -e bash -l \
#     /mnt/c/Users/Administrator/.claude/skills/system-checkup/scripts/run-omp-worker.sh \
#     /mnt/c/performance-diagnostics/checkup-YYYYMMDD W1-wsl-audit 45m high
#
# Args: <checkup-dir (WSL path)> <brief-name> [max-time] [thinking]
#   The brief is read from <checkup>/workers/prompts/<brief-name>.md (render it first with
#   render-briefs.sh). The worker must write its own output under <checkup>/workers/.
# Uses omp's normal login-shell provider auth (no key export, nothing printed) and omp's default
# approval policy (no --auto-approve). Toolset: read/search/write-file + bash.
set -uo pipefail
export PATH="$HOME/.bun/bin:$HOME/.local/bin:$HOME/.npm-global/bin:$PATH"
CK="$1"; NAME="$2"; MAXT="${3:-45m}"; THINK="${4:-high}"
MODEL="${OMP_WORKER_MODEL:-opencode-go/muse-spark-1.3-contributor}"
PROMPT="$CK/workers/prompts/$NAME.md"
LOG="$CK/workers/$NAME.stdout.log"
[ -f "$PROMPT" ] || { echo "no brief: $PROMPT" >&2; exit 2; }
mkdir -p "$HOME/.omp/checkup-sessions" "/tmp/omp-work/$NAME"
cd "/tmp/omp-work/$NAME" || exit 3
echo "[$(date -Is)] start $NAME model=$MODEL thinking=$THINK max=$MAXT" > "$LOG"
omp -p --model "$MODEL" --thinking "$THINK" \
  --tools read,bash,glob,grep,find,web_search,write \
  --max-time "$MAXT" --no-title \
  --session-dir "$HOME/.omp/checkup-sessions" \
  "@$PROMPT" "Execute the task described in the attached brief exactly. Write the output file(s) it specifies. When finished reply with DONE and the output path(s)." >> "$LOG" 2>&1
RC=$?
echo "[$(date -Is)] exit=$RC $NAME" >> "$LOG"
exit $RC
