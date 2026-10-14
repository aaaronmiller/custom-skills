#!/usr/bin/env bash
# deploy-windows.sh - copy this skill from the custom-skills repo (source of truth) to the Windows
# Claude Code skills folder. Windows Claude Code only loads skills from
# C:\Users\Administrator\.claude\skills, and it must work even when WSL is wedged, so the Windows side
# gets a real copy rather than a link into \\wsl.localhost.
# Usage (inside WSL): bash ~/code/custom-skills/system-checkup/scripts/deploy-windows.sh
set -euo pipefail
SRC="$(cd "$(dirname "$0")/.." && pwd)"
DST=/mnt/c/Users/Administrator/.claude/skills/system-checkup
mkdir -p "$DST"
# mirror: copy everything, then remove files that no longer exist in the source
cp -r "$SRC"/. "$DST"/
( cd "$DST" && find . -type f | while read -r f; do [ -e "$SRC/$f" ] || { echo "removing stale $f"; rm -f -- "$f"; }; done )
echo "deployed $SRC -> $DST ($(find "$DST" -type f | wc -l) files)"
