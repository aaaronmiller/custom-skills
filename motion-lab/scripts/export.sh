#!/usr/bin/env bash
# export.sh: frames to an X-ready MP4 or GIF, a loop-seam check, and audio muxing.
#
#   export.sh mp4  [fps=24] [frames_dir=out/frames] [out=out/anim.mp4]
#   export.sh gif  [fps=24] [frames_dir=out/frames] [out=out/anim.gif] [width=1200]
#   export.sh loop [in=out/anim.mp4] [out=out/loop_check.mp4]      plays it 3 times back to back
#   export.sh mux  video.mp4 out.mp4 audio.wav [more.wav ...]      mix, -14 LUFS, -1 dBTP, mux
#   export.sh loudness file                                        integrated LUFS and true peak
#
# Commands from "Opus 5.5 Motion Lab" by @flxrnc (X, 2026-09-30). X limits: GIF 15 MB,
# up to 1280x1080, at most 350 frames; video H.264 High, yuv420p, AAC, up to 60 fps.
set -euo pipefail
cmd=${1:-}; shift || true

case "$cmd" in
  mp4)
    fps=${1:-24}; dir=${2:-out/frames}; out=${3:-out/anim.mp4}
    ffmpeg -v error -y -framerate "$fps" -start_number 0 -i "$dir/%04d.png" \
      -c:v libx264 -profile:v high -pix_fmt yuv420p -crf 18 -movflags +faststart "$out"
    echo "mp4 -> $out ($(ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames -of csv=p=0 "$out") frames)"
    ;;
  gif)
    fps=${1:-24}; dir=${2:-out/frames}; out=${3:-out/anim.gif}; width=${4:-1200}
    n=$(find "$dir" -maxdepth 1 -name '[0-9][0-9][0-9][0-9].png' | wc -l)
    [ "$n" -le 350 ] || echo "warning: $n frames; X takes at most 350 frames in a GIF" >&2
    # One palette for the whole clip keeps colors from flickering between frames.
    ffmpeg -v error -y -framerate "$fps" -start_number 0 -i "$dir/%04d.png" \
      -vf "scale=${width}:-1:flags=lanczos,split[a][b];[a]palettegen=stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle" \
      -loop 0 "$out"
    size=$(stat -c %s "$out" 2>/dev/null || stat -f %z "$out")
    [ "$size" -le 15728640 ] || echo "warning: $out is over X's 15 MB GIF limit" >&2
    echo "gif -> $out ($n frames, $((size / 1024)) KB)"
    ;;
  loop)
    in=${1:-out/anim.mp4}; out=${2:-out/loop_check.mp4}
    ffmpeg -v error -y -stream_loop 2 -i "$in" -c copy "$out"
    echo "loop check -> $out (watch the two seams)"
    ;;
  mux)
    [ $# -ge 3 ] || { echo "usage: export.sh mux video.mp4 out.mp4 audio.wav [more.wav ...]" >&2; exit 1; }
    video=$1; out=$2; shift 2
    tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
    # 1. Mix every audio input at its own level (no automatic halving).
    inputs=(); labels=""; k=0
    for a in "$@"; do inputs+=(-i "$a"); labels+="[$k:a]"; k=$((k + 1)); done
    if [ "$#" -gt 1 ]; then
      ffmpeg -v error -y "${inputs[@]}" -filter_complex "${labels}amix=inputs=$#:duration=first:normalize=0[a]" \
        -map "[a]" -c:a pcm_f32le "$tmp/mix.wav"
    else
      ffmpeg -v error -y -i "$1" -c:a pcm_f32le "$tmp/mix.wav"
    fi
    # 2. Two-pass loudness: measure, then apply one linear gain to -14 LUFS with peaks at -1 dBTP.
    #    A single pass rides the gain dynamically and misses the target on short loops.
    m=$(ffmpeg -hide_banner -i "$tmp/mix.wav" -af loudnorm=I=-14:TP=-1:LRA=11:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
    val() { printf '%s\n' "$m" | sed -n "s/.*\"$1\" : \"\\([^\"]*\\)\".*/\\1/p"; }
    ffmpeg -v error -y -i "$tmp/mix.wav" -af "loudnorm=I=-14:TP=-1:LRA=11:measured_I=$(val input_i):measured_TP=$(val input_tp):measured_LRA=$(val input_lra):measured_thresh=$(val input_thresh):offset=$(val target_offset):linear=true,aresample=48000" \
      -c:a pcm_f32le "$tmp/norm.wav"
    # 3. Mux under the picture. Video is copied untouched.
    ffmpeg -v error -y -i "$video" -i "$tmp/norm.wav" -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k \
      -shortest -movflags +faststart "$out"
    echo "mux -> $out"
    "$0" loudness "$out"
    ;;
  loudness)
    in=${1:?usage: export.sh loudness file}
    r=$(ffmpeg -hide_banner -nostats -i "$in" -vn -af ebur128=peak=true -f null - 2>&1)
    i=$(printf '%s\n' "$r" | sed -n 's/^ *I: *\(-*[0-9.]*\) LUFS/\1/p' | tail -1)
    tp=$(printf '%s\n' "$r" | sed -n 's/^ *Peak: *\(-*[0-9.]*\) dBFS/\1/p' | tail -1)
    echo "loudness $in: integrated ${i} LUFS (target -14), true peak ${tp} dBTP (target at most -1)"
    if awk -v i="$i" 'BEGIN { exit !(i < -15) }'; then
      echo "warning: more than 1 LU under target. The mix is too peaky to reach -14 under a -1 dBTP ceiling:" \
           "raise the bed or trim the loudest hits, then mux again." >&2
    fi
    ;;
  *)
    sed -n '2,10p' "$0"; exit 1 ;;
esac
