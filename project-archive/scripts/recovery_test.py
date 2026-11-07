#!/usr/bin/env python3
"""Test the recorded recovery of an archived folder on a scratch copy (DA-033 tested recovery).

Usage:
  python3 -I recovery_test.py --work W --scratch DIR

Reads only W/archive-record.json (the record a later reader would have), not
the code that wrote it. Copies the archived folder into DIR, rebuilds the
old-path link there, then follows the record's recovery instructions with
every path mapped into DIR. Passes when the restored copy has the recorded
tree digest and, for a repository, the recorded HEAD, branch, status, stash
list and the hash of the changed content (so a dirty file, an untracked file and the stash,
which is Git metadata, are all part of the check). On a pass it sets
recovery.tested in the record and writes W/recovery-test.json.
The archived folder itself is only read.
"""
import argparse
import os
import shutil
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import _lib as L  # noqa: E402


def run(work, scratch):
    recp = os.path.join(work, "archive-record.json")
    rec = L.read_json(recp)
    steps = [r["step"] for r in L.read_receipts(work)]
    if "move" not in steps:
        L.die("recovery_test: refused, the move is not recorded yet", 3)
    orig, arch = rec["locators"]["original_path"], rec["locators"]["archive_path"]
    scratch = os.path.abspath(scratch)
    if L.inside(scratch, arch) or L.inside(scratch, orig) or (os.path.exists(scratch) and os.listdir(scratch)):
        L.die("recovery_test: the scratch directory must be new or empty and outside the archived folder", 2)
    name = os.path.basename(arch)
    m_arch = os.path.join(scratch, "archive", name)
    m_orig = os.path.join(scratch, "original", os.path.basename(orig))
    os.makedirs(os.path.dirname(m_arch))
    os.makedirs(os.path.dirname(m_orig))
    shutil.copytree(arch, m_arch, symlinks=True)
    os.symlink(m_arch, m_orig)
    mapping = {orig: m_orig, arch: m_arch}
    out = {"scratch": scratch, "steps": [], "passed": False}

    def mp(p):
        return mapping.get(p, p)

    for ins in rec["recovery"]["instructions"]:
        op = ins["op"]
        if op == "remove-link":
            p = mp(ins["path"])
            ok = os.path.islink(p)
            if ok:
                os.unlink(p)
            out["steps"].append({"op": op, "ok": ok, "path": p})
        elif op == "move":
            src, dst = mp(ins["from"]), mp(ins["to"])
            ok = os.path.isdir(src) and not os.path.lexists(dst)
            if ok:
                os.rename(src, dst)
            out["steps"].append({"op": op, "ok": ok, "from": src, "to": dst})
        elif op == "verify":
            d = L.tree_digest(m_orig) if os.path.isdir(m_orig) else None
            ok = d == ins["tree_digest"]
            detail = {"digest_ok": ok}
            if ins.get("git_state") is not None:
                g = L.git_state(L.git_facts(m_orig))
                diff = [k for k in ins["git_state"] if ins["git_state"][k] != g.get(k)]
                detail["git_differs"] = diff
                ok = ok and not diff
            out["steps"].append({"op": op, "ok": ok, **detail})
        else:
            out["steps"].append({"op": op, "ok": False, "detail": "unknown instruction"})
        if not out["steps"][-1]["ok"]:
            break
    out["passed"] = bool(out["steps"]) and all(s["ok"] for s in out["steps"]) and out["steps"][-1]["op"] == "verify"
    out["tested_at"] = L.now_iso()
    h = L.write_json(os.path.join(work, "recovery-test.json"), out)
    if out["passed"]:
        rec["recovery"].update({"tested": True, "tested_at": out["tested_at"], "result_file": "recovery-test.json", "result_sha256": h})
        L.write_json(recp, rec)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--work", required=True)
    ap.add_argument("--scratch", required=True)
    a = ap.parse_args()
    res = run(os.path.abspath(a.work), a.scratch)
    for s in res["steps"]:
        print("%s  %s" % ("ok  " if s["ok"] else "FAIL", s))
    print("recovery tested: %s" % res["passed"])
    sys.exit(0 if res["passed"] else 1)


if __name__ == "__main__":
    main()
