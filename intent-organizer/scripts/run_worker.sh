#!/usr/bin/env bash
# run_worker.sh - run one rendered brief as a headless omp session (default model: muse-spark-1.3-contributor).
# Usage (from Windows Git Bash, as its own background task; never nohup, the session must stay attached):
#   MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu -e bash -l <skill>/scripts/run_worker.sh <brief.md> [max-time] [thinking] [model]
#   <brief.md> is a WSL path, e.g. /mnt/c/.../org/briefs/WORKER-A-downloads-1.md ; the log is <brief>.log
# `bash -l` matters: provider keys live in the login environment. No --auto-approve: the brief only needs
# read/search tools plus writing its own output file.
set -uo pipefail
export PATH="$HOME/.bun/bin:$HOME/.local/bin:$HOME/.npm-global/bin:$PATH"
BRIEF="$1"; MAXT="${2:-55m}"; THINK="${3:-high}"; MODEL="${4:-opencode-go/muse-spark-1.3-contributor}"
[ -f "$BRIEF" ] || { echo "no brief: $BRIEF" >&2; exit 2; }
NAME="$(basename "$BRIEF" .md)"
LOG="${BRIEF%.md}.log"
mkdir -p "$HOME/.omp/organizer-sessions" "/tmp/omp-work/$NAME"
cd "/tmp/omp-work/$NAME" || exit 3
echo "[$(date -Is)] start $NAME model=$MODEL thinking=$THINK max=$MAXT" > "$LOG"
omp -p --model "$MODEL" --thinking "$THINK" \
  --tools read,bash,glob,grep,find,web_search,write \
  --max-time "$MAXT" --no-title \
  --session-dir "$HOME/.omp/organizer-sessions" \
  "@$BRIEF" "Execute the task described in the attached brief exactly. Write the output file it specifies. When finished reply with DONE, the output path, and counts per decision." >> "$LOG" 2>&1
RC=$?
echo "[$(date -Is)] exit=$RC $NAME" >> "$LOG"
exit $RC
