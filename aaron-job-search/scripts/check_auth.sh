#!/bin/bash
# Quick check which sites are authenticated
B=~/.claude/skills/gstack/browse/dist/browse
STATE_DIR="/home/cheta/tmp/.gstack/browse-states"

echo "=== Auth Status ==="
for site in wellfound builtin linkedin greenhouse ashby yc-was; do
    state_file="$STATE_DIR/job-$site.json"
    if [ -f "$state_file" ]; then
        size=$(stat -c%s "$state_file" 2>/dev/null || echo "0")
        if [ "$size" -gt 100 ]; then
            echo "  ✓ $site (${size} bytes — has cookies)"
        else
            echo "  ~ $site (${size} bytes — may need re-auth)"
        fi
    else
        echo "  ✗ $site (not set up)"
    fi
done
