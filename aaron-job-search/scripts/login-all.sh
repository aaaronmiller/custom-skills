#!/bin/bash
# One-shot login for all job search sites
# Opens each site, you log in, state is saved. Takes ~5 minutes.

B=~/.claude/skills/gstack/browse/dist/browse

echo "========================================="
echo "  JOB SEARCH - LOGIN ALL SITES"
echo "========================================="
echo ""
echo "For each site, the browser will open."
echo "Log in with your credentials."
echo "When done, press ENTER to save and continue."
echo ""
read -p "Press ENTER to start..."

# Site list: name|url
SITES=(
    "wellfound|https://wellfound.com"
    "linkedin|https://www.linkedin.com"
    "builtin|https://builtin.com"
    "greenhouse|https://boards.greenhouse.io"
    "ashby|https://jobs.ashbyhq.com"
)

for entry in "${SITES[@]}"; do
    IFS='|' read -r name url <<< "$entry"
    echo ""
    echo ">>> $name"
    $B goto "$url" 2>&1 | tail -2
    echo "Log in now, then press ENTER..."
    read -p ""
    $B state save "job-$name" 2>&1 | tail -1
    echo "Saved: $name"
done

echo ""
echo "========================================="
echo "  ALL DONE! States saved."
echo "========================================="
echo ""
echo "Verify with: check_auth.sh"
