---
name: imagegen
description: Generate or edit images from the terminal with no API keys, using an authorized CLI agent's own account. Use when asked to generate an image, icon, banner, texture, illustration, sprite, or placeholder art headlessly or in a script. Default backend is Codex ($imagegen, gpt-image-2, ChatGPT plan). Optional Antigravity/Nano Banana Pro backend reuses Google OAuth.
license: MIT
metadata:
  version: "2.0.0"
  author: Ice-ninja
  bundled_cli: bin/imagegen.sh
---

# imagegen

Keyless headless image generation. No `GEMINI_API_KEY`, `OPENAI_API_KEY`, or `NANOBANANA_API_KEY`. Each backend uses the CLI's own account authorization.

## Use the bundled CLI

```bash
bin/imagegen.sh -p "<prompt>" -o out.png            # default backend: codex
bin/imagegen.sh -p "<prompt>" -o out.png -b antigravity
bin/imagegen.sh -p "edit: purple sky" -o out.png -r base.png   # -r reference image
```

Prints the absolute path of the generated file on stdout. When installed via the agents sync, the wrapper is also on PATH as `imagegen.sh`.

## Backends

- **codex** (default, VERIFIED working): Codex CLI built-in image gen. `codex exec` runs headless; `$imagegen` invokes `gpt-image-2` via the ChatGPT plan login. Renders to `~/.codex/generated_images/<session>/` then copies to your path. Counts toward Codex plan usage, not API billing.
- **antigravity** (entitlement-gated): reuses Antigravity Google OAuth (`~/.cli-proxy-api/antigravity-*.json`) to call Nano Banana Pro (`gemini-3-pro-image-preview`) via the CloudCode API. The local environment must provide `ANTIGRAVITY_OAUTH_CLIENT_ID` and `ANTIGRAVITY_OAUTH_CLIENT_SECRET`; they are never distributed with this skill. `agy` itself has no image model, so this drives the bundled `bin/generate_image.py`. Image models may return HTTP 404 when the account lacks image access.

If a call fails, read the stderr trace. Do not fall back to a keyed API: this skill is deliberately keyless.

## Direct one-liner (no wrapper)

```bash
codex exec --sandbox workspace-write --skip-git-repo-check \
  "Use the $imagegen skill: <prompt>. Save one PNG to '<abs-path>'." </dev/null
```

Close stdin (`</dev/null`) or `codex exec` hangs. `--full-auto` is deprecated; use `--sandbox workspace-write`.

## Do not use

- Gemini CLI `nanobanana` extension: needs `NANOBANANA_API_KEY`. Excluded (keyless only).
- `agy` for image gen directly: no native image model; Nano Banana is an IDE-only feature there.

See `references/backends.md` for the full capability matrix and the entitlement finding.
