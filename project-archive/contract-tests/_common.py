"""Shared helpers for the contract tests. Standard library only.

The rules in check_archive_output and check_lineage_output are a line-by-line
port of checkArchiveOutput and checkLineageOutput in the workbench's
packages/durable-agent/src/assign/skill-contracts.ts (T045), so a skill that
passes here passes the agent's harness on the same output.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.realpath(__file__))
SEVEN = ["consumers", "sandbox_test", "manifest", "path_map", "old_path_links", "working_copy_repair", "live_use_guard"]
GIT_ENV = dict(os.environ, GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0", LC_ALL="C")


def args(desc):
    ap = argparse.ArgumentParser(description=desc)
    ap.add_argument("--skills", default=os.path.dirname(HERE), help="folder holding project-archive/ and portfolio-lineage/")
    ap.add_argument("--project-archive", help="path of the project-archive skill (overrides --skills)")
    ap.add_argument("--portfolio-lineage", help="path of the portfolio-lineage skill (overrides --skills)")
    ap.add_argument("--tmp", help="parent for the temporary sandbox (default: system temp)")
    a = ap.parse_args()
    a.pa = os.path.abspath(a.project_archive or os.path.join(a.skills, "project-archive"))
    a.pl = os.path.abspath(a.portfolio_lineage or os.path.join(a.skills, "portfolio-lineage"))
    return a


def run(script, *argv, env=None):
    r = subprocess.run([sys.executable, "-I", "-B", script] + [str(x) for x in argv], capture_output=True, text=True, env=env)
    return r.returncode, r.stdout, r.stderr


def contract_output(skill_dir, sandbox, env=None):
    """Run <skill>/bin/contract the way the T045 harness does; return (exit, parsed JSON or None, stderr)."""
    rc, so, se = run(os.path.join(skill_dir, "bin", "contract"), "--fixture", os.path.join(sandbox, "no-fixture"), "--sandbox", os.path.join(sandbox, "contract"), env=env)
    try:
        return rc, json.loads(so), se
    except ValueError:
        return rc, None, se


def contract_verdict(rc, out, probs, clause):
    """(ok, message) for part 1. The harness needs exit 0 AND output that meets its rules."""
    if out is None:
        return False, "bin/contract printed no JSON (exit %s)" % rc
    if probs:
        return False, "; ".join(probs)
    if rc != 0:
        own = [c.get("check") for c in out.get("checks", []) if not c.get("ok")]
        return False, "bin/contract exited %s; its own failing checks: %s" % (rc, own)
    return True, "bin/contract exits 0 and its output meets the harness %s rules" % clause


def check_archive_output(o):
    p = []
    if (o.get("move_without_hold") or {}).get("refused") is not True:
        p.append("DA-032: a folder move without a hold or an approval must be refused as never-class")
    for a in SEVEN:
        if (o.get("artifacts") or {}).get(a) is None:
            p.append("DA-032: approved move under a hold lacks %s" % a)
    if ((o.get("artifacts") or {}).get("sandbox_test") or {}).get("passed") is not True:
        p.append("DA-032: the sandbox test did not pass")
    if o.get("steps") != ["mine", "index", "move", "link"]:
        p.append("DA-033: steps must run in the order mine, index, move, link")
    for k in ("identity", "locators", "predecessor", "successor", "uncommitted_state", "working_copy_state"):
        if not (o.get("record") and k in o["record"]):
            p.append("DA-033: the record does not keep %s" % k)
    if (o.get("recovery") or {}).get("tested") is not True:
        p.append("DA-033: the recovery was not tested")
    if o.get("archive_root_excluded_from_discovery") is not True:
        p.append("DA-033: the archive root is not excluded from discovery")
    if not isinstance(o.get("lineage_page"), str) or not o.get("lineage_page"):
        p.append("DA-033: no Living Documents lineage page")
    return p


def check_lineage_output(o):
    p = []
    for c in o.get("clauses") or []:
        if c.get("mark") not in ("covered", "partial", "unique"):
            p.append("DA-034: clause %s must be marked covered, partial or unique" % c.get("id"))
    if not (o.get("clauses") or []):
        p.append("DA-034: no clause-level comparison")
    for f in o.get("folders") or []:
        if (f.get("unique_without_destination") or 0) > 0 and f.get("archived"):
            p.append("DA-034: %s holds a unique clause without a destination and was archived" % f.get("path"))
    return p


def git_out(folder, *argv):
    r = subprocess.run(["git", "-C", folder] + list(argv), capture_output=True, env=GIT_ENV)
    return r.stdout


def tree_hash(folder):
    """Independent tree hash (not the skill's): paths, link targets and file bytes."""
    h = hashlib.sha256()
    for d, dirs, files in os.walk(folder, followlinks=False):
        dirs.sort()
        for n in sorted(files + [x for x in dirs if os.path.islink(os.path.join(d, x))]):
            p = os.path.join(d, n)
            rel = os.path.relpath(p, folder)
            if os.path.islink(p):
                h.update(b"L" + rel.encode() + b"\0" + os.readlink(p).encode() + b"\0")
            else:
                with open(p, "rb") as fh:
                    h.update(b"F" + rel.encode() + b"\0" + hashlib.sha256(fh.read()).digest())
    return h.hexdigest()


class Report:
    def __init__(self, clause):
        self.clause = clause
        self.fails = []
        self.passes = []

    def check(self, ok, what):
        (self.passes if ok else self.fails).append(what)
        return ok

    def finish(self):
        if self.fails:
            print("FAIL %s: %s" % (self.clause, "; ".join(self.fails)))
            print("  (%d of %d checks passed)" % (len(self.passes), len(self.passes) + len(self.fails)))
            sys.exit(1)
        print("PASS %s: all %d checks hold (%s)" % (self.clause, len(self.passes), "; ".join(self.passes)))
        sys.exit(0)


def sandbox(tmp):
    return tempfile.TemporaryDirectory(prefix="contract-", dir=tmp)
