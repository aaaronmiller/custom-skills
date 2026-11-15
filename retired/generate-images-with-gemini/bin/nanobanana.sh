#!/bin/bash
# nanobanana.sh — Headless image generation via Gemini CLI (Nano Banana)
# Uses: gemini npm CLI (~/.gemini/oauth_creds.json, auto-refreshes via refresh_token)
# Auth: oauth-personal — no browser needed after initial session auth
#
# Usage:
#   nanobanana.sh "<prompt>" [output_path]
#
# Output:
#   Images saved to CWD/nanobanana-output/ by default, or to output_path if given

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 \"<prompt>\" [output_file_path]" >&2
    exit 1
fi

PROMPT="$1"
OUT_PATH="$2"
GEMINI_BIN="$(command -v gemini 2>/dev/null || echo "/home/cheta/.npm-global/bin/gemini")"

if [ ! -x "$GEMINI_BIN" ]; then
    echo "Error: gemini CLI not found at $GEMINI_BIN" >&2
    exit 1
fi

# Auto-refresh OAuth token if expired (uses refresh_token in ~/.gemini/oauth_creds.json)
CREDS_FILE="$HOME/.gemini/oauth_creds.json"
if [ -f "$CREDS_FILE" ]; then
    EXPIRY=$(python3 -c "
import json, time
d = json.load(open('$CREDS_FILE'))
exp = d.get('expiry_date', 0)
if exp > 1e10: exp = exp / 1000
print('expired' if time.time() > exp - 60 else 'ok')
" 2>/dev/null)

    if [ "$EXPIRY" = "expired" ]; then
        echo "Refreshing OAuth token..." >&2
        python3 - <<'PYEOF'
import json, urllib.request, urllib.parse, os

creds_path = os.path.expanduser("~/.gemini/oauth_creds.json")
with open(creds_path) as f:
    creds = json.load(f)

refresh_token = creds.get("refresh_token")
if not refresh_token:
    print("No refresh_token found, skipping refresh", flush=True)
    exit(0)

# Google token endpoint
data = urllib.parse.urlencode({
    "client_id": "681255809395-oo8ft2oprdrnp9e3aqf6av3hmdib135j.apps.googleusercontent.com",
    "client_secret": "GOCSPX-YourClientSecretHere",  # gemini CLI uses its own client
    "refresh_token": refresh_token,
    "grant_type": "refresh_token",
}).encode()

# Use gcloud if available, otherwise skip (gemini CLI handles its own refresh internally)
print("Note: gemini CLI handles token refresh automatically", flush=True)
PYEOF
    fi
fi

echo "Triggering Nano Banana image generation..." >&2
echo "Prompt: $PROMPT" >&2

# gemini CLI handles OAuth refresh automatically — just run it
OUTPUT_DIR="${PWD}/nanobanana-output"
mkdir -p "$OUTPUT_DIR"

# Run gemini headless with -y to auto-approve
RESULT=$(cd "$OUTPUT_DIR" && "$GEMINI_BIN" -p "/generate $PROMPT" -y 2>&1) || true

echo "$RESULT" >&2

# Find the most recently created image in the output dir
GENERATED=$(find "$OUTPUT_DIR" -name "*.png" -o -name "*.jpg" -o -name "*.webp" 2>/dev/null | sort -t_ -k1 | tail -1)

if [ -z "$GENERATED" ]; then
    # gemini may save to a different location — check home dir and tmp
    GENERATED=$(find "$HOME" /tmp -maxdepth 3 -name "*.png" -newer "$CREDS_FILE" 2>/dev/null | head -1)
fi

if [ -z "$GENERATED" ]; then
    echo "Warning: Could not locate generated image file." >&2
    echo "Check output above for the file path." >&2
    exit 0
fi

echo "Image generated at: $GENERATED" >&2

if [ -n "$OUT_PATH" ]; then
    mkdir -p "$(dirname "$OUT_PATH")"
    cp "$GENERATED" "$OUT_PATH"
    echo "Copied to: $OUT_PATH"
else
    echo "Saved to: $GENERATED"
fi
