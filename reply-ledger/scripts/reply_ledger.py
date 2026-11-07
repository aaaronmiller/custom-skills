#!/usr/bin/env python3
"""reply-ledger: keep every reply the operator saw, as structured HTML in Living Documents.

Runs as a Claude Code Stop hook. No model calls. Reads only the transcript bytes added since
the last run, appends the operator's prompts and every assistant text block (the text the
operator sees between and after tool calls) to

    ~/LIVING_DOCUMENTS/replies/<session-id>.jsonl      source records, one per line
    ~/LIVING_DOCUMENTS/replies/<session-id>.html       the rendered, navigable session
    ~/LIVING_DOCUMENTS/replies/index.html              every captured session

Usage
  reply_ledger.py --hook                       Stop hook: stdin is the hook JSON; work runs detached
  reply_ledger.py --transcript PATH [--session ID]   capture one transcript now (backfill)
  reply_ledger.py --render-all                 re-render every session page and the index

The hook never blocks or fails the session: it detaches, and every error goes to
~/LIVING_DOCUMENTS/replies/.state/errors.log with exit status 0.
"""
import argparse
import datetime as dt
import fcntl
import html
import json
import os
import re
import subprocess
import sys
import traceback
from pathlib import Path
from zoneinfo import ZoneInfo

OUT = Path(os.environ.get("REPLY_LEDGER_DIR", Path.home() / "LIVING_DOCUMENTS" / "replies"))
STATE = OUT / ".state"
PT = ZoneInfo("America/Los_Angeles")

SUMMARY_PREFIX = "This session is being continued from a previous conversation"
SKIP_USER = ("<command-", "<local-command", "Caveat:", "<bash-", "[Request interrupted")
REMINDER = re.compile(r"<system-reminder>.*?</system-reminder>", re.S)
STATUS_LINE = re.compile(r"^\s*\**DONE:?\**:?\s*(.+)$", re.M)


# ---------- capture ----------

def user_text(msg):
    c = msg.get("content")
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        parts = [b.get("text", "") for b in c if isinstance(b, dict) and b.get("type") == "text"]
        return "\n".join(p for p in parts if p)
    return ""


def records_from(lines):
    """Turn raw transcript lines into prompt, summary and reply records."""
    out = []
    for raw in lines:
        try:
            d = json.loads(raw)
        except ValueError:
            continue
        if d.get("isSidechain") or d.get("isMeta"):
            continue
        t, msg = d.get("type"), d.get("message") or {}
        base = {"ts": d.get("timestamp"), "uuid": d.get("uuid")}
        if t == "user":
            text = REMINDER.sub("", user_text(msg)).strip()
            if not text or text.startswith(SKIP_USER):
                continue
            if text.startswith("<task-notification>"):  # a background task finished; not typed by the operator
                s = re.search(r"<summary>(.*?)</summary>", text, re.S)
                out.append({**base, "role": "event", "text": (s.group(1) if s else "background task finished").strip()})
                continue
            role = "summary" if text.startswith(SUMMARY_PREFIX) or d.get("isCompactSummary") else "user"
            out.append({**base, "role": role, "text": text})
        elif t == "assistant" and isinstance(msg.get("content"), list):
            for b in msg["content"]:
                if isinstance(b, dict) and b.get("type") == "text" and b.get("text", "").strip():
                    out.append({**base, "role": "assistant", "text": b["text"].strip(), "msg_id": msg.get("id")})
    return out


def capture(transcript: Path, session: str, cwd: str = ""):
    """Append the records added since the last run; return how many were added."""
    STATE.mkdir(parents=True, exist_ok=True)
    state_file = STATE / f"{session}.json"
    state = json.loads(state_file.read_text()) if state_file.exists() else {"offset": 0}
    size = transcript.stat().st_size
    if size < state["offset"]:  # transcript rewritten: start over
        state = {"offset": 0}
        (OUT / f"{session}.jsonl").unlink(missing_ok=True)
    with open(transcript, "rb") as fh:
        fh.seek(state["offset"])
        chunk = fh.read()
    end = chunk.rfind(b"\n") + 1  # never parse a half-written last line
    if end == 0:
        return 0
    recs = records_from(chunk[:end].decode("utf-8", "replace").splitlines())
    if recs:
        with open(OUT / f"{session}.jsonl", "a") as fh:
            for r in recs:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    state.update(offset=state["offset"] + end, transcript=str(transcript), cwd=cwd or state.get("cwd", ""),
                 updated=dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"))
    state_file.write_text(json.dumps(state))
    return len(recs)


# ---------- render ----------

def md():
    from markdown_it import MarkdownIt
    return MarkdownIt("commonmark", {"html": False, "linkify": False, "breaks": False}).enable(["table", "strikethrough"])


def when(ts):
    try:
        return dt.datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(PT)
    except (AttributeError, ValueError):
        return None


def turns_of(records):
    turns, cur = [], None
    for r in records:
        if r["role"] in ("user", "summary", "event") or cur is None:
            cur = {"prompt": r if r["role"] != "assistant" else None, "replies": []}
            turns.append(cur)
            if r["role"] != "assistant":
                continue
        cur["replies"].append(r)
    return turns


CSS = """
:root{--bg:#fbfaf7;--fg:#1d1d1f;--mut:#6b6b70;--line:#e4e1da;--card:#ffffff;--acc:#2f5d8a;--code:#f2efe8;--user:#f4f1ea}
@media (prefers-color-scheme:dark){:root{--bg:#141416;--fg:#e9e7e2;--mut:#9a9aa1;--line:#2c2c31;--card:#1c1c20;--acc:#8db4e0;--code:#26262b;--user:#202026}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.6 Charter,"Iowan Old Style",Georgia,serif}
header{padding:20px 24px;border-bottom:1px solid var(--line)}h1{font:600 22px/1.3 system-ui,sans-serif;margin:0 0 4px}
.meta{color:var(--mut);font:13px system-ui,sans-serif}
.wrap{display:grid;grid-template-columns:300px minmax(0,1fr);gap:0}
nav{position:sticky;top:0;height:100vh;overflow:auto;border-right:1px solid var(--line);padding:12px;font:13px/1.4 system-ui,sans-serif}
nav input{width:100%;padding:6px 8px;margin-bottom:8px;border:1px solid var(--line);border-radius:6px;background:var(--card);color:var(--fg)}
nav a{display:block;padding:5px 6px;border-radius:5px;color:var(--fg);text-decoration:none}nav a:hover{background:var(--user)}
nav a .t{color:var(--mut);font-variant-numeric:tabular-nums}
main{padding:16px 28px 80px;max-width:900px}
section.turn{margin:22px 0 34px;border-top:1px solid var(--line);padding-top:14px}
.turn h2{font:600 13px system-ui,sans-serif;color:var(--mut);margin:0 0 8px;letter-spacing:.02em}
details.prompt{background:var(--user);border-radius:8px;padding:10px 14px;margin-bottom:12px;font:14px/1.5 system-ui,sans-serif}
details.prompt summary{cursor:pointer;color:var(--mut)}details.prompt .body{white-space:pre-wrap;margin-top:8px}
details.summary{border:1px dashed var(--line);border-radius:8px;padding:8px 14px;color:var(--mut);font:13px system-ui,sans-serif}
.reply{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:4px 20px;margin:10px 0}
.reply.interim{opacity:.85;font-size:15px;border-style:dashed}
.reply h1,.reply h2,.reply h3{font-family:system-ui,sans-serif;line-height:1.3}.reply h2{font-size:19px;margin-top:22px}
code{background:var(--code);padding:1px 5px;border-radius:4px;font:13.5px ui-monospace,SFMono-Regular,Menlo,monospace}
pre{background:var(--code);padding:12px 14px;border-radius:8px;overflow:auto}pre code{padding:0;background:none}
table{border-collapse:collapse;margin:12px 0;font:14px/1.4 system-ui,sans-serif;display:block;overflow-x:auto}
th,td{border:1px solid var(--line);padding:6px 10px;text-align:left;vertical-align:top}th{background:var(--user)}
a{color:var(--acc)}
@media (max-width:820px){.wrap{grid-template-columns:minmax(0,1fr)}h1{font-size:18px}header{padding:14px 16px}nav{position:static;height:auto;max-height:40vh;border-right:0;border-bottom:1px solid var(--line)}main{padding:12px 16px 60px}}
"""

JS = """
const q=document.getElementById('q');q&&q.addEventListener('input',()=>{const v=q.value.toLowerCase();
document.querySelectorAll('section.turn').forEach(s=>{const hit=!v||s.textContent.toLowerCase().includes(v);
s.style.display=hit?'':'none';const a=document.querySelector('nav a[href="#'+s.id+'"]');if(a)a.style.display=hit?'':'none';});});
"""


def short(text, n):
    t = " ".join(text.split())
    return t if len(t) <= n else t[: n - 1] + "…"


def render_session(session: str):
    src = OUT / f"{session}.jsonl"
    if not src.exists():
        return None
    records = [json.loads(l) for l in src.read_text().splitlines() if l.strip()]
    state_file = STATE / f"{session}.json"
    state = json.loads(state_file.read_text()) if state_file.exists() else {}
    m = md()
    turns = turns_of(records)
    nav, body = [], []
    n = 0
    for t in turns:
        p = t["prompt"]
        if p and p["role"] == "summary":
            body.append(f'<details class="summary"><summary>Context summary after a compaction '
                        f'({when(p["ts"]):%a %m-%d %H:%M} PT)</summary><div>{m.render(p["text"])}</div></details>'
                        if when(p["ts"]) else f'<details class="summary"><summary>Context summary</summary>{m.render(p["text"])}</details>')
            if not t["replies"]:
                continue
        n += 1
        w = when((p or t["replies"][0])["ts"])
        stamp = f"{w:%a %m-%d %H:%M}" if w else ""
        status = ""
        for r in t["replies"]:
            s = STATUS_LINE.search(r["text"])
            if s:
                status = s.group(1).strip("* ")
        if p and p["role"] == "user":
            label = short(p["text"], 70)
        elif p and p["role"] == "event":
            label = "↻ " + short(p["text"], 66)
        else:
            label = short(status, 70) or "continued"
        nav.append(f'<a href="#t{n}"><span class="t">{n}. {stamp}</span><br>{html.escape(label)}</a>')
        parts = [f'<section class="turn" id="t{n}"><h2>Turn {n} &middot; {stamp} PT</h2>']
        if p and p["role"] == "user":
            parts.append(f'<details class="prompt"><summary>Operator: {html.escape(short(p["text"], 160))}</summary>'
                         f'<div class="body">{html.escape(p["text"])}</div></details>')
        elif p and p["role"] == "event":
            parts.append(f'<p class="meta">Background event: {html.escape(short(p["text"], 200))}</p>')
        last = len(t["replies"]) - 1
        for i, r in enumerate(t["replies"]):
            cls = "reply" if i == last else "reply interim"
            parts.append(f'<div class="{cls}">{m.render(r["text"])}</div>')
        parts.append("</section>")
        body.append("".join(parts))
    first = next((r for r in records if r["role"] == "user"), None)
    title = short(first["text"], 90) if first else session
    first_w, last_w = when(records[0]["ts"]) if records else None, when(records[-1]["ts"]) if records else None
    meta = (f'Session {session} &middot; {html.escape(state.get("cwd", ""))} &middot; {n} turns &middot; '
            f'{first_w:%Y-%m-%d %H:%M} to {last_w:%Y-%m-%d %H:%M} PT' if first_w and last_w else f"Session {session}")
    page = (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>Replies {session[:8]}</title><style>{CSS}</style></head><body>'
            f'<header><h1>{html.escape(title)}</h1><div class="meta">{meta} &middot; <a href="index.html">all sessions</a></div></header>'
            f'<div class="wrap"><nav><input id="q" placeholder="Filter turns" aria-label="Filter turns">{"".join(nav)}</nav>'
            f'<main>{"".join(body)}</main></div><script>{JS}</script></body></html>')
    tmp = OUT / f".{session}.html.tmp"
    tmp.write_text(page)
    tmp.replace(OUT / f"{session}.html")
    return {"session": session, "title": title, "turns": n, "cwd": state.get("cwd", ""),
            "first": first_w.isoformat() if first_w else "", "last": last_w.isoformat() if last_w else ""}


def render_index():
    rows = []
    for f in OUT.glob("*.jsonl"):
        s = f.stem
        lines = [json.loads(l) for l in f.read_text().splitlines() if l.strip()]
        if not lines:
            continue
        first = next((r for r in lines if r["role"] == "user"), lines[0])
        state_file = STATE / f"{s}.json"
        state = json.loads(state_file.read_text()) if state_file.exists() else {}
        turns = sum(1 for r in lines if r["role"] == "user")
        rows.append((lines[-1].get("ts") or "", s, short(first["text"], 120), turns, state.get("cwd", "")))
    rows.sort(reverse=True)
    trs = "".join(f'<tr><td>{(when(ts) or dt.datetime.min):%Y-%m-%d %H:%M}</td><td><a href="{s}.html">{html.escape(t)}</a></td>'
                  f'<td>{n}</td><td>{html.escape(c)}</td></tr>' for ts, s, t, n, c in rows)
    page = (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>Session replies</title><style>{CSS} main{{max-width:1100px}}</style></head><body>'
            f'<header><h1>Session replies</h1><div class="meta">Every reply the operator saw, captured by the reply-ledger Stop hook. '
            f'Newest first.</div></header><main><table><tr><th>Last reply (PT)</th><th>First prompt</th><th>Turns</th><th>Folder</th></tr>'
            f'{trs}</table></main></body></html>')
    (OUT / "index.html").write_text(page)


# ---------- entry points ----------

def run(transcript: Path, session: str, cwd: str):
    STATE.mkdir(parents=True, exist_ok=True)
    with open(STATE / f"{session}.lock", "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)  # serialize per session; a waiting run picks up the newest bytes
        added = capture(transcript, session, cwd)
        if added or not (OUT / f"{session}.html").exists():
            render_session(session)
            render_index()
    return added


def log_error():
    STATE.mkdir(parents=True, exist_ok=True)
    with open(STATE / "errors.log", "a") as fh:
        fh.write(f"{dt.datetime.now().isoformat(timespec='seconds')} {traceback.format_exc()}\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--hook", action="store_true")
    ap.add_argument("--transcript")
    ap.add_argument("--session")
    ap.add_argument("--cwd", default="")
    ap.add_argument("--render-all", action="store_true")
    a = ap.parse_args()
    try:
        if a.hook:
            h = json.load(sys.stdin)
            tp, sid = h.get("transcript_path"), h.get("session_id")
            if tp and sid and Path(tp).exists():
                subprocess.Popen([sys.executable, "-I", os.path.abspath(__file__), "--transcript", tp,
                                  "--session", sid, "--cwd", h.get("cwd", "")],
                                 stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                 start_new_session=True)
            return 0
        if a.render_all:
            for f in OUT.glob("*.jsonl"):
                render_session(f.stem)
            render_index()
            return 0
        if a.transcript:
            p = Path(a.transcript)
            added = run(p, a.session or p.stem, a.cwd)
            print(json.dumps({"session": a.session or p.stem, "added": added, "page": str(OUT / f"{a.session or p.stem}.html")}))
            return 0
        ap.print_help()
    except Exception:
        log_error()
    return 0


if __name__ == "__main__":
    sys.exit(main())
