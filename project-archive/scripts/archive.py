#!/usr/bin/env python3
"""Archive one folder in the order mine, index, move, link (DA-033).

Usage (one work directory W per archived folder; W must be outside the folder):
  archive.py mine   --work W --folder F --archive-root R --project ID --lineage-gate GATE.json
                    [--successor-dir DIR] [--predecessor TEXT] [--successor TEXT] [--reason TEXT]
  archive.py index  --work W
  archive.py move   --work W                      print the gated dry-run commands (human runs them)
  archive.py move   --work W --sandbox-root S     execute inside a marked sandbox only (tests, contract)
  archive.py verify --work W                      after a human ran the move: verify and record it
  archive.py link   --work W --ld-page PAGE --discovery-config CFG.json [--apply]
  archive.py status --work W

Order is enforced by W/receipts.jsonl: each step refuses unless exactly the
earlier steps are recorded, in order, and refuses to run twice. The move step
also needs W/plan/readiness.json from plan.py (the seven DA-032 artifacts and
an operator approval for this exact move); `link` also needs a passed recovery
test (recovery_test.py) and a discovery config that excludes the archive root.

Kept in W/archive-record.json: identity, locators, predecessor and successor,
retirement reason and date, source revision, content digest, uncommitted state
(status, untracked list, hash of the changed content), working-copy state (branch, stash
list, worktrees) and structured recovery instructions.
"""
import argparse
import os
import re
import shutil
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import _lib as L  # noqa: E402
import discovery as D  # noqa: E402
import move_dryrun as M  # noqa: E402
import verify_move as V  # noqa: E402

ORDER = ["mine", "index", "move", "link"]
SANDBOX_MARKER = ".project-archive-sandbox"
DATE_RE = re.compile(r"\b(20\d\d)-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])\b")


def require_order(work, step):
    done = [r["step"] for r in L.read_receipts(work)]
    want = ORDER[: ORDER.index(step)]
    if done != want:
        L.die("archive %s: refused, steps so far are %s but %s needs exactly %s first" % (step, done or "none", step, want or "none"), 3)


def cfg(work):
    return L.read_json(os.path.join(work, "archive.json"))


def cmd_mine(a):
    work = os.path.abspath(a.work)
    folder = os.path.abspath(os.path.expanduser(a.folder))
    if L.inside(work, folder):
        L.die("archive mine: the work directory must be outside the folder")
    os.makedirs(work, exist_ok=True)
    require_order(work, "mine")
    if not os.path.isdir(folder) or os.path.islink(folder):
        L.die("archive mine: %s is not a real directory" % folder)
    gate = L.read_json(a.lineage_gate)
    problems = []
    if gate.get("schema") != "lineage-gate/1":
        problems.append("the lineage gate file is not a portfolio-lineage gate (schema lineage-gate/1)")
    if os.path.realpath(gate.get("folder", "")) != os.path.realpath(folder):
        problems.append("the lineage gate was run for %s, not this folder" % gate.get("folder"))
    if not gate.get("allowed") or gate.get("unique_without_destination", 1) != 0:
        problems.append("the lineage gate refuses archiving: %d unique clause(s) lack a recorded destination" % gate.get("unique_without_destination", -1))
    if problems:
        L.die("archive mine: refused (DA-034)\n  " + "\n  ".join(problems), 4)
    root = os.path.abspath(os.path.expanduser(a.archive_root))
    dest = os.path.join(root, a.project, os.path.basename(folder))
    files = [r for r in L.file_manifest(folder) if not r["path"].split(os.sep)[0] == ".git"]
    by_sha = {}
    for r in files:
        if r.get("sha256"):
            by_sha.setdefault(r["sha256"], []).append(r["path"])
    dates_inside = set()
    for r in files:
        if r["type"] == "file" and not r.get("sensitive_name") and r.get("size", 0) < 2_000_000:
            try:
                with open(os.path.join(folder, r["path"]), "rb") as fh:
                    data = fh.read()
                if b"\0" not in data[:8192]:
                    dates_inside.update(m.group(0) for m in DATE_RE.finditer(data.decode("utf-8", "replace")))
            except OSError:
                pass
    compare = None
    if a.successor_dir:
        succ = os.path.abspath(os.path.expanduser(a.successor_dir))
        theirs = {r["path"]: r.get("sha256") for r in L.file_manifest(succ) if r["path"].split(os.sep)[0] != ".git"}
        their_hashes = set(v for v in theirs.values() if v)
        compare = {"successor_dir": succ, "only_here": [], "differs": [], "same": 0}
        for r in files:
            if r["type"] != "file":
                continue
            if r["path"] in theirs and theirs[r["path"]] == r["sha256"]:
                compare["same"] += 1
            elif r["path"] in theirs:
                compare["differs"].append(r["path"])
            elif r["sha256"] not in their_hashes:
                compare["only_here"].append(r["path"])
            else:
                compare["same"] += 1
    copy_outs = [c for c in gate.get("clauses", []) if c.get("mark") in ("unique", "partial") and c.get("destination")]
    mtimes = sorted(r["mtime"] for r in files)
    mine = {
        "schema": "project-archive/mine/1",
        "folder": folder, "file_count": len(files),
        "date_range": {"mtime_first": mtimes[0] if mtimes else None, "mtime_last": mtimes[-1] if mtimes else None,
                       "dates_inside": sorted(dates_inside)},
        "inventory": files,
        "duplicates_inside": [v for v in by_sha.values() if len(v) > 1],
        "successor_comparison": compare,
        "lineage_gate": {"file": os.path.abspath(a.lineage_gate), "sha256": L.sha256_file(a.lineage_gate),
                         "counts": gate.get("counts"), "allowed": gate.get("allowed")},
        "copy_outs": copy_outs,
        "written_at": L.now_iso(),
    }
    conf = {"folder": folder, "dest": dest, "archive_root": root, "project": a.project,
            "predecessor": a.predecessor, "successor": a.successor, "reason": a.reason,
            "index_path": os.path.join(root, a.project, "ARCHIVE-INDEX-%s.md" % os.path.basename(folder))}
    h1 = L.write_json(os.path.join(work, "archive.json"), conf)
    h2 = L.write_json(os.path.join(work, "mine.json"), mine)
    L.append_receipt(work, "mine", {"archive.json": h1, "mine.json": h2})
    print("mine: %d files, %d copy-outs with destinations, gate allowed; dest will be %s" % (len(files), len(copy_outs), dest))


def first_heading(folder):
    for name in ("README.md", "readme.md", "README", "start-here.md"):
        p = os.path.join(folder, name)
        if os.path.isfile(p) and not L.is_sensitive_name(p):
            for line in open(p, encoding="utf-8", errors="replace"):
                if line.startswith("#"):
                    return line.lstrip("#").strip(), name
    return None, None


def no_dash(s):
    return str(s).replace("\u2014", ", ").replace("\u2013", " to ")


def cmd_index(a):
    work = os.path.abspath(a.work)
    require_order(work, "index")
    c, mine = cfg(work), L.read_json(os.path.join(work, "mine.json"))
    folder = c["folder"]
    facts = L.git_facts(folder)
    digest = L.tree_digest(folder)
    record = {
        "schema": "project-archive/record/1",
        "identity": {"project_id": c["project"], "folder_name": os.path.basename(folder),
                     "repository": {"remotes": facts.get("remotes", []), "root_commits": facts.get("root_commits", [])} if facts.get("is_repo_root") else None,
                     "tree_digest": digest},
        "locators": {"original_path": folder, "archive_path": c["dest"], "old_path_link": folder,
                     "index_path": c["index_path"], "remotes": facts.get("remotes", [])},
        "predecessor": c.get("predecessor"),
        "successor": c.get("successor"),
        "retirement": {"reason": c.get("reason"), "date": L.now_iso()[:10]},
        "source_revisions": {"head": facts.get("head"), "branch": facts.get("branch")},
        "content_manifest": {"tree_digest": digest, "file_count": mine["file_count"]},
        "uncommitted_state": {"status_porcelain": facts.get("status_porcelain"), "untracked": facts.get("untracked"),
                              "changed_content_sha256": facts.get("changed_content_sha256"), "dirty": facts.get("dirty")},
        "working_copy_state": {"is_repo_root": facts.get("is_repo_root", False), "branch": facts.get("branch"),
                               "stash_list": facts.get("stash_list"), "stash_count": facts.get("stash_count"),
                               "worktrees": facts.get("worktrees"), "is_linked_worktree": facts.get("is_linked_worktree")},
        "recovery": {
            "instructions": [
                {"op": "remove-link", "path": folder, "note": "removes only the link left at the old path"},
                {"op": "move", "from": c["dest"], "to": folder},
                {"op": "verify", "tree_digest": digest, "git_state": L.git_state(facts) if facts.get("is_repo_root") else None},
            ],
            "human_steps": "unlink %s ; mv %s %s ; then run verify_move.py or recovery_test.py checks; if the folder had linked worktrees run git worktree repair" % (folder, c["dest"], folder),
            "tested": False,
        },
    }
    title, from_file = first_heading(folder)
    g = mine["lineage_gate"]
    lines = [
        "---", "title: %s archive index" % os.path.basename(folder), "type: archive-index",
        "date: %s" % L.now_iso()[:10], "project: %s" % c["project"],
        "original-location: %s" % folder, "archive-location: %s" % c["dest"],
        "generated-by: project-archive scripts/archive.py index", "---", "",
        "# %s: archive index" % os.path.basename(folder), "",
        "## 1. What the folder was", "",
        ("First heading of `%s`: %s" % (from_file, no_dash(title))) if title else "No README heading found; see the inventory.",
        "", "Reason for retirement: %s" % no_dash(c.get("reason") or "not given"), "",
        "## 2. Date range", "",
        "- File dates: %s to %s (UTC)" % (mine["date_range"]["mtime_first"], mine["date_range"]["mtime_last"]),
        "- Dates written inside files: %s" % (", ".join(mine["date_range"]["dates_inside"][:3] + (["..."] if len(mine["date_range"]["dates_inside"]) > 6 else []) + mine["date_range"]["dates_inside"][-3:]) if mine["date_range"]["dates_inside"] else "none found"),
        "", "## 3. Lineage", "",
        "- Predecessor: %s" % no_dash(c.get("predecessor") or "none recorded"),
        "- Successor: %s" % no_dash(c.get("successor") or "none recorded"), "",
        "## 4. Clause comparison (portfolio-lineage gate)", "",
        "Gate file `%s` (sha256 %s): %s; archiving allowed: %s." % (
            g["file"], g["sha256"][:12], ", ".join("%s %s" % (k, v) for k, v in sorted((g["counts"] or {}).items())), g["allowed"]), "",
    ]
    if mine["copy_outs"]:
        lines += ["| Clause | Mark | Destination |", "|---|---|---|"]
        for co in mine["copy_outs"]:
            lines.append("| %s | %s | %s |" % (co.get("key"), co.get("mark"), no_dash(co.get("destination"))))
        lines.append("")
    lines += ["## 5. File inventory", "", "| File | Bytes | Modified (UTC) | sha256 (first 12) |", "|---|---|---|---|"]
    for r in mine["inventory"]:
        if r["type"] == "file":
            lines.append("| `%s` | %s | %s | `%s` |" % (r["path"], r["size"], r["mtime"], "(sensitive name, hash only)" if r.get("sensitive_name") else r["sha256"][:12]))
        else:
            lines.append("| `%s` | %s | %s | %s |" % (r["path"], r["type"], r["mtime"], r.get("target", "")))
    lines += ["", "## 6. State kept", "",
              "- Git repository: %s; HEAD %s on %s" % (facts.get("is_repo_root", False), facts.get("head"), facts.get("branch")),
              "- Uncommitted lines in `git status --porcelain`: %d; untracked files: %d; stash entries: %s" % (
                  len((facts.get("status_porcelain") or "").splitlines()), len(facts.get("untracked") or []), facts.get("stash_count")),
              "- Tree digest: `%s`" % digest, "",
              "## 7. Recovery", "", "`%s`" % record["recovery"]["human_steps"], "",
              "Tested recovery result: see `recovery-test.json` in the work directory.", ""]
    h1 = L.write_json(os.path.join(work, "archive-record.json"), record)
    idx = os.path.join(work, "ARCHIVE-INDEX.md")
    with open(idx, "w", encoding="utf-8") as fh:
        fh.write("\n".join(no_dash(x) for x in lines))
    L.append_receipt(work, "index", {"archive-record.json": h1, "ARCHIVE-INDEX.md": L.sha256_file(idx)})
    print("index: wrote %s and the archive record" % idx)


def _plan_matches(work, c):
    plan = os.path.join(work, "plan")
    rp = os.path.join(plan, "readiness.json")
    if not os.path.isfile(rp):
        L.die("archive move: refused, no %s; run plan.py --staging %s --folder %s --dest %s first" % (rp, plan, c["folder"], c["dest"]), 3)
    r = L.read_json(rp)
    if r["source"] != c["folder"] or r["dest"] != c["dest"]:
        L.die("archive move: refused, the plan is for %s -> %s, not %s -> %s" % (r["source"], r["dest"], c["folder"], c["dest"]), 3)
    return plan


def _record_move(work, plan, mode):
    res = V.verify(plan)
    h = L.write_json(os.path.join(work, "move-verify.json"), res)
    if not res["passed"]:
        L.die("archive: the move did not verify; run the rollback printed by move_dryrun.py\n  " +
              "\n  ".join("%s: %s" % (x["check"], x["detail"]) for x in res["checks"] if not x["ok"]), 5)
    L.append_receipt(work, "move", {"move-verify.json": h}, {"mode": mode})
    print("move: verified and recorded (%s)" % mode)


def cmd_move(a):
    work = os.path.abspath(a.work)
    require_order(work, "move")
    c = cfg(work)
    plan = _plan_matches(work, c)
    r, reasons = M.check(plan, a.recent_minutes)
    if reasons:
        print("REFUSED (never-class): this move cannot go ahead.")
        for x in reasons:
            print("  - %s" % x)
        sys.exit(2)
    if not a.sandbox_root:
        print("\n".join(M.commands(r, plan)))
        print("# Then copy %s to %s and run: archive.py verify --work %s" % (os.path.join(work, "ARCHIVE-INDEX.md"), c["index_path"], work))
        return
    box = os.path.realpath(a.sandbox_root)
    if not os.path.isfile(os.path.join(box, SANDBOX_MARKER)):
        L.die("archive move: refused, %s has no %s marker; real moves are printed, never executed" % (box, SANDBOX_MARKER), 3)
    for p in (c["folder"], c["dest"], c["index_path"]):
        if not L.inside(os.path.realpath(os.path.dirname(p)), box):
            L.die("archive move: refused, %s is outside the sandbox %s" % (p, box), 3)
    os.makedirs(os.path.dirname(c["dest"]), exist_ok=True)
    os.rename(c["folder"], c["dest"])
    os.symlink(c["dest"], c["folder"])
    shutil.copy2(os.path.join(work, "ARCHIVE-INDEX.md"), c["index_path"])
    _record_move(work, plan, "sandbox")


def cmd_verify(a):
    work = os.path.abspath(a.work)
    require_order(work, "move")
    c = cfg(work)
    plan = _plan_matches(work, c)
    if not os.path.isfile(c["index_path"]):
        L.die("archive verify: the index is not at %s yet; copy it there first" % c["index_path"], 5)
    _record_move(work, plan, "human-run")


def cmd_link(a):
    work = os.path.abspath(a.work)
    require_order(work, "link")
    c = cfg(work)
    rec = L.read_json(os.path.join(work, "archive-record.json"))
    if not rec["recovery"].get("tested"):
        L.die("archive link: refused, the recovery has not been tested; run recovery_test.py --work %s first" % work, 3)
    disc = D.check(a.discovery_config, c["archive_root"])
    h_disc = L.write_json(os.path.join(work, "discovery-check.json"), disc)
    if not disc["passed"]:
        L.die("archive link: refused, the archive root is not excluded from discovery:\n  " + "\n  ".join(disc["problems"]), 3)
    entry = "\n".join([
        "", "## Lineage: %s archived %s" % (os.path.basename(c["folder"]), L.now_iso()[:10]), "",
        "- Archived from `%s` to `%s`; the old path is now a link." % (c["folder"], c["dest"]),
        "- Archive index: `%s`" % c["index_path"],
        "- Predecessor: %s. Successor: %s." % (no_dash(c.get("predecessor") or "none recorded"), no_dash(c.get("successor") or "none recorded")),
        "- Reason: %s" % no_dash(c.get("reason") or "not given"),
        "- Recovery tested %s; identity digest `%s`." % (rec["recovery"].get("tested_at", "")[:10], rec["identity"]["tree_digest"][:16]),
        "",
    ])
    entry_file = os.path.join(work, "lineage-entry.md")
    with open(entry_file, "w", encoding="utf-8") as fh:
        fh.write(entry)
    page = os.path.abspath(os.path.expanduser(a.ld_page))
    applied = False
    if a.apply:
        if not os.path.isfile(page):
            L.die("archive link: the Living Documents page %s does not exist; create it through the Living Documents tools first" % page, 3)
        os.makedirs(os.path.join(work, "backups"), exist_ok=True)
        shutil.copy2(page, os.path.join(work, "backups", os.path.basename(page) + ".before-link"))
        with open(page, "a", encoding="utf-8") as fh:
            fh.write(entry)
        applied = True
        print("link: appended the lineage entry to %s (backup in %s)" % (page, os.path.join(work, "backups")))
    else:
        print("link: lineage entry written to %s; append it to %s (or re-run with --apply)" % (entry_file, page))
    L.append_receipt(work, "link", {"lineage-entry.md": L.sha256_file(entry_file), "discovery-check.json": h_disc},
                     {"lineage_page": page, "applied": applied})


def cmd_status(a):
    for r in L.read_receipts(os.path.abspath(a.work)):
        print("%d %-6s %s %s" % (r["seq"], r["step"], r["at"], r.get("mode", "")))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("mine")
    m.add_argument("--work", required=True)
    m.add_argument("--folder", required=True)
    m.add_argument("--archive-root", required=True)
    m.add_argument("--project", required=True)
    m.add_argument("--lineage-gate", required=True)
    m.add_argument("--successor-dir")
    m.add_argument("--predecessor")
    m.add_argument("--successor")
    m.add_argument("--reason", default="")
    for name in ("index", "verify", "status"):
        s = sub.add_parser(name)
        s.add_argument("--work", required=True)
    mv = sub.add_parser("move")
    mv.add_argument("--work", required=True)
    mv.add_argument("--sandbox-root")
    mv.add_argument("--recent-minutes", type=int, default=60)
    lk = sub.add_parser("link")
    lk.add_argument("--work", required=True)
    lk.add_argument("--ld-page", required=True)
    lk.add_argument("--discovery-config", required=True)
    lk.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    {"mine": cmd_mine, "index": cmd_index, "move": cmd_move, "verify": cmd_verify,
     "link": cmd_link, "status": cmd_status}[a.cmd](a)


if __name__ == "__main__":
    main()
