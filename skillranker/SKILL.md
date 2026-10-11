---
name: skillranker
description: Use sr (skillranker) to ask which installed skill fits the next step of the current session. Use when unsure which skill applies, when many skills could apply, or to check why an expected skill was not suggested. Recommendations come from TypeSafe Jev, are advisory, and are never run automatically.
tags:
- skills
- skill-selection
- routing
- jev
- cli
source: custom
---

# skillranker (`sr`)

`sr` reads the live session, finds the skills that are actually loadable in this harness, and asks
TypeSafe's Jev model which one (if any) fits the next step. It may abstain; an abstention is a valid answer.

## On this machine

- `/home/cheta/.local/bin/sr` is a wrapper around the build in `/home/cheta/git/skillranker` (a `git pull` there rebuilds it). It points sr at free Jev (`jev-1.13-free`) on OpenCode Zen and reads the Zen key from OpenCode's auth store at run time.
- Network consent is on in `/home/cheta/.config/sr/config.toml`, so `sr rank` reaches Jev without `--allow-network`. If `sr doctor --json` reports a problem, choose skills yourself; do not try to fix credentials.
- The Claude Code hook (automatic per-prompt suggestions) is not installed.

## Use it

```bash
sr doctor --json                 # readiness: credential presence, consent, roster, adapters
sr roster --json                 # which skills are visible, shadowed or excluded here
sr rank --transcript SESSION.jsonl --harness claude_code --dry-run           # preview the redacted request
sr rank --transcript SESSION.jsonl --harness claude_code --allow-network --json   # live ranking
sr rank --session PATH --allow-network --json                                # any harness, through cass
sr rank --allow-network --why-not SKILL_ID --explain   # why an expected skill was excluded (no extra calls)
sr demo --case useful            # offline fixture; shows the output shape without a key or network
```

`--dry-run` and `--offline` make no network calls. `--allow-network` authorizes one run only.

## Rules

- A suggestion is advice. Use the skill only if it fits the user's request and current instructions.
- Never print, log or copy credentials. Never paste a key into a command line.
- Do not install hooks, change `~/.config/sr/config.toml`, or enable network consent unless the user asks.
- Full reference: `/home/cheta/git/skillranker/README.md`.
