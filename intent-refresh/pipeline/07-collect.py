#!/usr/bin/env python3
"""Phase 7: collect the operator's prompts from every harness since a date.

Deterministic. No model runs here. Output is the input to the cleanup,
correlation and summary passes (08) and to the intent batches (04/05).

  python3 -I 07-collect.py --since 2026-08-29 [--run NAME]

Writes ~/.intent-archaeology/corpus/<run>/prompts.jsonl and sessions.jsonl.

Sources, chosen by measured reliability (2026-11-05):
  claude_code  raw ~/.claude/projects/*/*.jsonl (subagents/ excluded: those
               turns are agent-written). entrypoint 'cli' = interactive,
               sdk-* = dispatched.
  codex        raw ~/.codex/sessions/**/rollout-*.jsonl, event_msg/user_message.
               originator codex_exec = dispatched; casr = a converted copy of
               another harness's session (kept, deduped by text below).
  omp, pi      raw top-level session files. Nested files are subagents.
  muse, hermes, antigravity, openclaw
               the cass archive database, read-only (role 'user'). cass labels
               omp tool output as 'user', which is why omp is read raw.

Rules carried from earlier runs:
  - Filtering is structural, never editorial: harness wrappers, compaction
    summaries, task notifications and interruption markers are dropped;
    no prompt is dropped for its content.
  - Every prompt is kept whole. Summaries are a display decision (26%
    corpus-loss lesson, 2026-08-04).
  - Identical text is one prompt: the first occurrence is kept and the rest
    are counted (one runaway omp session repeats a few prompts 24,613 times).
  - Secrets are redacted before anything is written.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib.common import BASE, confined, redact, sha  # noqa: E402

HOME = Path.home()
CASS_DB = HOME / ".local/share/coding-agent-search/agent_search.db"
DOSSIERS = HOME / "LIVING_DOCUMENTS/projects"
SKIP_PREFIX = ("<", "This session is being continued", "[SYSTEM", "Caveat:",
               "[Request interrupted", "[Image #", "Base directory for this skill",
               "# AGENTS.md instructions")
MIN_CHARS = 12
CASS_AGENTS = ("muse", "hermes", "antigravity", "openclaw/main")


def epoch_ms(day: str) -> int:
    return int(datetime.fromisoformat(day).replace(tzinfo=timezone.utc).timestamp() * 1000)


def iso(ms) -> str:
    try:
        return datetime.fromtimestamp(int(ms) / 1000, timezone.utc).isoformat()
    except (TypeError, ValueError, OSError):
        return ""


def text_of(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(b.get("text", "") for b in content
                         if isinstance(b, dict) and b.get("type") in ("text", "input_text"))
    return ""


def keep(text: str) -> bool:
    t = text.strip()
    return len(t) >= MIN_CHARS and not t.startswith(SKIP_PREFIX)


def jsonl(path: str):
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                if line.startswith("{"):
                    try:
                        yield json.loads(line)
                    except ValueError:
                        continue
    except OSError:
        return


def recent(paths, since_ts: float):
    for p in paths:
        try:
            if os.path.getmtime(p) >= since_ts:
                yield p
        except OSError:
            continue


def claude(since: str, since_ts: float):
    for p in recent(glob.glob(str(HOME / ".claude/projects/*/*.jsonl")), since_ts):
        sess = {"harness": "claude_code", "source_path": p, "session_id": Path(p).stem,
                "cwd": None, "origin": "interactive"}
        rows = []
        for d in jsonl(p):
            if d.get("entrypoint", "").startswith("sdk"):
                sess["origin"] = "dispatched"
            if d.get("cwd") and not sess["cwd"]:
                sess["cwd"] = d["cwd"]
            if (d.get("type") != "user" or d.get("isMeta") or d.get("isCompactSummary")
                    or d.get("isSidechain")):
                continue
            ts = d.get("timestamp", "")
            t = text_of((d.get("message") or {}).get("content"))
            if ts >= since and keep(t):
                rows.append((ts, t, d.get("cwd")))
        yield sess, rows


def codex(since: str, since_ts: float):
    for p in recent(glob.glob(str(HOME / ".codex/sessions/*/*/*/*.jsonl")), since_ts):
        sess = {"harness": "codex", "source_path": p, "session_id": Path(p).stem,
                "cwd": None, "origin": "interactive"}
        rows, items = [], []
        for d in jsonl(p):
            pl = d.get("payload") or {}
            if d.get("type") == "session_meta":
                sess["cwd"] = pl.get("cwd")
                orig = str(pl.get("originator") or "")
                if "exec" in orig:
                    sess["origin"] = "dispatched"
                elif orig == "casr":
                    sess["origin"] = "converted"
            ts = d.get("timestamp", "")
            if d.get("type") == "event_msg" and pl.get("type") == "user_message":
                t = pl.get("message") or ""
                if ts >= since and keep(t):
                    rows.append((ts, t, sess["cwd"]))
            # Newer codex builds (codex-tui, 2026-09) record the turn only as a
            # response_item; the injected AGENTS.md block is skipped by keep().
            if d.get("type") == "response_item" and pl.get("role") == "user":
                t = text_of(pl.get("content"))
                if ts >= since and keep(t):
                    items.append((ts, t, sess["cwd"]))
        yield sess, rows or items


def omp_like(harness: str, root: Path, since: str, since_ts: float):
    for p in recent(glob.glob(str(root / "*/*.jsonl")), since_ts):
        sess = {"harness": harness, "source_path": p, "session_id": Path(p).stem,
                "cwd": None, "origin": "interactive"}
        rows = []
        for d in jsonl(p):
            if d.get("type") == "session":
                sess["cwd"] = d.get("cwd")
            if d.get("type") != "message":
                continue
            m = d.get("message") or {}
            if m.get("role") != "user":
                continue
            ts = d.get("timestamp", "")
            t = text_of(m.get("content"))
            if ts >= since and keep(t):
                rows.append((ts, t, sess["cwd"]))
        yield sess, rows


def from_cass(since: str):
    if not CASS_DB.exists():
        return
    con = sqlite3.connect(f"file:{CASS_DB}?mode=ro", uri=True)
    q = f"""SELECT a.slug, c.id, c.source_path, w.path, m.created_at, m.content
              FROM conversations c JOIN agents a ON a.id=c.agent_id
              LEFT JOIN workspaces w ON w.id=c.workspace_id
              JOIN messages m ON m.conversation_id=c.id
             WHERE c.started_at >= ? AND m.role='user'
               AND a.slug IN ({','.join('?' * len(CASS_AGENTS))})
             ORDER BY c.id, m.idx"""
    cur, sess, rows = None, None, []
    for slug, cid, path, ws, created, content in con.execute(q, (epoch_ms(since), *CASS_AGENTS)):
        if cid != cur:
            if sess:
                yield sess, rows
            cur, rows = cid, []
            sess = {"harness": slug.split("/")[0], "source_path": path, "session_id": str(cid),
                    "cwd": ws, "origin": "dispatched" if "/.gemini/antigravity" in path else "interactive"}
        if keep(content or ""):
            rows.append((iso(created), content, ws))
    if sess:
        yield sess, rows
    con.close()


def dossier_roots() -> list[tuple[str, str]]:
    out = []
    for pm in DOSSIERS.glob("*/project.md"):
        m = re.search(r"^source-root:\s*(\S+)", pm.read_text(errors="replace"), re.M)
        if m and m.group(1).startswith("/"):
            out.append((os.path.realpath(m.group(1)), pm.parent.name))
        out.append((str(pm.parent), pm.parent.name))
    return sorted(out, key=lambda r: -len(r[0]))


UNSPECIFIC = {str(HOME), str(HOME / "tmp"), str(HOME / "code"), str(HOME / "code2"),
              str(HOME / "LIVING_DOCUMENTS"), str(DOSSIERS), "/tmp", "/"}


def correlate(cwd: str | None, roots) -> tuple[str | None, str]:
    """Deterministic rungs. Returns (dossier id or code:<name>, rung)."""
    if not cwd:
        return None, "no-cwd"
    c = os.path.realpath(cwd)
    if c in UNSPECIFIC:
        return None, "unspecific-cwd"
    for root, did in roots:
        if c == root or c.startswith(root + os.sep):
            return did, "cwd-in-dossier-root"
    for base in (HOME / "code", HOME / "code2"):
        b = str(base) + os.sep
        if c.startswith(b):
            name = c[len(b):].split(os.sep)[0]
            if (DOSSIERS / name / "project.md").exists():
                return name, "repo-name-matches-dossier"
            return "code:" + name, "cwd-in-repo-without-dossier"
    return None, "cwd-outside-projects"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", required=True, help="YYYY-MM-DD")
    ap.add_argument("--run", help="run folder name (default: since date)")
    a = ap.parse_args()
    since = a.since + "T00:00:00"
    since_ts = epoch_ms(a.since) / 1000
    out = confined(f"corpus/{a.run or a.since}", BASE)
    out.mkdir(parents=True, exist_ok=True)

    roots = dossier_roots()
    seen: dict[str, dict] = {}
    sessions = []
    sources = [claude(since, since_ts), codex(since, since_ts),
               omp_like("omp", HOME / ".omp/agent/sessions", since, since_ts),
               omp_like("pi", HOME / ".pi/agent/sessions", since, since_ts),
               from_cass(since)]
    for src in sources:
        for sess, rows in src:
            if not rows:
                continue
            sid = f"{sess['harness']}:{sess['session_id']}"
            proj, rung = correlate(sess["cwd"], roots)
            sess.update(id=sid, project=proj, rung=rung, prompts=0, repeats=0,
                        first_ts=min(r[0] for r in rows), last_ts=max(r[0] for r in rows))
            for i, (ts, text, cwd) in enumerate(sorted(rows, key=lambda r: r[0])):
                clean, hits = redact(text.strip())
                key = sha(" ".join(clean.split()), n=20)
                if key in seen:
                    seen[key]["repeats"] += 1
                    sess["repeats"] += 1
                    continue
                seen[key] = {"id": "op_" + key, "session": sid, "harness": sess["harness"],
                             "origin": sess["origin"], "ts": ts, "seq": i,
                             "cwd": cwd or sess["cwd"], "project": proj, "rung": rung,
                             "chars": len(clean), "redactions": hits, "repeats": 0,
                             "text": clean}
                sess["prompts"] += 1
            sessions.append(sess)

    prompts = sorted(seen.values(), key=lambda r: r["ts"])
    with open(out / "prompts.jsonl", "w") as fh:
        for r in prompts:
            fh.write(json.dumps(r) + "\n")
    with open(out / "sessions.jsonl", "w") as fh:
        for s in sorted(sessions, key=lambda s: s["first_ts"]):
            fh.write(json.dumps(s) + "\n")

    by = {}
    for r in prompts:
        k = (r["harness"], r["origin"])
        by[k] = by.get(k, 0) + 1
    print(f"{len(prompts)} unique prompts from {len(sessions)} sessions -> {out}")
    for k, n in sorted(by.items()):
        print(f"  {k[0]:12} {k[1]:12} {n}")
    rungs = {}
    for s in sessions:
        rungs[s["rung"]] = rungs.get(s["rung"], 0) + 1
    print("session correlation:", rungs)
    return 0


if __name__ == "__main__":
    sys.exit(main())
