#!/bin/bash
# Login helper: opens job sites for manual authentication, then saves state
# Usage: login_sites.sh [site]
# Sites: greenhouse, ashby, workday, wellfound, builtin, linkedin, all

B=~/.claude/skills/gstack/browse/dist/browse

login_site() {
    local url=$1
    local name=$2
    echo "Opening $name..."
    $B goto "$url" 2>&1 | tail -3
    echo "Log in manually, then press Enter to save state..."
    read -p "Press Enter after logging in to $name: "
    $B state save "job-$name" 2>&1
    echo "State saved: job-$name"
}

case "${1:-all}" in
    greenhouse) login_site "https://boards.greenhouse.io" "Greenhouse" ;;
    ashby) login_site "https://jobs.ashbyhq.com" "Ashby" ;;
    workday) login_site "https://www.myworkdayjobs.com" "Workday" ;;
    wellfound) login_site "https://wellfound.com" "Wellfound" ;;
    builtin) login_site "https://builtin.com" "BuiltIn" ;;
    linkedin) login_site "https://www.linkedin.com" "LinkedIn" ;;
    all)
        login_site "https://wellfound.com" "Wellfound"
        login_site "https://builtin.com" "BuiltIn"
        login_site "https://www.linkedin.com" "LinkedIn"
        echo "All sites authenticated. State saved."
        ;;
esac
