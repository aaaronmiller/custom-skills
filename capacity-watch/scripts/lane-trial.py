#!/usr/bin/env python3
"""Lane trial: run identical intent-refine chunks through several models and measure cost, speed and quality.

  OPENCODE_GO_API_KEY=... python3 -I lane-trial.py --run 2026-08-29 --chunks 0-19 \
      --models muse-spark-1.3-contributor,deepseek-v4.1-flash,gemini-4-argon,crouton-alpha-free \
      --lanes 3 --out ~/.local/state/capacity-watch/trials/2026-11-07

Every call goes to the OpenCode Go endpoint. Text is the 07-collect redacted corpus, redacted again here.
Per call it records latency, tokens, list cost and plan allowance (usage.opencode), and whether the
answer passes 08-refine's validator. Quality proxy: agreement of each prompt's project with the
already accepted refined output for that chunk. Plan percent is read before and after the trial.
Nothing is written into the corpus.
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

URL = "https://opencode.ai/zen/go/v1/chat/completions"
USAGE = "https://opencode.ai/zen/go/v1/usage"
UA = "capacity-watch-lane-trial/1.0"
REFINE = Path("/home/cheta/code/custom-skills/intent-refresh/pipeline/08-refine.py")
NOTES = Path("/home/cheta/code/custom-skills/notes-sweeper/scripts")
STALL_S = 300


def load_refine():
    sys.path.insert(0, str(REFINE.parent))
    spec = importlib.util.spec_from_file_location("refine08", REFINE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def redactor():
    sys.path.insert(0, str(NOTES))
    from organize import redact  # noqa: E402
    return lambda t: redact(t)[0]


def key() -> str:
    return os.environ["OPENCODE_GO_API_KEY"]


def plan_usage() -> dict:
    req = urllib.request.Request(USAGE, headers={"Authorization": "Bearer " + key(), "User-Agent": UA})
    try:
        return json.load(urllib.request.urlopen(req, timeout=30)).get("usage", {})
    except Exception as e:  # noqa: BLE001
        return {"error": str(e)}


def call(model: str, prompt: str) -> dict:
    body = {"model": model, "messages": [{"role": "user", "content": prompt}], "max_tokens": 16000}
    req = urllib.request.Request(URL, data=json.dumps(body).encode(), headers={
        "Authorization": "Bearer " + key(), "Content-Type": "application/json", "User-Agent": UA,
        "x-opencode-session": str(uuid.uuid4())})
    t0 = time.time()
    rec = {"model": model, "start": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    try:
        d = json.load(urllib.request.urlopen(req, timeout=STALL_S))
        rec["latency_s"] = round(time.time() - t0, 2)
        rec["outcome"] = "ok"
        rec["usage"] = d.get("usage")
        rec["text"] = d["choices"][0]["message"].get("content") or ""
    except urllib.error.HTTPError as e:
        rec["latency_s"] = round(time.time() - t0, 2)
        rec["outcome"] = "429" if e.code == 429 else f"http{e.code}"
        rec["error"] = e.read()[:300].decode("utf8", "replace")
    except Exception as e:  # noqa: BLE001
        rec["latency_s"] = round(time.time() - t0, 2)
        rec["outcome"] = "stall" if rec["latency_s"] >= STALL_S - 1 else "error"
        rec["error"] = str(e)[:300]
    return rec


def parse(text: str):
    s = text[text.find("{"): text.rfind("}") + 1]
    return json.loads(s)


def agreement(ans: dict, ref: dict) -> float | None:
    want = {p["id"]: p.get("project") for p in ref.get("prompts", [])}
    got = {p.get("id"): p.get("project") for p in ans.get("prompts", [])}
    common = [i for i in want if i in got]
    return round(sum(want[i] == got[i] for i in common) / len(common), 3) if common else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default="2026-08-29")
    ap.add_argument("--chunks", default="0-19")
    ap.add_argument("--models", required=True)
    ap.add_argument("--lanes", type=int, default=3, help="concurrent calls per model")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = Path(os.path.expanduser(a.out))
    out.mkdir(parents=True, exist_ok=True)
    r8 = load_refine()
    red = redactor()
    base = Path.home() / ".intent-archaeology/corpus" / a.run
    sessions = {json.loads(l)["id"]: json.loads(l) for l in open(base / "sessions.jsonl")}
    prompts = [json.loads(l) for l in open(base / "prompts.jsonl")]
    prompts = [p for p in prompts if p["origin"] != "dispatched"]
    cs = r8.chunks(prompts, sessions)
    lo, hi = (int(x) for x in a.chunks.split("-"))
    cs = [c for c in cs if lo <= c["n"] <= hi and (base / "refined" / f"chunk-{c['n']:04d}.json").exists()]
    cat = r8.catalog()
    valid = {pm.parent.name for pm in r8.DOSSIERS.glob("*/project.md")} | {"sysadmin", "unclassified"}
    models = a.models.split(",")
    before = plan_usage()
    (out / "plan-before.json").write_text(json.dumps(before))
    t_start = time.time()

    def job(model, c):
        prompt = red(r8.render_prompt(c, sessions, cat))
        rec = call(model, prompt)
        rec["chunk"] = c["n"]
        rec["prompt_chars"] = len(prompt)
        if rec["outcome"] == "ok":
            try:
                ans = parse(rec["text"])
                ok, reason = r8.validate(ans, c, valid)
                rec["valid"], rec["reason"] = ok, reason
                ref = json.loads((base / "refined" / f"chunk-{c['n']:04d}.json").read_text())
                rec["project_agreement"] = agreement(ans, ref)
            except Exception as e:  # noqa: BLE001
                rec["valid"], rec["reason"] = False, f"unparseable: {e}"[:200]
        rec.pop("text", None)
        with open(out / "calls.jsonl", "a") as f:
            f.write(json.dumps(rec) + "\n")
        with open(Path.home() / ".local/state/capacity-watch/calls-direct.jsonl", "a") as f:
            f.write(json.dumps({"ts": rec["start"], "harness": "direct-api", "job": "lane-trial", "provider": "opencode-go",
                                "model": model, "latency_s": rec["latency_s"], "outcome": rec["outcome"],
                                "usage": rec.get("usage")}) + "\n")
        print(f"{model} chunk {c['n']}: {rec['outcome']} {rec['latency_s']}s valid={rec.get('valid')}", flush=True)
        return rec

    pools = {m: cf.ThreadPoolExecutor(a.lanes) for m in models}
    futs = [pools[m].submit(job, m, c) for c in cs for m in models]
    recs = [f.result() for f in futs]
    for p in pools.values():
        p.shutdown()
    after = plan_usage()
    (out / "plan-after.json").write_text(json.dumps(after))

    summary = {}
    for m in models:
        rs = [r for r in recs if r["model"] == m]
        oks = [r for r in rs if r["outcome"] == "ok"]
        u = [r.get("usage") or {} for r in oks]
        oc = [x.get("opencode") or {} for x in u]
        toks = sum((x.get("prompt_tokens") or 0) + (x.get("completion_tokens") or 0) for x in u)
        valid_n = sum(1 for r in oks if r.get("valid"))
        agr = [r["project_agreement"] for r in oks if r.get("project_agreement") is not None]
        allowance = sum(x.get("allowance") or 0 for x in oc)
        summary[m] = {
            "calls": len(rs), "ok": len(oks), "valid": valid_n,
            "outcomes": {o: sum(1 for r in rs if r["outcome"] == o) for o in {r["outcome"] for r in rs}},
            "median_latency_s": sorted(r["latency_s"] for r in oks)[len(oks) // 2] if oks else None,
            "tokens": toks,
            "list_cost_usd": round(sum(x.get("list_cost") or 0 for x in oc), 5),
            "allowance_usd": round(allowance, 5),
            "allowance_per_valid_chunk": round(allowance / valid_n, 5) if valid_n else None,
            "tokens_per_min_per_lane": round(toks / (sum(r["latency_s"] for r in oks) / 60), 1) if oks else None,
            "project_agreement_mean": round(sum(agr) / len(agr), 3) if agr else None,
        }
    res = {"chunks": [c["n"] for c in cs], "models": models, "lanes_per_model": a.lanes,
           "wall_s": round(time.time() - t_start, 1), "plan_before": before, "plan_after": after, "summary": summary}
    (out / "summary.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
