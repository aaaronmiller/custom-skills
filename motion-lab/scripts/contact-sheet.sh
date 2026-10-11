#!/usr/bin/env bash
# contact-sheet.sh: put every Nth frame on one image, each tile labelled with its frame number,
# so a review can name exact frames. Read the PNG like a storyboard.
#
#   contact-sheet.sh [frames_dir=out/frames] [every=12] [cols=4] [rows=3] [out=out/contact.png]
#
# From "Opus 5.5 Motion Lab" by @flxrnc (X, 2026-09-30); frame labels are an addition.
set -euo pipefail
dir=${1:-out/frames}
every=${2:-12}
cols=${3:-4}
rows=${4:-3}
out=${5:-out/contact.png}

[ -f "$dir/0000.png" ] || { echo "contact-sheet.sh: $dir/0000.png not found; render from frame 0 first" >&2; exit 1; }
mkdir -p "$(dirname "$out")"

label=""
filters=$(ffmpeg -hide_banner -filters 2>/dev/null || true)   # no pipe into grep -q: pipefail + SIGPIPE
if [[ $filters == *" drawtext "* ]]; then
  # Label before select, so n is the source frame number rather than the tile index.
  label="drawtext=text='%{eif\:n\:d}':x=12:y=12:fontsize=h/14:fontcolor=white:box=1:boxcolor=black@0.6:boxborderw=6,"
fi

ffmpeg -v error -y -start_number 0 -i "$dir/%04d.png" \
  -vf "${label}select='not(mod(n\,$every))',scale=400:-1,tile=${cols}x${rows}:padding=4:color=white" \
  -frames:v 1 "$out"
echo "contact sheet: every ${every}th frame, ${cols}x${rows} -> $out"
