#!/usr/bin/env python3
"""Phase 3: read raw session records and materialize the event schema.

cass gives retrieval. It does not preserve the fields this audit needs.
This phase joins back to the raw file for the ones that decide correctness:

  isSidechain   agent-authored prompts to subagents. Not the user.
  isMeta        injected system content.
  gitBranch     spec-kit feature key.
  parentUuid    the conversation is a DAG, not a list.
  tool paths    the evidence layer.
  slash cmds    how spec invocations are found.

is_human is computed here and stored. It is never inferred at query time,
so a later correction to the rule is a visible recomputation rather than a
silent change in results.

Secrets are redacted before storage. Payloads are dropped to length only.
Resumable: sessions already enriched are skipped unless --force.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib.common import (  # noqa: E402
    PIPELINE_VERSION, SLASH_ARGS_RE, SLASH_RE, connect, extract_text,
    is_approval, iter_jsonl, log, observe, redact, report, sha,
)

MAX_TEXT = 20000  # store enough to classify; drop pasted-dump tails


def role_of(obj: dict) -> str:
    t = (obj.get("type") or "").lower()
    if t in ("user", "assistant", "system", "tool"):
        return t
    msg = obj.get("message")
    if isinstance(msg, dict) and msg.get("role"):
        return str(msg["role"]).lower()
    if obj.get("role"):
        return str(obj["role"]).lower()
    return "other"


def tool_info(obj: dict) -> tuple[str | None, list[str]]:
    name = None
    paths: list[str] = []
    msg = obj.get("message")
    content = msg.get("content") if isinstance(msg, dict) else None
    if isinstance(content, list):
        for block in content:
            if isinstance(block, dict) and block.get("type") == "tool_use":
                name = block.get("name") or name
                inp = block.get("input")
                if isinstance(inp, dict):
                    for key in ("file_path", "path", "notebook_path", "filePath"):
                        v = inp.get(key)
                        if isinstance(v, str) and v.startswith("/"):
                            paths.append(v)
    tur = obj.get("toolUseResult")
    if isinstance(tur, dict):
        for key in ("filePath", "file_path", "path"):
            v = tur.get(key)
            if isinstance(v, str) and v.startswith("/"):
                paths.append(v)
    return name, sorted(set(paths))[:20]


def compute_is_human(obj: dict, role: str, text: str) -> int:
    """The single most important derived boolean in the schema."""
    if role != "user":
        return 0
    if obj.get("isSidechain") is True:
        return 0          # agent talking to a subagent
    if obj.get("isMeta") is True:
        return 0
    ut = obj.get("userType")
    if ut is not None and str(ut).lower() != "external":
        return 0
    if not text or not text.strip():
        return 0
    if text.lstrip().startswith("<") and "system-reminder" in text[:200].lower():
        return 0
    return 1


def enrich_session(conn, row) -> tuple[int, int, int]:
    path = Path(row["source_path"])
    if not path.is_file():
        return 0, 0, 0

    sid = row["id"]
    pid = row["project_id"]
    conn.execute("DELETE FROM event WHERE session_id=?", (sid,))

    seen_hashes: set[str] = set()
    n_events = n_human = n_dupe = 0
    last_type = None

    for seq, obj in iter_jsonl(path):
        role = role_of(obj)
        raw_text = extract_text(obj.get("message") or obj.get("content") or obj.get("text"))
        text = raw_text[:MAX_TEXT]
        is_human = compute_is_human(obj, role, text)

        if is_human and is_approval(text):
            is_human = 0  # counted below, not stored as intent-bearing

        slash = slash_args = None
        if text:
            m = SLASH_RE.search(text)
            if m:
                slash = m.group(1).strip()
                a = SLASH_ARGS_RE.search(text)
                slash_args = a.group(1).strip() if a else None

        # Replay dedupe: identical human text at the same DAG position is a
        # resumed-session replay, not a second instruction.
        th = sha(text, str(obj.get("parentUuid") or ""), n=16) if text else None
        if is_human and th:
            if th in seen_hashes:
                n_dupe += 1
                continue
            seen_hashes.add(th)

        clean, hits = redact(text) if text else ("", [])
        tname, paths = tool_info(obj)

        eid = "evt_" + sha(sid, str(obj.get("uuid") or seq), str(seq))
        conn.execute(
            """INSERT OR REPLACE INTO event (id,session_id,project_id,parent_event_id,seq,ts,
                 role,is_human,is_sidechain,is_meta,text,text_hash,char_len,cwd,git_branch,
                 tool_name,paths_touched,slash_command,slash_args,redactions,pipeline_version)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (eid, sid, pid, obj.get("parentUuid"), seq,
             obj.get("timestamp") or obj.get("ts"), role, is_human,
             1 if obj.get("isSidechain") else 0, 1 if obj.get("isMeta") else 0,
             clean if (is_human or slash) else None,   # payloads dropped
             th, len(raw_text) if raw_text else 0,
             obj.get("cwd"), obj.get("gitBranch"), tname,
             json.dumps(paths) if paths else None, slash, slash_args,
             json.dumps(hits) if hits else None, PIPELINE_VERSION),
        )
        n_events += 1
        n_human += is_human
        last_type = role

    crashed = 1 if last_type in ("tool", "assistant") else 0
    conn.execute(
        "UPDATE session SET enriched=1, message_count=?, crashed=? WHERE id=?",
        (n_events, crashed, sid),
    )
    return n_events, n_human, n_dupe


def main() -> int:
    ap = argparse.ArgumentParser(description="Phase 3: enrich sessions into events")
    ap.add_argument("--project", help="limit to one project slug")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--force", action="store_true", help="re-enrich already-done sessions")
    args = ap.parse_args()

    conn = connect()
    log(conn, "enrich", "start")

    q = "SELECT id,source_path,project_id FROM session WHERE 1=1"
    params: list = []
    if not args.force:
        q += " AND enriched=0"
    if args.project:
        q += " AND project_id=?"
        params.append(args.project)
    q += " ORDER BY last_ts DESC"   # newest first, per the ordering rule
    if args.limit:
        q += f" LIMIT {int(args.limit)}"

    rows = conn.execute(q, params).fetchall()
    print(f"Enriching {len(rows)} sessions (newest first)")

    tot_e = tot_h = tot_d = 0
    for i, row in enumerate(rows, 1):
        e, h, d = enrich_session(conn, row)
        tot_e += e
        tot_h += h
        tot_d += d
        if i % 25 == 0:
            conn.commit()
            print(f"  {i}/{len(rows)} sessions, {tot_e} events, {tot_h} human turns")
    conn.commit()

    stats = conn.execute(
        "SELECT COUNT(*) events, SUM(is_human) human,"
        " SUM(CASE WHEN redactions IS NOT NULL THEN 1 ELSE 0 END) redacted,"
        " SUM(CASE WHEN is_sidechain=1 THEN 1 ELSE 0 END) sidechain,"
        " SUM(CASE WHEN slash_command IS NOT NULL THEN 1 ELSE 0 END) slash"
        " FROM event"
    ).fetchone()

    report("Corpus", [
        ("events", stats["events"] or 0),
        ("human turns", stats["human"] or 0),
        ("human ratio", f"{100.0*(stats['human'] or 0)/(stats['events'] or 1):.1f}%"),
        ("sidechain excluded", stats["sidechain"] or 0),
        ("replays deduped", tot_d),
        ("events with redactions", stats["redacted"] or 0),
        ("slash commands found", stats["slash"] or 0),
    ])

    crashed = conn.execute("SELECT COUNT(*) c FROM session WHERE crashed=1").fetchone()["c"]
    print(f"\nCrash-terminated sessions: {crashed}")
    print("These are labelled incompleteness. 04-batch.py upweights them.")

    if (stats["sidechain"] or 0) == 0 and (stats["events"] or 0) > 500:
        observe(conn, "schema_violation",
                "no sidechain turns found in a large corpus; verify the field exists")
        conn.commit()
        print("\nWarning: zero sidechain turns in a large corpus. Verify the field is")
        print("present in your harness logs before trusting the human-turn count.")

    log(conn, "enrich", "done", f"{tot_e} events")
    print("\nExit criterion: rerun this and confirm the event count is stable.")
    print("Next: 04-batch.py --project <slug>")
    return 0


if __name__ == "__main__":
    sys.exit(main())
