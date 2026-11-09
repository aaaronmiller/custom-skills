---
name: imagegen
description: Generate or edit images from the terminal with no API keys, using an authorized CLI agent's own account. Use when asked to generate an image, icon, banner, texture, illustration, sprite, or placeholder art headlessly or in a script. Default backend is Codex ($imagegen, gpt-image-2, ChatGPT plan). The agy backend runs the Antigravity CLI headless and uses its built-in image tool; use it when Codex is out of quota.
license: MIT
metadata:
  version: "2.1.0"
  author: Ice-ninja
  bundled_cli: bin/imagegen.sh
---

# imagegen

Keyless headless image generation. No `GEMINI_API_KEY`, `OPENAI_API_KEY`, or `NANOBANANA_API_KEY`. Each backend uses the CLI's own account authorization.

## Use the bundled CLI

```bash
bin/imagegen.sh -p "<prompt>" -o out.png            # default backend: codex
bin/imagegen.sh -p "<prompt>" -o out.png -b agy    # Antigravity CLI headless
bin/imagegen.sh -p "edit: purple sky" -o out.png -r base.png   # -r reference image
```

Prints the absolute path of the generated file on stdout. When installed via the agents sync, the wrapper is also on PATH as `imagegen.sh`.

## Backends

- **codex** (default, VERIFIED working): Codex CLI built-in image gen. `codex exec` runs headless; `$imagegen` invokes `gpt-image-2` via the ChatGPT plan login. Renders to `~/.codex/generated_images/<session>/` then copies to your path. Counts toward Codex plan usage, not API billing.
- **agy** (VERIFIED 2026-11-09, the expected Antigravity route): `agy --model <m> --mode accept-edits -p "<instr>"` runs headless, and the agent's built-in image tool writes a 1024x1024 PNG to the path you name. `agy models` lists no image model; the tool still works. Model via `IMAGEGEN_AGY_MODEL` (default `gemini-3.8-flash-medium`). Two rules: `-p` goes last, because agy reads the token right after `-p` as the prompt; and use `--mode accept-edits`, never `--dangerously-skip-permissions`, which Claude Code auto mode refuses as an unsafe agent.
- **antigravity** (legacy, entitlement-gated): drives the bundled `bin/generate_image.py` directly against the CloudCode API with the Antigravity OAuth creds. Needs `ANTIGRAVITY_OAUTH_CLIENT_ID` and `ANTIGRAVITY_OAUTH_CLIENT_SECRET` in the environment (never distributed with this skill); free-tier accounts get HTTP 404. Prefer `-b agy`.

If a call fails, read the stderr trace. Codex failing with "You've hit your usage limit" means its plan quota is spent: switch to `-b agy`. Do not fall back to a keyed API: this skill is deliberately keyless.

No free image-output model exists on opencode-go or OpenRouter (checked 2026-11-09: 0 of 40 opencode-go models output images; 0 of 13 OpenRouter image models are free).

## Direct one-liner (no wrapper)

```bash
codex exec --sandbox workspace-write --skip-git-repo-check \
  "Use the $imagegen skill: <prompt>. Save one PNG to '<abs-path>'." </dev/null
```

Close stdin (`</dev/null`) or `codex exec` hangs. `--full-auto` is deprecated; use `--sandbox workspace-write`.

## Do not use

- Gemini CLI `nanobanana` extension: needs `NANOBANANA_API_KEY`. Excluded (keyless only).

See `references/backends.md` for the full capability matrix and the entitlement finding.
