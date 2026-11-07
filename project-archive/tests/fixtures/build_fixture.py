#!/usr/bin/env python3
"""Build the project-archive test fixture inside a new directory.

Usage: python3 -I build_fixture.py TOP

TOP must not exist or be empty. Creates, all under TOP:
  .project-archive-sandbox     marker that allows sandbox-mode moves under TOP
  root/proj-a/                 plain folder with three planted consumers:
  root/tools/proj-a-link         a symlink to proj-a
  root/config/app.json           a config file naming proj-a's path
  root/scripts/run.sh            a script naming proj-a's path
  root/proj-b/                 Git repository with one uncommitted edit, one
                               untracked file and one stash entry, plus a
                               spec.md whose clauses the successor covers
  successor/spec.md            the successor spec for proj-b
  archive-root/                empty archive root
  ld/project-history.md        Living Documents history page (fixture)
  discovery.json               roots [TOP], exclude [archive-root]
  hold.yaml                    hold: [migration]
  approval-proj-a.json         operator approval for root/proj-a -> archive-root/demo/proj-a
  approval-proj-b.json         operator approval for root/proj-b -> archive-root/demo/proj-b
Every file time is set two hours back so the live-use guard passes.
Git runs with no global or system config, so the fixture is the same on every host.
"""
import json
import os
import subprocess
import sys
import time

sys.dont_write_bytecode = True

GIT_ENV = dict(os.environ, GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull, GIT_TERMINAL_PROMPT="0",
               GIT_AUTHOR_DATE="2026-11-01T10:00:00Z", GIT_COMMITTER_DATE="2026-11-01T10:00:00Z")
GITC = ["-c", "user.name=fixture builder", "-c", "user.email=fixture-builder@localhost",
        "-c", "commit.gpgsign=false", "-c", "init.defaultBranch=main"]


def w(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def git(cwd, *args):
    subprocess.run(["git"] + GITC + list(args), cwd=cwd, env=GIT_ENV, check=True, capture_output=True)


SUCCESSOR_SPEC = """# Successor spec (fixture)

Test data for the project-archive skill. Not a real specification.

## Requirements

- **SPEC-001**: THE archive procedure SHALL mine, index, move and link a folder in that order.
- **SPEC-002**: THE archive procedure SHALL keep the uncommitted and working-copy state of the folder.
"""

PROJ_B_SPEC = """# proj-b spec (fixture)

## Requirements

- **SPEC-001**: THE archive procedure SHALL mine, index, move and link a folder in that order.
- **SPEC-002**: THE archive procedure SHALL keep the uncommitted and working-copy state of the folder.
"""


def build(top):
    top = os.path.abspath(top)
    if os.path.exists(top) and os.listdir(top):
        raise SystemExit("build_fixture: %s exists and is not empty" % top)
    os.makedirs(top, exist_ok=True)
    w(os.path.join(top, ".project-archive-sandbox"), "project-archive sandbox marker; moves under this folder are test moves\n")
    root = os.path.join(top, "root")
    a = os.path.join(root, "proj-a")
    w(os.path.join(a, "README.md"), "# proj-a\n\nA plain folder used as the move fixture.\n")
    w(os.path.join(a, "data", "values.csv"), "name,value\nalpha,1\nbeta,2\n")
    w(os.path.join(a, "src", "tool.py"), "print('proj-a tool')\n")
    os.chmod(os.path.join(a, "src", "tool.py"), 0o755)
    os.makedirs(os.path.join(root, "tools"))
    os.symlink(a, os.path.join(root, "tools", "proj-a-link"))
    w(os.path.join(root, "config", "app.json"), json.dumps({"data_dir": a + "/data"}, indent=1) + "\n")
    w(os.path.join(root, "scripts", "run.sh"), "#!/bin/sh\ncd %s && python3 src/tool.py\n" % a)
    w(os.path.join(root, "scripts", "unrelated.sh"), "#!/bin/sh\necho %s\n" % (a + "-old"))
    b = os.path.join(root, "proj-b")
    w(os.path.join(b, "README.md"), "# proj-b\n\nA Git repository used as the archive fixture.\n")
    w(os.path.join(b, "spec.md"), PROJ_B_SPEC)
    w(os.path.join(b, "notes.md"), "first line\n")
    git(b, "init", "-q")
    git(b, "add", "-A")
    git(b, "commit", "-q", "-m", "fixture: first commit")
    w(os.path.join(b, "notes.md"), "first line\nstashed line\n")
    git(b, "stash", "push", "-q", "-m", "fixture stash entry")
    w(os.path.join(b, "README.md"), "# proj-b\n\nA Git repository used as the archive fixture.\nUncommitted edit.\n")
    w(os.path.join(b, "untracked.txt"), "an untracked file\n")
    w(os.path.join(top, "successor", "spec.md"), SUCCESSOR_SPEC)
    os.makedirs(os.path.join(top, "archive-root"))
    w(os.path.join(top, "ld", "project-history.md"), "# demo project: history\n\nLineage entries are appended below.\n")
    w(os.path.join(top, "discovery.json"), json.dumps({"roots": [top], "exclude": [os.path.join(top, "archive-root")]}, indent=1) + "\n")
    w(os.path.join(top, "hold.yaml"), "run: go\nhold: [migration]\n")
    for name in ("proj-a", "proj-b"):
        w(os.path.join(top, "approval-%s.json" % name), json.dumps({
            "source": os.path.join(root, name), "dest": os.path.join(top, "archive-root", "demo", name),
            "approved_by": "fixture operator", "approved_at": "2026-11-07T00:00:00Z"}, indent=1) + "\n")
    old = time.time() - 7200
    for d, dirs, files in os.walk(top):
        for n in dirs + files:
            os.utime(os.path.join(d, n), (old, old), follow_symlinks=False)
    return top


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    print(build(sys.argv[1]))
