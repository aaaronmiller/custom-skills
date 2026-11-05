#!/usr/bin/env python3
"""Phase 9: load a refined corpus run into the archaeology database.

  python3 -I 09-load.py --run 2026-08-29

Operator-authored prompts become human events under the project their
dossier maps to, so 04-batch and 05-merge can derive intents from them and
intent-find sees them. Agent briefs are recorded as non-human events (counted
and listed as filtered, never classified as operator intent).

Idempotent: existing event ids are skipped. Event text is the redacted
original, never the cleaned text, because 05-merge's provenance gate quotes
against it.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib.common import BASE, PIPELINE_VERSION, confined, connect, log, now  # noqa: E402
from lib.corpus import load  # noqa: E402

DOSSIERS = Path.home() / "LIVING_DOCUMENTS/projects"


def project_ids(conn, dossiers: set[str]) -> dict[str, str]:
    """Map each dossier id to a database project id, creating rows as needed."""
    by_path = {os.path.realpath(r["path"]): r["id"] for r in
               conn.execute("SELECT id, path FROM project WHERE kind IN ('project','monorepo')")}
    out = {}
    for d in sorted(dossiers):
        pm = DOSSIERS / d / "project.md"
        root = None
        if pm.exists():
            m = re.search(r"^source-root:\s*(\S+)", pm.read_text(errors="replace"), re.M)
            root = os.path.realpath(m.group(1)) if m else None
        if root and root in by_path:
            out[d] = by_path[root]
            continue
        pid = "ld-" + d.replace("new:", "new-")
        conn.execute(
            "INSERT OR IGNORE INTO project (id,path,root,kind,description,pipeline_version,created_at)"
            " VALUES (?,?,?,?,?,?,?)",
            (pid, root or str(DOSSIERS / d.replace("new:", "")), "living-documents", "project",
             f"dossier {d}", PIPELINE_VERSION, now()))
        out[d] = pid
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    a = ap.parse_args()
    run = confined(f"corpus/{a.run}", BASE)
    prompts, sessions = load(run)
    conn = connect()
    pids = project_ids(conn, {p["dossier"] for p in prompts})

    have = {r[0] for r in conn.execute("SELECT id FROM event WHERE id LIKE 'evt_op_%'")}
    added = Counter()
    for sid, s in sessions.items():
        mine = [p for p in prompts if p["session"] == sid]
        if not mine:
            continue
        main_dossier = Counter(p["dossier"] for p in mine).most_common(1)[0][0]
        conn.execute(
            "INSERT OR IGNORE INTO session (id,harness,harness_session_id,source_path,workspace,"
            "first_ts,last_ts,message_count,project_id,attribution_method,attribution_rung,"
            "attribution_confidence,enriched,crashed,pipeline_version)"
            " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,1,0,?)",
            (sid, s["harness"], s["session_id"], s["source_path"], s.get("cwd"),
             s["first_ts"], s["last_ts"], len(mine), pids[main_dossier],
             "intent-refresh-07/" + s.get("rung", ""), 1 if s.get("project") else 7,
             1.0 if s.get("project") else 0.6, PIPELINE_VERSION))
        for p in mine:
            eid = "evt_" + p["id"]
            if eid in have:
                continue
            human = 1 if p["author"] == "operator" else 0
            conn.execute(
                "INSERT INTO event (id,session_id,project_id,seq,ts,role,is_human,is_sidechain,"
                "is_meta,text,text_hash,char_len,cwd,redactions,pipeline_version)"
                " VALUES (?,?,?,?,?,'user',?,0,0,?,?,?,?,?,?)",
                (eid, sid, pids[p["dossier"]], p["seq"], p["ts"], human,
                 p["text"] if human else None, p["id"], p["chars"], p.get("cwd"),
                 ",".join(p["redactions"]) or None, PIPELINE_VERSION))
            added["human" if human else "filtered"] += 1
    conn.commit()
    log(conn, "load", "done", f"{a.run} {dict(added)}")
    print(f"loaded {added['human']} operator prompts and {added['filtered']} filtered prompts"
          f" across {len(pids)} projects")
    for d, n in Counter(p["dossier"] for p in prompts if p["author"] == "operator").most_common():
        print(f"  {n:5}  {d}  ({pids[d]})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
