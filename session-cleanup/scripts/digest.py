#!/usr/bin/env python3
"""Digest one agent session file into a compact text: user asks, last assistant replies, files touched."""
import json, re, sqlite3, sys, os, collections

MAX_USER = 1800
MAX_ASSIST = 2500

def txt(content):
    if isinstance(content, str):
        return content
    out = []
    if isinstance(content, list):
        for c in content:
            if isinstance(c, dict):
                if c.get("type") in ("text", "input_text", "output_text"):
                    out.append(c.get("text") or "")
            elif isinstance(c, str):
                out.append(c)
    return "\n".join(out)

PATH_RE = re.compile(r"/home/(?:cheta|misscheta)/[A-Za-z0-9_.@+/-]{3,}")

def claude(path):
    users, assists, paths, ts = [], [], collections.Counter(), []
    for l in open(path, errors="replace"):
        try:
            d = json.loads(l)
        except Exception:
            continue
        t = d.get("timestamp")
        if t: ts.append(t)
        m = d.get("message")
        if not isinstance(m, dict):
            continue
        if d.get("type") == "user" and not d.get("isMeta"):
            s = txt(m.get("content"))
            if s and not s.startswith("<") and "tool_result" not in str(m.get("content"))[:200]:
                users.append((t, s))
        elif d.get("type") == "assistant":
            s = txt(m.get("content"))
            if s.strip():
                assists.append((t, s))
            for c in m.get("content") or []:
                if isinstance(c, dict) and c.get("type") == "tool_use":
                    for p in PATH_RE.findall(json.dumps(c.get("input"))):
                        paths[p] += 1
    return users, assists, paths, ts

def codex(path):
    users, assists, paths, ts = [], [], collections.Counter(), []
    for l in open(path, errors="replace"):
        try:
            d = json.loads(l)
        except Exception:
            continue
        t = d.get("timestamp"); ts.append(t) if t else None
        p = d.get("payload") or {}
        if d.get("type") == "response_item" and p.get("type") == "message":
            s = txt(p.get("content"))
            if p.get("role") == "user" and s and not s.startswith("<"):
                users.append((t, s))
            elif p.get("role") == "assistant" and s.strip():
                assists.append((t, s))
        elif d.get("type") == "response_item" and p.get("type") in ("function_call", "custom_tool_call", "local_shell_call"):
            for q in PATH_RE.findall(json.dumps(p)):
                paths[q] += 1
    return users, assists, paths, ts

def omp(path):
    users, assists, paths, ts = [], [], collections.Counter(), []
    for l in open(path, errors="replace"):
        try:
            d = json.loads(l)
        except Exception:
            continue
        t = d.get("timestamp"); ts.append(t) if t else None
        m = d.get("message")
        if d.get("type") != "message" or not isinstance(m, dict):
            continue
        if m.get("role") == "user":
            s = txt(m.get("content"))
            if s: users.append((t, s))
        elif m.get("role") == "assistant":
            s = txt(m.get("content"))
            if s.strip(): assists.append((t, s))
            for c in m.get("content") or []:
                if isinstance(c, dict) and c.get("type") in ("toolCall", "tool_use"):
                    for q in PATH_RE.findall(json.dumps(c)):
                        paths[q] += 1
    return users, assists, paths, ts

def agy(path):
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    users, assists, paths = [], [], collections.Counter()
    for idx, st, payload in con.execute("select idx, step_type, step_payload from steps order by idx"):
        if not payload:
            continue
        runs = re.findall(rb"[\x20-\x7e\n\t\xc2-\xf4\x80-\xbf]{40,}", payload)
        s = "\n".join(r.decode("utf8", "replace") for r in runs)
        for q in PATH_RE.findall(s):
            paths[q] += 1
        if s.strip():
            (users if st in (1, 14, 19) else assists).append((str(idx), f"[step_type {st}] " + s))
    return users, assists, paths, []

def main():
    kind, path, out = sys.argv[1], sys.argv[2], sys.argv[3]
    users, assists, paths, ts = {"claude": claude, "codex": codex, "omp": omp, "agy": agy}[kind](path)
    with open(out, "w") as f:
        f.write(f"SESSION FILE: {path}\nHARNESS: {kind}\n")
        if ts:
            f.write(f"FIRST: {min(ts)}  LAST: {max(ts)}\n")
        f.write(f"USER MESSAGES: {len(users)}  ASSISTANT MESSAGES: {len(assists)}\n\n== USER MESSAGES (all, truncated) ==\n")
        for t, s in users[-60:] if len(users) > 60 else users:
            f.write(f"\n[{t}] {s[:MAX_USER]}\n")
        f.write("\n== LAST ASSISTANT MESSAGES ==\n")
        for t, s in assists[-6:]:
            f.write(f"\n[{t}] {s[-MAX_ASSIST:]}\n")
        f.write("\n== PATHS TOUCHED (top 40) ==\n")
        for p, n in paths.most_common(40):
            f.write(f"{n:4d} {p}\n")

if __name__ == "__main__":
    main()
