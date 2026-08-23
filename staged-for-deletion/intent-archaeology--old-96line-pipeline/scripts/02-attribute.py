#!/usr/bin/env python3
"""Phase 2: discover sessions and attribute them to projects.

The deterministic ladder, first match wins, method always recorded:

  1 cwd exact          session cwd resolves to a known project path
  2 git identity       cwd's git root matches a project remote or initial sha
  3 paths touched      absolute paths in the session fall inside one project
  4 branch name        spec-kit feature branch maps to a project
  5 name similarity    workspace basename matches a project slug
  6 unattributed       left for the model or the human. Never guessed here.

Rungs 1 to 4 are deterministic. Coverage by rung is the trust signal for
everything downstream, so it is reported, not hidden.

Idempotent and resumable.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib.common import (  # noqa: E402
    PIPELINE_VERSION, cass_json, connect, die, git, have, iter_jsonl, log,
    now, observe, report, sha,
)

HARNESS_GLOBS = [
    ("claude_code", Path.home() / ".claude/projects", "**/*.jsonl"),
    ("codex", Path.home() / ".codex/sessions", "**/*.jsonl"),
    ("pi", Path.home() / ".pi/agent/sessions", "**/*.jsonl"),
    ("omp", Path.home() / ".omp/agent/sessions", "**/*.jsonl"),
    ("kimi", Path.home() / ".kimi/sessions", "**/*/wire.jsonl"),
    ("openclaw", Path.home() / ".openclaw/agents", "**/sessions/*.jsonl"),
    ("clawdbot", Path.home() / ".clawdbot/sessions", "**/*.jsonl"),
    ("factory", Path.home() / ".factory/sessions", "**/*.jsonl"),
]


def load_projects(conn) -> list[dict]:
    rows = conn.execute(
        "SELECT id,path,git_remote,git_initial_sha,kind FROM project"
        " WHERE kind IN ('project','monorepo')"
    ).fetchall()
    out = []
    for r in rows:
        out.append({
            "id": r["id"], "path": str(Path(r["path"]).resolve()),
            "remote": (r["git_remote"] or "").rstrip("/").removesuffix(".git").lower(),
            "sha": r["git_initial_sha"], "base": Path(r["path"]).name.lower(),
        })
    return sorted(out, key=lambda p: -len(p["path"]))  # deepest path first


def discover_from_cass(limit: int) -> list[dict]:
    """Explicit fallback only: CASS session listing can be expensive on large archives."""
    data = cass_json(["sessions", "--json", "--limit", str(limit)])
    if not data:
        return []
    rows = data.get("sessions", data) if isinstance(data, dict) else data
    out = []
    for s in rows if isinstance(rows, list) else []:
        if not isinstance(s, dict):
            continue
        path = s.get("path") or s.get("source_path")
        if not path:
            continue
        out.append({
            "harness": s.get("agent") or "unknown",
            "source_path": path,
            "workspace": s.get("workspace") or s.get("workspace_original"),
            "session_id": s.get("session_id") or s.get("id"),
            "first_ts": s.get("created_at") or s.get("first_ts"),
            "last_ts": s.get("updated_at") or s.get("last_ts"),
            "message_count": s.get("message_count"),
        })
    return out


def discover_from_disk() -> list[dict]:
    out = []
    for harness, root, pattern in HARNESS_GLOBS:
        if not root.is_dir():
            continue
        for p in root.glob(pattern):
            if p.is_file():
                out.append({
                    "harness": harness, "source_path": str(p),
                    "workspace": None, "session_id": p.stem,
                    "first_ts": None, "last_ts": None, "message_count": None,
                })
    return out


def peek(path: Path, limit: int = 400) -> dict:
    """Read enough of a session to attribute it without parsing the whole file."""
    info = {"cwd": None, "branch": None, "paths": set(), "first_ts": None,
            "last_ts": None, "n": 0}
    for _, obj in iter_jsonl(path):
        info["n"] += 1
        if info["cwd"] is None and obj.get("cwd"):
            info["cwd"] = obj["cwd"]
        if info["branch"] is None and obj.get("gitBranch"):
            info["branch"] = obj["gitBranch"]
        ts = obj.get("timestamp") or obj.get("ts")
        if ts:
            if info["first_ts"] is None:
                info["first_ts"] = ts
            info["last_ts"] = ts
        blob = obj.get("toolUseResult") or obj.get("message") or {}
        text = json.dumps(blob)[:4000] if not isinstance(blob, str) else blob[:4000]
        for token in text.split('"'):
            if token.startswith("/") and len(token) > 8 and "/" in token[1:]:
                info["paths"].add(token)
        if info["n"] >= limit and info["cwd"]:
            break
    return info


def attribute(info: dict, workspace: str | None, projects: list[dict]) -> tuple[str | None, str, int, float]:
    candidates = [c for c in (info.get("cwd"), workspace) if c]

    for c in candidates:
        rc = str(Path(c).expanduser().resolve()) if c.startswith("/") or c.startswith("~") else c
        for p in projects:
            if rc == p["path"] or rc.startswith(p["path"] + "/"):
                return p["id"], "cwd", 1, 1.0

    for c in candidates:
        cp = Path(c).expanduser()
        if cp.is_dir():
            root = git(cp, "rev-parse", "--show-toplevel")
            if root:
                rp = str(Path(root).resolve())
                for p in projects:
                    if rp == p["path"]:
                        return p["id"], "git-identity", 2, 1.0
                remote = (git(cp, "config", "--get", "remote.origin.url") or "")
                remote = remote.rstrip("/").removesuffix(".git").lower()
                if remote:
                    for p in projects:
                        if p["remote"] and p["remote"] == remote:
                            return p["id"], "git-identity", 2, 1.0

    if info["paths"]:
        hits = Counter()
        for tp in info["paths"]:
            for p in projects:
                if tp.startswith(p["path"] + "/"):
                    hits[p["id"]] += 1
                    break
        if hits:
            top, n = hits.most_common(1)[0]
            total = sum(hits.values())
            if total and n / total >= 0.6:
                return top, "paths-touched", 3, round(n / total, 2)

    branch = info.get("branch")
    if branch and branch not in ("main", "master", "develop", "dev"):
        b = branch.lower().lstrip("0123456789-")
        for p in projects:
            if b and (b in p["base"] or p["base"] in b):
                return p["id"], "branch-name", 4, 0.7

    for c in candidates:
        base = Path(c).name.lower()
        for p in projects:
            if base and base == p["base"]:
                return p["id"], "name-match", 5, 0.5

    return None, "unattributed", 6, 0.0


def main() -> int:
    ap = argparse.ArgumentParser(description="Phase 2: session attribution")
    ap.add_argument("--limit", type=int, default=0, help="cap sessions processed")
    ap.add_argument("--rescan", action="store_true", help="re-attribute existing sessions")
    ap.add_argument(
        "--discovery", choices=("disk", "cass"), default="disk",
        help="discovery source; disk is the bounded default, cass is explicit fallback",
    )
    ap.add_argument(
        "--cass-limit", type=int, default=100,
        help="maximum sessions requested only when --discovery cass is selected",
    )
    args = ap.parse_args()

    conn = connect()
    projects = load_projects(conn)
    if not projects:
        die("no projects found. Run 01-inventory.py first.")

    log(conn, "attribute", "start")

    if args.discovery == "cass":
        sessions = discover_from_cass(args.cass_limit)
        source = "cass"
        if not sessions:
            print("CASS enumeration returned no sessions; falling back to direct disk discovery")
            sessions = discover_from_disk()
            source = "disk"
    else:
        sessions = discover_from_disk()
        source = "disk"
    print(f"Discovered {len(sessions)} sessions via {source}")

    known = {r["source_path"] for r in
             conn.execute("SELECT source_path FROM session").fetchall()} if not args.rescan else set()

    processed = 0
    for s in sessions:
        if s["source_path"] in known:
            continue
        if args.limit and processed >= args.limit:
            break
        p = Path(s["source_path"])
        info = peek(p) if p.is_file() else {"cwd": None, "branch": None, "paths": set(),
                                            "first_ts": None, "last_ts": None, "n": 0}
        pid, method, rung, conf = attribute(info, s.get("workspace"), projects)
        sid = f"{s['harness']}:{s.get('session_id') or sha(s['source_path'])}"

        conn.execute(
            """INSERT INTO session (id,harness,harness_session_id,source_path,workspace,
                 first_ts,last_ts,message_count,project_id,attribution_method,
                 attribution_rung,attribution_confidence,pipeline_version)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
               ON CONFLICT(id) DO UPDATE SET
                 project_id=excluded.project_id,
                 attribution_method=excluded.attribution_method,
                 attribution_rung=excluded.attribution_rung,
                 attribution_confidence=excluded.attribution_confidence""",
            (sid, s["harness"], s.get("session_id"), s["source_path"],
             s.get("workspace") or info.get("cwd"),
             s.get("first_ts") or info.get("first_ts"),
             s.get("last_ts") or info.get("last_ts"),
             s.get("message_count") or info.get("n"),
             pid, method, rung, conf, PIPELINE_VERSION),
        )
        processed += 1
        if processed % 100 == 0:
            conn.commit()
            print(f"  {processed} sessions attributed")

    conn.commit()

    rows = conn.execute(
        "SELECT attribution_method m, attribution_rung r, COUNT(*) c"
        " FROM session GROUP BY m,r ORDER BY r"
    ).fetchall()
    report("Attribution by rung", [(f"{r['r']} {r['m']}", r["c"]) for r in rows])

    total = conn.execute("SELECT COUNT(*) c FROM session").fetchone()["c"]
    det = conn.execute(
        "SELECT COUNT(*) c FROM session WHERE attribution_rung <= 4"
    ).fetchone()["c"]
    pct = (100.0 * det / total) if total else 0.0
    print(f"\nDeterministic coverage (rungs 1-4): {det}/{total} = {pct:.1f}%")

    if pct < 70 and total:
        observe(conn, "attribution_fallthrough",
                f"deterministic coverage {pct:.1f}% below 70%")
        conn.commit()
        print("  Low coverage. Most sessions were probably started from ~ rather than")
        print("  a project root. Expect to resolve more by hand.")

    resid = conn.execute(
        "SELECT source_path, workspace FROM session WHERE attribution_rung >= 5"
        " ORDER BY last_ts DESC LIMIT 20"
    ).fetchall()
    if resid:
        print(f"\nSpot-check sample (rung 5+), newest first:")
        for r in resid:
            print(f"  {r['workspace'] or '?'}  <-  {r['source_path']}")

    log(conn, "attribute", "done", f"{det}/{total}")
    print("\nExit criterion: coverage reported and sample above reviewed. Next: 03-enrich.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
