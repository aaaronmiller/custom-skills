---
name: browser
description: Web scraping and browser automation through local CLIs, routed by how hard the site fights back. Obscura for cheap fetches, Camoufox for bot-protected pages, Interceptor (real Chrome plus extension) for the hardest walls and interactive flows, agent-browser for ordinary interactive pages. Use for web scraping, reading a page, searching a site, checking stock or prices, filling forms, or any site interaction task.
disable-model-invocation: true
allowed-tools: Bash(obscura *), Bash(camoufox-fetch *), Bash(interceptor *), Bash(interceptor-browser *), Bash(agent-browser *)
inputs:
- name: url_or_action
  description: URL to visit or action to perform on a webpage
  pointer_type: parameter
outputs:
- name: extracted_content
  description: Extracted text or data from the webpage
  pointer_type: output_file
tags:
- web
- scraping
- automation
- anti-bot
grade: B
source: custom
---

# Browser: scraping and site interaction

Pick the engine by how hostile the target is. Start at the cheapest rung and
climb only when the current rung fails. Never use MCP browser tools when one of
these CLIs reaches the page. Never screenshot to read text.

## Engine ladder

| Rung | Engine | Use when | Cost |
|---|---|---|---|
| 1 | `obscura fetch --stealth <url>` | Bulk or single reads of pages that do not fight back | tens of MB, ~3 s |
| 2 | `camoufox-fetch <url>` | Bot-protected pages (JS challenge, Cloudflare, fingerprinting). Default for hostile targets | ~430 MB, ~10 s |
| 3 | `interceptor open <url>` | Camoufox was blocked, or the task needs real Chrome: logins, tabs, rich editors, `isTrusted` input | ~1.3 GB |
| side | `agent-browser` | Interactive flows (forms, clicks) on ordinary sites that do not block headless Chromium | ~400 MB |

Escalate on any of: HTTP 403/429, an empty render, a challenge page
("verify you are human", "blocked by network security"), or `camoufox-fetch`
exit code 4. Do not escalate by retrying the same engine.

agent-browser drives headless Playwright Chromium. Reddit-class bot walls
block it outright, so it is never an anti-bot rung.

## Rung 1: Obscura

```bash
obscura fetch --stealth "https://example.com"          # rendered page
obscura scrape --stealth "https://example.com"         # see `obscura scrape --help`
```

Fails on real JS challenges (synthetic DOM, non-browser TLS). Move to rung 2.

## Rung 2: Camoufox

```bash
camoufox-fetch "https://www.reddit.com/r/Polymarket/"                  # visible text
camoufox-fetch "<url>" --selector "shreddit-post" --wait 6000          # only matching elements
camoufox-fetch "<url>" --html                                          # rendered DOM
```

Exit codes: 0 ok, 3 navigation failed, 4 bot wall detected (escalate).
Script source: `scripts/camoufox-fetch` in this skill; runs on the dedicated
venv `/home/cheta/.venvs/camoufox`.

## Rung 3: Interceptor

Start the dedicated browser once per session, then drive it by element refs.

```bash
interceptor-browser start              # Chrome for Testing + extension, own profile
interceptor open "<url>" --text-only   # background tab, returns visible text
interceptor read                       # tree (e1, e2 refs) + text of current tab
interceptor act e5                     # click a ref, returns updated tree
interceptor act e3 "hello"             # type into a ref
interceptor text --markdown            # text keeping headings and tables
interceptor net log --filter api --limit 20
interceptor-browser stop               # free ~1.3 GB when done
```

Refs go stale after navigation or re-render; run `read` again. `interceptor get`
is not a command. Run `interceptor help <verb>` for any verb's contract.

## Side path: agent-browser

```bash
agent-browser open "<url>"
agent-browser snapshot                 # refs like @e5; always before acting
agent-browser click @e5 | fill @e5 "text" | press Enter
agent-browser get text @e20
agent-browser state save <path> / state load <path>
```

## Rules

- Narrow before extracting: one table, list, or selector, never a whole-page parse.
- Re-read refs after every navigation or click, whatever the engine.
- Stop Interceptor's browser when finished; it is the heaviest stack.

Install layout, profiles, and troubleshooting: [reference.md](reference.md).
