#!/usr/bin/env python3
"""Screen every removal candidate before it reaches the judge. Classifies only; deletes nothing.

Usage:
  python3 -I -B screen_removals.py --ledgers DOSSIER/ledgers [--git-root ROOT[@REV] ...]
      [--prefer CANONICAL_ROOT ...] [--date YYYY-MM-DD] [--report DOSSIER/ledgers/runs/<date>-screen.json]

A rule may propose "removal-candidate"; this screen decides whether the file ledger may keep
that disposition. It reads ledgers/file-ledger.jsonl, ledgers/idea-ledger.jsonl and
ledgers/rules.json (optional "protect": [{"glob", "reason"}]), and rewrites the file ledger.
Every row a rule proposed for removal ends in one of two states:

  passed  disposition stays removal-candidate and the row gets
          survivor = {"kind": "loose"|"zip-member"|"git-blob"|"ephemeral", "path", ...}
          (for a zip: one survivor per member, under "members"), screened = date, and
          screened_sha256 = the bytes screened.
  held    disposition becomes archive; held = [reasons]; rule_disposition = removal-candidate.

A candidate is held when any of these is true (all reasons are recorded, not only the first):
  H1 stale      its bytes on disk differ from the ledger's sha256 (rerun inventory.py).
  H2 cited      it is the source of an idea row; the citation must keep resolving. Re-point
                the idea's source to a surviving copy (ideas_tool.py set) to release it.
  H3 protected  operator words or credential handling: a basename naming a prompt, transcript,
                pasted text, handoff, restart or meta prompt, intent or instructions; text that
                mentions credentials, API keys, tokens, passwords or secrets; or a "protect"
                glob in rules.json. An archive is protected when any member is. Protected rows
                are held even when a byte copy exists.
  H4 unique     its bytes do not survive outside the removal set. Survival is checked against
                the whole set at once: a copy that is itself removed does not count, a member of
                an archive counts only while that archive survives, a git blob counts only in the
                tree of a named revision (--git-root ROOT[@REV]), and a loose survivor is
                re-hashed live. Among identical candidates with no other survivor, the first in keeper
                order (--prefer roots, then archives, then path) is held so the rest can go.
  H5 exclusive  an archive (.zip, .tar, .tar.gz, .tgz) with a member whose bytes survive
                nowhere else, or an archive that cannot be read.

Only truly ephemeral files (.pid, .lock, .tmp, .swp, .pyc, .DS_Store, Thumbs.db) pass H4
without a survivor. Generated output, logs, backups, coverage data and superseded data are not
ephemeral: they pass only with a surviving byte copy.

inventory.py clears survivor, held and screened on every run, so the screen must run after
every inventory run; render.py and check_ledgers.py refuse a removal candidate without a
current survivor stamp.
"""
import argparse
import datetime as dt
import fnmatch
import hashlib
import json
import os
import re
import subprocess
import sys
import tarfile
import zipfile

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import SCREEN_FIELDS, read_jsonl, write_jsonl  # noqa: E402

PROTECTED_NAME = re.compile(
    r"prompt|transcript|pasted[ _-]?text|handoff|hand-off|restart|intent|instructions?|"
    r"credential|secret|\.env(\.|$)|auth\.json", re.I)
CREDENTIAL_TEXT = re.compile(
    r"api[_ -]?keys?\b|[A-Z0-9]+_API_KEY|access[_ -]?tokens?\b|bearer\s|passwords?\b|credentials?\b|"
    r"auth\.json|secrets?\b", re.I)
TEXT_EXT = (".md", ".txt", ".py", ".sh", ".json", ".jsonl", ".yaml", ".yml", ".toml", ".html", ".htm",
            ".js", ".ts", ".csv", ".tsv", ".log", ".ini", ".cfg", ".conf", ".env", ".xml", ".rst")
EPHEMERAL = re.compile(r"(\.pid|\.lock|\.tmp|\.swp|\.pyc)$|(^|/)(\.DS_Store|Thumbs\.db)$")
ARCHIVE = re.compile(r"\.(zip|tar|tar\.gz|tgz|tar\.bz2|tar\.xz)$", re.I)
MAX_SCAN = 4 * 1024 * 1024


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def git_blob_id(path):
    h = hashlib.sha1()
    h.update(b"blob %d\0" % os.path.getsize(path))
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def git_blobs(spec):
    """Blob ids in the tree of one named revision: "ROOT" (HEAD) or "ROOT@REV".

    Only a tree someone can name counts. A blob that is merely reachable somewhere in history
    is not a survivor: nobody will find it, and the first run accepted 11 such rows that the
    judge rejected."""
    root, _, rev = spec.partition("@")
    root, rev = os.path.abspath(os.path.expanduser(root)), rev or "HEAD"
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0")
    c = subprocess.run(["git", "-C", root, "rev-parse", "--verify", "--quiet", rev + "^{commit}"],
                       capture_output=True, text=True, env=env, timeout=60)
    if c.returncode != 0:
        raise SystemExit(f"--git-root {spec}: {rev} is not a commit in {root}")
    rev = c.stdout.strip()  # record the commit itself, so a moving HEAD cannot change the stamp
    r = subprocess.run(["git", "-C", root, "ls-tree", "-r", "-z", rev], capture_output=True, env=env, timeout=600)
    if r.returncode != 0:
        raise SystemExit(f"--git-root {spec}: cannot list the tree ({r.stderr.decode(errors='replace').strip()})")
    out = {}
    for entry in r.stdout.decode("utf-8", "replace").split("\0"):
        meta, _, path = entry.partition("\t")
        parts = meta.split()
        if len(parts) == 3 and parts[1] == "blob":
            out.setdefault(parts[2], f"{rev}:{path}")
    return out


def archive_members(path):
    """[(member name, sha256, bytes or None)] of the regular files inside an archive; None when
    unreadable. Bytes are kept only for small text members, for the protected-class scan."""
    out = []

    def keep(name, data):
        small = name.lower().endswith(TEXT_EXT) and len(data) <= MAX_SCAN
        out.append((name, sha256_bytes(data), data if small else None))
    try:
        if path.lower().endswith(".zip"):
            with zipfile.ZipFile(path) as z:
                for info in z.infolist():
                    if not info.is_dir():
                        keep(info.filename, z.read(info))
        else:
            with tarfile.open(path) as t:
                for m in t.getmembers():
                    if m.isfile():
                        keep(m.name, t.extractfile(m).read())
    except (OSError, zipfile.BadZipFile, tarfile.TarError, RuntimeError, EOFError, KeyError):
        return None
    return out


def protected_text(name, text):
    if PROTECTED_NAME.search(os.path.basename(name)):
        return "the name marks operator words, a transcript, a handoff or credential material"
    if text is not None:
        m = CREDENTIAL_TEXT.search(text)
        if m:
            return f"the text handles credentials (mentions {m.group(0).strip()!r})"
    return None


def protected_reason(path, protect_rules, members=None):
    """Why a file (or, for an archive, any of its members) is in a protected class, else None."""
    for p in protect_rules:
        if fnmatch.fnmatchcase(path, os.path.expanduser(p["glob"])):
            return f"protected by rule glob {p['glob']}: {p.get('reason', '')}".rstrip(": ")
    text = None
    if path.lower().endswith(TEXT_EXT) and os.path.getsize(path) <= MAX_SCAN:
        with open(path, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
    why = protected_text(path, text)
    if why:
        return "protected: " + why
    for name, _digest, data in members or []:
        why = protected_text(name, None if data is None else data.decode("utf-8", "replace"))
        if why:
            return f"protected: archive member {name}: {why}"
    return None


def screen(files, ideas, protect_rules=(), git_roots=(), prefer=(), date=None):
    """Screen the rows of files (dicts keyed by path) in place. Returns a summary dict."""
    date = date or dt.date.today().isoformat()
    prefer = [os.path.abspath(os.path.expanduser(p)).rstrip("/") + "/" for p in prefer]
    cited = {}
    for i in ideas:
        cited.setdefault(os.path.abspath(os.path.expanduser(i.get("source", ""))), []).append(i.get("id"))

    def proposed(r):
        return r.get("disposition") == "removal-candidate" or r.get("rule_disposition") == "removal-candidate"

    live = {p: r for p, r in files.items() if not r.get("missing") and os.path.isfile(p)}
    cands = [p for p, r in live.items() if proposed(r)]
    for p in cands:
        r = files[p]
        for k in SCREEN_FIELDS:
            r.pop(k, None)
        r["rule_disposition"] = "removal-candidate"

    members = {p: archive_members(p) for p in live if ARCHIVE.search(p)}
    held = {p: [] for p in cands}
    current = {}
    for p in cands:
        r = files[p]
        current[p] = sha256_file(p)
        if current[p] != r.get("sha256"):
            held[p].append("H1 stale: the bytes changed since inventory; rerun inventory.py")
        if p in cited:
            ids = sorted(x for x in cited[p] if x)
            held[p].append(f"H2 cited: source of idea rows {', '.join(ids[:8])}{' ...' if len(ids) > 8 else ''}; "
                           "re-point them to a surviving copy to release this file")
        why = protected_reason(p, protect_rules, members.get(p))
        if why:
            held[p].append("H3 " + why)

    # Indexes of everything that could survive: every live row's bytes and every archive member.
    by_sha = {}
    for p, r in live.items():
        by_sha.setdefault(r.get("sha256"), set()).add(p)
    member_index = {}
    for z, ms in members.items():
        for name, digest, _data in ms or []:
            member_index.setdefault(digest, []).append((z, name))
    blobs = {spec: git_blobs(spec) for spec in git_roots}

    removed = {p for p in cands if not held[p]}
    verified = {}

    def live_match(path, digest):
        if path not in verified:
            verified[path] = sha256_file(path) if os.path.isfile(path) else None
        return verified[path] == digest

    def copy_of(digest, exclude, path_for_git=None):
        for q in sorted(by_sha.get(digest, ())):
            if q != exclude and q not in removed and live_match(q, digest):
                return {"kind": "loose", "path": q, "sha256": digest}
        for z, name in sorted(member_index.get(digest, ())):
            if z != exclude and z not in removed:
                return {"kind": "zip-member" if z.lower().endswith(".zip") else "archive-member",
                        "path": z, "member": name, "sha256": digest}
        if path_for_git:
            bid = git_blob_id(path_for_git)
            for spec in sorted(blobs):
                if bid in blobs[spec]:
                    return {"kind": "git-blob", "path": spec.partition("@")[0], "tree_path": blobs[spec][bid],
                            "blob": bid, "sha256": digest}
        return None

    def survival(p):
        """(survivor dict or None, reasons) for a candidate against the current removal set."""
        if p in members:
            ms = members[p]
            if ms is None:
                return None, ["H5 exclusive: the archive cannot be read, so its members cannot be checked"]
            found, exclusive = [], []
            for name, digest, _data in ms:
                s = copy_of(digest, p)
                if s:
                    found.append(dict(s, member_of_candidate=name))
                else:
                    exclusive.append(name)
            if exclusive:
                return None, [f"H5 exclusive: {len(exclusive)} of {len(ms)} members survive nowhere else "
                              f"(e.g. {', '.join(exclusive[:3])})"]
            return {"kind": "members", "members": found}, []
        s = copy_of(current[p], p, p)
        if s:
            return s, []
        if EPHEMERAL.search(p):
            return {"kind": "ephemeral", "path": p, "sha256": current[p]}, []
        return None, ["H4 unique: no byte copy survives outside the removal set (loose file, member of a "
                      "surviving archive, or the git tree of a named revision)"]

    def keeper_order(p):
        return (not any(p.startswith(x) for x in prefer), not bool(ARCHIVE.search(p)), p.count("/"), p)

    order = sorted(cands, key=keeper_order)
    survivors = {}
    for p in order:  # holding only adds survivors, so one ordered pass is enough
        if p not in removed:
            continue
        s, why = survival(p)
        if s is None:
            removed.discard(p)
            held[p].extend(why)
        else:
            survivors[p] = s

    def relied_on(q):
        for s in survivors.values():
            for x in s.get("members", [s]):
                if x.get("path") == q:
                    return True
        return False

    # Release pass: a row held only for H4/H5 may go once later holds gave it a survivor,
    # provided no passed row relies on it.
    for p in reversed(order):
        reasons = held.get(p) or []
        if not reasons or any(not x.startswith(("H4", "H5")) for x in reasons) or relied_on(p):
            continue
        removed.add(p)
        s, why = survival(p)
        if s is None:
            removed.discard(p)
        else:
            held[p] = []
            survivors[p] = s

    counts = {"proposed": len(cands), "passed": 0, "held": 0, "by_reason": {}}
    for p in cands:
        r = files[p]
        if held[p]:
            counts["held"] += 1
            for x in held[p]:
                counts["by_reason"][x[:2]] = counts["by_reason"].get(x[:2], 0) + 1
            r["disposition"] = "archive"
            r["held"] = held[p]
        else:
            counts["passed"] += 1
            r["disposition"] = "removal-candidate"
            r["survivor"] = survivors[p]
            r["screened_sha256"] = current[p]
        r["screened"] = date
    return counts


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ledgers", required=True)
    ap.add_argument("--git-root", action="append", default=[],
                    help="ROOT or ROOT@REV: a blob in that tree counts as a survivor (default rev HEAD)")
    ap.add_argument("--prefer", action="append", default=[], help="root whose copies are kept first")
    ap.add_argument("--date", default=dt.date.today().isoformat())
    ap.add_argument("--report")
    a = ap.parse_args()

    fl = os.path.join(a.ledgers, "file-ledger.jsonl")
    rows = read_jsonl(fl)
    files = {r["path"]: r for r in rows}
    ideas = read_jsonl(os.path.join(a.ledgers, "idea-ledger.jsonl"))
    protect = []
    rp = os.path.join(a.ledgers, "rules.json")
    if os.path.exists(rp):
        with open(rp, encoding="utf-8") as fh:
            protect = json.load(fh).get("protect", [])
    counts = screen(files, ideas, protect, a.git_root, a.prefer, a.date)
    write_jsonl(fl, [files[r["path"]] for r in rows])
    if a.report:
        os.makedirs(os.path.dirname(os.path.abspath(a.report)), exist_ok=True)
        held = [{"path": p, "held": r["held"]} for p, r in files.items() if r.get("held")]
        with open(a.report, "w", encoding="utf-8") as fh:
            json.dump({"date": a.date, "counts": counts, "held": held}, fh, indent=2, sort_keys=True)
    print(json.dumps(counts, sort_keys=True))


if __name__ == "__main__":
    main()
