#!/bin/bash
# Restore authenticated browser state
# Usage: restore_auth.sh [site]
B=~/.claude/skills/gstack/browse/dist/browse

case "${1:-all}" in
    greenhouse) $B state load "job-greenhouse" 2>&1 ;;
    ashby) $B state load "job-ashby" 2>&1 ;;
    workday) $B state load "job-workday" 2>&1 ;;
    wellfound) $B state load "job-wellfound" 2>&1 ;;
    builtin) $B state load "job-builtin" 2>&1 ;;
    linkedin) $B state load "job-linkedin" 2>&1 ;;
    all)
        for site in wellfound builtin linkedin; do
            $B state load "job-$site" 2>&1 | tail -1
        done
        ;;
esac
