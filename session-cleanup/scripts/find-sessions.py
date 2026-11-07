#!/usr/bin/env python3
"""List running agent sessions on this host and map each to its session file.

  python3 -I find-sessions.py > sessions.tsv
Columns: key, harness, session_id, folder, session_file, pid, started.
Harnesses: claude, codex, omp, agy. Resolution rules (verified 2026-11-07):
  claude --resume <id>  -> ~/.claude/projects/<cwd-slug>/<id>.jsonl ; bare claude -> newest jsonl in that slug dir
  codex resume <id>     -> ~/.codex/sessions/**/rollout-*<id>.jsonl ; bare codex -> newest rollout whose cwd matches
  omp --resume <id>     -> ~/.omp/agent/sessions/*/*<id>*.jsonl
  agy --conversation=<id> -> ~/.gemini/antigravity-cli/conversations/<id>.db
Daemons (app-server, worker brokers) are skipped.
"""
import glob
import json
import os
import re
import subprocess

HOME = os.path.expanduser("~")


def procs():
    out = subprocess.run(["ps", "-eo", "pid=,lstart=,args="], capture_output=True, text=True).stdout
    for line in out.splitlines():
        m = re.match(r"\s*(\d+)\s+(\w{3} \w{3}\s+\d+ [\d:]+ \d{4})\s+(.*)", line)
        if m:
            yield int(m.group(1)), m.group(2), m.group(3)


def cwd(pid):
    try:
        return os.readlink(f"/proc/{pid}/cwd")
    except OSError:
        return ""


def newest(pattern, pred=None):
    files = sorted(glob.glob(pattern, recursive=True), key=os.path.getmtime, reverse=True)
    for f in files[:200]:
        if pred is None or pred(f):
            return f
    return ""


def codex_cwd_is(path, want):
    try:
        with open(path, errors="replace") as fh:
            for _ in range(5):
                line = fh.readline()
                if f'"cwd":"{want}"' in line.replace(" ", ""):
                    return True
    except OSError:
        pass
    return False


def main():
    rows, seen = [], set()
    for pid, started, args in procs():
        a = args.split()
        exe = os.path.basename(a[0]) if a else ""
        if exe == "node" and len(a) > 1:
            continue  # the node shim; the native child is listed too
        if "app-server" in args or "worker_daemon" in args or "pid-update-loop" in args:
            continue
        c = cwd(pid)
        h = sid = f = ""
        if exe == "claude":
            h = "claude"
            m = re.search(r"--resume\s+([0-9a-f-]{36})", args)
            slug = c.replace("/", "-").replace(".", "-")
            d = f"{HOME}/.claude/projects/{slug}"
            if m:
                sid, f = m.group(1), f"{d}/{m.group(1)}.jsonl"
            else:
                f = newest(f"{d}/*.jsonl")
                sid = os.path.basename(f)[:-6] if f else ""
        elif exe == "codex":
            h = "codex"
            m = re.search(r"resume\s+([0-9a-f-]{36})", args)
            if m:
                sid = m.group(1)
                f = newest(f"{HOME}/.codex/sessions/**/rollout-*{sid}.jsonl")
            else:
                f = newest(f"{HOME}/.codex/sessions/**/rollout-*.jsonl", lambda p: codex_cwd_is(p, c))
                sid = re.sub(r".*-([0-9a-f]{8}-[0-9a-f-]{27})\.jsonl$", r"\1", f) if f else ""
        elif exe == "omp":
            h = "omp"
            m = re.search(r"--resume\s+([0-9a-f-]{20,})", args)
            if m:
                sid = m.group(1)
                f = newest(f"{HOME}/.omp/agent/sessions/*/*{sid}*.jsonl")
        elif exe == "agy":
            h = "agy"
            m = re.search(r"--conversation=([0-9a-f-]{36})", args)
            if m:
                sid = m.group(1)
                f = f"{HOME}/.gemini/antigravity-cli/conversations/{sid}.db"
        if not h or (h, sid) in seen:
            continue
        seen.add((h, sid))
        rows.append((h, sid, c, f, pid, started))
    for i, r in enumerate(rows, 1):
        print("\t".join([f"L{i}"] + [str(x) for x in r]))


if __name__ == "__main__":
    main()
