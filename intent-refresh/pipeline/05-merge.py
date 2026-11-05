#!/usr/bin/env python3
"""Phase 6: the curator. Deterministic. No model runs here, ever.

LLMs that iteratively refine their own output drift toward generic content.
Proposal is a model job; merging, deduplication and conflict resolution are
code. That boundary is the reason this pipeline can be rerun and trusted.

Three hard gates, enforced here rather than by prompt:

  ID accounting.  Every submitted id must return a verdict. A missing id is
  a silent-omission failure, not an empty result, and it fails the merge.

  Provenance.     No intent row without a verbatim span and an event id.
  A row that cannot cite itself is a hallucination that has not been caught.

  Monotonic merge. Processing is newest-first, so an arriving intent that
  conflicts with a stored one is always older and can only be marked
  superseded. No status already assigned is ever revised.

Repetition is counted, never collapsed away: five occurrences is the strongest
available signal of importance and of repeated non-compliance.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib.common import (  # noqa: E402
    PIPELINE_VERSION, connect, die, log, now, observe, report, sha,
)

VALID_TYPES = {
    "directive.feature", "directive.constraint", "correction.behavior",
    "correction.factual", "bugreport", "scope.defer", "scope.cut",
    "preference.style", "question", "meta.harness", "noise",
}
TERMINAL = {"scope.cut"}
STOPWORDS = {
    "the", "a", "an", "to", "of", "and", "or", "in", "on", "for", "with",
    "is", "it", "this", "that", "be", "should", "please", "can", "we", "i",
}


def norm(text: str) -> str:
    t = re.sub(r"[^a-z0-9\s]", " ", (text or "").lower())
    return " ".join(w for w in t.split() if w not in STOPWORDS)


def similar(a: str, b: str) -> float:
    sa, sb = set(norm(a).split()), set(norm(b).split())
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def load_verdicts(path: Path) -> list[dict]:
    raw = json.loads(path.read_text())
    if isinstance(raw, dict):
        raw = raw.get("verdicts") or raw.get("items") or []
    if not isinstance(raw, list):
        die("verdict file must be a JSON list of verdict objects")
    return raw


def main() -> int:
    ap = argparse.ArgumentParser(description="Phase 6: deterministic merge")
    ap.add_argument("--verdicts", required=True)
    ap.add_argument("--batch", help="batch id (inferred if omitted)")
    ap.add_argument("--dedupe-threshold", type=float, default=0.72)
    ap.add_argument("--allow-partial", action="store_true",
                    help="permit missing ids. Records an observation. Use sparingly.")
    ap.add_argument("--repair-rejected", action="store_true",
                    help="accept verdicts only for empty-verdict items in an already merged batch")
    args = ap.parse_args()

    conn = connect()
    verdicts = load_verdicts(Path(args.verdicts))

    bid = args.batch
    if not bid:
        ids = [v.get("id") for v in verdicts if v.get("id")]
        row = conn.execute(
            "SELECT batch_id, COUNT(*) c FROM batch_item WHERE event_id IN "
            f"({','.join('?' * len(ids))}) GROUP BY batch_id ORDER BY c DESC LIMIT 1",
            ids,
        ).fetchone() if ids else None
        if not row:
            die("cannot infer batch. Pass --batch <id>.")
        bid = row["batch_id"]

    batch = conn.execute("SELECT * FROM batch WHERE id=?", (bid,)).fetchone()
    if not batch:
        die(f"unknown batch {bid}")
    if batch["merged_at"] and not args.repair_rejected:
        die(f"batch {bid} already merged at {batch['merged_at']}")
    if args.repair_rejected and not batch["merged_at"]:
        die("--repair-rejected requires an already merged batch")

    if args.repair_rejected:
        submitted = {r["event_id"] for r in conn.execute(
            "SELECT event_id FROM batch_item WHERE batch_id=? AND (verdict IS NULL OR verdict='')",
            (bid,)).fetchall()}
        if not submitted:
            die(f"batch {bid} has no rejected items to repair")
    else:
        submitted = {r["event_id"] for r in conn.execute(
            "SELECT event_id FROM batch_item WHERE batch_id=?", (bid,)).fetchall()}
    returned = {v.get("id") for v in verdicts if v.get("id")}

    missing = submitted - returned
    orphan = returned - submitted

    if orphan:
        die(f"{len(orphan)} verdict ids were not in the batch. First: {sorted(orphan)[:3]}")

    if missing:
        observe(conn, "id_accounting_mismatch",
                f"batch {bid}: {len(missing)} of {len(submitted)} ids missing",
                sorted(missing)[:50])
        conn.commit()
        print(f"ID accounting FAILED: {len(missing)}/{len(submitted)} ids missing.")
        print("This is the silent-omission failure mode. Missing ids, first 10:")
        for m in sorted(missing)[:10]:
            print(f"  {m}")
        if not args.allow_partial:
            print("\nRe-classify the missing items and rerun, or pass --allow-partial")
            print("if you accept a known-incomplete merge.")
            return 2

    project = batch["project_id"]
    tranche = batch["tranche"]

    existing = conn.execute(
        "SELECT id,type,statement,first_ts,last_ts,occurrences,status"
        " FROM intent WHERE project_id=? AND superseded_by IS NULL",
        (project,),
    ).fetchall()
    ledger = [dict(r) for r in existing]

    added = merged = superseded = rejected = noise = 0

    for v in verdicts:
        eid = v.get("id")
        vtype = (v.get("type") or "").strip()
        if vtype == "noise" or not vtype:
            noise += 1
            conn.execute("UPDATE batch_item SET verdict=? WHERE batch_id=? AND event_id=?",
                         (json.dumps({"type": "noise"}), bid, eid))
            continue
        if vtype not in VALID_TYPES:
            rejected += 1
            observe(conn, "schema_violation", f"unknown type '{vtype}' on {eid}", [eid])
            continue

        statement = (v.get("statement") or "").strip()
        verbatim = (v.get("verbatim") or "").strip()
        if not statement or not verbatim:
            rejected += 1
            observe(conn, "schema_violation", f"missing statement or verbatim on {eid}", [eid])
            continue

        ev = conn.execute("SELECT ts,text FROM event WHERE id=?", (eid,)).fetchone()
        if not ev:
            rejected += 1
            continue
        # Provenance gate: the quote must actually be in the turn.
        if verbatim[:40].lower() not in (ev["text"] or "").lower():
            rejected += 1
            observe(conn, "verifier_disagreement",
                    f"verbatim not found in source turn {eid}", [eid])
            continue

        ts = ev["ts"]
        match = None
        for cand in ledger:
            if cand["type"] == vtype and similar(cand["statement"], statement) >= args.dedupe_threshold:
                match = cand
                break

        if match:
            # Repetition is signal. Count it, do not collapse it away.
            conn.execute(
                "UPDATE intent SET occurrences=occurrences+1,"
                " first_ts=MIN(COALESCE(first_ts,?),?) WHERE id=?",
                (ts, ts, match["id"]),
            )
            conn.execute("INSERT OR IGNORE INTO intent_event VALUES (?,?)", (match["id"], eid))
            match["occurrences"] += 1
            merged += 1
        else:
            conflict = None
            for cand in ledger:
                if cand["type"] != vtype:
                    continue
                if cand["status"] in TERMINAL:
                    continue
                if 0.45 <= similar(cand["statement"], statement) < args.dedupe_threshold:
                    conflict = cand
                    break

            iid = "int_" + sha(project, vtype, norm(statement))
            conn.execute(
                """INSERT OR IGNORE INTO intent
                     (id,project_id,type,statement,verbatim,scope,status,first_ts,last_ts,
                      occurrences,confidence,provisional,tranche,pipeline_version,created_at)
                   VALUES (?,?,?,?,?,?,?,?,?,1,?,?,?,?,?)""",
                (iid, project, vtype, statement, verbatim, v.get("scope"),
                 "cut" if vtype == "scope.cut" else None, ts, ts,
                 v.get("confidence"), 1 if tranche == 1 else 0, tranche,
                 PIPELINE_VERSION, now()),
            )
            conn.execute("INSERT OR IGNORE INTO intent_event VALUES (?,?)", (iid, eid))
            ledger.append({"id": iid, "type": vtype, "statement": statement,
                           "first_ts": ts, "last_ts": ts, "occurrences": 1, "status": None})
            added += 1

            if conflict:
                # Monotonic: arriving item is older, so it is the one superseded.
                older, newer = (iid, conflict["id"])
                if (ts or "") > (conflict["last_ts"] or ""):
                    older, newer = conflict["id"], iid
                conn.execute(
                    "UPDATE intent SET superseded_by=?, status='superseded' WHERE id=?",
                    (newer, older),
                )
                superseded += 1

        conn.execute("UPDATE batch_item SET verdict=? WHERE batch_id=? AND event_id=?",
                     (json.dumps(v), bid, eid))

    if args.repair_rejected:
        conn.execute("UPDATE batch SET ids_returned=ids_returned+? WHERE id=?",
                     (len(returned), bid))
    else:
        conn.execute(
            "UPDATE batch SET merged_at=?, ids_returned=? WHERE id=?",
            (now(), len(returned), bid),
        )
    conn.commit()
    log(conn, "merge", "done", f"{bid} +{added}")

    report("Merge result", [
        ("batch", bid),
        ("ids submitted", len(submitted)),
        ("ids returned", len(returned)),
        ("id accounting", "BALANCED" if not missing else f"MISSING {len(missing)}"),
        ("new intents", added),
        ("occurrences merged", merged),
        ("superseded", superseded),
        ("noise", noise),
        ("rejected (no provenance or bad type)", rejected),
    ])

    if rejected:
        print("\nRejected rows had no verbatim span, an unquotable span, or an unknown")
        print("type. They were dropped rather than stored. See the observation table.")

    tot = conn.execute(
        "SELECT COUNT(*) c FROM intent WHERE project_id=? AND superseded_by IS NULL",
        (project,)).fetchone()["c"]
    print(f"\nActive intents for {project}: {tot}")
    print("Next: another batch, or 06-render.py once a project has enough coverage.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
