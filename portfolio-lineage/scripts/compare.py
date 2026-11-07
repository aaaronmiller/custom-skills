#!/usr/bin/env python3
"""Mark every clause of a folder covered, partial or unique against candidate successors (DA-034).

Usage:
  python3 -I compare.py --source FOLDER_OR_FILE [...] --successor PATH [PATH ...]
                        [--destinations dest.json] [--overrides overrides.json]
                        --out ledger.json [--md ledger.md]

--source and --successor take Markdown files, folders, or clauses.json files
written by extract_clauses.py. Each source clause is compared with every
successor clause and every successor paragraph:

  covered  the best match restates it: same normalized text, or a score of at
           least 0.80 with every precision token present (numbers, `code`,
           CAPITALISED terms, identifiers);
  partial  the best match states the behaviour (score at least 0.45) but is
           missing a precision token or scores below 0.80; the missing tokens
           are listed;
  unique   nothing in the successors scores 0.45 or more.

These words follow the 2026-11-03 lineage comparison (durable-agent-attempts.md
line 22): COVERED means the successor states it with equal or stronger force;
PARTIAL means it states the behaviour but omits a precision, number or edge case.

The score is mechanical: 0.6 x share of the clause's words found in the match,
plus 0.2 x Jaccard, plus 0.2 x sequence ratio, after removing cross-reference
tags ([EVAL-001], SPEC-012) and simple word endings. It is a first pass, not a
fidelity judgement, and it errs toward unique: see references/clause-comparison.md. A reviewer records judgements in overrides.json
({"<clause key or id>": {"mark": "covered|partial|unique", "reason": "...", "by": "..."}});
the ledger keeps the mechanical mark beside the override.

destinations.json maps a clause key or id to where its content now lives
(a file path, a register row, a task). The gate (gate.py) refuses archiving
while a unique clause has none.
"""
import argparse
import difflib
import json
import os
import re
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import extract_clauses as X  # noqa: E402

COVER, PARTIAL = 0.80, 0.45
MARKS = ("covered", "partial", "unique")
STOP = set("""a an the and or of to in on for by with as at is are be been it its this that these those
from into than then so such not no any all each every one when while if where which who whose shall must
should may will can only also more most other same per via""".split())
KEYWORDS = {"SHALL", "MUST", "NOT", "WHEN", "WHILE", "IF", "THEN", "THE", "WHERE", "AND", "OR", "SHOULD",
            "MAY", "BEFORE", "AFTER", "REQUIRED", "A", "AN", "IN", "OF", "TO"}


def load(paths):
    out = {"files": [], "clauses": [], "paragraphs": []}
    plain = []
    for p in paths:
        if p.endswith(".json"):
            d = json.load(open(p, encoding="utf-8"))
            for k in out:
                out[k] += d.get(k, [])
        else:
            plain.append(p)
    if plain:
        d = X.extract_paths(plain)
        for k in out:
            out[k] += d.get(k, [])
    return out


REF_RE = re.compile(r"\[?\b(?:[A-Z][A-Z0-9]{0,11}-\d{1,4}[a-z]?)\b\]?")


def clean(text):
    """Drop cross-reference tags such as [EVAL-001] or SPEC-012: they name clauses, they do not state them."""
    return REF_RE.sub(" ", text)


def stem(w):
    for suf in ("ing", "ed", "es", "s"):
        if w.endswith(suf) and len(w) - len(suf) >= 4:
            return w[: -len(suf)]
    return w


def words(text):
    return [stem(w) for w in re.findall(r"[a-z0-9]+(?:[._-][a-z0-9]+)*", clean(text).lower()) if w not in STOP and len(w) > 1]


def precision_tokens(text):
    text = clean(text)
    toks = set()
    toks.update(re.findall(r"\b\d+(?:\.\d+)?%?", text))
    toks.update(t.lower() for t in re.findall(r"`([^`]+)`", text))
    toks.update(t.lower() for t in re.findall(r"\b[A-Z][A-Z0-9_]{1,}\b", text) if t not in KEYWORDS)
    toks.update(t.lower() for t in re.findall(r"\b[a-z0-9]+(?:[_.][a-z0-9]+)+\b", text, re.I))
    return toks


def present(tok, text):
    return tok in text.lower()


def score(a_words, a_norm, b_text):
    b_words = words(b_text)
    if not a_words or not b_words:
        return 0.0
    A, B = set(a_words), set(b_words)
    cont = len(A & B) / len(A)
    jac = len(A & B) / len(A | B)
    seq = difflib.SequenceMatcher(None, a_norm, " ".join(b_words), autojunk=False).ratio()
    return round(0.6 * cont + 0.2 * jac + 0.2 * seq, 4)


def lookup(table, c):
    for k in (c["key"], c.get("id")):
        if k and k in table:
            return table[k]
    return None


def compare(source, successor, destinations=None, overrides=None):
    destinations = destinations or {}
    overrides = overrides or {}
    cands = [("clause", s) for s in successor["clauses"]] + [("paragraph", p) for p in successor["paragraphs"]]
    rows = []
    for c in source["clauses"]:
        aw = words(c["text"])
        an = " ".join(aw)
        best, best_s = None, 0.0
        for kind, s in cands:
            if s.get("norm_sha") and s["norm_sha"] == c.get("norm_sha") and c["text"]:
                best, best_s = (kind, s), 1.0
                break
            sc = score(aw, an, s["text"])
            if sc > best_s:
                best, best_s = (kind, s), sc
        prec = precision_tokens(c["text"])
        missing = sorted(t for t in prec if not best or not present(t, best[1]["text"]))
        if best_s >= 1.0 or (best_s >= COVER and not missing):
            mark = "covered"
        elif best_s >= PARTIAL:
            mark = "partial"
        else:
            mark = "unique"
        row = {"key": c["key"], "id": c.get("id"), "kind": c["kind"], "file": c["file"], "line": c["line"],
               "text": c["text"], "mark": mark, "mechanical_mark": mark, "score": best_s, "basis": "mechanical",
               "missing_precision": missing if mark != "unique" else [],
               "match": None if not best or mark == "unique" else {
                   "kind": best[0], "file": best[1]["file"], "line": best[1]["line"],
                   "key": best[1].get("key"), "text": best[1]["text"][:300]}}
        ov = lookup(overrides, c)
        if ov:
            if ov.get("mark") not in MARKS:
                raise SystemExit("override for %s has mark %r; use covered, partial or unique" % (c["key"], ov.get("mark")))
            row.update({"mark": ov["mark"], "basis": "override", "override_reason": ov.get("reason"), "override_by": ov.get("by")})
        dest = lookup(destinations, c)
        if dest:
            row["destination"] = dest
        rows.append(row)
    counts = {m: sum(1 for r in rows if r["mark"] == m) for m in MARKS}
    return {"schema": "clause-ledger/1", "source_files": [{"path": f["path"], "abspath": f.get("abspath"), "sha256": f["sha256"]} for f in source["files"]],
            "successor_files": [{"path": f["path"], "abspath": f.get("abspath"), "sha256": f["sha256"]} for f in successor["files"]],
            "thresholds": {"covered": COVER, "partial": PARTIAL}, "counts": counts, "clauses": rows}


def to_md(ledger):
    out = ["# Clause ledger", "", "Counts: covered %(covered)d, partial %(partial)d, unique %(unique)d." % ledger["counts"], "",
           "| Clause | Mark | Score | Basis | Best match | Missing precision | Destination |", "|---|---|---|---|---|---|---|"]
    for r in ledger["clauses"]:
        m = "%s:%s" % (r["match"]["file"], r["match"]["line"]) if r["match"] else ""
        out.append("| %s (%s:%d) | %s | %.2f | %s | %s | %s | %s |" % (
            r["id"] or r["key"], r["file"], r["line"], r["mark"], r["score"], r["basis"], m,
            ", ".join(r["missing_precision"]), r.get("destination", "")))
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", nargs="+", required=True)
    ap.add_argument("--successor", nargs="+", required=True)
    ap.add_argument("--destinations")
    ap.add_argument("--overrides")
    ap.add_argument("--out", required=True)
    ap.add_argument("--md")
    a = ap.parse_args()
    dest = json.load(open(a.destinations, encoding="utf-8")) if a.destinations else {}
    ov = json.load(open(a.overrides, encoding="utf-8")) if a.overrides else {}
    ledger = compare(load(a.source), load(a.successor), dest, ov)
    with open(a.out, "w", encoding="utf-8") as fh:
        json.dump(ledger, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    if a.md:
        with open(a.md, "w", encoding="utf-8") as fh:
            fh.write(to_md(ledger))
    print("clauses %d: covered %d, partial %d, unique %d" % (len(ledger["clauses"]), ledger["counts"]["covered"], ledger["counts"]["partial"], ledger["counts"]["unique"]))
    for r in ledger["clauses"]:
        print("  %-8s %.2f  %s  %s" % (r["mark"], r["score"], r["id"] or r["key"], ("missing: " + ", ".join(r["missing_precision"])) if r["missing_precision"] else ""))


if __name__ == "__main__":
    main()
