#!/usr/bin/env python3
"""Print each skill's content digest for the skill import register (T045, DA-098).

Usage: python3 -I -B skill_digest.py [SKILL_DIR ...]
       (default: ../project-archive and ../portfolio-lineage)

The digest is the one the workbench's scripts/import-skill computes: SHA-256
over the sorted relative paths and bytes of every file in the skill folder,
each as  path + NUL + bytes + NUL. A renamed, added, removed or edited file
changes it, and so does a stray __pycache__ folder: the script warns about
those because the scripts are run with -B so they never create one.
The register itself is not written; the matching import-skill command is printed.
"""
import hashlib
import os
import sys
from pathlib import Path

sys.dont_write_bytecode = True


def digest(folder):
    h = hashlib.sha256()
    files = sorted(p for p in Path(folder).rglob("*") if p.is_file())
    for f in files:
        rel = f.relative_to(folder).as_posix()
        h.update(rel.encode("utf-8") + b"\0" + f.read_bytes() + b"\0")
    return h.hexdigest(), len(files)


def main():
    here = Path(__file__).resolve().parent
    dirs = [Path(d).resolve() for d in sys.argv[1:]] or [here.parent / "project-archive", here.parent / "portfolio-lineage"]
    rc = 0
    for d in dirs:
        if not (d / "SKILL.md").is_file():
            print("%s: no SKILL.md, not a skill" % d)
            rc = 1
            continue
        stray = [p for p in d.rglob("*") if p.name == "__pycache__" or p.suffix == ".pyc"]
        dg, n = digest(d)
        print("%-20s sha256 %s  (%d files)" % (d.name, dg, n))
        if stray:
            print("  warning: %d __pycache__ or .pyc entries change the digest; remove them before registering" % len(stray))
        print("  register with: python3 -I scripts/import-skill add --name %s --path <installed path of %s> --origin <origin> --license MIT" % (d.name, d.name))
    sys.exit(rc)


if __name__ == "__main__":
    main()
