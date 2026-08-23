# Browser Authentication Setup

## Problem

Windows Chrome cookies are DPAPI-encrypted (OS-level encryption). Linux Chromium cannot decrypt them. We copied the full Chrome profile (bookmarks, history, preferences, saved passwords DB) but sessions are dead — only a manual login per site works.

**What transferred:** Bookmarks ✅, History (15K entries) ✅, Preferences ✅, Saved Passwords DB (readable usernames, passwords encrypted) ✅
**What didn't:** Session cookies ❌ (DPAPI-encrypted, cannot decrypt from WSL)

## Solution: Manual Login + State Save

One-time setup per site: you log in manually, then browse saves the session state. States persist across sessions.

## Quick Start

```bash
# One-shot: log in to all 5 sites in sequence (~5 min)
/home/cheta/code/custom-skills/aaron-job-search/scripts/login-all.sh

# Or one site at a time
/home/cheta/code/custom-skills/aaron-job-search/scripts/auth_setup.sh --site wellfound
/home/cheta/code/custom-skills/aaron-job-search/scripts/auth_setup.sh --site linkedin

# Check status
/home/cheta/code/custom-skills/aaron-job-search/scripts/check_auth.sh
```

## Sites to Authenticate

| Site | Why | Priority |
|------|-----|----------|
| **Wellfound** | 28 direct-apply jobs | HIGH |
| **LinkedIn** | Professional profile + Easy Apply | HIGH |
| **BuiltIn** | 5 direct-apply jobs | MEDIUM |
| **Greenhouse** | 10 ATS jobs (Anduril, Anthropic, etc.) | MEDIUM |
| **Ashby** | 17 ATS jobs (OpenAI, Whatnot, etc.) | MEDIUM |
| **YC Work at a Startup** | YC company jobs | LOW |

## How It Works

1. Script opens site in headless browser
2. You log in manually (password, 2FA, etc.)
3. Script saves browser state (cookies + URLs) to `~/.gstack/browse-states/`
4. Future sessions restore state automatically

## State Files

Located at: `~/.gstack/browse-states/job-*.json`

- `job-wellfound.json` — Wellfound session
- `job-builtin.json` — BuiltIn session
- `job-linkedin.json` — LinkedIn session
- `job-greenhouse.json` — Greenhouse session
- `job-ashby.json` — Ashby session
- `job-yc-was.json` — YC Work at a Startup session

## For Job Submissions

Once authenticated, use:
```bash
# Restore a specific site's auth
/home/cheta/code/custom-skills/aaron-job-search/scripts/restore_auth.sh wellfound

# Then navigate and apply
~/.claude/skills/gstack/browse/dist/browse goto "https://wellfound.com/jobs/..."
```

## Security Note

State files contain session cookies in plaintext. They're stored in `~/.gstack/browse-states/` which is user-readable only. Delete when job search is complete.
