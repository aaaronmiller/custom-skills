#!/bin/bash
# Install the `repo` command (git-audit-sync) onto PATH.
# Symlinks ~/.local/bin/repo -> this repo's bin/repo so updates are automatic.
set -euo pipefail

HERE="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="$HERE/bin/repo"
DEST_DIR="${1:-$HOME/.local/bin}"
DEST="$DEST_DIR/repo"

chmod +x "$TARGET"
mkdir -p "$DEST_DIR"
ln -sf "$TARGET" "$DEST"

echo "Installed: $DEST -> $TARGET"
case ":$PATH:" in
    *":$DEST_DIR:"*) ;;
    *) echo "Note: $DEST_DIR is not on PATH. Add it to use 'repo' directly." ;;
esac
