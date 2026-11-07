#!/usr/bin/env python3
"""Reference discovery scan, and the check that an archive root is excluded from it.

Usage:
  python3 -I discovery.py scan  --config CFG.json [--json OUT]
  python3 -I discovery.py check --config CFG.json --archive-root R

CFG.json: {"roots": ["~/code", ...], "exclude": ["~/archive", ...]}

scan walks every root without following links (Atlas Phase 2 step 1 skip
list), lists each directory that holds a .git entry or a project marker as an
artifact, and lists links as aliases, never as artifacts: the link left at an
old path after a move is an alias of the archived folder.

check passes only when an exclude entry covers the archive root AND a fresh
scan lists nothing that resolves under the archive root. Agents that scan the
code roots treat old spec files inside archive folders as current, which is
why the archive root is a separate, excluded root (foundation plan section 6).
Other discovery tools (catalogs, indexers, plan-lineage) need the same
exclusion configured in their own settings; this script only proves the rule
on the config it is given.
"""
import argparse
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import _lib as L  # noqa: E402

MARKERS = ("package.json", "pyproject.toml", "setup.py", "Cargo.toml", "go.mod", "SKILL.md",
           "spec.md", "tasks.md", "README.md", "project-intake.json", "CLAUDE.md", "AGENTS.md")


def expand(p):
    return os.path.abspath(os.path.expanduser(p))


def scan(config):
    roots = [expand(r) for r in config.get("roots", [])]
    exclude = [expand(e) for e in config.get("exclude", [])]
    artifacts, aliases = [], []
    for root in roots:
        if not os.path.isdir(root) or any(L.inside(root, e) for e in exclude):
            continue
        for dirpath, _dirs, files, links in L.walk(root, exclude=exclude, skip_git=True):
            has_git = os.path.lexists(os.path.join(dirpath, ".git"))
            marks = [m for m in MARKERS if m in files]
            if (has_git or marks) and dirpath != root:
                artifacts.append({"path": dirpath, "class": "project", "git": has_git, "markers": marks})
            for name in links:
                full = os.path.join(dirpath, name)
                aliases.append({"path": full, "target": os.readlink(full), "class": "alias"})
    return {"roots": roots, "exclude": exclude, "artifacts": artifacts, "aliases": aliases}


def check(config_path, archive_root):
    config = L.read_json(config_path)
    root = expand(archive_root)
    res = scan(config)
    problems = []
    if not any(L.inside(root, e) or L.inside(os.path.realpath(root), e) for e in res["exclude"]):
        problems.append("no exclude entry in %s covers the archive root %s" % (config_path, root))
    listed = [x["path"] for x in res["artifacts"] if L.inside_real(x["path"], root)]
    if listed:
        problems.append("the scan lists %d path(s) under the archive root, e.g. %s" % (len(listed), listed[0]))
    return {"config": os.path.abspath(config_path), "archive_root": root, "artifacts_seen": len(res["artifacts"]),
            "aliases_seen": len(res["aliases"]), "listed_under_archive_root": listed,
            "problems": problems, "passed": not problems, "checked_at": L.now_iso()}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("scan")
    s.add_argument("--config", required=True)
    s.add_argument("--json")
    c = sub.add_parser("check")
    c.add_argument("--config", required=True)
    c.add_argument("--archive-root", required=True)
    a = ap.parse_args()
    if a.cmd == "scan":
        res = scan(L.read_json(a.config))
        if a.json:
            L.write_json(a.json, res)
        for x in res["artifacts"]:
            print("artifact  %s" % x["path"])
        for x in res["aliases"]:
            print("alias     %s -> %s" % (x["path"], x["target"]))
        return
    res = check(a.config, a.archive_root)
    for p in res["problems"]:
        print("FAIL  %s" % p)
    print("archive root excluded from discovery: %s" % res["passed"])
    sys.exit(0 if res["passed"] else 1)


if __name__ == "__main__":
    main()
