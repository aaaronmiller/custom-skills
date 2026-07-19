# imagegen backends — capability matrix

The default Codex backend is keyless and uses the CLI's own account auth. The optional Antigravity backend also avoids API keys, but requires local OAuth application configuration that is never distributed with the skill.

| Backend | Auth | Model | Headless | Status (verified 2026-07) |
|---|---|---|---|---|
| codex | ChatGPT plan login | gpt-image-2 | `codex exec` | Works. Generated a real 1254x1254 PNG. |
| antigravity | Antigravity Google OAuth (reused) | gemini-3-pro-image-preview (Nano Banana Pro) | `uv run generate_image.py` | Auth works; image returns HTTP 404 on free-tier CloudCode accounts. |

## codex (default)

`codex exec --sandbox workspace-write --skip-git-repo-check "Use the $imagegen skill: <prompt>. Save one PNG to '<abs>'." </dev/null`

- Close stdin or it hangs. `--full-auto` deprecated → `--sandbox workspace-write` (needed to write the file).
- Codex renders to `~/.codex/generated_images/<session>/ig_*.png`, then the agent copies to the path you name. The wrapper also grabs the newest render as a fallback.
- Counts toward Codex plan usage, not API billing.

## antigravity (OAuth, entitlement-gated)

`bin/generate_image.py` (bundled) reuses `~/.cli-proxy-api/antigravity-*.json` OAuth creds:
refresh the token using `ANTIGRAVITY_OAUTH_CLIENT_ID` and `ANTIGRAVITY_OAUTH_CLIENT_SECRET` from the local environment, call CloudCode `v1internal:loadCodeAssist`
for the project id, then `v1internal:streamGenerateContent` with `gemini-3-pro-image-preview`
(falls back to `gemini-3-pro-image`).

**Why it 404s here:** the CloudCode API tied to these OAuth creds reports `currentTier.id = free-tier`
("Gemini Code Assist for individuals"). All image model names return
`404 "Requested entity was not found."` — the free-tier CLI/API surface does not serve Nano Banana.
That is why image gen was omitted from the Antigravity CLI (it is an IDE / paid-tier feature).

**Note on Google AI Pro ($20):** a Google AI Pro subscription is not the same entitlement as the
CloudCode "Gemini Code Assist" tier these creds authenticate against. If the CloudCode tier stays
free, the image endpoint stays 404 regardless of the AI Pro plan. Resolve by authenticating the
Antigravity CLI with the account that carries the image entitlement, then re-run
`imagegen.sh -b antigravity -p test -o /tmp/t.png`. Local patch added a Priority-0 credential
source so the helper reads `~/.cli-proxy-api/antigravity-*.json` (upstream only checks `~/.openclaw/`).

## Excluded

- Gemini CLI `nanobanana` extension: requires `NANOBANANA_API_KEY`. Violates keyless rule.
- Direct Gemini/OpenAI REST APIs: require keys. Excluded.
