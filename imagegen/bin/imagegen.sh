#!/usr/bin/env bash
# imagegen.sh - headless image generation driven by an authorized CLI agent.
#
# No custom API keys. Each backend uses the CLI's OWN account authorization to
# call an image model directly.
#
# Backends:
#   codex        (default, VERIFIED)  OpenAI Codex CLI built-in image gen via
#                `codex exec`. Uses your ChatGPT plan login ($imagegen -> gpt-image-2).
#                No OPENAI_API_KEY required.
#   agy          (VERIFIED 2026-11-09) Antigravity CLI headless: `agy --mode accept-edits
#                -p "<instr>"`; the agent's built-in image tool renders the PNG. Uses the
#                agy login; model via IMAGEGEN_AGY_MODEL (default gemini-3.8-flash-medium).
#   antigravity  (legacy, entitlement-gated) Reuses Antigravity Google OAuth (via
#                ~/.cli-proxy-api/antigravity-*.json) to call Nano Banana Pro through
#                the CloudCode API. Requires local ANTIGRAVITY_OAUTH_CLIENT_ID and
#                ANTIGRAVITY_OAUTH_CLIENT_SECRET configuration. Image models may return
#                HTTP 404 when the account lacks access. `agy` itself has no image model,
#                so this drives a helper script, not the agy binary.
#
# Usage:
#   imagegen.sh -p "a red panda on a branch" -o out.png
#   imagegen.sh -p "minimalist gear icon, flat" -o icon.png
#   imagegen.sh -p "edit: make the sky purple" -o edited.png -r base.png
#
# Output: absolute path of the generated file on stdout. Diagnostics on stderr.

set -euo pipefail

PROMPT=""; OUT=""; BACKEND="codex"; REF=""; TIMEOUT="300"
# Resolve the Antigravity helper next to this script first (skill-bundled),
# then fall back to the standalone install location.
_SELF_DIR="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"
if [ -f "$_SELF_DIR/generate_image.py" ]; then
  NBA_SCRIPT="$_SELF_DIR/generate_image.py"
else
  NBA_SCRIPT="$HOME/.local/share/imagegen/nano-banana-antigravity/scripts/generate_image.py"
fi

log() { printf '%s\n' "$*" >&2; }
die() { log "error: $*"; exit 1; }

while [ $# -gt 0 ]; do
  case "$1" in
    -p|--prompt)  PROMPT="$2"; shift 2;;
    -o|--out)     OUT="$2"; shift 2;;
    -b|--backend) BACKEND="$2"; shift 2;;
    -r|--ref)     REF="$2"; shift 2;;
    -t|--timeout) TIMEOUT="$2"; shift 2;;
    -h|--help)    sed -n '2,26p' "$0"; exit 0;;
    *) die "unknown arg: $1";;
  esac
done

[ -n "$PROMPT" ] || die "missing -p/--prompt"
[ -n "$OUT" ] || OUT="./images/$(printf '%s' "$PROMPT" | tr -cs 'A-Za-z0-9' '_' | cut -c1-60).png"
mkdir -p "$(dirname "$OUT")"

# --- codex backend: keyless, built-in $imagegen (gpt-image-2) ---
# Verified: codex exec --sandbox workspace-write, stdin closed. Codex renders to
# ~/.codex/generated_images/<session>/ig_*.png then copies to the requested path.
gen_codex() {
  command -v codex >/dev/null || die "codex CLI not installed"
  codex login status >/dev/null 2>&1 || die "codex not logged in (run: codex login)"

  local ref=""; [ -n "$REF" ] && ref=" Use '${REF}' as the reference image."
  local instr="Use the \$imagegen image generation skill: ${PROMPT}.${ref} Save exactly one PNG to the absolute path '${OUT}' (create parent dirs). Do nothing else: no code edits, no git, no other commands."

  log "codex: \$imagegen -> gpt-image-2 (keyless, ChatGPT plan; up to ${TIMEOUT}s)"
  # Snapshot existing renders before launching so concurrent imagegen.sh calls
  # never race on a shared timestamp file (each call diffs its own before/after set).
  local before; before="$(mktemp)"
  find "$HOME/.codex/generated_images" -type f -name '*.png' 2>/dev/null | sort >"$before"
  timeout "$TIMEOUT" codex exec --sandbox workspace-write --skip-git-repo-check "$instr" </dev/null >&2 \
    || log "warn: codex exec returned non-zero or timed out; checking for output anyway"

  # Primary: codex copied to OUT. Fallback: diff against the pre-run snapshot to
  # find files this invocation produced, then take the newest of those.
  if [ ! -s "$OUT" ]; then
    local after newest
    after="$(mktemp)"
    find "$HOME/.codex/generated_images" -type f -name '*.png' 2>/dev/null | sort >"$after"
    newest="$(comm -13 "$before" "$after" | xargs -r ls -t 2>/dev/null | head -1)"
    rm -f "$after"
    [ -n "$newest" ] && cp "$newest" "$OUT"
  fi
  rm -f "$before"
  [ -s "$OUT" ] || die "codex produced no image at $OUT (check output above)"
}

# --- agy backend: Antigravity CLI headless (the expected Antigravity route) ---
# `agy models` lists no image model, but the agent's own image tool generates one.
# Verified 2026-11-09: three 1024x1024 PNGs with gemini-3.8-flash-medium.
# --mode accept-edits auto-approves file writes only; never --dangerously-skip-permissions
# (Claude Code auto mode refuses it as an unsafe agent). -p must be the LAST flag:
# agy reads the token right after -p as the prompt.
gen_agy() {
  command -v agy >/dev/null || die "agy CLI not installed"
  local model="${IMAGEGEN_AGY_MODEL:-gemini-3.8-flash-medium}"
  local dir; dir="$(cd "$(dirname "$OUT")" && pwd)"
  local abs="$dir/$(basename "$OUT")"
  local ref="" add=()
  if [ -n "$REF" ]; then
    local rabs; rabs="$(cd "$(dirname "$REF")" && pwd)/$(basename "$REF")"
    ref=" Use the image at '${rabs}' as the reference."; add=(--add-dir "$(dirname "$rabs")")
  fi
  local instr="Use your image generation tool to create one image and save it as a PNG file at '${abs}'. Do not write code to draw it.${ref} Image: ${PROMPT} When done, reply with the saved path only."
  log "agy: headless image tool via ${model} (up to ${TIMEOUT}s)"
  (cd "$dir" && timeout "$TIMEOUT" agy --model "$model" --mode accept-edits "${add[@]}" \
      --print-timeout "$((TIMEOUT - 10))s" -p "$instr" </dev/null >&2) \
    || log "warn: agy returned non-zero or timed out; checking for output anyway"
  [ -s "$abs" ] || die "agy produced no image at $abs (check output above)"
}

# --- antigravity backend (legacy): OAuth reuse -> Nano Banana Pro via CloudCode ---
# Drives the bundled helper script directly. Needs ANTIGRAVITY_OAUTH_CLIENT_ID and
# ANTIGRAVITY_OAUTH_CLIENT_SECRET in the environment; free-tier accounts 404. Prefer -b agy.
gen_antigravity() {
  command -v uv >/dev/null || die "uv required for antigravity backend"
  [ -f "$NBA_SCRIPT" ] || die "helper missing: $NBA_SCRIPT"
  local args=(-p "$PROMPT" -f "$OUT")
  [ -n "$REF" ] && args+=(-i "$REF")
  log "antigravity: Nano Banana Pro via OAuth (404 if account lacks image access)"
  timeout "$TIMEOUT" uv run "$NBA_SCRIPT" "${args[@]}" >&2 || die "antigravity gen failed (see above; free-tier accounts 404)"
  [ -s "$OUT" ] || die "antigravity produced no image at $OUT"
}

case "$BACKEND" in
  codex)       gen_codex;;
  agy)         gen_agy;;
  antigravity) gen_antigravity;;
  *)           die "unknown backend: $BACKEND (use: codex | agy | antigravity)";;
esac

ABS="$(cd "$(dirname "$OUT")" && printf '%s/%s' "$(pwd)" "$(basename "$OUT")")"
log "ok: $BACKEND -> $ABS ($(wc -c <"$ABS") bytes)"
printf '%s\n' "$ABS"
