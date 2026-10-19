#!/usr/bin/env bash
# agy-run.sh: quota-aware driver for headless Antigravity (agy -p) units.
#
# Usage:
#   agy-run.sh units.tsv
#
# units.tsv: tab-separated, one unit per line, '#' lines ignored:
#   unit_id <TAB> pool <TAB> model_id <TAB> prompt_file <TAB> done_marker <TAB> verify_cmd <TAB> requires
#   pool is a free label for the quota pool, normally "claude" or "gemini".
#   verify_cmd and requires are optional (leave the field empty). requires is a comma-separated list
#   of unit_ids that must be done (in this run or earlier) before this unit may start.
#   CRLF line endings are tolerated.
#
# Behavior:
#   - Skips units whose done_marker exists.
#   - Runs each unit as a fresh agy session with stdin from /dev/null and stream-json logging.
#   - On RESOURCE_EXHAUSTED, reads "Resets in XhYmZs":
#       reset <= SHORT_MAX_SECONDS  -> short window: sleep until reset + jitter, rerun the same unit.
#       reset >  SHORT_MAX_SECONDS  -> weekly lock: park every remaining unit on that pool, continue others.
#   - After a unit, runs verify_cmd (if given). A failing verify demotes the marker to <marker>.failed.
#   - Units whose requires are not done are reported as blocked and skipped (never run on stale inputs).
#   - Optionally detects writes under FORBIDDEN_ROOTS during a unit.
#   - Holds a lock in LOG_DIR so two drivers (for example overlapping cron runs) never run one campaign twice.
#
# Exit codes: 0 all units done; 75 one or more pools parked on a weekly lock; 1 one or more units failed;
#             73 another driver holds the lock for this LOG_DIR.
# Note: the prompt is passed as an argument and is visible in `ps` on shared machines; keep secrets out of prompts.
#
# Environment (all optional):
#   AGY_BIN              agy executable (default: agy)
#   AGY_EXTRA_ARGS       extra flags appended to every agy call
#                        (default: --dangerously-skip-permissions --print-timeout 0; confirm both with `agy --help`)
#   MAX_PROMPT_BYTES     largest prompt passed via -p (default: 122880). Linux caps one argv string at 128 KB;
#                        reference the context pack by path instead of inlining it.
#   LOG_DIR              log and status directory (default: ./agy-logs)
#   WALL_GUARD_SECONDS   hard wall-clock limit per attempt (default: 14400, i.e. 4h); 0 disables
#   SHORT_MAX_SECONDS    longest reset still treated as the short window (default: 18900, i.e. 5h15m)
#   JITTER_SECONDS       extra wait after a short reset (default: 180)
#   MAX_SHORT_RETRIES    short-window relaunches per unit (default: 3)
#   FORBIDDEN_ROOTS      colon-separated directories the worker must not modify
#   DRY_RUN              if 1, print commands without running agy

set -u

MANIFEST="${1:-}"
if [ -z "$MANIFEST" ] || [ ! -f "$MANIFEST" ]; then
  printf 'usage: %s units.tsv\n' "$0" >&2
  exit 2
fi

AGY_BIN="${AGY_BIN:-agy}"
AGY_EXTRA_ARGS="${AGY_EXTRA_ARGS:---dangerously-skip-permissions --print-timeout 0}"
MAX_PROMPT_BYTES="${MAX_PROMPT_BYTES:-122880}"
LOG_DIR="${LOG_DIR:-./agy-logs}"
WALL_GUARD_SECONDS="${WALL_GUARD_SECONDS:-14400}"
SHORT_MAX_SECONDS="${SHORT_MAX_SECONDS:-18900}"
JITTER_SECONDS="${JITTER_SECONDS:-180}"
MAX_SHORT_RETRIES="${MAX_SHORT_RETRIES:-3}"
FORBIDDEN_ROOTS="${FORBIDDEN_ROOTS:-}"
DRY_RUN="${DRY_RUN:-0}"

mkdir -p "$LOG_DIR"
LOCK_DIR="$LOG_DIR/.driver.lock"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  printf 'another agy-run.sh holds %s; remove it only if no driver is running\n' "$LOCK_DIR" >&2
  exit 73
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null' EXIT
trap 'exit 130' INT TERM
STATUS_FILE="$LOG_DIR/status.tsv"
PARKED_POOLS=" "
DONE_IDS=" "
FAILED=0

log() { printf '%s %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*" | tee -a "$LOG_DIR/driver.log" >&2; }
status() { printf '%s\t%s\t%s\t%s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$1" "$2" "$3" >> "$STATUS_FILE"; }

# Pick a wall-clock guard command if one exists (GNU timeout on Linux, gtimeout via coreutils on macOS).
GUARD=""
if [ "$WALL_GUARD_SECONDS" != "0" ]; then
  if command -v timeout >/dev/null 2>&1; then GUARD="timeout"
  elif command -v gtimeout >/dev/null 2>&1; then GUARD="gtimeout"
  else log "WARN no timeout/gtimeout found; running without a wall-clock guard"
  fi
fi

# Convert "6d2h", "4h33m58s", "162h51m37s", "12m", "45s" to seconds. Fails (prints nothing) if
# the spec is empty or unparseable, which the caller treats as a weekly lock (the safe direction).
reset_to_seconds() {
  local spec="$1" d=0 h=0 m=0 s=0
  [ -z "$spec" ] && return 1
  case "$spec" in *d*) d="${spec%%d*}"; spec="${spec#*d}";; esac
  case "$spec" in *h*) h="${spec%%h*}"; spec="${spec#*h}";; esac
  case "$spec" in *m*) m="${spec%%m*}"; spec="${spec#*m}";; esac
  case "$spec" in *s*) s="${spec%%s*}";; esac
  case "$d$h$m$s" in *[!0-9]*|'') return 1;; esac
  printf '%s\n' $(( 10#$d * 86400 + 10#$h * 3600 + 10#$m * 60 + 10#$s ))
}

# A quota failure is an AGY_ERROR line near the end of the log. Workers that merely quote old
# errors in tool output (forensics) emit JSON events, not lines starting with AGY_ERROR:.
quota_error_line() {
  tail -n 30 "$1" 2>/dev/null | grep '^AGY_ERROR:.*RESOURCE_EXHAUSTED' | tail -n 1
}

# Extract the "Resets in ..." duration token from a quota error line.
reset_spec_from() {
  printf '%s\n' "$1" | grep -o 'Resets in [0-9hms]*' | tail -n 1 | sed 's/Resets in //'
}

check_forbidden() {
  local stamp="$1" root hits=""
  [ -z "$FORBIDDEN_ROOTS" ] && return 0
  local IFS=':'
  for root in $FORBIDDEN_ROOTS; do
    [ -d "$root" ] || continue
    hits="$hits$(find "$root" -newer "$stamp" -type f 2>/dev/null | head -n 20)"
  done
  if [ -n "$hits" ]; then
    log "FORBIDDEN WRITES detected:"; printf '%s\n' "$hits" | tee -a "$LOG_DIR/driver.log" >&2
    return 1
  fi
  return 0
}

run_unit() {
  local id="$1" pool="$2" model="$3" prompt_file="$4" marker="$5" verify="$6"
  local attempt=0 logf stamp rc spec secs prompt qline

  if [ ! -f "$prompt_file" ]; then
    log "FAIL $id prompt file missing: $prompt_file"; status "$id" failed "missing prompt"; FAILED=1; return
  fi
  if [ "$(wc -c < "$prompt_file")" -gt "$MAX_PROMPT_BYTES" ]; then
    log "FAIL $id prompt is over $MAX_PROMPT_BYTES bytes; reference the context pack by path instead of inlining it"
    status "$id" failed "prompt too large"; FAILED=1; return
  fi

  while :; do
    attempt=$((attempt + 1))
    logf="$LOG_DIR/$id.attempt$attempt.jsonl"
    stamp="$LOG_DIR/.stamp-$id-$attempt"
    : > "$stamp"
    prompt="$(cat "$prompt_file")"
    log "RUN $id pool=$pool model=$model attempt=$attempt log=$logf"

    if [ "$DRY_RUN" = "1" ]; then
      log "DRY $AGY_BIN -p <$prompt_file> --model $model --output-format stream-json $AGY_EXTRA_ARGS"
      status "$id" dry-run "$model"; return
    fi

    # shellcheck disable=SC2086
    if [ -n "$GUARD" ]; then
      "$GUARD" "$WALL_GUARD_SECONDS" "$AGY_BIN" -p "$prompt" --model "$model" --output-format stream-json $AGY_EXTRA_ARGS < /dev/null > "$logf" 2>&1
    else
      "$AGY_BIN" -p "$prompt" --model "$model" --output-format stream-json $AGY_EXTRA_ARGS < /dev/null > "$logf" 2>&1
    fi
    rc=$?

    if ! check_forbidden "$stamp"; then
      status "$id" failed "forbidden writes"; FAILED=1; rm -f "$stamp"; return
    fi
    rm -f "$stamp"

    qline=""
    [ -f "$marker" ] || qline="$(quota_error_line "$logf")"
    if [ -n "$qline" ]; then
      spec="$(reset_spec_from "$qline")"
      secs="$(reset_to_seconds "$spec" 2>/dev/null || true)"
      if [ -z "$secs" ]; then
        log "QUOTA $id unparseable reset ('$spec'); treating as weekly lock for pool $pool"
        secs=$((SHORT_MAX_SECONDS + 1))
      fi
      if [ "$secs" -le "$SHORT_MAX_SECONDS" ]; then
        if [ "$attempt" -gt "$MAX_SHORT_RETRIES" ]; then
          log "FAIL $id exceeded $MAX_SHORT_RETRIES short-window relaunches"; status "$id" failed "short retries exhausted"; FAILED=1; return
        fi
        log "QUOTA $id short window, reset in $spec; sleeping $((secs + JITTER_SECONDS))s then resuming from checkpoint"
        status "$id" short-wait "$spec"
        sleep $((secs + JITTER_SECONDS))
        continue
      fi
      log "QUOTA $id WEEKLY lock on pool $pool, reset in $spec; parking pool"
      status "$id" parked "weekly $spec"
      PARKED_POOLS="$PARKED_POOLS$pool "
      printf '%s\t%s\n' "$pool" "$spec" >> "$LOG_DIR/parked-pools.tsv"
      return
    fi

    if [ "$rc" -eq 124 ]; then
      log "GUARD $id hit the ${WALL_GUARD_SECONDS}s wall-clock guard; a relaunch will resume from its checkpoint"
    fi

    if [ ! -f "$marker" ]; then
      if [ "$rc" -eq 124 ] && [ "$attempt" -le "$MAX_SHORT_RETRIES" ]; then continue; fi
      log "FAIL $id exited rc=$rc without its done-marker ($marker)"; status "$id" failed "no marker rc=$rc"; FAILED=1; return
    fi

    if [ -n "$verify" ]; then
      if ! sh -c "$verify" > "$LOG_DIR/$id.verify.log" 2>&1; then
        command mv -f "$marker" "$marker.failed"
        log "FAIL $id verify failed; marker demoted to $marker.failed (see $LOG_DIR/$id.verify.log)"
        status "$id" failed "verify"; FAILED=1; return
      fi
    fi

    log "DONE $id"; status "$id" "done" "$model"; DONE_IDS="$DONE_IDS$id "; return
  done
}

TAB="$(printf '\t')"
US="$(printf '\037')"
while IFS= read -r line || [ -n "$line" ]; do
  line="${line%"$(printf '\r')"}"
  case "$line" in ''|'#'*) continue;; esac
  # Split on a non-whitespace separator so empty optional fields are preserved.
  line="${line//$TAB/$US}"
  IFS="$US" read -r id pool model prompt_file marker verify requires <<EOF_LINE
$line
EOF_LINE
  if [ -f "$marker" ]; then
    log "SKIP $id (done-marker present)"; DONE_IDS="$DONE_IDS$id "; continue
  fi
  case "$PARKED_POOLS" in *" $pool "*)
    log "PARK $id (pool $pool is weekly-locked)"; status "$id" parked "pool locked"; continue;;
  esac
  blocked=""
  for req in $(printf '%s' "${requires:-}" | tr ',' ' '); do
    case "$DONE_IDS" in *" $req "*) ;; *) blocked="$blocked $req";; esac
  done
  if [ -n "$blocked" ]; then
    log "BLOCK $id (waiting on:$blocked)"; status "$id" blocked "needs$blocked"; continue
  fi
  run_unit "$id" "$pool" "$model" "$prompt_file" "$marker" "${verify:-}"
done < "$MANIFEST"

if [ "$FAILED" -ne 0 ]; then
  log "SUMMARY one or more units FAILED; status in $STATUS_FILE"
fi
if [ "$PARKED_POOLS" != " " ]; then
  log "SUMMARY parked pools:$PARKED_POOLS(see $LOG_DIR/parked-pools.tsv); status in $STATUS_FILE"
  exit 75
fi
if [ "$FAILED" -ne 0 ]; then
  exit 1
fi
log "SUMMARY all units done"
exit 0
