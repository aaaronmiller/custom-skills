#!/usr/bin/env python3
"""Plan one folder move without moving anything (DA-032).

Usage:
  python3 -I plan.py --folder SRC --dest DEST --roots PATH [PATH ...] --staging DIR
                     [--exclude PATH ...] [--hold-file FILE] [--approval FILE]
                     [--operation ARCHIVE|MOVE|RENAME] [--reason TEXT]
                     [--recent-minutes 60] [--max-sandbox-bytes N] [--crontab]

Writes into DIR (which must lie outside SRC and DEST):
  consumers.json            every consumer of SRC (consumers.py)
  manifest.json             one row per file: path, type, mode, size, sha256;
                            tree digest; Git facts; operation, risk and reason
  path-map.json             old to new for the folder and for every consumer
  old-path-links.json       the link to leave at the old path, and how
  working-copy-repair.json  worktree repair commands, metadata backups,
                            embedded absolute paths, dirty state (never committed)
  live-use-guard.json       files changed in the last N minutes and processes
                            whose working directory or open files are inside SRC
  sandbox-test.json         a copy of SRC moved inside DIR/sandbox, linked,
                            verified, then recovered and verified again
  readiness.json            the never-class verdict: approval, hold, artifact
                            hashes and every blocker

Nothing outside DIR is written. SRC and DEST are never touched. The readiness
record never authorises a move by itself: moves are never-class, and the
dry-run mover (move_dryrun.py) only prints commands for a human.
"""
import argparse
import os
import shutil
import sys
import time

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import _lib as L  # noqa: E402
import consumers as C  # noqa: E402

ARTIFACTS = [
    ("consumers", "consumers.json"),
    ("manifest", "manifest.json"),
    ("path_map", "path-map.json"),
    ("old_path_links", "old-path-links.json"),
    ("working_copy_repair", "working-copy-repair.json"),
    ("live_use_guard", "live-use-guard.json"),
    ("sandbox_test", "sandbox-test.json"),
]


def live_use_guard(folder, minutes=60):
    """Atlas Phase 7: defer a folder with files changed in the last hour or a process inside it."""
    folder = os.path.abspath(folder)
    real = os.path.realpath(folder)
    cutoff = time.time() - minutes * 60
    recent = []
    for dirpath, _d, files, links in L.walk(folder, skip_dirs=set(), skip_git=True):
        for name in files + links:
            full = os.path.join(dirpath, name)
            try:
                if os.lstat(full).st_mtime >= cutoff:
                    recent.append(os.path.relpath(full, folder))
            except OSError:
                pass
    procs = []
    me = os.getpid()
    if os.path.isdir("/proc"):
        for pid in os.listdir("/proc"):
            if not pid.isdigit() or int(pid) in (me, os.getppid()):
                continue
            hit = None
            try:
                cwd = os.readlink("/proc/%s/cwd" % pid)
                if L.inside(cwd, real) or L.inside(cwd, folder):
                    hit = "cwd"
            except OSError:
                pass
            if not hit:
                try:
                    for fd in os.listdir("/proc/%s/fd" % pid):
                        try:
                            t = os.readlink("/proc/%s/fd/%s" % (pid, fd))
                        except OSError:
                            continue
                        if t.startswith("/") and (L.inside(t, real) or L.inside(t, folder)):
                            hit = "open-file"
                            break
                except OSError:
                    pass
            if hit:
                try:
                    comm = open("/proc/%s/comm" % pid).read().strip()
                except OSError:
                    comm = "?"
                procs.append({"pid": int(pid), "command_name": comm, "inside_by": hit})
    return {
        "folder": folder,
        "checked_at": L.now_iso(),
        "recent_minutes": minutes,
        "recent_files_count": len(recent),
        "recent_files": sorted(recent)[:50],
        "processes": procs,
        "passed": not recent and not procs,
        "note": "Re-run immediately before any real move; move_dryrun.py does this.",
    }


def risk_of(facts, cons, guard):
    reasons = []
    if facts.get("dirty"):
        reasons.append("uncommitted or untracked work")
    if facts.get("stash_count"):
        reasons.append("stash entries")
    if facts.get("is_linked_worktree") or len(facts.get("worktrees") or []) > 1:
        reasons.append("linked worktrees")
    if cons["consumer_count"]:
        reasons.append("%d consumers" % cons["consumer_count"])
    if not guard["passed"]:
        reasons.append("in live use")
    level = "high" if len(reasons) >= 2 or not guard["passed"] else ("medium" if reasons else "low")
    return level, reasons


def link_method(old_path):
    if old_path.startswith("/mnt/") and len(old_path) > 6 and old_path[6] == "/":
        return "windows-junction", 'cmd.exe /c mklink /J "<windows form of old path>" "<windows form of new path>"'
    return "symlink", None


def sandbox_test(folder, dest, staging, manifest_digest, facts, max_bytes):
    """Copy, move, link, verify, recover and verify again, all inside staging/sandbox."""
    res = {"started_at": L.now_iso(), "steps": [], "passed": False}
    total = 0
    for dirpath, _d, files in os.walk(folder):
        for f in files:
            try:
                total += os.lstat(os.path.join(dirpath, f)).st_size
            except OSError:
                pass
    res["source_bytes"] = total
    if total > max_bytes:
        res["reason"] = "folder is %d bytes, above --max-sandbox-bytes %d; test a representative copy by hand" % (total, max_bytes)
        return res
    run = time.strftime("%Y%m%dT%H%M%S")
    box = os.path.join(staging, "sandbox", run)
    old = os.path.join(box, "old-location", os.path.basename(folder))
    new = os.path.join(box, "new-location", os.path.basename(dest))
    os.makedirs(os.path.dirname(old))
    os.makedirs(os.path.dirname(new))
    res["sandbox"] = box

    def step(name, ok, detail=""):
        res["steps"].append({"step": name, "ok": bool(ok), "detail": detail})
        return ok

    shutil.copytree(folder, old, symlinks=True)
    d0 = L.tree_digest(old)
    if not step("copy is faithful", d0 == manifest_digest, "copy digest %s, manifest digest %s" % (d0[:12], manifest_digest[:12])):
        return res
    g0 = L.git_state(L.git_facts(old)) if facts.get("is_repo_root") else None
    os.rename(old, new)
    os.symlink(new, old)
    d1 = L.tree_digest(new)
    if not step("move keeps every byte", d1 == manifest_digest, d1[:12]):
        return res
    if not step("old-path link resolves", os.path.realpath(old) == os.path.realpath(new), os.readlink(old)):
        return res
    bad = 0
    for rel, kind, _t, _f in L.tree_entries(new):
        if kind == "f" and not os.path.isfile(os.path.join(old, rel)):
            bad += 1
    if not step("every file reachable through the old path", bad == 0, "%d unreachable" % bad):
        return res
    if g0 is not None:
        g1 = L.git_state(L.git_facts(new))
        if not step("Git HEAD, status, stash and diff unchanged after move", g1 == g0, ""):
            return res
    os.unlink(old)
    os.rename(new, old)
    d2 = L.tree_digest(old)
    if not step("recovery restores every byte", d2 == manifest_digest, d2[:12]):
        return res
    if g0 is not None:
        g2 = L.git_state(L.git_facts(old))
        if not step("Git state unchanged after recovery", g2 == g0, ""):
            return res
    res["passed"] = True
    res["finished_at"] = L.now_iso()
    res["note"] = "Sandbox copies are left in place for inspection; remove the staging directory by hand when done."
    return res


def working_copy_repair(folder, dest, facts, cons):
    plan = {
        "is_repo_root": facts.get("is_repo_root", False),
        "inside_repo": facts.get("inside_repo"),
        "is_linked_worktree": facts.get("is_linked_worktree", False),
        "worktrees": facts.get("worktrees", []),
        "dirty": facts.get("dirty", False),
        "untracked_count": len(facts.get("untracked") or []),
        "stash_count": facts.get("stash_count", 0),
        "never": "Do not commit, stash, reset, checkout or clean. Dirty and untracked work moves as it is.",
        "backups": [],
        "commands": [],
        "punch_items": [],
    }
    meta = []
    if facts.get("is_linked_worktree"):
        meta.append(os.path.join(folder, ".git"))
        ptr = facts.get("gitdir_pointer", "")
        if ptr.startswith("gitdir:"):
            gd = ptr.split(":", 1)[1].strip()
            meta.append(os.path.join(gd, "gitdir"))
    elif facts.get("is_repo_root"):
        wtdir = os.path.join(folder, ".git", "worktrees")
        if os.path.isdir(wtdir):
            for w in sorted(os.listdir(wtdir)):
                p = os.path.join(wtdir, w, "gitdir")
                if os.path.isfile(p):
                    meta.append(p)
    for c in cons["consumers"]:
        if c["kind"] == "git-worktree-link":
            meta.append(c["path"])
    for m in meta:
        if os.path.isfile(m):
            plan["backups"].append({"file": m, "sha256": L.sha256_file(m)})
    if plan["is_linked_worktree"] or len(plan["worktrees"]) > 1 or any(c["kind"] in ("git-worktree-link", "linked-worktree") for c in cons["consumers"]):
        plan["commands"].append("git -C %s worktree repair" % dest)
        for c in cons["consumers"]:
            if c["kind"] == "linked-worktree":
                plan["commands"].append("git -C %s worktree repair %s" % (c["path"], dest))
    for r in cons["internal_absolute_refs"]:
        plan["punch_items"].append({"path": r["path"], "line": r.get("line"), "why": "embedded absolute path to the old location (for example a virtual environment); keeps working only through the old-path link"})
    plan["needed"] = bool(plan["commands"] or plan["punch_items"])
    return plan


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--folder", required=True)
    ap.add_argument("--dest", required=True)
    ap.add_argument("--roots", nargs="+", required=True)
    ap.add_argument("--staging", required=True)
    ap.add_argument("--exclude", nargs="*", default=[])
    ap.add_argument("--hold-file")
    ap.add_argument("--approval")
    ap.add_argument("--operation", default="ARCHIVE", choices=["ARCHIVE", "MOVE", "RENAME"])
    ap.add_argument("--reason", default="")
    ap.add_argument("--recent-minutes", type=int, default=60)
    ap.add_argument("--max-sandbox-bytes", type=int, default=2 * 1024 ** 3)
    ap.add_argument("--crontab", action="store_true")
    a = ap.parse_args()

    src = os.path.abspath(os.path.expanduser(a.folder))
    dest = os.path.abspath(os.path.expanduser(a.dest))
    staging = os.path.abspath(os.path.expanduser(a.staging))
    if not os.path.isdir(src) or os.path.islink(src):
        L.die("plan: %s is not a real directory" % src)
    for x, y, why in ((staging, src, "staging inside the folder"), (src, staging, "folder inside staging"),
                      (staging, dest, "staging inside the destination"), (dest, src, "destination inside the folder")):
        if L.inside(x, y):
            L.die("plan: refused, %s" % why)
    os.makedirs(staging, exist_ok=True)

    cons = C.find_consumers(src, a.roots, list(a.exclude) + [staging], crontab=a.crontab)
    facts = L.git_facts(src)
    digest = L.tree_digest(src)
    guard = live_use_guard(src, a.recent_minutes)
    level, why = risk_of(facts, cons, guard)
    sensitive = [r["path"] for r in L.file_manifest(src) if r.get("sensitive_name")]
    manifest = {
        "schema": "project-archive/manifest/1",
        "row": {"current_path": src, "target_path": dest, "operation": a.operation, "risk": level,
                "risk_reasons": why, "reason": a.reason, "deletions": "none"},
        "realpath": os.path.realpath(src),
        "tree_digest": digest,
        "git": facts,
        "files": L.file_manifest(src),
        "sensitive_files_present": sensitive,
        "written_at": L.now_iso(),
    }
    rewrites, relinks = [], []
    for c in cons["consumers"]:
        if c["kind"] in ("path-reference", "crontab"):
            m = c["matched"]
            new = dest + m[len(src):] if m.startswith(src) else None
            if new is None and m.startswith(os.path.realpath(src)):
                new = dest + m[len(os.path.realpath(src)):]
            if new is None:
                home = os.path.expanduser("~")
                for pre in ("~/", "$HOME/", "${HOME}/"):
                    if m.startswith(pre):
                        new =(pre + os.path.relpath(dest, home)) if L.inside(dest, home) else dest
                        break
            rewrites.append({"file": c["path"], "line": c.get("line"), "old": m, "new": new or dest,
                             "how": "edit by hand or through the owning tool; old text keeps working through the old-path link"})
        elif c["kind"] == "symlink":
            t = c["target"]
            relinks.append({"link": c["path"], "old_target": t, "new_target": dest + t[len(src):] if t.startswith(src) else dest})
    path_map = {"schema": "project-archive/path-map/1", "entries": [{"old": src, "new": dest}],
                "rewrites": rewrites, "relinks": relinks, "aliases": [src], "written_at": L.now_iso()}
    method, junction = link_method(src)
    links = {"schema": "project-archive/old-path-links/1",
             "links": [{"at": src, "points_to": dest, "method": method,
                        "command": junction or "ln -s -- %s %s" % (dest, src)}],
             "checks": {"old_parent_exists": os.path.isdir(os.path.dirname(src)),
                        "old_parent_writable": os.access(os.path.dirname(src), os.W_OK),
                        "dest_exists_now": os.path.lexists(dest)},
             "note": "The old path becomes an alias. Discovery must treat it as an alias, never as an artifact.",
             "written_at": L.now_iso()}
    repair = working_copy_repair(src, dest, facts, cons)
    repair["written_at"] = L.now_iso()
    sbox = sandbox_test(src, dest, staging, digest, facts, a.max_sandbox_bytes)

    files = {}
    for key, name, obj in (("consumers", "consumers.json", cons), ("manifest", "manifest.json", manifest),
                           ("path_map", "path-map.json", path_map), ("old_path_links", "old-path-links.json", links),
                           ("working_copy_repair", "working-copy-repair.json", repair),
                           ("live_use_guard", "live-use-guard.json", guard), ("sandbox_test", "sandbox-test.json", sbox)):
        p = os.path.join(staging, name)
        files[key] = {"file": name, "sha256": L.write_json(p, obj), "written_at": L.now_iso()}

    hold = L.hold_active(a.hold_file)
    appr = L.load_approval(a.approval, src, dest)
    blockers = []
    if not appr["present"]:
        blockers.append("no operator approval: folder moves are never-class")
    elif not appr["matches_exact_move"]:
        blockers.append("the approval does not name this exact source and destination, or has no approver")
    if os.path.lexists(dest):
        blockers.append("destination already exists (collision)")
    if not sbox["passed"]:
        blockers.append("sandbox test did not pass: %s" % (sbox.get("reason") or [s for s in sbox["steps"] if not s["ok"]]))
    if not guard["passed"]:
        blockers.append("live-use guard: %d recent files, %d processes inside" % (guard["recent_files_count"], len(guard["processes"])))
    if not links["checks"]["old_parent_writable"]:
        blockers.append("cannot write the old-path link: parent of the old path is not writable")
    missing = [k for k, _ in ARTIFACTS if k not in files]
    if missing:
        blockers.append("missing artifacts: %s" % ", ".join(missing))
    readiness = {
        "schema": "project-archive/readiness/1",
        "source": src, "dest": dest, "staging": staging,
        "move_class": "never",
        "policy": "Folder moves are always never-class. This skill treats every move as if a migration hold were active, "
                  "so all seven artifacts are required even when no hold is set.",
        "hold_file": a.hold_file, "hold_active": hold,
        "approval": appr,
        "artifacts": files,
        "consumer_count": cons["consumer_count"],
        "blockers": blockers,
        "ready": not blockers,
        "written_at": L.now_iso(),
    }
    L.write_json(os.path.join(staging, "readiness.json"), readiness)
    print("staging: %s" % staging)
    for k, v in files.items():
        print("  %-20s %s %s" % (k, v["file"], v["sha256"][:12]))
    print("consumers: %d; sandbox test: %s; live-use guard: %s" % (cons["consumer_count"], "passed" if sbox["passed"] else "FAILED", "passed" if guard["passed"] else "FAILED"))
    print("move class: never; hold active: %s; ready for a human-run move: %s" % (hold, not blockers))
    for b in blockers:
        print("  blocker: %s" % b)
    print("Nothing was moved.")


if __name__ == "__main__":
    main()
