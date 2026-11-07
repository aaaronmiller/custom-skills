#!/usr/bin/env python3
"""goapi-lane.py: free-lane.sh's direct transport. One text-only call to the OpenCode Go API.

  goapi-lane.py MODEL PROMPT_FILE OUT_FILE      (MODEL without the goapi/ prefix)

Same contract as free-lane.sh: redacted text in, the answer text in OUT_FILE, exit 0 only when OUT_FILE is
non-empty, errors in OUT_FILE.err. No tools, no files, no shell: a single chat completion. Used because the
`opencode run` free route stalled (exit 124) for whole passes on 2026-11-05 to 11-07 while direct calls did
not. Each call is logged (counts only, never text) to ~/.local/state/capacity-watch/calls-direct.jsonl.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

URL = "https://opencode.ai/zen/go/v1/chat/completions"


def main() -> int:
    if len(sys.argv) != 4:
        print("usage: goapi-lane.py MODEL PROMPT_FILE OUT_FILE", file=sys.stderr)
        return 2
    model, prompt, out = sys.argv[1], Path(sys.argv[2]).read_text(errors="replace"), Path(sys.argv[3])
    err = Path(str(out) + ".err")
    key = os.environ.get("OPENCODE_GO_API_KEY")
    if not key:
        err.write_text("OPENCODE_GO_API_KEY is not set")
        return 3
    body = {"model": model, "messages": [{"role": "user", "content": prompt}], "max_tokens": 16000}
    req = urllib.request.Request(URL, data=json.dumps(body).encode(), headers={
        "Authorization": "Bearer " + key, "Content-Type": "application/json",
        "User-Agent": "intent-refresh/2.1", "x-opencode-session": str(uuid.uuid4())})
    t0, outcome, usage = time.time(), "ok", None
    try:
        d = json.load(urllib.request.urlopen(req, timeout=int(os.environ.get("FREE_LANE_TIMEOUT", "600"))))
        usage = d.get("usage")
        text = d["choices"][0]["message"].get("content") or ""
        out.write_text(text)
    except urllib.error.HTTPError as e:
        outcome = "429" if e.code == 429 else f"http{e.code}"
        err.write_text(f"{outcome} {e.read()[:300].decode('utf8', 'replace')}")
    except Exception as e:  # noqa: BLE001
        outcome = "error"
        err.write_text(str(e)[:300])
    try:
        log = Path.home() / ".local/state/capacity-watch/calls-direct.jsonl"
        with open(log, "a") as f:
            f.write(json.dumps({"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "harness": "direct-api",
                                "job": os.environ.get("LANE_JOB", "intent-refresh"), "provider": "opencode-go",
                                "model": model, "latency_s": round(time.time() - t0, 2), "outcome": outcome,
                                "usage": usage}) + "\n")
    except OSError:
        pass
    return 0 if out.exists() and out.stat().st_size > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
