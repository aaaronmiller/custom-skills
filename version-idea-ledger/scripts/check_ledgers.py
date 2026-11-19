#!/usr/bin/env python3
"""Gate for a family's ledgers: every idea has one valid category, every file one disposition.

Usage:
  python3 -I -B check_ledgers.py --files DOSSIER/ledgers/file-ledger.jsonl \
      --ideas DOSSIER/ledgers/idea-ledger.jsonl --canonical-root PATH \
      [--allow-pending] [--no-quote-check] [--json-out report.json]

Exit 0 prints PASS and the counts; exit 1 prints REFUSED and every failing row.

Idea rows (one atomic idea each) must have id, version, source, loc, idea and category.
  implemented     where: "path[:line]" or "path#section", several joined by "; ". Each path
                  exists (absolute, or relative to --canonical-root).
  to-incorporate  target: where in the current implementation it should land.
  duplicate       duplicate_of: the id of a row that is not itself a duplicate.
  rejected        reason.
  stretch-goal    (reason recommended).
  unknown         question: the evidence that would decide it.
The quote, when present, must occur in the source file (whitespace and Markdown emphasis
ignored), within three lines of loc when loc is "L<n>" or "L<n>-L<m>". A row without a
quote needs quote_exempt (for example "binary" or "generated HTML"). For an idea inside a zip
archive, source is the .zip and member names the file inside it; loc counts lines in the member.
HTML is compared with its tags removed.

File rows must have a final disposition (keep, archive, removal-candidate). A removal
candidate needs a reason. An archived file may not be the source of an unknown idea, since
archiving says every idea in it has a home. A file whose ideas_status is pending has not
been mined, unless its bytes equal a file that was (same_as).
"""
import argparse
import html
import json
import os
import re
import sys
import zipfile

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import CATEGORIES, FINAL_DISPOSITIONS, ID_RE, LOC_LINE_RE, norm_ws, read_jsonl  # noqa: E402

MAX_QUOTE_FILE = 25 * 1024 * 1024
_cache = {}


def simplify(s):
    s = s.replace("**", "").replace("__", "").replace("`", "")
    return norm_ws(s).lower()


def text_of(path, member=None):
    """File text; a zip member's text when member is set; HTML with tags removed."""
    if member:
        with zipfile.ZipFile(path) as z:
            text = z.read(member).decode("utf-8", "replace")
    else:
        if os.path.getsize(path) > MAX_QUOTE_FILE:
            return None
        with open(path, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
    if (member or path).lower().endswith((".html", ".htm")):
        text = html.unescape(re.sub(r"<[^>]+>", " ", text))
    return text


def lines_of(path, member=None):
    key = (path, member)
    if key not in _cache:
        try:
            text = text_of(path, member)
            _cache[key] = None if text is None else text.splitlines()
        except (OSError, KeyError, zipfile.BadZipFile):
            _cache[key] = None
    return _cache[key]


def quote_found(path, loc, quote, member=None):
    lines = lines_of(path, member)
    if lines is None:
        return None
    q = simplify(quote)
    m = LOC_LINE_RE.match(loc or "")
    if m:
        lo = max(int(m.group(1)) - 4, 0)
        hi = int(m.group(2) or m.group(1)) + 3
        window = " ".join(lines[lo:hi])
        if q in simplify(window):
            return True
    return q in simplify(" ".join(lines))


def where_paths(where):
    for part in where.split(";"):
        part = part.strip()
        if not part:
            continue
        yield re.split(r"[#]|:(?=\d|L\d|[A-Za-z_])", part, maxsplit=1)[0].strip()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--files", required=True)
    ap.add_argument("--ideas", required=True)
    ap.add_argument("--canonical-root", required=True)
    ap.add_argument("--allow-pending", action="store_true")
    ap.add_argument("--no-quote-check", action="store_true")
    ap.add_argument("--json-out")
    a = ap.parse_args()

    files = {r["path"]: r for r in read_jsonl(a.files)}
    ideas = read_jsonl(a.ideas)
    errors, warnings = [], []
    ids = {}
    for i in ideas:
        iid = i.get("id", "")
        if not ID_RE.match(iid):
            errors.append(f"idea {iid!r}: bad or missing id")
        if iid in ids:
            errors.append(f"idea {iid}: duplicate id")
        ids[iid] = i

    unknown_sources = set()
    for i in ideas:
        iid, cat = i.get("id"), i.get("category")
        for key in ("version", "source", "loc", "idea", "category"):
            if not i.get(key):
                errors.append(f"idea {iid}: missing {key}")
        if cat not in CATEGORIES:
            errors.append(f"idea {iid}: category {cat!r} not one of {', '.join(CATEGORIES)}")
            continue
        src = os.path.abspath(os.path.expanduser(i.get("source", "")))
        if src not in files:
            errors.append(f"idea {iid}: source not in file ledger: {src}")
        if cat == "unknown":
            unknown_sources.add(src)
        if i.get("quote"):
            if not a.no_quote_check and os.path.exists(src):
                ok = quote_found(src, i.get("loc"), i["quote"], i.get("member"))
                if ok is False:
                    errors.append(f"idea {iid}: quote not found in {src} near {i.get('loc')}: {i['quote'][:80]!r}")
                elif ok is None:
                    warnings.append(f"idea {iid}: quote not checked (file unreadable or over 25 MB)")
        elif not i.get("quote_exempt"):
            errors.append(f"idea {iid}: no quote and no quote_exempt")
        if cat == "implemented":
            if not i.get("where"):
                errors.append(f"idea {iid}: implemented without where")
            else:
                for p in where_paths(i["where"]):
                    full = p if os.path.isabs(p) else os.path.join(a.canonical_root, p)
                    if not os.path.exists(os.path.expanduser(full)):
                        errors.append(f"idea {iid}: where path does not exist: {p}")
        elif cat == "to-incorporate" and not i.get("target"):
            errors.append(f"idea {iid}: to-incorporate without target")
        elif cat == "duplicate":
            d = i.get("duplicate_of")
            if not d or d not in ids or d == iid:
                errors.append(f"idea {iid}: duplicate_of {d!r} is not another row")
            elif ids[d].get("category") == "duplicate":
                errors.append(f"idea {iid}: duplicate_of {d} is itself a duplicate; point at the canonical row")
        elif cat == "rejected" and not i.get("reason"):
            errors.append(f"idea {iid}: rejected without reason")
        elif cat == "unknown" and not i.get("question"):
            errors.append(f"idea {iid}: unknown without question")

    mined = {p for p, r in files.items() if r.get("ideas_status") in ("mined", "no-ideas")}
    for path, r in files.items():
        disp = r.get("disposition")
        if r.get("missing"):
            continue
        if disp not in FINAL_DISPOSITIONS:
            if not (a.allow_pending and disp == "pending"):
                errors.append(f"file {path}: disposition {disp!r}")
        if disp == "removal-candidate" and not r.get("reason"):
            errors.append(f"file {path}: removal candidate without reason")
        if disp == "archive" and path in unknown_sources:
            errors.append(f"file {path}: archived but the source of an unknown idea")
        if r.get("ideas_status") not in ("mined", "no-ideas") and r.get("same_as") not in mined:
            if not a.allow_pending:
                errors.append(f"file {path}: not mined (ideas_status {r.get('ideas_status')!r})")

    cat_counts = {c: sum(1 for i in ideas if i.get("category") == c) for c in CATEGORIES}
    disp_counts = {d: sum(1 for r in files.values() if r.get("disposition") == d)
                   for d in FINAL_DISPOSITIONS + ("pending",)}
    report = {"result": "REFUSED" if errors else "PASS", "ideas": len(ideas), "categories": cat_counts,
              "files": len(files), "dispositions": disp_counts, "errors": errors, "warnings": warnings}
    if a.json_out:
        with open(a.json_out, "w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=2, sort_keys=True)
    for w in warnings[:50]:
        print("warning:", w)
    for e in errors:
        print(e)
    print(report["result"], json.dumps({"ideas": cat_counts, "files": disp_counts}, sort_keys=True))
    raise SystemExit(1 if errors else 0)


if __name__ == "__main__":
    main()
