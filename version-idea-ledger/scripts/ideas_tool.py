#!/usr/bin/env python3
"""Merge reader output into the idea ledger, and suggest cross-version duplicates.

Usage:
  python3 -I -B ideas_tool.py merge --ledger DOSSIER/ledgers/idea-ledger.jsonl ideas-<slice>.jsonl ...
  python3 -I -B ideas_tool.py dupes --ledger DOSSIER/ledgers/idea-ledger.jsonl [--threshold 0.5] [--out pairs.jsonl]
  python3 -I -B ideas_tool.py set --ledger DOSSIER/ledgers/idea-ledger.jsonl --id ID key=value [key=value ...]

merge: rows are keyed by id; a row in a later file replaces the earlier one, and rows already in
the ledger that no file mentions are kept, so a rerun only adds or revises. Each row gets a
`date` if it has none.
dupes: pairs of ideas from different sources whose content words overlap (Jaccard over stemmed
words, stop words removed) at or above the threshold, best first. These are candidates: the
coordinator decides, then sets category duplicate and duplicate_of on the weaker row.
set: change fields of one row (for example after an idea is incorporated:
category=implemented where=path:line note="incorporated in commit abc1234").
"""
import argparse
import datetime as dt
import json
import os
import re
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import read_jsonl, write_jsonl  # noqa: E402

STOP = set("a an the of to in on for and or with by from is are be as at it its this that each every "
           "when than then into only not no one per all any can use used uses using".split())


def words(text):
    out = set()
    for w in re.findall(r"[a-z0-9]+", (text or "").lower()):
        if w in STOP or len(w) < 3:
            continue
        for suf in ("ing", "ed", "es", "s"):
            if w.endswith(suf) and len(w) - len(suf) >= 3:
                w = w[: -len(suf)]
                break
        out.add(w)
    return out


def cmd_merge(a):
    rows = {r["id"]: r for r in read_jsonl(a.ledger)}
    order = list(rows)
    today = dt.date.today().isoformat()
    for f in a.files:
        for r in read_jsonl(f):
            r.setdefault("date", today)
            if r["id"] not in rows:
                order.append(r["id"])
            rows[r["id"]] = r
    write_jsonl(a.ledger, [rows[i] for i in order])
    print(f"{len(order)} ideas in {a.ledger}")


def cmd_dupes(a):
    rows = [r for r in read_jsonl(a.ledger) if r.get("category") != "duplicate"]
    ws = [words(r.get("idea")) for r in rows]
    pairs = []
    for i in range(len(rows)):
        for j in range(i + 1, len(rows)):
            if rows[i].get("source") == rows[j].get("source") or not ws[i] or not ws[j]:
                continue
            s = len(ws[i] & ws[j]) / len(ws[i] | ws[j])
            if s >= a.threshold:
                pairs.append({"score": round(s, 3), "a": rows[i]["id"], "b": rows[j]["id"],
                              "a_idea": rows[i].get("idea"), "b_idea": rows[j].get("idea")})
    pairs.sort(key=lambda p: -p["score"])
    if a.out:
        write_jsonl(a.out, pairs)
    for p in pairs[: a.show]:
        print(f"{p['score']:.2f} {p['a']} | {p['b']}\n   {p['a_idea'][:110]}\n   {p['b_idea'][:110]}")
    print(f"{len(pairs)} candidate pairs at threshold {a.threshold}")


def cmd_set(a):
    rows = read_jsonl(a.ledger)
    hit = [r for r in rows if r.get("id") == a.id]
    if not hit:
        raise SystemExit(f"no idea {a.id}")
    for kv in a.pairs:
        k, _, v = kv.partition("=")
        if v == "":
            hit[0].pop(k, None)
        else:
            hit[0][k] = v
    write_jsonl(a.ledger, rows)
    print(json.dumps(hit[0], ensure_ascii=False, sort_keys=True))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("merge")
    m.add_argument("--ledger", required=True)
    m.add_argument("files", nargs="+")
    d = sub.add_parser("dupes")
    d.add_argument("--ledger", required=True)
    d.add_argument("--threshold", type=float, default=0.5)
    d.add_argument("--out")
    d.add_argument("--show", type=int, default=40)
    s = sub.add_parser("set")
    s.add_argument("--ledger", required=True)
    s.add_argument("--id", required=True)
    s.add_argument("pairs", nargs="+")
    a = ap.parse_args()
    {"merge": cmd_merge, "dupes": cmd_dupes, "set": cmd_set}[a.cmd](a)


if __name__ == "__main__":
    main()
