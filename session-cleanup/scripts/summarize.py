#!/usr/bin/env python3
"""Summarize session digests with Gemini 4 Argon on OpenCode Go (no training, zero retention). Redacts first."""
import json, os, sys, uuid, urllib.request, time, concurrent.futures as cf
sys.path.insert(0, "/home/cheta/code/custom-skills/notes-sweeper/scripts")
from organize import redact  # noqa: E402

KEY = os.environ["OPENCODE_GO_API_KEY"]
URL = "https://opencode.ai/zen/go/v1/chat/completions"
MODEL = os.environ.get("SURVEY_MODEL", "gemini-4-argon")
LEDGER = os.environ.get("CALL_LEDGER")

SYSTEM = """You audit one AI coding-agent session for its operator. You get a digest: the operator's messages, the agent's last replies, and file paths the agent touched.
Return JSON only, with these keys:
 "title": short task name (max 8 words),
 "task": 2-3 sentences: what the operator asked this session to do,
 "status": "finished" | "unfinished" | "abandoned" | "unclear",
 "done": list of what was completed (max 6 short items, cite files or commits when shown),
 "remaining": list of what is still open (max 6 short items; empty if finished),
 "repos": list of absolute repository or project folder paths the work changed (from the paths list; folder level, not files),
 "projects": 1-3 short project names,
 "action": one sentence: the single best next action to resolve the open work (resume here, hand off to X, close the session, or nothing),
 "close_safe": true if the session can be closed without losing work, else false,
 "evidence": one sentence citing what in the digest supports the status.
Write plain English. No em dashes."""

def call(text):
    body = {"model": MODEL, "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": text}],
            "max_tokens": 4000, "response_format": {"type": "json_object"}}
    req = urllib.request.Request(URL, data=json.dumps(body).encode(), headers={
        "Authorization": "Bearer " + KEY, "Content-Type": "application/json",
        "User-Agent": "session-survey/1.0", "x-opencode-session": str(uuid.uuid4())})
    t0 = time.time()
    d = json.load(urllib.request.urlopen(req, timeout=300))
    dt = time.time() - t0
    if LEDGER:
        u = d.get("usage") or {}
        with open(LEDGER, "a") as f:
            f.write(json.dumps({"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "harness": "direct-api",
                                "job": "session-survey", "provider": "opencode-go", "model": MODEL, "latency_s": round(dt, 2),
                                "usage": u}) + "\n")
    s = d["choices"][0]["message"]["content"]
    s = s[s.find("{"): s.rfind("}") + 1]
    return json.loads(s)

def one(key):
    src = open(f"{key}.txt", errors="replace").read()
    red, _hits = redact(src)
    for attempt in range(3):
        try:
            out = call(red[:120000])
            json.dump(out, open(f"{key}.json", "w"), indent=1)
            return key, "ok"
        except Exception as e:  # noqa: BLE001
            err = str(e)
            time.sleep(5 * (attempt + 1))
    return key, "fail " + err

if __name__ == "__main__":
    # usage: summarize.py <work-dir holding KEY.txt digests> KEY [KEY ...]; writes KEY.json beside them
    os.chdir(sys.argv[1])
    keys = sys.argv[2:]
    with cf.ThreadPoolExecutor(3) as ex:
        for k, r in ex.map(one, keys):
            print(k, r, flush=True)
