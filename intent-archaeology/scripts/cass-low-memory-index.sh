#!/usr/bin/env bash
# Resource-bounded CASS refresh launcher for low-memory hosts.
#
# Default behavior is deliberately non-mutating: it prints the exact command.
# Pass --execute only after reviewing the profile and a current CASS health
# read-back. The cgroup limits are authoritative even if a CASS environment
# tuning variable is ignored by an installed binary.
set -euo pipefail

memory_max="1536M"
cpu_quota="50%"
runtime_max="90s"
idempotency_key="intent-archaeology-low-memory-refresh"
execute=0

usage() {
  cat <<'EOF'
Usage: cass-low-memory-index.sh [--execute] [--memory-max SIZE] [--cpu-quota PCT] [--runtime-max DURATION] [--idempotency-key KEY]

Prints a cgroup-bounded incremental CASS index command by default. With
--execute, runs it in a transient user-systemd scope with hard memory, CPU,
and elapsed-time limits. It never enables watch mode or a full rebuild.
EOF
}

while (($#)); do
  case "$1" in
    --execute) execute=1 ;;
    --memory-max) memory_max="$2"; shift ;;
    --cpu-quota) cpu_quota="$2"; shift ;;
    --runtime-max) runtime_max="$2"; shift ;;
    --idempotency-key) idempotency_key="$2"; shift ;;
    -h|--help) usage; exit 0 ;;
    *) printf 'Unknown argument: %s\n' "$1" >&2; usage >&2; exit 2 ;;
  esac
  shift
done

command -v cass >/dev/null || { printf 'cass is not on PATH\n' >&2; exit 127; }
command -v systemd-run >/dev/null || { printf 'systemd-run is required for cgroup enforcement\n' >&2; exit 127; }

cmd=(
  systemd-run --user --wait --collect
  "--property=MemoryMax=${memory_max}"
  "--property=CPUQuota=${cpu_quota}"
  "--property=RuntimeMaxSec=${runtime_max}"
  --
  cass index --json --no-progress-events
  "--idempotency-key=${idempotency_key}"
)

printf 'CASS refresh profile: MemoryMax=%s CPUQuota=%s RuntimeMaxSec=%s\n' "$memory_max" "$cpu_quota" "$runtime_max"
printf 'Command: '
printf '%q ' "${cmd[@]}"
printf '\n'

if (( ! execute )); then
  printf 'Dry presentation only. Re-run with --execute after reviewing current cass health.\n'
  exit 0
fi

exec "${cmd[@]}"
