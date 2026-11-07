#!/usr/bin/env python3
"""Extract clauses from Markdown specs and plans.

Usage:
  python3 -I extract_clauses.py PATH [PATH ...] [--base DIR] [--out clauses.json]

PATH may be a Markdown file or a folder (every *.md under it, skipping the
discovery skip list and .git). A clause is one of:
  id        a line, list item, heading or table row that starts with an ID
            such as SPEC-001, DA-032, FR-12, CTX-004, C054, U14, T045 or D01
            (text continues over the following lines until a blank line,
            heading or new item);
  normative a line with SHALL, MUST, SHALL NOT, MUST NOT or REQUIRED in capitals
            and no ID; its key is <file>:L<line>;
  numbered  a numbered list item under a heading that names requirements,
            decisions, rules, invariants, principles, constraints, guarantees
            or acceptance criteria; its key is <file>:<heading>:<n>.
Fenced code blocks are skipped. Every clause keeps file, line, heading path
and text. Every non-empty paragraph is also kept (as `paragraphs`) so a
successor's prose can be searched, not only its numbered clauses.
The unit rule follows the 2026-11-03 lineage comparison: a clause is a
numbered normative requirement; other statements are kept as non-clause items.
"""
import argparse
import hashlib
import json
import os
import re
import sys

sys.dont_write_bytecode = True

SKIP = {"node_modules", ".venv", "venv", "dist", "build", ".next", "target", ".turbo", ".cache",
        "coverage", "__pycache__", "vendor", ".git"}
ID_RE = re.compile(r"^(?:[A-Z][A-Z0-9]{0,11}-\d{1,4}[a-z]?|[A-Z]{1,3}\d{2,4})(?![\w-])")
NORMATIVE = re.compile(r"\b(SHALL|MUST|REQUIRED)\b")
CLAUSE_HEADINGS = re.compile(r"requirement|decision|rule|invariant|principle|constraint|guarantee|acceptance|clause|must", re.I)
LIST_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+(?:\[[ xX]\]\s+)?")
NUM_RE = re.compile(r"^\s*(\d+)[.)]\s+")


def strip_md(s):
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)
    s = s.replace("**", "").replace("__", "")
    return re.sub(r"\s+", " ", s).strip()


def norm_hash(text):
    t = re.sub(r"[^a-z0-9 ]+", " ", text.lower())
    return hashlib.sha256(" ".join(t.split()).encode()).hexdigest()[:16]


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:40] or "section"


def md_files(path):
    if os.path.isfile(path):
        return [path]
    out = []
    for d, dirs, files in os.walk(path, followlinks=False):
        dirs[:] = sorted(x for x in dirs if x not in SKIP and not os.path.islink(os.path.join(d, x)))
        for f in sorted(files):
            if f.lower().endswith((".md", ".markdown")) and not os.path.islink(os.path.join(d, f)):
                out.append(os.path.join(d, f))
    return out


def lead_id(text):
    t = text.strip().lstrip("*_`#").strip()
    m = ID_RE.match(t)
    if not m:
        return None, text
    rest = t[m.end():].lstrip("*_`").lstrip(" :.)-\u2013\u2014|").strip()
    return m.group(0), rest


def extract(path, rel):
    with open(path, encoding="utf-8", errors="replace") as fh:
        lines = fh.read().split("\n")
    clauses, paragraphs, dup = [], [], []
    heads = []
    fence = None
    seen = set()
    current = None
    para = None
    numbered_n = {}

    def close():
        nonlocal current, para
        if current:
            current["text"] = strip_md(current["text"])
            if current["text"] or current["kind"] == "id":
                current["norm_sha"] = norm_hash(current["text"])
                clauses.append(current)
            current = None
        if para and para["text"].strip():
            para["text"] = strip_md(para["text"])
            paragraphs.append(para)
        para = None

    def start(key, cid, kind, n, text):
        nonlocal current
        if key in seen:
            dup.append({"key": key, "line": n})
            return
        seen.add(key)
        current = {"key": key, "id": cid, "kind": kind, "file": rel, "line": n,
                   "heading": " > ".join(h for _, h in heads), "text": text}

    for n, raw in enumerate(lines, 1):
        s = raw.strip()
        if fence:
            if s.startswith(fence):
                fence = None
            continue
        if s.startswith("```") or s.startswith("~~~"):
            close()
            fence = s[:3]
            continue
        if not s:
            close()
            continue
        hm = re.match(r"^(#{1,6})\s+(.*)$", s)
        if hm:
            close()
            level, title = len(hm.group(1)), strip_md(hm.group(2))
            heads = [h for h in heads if h[0] < level] + [(level, title)]
            cid, rest = lead_id(title)
            if cid:
                start("%s#%s" % (rel, cid), cid, "id", n, rest)
            continue
        if s.startswith("|"):
            close()
            cells = [c.strip() for c in s.strip("|").split("|")]
            if cells and not re.match(r"^:?-{2,}", cells[0]):
                cid, rest = lead_id(cells[0])
                if cid and len(cells) > 1:
                    start("%s#%s" % (rel, cid), cid, "id", n, cells[1])
                    close()
                elif NORMATIVE.search(s):
                    start("%s:L%d" % (rel, n), None, "normative", n, " ".join(cells))
                    close()
                else:
                    paragraphs.append({"file": rel, "line": n, "text": strip_md(" ".join(cells))})
            continue
        is_item = bool(LIST_RE.match(raw))
        body = LIST_RE.sub("", raw).strip() if is_item else s
        cid, rest = lead_id(body)
        if is_item or cid:
            close()
            if cid:
                start("%s#%s" % (rel, cid), cid, "id", n, rest)
            elif NUM_RE.match(raw) and heads and CLAUSE_HEADINGS.search(heads[-1][1]):
                hk = slug(heads[-1][1])
                numbered_n[hk] = int(NUM_RE.match(raw).group(1))
                start("%s:%s:%d" % (rel, hk, numbered_n[hk]), None, "numbered", n, body)
            elif NORMATIVE.search(body):
                start("%s:L%d" % (rel, n), None, "normative", n, body)
            else:
                para = {"file": rel, "line": n, "text": body}
            continue
        if current is not None:
            current["text"] += " " + s
            continue
        if para is not None:
            para["text"] += " " + s
            continue
        if NORMATIVE.search(s):
            start("%s:L%d" % (rel, n), None, "normative", n, s)
            continue
        para = {"file": rel, "line": n, "text": s}
    close()
    return clauses, paragraphs, dup


def extract_paths(paths, base=None):
    files, clauses, paragraphs, dups = [], [], [], []
    for p in paths:
        p = os.path.abspath(os.path.expanduser(p))
        b = os.path.abspath(base) if base else (p if os.path.isdir(p) else os.path.dirname(p))
        for f in md_files(p):
            rel = os.path.relpath(f, b)
            with open(f, "rb") as fh:
                data = fh.read()
            files.append({"path": rel, "abspath": f, "sha256": hashlib.sha256(data).hexdigest(),
                          "lines": data.count(b"\n") + 1})
            c, para, d = extract(f, rel)
            clauses += c
            paragraphs += para
            dups += d
    return {"schema": "clauses/1", "inputs": [os.path.abspath(os.path.expanduser(p)) for p in paths],
            "files": files, "clauses": clauses, "paragraphs": paragraphs, "duplicate_keys": dups}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--base", help="make file paths relative to this folder")
    ap.add_argument("--out")
    a = ap.parse_args()
    res = extract_paths(a.paths, a.base)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as fh:
            json.dump(res, fh, indent=1, ensure_ascii=False)
            fh.write("\n")
    kinds = {}
    for c in res["clauses"]:
        kinds[c["kind"]] = kinds.get(c["kind"], 0) + 1
    print("%d files, %d clauses %s, %d paragraphs, %d duplicate keys" % (
        len(res["files"]), len(res["clauses"]), kinds, len(res["paragraphs"]), len(res["duplicate_keys"])))
    if not a.out:
        for c in res["clauses"]:
            print("  %-40s %-9s %s" % (c["key"][:40], c["kind"], c["text"][:90]))


if __name__ == "__main__":
    main()
