#!/usr/bin/env python3
"""Summarize every mesh-dispatch job on this host as one JSON document on stdout.

Run on a mesh worker (stdlib only):  ssh HOST python3 - < job-summary-remote.py
Reads ~/work/jobs/JOB/{brief.md, log.jsonl, EXIT, out/}. Writes no files.
Per job: the brief text, first and last event times, models, tool and subagent counts,
tool errors, API errors and retries, the final result event's metrics, and the output files.
"""
import collections
import json
import os
import sys
from pathlib import Path

ROOT = Path.home() / "work" / "jobs"
SUBAGENT_TOOLS = {"Task", "Agent"}


def summarize(job: Path):
    s = {"job": job.name, "brief": "", "exit": None, "models": collections.Counter(), "tools": collections.Counter(),
         "subagents": 0, "tool_errors": 0, "api_errors": 0, "api_retries": 0, "first_ts": None, "last_ts": None,
         "result": None, "init": None, "out_files": [], "out_count": 0, "log_bytes": 0}
    b = job / "brief.md"
    if b.exists():
        s["brief"] = b.read_text(errors="replace")
    e = job / "EXIT"
    if e.exists():
        s["exit"] = e.read_text().strip()[:20]
    log = job / "log.jsonl"
    if log.exists():
        s["log_bytes"] = log.stat().st_size
        with open(log, errors="replace") as fh:
            for line in fh:
                try:
                    d = json.loads(line)
                except ValueError:
                    continue
                if not isinstance(d, dict):
                    continue
                t = d.get("type")
                ts = d.get("timestamp")
                if ts:
                    s["first_ts"] = s["first_ts"] or ts
                    s["last_ts"] = ts
                if t == "system":
                    sub = d.get("subtype")
                    if sub == "init" and not s["init"]:
                        s["init"] = {k: d.get(k) for k in ("model", "permissionMode", "cwd", "claude_code_version") if d.get(k)}
                    elif sub in ("api_retry", "api_error") or "retry" in str(sub):
                        s["api_retries" if "retry" in str(sub) else "api_errors"] += 1
                elif t == "assistant":
                    m = d.get("message") or {}
                    if m.get("model"):
                        s["models"][m["model"]] += 1
                    for c in m.get("content") or []:
                        if isinstance(c, dict) and c.get("type") == "tool_use":
                            s["tools"][c.get("name")] += 1
                            if c.get("name") in SUBAGENT_TOOLS:
                                s["subagents"] += 1
                    if d.get("error") or m.get("error"):
                        s["api_errors"] += 1
                elif t == "user":
                    for c in (d.get("message") or {}).get("content") or []:
                        if isinstance(c, dict) and c.get("type") == "tool_result" and c.get("is_error"):
                            s["tool_errors"] += 1
                elif t == "result":
                    s["result"] = {k: d.get(k) for k in ("subtype", "is_error", "duration_ms", "duration_api_ms", "num_turns",
                                                         "total_cost_usd", "usage", "modelUsage")}
                    s["result"]["text"] = (d.get("result") or "")[:4000]
    out = job / "out"
    if out.exists():
        files = []
        for dirpath, dirnames, filenames in os.walk(out):
            dirnames[:] = [x for x in dirnames if x not in (".git", "node_modules", "__pycache__", ".venv")]
            for f in filenames:
                files.append(os.path.relpath(os.path.join(dirpath, f), out))
        s["out_count"] = len(files)
        s["out_files"] = sorted(files)[:60]
    s["models"], s["tools"] = dict(s["models"]), dict(s["tools"])
    return s


def main():
    host = os.uname().nodename
    jobs = [summarize(j) for j in sorted(ROOT.iterdir()) if j.is_dir() and not j.name.startswith("_")] if ROOT.exists() else []
    json.dump({"host": host, "jobs": jobs}, sys.stdout)


if __name__ == "__main__":
    main()
