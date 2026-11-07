#!/usr/bin/env python3
"""Archive gate: refuse while a unique clause lacks a recorded destination (DA-034).

Usage:
  python3 -I gate.py --ledger ledger.json --folder FOLDER [--destinations dest.json]
                     [--allow-missing-destination-files] [--out gate.json]

Refuses (exit 1, "REFUSED") when any of these hold:
  - a clause in the ledger is not marked exactly one of covered, partial, unique;
  - a source file in the ledger is missing or its bytes changed since the
    comparison (stale ledger);
  - the folder holds a clause the ledger does not mark (a fresh extraction of
    every Markdown file in FOLDER is checked against the ledger, so comparing
    only part of the folder is caught);
  - the ledger has no clause at all for a folder that holds Markdown clauses;
  - a clause marked unique has no recorded destination;
  - a destination that is a local path (starts with /, ~ or ./) does not
    exist, unless --allow-missing-destination-files is given.
Destinations come from the ledger and from --destinations (which wins).
Writes gate.json (schema lineage-gate/1) for project-archive's mine step.
Exit 0 and "PASS" when archiving may proceed.
"""
import argparse
import hashlib
import json
import os
import sys
import datetime as dt

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import extract_clauses as X  # noqa: E402

MARKS = ("covered", "partial", "unique")


def sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def is_local_path(d):
    return isinstance(d, str) and d.startswith(("/", "~", "./", "../"))


def ident(abspath, rel, key):
    return (abspath, key[len(rel):] if key.startswith(rel) else key)


def gate(ledger, folder, destinations=None, allow_missing=False):
    destinations = destinations or {}
    folder = os.path.realpath(os.path.expanduser(folder))
    refusals = []
    rel2abs = {}
    for f in ledger.get("source_files", []):
        ap = f.get("abspath")
        rel2abs[f["path"]] = ap
        if not ap or not os.path.isfile(ap):
            refusals.append({"key": f["path"], "reason": "source file in the ledger is missing"})
        elif sha(ap) != f["sha256"]:
            refusals.append({"key": f["path"], "reason": "source file changed since the comparison; re-run compare.py"})
    marked = {}
    for c in ledger.get("clauses", []):
        if c.get("mark") not in MARKS:
            refusals.append({"key": c.get("key"), "reason": "clause is not marked covered, partial or unique (mark %r)" % c.get("mark")})
        ap = rel2abs.get(c["file"])
        if ap:
            marked[ident(os.path.realpath(ap), c["file"], c["key"])] = c
    fresh = X.extract_paths([folder], base=folder)
    unmarked = []
    for c in fresh["clauses"]:
        ap = os.path.realpath(os.path.join(folder, c["file"]))
        if ident(ap, c["file"], c["key"]) not in marked:
            unmarked.append(c)
    for c in unmarked:
        refusals.append({"key": c["key"], "text": c["text"][:200], "reason": "clause in the folder is not in the ledger (not compared)"})
    if fresh["clauses"] and not ledger.get("clauses"):
        refusals.append({"key": folder, "reason": "no clause-level comparison for a folder that holds clauses"})
    unique_without = 0
    rows = []
    for c in ledger.get("clauses", []):
        dest = destinations.get(c["key"]) or (destinations.get(c.get("id")) if c.get("id") else None) or c.get("destination")
        row = {"key": c["key"], "id": c.get("id"), "mark": c.get("mark"), "destination": dest, "text": c["text"][:300]}
        if c.get("mark") == "unique":
            if not dest:
                unique_without += 1
                refusals.append({"key": c["key"], "text": c["text"][:200], "reason": "unique clause has no recorded destination"})
            elif is_local_path(dest) and not allow_missing:
                p = os.path.expanduser(dest.split("#", 1)[0])
                if not os.path.exists(p):
                    refusals.append({"key": c["key"], "text": c["text"][:200], "reason": "recorded destination %s does not exist yet" % dest})
        rows.append(row)
    counts = {m: sum(1 for r in rows if r["mark"] == m) for m in MARKS}
    return {"schema": "lineage-gate/1", "folder": folder, "allowed": not refusals,
            "counts": counts, "clauses_total": len(rows), "unique_without_destination": unique_without,
            "refusals": refusals, "clauses": rows,
            "checked_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--folder", required=True)
    ap.add_argument("--destinations")
    ap.add_argument("--allow-missing-destination-files", action="store_true")
    ap.add_argument("--out")
    a = ap.parse_args()
    ledger = json.load(open(a.ledger, encoding="utf-8"))
    dest = json.load(open(a.destinations, encoding="utf-8")) if a.destinations else {}
    res = gate(ledger, a.folder, dest, a.allow_missing_destination_files)
    res["ledger"] = os.path.abspath(a.ledger)
    res["ledger_sha256"] = sha(a.ledger)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as fh:
            json.dump(res, fh, indent=1, ensure_ascii=False)
            fh.write("\n")
    c = res["counts"]
    if res["allowed"]:
        print("PASS: %s may be archived (covered %d, partial %d, unique %d, all unique clauses have destinations)" % (res["folder"], c["covered"], c["partial"], c["unique"]))
        sys.exit(0)
    print("REFUSED: %s must not be archived (%d problem(s); %d unique clause(s) without a destination)" % (res["folder"], len(res["refusals"]), res["unique_without_destination"]))
    for r in res["refusals"]:
        print("  - %s: %s%s" % (r["key"], r["reason"], (" | " + r["text"]) if r.get("text") else ""))
    sys.exit(1)


if __name__ == "__main__":
    main()
