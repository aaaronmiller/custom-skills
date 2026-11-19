#!/usr/bin/env python3
"""Write a one-line-per-file map of the current implementation for readers.

Usage:
  python3 -I -B canonical_map.py ROOT [--out canonical-map.md] [--exclude GLOB ...]

For each tracked text file under ROOT (git ls-files when ROOT is a work tree, else a walk),
prints its relative path and a purpose line: the first line of a Python module docstring, the
first Markdown heading, or the first comment line of a shell, JavaScript or HTML file. Readers
use it to find where an idea may already be implemented; it is a starting point for a search,
never proof that something is or is not implemented.
"""
import argparse
import ast
import fnmatch
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import SKIP_DIRS  # noqa: E402

TEXT_EXT = {".py", ".md", ".sh", ".js", ".ts", ".mjs", ".html", ".toml", ".yaml", ".yml", ".json", ".svelte"}


def files(root):
    r = subprocess.run(["git", "-C", root, "ls-files"], capture_output=True, text=True,
                       env=dict(os.environ, GIT_OPTIONAL_LOCKS="0"))
    if r.returncode == 0 and r.stdout.strip():
        return sorted(r.stdout.split("\n")[:-1])
    out = []
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in SKIP_DIRS]
        out += [os.path.relpath(os.path.join(dp, f), root) for f in fn]
    return sorted(out)


def purpose(path):
    ext = os.path.splitext(path)[1]
    try:
        if os.path.getsize(path) > 2_000_000:
            return "(large file)"
        text = open(path, encoding="utf-8", errors="replace").read()
    except OSError:
        return "(unreadable)"
    if ext == ".py":
        try:
            doc = ast.get_docstring(ast.parse(text))
            if doc:
                return doc.strip().splitlines()[0]
        except (SyntaxError, ValueError):
            pass
    if ext == ".md":
        m = re.search(r"^#{1,3}\s+(.+)$", text, re.M)
        if m:
            return m.group(1).strip()
    m = re.search(r"^\s*(?:#(?!!)|//|<!--)\s*(.{8,})$", text, re.M)
    if m:
        return m.group(1).strip(" ->")
    return ""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root")
    ap.add_argument("--out")
    ap.add_argument("--exclude", action="append", default=[])
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    lines = [f"# Canonical map: {root}", "",
             "One line per tracked text file: path, then its stated purpose. Search before trusting it.", ""]
    for rel in files(root):
        if os.path.splitext(rel)[1] not in TEXT_EXT or any(fnmatch.fnmatchcase(rel, g) for g in a.exclude):
            continue
        full = os.path.join(root, rel)
        if os.path.isfile(full):
            lines.append(f"- `{rel}`: {purpose(full)[:160]}")
    text = "\n".join(lines) + "\n"
    if a.out:
        with open(a.out, "w", encoding="utf-8") as fh:
            fh.write(text)
        print(f"wrote {a.out} ({len(lines) - 4} files)")
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    main()
