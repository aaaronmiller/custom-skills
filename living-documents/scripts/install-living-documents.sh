#!/usr/bin/env sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
UNIT_TEMPLATE="$ROOT/systemd/living-documents-renderer.service"
WATCHER_TEMPLATE="$ROOT/systemd/living-documents-projection-watcher.service"
UNIT_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
UNIT_TARGET="$UNIT_DIR/living-documents-renderer.service"
WATCHER_TARGET="$UNIT_DIR/living-documents-projection-watcher.service"

if [ "${1-}" = "--help" ]; then
  printf '%s\n' "Usage: install-living-documents.sh [--enable-renderer] [--install-hooks] [--sync-skills]"
  exit 0
fi

ENABLE_RENDERER=0
INSTALL_HOOKS=0
SYNC_SKILLS=0
while [ "$#" -gt 0 ]; do
  case "$1" in
    --enable-renderer) ENABLE_RENDERER=1 ;;
    --install-hooks) INSTALL_HOOKS=1 ;;
    --sync-skills) SYNC_SKILLS=1 ;;
    *)
      printf '%s\n' "Unknown option: $1" >&2
      exit 2
      ;;
  esac
  shift
done

mkdir -p "$UNIT_DIR"
for template in "$UNIT_TEMPLATE" "$WATCHER_TEMPLATE"; do
  case "$template" in
    "$UNIT_TEMPLATE") target="$UNIT_TARGET" ;;
    *) target="$WATCHER_TARGET" ;;
  esac
  temp=$(mktemp "$UNIT_DIR/.living-documents.XXXXXX")
  sed "s|@SKILL_ROOT@|$ROOT|g" "$template" > "$temp"
  mv "$temp" "$target"
done
systemctl --user daemon-reload

if [ "$ENABLE_RENDERER" -eq 1 ]; then
  systemctl --user enable --now living-documents-renderer.service living-documents-projection-watcher.service
fi

if [ "$INSTALL_HOOKS" -eq 1 ]; then
  python3 "$ROOT/scripts/install-living-documents-hooks.py" --apply
fi

if [ "$SYNC_SKILLS" -eq 1 ]; then
  skillshare sync
fi

printf '%s\n' "Installed portable renderer unit: $UNIT_TARGET"
printf '%s\n' "Installed portable watcher unit: $WATCHER_TARGET"
