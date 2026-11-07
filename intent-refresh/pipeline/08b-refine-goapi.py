#!/usr/bin/env python3
"""Phase 8b: refine the chunks that 08-refine could not finish, through the OpenCode Go API directly.

  OPENCODE_GO_API_KEY=... python3 -I 08b-refine-goapi.py --run 2026-08-29 --out <refined dir> \
      --catalog <frozen catalog.json> [--also <other refined dir>] [--models crouton-alpha-free,muse-spark-1.3-contributor] [--lanes 3]

Same chunking, prompt, validator and output format as 08-refine; only the transport differs. The
`opencode run` free route stalls (exit 124) for whole passes, while direct calls to the Go endpoint did
not stall in the 2026-11-07 lane trial. A chunk already valid in --out or any --also dir is skipped.
Text sent is the 07-collect redacted corpus. Each call is logged to the capacity-watch direct ledger.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import importlib.util
import json
import os
import sys
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

HERE = Path(__file__).parent
URL = "https://opencode.ai/zen/go/v1/chat/completions"
UA = "intent-refresh/2.1"
LEDGER = Path.home() / ".local/state/capacity-watch/calls-direct.jsonl"


def refine08():
    sys.path.insert(0, str(HERE))
    spec = importlib.util.spec_from_file_location("refine08", HERE / "08-refine.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def call(model: str, prompt: str) -> tuple[str | None, str]:
    body = {"model": model, "messages": [{"role": "user", "content": prompt}], "max_tokens": 16000}
    req = urllib.request.Request(URL, data=json.dumps(body).encode(), headers={
        "Authorization": "Bearer " + os.environ["OPENCODE_GO_API_KEY"], "Content-Type": "application/json",
        "User-Agent": UA, "x-opencode-session": str(uuid.uuid4())})
    t0 = time.time()
    outcome, usage, text = "ok", None, None
    try:
        d = json.load(urllib.request.urlopen(req, timeout=300))
        usage, text = d.get("usage"), d["choices"][0]["message"].get("content") or ""
    except urllib.error.HTTPError as e:
        outcome = "429" if e.code == 429 else f"http{e.code}"
    except Exception:  # noqa: BLE001
        outcome = "stall" if time.time() - t0 >= 299 else "error"
    with open(LEDGER, "a") as f:
        f.write(json.dumps({"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "harness": "direct-api",
                            "job": "intent-refine-goapi", "provider": "opencode-go", "model": model,
                            "latency_s": round(time.time() - t0, 2), "outcome": outcome, "usage": usage}) + "\n")
    return text, outcome


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--catalog", required=True)
    ap.add_argument("--also", action="append", default=[])
    ap.add_argument("--models", default="crouton-alpha-free,muse-spark-1.3-contributor")
    ap.add_argument("--lanes", type=int, default=3)
    a = ap.parse_args()
    r8 = refine08()
    base = Path.home() / ".intent-archaeology/corpus" / a.run
    sessions = {json.loads(l)["id"]: json.loads(l) for l in open(base / "sessions.jsonl")}
    prompts = [json.loads(l) for l in open(base / "prompts.jsonl")]
    prompts = [p for p in prompts if p["origin"] != "dispatched"]
    frozen = json.loads(Path(a.catalog).read_text())
    cat, valid = frozen["catalog"], set(frozen["valid"])
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    have = {p.name for d in [out, *map(Path, a.also)] for p in d.glob("chunk-[0-9][0-9][0-9][0-9].json")}
    todo = [c for c in r8.chunks(prompts, sessions) if f"chunk-{c['n']:04d}.json" not in have]
    models = a.models.split(",")
    print(f"{len(todo)} chunks to refine: {[c['n'] for c in todo]}", flush=True)

    def one(i_c):
        i, c = i_c
        prompt = r8.render_prompt(c, sessions, cat)
        reason = ""
        for attempt in range(4):
            model = models[min(attempt, len(models) - 1)] if attempt < 2 else models[(i + attempt) % len(models)]
            text, outcome = call(model, prompt)
            if outcome != "ok":
                reason = f"{model}: {outcome}"
                time.sleep(20 if outcome == "429" else 3)
                continue
            try:
                ans = r8.parse(text)
            except Exception as e:  # noqa: BLE001
                reason = f"{model}: unparseable {e}"[:200]
                continue
            ok, why = r8.validate(ans, c, valid)
            if ok:
                ans["model"], ans["chunk"] = f"opencode-go/{model}", c["n"]
                ans["ids"] = [p["id"] for p in c["prompts"]]
                (out / f"chunk-{c['n']:04d}.json").write_text(json.dumps(ans, indent=1))
                return c["n"], f"ok via {model}"
            reason = f"{model}: {why}"
        return c["n"], "FAILED " + reason

    ok = 0
    with cf.ThreadPoolExecutor(a.lanes) as ex:
        for n, status in ex.map(one, enumerate(todo)):
            ok += status.startswith("ok")
            print(f"chunk {n}: {status}", flush=True)
    print(f"done: {ok} ok, {len(todo) - ok} failed")
    return 0 if ok == len(todo) else 3


if __name__ == "__main__":
    sys.exit(main())
