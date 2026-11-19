#!/usr/bin/env python3
"""Build or refresh a family's file ledger: one row per audited file, keyed by absolute path.

Usage:
  python3 -I -B inventory.py --ledger DOSSIER/ledgers/file-ledger.jsonl \
      --root LABEL=PATH [--root LABEL=PATH ...] [--file LABEL=PATH ...] \
      [--rules DOSSIER/ledgers/rules.json] [--known GLOB ...] [--no-known] \
      [--prefer CANONICAL_ROOT] [--date YYYY-MM-DD] [--run-out DOSSIER/ledgers/runs/<date>.json]

Each row: path, version (the LABEL), sha256, bytes, mtime (date), git (tracked, untracked,
ignored or none), audited (date this hash was first recorded), disposition, reason, rule,
ideas_status (pending, mined, no-ideas), same_as (the original of a byte copy: a path under a
--prefer root first, else the first path in sort order),
previous_sha256 when the file changed, missing when it left the disk. Rows are never dropped.

The ledger's own folder is never inventoried, so a dossier that holds its ledgers can be a root.

Rerun behaviour, which is the point of the ledger:
  * same path and same sha256: the row is kept as it is; mining is not repeated;
  * same path, new sha256: previous_sha256 is recorded and ideas_status returns to pending;
  * path recorded with the same sha256 in another family's ledger (--known): the row copies
    that disposition and ideas_status and names the ledger in ledger_ref.
Rules (JSON: {"rules": [{"id", "glob", "disposition", "reason", "ideas": "mine"|"none"}]}) are
matched first-match-wins against the absolute path with fnmatch, where * also crosses "/".
A rule with "copy": true matches only byte copies (rows with same_as), "copy": false only
originals. They are re-applied on every run, so the rules file is the durable record of each
judgement.
A file no rule matches stays disposition "pending"; check_ledgers.py refuses pending rows.
"""
import argparse
import datetime as dt
import fnmatch
import glob
import hashlib
import json
import os
import subprocess
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import DISPOSITIONS, SKIP_DIRS, read_jsonl, write_jsonl  # noqa: E402


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def git_status_map(root):
    """Map absolute path -> tracked/untracked/ignored for files under a git work tree."""
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0")
    try:
        top = subprocess.run(["git", "-C", root, "rev-parse", "--show-toplevel"], capture_output=True,
                             text=True, env=env, timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if top.returncode != 0:
        return None
    top = top.stdout.strip()
    out = {}
    for flag, label in ((["--cached"], "tracked"), (["--others", "--exclude-standard"], "untracked"),
                        (["--others", "--ignored", "--exclude-standard"], "ignored")):
        r = subprocess.run(["git", "-C", top, "ls-files", "-z", *flag], capture_output=True, env=env, timeout=300)
        for rel in r.stdout.decode("utf-8", "replace").split("\0"):
            if rel:
                out.setdefault(os.path.join(top, rel), label)
    return out


def walk(root, skipped, own=None):
    for dirpath, dirnames, filenames in os.walk(root):
        keep = []
        for d in dirnames:
            full = os.path.join(dirpath, d)
            if d in SKIP_DIRS or full == own:
                skipped.append(full)
            elif os.path.islink(full):
                skipped.append(full + " (symlink)")
            else:
                keep.append(d)
        dirnames[:] = sorted(keep)
        for f in sorted(filenames):
            full = os.path.join(dirpath, f)
            if os.path.islink(full) or not os.path.isfile(full):
                skipped.append(full + " (link or special)")
                continue
            yield full


def load_rules(path):
    if not path:
        return []
    with open(path, encoding="utf-8") as fh:
        rules = json.load(fh).get("rules", [])
    seen = set()
    for r in rules:
        for key in ("id", "glob", "disposition", "reason"):
            if not r.get(key):
                raise SystemExit(f"rule {r!r} lacks {key}")
        if r["disposition"] not in DISPOSITIONS:
            raise SystemExit(f"rule {r['id']}: unknown disposition {r['disposition']}")
        if r["id"] in seen:
            raise SystemExit(f"duplicate rule id {r['id']}")
        if r.get("ideas", "mine") not in ("mine", "none"):
            raise SystemExit(f"rule {r['id']}: ideas must be mine or none")
        r["glob"] = os.path.expanduser(r["glob"])
        seen.add(r["id"])
    return rules


def match_rule(rules, path, row):
    for r in rules:
        if "copy" in r and bool(r["copy"]) != bool(row.get("same_as")):
            continue
        if fnmatch.fnmatchcase(path, r["glob"]):
            return r
    return None


def load_known(patterns, own):
    known = {}
    for pat in patterns:
        for p in sorted(glob.glob(os.path.expanduser(pat))):
            if os.path.abspath(p) == os.path.abspath(own):
                continue
            for row in read_jsonl(p):
                if row.get("disposition") in ("keep", "archive", "removal-candidate"):
                    known.setdefault((row["path"], row["sha256"]), (p, row))
    return known


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--root", action="append", default=[], help="LABEL=PATH, walked recursively")
    ap.add_argument("--file", action="append", default=[], help="LABEL=PATH, one file")
    ap.add_argument("--rules")
    ap.add_argument("--known", action="append",
                    default=["~/LIVING_DOCUMENTS/projects/*/ledgers/file-ledger.jsonl"])
    ap.add_argument("--no-known", action="store_true")
    ap.add_argument("--prefer", action="append", default=[],
                    help="root whose files count as the original when bytes repeat (the canonical root)")
    ap.add_argument("--date", default=dt.date.today().isoformat())
    ap.add_argument("--run-out")
    a = ap.parse_args()

    rules = load_rules(a.rules)
    known = {} if a.no_known else load_known(a.known, a.ledger)
    old = {r["path"]: r for r in read_jsonl(a.ledger)}
    skipped, seen = [], {}
    targets = []
    for spec in a.root + a.file:
        if "=" not in spec:
            raise SystemExit(f"expected LABEL=PATH, got {spec}")
        label, path = spec.split("=", 1)
        path = os.path.abspath(os.path.expanduser(path))
        if not os.path.exists(path):
            raise SystemExit(f"missing: {path}")
        targets.append((label, path))

    gitmaps = {}
    counts = {"new": 0, "unchanged": 0, "changed": 0, "missing": 0, "from_known": 0}
    for label, root in targets:
        files = [root] if os.path.isfile(root) else list(walk(root, skipped, os.path.dirname(os.path.abspath(a.ledger))))
        gmap = gitmaps.setdefault(root, git_status_map(root if os.path.isdir(root) else os.path.dirname(root)))
        for path in files:
            if path in seen:
                continue
            st = os.stat(path)
            digest = sha256(path)
            row = dict(old.get(path, {}))
            if not row:
                counts["new"] += 1
                row = {"path": path, "audited": a.date, "ideas_status": "pending"}
            elif row.get("sha256") != digest:
                counts["changed"] += 1
                row["previous_sha256"] = row.get("sha256")
                row["audited"] = a.date
                row["ideas_status"] = "pending"
                row.pop("mined", None)
            else:
                counts["unchanged"] += 1
            row.pop("missing", None)
            row.update({"version": label, "sha256": digest, "bytes": st.st_size,
                        "mtime": dt.date.fromtimestamp(st.st_mtime).isoformat(),
                        "git": (gmap or {}).get(path, "none") if gmap is not None else "none"})
            seen[path] = row

    for path, row in old.items():
        if path not in seen:
            if not os.path.exists(path):
                row["missing"] = a.date
                counts["missing"] += 1
            seen[path] = row

    prefer = [os.path.abspath(os.path.expanduser(p)).rstrip("/") + "/" for p in a.prefer]

    def original_first(path):
        return (not any(path.startswith(p) for p in prefer), path)

    by_sha = {}
    for path in sorted(seen, key=original_first):
        row = seen[path]
        first = by_sha.setdefault(row["sha256"], path)
        if first != path:
            row["same_as"] = first
        else:
            row.pop("same_as", None)

    for path in sorted(seen):
        row = seen[path]
        if row.get("missing"):
            continue
        digest = row["sha256"]
        rule = match_rule(rules, path, row)
        ref = known.get((path, digest))
        if rule:
            row.update({"disposition": rule["disposition"], "reason": rule["reason"], "rule": rule["id"]})
            if rule.get("ideas") == "none" and row.get("ideas_status") == "pending":
                row["ideas_status"] = "no-ideas"
        elif ref:
            counts["from_known"] += 1
            row.update({"disposition": ref[1]["disposition"], "reason": ref[1].get("reason", ""),
                        "rule": "known", "ledger_ref": ref[0],
                        "ideas_status": ref[1].get("ideas_status", "pending")})
        else:
            row.setdefault("disposition", "pending")
            if row.get("rule") not in (None, "manual"):
                row.update({"disposition": "pending", "reason": "", "rule": None})

    rows = [seen[p] for p in sorted(seen)]
    write_jsonl(a.ledger, rows)
    disp = {}
    for r in rows:
        disp[r.get("disposition", "pending")] = disp.get(r.get("disposition", "pending"), 0) + 1
    record = {"date": a.date, "ledger": os.path.abspath(a.ledger), "roots": [f"{l}={p}" for l, p in targets],
              "rows": len(rows), "counts": counts, "dispositions": disp, "skipped": sorted(set(skipped)),
              "rules": a.rules}
    if a.run_out:
        os.makedirs(os.path.dirname(os.path.abspath(a.run_out)), exist_ok=True)
        with open(a.run_out, "w", encoding="utf-8") as fh:
            json.dump(record, fh, indent=2, sort_keys=True)
    print(json.dumps({k: record[k] for k in ("rows", "counts", "dispositions")}, sort_keys=True))
    print(f"skipped directories or links: {len(record['skipped'])}")


if __name__ == "__main__":
    main()
