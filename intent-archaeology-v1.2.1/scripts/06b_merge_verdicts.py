#!/usr/bin/env python3
"""Phase 6b: merge classification verdicts. Deterministic. No model runs here.

Three gates, enforced in code rather than by prompt, because a prompt-enforced
rule is a suggestion:

  ID accounting. Every id sent out in a batch must come back with a verdict.
  A missing id means the model silently skipped material, which is the failure
  mode you would never otherwise notice, because the output looks complete.
  Missing ids fail the merge unless you pass --allow-partial.

  Provenance. No intent is stored without a verbatim span that actually appears
  in its source prompt, checked by substring match. A row that cannot cite
  itself is a hallucination that has not been caught yet.

  Monotonic supersession. Prompts are processed newest-first, so any arriving
  intent that conflicts with a stored one is necessarily older and can only be
  marked superseded. No judgment already recorded is ever revised by later
  processing, which is what makes a partial run correct rather than misleading.

Repetition is counted, never collapsed. Five occurrences of one instruction is
the strongest available signal both that it mattered and that it kept being
ignored, and that signal is destroyed by deduplicating to a single row.

Usage:
    python scripts/06b_merge_verdicts.py --db ~/.intent-archaeology/state.db \\
        --verdicts ~/.intent-archaeology/verdicts/
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from pathlib import Path

# Jaccard overlap on content words, above which two intents of the same type are
# treated as one restatement rather than two intents. 0.72 was chosen so that
# "add rate limiting to /auth" and "add rate limiting on the auth endpoint"
# merge, while "add rate limiting" and "add request logging" do not. Raise it if
# distinct intents are collapsing; lower it if one instruction keeps appearing as
# several rows.
DEDUPE_THRESHOLD = 0.72

# Below 0.45 two statements share too little to concern the same obligation.
# Between 0.45 and the dedupe threshold they concern the same thing but say
# something different about it, which is what supersession means.
CONFLICT_FLOOR = 0.45

# Verbatim spans are matched on their first 40 characters. Long enough to be
# specific, short enough to survive whitespace normalization by the model.
QUOTE_MATCH_CHARS = 40

STOPWORDS = {"the", "a", "an", "to", "of", "and", "or", "in", "on", "for", "with",
             "is", "it", "this", "that", "be", "should", "please", "can", "we", "i"}

TERMINAL_TYPES = {"scope-cut", "scope.cut", "abandoned"}


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
        raise ValueError(f"{path}: expected a JSON list of verdict objects")
    return raw


def load_valid_types(skill_root: Path) -> set[str] | None:
    """Read the closed vocabulary from the taxonomy reference if present."""
    ref = skill_root / "references" / "intent_taxonomy.md"
    if not ref.exists():
        return None
    found = set(re.findall(r"`([a-z]+[a-z.\-]*)`", ref.read_text()))
    found = {f for f in found if "-" in f or "." in f or f in
             {"command", "constraint", "correction", "question", "noise", "bugreport"}}
    found.add("noise")
    return found or None


def columns(conn: sqlite3.Connection, table: str) -> set[str]:
    return {r[1] for r in conn.execute(f"PRAGMA table_info({table})")}


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--db", required=True)
    ap.add_argument("--verdicts", required=True,
                    help="a verdict JSON file, or a directory of them")
    ap.add_argument("--batches", default="~/.intent-archaeology/batches",
                    help="directory holding the emitted batch files")
    ap.add_argument("--allow-partial", action="store_true",
                    help="permit missing ids. Records an observation. Use sparingly.")
    args = ap.parse_args()

    skill_root = Path(__file__).resolve().parent.parent
    db = Path(args.db).expanduser()
    if not db.exists():
        print(f"ERROR: no state database at {db}", file=sys.stderr)
        return 1

    vpath = Path(args.verdicts).expanduser()
    vfiles = sorted(vpath.glob("*.json")) if vpath.is_dir() else [vpath]
    if not vfiles:
        print(f"ERROR: no verdict files at {vpath}", file=sys.stderr)
        return 1

    bdir = Path(args.batches).expanduser()
    batch_ids: dict[int, set[int]] = {}
    for bf in bdir.glob("*.json") if bdir.is_dir() else []:
        try:
            b = json.loads(bf.read_text())
            batch_ids[bf.stem] = {i["id"] for i in b.get("items", [])}
        except (json.JSONDecodeError, KeyError, TypeError):
            continue

    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row

    # The provenance gate is worthless if the quote it validated is then thrown
    # away, so the columns that hold it are added if the schema predates them.
    # Idempotent: an existing column makes the ALTER a no-op we swallow.
    for col, decl in (("verbatim", "TEXT"), ("occurrences", "INTEGER DEFAULT 1")):
        if col not in columns(conn, "intents"):
            try:
                conn.execute(f"ALTER TABLE intents ADD COLUMN {col} {decl}")
                conn.commit()
            except sqlite3.OperationalError:
                pass
    icols = columns(conn, "intents")
    has_verbatim = "verbatim" in icols
    has_occ = "occurrences" in icols
    valid_types = load_valid_types(skill_root)

    totals = {"added": 0, "repeat": 0, "superseded": 0, "noise": 0, "rejected": 0}
    all_missing: set[int] = set()

    for vf in vfiles:
        try:
            verdicts = load_verdicts(vf)
        except (json.JSONDecodeError, ValueError) as exc:
            print(f"SKIP {vf.name}: {exc}", file=sys.stderr)
            continue

        returned = {v.get("id") for v in verdicts if v.get("id") is not None}
        submitted = set()
        for bid, ids in batch_ids.items():
            if returned & ids:
                submitted |= ids
        missing = submitted - returned if submitted else set()
        orphan = returned - submitted if submitted else set()

        if orphan:
            print(f"ERROR {vf.name}: {len(orphan)} verdict ids were not in any batch. "
                  f"First: {sorted(orphan)[:3]}", file=sys.stderr)
            return 2
        if missing:
            all_missing |= missing
            conn.execute(
                "INSERT INTO observations (kind, detail) VALUES (?,?)",
                ("id_accounting_mismatch",
                 f"{vf.name}: {len(missing)} of {len(submitted)} ids missing"),
            ) if "observations" in {r[0] for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'")} else None
            print(f"ID accounting FAILED for {vf.name}: {len(missing)}/{len(submitted)} "
                  f"ids missing. First 10: {sorted(missing)[:10]}", file=sys.stderr)
            if not args.allow_partial:
                print("Re-classify the missing items and rerun, or pass "
                      "--allow-partial to accept a known-incomplete merge.",
                      file=sys.stderr)
                return 2

        for v in verdicts:
            pid = v.get("id")
            vtype = (v.get("type") or "").strip()
            if not pid or not vtype or vtype == "noise":
                totals["noise"] += 1
                continue
            if valid_types and vtype not in valid_types:
                totals["rejected"] += 1
                print(f"  reject: unknown type '{vtype}' on prompt {pid}", file=sys.stderr)
                continue

            summary = (v.get("summary") or v.get("statement") or "").strip()
            verbatim = (v.get("verbatim") or "").strip()
            if not summary or not verbatim:
                totals["rejected"] += 1
                print(f"  reject: missing summary or verbatim on prompt {pid}",
                      file=sys.stderr)
                continue

            row = conn.execute(
                "SELECT id, tranche_id, project_id, prompt_text FROM prompts WHERE id=?",
                (pid,)).fetchone()
            if not row:
                totals["rejected"] += 1
                continue

            probe = verbatim[:QUOTE_MATCH_CHARS].lower()
            if probe not in (row["prompt_text"] or "").lower():
                totals["rejected"] += 1
                print(f"  reject: verbatim not found in prompt {pid}", file=sys.stderr)
                continue

            existing = [dict(r) for r in conn.execute(
                "SELECT id, type, summary, superseded_by FROM intents "
                "WHERE project_id=? AND superseded_by IS NULL AND type=?",
                (row["project_id"], vtype)).fetchall()]

            match = next((e for e in existing
                          if similar(e["summary"], summary) >= DEDUPE_THRESHOLD), None)
            if match:
                if has_occ:
                    conn.execute(
                        "UPDATE intents SET occurrences=COALESCE(occurrences,1)+1 "
                        "WHERE id=?", (match["id"],))
                totals["repeat"] += 1
                continue

            fields = ["prompt_id", "tranche_id", "project_id", "type", "summary",
                      "superseded_by", "taxonomy_version"]
            values = [pid, row["tranche_id"], row["project_id"], vtype, summary,
                      None, "1.0"]
            if has_verbatim:
                fields.append("verbatim")
                values.append(verbatim)
            cur = conn.execute(
                f"INSERT INTO intents ({','.join(fields)}) "
                f"VALUES ({','.join('?' * len(fields))})", values)
            new_id = cur.lastrowid
            totals["added"] += 1

            if vtype not in TERMINAL_TYPES:
                conflict = next(
                    (e for e in existing
                     if CONFLICT_FLOOR <= similar(e["summary"], summary) < DEDUPE_THRESHOLD),
                    None)
                if conflict:
                    # Newest-first: the arriving intent is older, so it is superseded.
                    conn.execute("UPDATE intents SET superseded_by=? WHERE id=?",
                                 (conflict["id"], new_id))
                    totals["superseded"] += 1

        conn.commit()
        print(f"merged {vf.name}", file=sys.stderr)

    print("\n--- merge result ---", file=sys.stderr)
    print(f"  id accounting        {'BALANCED' if not all_missing else f'MISSING {len(all_missing)}'}",
          file=sys.stderr)
    print(f"  new intents          {totals['added']}", file=sys.stderr)
    print(f"  repeats counted      {totals['repeat']}", file=sys.stderr)
    print(f"  superseded           {totals['superseded']}", file=sys.stderr)
    print(f"  noise                {totals['noise']}", file=sys.stderr)
    print(f"  rejected             {totals['rejected']}", file=sys.stderr)
    if totals["rejected"]:
        print("\nRejected rows lacked a summary, lacked a verbatim span, quoted text "
              "that is not in the source prompt, or used a type outside the closed "
              "vocabulary. They were dropped rather than stored.", file=sys.stderr)
    print("\nNext: python scripts/07_three_way_join.py --db " + args.db, file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
