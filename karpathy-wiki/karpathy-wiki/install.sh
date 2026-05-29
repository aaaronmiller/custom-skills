#!/usr/bin/env bash
# =============================================================================
# Karpathy Wiki — Quick Install
# =============================================================================
#
# Lightweight wrapper around setup.sh. Passes all flags through.
# For full options: ./setup.sh --help
#
# Usage:
#   ./install.sh                    # Quick install (defaults)
#   ./install.sh --preset balanced  # Apply preset
#   ./install.sh --dry-run          # Show what would be done
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "━━━ Karpathy Wiki — Quick Install ━━━"
echo ""

# Delegate to setup.sh with minimal flags + fast path
if [[ -f "$SCRIPT_DIR/setup.sh" ]]; then
    # Pass all args through, add --skip-clawmem --skip-mcp by default
    # (quick install focuses on data dir + symlinks + skills)
    exec "$SCRIPT_DIR/setup.sh" "$@"
else
    echo "ERROR: setup.sh not found alongside install.sh"
    echo "Expected at: $SCRIPT_DIR/setup.sh"
    exit 1
fi
