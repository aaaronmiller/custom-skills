#!/usr/bin/env python3
"""refresh-step.py: the only way the intent-refresh cron agent runs the two
pipeline phases that take arguments.

  python3 -I refresh-step.py batch <project-slug>
  python3 -I refresh-step.py merge <verdict-file-name>

The slug must be a plain slug and the verdict file must be a bare file name
inside ~/.intent-archaeology/verdicts/. No other argument reaches the phase
scripts, so the agent cannot choose an output path (04-batch --out) or point
the merge at a file outside the verdicts folder.
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
VERDICTS = os.path.expanduser("~/.intent-archaeology/verdicts")
SLUG = re.compile(r"^[a-z0-9][a-z0-9._-]{0,80}$")
NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,120}\.json$")


def main(argv):
    if len(argv) != 2:
        sys.exit("usage: refresh-step.py batch <slug> | merge <verdict-file.json>")
    step, value = argv
    if step == "batch":
        if not SLUG.match(value):
            sys.exit(f"refused: not a project slug: {value!r}")
        cmd = [sys.executable, "-I", os.path.join(HERE, "04-batch.py"), "--project", value]
    elif step == "merge":
        if not NAME.match(value):
            sys.exit(f"refused: not a bare verdict file name: {value!r}")
        path = os.path.join(VERDICTS, value)
        if not os.path.isfile(path):
            sys.exit(f"refused: no such verdict file: {path}")
        cmd = [sys.executable, "-I", os.path.join(HERE, "05-merge.py"), "--verdicts", path]
    else:
        sys.exit(f"refused: unknown step {step!r}")
    return subprocess.call(cmd)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
