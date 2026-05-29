# Pre-Curate Junk Skill Detection Guide

## Background

Before Hermes had a `curator` system (auto-review agent-managed skills), Hermes
would create skills via `skill_manage` tool after completing complex tasks. These
skills often represent **single-session workflows** that should have been ephemeral
notes, not persistent skills.

## Detection Heuristics

### Primary Signals (Strong)

**1. The 4 eBay Scraper Pattern**
```
research/macbook-analyzer-pipeline
research/ebay-mdm-analyzer
data-collection/ebay-autonomous-scraper
web-scraping/ebay-duckduckgo-browser-scraping
```
These are 4 skills doing the SAME thing — scraping eBay for MacBook logic boards.
This is the canonical "pre-curate" pattern: one cron job saved as 4 different skills.

**2. Command-and-Output Style**
Skills that read like a terminal transcript:
```markdown
## Steps
1. Run: python3 script.py
2. If error, run: pip install ...
3. Check output...
```
This is session documentation, not a reusable skill.

**3. Tool References Outside Context**
Skills that use `browser_navigate`, `browser_vision`, or other sandbox-specific
tools that don't exist in the agent's standard toolset. These are session notes
that got saved as skills.

**4. Redundant Clusters**
Multiple skills on the same topic with slightly different names:
- electron-white-screen-debugger + electron-white-screen-debugging (same session)
- macbook-analyzer-pipeline + ebay-mdm-analyzer (same cron job)

### Secondary Signals (Supporting)

**5. Created Without Category**
Skills in the root of a category with no subdirectory organization often indicate
quick saves: `research/macbook-analyzer-pipeline` vs properly organized `mlops/training/axolotl`.

**6. Single Cron Job as Core Purpose**
If the skill's main value is "run this on a schedule" and the task is simple
(web scrape, check prices), it's a cron job, not a skill.

**7. Missing Version and Author**
Compare:
```yaml
# Good (indicates curation)
version: 1.0.0
author: Orchestra Research
license: MIT

# Junk (indicates auto-save)
# No version, no author, no license
```

**8. References Non-Existent Tools**
Search for `web_search`, `browser_navigate`, or agent-specific tool names
that don't exist in the current agent's tool registry.

## Confirmation Protocol

When a skill triggers 3+ junk indicators:

1. **Read SKILL.md in full** — Don't rely on description/title alone
2. **Check for actual utility** — "Would I use this next week? Would someone else?"
3. **Check for duplicates** — Is there a better version of the same thing?
4. **Check script availability** — If it references scripts, do they exist?
5. **Determine creator** — Bundled? User? Hermes-generated? Hub-installed?

## Undeploy vs Delete

| Origin | Action for junk |
|--------|----------------|
| Hermes-created (agent auto-saved) | Safe to delete (recoverable via curate) |
| Hermes-created (user said "save") | Ask user before deleting |
| Bundled (shipped with Hermes) | Don't delete (restored on update). Just hide from context. |
| Third-party (hub-installed) | Can uninstall via `hermes skills uninstall` |
| User-created | Never delete without explicit user confirmation |
