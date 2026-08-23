#!/bin/bash
# Full auth setup for job search sites
# Run this once to authenticate on all sites, then states persist
# Usage: auth_setup.sh [--site SITE] [--list] [--check]

B=~/.claude/skills/gstack/browse/dist/browse
STATE_DIR="/home/cheta/tmp/.gstack/browse-states"

# Job sites to authenticate
SITES=(
    "wellfound|https://wellfound.com|Wellfound (AngelList)"
    "builtin|https://builtin.com|BuiltIn Seattle"
    "linkedin|https://www.linkedin.com|LinkedIn"
    "greenhouse|https://boards.greenhouse.io|Greenhouse ATS"
    "ashby|https://jobs.ashbyhq.com|Ashby ATS"
    "yc-was|https://www.workatastartup.com|YC Work at a Startup"
)

list_states() {
    echo "=== Saved Auth States ==="
    for entry in "${SITES[@]}"; do
        IFS='|' read -r key url name <<< "$entry"
        state_file="$STATE_DIR/job-$key.json"
        if [ -f "$state_file" ]; then
            size=$(stat -c%s "$state_file" 2>/dev/null || echo "0")
            echo "  ✓ $name ($key) — ${size} bytes"
        else
            echo "  ✗ $name ($key) — NOT SAVED"
        fi
    done
}

check_auth() {
    echo "=== Checking Login Status ==="
    for entry in "${SITES[@]}"; do
        IFS='|' read -r key url name <<< "$entry"
        # Load state if exists
        state_file="$STATE_DIR/job-$key.json"
        if [ -f "$state_file" ]; then
            $B state load "job-$key" 2>/dev/null
        fi
        $B goto "$url" 2>/dev/null
        sleep 2
        # Check for login/signup buttons (not logged in)
        snapshot=$($B snapshot -i 2>/dev/null)
        if echo "$snapshot" | grep -q "Log in\|Sign up\|Sign In"; then
            echo "  ✗ $name — NOT LOGGED IN"
        else
            echo "  ✓ $name — LOGGED IN"
        fi
    done
}

login_site() {
    local key=$1
    local url=$2
    local name=$3
    
    echo ""
    echo "=== Logging into: $name ==="
    echo "Opening $url in browser..."
    $B goto "$url" 2>&1 | tail -2
    
    echo ""
    echo "Please log in to $name in the browser window."
    echo "Once logged in, press ENTER here to save the state."
    read -p "Ready? "
    
    $B state save "job-$key" 2>&1
    echo "✓ State saved for $name"
}

# Parse args
case "${1:-}" in
    --list|-l)
        list_states
        exit 0
        ;;
    --check|-c)
        check_auth
        exit 0
        ;;
    --site|-s)
        key="$2"
        for entry in "${SITES[@]}"; do
            IFS='|' read -r k url name <<< "$entry"
            if [ "$k" = "$key" ]; then
                login_site "$k" "$url" "$name"
                exit 0
            fi
        done
        echo "Unknown site: $key"
        echo "Available: wellfound, builtin, linkedin, greenhouse, ashby, yc-was"
        exit 1
        ;;
    *)
        echo "=== Job Search Auth Setup ==="
        echo ""
        echo "This will open each site for you to log in."
        echo "States are saved and persist across sessions."
        echo ""
        list_states
        echo ""
        read -p "Set up auth for all sites? (y/n) "
        if [ "$REPLY" = "y" ] || [ "$REPLY" = "Y" ]; then
            for entry in "${SITES[@]}"; do
                IFS='|' read -r key url name <<< "$entry"
                login_site "$key" "$url" "$name"
            done
            echo ""
            echo "=== All done! ==="
            list_states
        fi
        ;;
esac
