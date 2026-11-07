#!/usr/bin/env python3
"""List every consumer of a folder: things outside it that would break if it moved.

Usage:
  python3 -I consumers.py FOLDER --roots PATH [PATH ...] [--exclude PATH ...]
                          [--crontab] [--max-bytes N] [--json OUT]

A consumer is found by path reference, never by name:
  symlink            a link outside the folder whose target resolves into it
  path-reference     a text file outside the folder that names the folder's
                     absolute path, its resolved path, or its ~ / $HOME form
  git-worktree-link  a .git file outside the folder whose gitdir points into it
  linked-worktree    a worktree of the folder's repository that lives outside it
  crontab            a line of `crontab -l` naming the folder (with --crontab)

Roots may be directories or single files (for example a saved crontab, a
skillshare config, catalog.json, links.json). Links are never followed while
walking. The skip list is Atlas Phase 2 step 1. The folder itself is walked
separately and its own absolute self-references are reported as
`internal_absolute_refs` (they break after a move unless the old-path link is
kept; virtual environments are the usual case).

Snippets never show secrets: files with sensitive names are reported without a
snippet, and every snippet passes through a redaction filter.
Read-only. Writes only the --json file when given.
"""
import argparse
import os
import subprocess
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import _lib as L  # noqa: E402


def needles_for(folder):
    a = os.path.abspath(folder)
    r = os.path.realpath(folder)
    out = {a, r}
    home = os.path.expanduser("~")
    for p in (a, r):
        if L.inside(p, home) and p != home:
            rel = os.path.relpath(p, home)
            out.add("~/" + rel)
            out.add("$HOME/" + rel)
            out.add("${HOME}/" + rel)
    return sorted(out, key=len, reverse=True)


def make_matcher(needles):
    import re
    pats = [re.escape(n) + r"(?![A-Za-z0-9_.\-])" for n in needles]
    return re.compile("|".join(pats))


def snippet(line, m):
    s = max(0, m.start() - 60)
    e = min(len(line), m.end() + 60)
    return L.redact(line[s:e].strip())


def scan_text(path, matcher, max_bytes, label=None):
    """Return (hits, problem). hits: list of (line_no, matched, snippet)."""
    try:
        st = os.stat(path)
    except OSError as exc:
        return [], "stat failed: %s" % exc.strerror
    if st.st_size > max_bytes:
        return [], "larger than %d bytes, not scanned" % max_bytes
    try:
        with open(path, "rb") as fh:
            data = fh.read()
    except OSError as exc:
        return [], "read failed: %s" % exc.strerror
    if b"\0" in data[:8192]:
        return [], None
    text = data.decode("utf-8", "replace")
    hits = []
    for n, line in enumerate(text.splitlines(), 1):
        m = matcher.search(line)
        if m:
            hits.append((n, m.group(0), snippet(line, m)))
    return hits, None


def find_consumers(folder, roots, exclude=(), max_bytes=2_000_000, crontab=False):
    folder_abs = os.path.abspath(folder)
    folder_real = os.path.realpath(folder)
    if not os.path.isdir(folder_abs):
        L.die("consumers: %s is not a directory" % folder_abs)
    needles = needles_for(folder_abs)
    matcher = make_matcher(needles)
    consumers, not_scanned = [], []
    scanned = 0
    seen = set()
    ex = list(exclude) + [folder_abs, folder_real]

    def add(c):
        k = (c["kind"], c["path"], c.get("line"))
        if k not in seen:
            seen.add(k)
            consumers.append(c)

    def check_symlink(full):
        try:
            target = os.readlink(full)
        except OSError:
            return
        resolved = os.path.realpath(full)
        if L.inside(resolved, folder_real) or matcher.search(target):
            add({"kind": "symlink", "path": full, "target": target})

    def check_file(full):
        nonlocal scanned
        base = os.path.basename(full)
        if base == ".git":
            try:
                txt = open(full, encoding="utf-8", errors="replace").read(4096)
            except OSError:
                txt = ""
            if txt.startswith("gitdir:"):
                gd = txt.split(":", 1)[1].strip()
                gd_abs = gd if os.path.isabs(gd) else os.path.join(os.path.dirname(full), gd)
                if L.inside_real(gd_abs, folder_real):
                    add({"kind": "git-worktree-link", "path": full, "gitdir": gd})
            return
        hits, problem = scan_text(full, matcher, max_bytes)
        if problem:
            not_scanned.append({"path": full, "reason": problem})
            return
        scanned += 1
        for n, matched, snip in hits:
            c = {"kind": "path-reference", "path": full, "line": n, "matched": matched}
            if L.is_sensitive_name(full):
                c["snippet"] = "(withheld: sensitive file name)"
            else:
                c["snippet"] = snip
            add(c)

    for root in roots:
        root = os.path.abspath(os.path.expanduser(root))
        if os.path.islink(root):
            check_symlink(root)
            continue
        if os.path.isfile(root):
            if not any(L.inside(root, e) for e in ex):
                check_file(root)
            continue
        if not os.path.isdir(root):
            not_scanned.append({"path": root, "reason": "root does not exist"})
            continue
        for dirpath, _dirs, files, links in L.walk(root, exclude=ex):
            for name in links:
                check_symlink(os.path.join(dirpath, name))
            for name in files:
                check_file(os.path.join(dirpath, name))

    facts = L.git_facts(folder_abs)
    for wt in facts.get("worktrees", []) or []:
        if not L.inside_real(wt, folder_real):
            add({"kind": "linked-worktree", "path": wt})

    if crontab:
        try:
            r = subprocess.run(["crontab", "-l"], capture_output=True, timeout=20)
            for n, line in enumerate(r.stdout.decode("utf-8", "replace").splitlines(), 1):
                m = matcher.search(line)
                if m:
                    add({"kind": "crontab", "path": "crontab -l", "line": n, "matched": m.group(0), "snippet": snippet(line, m)})
        except (OSError, subprocess.TimeoutExpired) as exc:
            not_scanned.append({"path": "crontab -l", "reason": str(exc)})

    internal = []
    for dirpath, _dirs, files, links in L.walk(folder_abs, skip_dirs=set(), skip_git=True):
        for name in files:
            full = os.path.join(dirpath, name)
            hits, _ = scan_text(full, matcher, max_bytes)
            for n, matched, snip in hits:
                internal.append({"path": os.path.relpath(full, folder_abs), "line": n, "matched": matched,
                                 "snippet": "(withheld: sensitive file name)" if L.is_sensitive_name(full) else snip})
        for name in links:
            full = os.path.join(dirpath, name)
            t = os.readlink(full)
            if os.path.isabs(t) and (L.inside(t, folder_abs) or L.inside(t, folder_real)):
                internal.append({"path": os.path.relpath(full, folder_abs), "symlink_target": t})

    consumers.sort(key=lambda c: (c["path"], c.get("line") or 0, c["kind"]))
    return {
        "folder": folder_abs,
        "folder_realpath": folder_real,
        "needles": needles,
        "roots": [os.path.abspath(os.path.expanduser(r)) for r in roots],
        "excluded": [os.path.abspath(e) for e in exclude],
        "consumers": consumers,
        "consumer_count": len(consumers),
        "internal_absolute_refs": internal,
        "files_scanned": scanned,
        "not_scanned": not_scanned,
        "generated_at": L.now_iso(),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder")
    ap.add_argument("--roots", nargs="+", required=True)
    ap.add_argument("--exclude", nargs="*", default=[])
    ap.add_argument("--crontab", action="store_true", help="also scan `crontab -l` (read-only)")
    ap.add_argument("--max-bytes", type=int, default=2_000_000)
    ap.add_argument("--json", help="write the full result here")
    a = ap.parse_args()
    res = find_consumers(a.folder, a.roots, a.exclude, a.max_bytes, a.crontab)
    if a.json:
        L.write_json(a.json, res)
    print("folder: %s" % res["folder"])
    print("consumers: %d (files scanned %d, not scanned %d)" % (res["consumer_count"], res["files_scanned"], len(res["not_scanned"])))
    for c in res["consumers"]:
        where = c["path"] + (":%d" % c["line"] if c.get("line") else "")
        extra = c.get("target") or c.get("gitdir") or c.get("snippet") or ""
        print("  %-18s %s  %s" % (c["kind"], where, extra))
    if res["internal_absolute_refs"]:
        print("internal absolute self-references: %d (break after a move unless the old-path link stays)" % len(res["internal_absolute_refs"]))
    for n in res["not_scanned"]:
        print("  not scanned: %s (%s)" % (n["path"], n["reason"]))


if __name__ == "__main__":
    main()
